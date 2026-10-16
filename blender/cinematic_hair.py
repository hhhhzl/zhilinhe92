"""Layered, skinned photographic hair cards with sparse geometric flyaways.

The RGBA atlas is a built-in ImageGen asset. Its real alpha and diffuse fiber
detail are retained; the cap is only an occlusion underlayer, not the hairstyle.
"""
import bpy,math,random
from mathutils import Vector

def build_hair(here,mesh,tube,material):
    rng=random.Random(8128);objects=[]
    scalp=material('Human Hair underlayer',(.009,.007,.006),.90)
    hair=material('Human Hair photographic cards',(.03,.022,.018),.73)
    n=hair.node_tree.nodes;l=hair.node_tree.links;p=n.get('Principled BSDF')
    atlas=bpy.data.images.load(str(here/'textures'/'zhilin-hair-cards.png'));atlas.pack()
    tex=n.new('ShaderNodeTexImage');tex.image=atlas
    l.new(tex.outputs['Color'],p.inputs['Base Color'])
    cut=n.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.20
    l.new(tex.outputs['Alpha'],cut.inputs[0]);l.new(cut.outputs[0],p.inputs['Alpha'])
    hair.surface_render_method='DITHERED';hair.use_backface_culling=False
    p.inputs['Specular IOR Level'].default_value=.17
    p.inputs['Anisotropic'].default_value=.65
    p.inputs['Anisotropic Rotation'].default_value=.25
    sn=scalp.node_tree.nodes;sl=scalp.node_tree.links;sp=sn.get('Principled BSDF')
    st=sn.new('ShaderNodeTexImage');st.image=atlas;sl.new(st.outputs['Color'],sp.inputs['Base Color'])
    sp.inputs['Specular IOR Level'].default_value=.12
    # Bake the atlas's fine strand relief once on a flat UV target. The runtime
    # receives a normal texture rather than unsupported procedural bump nodes.
    from avatar_surface import bake_channel
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.00015
    l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    d=bpy.data.meshes.new('Hair atlas bake target');d.from_pydata([(-.1,0,0),(.1,0,0),(.1,0,.2),(-.1,0,.2)],[],[(0,1,2,3)])
    d.materials.append(hair);target=bpy.data.objects.new('Hair atlas bake target',d);bpy.context.collection.objects.link(target)
    uv=d.uv_layers.new(name='Atlas')
    for i,value in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=value
    bake_channel(target,0,hair,here,'zhilin-hair-normal','NORMAL')
    bpy.data.objects.remove(target,do_unlink=True)
    def bottom(th):
        f=max(0,math.cos(th))
        return 1.616+.034*f+.049*math.exp(-(math.sin(th)/.38)**2)*f
    def surface(th,phi,offset=0):
        w=1+.017*math.sin(7*th+phi*3)+.010*math.sin(th*13-phi*5)
        return Vector(((.101+offset)*math.sin(phi)*math.sin(th)*w,
            .008-(.102+.024*max(0,math.cos(th))+offset)*math.sin(phi)*math.cos(th)*w,
            1.683+(.095+offset)*math.cos(phi)))
    verts=[];faces=[];rings=22;sectors=72
    for i in range(rings+1):
        for j in range(sectors):
            th=2*math.pi*j/sectors;phi=i/rings*math.acos((bottom(th)-1.683)/.095)
            verts.append(surface(th,phi))
            if i:faces.append(tuple(reversed(((i-1)*sectors+j,(i-1)*sectors+(j+1)%sectors,i*sectors+(j+1)%sectors,i*sectors+j))))
    cap=mesh('Human hidden scalp underlayer',verts,faces,scalp);uv=cap.data.uv_layers.new(name='Continuous scalp fibers')
    for face in cap.data.polygons:
        for li in face.loop_indices:
            v=cap.data.loops[li].vertex_index;r,c=divmod(v,sectors)
            # The opaque underlayer must never sample the transparent atlas
            # gutters/tips: those pixels have RGB zero despite ignored alpha.
            uv.data[li].uv=(.082+.090*c/sectors,.94-.72*r/rings)
    objects.append(cap)
    def card(name,points,width,column,phase):
        verts=[];faces=[];rows=len(points);cols=5
        for i,p in enumerate(points):
            t=i/(rows-1);tangent=points[min(rows-1,i+1)]-points[max(0,i-1)]
            outward=Vector((p.x,(p.y-.008)*.9,(p.z-1.683)*.65)).normalized()
            side=tangent.cross(outward).normalized()
            breadth=width*(.64+.36*math.sin(math.pi*t))
            for j in range(cols):
                u=2*j/(cols-1)-1
                q=p+side*u*breadth+outward*(.0025*(1-u*u)+.0012*math.sin(t*7+phase)*u)
                verts.append(q)
            if i:
                for j in range(cols-1):faces.append(((i-1)*cols+j,(i-1)*cols+j+1,i*cols+j+1,i*cols+j))
        o=mesh(name,verts,faces,hair);uv=o.data.uv_layers.new(name='Photographic strand alpha')
        for face in o.data.polygons:
            for li in face.loop_indices:
                v=o.data.loops[li].vertex_index;r,c=divmod(v,cols)
                uv.data[li].uv=(column*.25+.006+.238*c/(cols-1),1-r/(rows-1))
        objects.append(o)
    for layer in range(3):
        for j in range(42):
            th=2*math.pi*(j+rng.uniform(-.28,.28))/42
            if math.cos(th)>.78:continue
            end=math.acos((bottom(th)-1.683)/.095)+rng.uniform(-.03,.12)
            start=rng.uniform(.025,.12);phase=rng.uniform(0,6.28);points=[]
            for k in range(17):
                t=k/16;phi=start+(end-start)*t
                theta=th+.08*math.sin(t*5+phase)*math.sin(math.pi*t)+.05*t
                points.append(surface(theta,phi,.003+layer*.004))
            card('Human layered side and crown hair',points,rng.uniform(.014,.024),rng.choice([0,1,1,2]),phase)
    for sign in [-1,1]:
        for j in range(23):
            depth=j/22;phase=rng.uniform(0,6.28)
            p0=Vector((sign*(.004+rng.random()*.014),-.055+.092*depth,1.773-rng.random()*.006))
            p1=Vector((sign*.035,-.096+.075*depth,1.791-rng.random()*.009))
            p2=Vector((sign*(.046+.035*depth),-.138+.065*depth,1.714+rng.uniform(-.004,.008)))
            p3=Vector((sign*(.057+.044*depth),-.111+.066*depth,1.660-.031*depth+(.008 if sign>0 else 0)))
            points=[]
            for k in range(19):
                t=k/18;q=p0*(1-t)**3+p1*3*(1-t)**2*t+p2*3*(1-t)*t*t+p3*t**3
                q.x+=sign*.0035*math.sin(t*9+phase)*math.sin(math.pi*t)
                q.y+=.0035*math.sin(t*11+phase)*math.sin(math.pi*t)
                points.append(q)
            card('Human asymmetric wave fringe',points,rng.uniform(.012,.021),rng.choice([1,2,2,3]),phase)
    fly=material('Human Hair fine flyaways',(.018,.013,.010),.64)
    for j in range(56):
        th=rng.uniform(0,2*math.pi);start=rng.uniform(.35,.8);end=start+rng.uniform(.45,.95)
        points=[]
        for k in range(12):
            t=k/11;p=surface(th+.10*math.sin(t*4),start+(end-start)*t,.009+.004*math.sin(math.pi*t))
            points.append(p)
        objects.append(tube('Human single irregular flyaway',points,[.00012*(1-.75*k/11) for k in range(12)],fly,sides=3))
    return objects
