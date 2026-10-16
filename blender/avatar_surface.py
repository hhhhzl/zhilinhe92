"""Isolated material baking and identity-preserving face projection.

Only the chosen material remains on each temporary bake mesh. This prevents
Blender's use_clear option from clearing unrelated packed texture images.
"""
import bpy,bmesh,math
from mathutils import Vector

def bake_channel(original,material_index,mat,here,name,kind,socket=None,size=2048):
    """Bake an isolated PBR data channel without clearing another material."""
    n=mat.node_tree.nodes;l=mat.node_tree.links
    output=next(x for x in n if x.type=='OUTPUT_MATERIAL');p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    if kind!='NORMAL':
        emit=n.new('ShaderNodeEmission');l.new(socket,emit.inputs['Color']);l.new(emit.outputs[0],output.inputs['Surface'])
    image=bpy.data.images.new(name,width=size,height=size,alpha=False)
    image.colorspace_settings.name='Non-Color'
    target=n.new('ShaderNodeTexImage');target.image=image;n.active=target
    temp=original.copy();temp.data=original.data.copy();bpy.context.collection.objects.link(temp);temp.modifiers.clear()
    bm=bmesh.new();bm.from_mesh(temp.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=material_index],context='FACES');bm.to_mesh(temp.data);bm.free()
    temp.data.materials.clear();temp.data.materials.append(mat)
    for polygon in temp.data.polygons:polygon.material_index=0
    bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
    scene=bpy.context.scene;engine=scene.render.engine;scene.render.engine='CYCLES';scene.cycles.samples=1
    bpy.ops.object.bake(type='NORMAL' if kind=='NORMAL' else 'EMIT',margin=12,use_clear=True,normal_space='TANGENT')
    image.filepath_raw=str(here/'textures'/(name+'.png'));image.file_format='PNG';image.save();image.pack()
    l.new(p.outputs[0],output.inputs['Surface'])
    if kind=='NORMAL':
        normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=1
        l.new(target.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs['Normal'])
    else:l.new(target.outputs['Color'],p.inputs[kind])
    bpy.data.objects.remove(temp,do_unlink=True);scene.render.engine=engine
    return image

def refine_skin(o,human,head_index,here):
    mat=o.data.materials[head_index];mat.name='Human Skin cinematic PBR'
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Specular IOR Level'].default_value=.34;p.inputs['IOR'].default_value=1.4
    p.inputs['Subsurface Weight'].default_value=.075
    p.inputs['Subsurface Radius'].default_value=(1.,.43,.24);p.inputs['Subsurface Scale'].default_value=.0015
    M=human.matrix_world.inverted()@o.matrix_world
    attr=o.data.color_attributes.new(name='SkinRoughness',type='FLOAT_COLOR',domain='CORNER')
    for poly in o.data.polygons:
        for li in poly.loop_indices:
            q=M@o.data.vertices[o.data.loops[li].vertex_index].co
            nose=math.exp(-(q.x/.028)**2-((q.z-1.614)/.024)**2)
            lip=math.exp(-(q.x/.029)**2-((q.z-1.578)/.010)**2)
            forehead=math.exp(-((q.z-1.684)/.027)**2)
            value=.52-.14*nose-.13*lip-.08*forehead
            attr.data[li].color=(value,value,value,1)
    factor=n.new('ShaderNodeVertexColor');factor.layer_name='SkinRoughness'
    bake_channel(o,head_index,mat,here,'zhilin-skin-roughness','Roughness',factor.outputs[0])
    o.data.color_attributes.remove(o.data.color_attributes.get('SkinRoughness'))
    tc=n.new('ShaderNodeTexCoord');tc.object=human
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2100;noise.inputs['Detail'].default_value=2
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.00011
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    if p.inputs['Normal'].is_linked:l.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(bump.outputs['Normal'],p.inputs['Normal'])
    bake_channel(o,head_index,mat,here,'zhilin-skin-normal','NORMAL')

def refine_cotton(o,human,index,here):
    mat=o.data.materials[index];mat.name='Human Polo cotton pique PBR'
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.82;p.inputs['Sheen Weight'].default_value=.22
    p.inputs['Sheen Roughness'].default_value=.68
    tc=n.new('ShaderNodeTexCoord');tc.object=human
    noise=n.new('ShaderNodeTexVoronoi');noise.distance='EUCLIDEAN';noise.feature='DISTANCE_TO_EDGE';noise.inputs['Scale'].default_value=1600
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.00020
    l.new(noise.outputs['Distance'],bump.inputs['Height'])
    if p.inputs['Normal'].is_linked:l.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(bump.outputs[0],p.inputs['Normal'])
    bake_channel(o,index,mat,here,'zhilin-polo-normal','NORMAL')

def separate_eyes(o,head_index):
    """Use the real rigged eyeball surface; never add a floating glass lid."""
    groups={g.index for g in o.vertex_groups if g.name in ['Bip01 LEye','Bip01 REye']}
    eye=o.data.materials[head_index].copy();eye.name='Human Eyes iris and sclera PBR'
    n=eye.node_tree.nodes;l=eye.node_tree.links;p=n.get('Principled BSDF')
    for socket in ['Roughness','Normal']:
        for link in list(p.inputs[socket].links):l.remove(link)
    p.inputs['Roughness'].default_value=.24;p.inputs['IOR'].default_value=1.376
    p.inputs['Specular IOR Level'].default_value=.34
    p.inputs['Subsurface Weight'].default_value=0;p.inputs['Transmission Weight'].default_value=0
    o.data.materials.append(eye);index=len(o.data.materials)-1;count=0
    for poly in o.data.polygons:
        if poly.material_index!=head_index:continue
        weight=sum(g.weight for vi in poly.vertices for g in o.data.vertices[vi].groups if g.group in groups)/len(poly.vertices)
        if weight>.30:poly.material_index=index;count+=1
    print('REAL_EYEBALL_FACES',count,flush=True)

def bake_color(original,material_index,mat,color_socket,here,name,size=2048):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    principled=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    emission=nodes.new('ShaderNodeEmission');links.new(color_socket,emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
    image=bpy.data.images.new(name,width=size,height=size,alpha=False)
    target=nodes.new('ShaderNodeTexImage');target.image=image;nodes.active=target
    temp=original.copy();temp.data=original.data.copy();bpy.context.collection.objects.link(temp);temp.modifiers.clear()
    bm=bmesh.new();bm.from_mesh(temp.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=material_index],context='FACES');bm.to_mesh(temp.data);bm.free()
    temp.data.materials.clear();temp.data.materials.append(mat)
    for polygon in temp.data.polygons:polygon.material_index=0
    bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
    scene=bpy.context.scene;engine=scene.render.engine;scene.render.engine='CYCLES';scene.cycles.samples=1
    bpy.ops.object.bake(type='EMIT',margin=8,use_clear=True)
    image.filepath_raw=str(here/'textures'/(name+'.png'));image.file_format='PNG';image.save();image.pack()
    links.new(principled.outputs[0],output.inputs['Surface']);links.new(target.outputs['Color'],principled.inputs['Base Color'])
    bpy.data.objects.remove(temp,do_unlink=True);scene.render.engine=engine
    return image

def project_face(o,human,head_index,here):
    """Align a neutral-lit identity photo to the morphed eye/nose/lip rows."""
    M=human.matrix_world.inverted()@o.matrix_world
    primary_index=o.data.uv_layers.active_index
    o.data.uv_layers.new(name='FaceIdentityProjection')
    mask=o.data.color_attributes.new(name='IdentityBlend',type='FLOAT_COLOR',domain='CORNER')
    # Adding a corner attribute reallocates CustomData; reacquire UV RNA handles.
    projected=o.data.uv_layers.get('FaceIdentityProjection')
    rows=[(1.49,.91),(1.523,.78),(1.577,.635),(1.608,.55),(1.6474,.420),(1.668,.355),(1.705,.22),(1.80,.025)]
    def smooth(a,b,x):
        u=max(0.,min(1.,(x-a)/(b-a)));return u*u*(3-2*u)
    for p in o.data.polygons:
        for li in p.loop_indices:
            q=M@o.data.vertices[o.data.loops[li].vertex_index].co
            z=min(rows[-1][0],max(rows[0][0],q.z))
            for (a,aa),(b,bb) in zip(rows,rows[1:]):
                if a<=z<=b:top=aa+(bb-aa)*(z-a)/(b-a);break
            projected.data[li].uv=(.491+q.x/.292,1-top)
            # The lower portrait narrows toward the chin. Fade to side albedo
            # before projected samples reach its neutral studio background.
            face_width=.044+.032*smooth(1.535,1.625,q.z)
            weight=(1-smooth(face_width-.015,face_width,abs(q.x)))*smooth(.025,.072,-q.y)*smooth(1.505,1.535,q.z)*(1-smooth(1.70,1.735,q.z))
            mask.data[li].color=(weight,weight,weight,1.)
    o.data.uv_layers.active_index=primary_index
    mat=o.data.materials[head_index];n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    source=p.inputs['Base Color'].links[0].from_socket
    uv=n.new('ShaderNodeUVMap');uv.uv_map='FaceIdentityProjection'
    photo=n.new('ShaderNodeTexImage');photo.image=bpy.data.images.load(str(here/'textures'/'zhilin-face-projection.png'));photo.image.pack();l.new(uv.outputs[0],photo.inputs['Vector'])
    factor=n.new('ShaderNodeVertexColor');factor.layer_name='IdentityBlend'
    mix=n.new('ShaderNodeMixRGB');l.new(factor.outputs['Color'],mix.inputs[0]);l.new(source,mix.inputs[1]);l.new(photo.outputs['Color'],mix.inputs[2])
    bake_color(o,head_index,mat,mix.outputs[0],here,'zhilin-face-baked')
    for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
    return {'eye_row':1.6474,'nose_tip_row':1.608,'lip_row':1.577,'projection':'Landmark-aligned frontal reference; side/neck blend to original UV atlas'}
