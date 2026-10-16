"""Native skinned mesh helpers for the stylized character; no image impostors."""
import bpy,math
from mathutils import Vector,Matrix

class Geometry:
    def __init__(self,human,rig):self.human=human;self.rig=rig;self.objects=[]
    def material(self,name,color,rough=.65,metal=0):
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
        p.inputs['Specular IOR Level'].default_value=.26
        return m
    def mesh(self,name,verts,faces,material,bone='Bip01 Head'):
        d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.materials.append(material)
        o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
        o.parent=self.human;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
        vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(d.vertices))),1.,'REPLACE')
        mod=o.modifiers.new('Original performer skeleton','ARMATURE');mod.object=self.rig
        for p in d.polygons:p.use_smooth=True
        self.objects.append(o);return o
    def ellipsoid(self,name,center,scale,material,bone='Bip01 Head',rings=18,sectors=36):
        verts=[];faces=[];center=Vector(center)
        for i in range(rings+1):
            phi=math.pi*i/rings
            for j in range(sectors):
                theta=2*math.pi*j/sectors
                verts.append(center+Vector((scale[0]*math.sin(phi)*math.cos(theta),scale[1]*math.sin(phi)*math.sin(theta),scale[2]*math.cos(phi))))
                if i:faces.append(tuple(reversed(((i-1)*sectors+j,(i-1)*sectors+(j+1)%sectors,i*sectors+(j+1)%sectors,i*sectors+j))))
        return self.mesh(name,verts,faces,material,bone)
    def tube(self,name,points,radii,material,bone='Bip01 Head',sides=10,flatten=1.):
        verts=[];faces=[]
        for i,p in enumerate(points):
            p=Vector(p);t=(Vector(points[min(len(points)-1,i+1)])-Vector(points[max(0,i-1)])).normalized()
            helper=Vector((0,1,0)) if abs(t.y)<.9 else Vector((1,0,0))
            u=t.cross(helper).normalized();v=t.cross(u).normalized()
            for j in range(sides):
                a=2*math.pi*j/sides;verts.append(p+radii[i]*(u*math.cos(a)+v*math.sin(a)*flatten))
            if i:
                for j in range(sides):faces.append(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j))
        faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(points)-1)*sides+j for j in range(sides)))
        return self.mesh(name,verts,faces,material,bone)
    def bezier_lock(self,name,controls,width,depth,material):
        p0,p1,p2,p3=[Vector(p) for p in controls];verts=[];faces=[];steps=26;sides=16
        for i in range(steps+1):
            t=i/steps;p=p0*(1-t)**3+p1*3*(1-t)**2*t+p2*3*(1-t)*t*t+p3*t**3
            tangent=((p1-p0)*3*(1-t)**2+(p2-p1)*6*(1-t)*t+(p3-p2)*3*t*t).normalized()
            outward=Vector((p.x,p.y-.005,(p.z-1.69)*.8)).normalized()
            across=outward.cross(tangent).normalized();normal=tangent.cross(across).normalized()
            taper=max(.025,math.sin(math.pi*(.12+.86*t)))
            for j in range(sides):
                a=2*math.pi*j/sides
                verts.append(p+across*(width*taper*math.cos(a))+normal*(depth*taper*math.sin(a)))
            if i:
                for j in range(sides):faces.append(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j))
        faces.append(tuple(reversed(range(sides))));faces.append(tuple(steps*sides+j for j in range(sides)))
        return self.mesh(name,verts,faces,material)
    def join_by_material(self):
        groups={}
        for o in self.objects:groups.setdefault(o.data.materials[0],[]).append(o)
        for material,objects in groups.items():
            bpy.ops.object.select_all(action='DESELECT')
            for o in objects:o.select_set(True)
            bpy.context.view_layer.objects.active=objects[0]
            if len(objects)>1:bpy.ops.object.join()
            objects[0].name='Human_'+material.name.replace(' ','_');objects[0].select_set(False)
