"""Isolated material baking and identity-preserving face projection.

Only the chosen material remains on each temporary bake mesh. This prevents
Blender's use_clear option from clearing unrelated packed texture images.
"""
import bpy,bmesh,math
from mathutils import Vector

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
