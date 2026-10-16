"""Photo-referenced appearance adaptation; keeps the original rig and Echo.

The result is an approximate digital likeness, not a scan. Head albedo was
edited with built-in ImageGen from the owner's authorized reference pictures.
Clothing, eyewear and hair are native geometry/material adaptations.
"""
import bpy, math, random, os
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
    jacket=material('Zhilin fuzzy navy forest and yellow plaid',(.025,.05,.035),.95)
    jp=jacket.node_tree.nodes.get('Principled BSDF');color=jacket.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Outfit'
    # Vertex colors are replaced by a UV-baked procedural textile below.
    # Reuse the source's fabric micro-normal; it remains a standard glTF map.
    norm=bpy.data.images.get('m003_body_normal.tga')
    if norm is not None:
        n=jacket.node_tree.nodes.new('ShaderNodeTexImage');n.image=norm
        nm=jacket.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.8
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
    zipper=material('Dark jacket zip and trim',(.028,.033,.038),.58,.12)
    actor_inv=human.matrix_world.inverted()
    def smooth(a,b,x):
        t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
    def plaid(v):
        x,y,z=v;u=((x+.031)/.235)%1;t=((z+.017)/.235)%1
        a=(.014,.024,.044);b=(.038,.086,.059);gold=(.31,.28,.095)
        mix=(.25 if u<.5 else .65)*(.65 if t<.5 else 1.2)
        base=[a[k]*(1-mix)+b[k]*mix for k in range(3)]
        sy=max(0.,1-abs(t-.48)/.115);sx=max(0.,1-abs(u-.48)/.095)
        stripe=max(sy*.78,sx*.40)
        grain=1+.09*math.sin(x*1145+z*775)*math.sin(z*976-y*637)
        return tuple((base[k]*(1-stripe)+gold[k]*stripe)*grain for k in range(3))+(1,)
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
                if center.z>1.66 and luminance<.38:p.material_index=scalpi
            elif p.material_index==alphai:hairverts.update(p.vertices)
        for v in o.data.vertices:
            q=M@v.co
            if v.index in garment:
                n=(M.to_3x3()@v.normal).normalized()
                hand_weight=sum(g.weight for g in v.groups if any(k in groups[g.group] for k in ['Hand','Finger']))
                taper=(1-min(1.,hand_weight/.35))*smooth(.835,.93,q.z)
                q+=n*(.008+(.007 if q.z<1.32 else .003))*taper
                if abs(q.x)<.28:q.x*=1.06
            elif v.index in pantsverts:
                centre=.112 if q.x>0 else -.112
                widen=.28*(1-smooth(.73,.90,q.z))
                q.x=centre+(q.x-centre)*(1+widen);q.y*=1+widen*.60
            elif v.index in headverts and q.z>1.53:
                # Subtle contour adjustment only; eyelids/rig landmarks remain.
                cheek=math.exp(-((q.z-1.602)/.045)**2)*smooth(.015,.060,abs(q.x))
                q.x*=1+.055*cheek
                nose=math.exp(-(q.x/.025)**2-((q.z-1.616)/.034)**2)*smooth(.08,.13,-q.y)
                q.y+=.009*nose
                jaw=math.exp(-((q.z-1.558)/.032)**2)
                q.x*=1+.10*jaw

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
        o.data.update()
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
        cx=sign*.036;cz=1.646
        points=[(cx+.030*math.cos(a),-.136+.004*math.cos(a)**2,cz+.027*math.sin(a)) for a in [2*math.pi*i/64 for i in range(65)]]
        accessories.append(tube('Human round spectacle rim',points,[.00105]*len(points),frame))
        vs=[(cx,-.135,cz)]+[(cx+.029*math.cos(a),-.134,cz+.026*math.sin(a)) for a in [2*math.pi*i/64 for i in range(64)]]
        accessories.append(mesh('Human clear spectacle lens',vs,[(0,i+1,(i+1)%64+1) for i in range(64)],glass))
        accessories.append(tube('Human spectacle temple',[(sign*.065,-.132,1.65),(sign*.079,-.09,1.65),(sign*.087,-.015,1.647),(sign*.085,.026,1.63)],[.0013]*4,frame))
    accessories.append(tube('Human spectacle bridge',[(-.008,-.140,1.65),(0,-.146,1.655),(.008,-.140,1.65)],[.001]*3,frame))
    # Bake a continuous fuzzy plaid into the original garment UVs. This keeps
    # sharp fabric-scale checks in glTF without reliance on runtime shaders.
    original=meshes[0]
    N=jacket.node_tree.nodes;L=jacket.node_tree.links
    tc=N.new('ShaderNodeTexCoord');tc.object=human
    sep=N.new('ShaderNodeSeparateXYZ');L.new(tc.outputs['Object'],sep.inputs[0])
    def wave(socket):
        mul=N.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=1/.235;L.new(socket,mul.inputs[0])
        mod=N.new('ShaderNodeMath');mod.operation='PINGPONG';mod.inputs[1].default_value=.5;L.new(mul.outputs[0],mod.inputs[0])
        ramp=N.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements.remove(r.elements[1])
        r.interpolation='CONSTANT'
        stops=[(0.,(.013,.024,.043,1)),(.17,(.026,.067,.045,1)),(.29,(.34,.30,.105,1)),(.34,(.026,.067,.045,1)),(.47,(.013,.024,.043,1)),(.5,(.013,.024,.043,1))]
        for i,(pos,c) in enumerate(stops):e=r.elements[0] if i==0 else r.elements.new(pos);e.position=pos;e.color=c
        L.new(mod.outputs[0],ramp.inputs[0]);return ramp.outputs[0]
    wx,wz=wave(sep.outputs['X']),wave(sep.outputs['Z'])
    mix=N.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.46;L.new(wz,mix.inputs[1]);L.new(wx,mix.inputs[2])
    noise=N.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=850;noise.inputs['Detail'].default_value=2;L.new(tc.outputs['Object'],noise.inputs['Vector'])
    grain=N.new('ShaderNodeMixRGB');grain.blend_type='MULTIPLY';grain.inputs[0].default_value=.26;L.new(mix.outputs[0],grain.inputs[1]);L.new(noise.outputs['Fac'],grain.inputs[2])
    def mathnode(op,a,b=None):
        n=N.new('ShaderNodeMath');n.operation=op
        if hasattr(a,'node'):L.new(a,n.inputs[0])
        else:n.inputs[0].default_value=a
        if b is not None:
            if hasattr(b,'node'):L.new(b,n.inputs[1])
            else:n.inputs[1].default_value=b
        return n.outputs[0]
    width=mathnode('ADD',mathnode('MULTIPLY',mathnode('SUBTRACT',1.43,sep.outputs['Z']),.10),.021)
    centre=mathnode('LESS_THAN',mathnode('ABSOLUTE',sep.outputs['X']),width)
    front=mathnode('LESS_THAN',sep.outputs['Y'],-.04)
    lower=mathnode('GREATER_THAN',sep.outputs['Z'],.84);upper=mathnode('LESS_THAN',sep.outputs['Z'],1.43)
    mask=mathnode('MULTIPLY',mathnode('MULTIPLY',centre,front),mathnode('MULTIPLY',lower,upper))
    inner=N.new('ShaderNodeMixRGB');L.new(mask,inner.inputs[0]);L.new(grain.outputs[0],inner.inputs[1]);inner.inputs[2].default_value=(.009,.012,.017,1)
    emission=N.new('ShaderNodeEmission');L.new(inner.outputs[0],emission.inputs['Color'])
    output=next(n for n in N if n.type=='OUTPUT_MATERIAL');L.new(emission.outputs[0],output.inputs['Surface'])
    tex=bpy.data.images.new('zhilin-plaid-baked',width=2048,height=2048,alpha=False)
    target=N.new('ShaderNodeTexImage');target.image=tex;N.active=target
    temp=original.copy();temp.data=original.data.copy();bpy.context.collection.objects.link(temp);temp.modifiers.clear()
    import bmesh
    bm=bmesh.new();bm.from_mesh(temp.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=ji],context='FACES');bm.to_mesh(temp.data);bm.free()
    # Bake clears every active image in material slots, even unused slots.
    # Isolate the garment slot so face, hair and skin textures remain intact.
    temp.data.materials.clear();temp.data.materials.append(jacket)
    for polygon in temp.data.polygons:polygon.material_index=0
    bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
    previous_engine=bpy.context.scene.render.engine;bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1
    bpy.ops.object.bake(type='EMIT',margin=8,use_clear=True)
    tex.filepath_raw=str(here/'textures'/'zhilin-plaid.png');tex.file_format='PNG';tex.save();tex.pack()
    L.new(jp.outputs['BSDF'],output.inputs['Surface']);L.new(target.outputs['Color'],jp.inputs['Base Color'])
    bpy.data.objects.remove(temp,do_unlink=True);bpy.context.scene.render.engine=previous_engine
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
    human['outfit']='Navy forest-green yellow plaid fleece jacket, black inner, charcoal loose trousers, off-white sneakers'
