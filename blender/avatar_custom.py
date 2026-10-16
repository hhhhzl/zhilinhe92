"""Photo-referenced appearance adaptation; keeps the original rig and Echo.

The result is an approximate digital likeness, not a scan. Head albedo was
edited with built-in ImageGen from the owner's authorized reference pictures.
Clothing, eyewear and hair are native geometry/material adaptations.
"""
import bpy, math, random, os
from avatar_surface import bake_color,project_face
from mathutils import Vector, Matrix

def customize(human,rig,meshes,here):
    rng=random.Random(719)
    def material(name,color,rough=.65,metal=0,alpha=1):
        m=bpy.data.materials.new(name);m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*color,alpha)
        p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
        p.inputs['Alpha'].default_value=alpha
        if alpha<1:m.surface_render_method='DITHERED'
        return m
    jacket=material('Zhilin blue white striped cotton polo',(.05,.13,.28),.83)
    jp=jacket.node_tree.nodes.get('Principled BSDF');color=jacket.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Outfit'
    # Vertex colors are replaced by a UV-baked procedural textile below.
    # Reuse the source's fabric micro-normal; it remains a standard glTF map.
    norm=bpy.data.images.get('m003_body_normal.tga')
    if norm is not None:
        n=jacket.node_tree.nodes.new('ShaderNodeTexImage');n.image=norm
        nm=jacket.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.46
        jacket.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);jacket.node_tree.links.new(nm.outputs['Normal'],jp.inputs['Normal'])
    pants=material('Zhilin loose charcoal denim',(.035,.039,.045),.95)
    if norm is not None:
        n=pants.node_tree.nodes.new('ShaderNodeTexImage');n.image=norm
        nm=pants.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.75
        pants.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);pants.node_tree.links.new(nm.outputs['Normal'],pants.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
    shoes=material('Zhilin off-white sneaker upper',(.73,.70,.62),.81)
    soles=material('Zhilin warm white rubber sole',(.58,.56,.50),.9)
    black=material('Zhilin black cotton inner',(.009,.012,.017),.93)
    hairmats=[material('Zhilin black hair '+str(i),(.009+i*.003,.010+i*.003,.013+i*.003),.82) for i in range(3)]
    # Keep the source's precisely aligned hair atlas for its original scalp UVs.
    source=here.parents[2]/'work'/'rocketbox-source'
    source=__import__('pathlib').Path(os.environ.get('HUMAN_ASSET_DIR',str(source)))
    hair_image=bpy.data.images.load(str(source/'Assets/Avatars/Adults/Male_Adult_02/Textures/m003_head_color.tga'),check_existing=False)
    if max(hair_image.size)>1024:hair_image.scale(1024,1024)
    hair_image.filepath_raw=str(here/'textures'/'zhilin-hair-albedo.jpg');hair_image.file_format='JPEG';hair_image.save();hair_image.pack()
    pixels=list(hair_image.pixels);hairw,hairh=hair_image.size
    hm=hairmats[0];hn=hm.node_tree.nodes;hl=hm.node_tree.links;hp=hn.get('Principled BSDF')
    hi=hn.new('ShaderNodeTexImage');hi.image=hair_image
    tint=hn.new('ShaderNodeMix');tint.data_type='RGBA';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
    tint.inputs[7].default_value=(.12,.14,.17,1);hl.new(hi.outputs['Color'],tint.inputs[6]);hl.new(tint.outputs[2],hp.inputs['Base Color'])
    frame=material('Zhilin thin champagne metal eyeglasses',(.48,.40,.29),.25,.72)
    glass=material('Zhilin clear spectacle lenses',(.77,.87,.88),.08,.0,.035)
    actor_inv=human.matrix_world.inverted()
    def smooth(a,b,x):
        t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
    for o in meshes:
        M=actor_inv@o.matrix_world;I=M.inverted()
        mats=o.data.materials
        ji=next(i for i,m in enumerate(mats) if 'navy' in m.name.lower())
        bodyi=next(i for i,m in enumerate(mats) if 'trousers' in m.name.lower())
        headidx=next(i for i,m in enumerate(mats) if 'skin' in m.name.lower())
        alphai=next(i for i,m in enumerate(mats) if 'hair and lashes' in m.name.lower())
        mats[ji]=jacket
        ids={}
        for k,m in [('pants',pants),('shoes',shoes),('soles',soles),('inner',black)]:mats.append(m);ids[k]=len(mats)-1
        mats.append(hairmats[0]);scalpi=len(mats)-1
        groups={g.index:g.name for g in o.vertex_groups}
        garment=set();headverts=set();pantsverts=set();hairverts=set()
        for p in o.data.polygons:
            vs=[o.data.vertices[i] for i in p.vertices];center=sum((M@v.co for v in vs),Vector())/len(vs)
            if p.material_index==ji:
                garment.update(p.vertices)
                opening=.018+max(0.,1.42-center.z)*.115
                # A smooth skinned opening is added over this cloth surface.
            elif p.material_index==bodyi:
                if center.z<.092:p.material_index=ids['soles'] if center.z<.028 else ids['shoes']
                elif center.z<.88:p.material_index=ids['pants'];pantsverts.update(p.vertices)
            elif p.material_index==headidx:
                headverts.update(p.vertices)
                uvdata=o.data.uv_layers.active.data
                uv=sum((uvdata[i].uv for i in p.loop_indices),__import__('mathutils').Vector((0.,0.)))/len(p.loop_indices)
                ix=min(hairw-1,max(0,int(uv.x*hairw)));iy=min(hairh-1,max(0,int(uv.y*hairh)));pi=(iy*hairw+ix)*4
                luminance=sum(pixels[pi:pi+3])/3
                # The new continuous scalp covers source hair. Do not classify
                # dark eyebrow pixels as hair geometry.
            elif p.material_index==alphai:hairverts.update(p.vertices)
        edge_materials={}
        for p in o.data.polygons:
            for e in p.edge_keys:edge_materials.setdefault(tuple(sorted(e)),set()).add(p.material_index)
        cloth_boundary=set()
        for e,indices in edge_materials.items():
            if ji in indices and len(indices)>1:cloth_boundary.update(e)
        for v in o.data.vertices:
            q=M@v.co
            if v.index in cloth_boundary:
                if q.z<1.0 and abs(q.x)<.29:q.z=.895
                elif abs(q.x)>.43:q.x=math.copysign(.572,q.x)
            if v.index in garment:
                n=(M.to_3x3()@v.normal).normalized()
                hand_weight=sum(g.weight for g in v.groups if any(k in groups[g.group] for k in ['Hand','Finger']))
                taper=(1-min(1.,hand_weight/.35))*smooth(.835,.93,q.z)
                q+=n*(.006+(.004 if q.z<1.32 else .002))*taper
                if abs(q.x)<.28:q.x*=1.06
            elif v.index in pantsverts:
                centre=.112 if q.x>0 else -.112
                widen=.28*(1-smooth(.73,.90,q.z))
                q.x=centre+(q.x-centre)*(1+widen);q.y*=1+widen*.60
            elif v.index in headverts and q.z>1.53:
                # Facial proportions follow the owner's full lower cheeks,
                # rounded chin, softer eye sockets and shorter rounded nose.
                front=smooth(.02,.075,-q.y)
                cheek=math.exp(-((q.z-1.607)/.037)**2)*smooth(.015,.060,abs(q.x))*front
                q.x*=1+.085*cheek
                q.y-=.0045*math.exp(-((abs(q.x)-.050)/.028)**2-((q.z-1.609)/.037)**2)*front
                jaw=math.exp(-((q.z-1.552)/.034)**2)*front
                q.x*=1+.20*jaw
                q.z+=.004*math.exp(-((q.z-1.535)/.026)**2)*front
                nose=math.exp(-(q.x/.029)**2-((q.z-1.615)/.025)**2)*front
                q.y+=.012*nose;q.z-=.008*nose
                q.x*=1+.10*math.exp(-((q.z-1.608)/.018)**2-(q.x/.025)**2)*front
                brow=math.exp(-((q.z-1.666)/.012)**2)*front
                q.y+=.002*brow
                lip=math.exp(-(q.x/.031)**2-((q.z-1.576)/.012)**2)*front
                q.z+=(.002 if q.z<1.576 else -.001)*lip
                q.y-=.0015*lip
                q.z+=.0017*math.exp(-((abs(q.x)-.024)/.009)**2-((q.z-1.575)/.011)**2)*front

            v.co=I@q
        # Align the generated skin atlas back to the source UV landmark rows.
        rows=[(0.,0.),(.12,.12),(.28,.28),(.35,.367),(.405,.431),(.55,.562),(.77,.77),(1.,1.)]
        uv=o.data.uv_layers.active.data
        for p in o.data.polygons:
            if p.material_index!=headidx:continue
            for li in p.loop_indices:
                u,v=uv[li].uv;top=1-v
                if top<.78 and u>.18:
                    for (a,aa),(b,bb) in zip(rows,rows[1:]):
                        if a<=top<=b:
                            uv[li].uv.y=1-(aa+(bb-aa)*(top-a)/(b-a));break
        for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
        # Remove legacy hair cards; a continuous textured hair shell below
        # avoids scalp holes and broken card silhouettes in close eye views.
        import bmesh
        bm=bmesh.new();bm.from_mesh(o.data)
        hidden=[f for f in bm.faces if f.material_index==alphai or (f.material_index==headidx and (M@f.calc_center_median()).z>1.705)]
        bmesh.ops.delete(bm,geom=hidden,context='FACES');bm.to_mesh(o.data);bm.free()
        o.data.update()
        project_face(o,human,headidx,here)
    def skin_object(o,bone='Bip01 Head'):
        # Mesh coordinates are actor-space metres, independent of FBX cm scale.
        o.parent=human;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
        vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(o.data.vertices))),1.,'REPLACE')
        mod=o.modifiers.new('Follow original human skeleton','ARMATURE');mod.object=rig
        for p in o.data.polygons:p.use_smooth=True
        return o
    def mesh(name,verts,faces,mat,bone='Bip01 Head'):
        d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.materials.append(mat)
        o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
        return skin_object(o,bone)
    def tube(name,points,radii,mat,bone='Bip01 Head',sides=6):
        verts=[];faces=[]
        for i,p in enumerate(points):
            p=Vector(p);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
            t.normalize();axis=Vector((0,0,1)) if abs(t.z)<.9 else Vector((1,0,0));u=t.cross(axis).normalized();v=t.cross(u).normalized()
            for j in range(sides):
                a=2*math.pi*j/sides;verts.append(p+radii[i]*(u*math.cos(a)+v*math.sin(a)))
            if i:
                for j in range(sides):faces.append(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j))
        return mesh(name,verts,faces,mat,bone)
    accessories=[]
    # Thin round frames sized from the existing eye spacing.
    for sign in [-1,1]:
        cx=sign*.034;cz=1.646
        points=[(cx+.027*math.cos(a),-.126+.003*math.cos(a)**2,cz+.024*math.sin(a)) for a in [2*math.pi*i/64 for i in range(65)]]
        accessories.append(tube('Human round spectacle rim',points,[.00105]*len(points),frame))
        vs=[(cx,-.125,cz)]+[(cx+.026*math.cos(a),-.124,cz+.023*math.sin(a)) for a in [2*math.pi*i/64 for i in range(64)]]
        accessories.append(mesh('Human clear spectacle lens',vs,[(0,i+1,(i+1)%64+1) for i in range(64)],glass))
        accessories.append(tube('Human spectacle temple',[(sign*.060,-.123,1.65),(sign*.079,-.09,1.65),(sign*.087,-.015,1.647),(sign*.085,.026,1.63)],[.0013]*4,frame))
    accessories.append(tube('Human spectacle bridge',[(-.008,-.129,1.65),(0,-.135,1.655),(.008,-.129,1.65)],[.001]*3,frame))
    # Soft cotton collar is a folded continuous strip, with two front points.
    collar_mat=material('Polo ivory cotton collar',(.74,.77,.76),.88)
    blue_trim=material('Polo deep blue placket',(.025,.070,.15),.83)
    original=meshes[0];M=actor_inv@original.matrix_world
    torso=[M@v.co for v in original.data.vertices if .28>abs((M@v.co).x)]
    def front_y(x,z):
        candidates=[v for v in torso if v.y<-.025]
        near=sorted(candidates,key=lambda v:(v.x-x)**2+(v.z-z)**2)[:5]
        return sum(v.y for v in near)/len(near)-.003
    verts=[];faces=[];steps=52
    for i in range(steps+1):
        th=.36+(2*math.pi-.72)*i/steps;f=math.cos(th)
        inner=Vector((.059*math.sin(th),.012-.073*math.cos(th),1.486+.014*(1-f)/2))
        outer=Vector((.091*math.sin(th),.012-.117*math.cos(th),1.451+.017*(1-f)/2))
        edge=min(i,steps-i)/steps
        if edge<.10:
            amount=1-edge/.10;outer.z-=.017*amount
        if f>.25:
            inner.y=front_y(inner.x,inner.z)-.006
            outer.y=front_y(outer.x,outer.z)-.008
        for k in range(4):
            u=k/3;p=inner.lerp(outer,u);p.z+=.006*math.sin(math.pi*u);verts.append(p)
        if i:
            for k in range(3):faces.append(((i-1)*4+k,(i-1)*4+k+1,i*4+k+1,i*4+k))
    collar=mesh('Human soft polo collar',verts,faces,collar_mat,'Bip01 Spine2')
    solid=collar.modifiers.new('Cotton collar thickness','SOLIDIFY');solid.thickness=.0015
    sub=collar.modifiers.new('Soft sewn collar edge','SUBSURF');sub.levels=2
    bpy.context.view_layer.objects.active=collar
    bpy.ops.object.modifier_move_to_index(modifier=sub.name,index=0);bpy.ops.object.modifier_apply(modifier=sub.name)
    bpy.ops.object.modifier_move_to_index(modifier=solid.name,index=0);bpy.ops.object.modifier_apply(modifier=solid.name)
    accessories.append(collar)
    bandverts=[];bandfaces=[]
    for i in range(65):
        th=.95+(2*math.pi-1.90)*i/64
        for row in range(3):
            z=1.474+row*.010
            bandverts.append((.066*math.sin(th),.012-.079*math.cos(th),z))
        if i:
            for row in range(2):bandfaces.append(((i-1)*3+row,(i-1)*3+row+1,i*3+row+1,i*3+row))
    accessories.append(mesh('Human soft inner collar stand',bandverts,bandfaces,collar_mat,'Bip01 Spine2'))
    vs=[]
    for z in [1.447,1.42,1.39,1.36,1.33]:
        for x in [-.013,.013]:vs.append((x,front_y(x,z)-.001,z))
    accessories.append(mesh('Human short polo placket',vs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(4)],blue_trim,'Bip01 Spine2'))
    for z in [1.402,1.355]:
        points=[(.0032*math.cos(a),front_y(0,z)-.003,z+.0032*math.sin(a)) for a in [2*math.pi*i/16 for i in range(17)]]
        accessories.append(tube('Human polo mother of pearl button',points,[.0012]*len(points),collar_mat,'Bip01 Spine2'))
    # Continuous dark wavy silhouette and broad textured curtain locks.
    hair=material('Zhilin wavy black textured hair',(.012,.014,.018),.93)
    hn=hair.node_tree.nodes;hl=hair.node_tree.links;hp=hn.get('Principled BSDF')
    hi=hn.new('ShaderNodeTexImage');hi.image=hair_image
    tint=hn.new('ShaderNodeMix');tint.data_type='RGBA';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[7].default_value=(.16,.17,.20,1)
    hl.new(hi.outputs[0],tint.inputs[6]);hl.new(tint.outputs[2],hp.inputs['Base Color']);hp.inputs['Specular IOR Level'].default_value=.10
    verts=[];faces=[];rings=25;segments=90
    for i in range(rings+1):
        for j in range(segments):
            th=2*math.pi*j/segments;f=math.cos(th)
            bottom=1.615+.050*max(f,0)+.040*math.exp(-(math.sin(th)/.25)**2)*max(f,0)
            phi=i/rings*math.acos((bottom-1.683)/.101)
            wave=1+.048*math.sin(th*12+phi*3)+.020*math.sin(th*27-phi*4)
            verts.append((.107*math.sin(phi)*math.sin(th)*wave,.008-(.104+.030*max(f,0))*math.sin(phi)*math.cos(th)*wave,1.683+.101*math.cos(phi)+.002*math.sin(th*18+phi*8)*math.sin(phi)))
            if i:faces.append(((i-1)*segments+j,(i-1)*segments+(j+1)%segments,i*segments+(j+1)%segments,i*segments+j))
    cap=mesh('Human full wavy hair silhouette',verts,faces,hair)
    uv=cap.data.uv_layers.new(name='Hair texture')
    for p in cap.data.polygons:
        for li in p.loop_indices:
            v=cap.data.loops[li].vertex_index;row,col=divmod(v,segments);uv.data[li].uv=(.035+.16*col/segments,.55+.38*row/rings)
    accessories.append(cap)
    # Asymmetric individual swept fibers replace the detached solid front cards.
    # The overlapping bundles begin on the crown and curl toward the temples.
    front_strands=[material('Natural front hair fiber '+str(i),(.012+i*.003,.010+i*.0025,.009+i*.002),.78) for i in range(3)]
    for sign in [-1,1]:
        for j in range(105):
            layer=j/104;phase=rng.uniform(-.6,.6);points=[];radii=[]
            rootx=.004+.017*(j%15)/14
            rooty=-.048+.053*layer
            endx=.076+.022*layer
            endz=1.663+.026*layer+(.007 if sign<0 else 0)
            for k in range(25):
                t=k/24;swell=math.sin(math.pi*t)
                x=sign*(rootx+(endx-rootx)*math.sin(t*math.pi/2)+.005*math.sin(t*8+phase)*swell)
                y=rooty*(1-t)+(-.093+.021*layer)*t-.050*swell+.003*math.sin(t*10+phase)*swell
                z=(1.776-.005*layer)*(1-t)+endz*t+.014*swell+.003*math.sin(t*9+phase)*swell
                points.append((x,y,z));radii.append(.00072*(.30+.70*swell))
            accessories.append(tube('Human swept front hair fiber',points,radii,front_strands[j%3],sides=4))
    # Fine swept strands break the continuous shell's broad specular highlight.
    # They are real skinned geometry, so their texture survives glTF export.
    strand_materials=[material('Natural dark hair strand '+str(i),(.009+i*.004,.008+i*.0035,.007+i*.003),.72) for i in range(3)]
    for j in range(360):
        th=2*math.pi*(j+.27)/360;f=math.cos(th)
        bottom=1.615+.050*max(f,0)+.040*math.exp(-(math.sin(th)/.25)**2)*max(f,0)
        end=math.acos((bottom-1.683)/.101);points=[];radii=[]
        for k in range(19):
            t=k/18;phi=.08+(end-.08)*t
            angle=th+.035*math.sin(phi*4+th*3)*t
            wave=1+.048*math.sin(angle*12+phi*3)+.020*math.sin(angle*27-phi*4)
            points.append((.108*math.sin(phi)*math.sin(angle)*wave,.008-(.105+.030*max(math.cos(angle),0))*math.sin(phi)*math.cos(angle)*wave,1.683+.102*math.cos(phi)+.002*math.sin(angle*18+phi*8)*math.sin(phi)))
            radii.append(.00045*(.5+.5*math.sin(math.pi*t)))
        accessories.append(tube('Human fine wavy hair strand',points,radii,strand_materials[j%3],sides=4))
    # Fine blue/ivory horizontal bands follow the cloth rather than world space
    # after baking, so their scale stays consistent through the animation.
    N=jacket.node_tree.nodes;L=jacket.node_tree.links
    tc=N.new('ShaderNodeTexCoord');tc.object=human
    sep=N.new('ShaderNodeSeparateXYZ');L.new(tc.outputs['Object'],sep.inputs[0])
    scale=N.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=1/.090;L.new(sep.outputs['Z'],scale.inputs[0])
    mod=N.new('ShaderNodeMath');mod.operation='FRACT';L.new(scale.outputs[0],mod.inputs[0])
    ramp=N.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    ramp.color_ramp.elements[0].color=(.025,.10,.27,1);ramp.color_ramp.elements[1].position=.50;ramp.color_ramp.elements[1].color=(.77,.80,.78,1);L.new(mod.outputs[0],ramp.inputs[0])
    noise=N.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1050;noise.inputs['Detail'].default_value=2;L.new(tc.outputs['Object'],noise.inputs['Vector'])
    grain=N.new('ShaderNodeMixRGB');grain.blend_type='MULTIPLY';grain.inputs[0].default_value=.10;L.new(ramp.outputs[0],grain.inputs[1]);L.new(noise.outputs['Fac'],grain.inputs[2])
    bake_color(original,ji,jacket,grain.outputs[0],here,'zhilin-polo')
    # Join accessories by material to keep draw calls bounded, retaining weights.
    by_material={}
    for o in accessories:by_material.setdefault(o.data.materials[0],[]).append(o)
    for mat,group in by_material.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        if len(group)>1:bpy.ops.object.join()
        group[0].name='Human_'+mat.name.replace(' ','_')
        group[0].select_set(False)
    human['identity']='Photo-referenced digital likeness of Zhilin He; approximate, not a 3D scan'
    human['outfit']='Relaxed blue and ivory horizontal stripe cotton polo, folded collar, short button placket, charcoal loose trousers, off-white sneakers'
