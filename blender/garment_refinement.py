"""Deterministic cloth finishing for the native, skinned cartoon performer.

Call ``refine_clothing(human, rig, meshes, G, here, materials)`` after the
collar/cuffs/placket have been created and before ``G.join_by_material()``.
``materials`` contains polo, cream, navy and pants (other entries are ignored).
The operation is intentionally one-shot, and never replaces skin or armature
weights. Distances below are metres in the Human parent's bind coordinates.

Broad folds are actual geometry. Fine cotton/twill detail is saved as ordinary
PNG normal and roughness maps, attached through a named UV layer and standard
Principled inputs understood by Blender's glTF exporter. No renderer-only
procedural texture is required. Textures are generated locally with NumPy;
the pattern and output are reproducible and require no external assets.
"""
from pathlib import Path
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector

UV_NAME = 'FabricUV'
TILE_METRES = .12
VERSION = 1


def _smooth(a, b, x):
    t = max(0., min(1., (x-a)/(b-a)))
    return t*t*(3.-2.*t)


def _g(x, center, width):
    return math.exp(-((x-center)/width)**2)


def _ridge(x, center, width):
    # Broad compression crest with a shallow adjacent valley; zero net balloon.
    return _g(x, center, width)-.30*_g(x, center+width*1.7, width*1.35)


def _image(name, rgb, folder):
    height, width = rgb.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    image.colorspace_settings.name = 'Non-Color'
    rgba = np.ones((height, width, 4), dtype=np.float32)
    rgba[:, :, :3] = rgb
    image.pixels.foreach_set(rgba.ravel())
    image.filepath_raw = str(folder/(name+'.png'))
    image.file_format = 'PNG'
    image.save()
    image.pack()
    return image


def make_fabric_textures(here, size=512):
    """Return cotton/twill normal+roughness Image pairs; safe for GLB packing."""
    folder = Path(here)/'textures'
    folder.mkdir(parents=True, exist_ok=True)
    yy, xx = np.mgrid[0:size, 0:size]/float(size)
    tau = 2.*math.pi
    result = {}
    for kind in ('cotton', 'twill'):
        if kind == 'cotton':
            # Small woven crossing rather than coarse all-over random bumps.
            height = (np.cos(tau*64*xx)*(.64+.22*np.cos(tau*32*yy))
                      + np.cos(tau*64*yy)*(.64-.22*np.cos(tau*32*xx)))
            rough = .84+.025*np.cos(tau*64*xx)*np.cos(tau*64*yy)
        else:
            height = (.70*np.cos(tau*(48*xx+48*yy))
                      + .18*np.cos(tau*96*xx)+.12*np.cos(tau*96*yy))
            rough = .88+.026*np.cos(tau*(48*xx+48*yy))
        # Periodic central derivatives keep both tile edges seamless.
        dx = (np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.12
        dy = (np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.12
        normal = np.stack((-dx,-dy,np.ones_like(dx)), axis=-1)
        normal /= np.linalg.norm(normal,axis=-1,keepdims=True)
        result[kind] = (
            _image('cloth-'+kind+'-normal', normal*.5+.5, folder),
            _image('cloth-'+kind+'-roughness',np.repeat(rough[:,:,None],3,axis=2),folder))
    return result


def _fabric_material(mat, textures, strength):
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map=UV_NAME;uv.label='Physical cloth scale: 12 cm repeat'
    normal=nodes.new('ShaderNodeTexImage');normal.image=textures[0];normal.label='Exported woven cloth normal'
    rough=nodes.new('ShaderNodeTexImage');rough.image=textures[1];rough.label='Exported woven cloth roughness'
    for n in (normal,rough):
        n.interpolation='Linear';n.extension='REPEAT';links.new(uv.outputs['UV'],n.inputs['Vector'])
    convert=nodes.new('ShaderNodeNormalMap');convert.uv_map=UV_NAME
    convert.inputs['Strength'].default_value=strength
    links.new(normal.outputs['Color'],convert.inputs['Color'])
    links.new(convert.outputs['Normal'],p.inputs['Normal'])
    links.new(rough.outputs['Color'],p.inputs['Roughness'])
    p.inputs['Metallic'].default_value=0.
    p.inputs['Specular IOR Level'].default_value=.22
    if 'Sheen Weight' in p.inputs:
        # Keep the web and native response identical: cloth reads through its
        # weave and roughness, without a renderer-specific sheen-weight mix.
        p.inputs['Sheen Weight'].default_value=0.
    mat['cloth_detail']='Packed PNG normal + roughness; FabricUV; reproducible garment_refinement.py'


def _fabric_uv(obj, human):
    # A second per-face UV set preserves the existing baked blue/ivory atlas.
    # Tiny continuous weave is insensitive to projection seams at side panels.
    mesh=obj.data
    active=mesh.uv_layers.active_index
    uv=mesh.uv_layers.get(UV_NAME) or mesh.uv_layers.new(name=UV_NAME)
    M=human.matrix_world.inverted()@obj.matrix_world
    normal_matrix=M.to_3x3().inverted().transposed()
    for polygon in mesh.polygons:
        n=normal_matrix@polygon.normal
        major=max(range(3),key=lambda k:abs(n[k]))
        axes=((1,2),(0,2),(0,1))[major]
        sign=1. if n[major]>=0 else -1.
        for li in polygon.loop_indices:
            q=M@mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(q[axes[0]]*sign/TILE_METRES,q[axes[1]]/TILE_METRES)
    mesh.uv_layers.active_index=active


def _subdivide_cloth(obj, slots):
    # Linear refinement preserves source UVs and deform weights. Skin-only
    # edges are untouched; shared boundary edges split without a T junction.
    bm=bmesh.new();bm.from_mesh(obj.data)
    edges={e for f in bm.faces if f.material_index in slots for e in f.edges}
    bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True,smooth=0.)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free();obj.data.update()


def _refine_body(obj,human,rig,materials):
    if obj.get('cloth_refinement_version')==VERSION:
        return {'object':obj.name,'already_refined':True}
    mat_to_index={m:i for i,m in enumerate(obj.data.materials)}
    top_slots={mat_to_index[m] for key in ('polo','navy') if (m:=materials.get(key)) in mat_to_index}
    pant_slots={mat_to_index[m] for key in ('pants',) if (m:=materials.get(key)) in mat_to_index}
    if not top_slots and not pant_slots:return None
    _subdivide_cloth(obj,top_slots|pant_slots)
    mesh=obj.data;M=human.matrix_world.inverted()@obj.matrix_world;I=M.inverted()
    points=[M@v.co for v in mesh.vertices]
    original=[p.copy() for p in points]
    memberships=[set() for _ in points]
    adjacency=[set() for _ in points]
    for p in mesh.polygons:
        for vi in p.vertices:memberships[vi].add(p.material_index)
    for edge in mesh.edges:
        a,b=edge.vertices;adjacency[a].add(b);adjacency[b].add(a)
    cloth=top_slots|pant_slots
    movable={i for i,m in enumerate(memberships) if m and m.issubset(cloth)}
    groups={g.index:g.name for g in obj.vertex_groups}
    protect={v.index for v in mesh.vertices if sum(g.weight for g in v.groups
             if any(n in groups[g.group] for n in ('Hand','Finger')))>.12}
    movable-=protect
    # Fair the full shoulder transition, not just individual radial neck strips.
    # Inner neck and garment/skin boundaries stay anchored. Relaxation is local
    # and capped, so it cannot pull the collar apart or shrink the whole torso.
    shoulder_weights={}
    for i in movable:
        q=points[i]
        if memberships[i]&top_slots and q.z>1.31 and abs(q.x)<.29:
            inner=1.-_g(q.x,0.,.064)*_smooth(1.445,1.485,q.z)
            shoulder_weights[i]=(.68*_smooth(1.31,1.40,q.z)
                                  *(1.-_smooth(.24,.29,abs(q.x)))*inner)
    for _ in range(12):
        update={}
        for i,w in shoulder_weights.items():
            neighbors=adjacency[i]
            mean=sum((points[j] for j in neighbors),Vector())/len(neighbors)
            delta=(mean-points[i])*w
            p=points[i]+delta
            offset=p-original[i]
            if offset.length>.014:p=original[i]+offset.normalized()*.014
            update[i]=p
        for i,p in update.items():points[i]=p
    # The inherited neck closure contains a few tall boundary tips. Give the
    # shoulder tops a continuous sloping ceiling instead of preserving those
    # spikes merely because the fairing distance was capped.
    for i in movable:
        q=points[i]
        if memberships[i]&top_slots and .072<abs(q.x)<.235 and q.z>1.445:
            ceiling=1.490-.18*max(0.,abs(q.x)-.060)
            if q.z>ceiling:q.z=ceiling+.0025*math.tanh((q.z-ceiling)/.0025)
    for i,q in enumerate(points):mesh.vertices[i].co=I@q
    mesh.update()
    normal_matrix=M.to_3x3().inverted().transposed()
    normals=[(normal_matrix@v.normal).normalized() for v in mesh.vertices]
    bone_matrix=human.matrix_world.inverted()@rig.matrix_world
    joints={}
    for side in ('L','R'):
        elbow=(bone_matrix@rig.data.bones['Bip01 '+side+' Forearm'].matrix_local).translation
        wrist=(bone_matrix@rig.data.bones['Bip01 '+side+' Hand'].matrix_local).translation
        joints[side]=(elbow,wrist,(wrist-elbow).normalized(),(wrist-elbow).length)
    changed=0;maximum=0.
    for i in movable:
        q=points[i];x,y,z=q;nx=abs(x);d=0.
        if memberships[i]&top_slots:
            if nx<.255 and z<1.34:
                # Loose hem: three asymmetric, wide folds on the front plus
                # shallow side drape. The central chest stays calm and readable.
                front=1.-_smooth(-.055,.035,y)
                zone=(1.-_smooth(.20,.255,nx))*_smooth(.887,.925,z)
                d+=front*zone*(.0058*_ridge(z,.969+.14*x,.019)
                     +.0046*_ridge(z,1.044-.20*x,.024)*_g(x,.095,.15)
                     +.0032*_ridge(z,1.118+.23*x,.029)*_g(x,-.12,.095))
                d+=.0045*_g(z,.969,.085)*_g(nx,.155,.048)
                # Short diagonal underarm compression, not radial shoulders.
                d+=.0035*_g(nx,.205,.043)*_ridge(z,1.245+.15*nx,.025)
            if nx>.255:
                side='L' if x>0 else 'R'
                elbow,wrist,axis,length=joints[side]
                along=(q-elbow).dot(axis)
                radial=q-(elbow+axis*along)
                radius=radial.length
                # Keep the cuff seating and neutral anatomical wrist intact.
                gate=(1.-_smooth(length-.100,length-.055,along))*_smooth(-.10,-.035,along)
                facing=.35+.65*(.5-.5*radial.normalized().y) if radius else .5
                d+=gate*facing*(.0048*_ridge(along,.010,.020)
                               +.0040*_ridge(along,.064,.018))
                d+=.0035*gate*_g(along,.035,.090)
        elif memberships[i]&pant_slots and nx<.29 and z<.88:
            side=1. if x>0 else -1.
            across=x-side*.112
            front=1.-_smooth(-.025,.065,y)
            # Relaxed knee/shin folds and cloth settling above the shoe. Broad
            # waves are off-axis, so the trousers do not resemble ribbed tubes.
            gate=_smooth(.098,.145,z)*(1.-_smooth(.76,.88,z))
            d+=gate*front*(.0052*_ridge(z,.455+side*.30*across,.025)
                          +.0035*_ridge(z,.383-side*.23*across,.032)
                          +.0046*_ridge(z,.173+side*.20*across,.018)
                          +.0034*_ridge(z,.222-side*.35*across,.023))
            d+=.003*_g(across,.025*side,.034)*_g(z,.63,.17)
        if abs(d)>1e-7:
            mesh.vertices[i].co=I@(q+normals[i]*d)
            maximum=max(maximum,abs(d));changed+=1
    mesh.update()
    for p in mesh.polygons:p.use_smooth=True
    obj['cloth_refinement_version']=VERSION
    obj['cloth_fold_design']='Broad anatomical folds: hem, elbow, underarm, knee and ankle; wrist/skin protected'
    return {'object':obj.name,'fold_vertices':changed,'max_fold_m':maximum,
            'shoulder_vertices':len(shoulder_weights),'vertices':len(mesh.vertices)}


def _soft_trim(human,meshes,G,cream):
    """Replace only old upper ivory trim; preserve the source cuffs and skin."""
    A=human.matrix_world.inverted()
    for obj in list(G.objects):
        if obj.type!='MESH' or cream not in list(obj.data.materials):continue
        cream_indices={i for i,m in enumerate(obj.data.materials) if m==cream}
        M=A@obj.matrix_world
        bm=bmesh.new();bm.from_mesh(obj.data)
        remove=[]
        for face in bm.faces:
            q=M@face.calc_center_median()
            if face.material_index in cream_indices and q.z>1.32 and abs(q.x)<.18:remove.append(face)
        if remove:bmesh.ops.delete(bm,geom=remove,context='FACES')
        empty=not bm.faces
        bm.to_mesh(obj.data);bm.free()
        if empty:
            G.objects.remove(obj);bpy.data.objects.remove(obj,do_unlink=True)
    surface=[]
    for obj in meshes:
        M=A@obj.matrix_world
        for v in obj.data.vertices:
            q=M@v.co
            if abs(q.x)<.24 and 1.30<q.z<1.50 and q.y<-.018:surface.append(q)
    def front(x,z):
        # Closest garment samples; a small broad kernel avoids a faceted placket.
        close=sorted(surface,key=lambda q:(q.x-x)**2+(q.z-z)**2)[:10]
        weights=[1./(1e-5+(q.x-x)**2+(q.z-z)**2) for q in close]
        return sum(q.y*w for q,w in zip(close,weights))/sum(weights)-.0008
    def finish(obj,thickness):
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        # Apply mesh-only modifiers before the armature, preserving bind shape.
        sub=obj.modifiers.new('Soft sewn cloth curvature','SUBSURF');sub.levels=2
        bpy.ops.object.modifier_move_to_index(modifier=sub.name,index=0)
        bpy.ops.object.modifier_apply(modifier=sub.name)
        solid=obj.modifiers.new('Actual cotton fabric thickness','SOLIDIFY')
        solid.thickness=thickness;solid.offset=0.;solid.use_even_offset=True
        bpy.ops.object.modifier_move_to_index(modifier=solid.name,index=0)
        bpy.ops.object.modifier_apply(modifier=solid.name)
        bevel=obj.modifiers.new('Rounded fabric edge','BEVEL')
        bevel.width=.00065;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.55
        bpy.ops.object.modifier_move_to_index(modifier=bevel.name,index=0)
        bpy.ops.object.modifier_apply(modifier=bevel.name)
        obj.select_set(False)
    # One connected rolled collar around the nape, with two softly tapered
    # front leaves. Its inner edge sits outside the actual continuous neck.
    verts=[];faces=[];sections=64
    radial=(0.,.04,.12,.28,.48,.70,.88,.97,1.)
    for i in range(sections+1):
        theta=.145+(2.*math.pi-.290)*i/sections
        f=math.cos(theta);s=math.sin(theta)
        inner=Vector((.051*s,.007-.054*f,1.482+.013*(1.-f)/2.))
        point=_smooth(.65,.98,f)
        front_angle=min(theta,2.*math.pi-theta)
        tip=_g(front_angle,.145,.205)
        outer=Vector((.109*s+math.copysign(.018*point,s),
                      .010-.134*f,1.451+.026*(1.-f)/2.-.033*tip))
        if f>.28:
            contact=front(outer.x,outer.z)-.0015
            outer.y=outer.y*(1.-_smooth(.28,.70,f))+contact*_smooth(.28,.70,f)
        for u in radial:
            p=inner.lerp(outer,u)
            roll=math.sin(math.pi*u)
            p.z+=.009*roll
            p.y-=.0045*roll*max(0.,f)
            verts.append(p)
        if i:
            n=len(radial)
            for j in range(n-1):
                faces.append(((i-1)*n+j,(i-1)*n+j+1,i*n+j+1,i*n+j))
    collar=G.mesh('Human tailored rolled cotton collar',verts,faces,cream,'Bip01 Spine2')
    finish(collar,.0020)
    # A narrow, gently crowned placket conforms to the front instead of a flat
    # plane spanning empty space. Rounded corners are supplied by subdivision.
    verts=[];faces=[];rows=20;columns=6
    for i in range(rows+1):
        z=1.438-(1.438-1.348)*i/rows
        for j in range(columns+1):
            x=-.010+.020*j/columns
            y=front(x,z)-.0006-.0004*(1.-(x/.010)**2)
            verts.append((x,y,z))
        if i:
            for j in range(columns):
                n=columns+1
                faces.append(((i-1)*n+j,i*n+j,i*n+j+1,(i-1)*n+j+1))
    placket=G.mesh('Human conforming cotton polo placket',verts,faces,cream,'Bip01 Spine2')
    finish(placket,.0015)
    for z in (1.408,1.374):
        G.ellipsoid('Human small sewn polo button',(0,front(0,z)-.0038,z),
                    (.0027,.0013,.0027),cream,'Bip01 Spine2',rings=12,sectors=24)


def add_inner_neck_facing(G, navy):
    """Bridge the narrow new-neck/collar clearance with a tucked inner facing."""
    verts=[];faces=[];steps=96;rows=5
    for i in range(rows):
        u=i/(rows-1)
        for j in range(steps):
            a=2.*math.pi*j/steps;f=math.cos(a);si=math.sin(a)
            z=1.482+.0065*(1.-f)-.002
            t=max(0.,min(1.,(z-1.465)/.030))
            rx=.050+(.043-.050)*t;ry=.046+(.043-.046)*t;cy=.010+(.005-.010)*t
            inner=Vector(((rx-.0008)*si,cy-(ry-.0008)*f,z))
            outer=Vector((.0535*si,.007-.0565*f,z))
            verts.append(inner.lerp(outer,u))
            if i:faces.append(((i-1)*steps+j,(i-1)*steps+(j+1)%steps,i*steps+(j+1)%steps,i*steps+j))
    obj=G.mesh('Human fitted navy inner collar facing',verts,faces,navy,'Bip01 Neck')
    obj.vertex_groups.clear();neck=obj.vertex_groups.new(name='Bip01 Neck');spine=obj.vertex_groups.new(name='Bip01 Spine2')
    for i in range(rows):
        u=i/(rows-1);ids=list(range(i*steps,(i+1)*steps))
        neck.add(ids,1.-u,'REPLACE');spine.add(ids,u,'REPLACE')
    _fabric_uv(obj,G.human)
    obj['purpose']='Continuous thin inner facing; closes neck/collar clearance without changing shoulder silhouette'
    return obj


def refine_clothing(human,rig,meshes,G,here,materials):
    """Finish clothing only, returning a small integration audit dictionary."""
    if human.get('garment_refinement_version')==VERSION:
        return {'version':VERSION,'already_refined':True}
    textures=make_fabric_textures(here)
    for key in ('polo','cream','navy','pants'):
        mat=materials.get(key)
        if mat:
            _fabric_material(mat,textures['twill' if key=='pants' else 'cotton'],.55 if key=='pants' else .45)
    audit=[]
    for obj in meshes:
        if obj.type=='MESH':
            result=_refine_body(obj,human,rig,materials)
            if result:audit.append(result)
    if materials.get('cream'):
        _soft_trim(human,meshes,G,materials['cream'])
    if materials.get('navy'):
        add_inner_neck_facing(G,materials['navy'])
    # The generated collar and cuffs share the same physical weave size; apply
    # the UV after their modifiers are baked and before material-based joining.
    cloth_materials={materials[k] for k in ('polo','cream','navy','pants') if k in materials}
    for obj in list(meshes)+list(G.objects):
        if obj.type=='MESH' and any(m in cloth_materials for m in obj.data.materials):
            _fabric_uv(obj,human)
    human['garment_refinement_version']=VERSION
    human['garment_materials']='Cotton polo and twill trousers; packed UV normal/roughness PNGs; broad skinned folds'
    result={'version':VERSION,'meshes':audit,'texture_files':[str(Path(here)/'textures'/('cloth-'+k+'-'+t+'.png'))
                   for k in ('cotton','twill') for t in ('normal','roughness')],
            'uv_layer':UV_NAME,'tile_metres':TILE_METRES}
    print('GARMENT_REFINEMENT',result,flush=True)
    return result
