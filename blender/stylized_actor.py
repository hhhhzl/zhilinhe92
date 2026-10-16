"""Sculpted adult animation character based on the selected concept sheet.

No projected photos, pores, alpha hair cards, or view-dependent impostors.
The licensed performer supplies only the articulated body and stable motion rig.
The face, eyes, brows, eyewear and solid wave locks are newly authored meshes.
"""
import bpy,bmesh,math
from mathutils import Vector
from stylized_geometry import Geometry
from avatar_surface import bake_color

def smooth(a,b,x):
    u=max(0.,min(1.,(x-a)/(b-a)));return u*u*(3-2*u)
def gauss(x,c,s):return math.exp(-((x-c)/s)**2)
def customize(human,rig,meshes,here):
    (here/'textures').mkdir(exist_ok=True)
    G=Geometry(human,rig)
    skin=G.material('Human Stylized warm peach skin',(.56,.285,.165),.67)
    lip=G.material('Human Stylized soft rose lips',(.35,.135,.092),.66)
    mouth=G.material('Human Stylized smile crease',(.115,.038,.025),.85)
    earinner=G.material('Human Stylized ear warmth',(.42,.17,.105),.74)
    white=G.material('Human Stylized ivory sclera',(.84,.80,.70),.40)
    iris=G.material('Human Stylized chestnut iris',(.105,.042,.022),.38)
    pupil=G.material('Human Stylized pupil',(.009,.007,.006),.30)
    highlight=G.material('Human Stylized eye catchlight',(.98,.94,.82),.25)
    brow=G.material('Human Stylized sculpted eyebrows',(.028,.018,.016),.80)
    hair=[G.material('Human Stylized solid waves '+str(i),(.022+i*.004,.017+i*.003,.020+i*.003),.74) for i in range(3)]
    gold=G.material('Human Stylized champagne frames',(.55,.39,.19),.29,.62)
    polo=G.material('Human Stylized blue ivory polo',(.07,.105,.17),.85)
    cream=G.material('Human Stylized soft ivory collar',(.76,.735,.66),.87)
    navy=G.material('Human Stylized continuous blue neckline',(.055,.090,.17),.85)
    pants=G.material('Human Stylized charcoal trousers',(.038,.044,.055),.90)
    shoes=G.material('Human Stylized ivory sneakers',(.76,.74,.68),.76)
    soles=G.material('Human Stylized rubber soles',(.57,.56,.51),.90)
    A=human.matrix_world.inverted()
    for o in meshes:
        M=A@o.matrix_world;I=M.inverted();mats=o.data.materials
        bodyi=next(i for i,m in enumerate(mats) if 'body' in m.name.lower())
        headi=next(i for i,m in enumerate(mats) if 'head' in m.name.lower())
        alphai=next(i for i,m in enumerate(mats) if 'opacity' in m.name.lower())
        ji=next(i for i,m in enumerate(mats) if 'navy' in m.name.lower())
        mats[bodyi]=skin;mats[headi]=skin;mats[ji]=polo
        ids={}
        for name,mat in [('pants',pants),('shoes',shoes),('soles',soles)]:
            mats.append(mat);ids[name]=len(mats)-1
        garment=set();pantverts=set();groups={g.index:g.name for g in o.vertex_groups}
        for p in o.data.polygons:
            center=sum((M@o.data.vertices[v].co for v in p.vertices),Vector())/len(p.vertices)
            if p.material_index==ji:garment.update(p.vertices)
            elif p.material_index==bodyi and center.z<.88:
                if center.z<.092:p.material_index=ids['soles'] if center.z<.028 else ids['shoes']
                else:p.material_index=ids['pants'];pantverts.update(p.vertices)
        boundaries={}
        for p in o.data.polygons:
            for e in p.edge_keys:boundaries.setdefault(tuple(sorted(e)),set()).add(p.material_index)
        cloth_boundary={v for e,indices in boundaries.items() if ji in indices and len(indices)>1 for v in e}
        for v in o.data.vertices:
            q=M@v.co
            if v.index in cloth_boundary:
                if q.z<1.0 and abs(q.x)<.29:q.z=.895
                elif abs(q.x)>.43:q.x=math.copysign(.572,q.x)
            if v.index in garment:
                n=(M.to_3x3()@v.normal).normalized();w=sum(g.weight for g in v.groups if any(k in groups[g.group] for k in ['Hand','Finger']))
                q+=n*.012*(1-min(1.,w/.35))*smooth(.84,.94,q.z)
                if abs(q.x)<.28:q.x*=1.07
            elif v.index in pantverts:
                centre=.112 if q.x>0 else -.112;w=.30*(1-smooth(.73,.90,q.z))
                q.x=centre+(q.x-centre)*(1+w);q.y*=1+w*.65
            v.co=I@q
        for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
        mats.append(navy);seat_index=len(mats)-1
        bm=bmesh.new();bm.from_mesh(o.data)
        remove=[f for f in bm.faces if f.material_index in (alphai,headi) or (M@f.calc_center_median()).z>1.529 or (abs((M@f.calc_center_median()).x)<.132 and (M@f.calc_center_median()).z>1.445)]
        bmesh.ops.delete(bm,geom=remove,context='FACES')
        # Weld source UV seams only for topological boundary discovery, then
        # bridge the actual cloth opening. The outer vertices never move.
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001/max(M.to_scale()))
        boundary=[e for e in bm.edges if e.is_boundary]
        unseen=set(boundary);loops=[]
        while unseen:
            first=unseen.pop();path=[first.verts[0],first.verts[1]];edge=first
            while True:
                nxt=next((e for e in path[-1].link_edges if e in unseen),None)
                if nxt is None:break
                unseen.remove(nxt);v=nxt.other_vert(path[-1])
                if v==path[0]:break
                path.append(v)
            if len(path)>8:loops.append(path)
        candidates=[loop for loop in loops if min((M@v.co).z for v in loop)>1.38]
        print('COLLAR_BOUNDARIES',[(len(loop),round(sum((M@v.co).z for v in loop)/len(loop),3)) for loop in candidates],flush=True)
        if not candidates:raise RuntimeError('No actual shirt neckline boundary found')
        opening=max(candidates,key=len);deform=bm.verts.layers.deform.active
        spine=o.vertex_groups.get('Bip01 Spine2').index
        outer=[v for v in opening];previous=outer;bridge_vertices=[]
        outer_points=[M@v.co for v in outer]
        for row in range(1,7):
            u=row/6;current=[]
            for v,q in zip(outer,outer_points):
                a=math.atan2(q.x/.07,(.007-q.y)/.08)
                inner=Vector((.047*math.sin(a),.007-.051*math.cos(a),1.483+.016*(1-math.cos(a))/2))
                point=q.lerp(inner,u);point.z+=.0008*math.sin(math.pi*u)
                nv=bm.verts.new(I@point);weights={group:weight*(1-u) for group,weight in v[deform].items()};weights[spine]=weights.get(spine,0)+u
                for group,weight in weights.items():nv[deform][group]=weight
                current.append(nv)
                if row<6:bridge_vertices.append(nv)
            for j in range(len(outer)):
                k=(j+1)%len(outer)
                face=bm.faces.new((previous[j],previous[k],current[k],current[j]));face.material_index=seat_index;face.smooth=True
            previous=current
        for iteration in range(10):bmesh.ops.smooth_vert(bm,verts=bridge_vertices,factor=.6,use_axis_x=True,use_axis_y=True,use_axis_z=True)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
        for polygon in o.data.polygons:polygon.use_smooth=True
        # A broad stripe rhythm, UV-baked into only this garment slot.
        N=polo.node_tree.nodes;L=polo.node_tree.links
        tc=N.new('ShaderNodeTexCoord');tc.object=human
        sep=N.new('ShaderNodeSeparateXYZ');L.new(tc.outputs['Object'],sep.inputs[0])
        scale=N.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=1/.16;L.new(sep.outputs['Z'],scale.inputs[0])
        mod=N.new('ShaderNodeMath');mod.operation='FRACT';L.new(scale.outputs[0],mod.inputs[0])
        ramp=N.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
        ramp.color_ramp.elements[0].color=(.055,.090,.17,1);ramp.color_ramp.elements[1].position=.5;ramp.color_ramp.elements[1].color=(.76,.735,.66,1)
        L.new(mod.outputs[0],ramp.inputs[0]);bake_color(o,ji,polo,ramp.outputs[0],here,'stylized-polo-stripes',4096)
    from head_refinement import build_head
    human['head_refinement']=str(build_head(G,here,skin))
    # A connected folded collar wraps the neck and rests against the shoulders.
    original=meshes[0];M=A@original.matrix_world
    torso=[M@v.co for v in original.data.vertices if abs((M@v.co).x)<.28]
    def front_y(x,z):
        near=sorted((v for v in torso if v.y<-.025),key=lambda v:(v.x-x)**2+(v.z-z)**2)[:5]
        return sum(v.y for v in near)/len(near)-.004
    vs=[];fs=[];steps=64
    for i in range(steps+1):
        th=.38+(2*math.pi-.76)*i/steps;f=math.cos(th)
        inner=Vector((.058*math.sin(th),.012-.067*math.cos(th),1.487+.014*(1-f)/2))
        outer=Vector((.106*math.sin(th),.012-.137*math.cos(th),1.448+.018*(1-f)/2))
        edge=min(i,steps-i)/steps
        if edge<.1:outer.z-=.018*(1-edge/.1)
        if f>.25:outer.y-=.012*f
        for k in range(6):
            u=k/5;p=inner.lerp(outer,u);p.z+=.0035*math.sin(math.pi*u);vs.append(p)
        if i:
            for k in range(5):fs.append(((i-1)*6+k,(i-1)*6+k+1,i*6+k+1,i*6+k))
    collar=G.mesh('Human integrated soft polo collar',vs,fs,cream,'Bip01 Spine2')
    bpy.context.view_layer.objects.active=collar
    mod=collar.modifiers.new('Soft folded collar','SUBSURF');mod.levels=2
    bpy.ops.object.modifier_move_to_index(modifier=mod.name,index=0);bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=collar.modifiers.new('Soft cotton edge','SOLIDIFY');mod.thickness=.0012
    bpy.ops.object.modifier_move_to_index(modifier=mod.name,index=0);bpy.ops.object.modifier_apply(modifier=mod.name)
    # Smooth cuffs cover the old atlas material boundary, not the wrist joint.
    for side in ['L','R']:
        wrist=(A@rig.matrix_world@rig.data.bones['Bip01 '+side+' Hand'].matrix_local).translation
        elbow=(A@rig.matrix_world@rig.data.bones['Bip01 '+side+' Forearm'].matrix_local).translation
        direction=(wrist-elbow).normalized()
        pp=[wrist-direction*t for t in [.070,.064,.048,.028,.022]]
        G.tube('Human smooth rib cuff',pp,[.032,.035,.035,.032,.029],cream,'Bip01 '+side+' Forearm',sides=40)
    vs=[];fs=[]
    for i,z in enumerate([1.445,1.42,1.395,1.37,1.345]):
        for x in [-.013,.013]:vs.append((x,front_y(x,z)-.002,z))
        if i:fs.append(((i-1)*2,(i-1)*2+1,i*2+1,i*2))
    G.mesh('Human ivory polo placket',vs,fs,cream,'Bip01 Spine2')
    for z in [1.409,1.371]:G.ellipsoid('Human polo button',(0,front_y(0,z)-.004,z),(.003,.0016,.003),cream,'Bip01 Spine2',rings=10,sectors=16)
    from garment_refinement import refine_clothing
    garment_audit=refine_clothing(human,rig,meshes,G,here,{'polo':polo,'cream':cream,'navy':navy,'pants':pants,'shoes':shoes,'skin':skin})
    human['garment_refinement']=str(garment_audit)
    G.join_by_material()
    human['identity']='Stylized adult character of Zhilin He, designed from selected imagegen concept and supplied photos; deliberately animated, not a scan'
    human['art_direction']='Adult animation proportions; sculpted full cheeks and smile; almond eyes; champagne frames; asymmetric solid S-wave hair; blue/ivory broad-stripe polo'
    human['outfit']='Oversized blue and ivory horizontal stripe polo, continuous soft collar, wide charcoal trousers, ivory sneakers'
    print('STYLIZED_ACTOR_READY',flush=True)
