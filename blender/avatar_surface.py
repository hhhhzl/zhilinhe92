"""Bake only the selected garment material; never clear another image.

Native procedural stripes are the only raster texture in the cartoon actor.
"""
import bpy,bmesh

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
