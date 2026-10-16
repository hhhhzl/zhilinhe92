"""Concept-matched adult cartoon head with modeled sockets and layered waves.

The skin and spherical eye colors are native Blender-baked PBR base-color maps.
No projected portrait, alpha cards, screen-facing meshes or toon shader is used.
"""
import bpy,bmesh,math
from mathutils import Vector
from avatar_surface import bake_color

def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def bell(x,c,s):return math.exp(-((x-c)/s)**2)
def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def color_texture(obj,colors,here,name,size=2048):
    attr=obj.data.color_attributes.new(name='AuthoredTone',type='FLOAT_COLOR',domain='CORNER')
    for poly in obj.data.polygons:
        for li in poly.loop_indices:attr.data[li].color=(*colors[obj.data.loops[li].vertex_index],1.)
    mat=obj.data.materials[0];n=mat.node_tree.nodes;v=n.new('ShaderNodeVertexColor');v.layer_name='AuthoredTone'
    bake_color(obj,0,mat,v.outputs['Color'],here,name,size)
    obj.data.color_attributes.remove(attr)
def assign_uv(obj,coords):
    uv=obj.data.uv_layers.new(name='SurfaceUV')
    for p in obj.data.polygons:
        us=[coords[v][0] for v in p.vertices];wrap=max(us)-min(us)>.7
        for li in p.loop_indices:
            u,v=coords[obj.data.loops[li].vertex_index];uv.data[li].uv=(u+1 if wrap and u<.5 else u,v)

def build_head(G,here,body_skin):
    skin=G.material('Human Concept softly colored skin',(.67,.365,.225),.66)
    skin.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.22
    skin.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.035
    body_skin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.67,.365,.225,1)
    earinner=G.material('Human Concept ear warmth',(.54,.245,.145),.7)
    eyelid=G.material('Human Concept warm eyelids',(.64,.325,.205),.65)
    lips=G.material('Human Concept natural lips',(.54,.245,.166),.63)
    crease=G.material('Human Concept soft smile line',(.215,.076,.043),.78)
    brow=G.material('Human Concept shaped eyebrows',(.034,.019,.013),.72)
    gold=G.material('Human Concept champagne glasses',(.54,.385,.18),.27,.68)
    # The visible lower face is shorter and wider than the old ellipsoid.
    rows=[(1.524,.003,.008,-.010),(1.533,.025,.030,-.010),(1.548,.060,.056,-.005),(1.572,.083,.078,-.002),(1.601,.097,.091,-.001),(1.629,.102,.098,.001),(1.652,.099,.100,.002),(1.682,.094,.100,.005),(1.713,.088,.092,.012),(1.738,.075,.078,.016),(1.757,.048,.051,.017),(1.767,.004,.007,.017)]
    def profile(z):
        for i in range(len(rows)-1):
            if rows[i][0]<=z<=rows[i+1][0]:
                t=(z-rows[i][0])/(rows[i+1][0]-rows[i][0]);a=rows[max(0,i-1)];b=rows[i];c=rows[i+1];d=rows[min(len(rows)-1,i+2)]
                return [.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in range(1,4)]
        return rows[0 if z<rows[0][0] else -1][1:]
    def face_y(x,z):
        rx,ry,cy=profile(z);y=cy-ry*max(.001,1-(abs(x)/rx)**2.65)**.5
        # Full suborbital cheek pads; a round shallow nose, never a long ridge.
        y-=.0065*(bell(x,-.053,.027)+bell(x,.053,.027))*bell(z,1.614,.027)
        y-=.0145*bell(x,0,.019)*bell(z,1.615,.014)
        y-=.0035*(bell(x,-.013,.007)+bell(x,.013,.007))*bell(z,1.610,.008)
        y-=.003*bell(x,0,.014)*bell(z,1.642,.022)
        y+=.0065*(bell(x,-.040,.024)+bell(x,.040,.024))*bell(z,1.651,.017)
        y-=.004*bell(x,0,.037)*bell(z,1.585,.016)
        y-=.0025*bell(x,0,.031)*bell(z,1.552,.015)
        # A slight smile pushes the cheek above the mouth corners.
        y-=.002*(bell(x,-.030,.012)+bell(x,.030,.012))*bell(z,1.590,.014)
        smile_z=1.582+.006*(x/.033)**2+.0006*(x/.033)
        y-=.0021*bell(x,0,.034)*bell(z,smile_z+.002,.0025)
        y-=.0028*bell(x,0,.031)*bell(z,smile_z-.0028,.0031)
        return y
    def tone(x,y,z):
        c=(.67,.365,.225);front=smooth(.01,.075,-y)
        blush=(bell(x,-.059,.031)+bell(x,.059,.031))*bell(z,1.613,.024)*front*.25
        c=mix(c,(.73,.295,.205),min(.34,blush))
        orbital=(bell(x,-.040,.025)+bell(x,.040,.025))*bell(z,1.655,.014)*front*.07
        c=mix(c,(.55,.272,.165),min(.25,orbital))
        nose=bell(x,0,.021)*bell(z,1.615,.016)*front*.17;c=mix(c,(.72,.315,.20),nose)
        mouth=bell(x,0,.036)*bell(z,1.584,.011)*front*.16;c=mix(c,(.61,.285,.18),mouth)
        smile_z=1.582+.006*(x/.033)**2+.0006*(x/.033)
        lip=bell(x,0,.033)*bell(z,smile_z-.0008,.0042)*front*.75
        c=mix(c,(.55,.245,.16),lip)
        return c
    # Skip real almond-shaped openings in the face, then bridge those openings
    # to rounded eyeballs with broad skin lids instead of drawing eye stickers.
    def in_socket(x,z):
        for sign in [-1,1]:
            xx=(x-sign*.040)/.0293;zz=z-1.650;h=.0189 if zz>0 else .0187
            if xx*xx+(zz/h)**2<.98:return True
        return False
    vs=[];fs=[];uv=[];colors=[];nz=150;nt=192
    for i in range(nz+1):
        z=rows[0][0]+(rows[-1][0]-rows[0][0])*i/nz;rx,ry,cy=profile(z)
        for j in range(nt):
            a=2*math.pi*j/nt;x=rx*math.sin(a);y=cy-ry*math.cos(a)
            if math.cos(a)>0:
                base=cy-ry*max(.001,1-(abs(x)/rx)**2.65)**.5;y=base+(face_y(x,z)-base)*smooth(0,.4,math.cos(a))
            surface_z=z+.013*(1-max(0.,math.cos(a)))*bell(z,1.54,.033)
            vs.append((x,y,surface_z));uv.append((j/nt,i/nz));colors.append(tone(x,y,surface_z))
            if i:
                face=((i-1)*nt+j,(i-1)*nt+(j+1)%nt,i*nt+(j+1)%nt,i*nt+j)
                center=(Vector(vs[(i-1)*nt+j])+Vector(vs[i*nt+j]))/2
                if not(center.y<-.04 and in_socket(center.x,center.z)):fs.append(face)
    fs.append(tuple(reversed(range(nt))));fs.append(tuple(nz*nt+j for j in range(nt)))
    head=G.mesh('Human Concept rounded cheek face',vs,fs,skin)
    # Bridge the actual skin boundary to each globe. Both ends belong to this
    # same face mesh, so no rectangular cut edges can remain exposed.
    bm=bmesh.new();bm.from_mesh(head.data);remaining={e for e in bm.edges if e.is_boundary};loops=[]
    while remaining:
        first=remaining.pop();path=[first.verts[0],first.verts[1]]
        while True:
            edge=next((e for e in path[-1].link_edges if e in remaining),None)
            if edge is None:break
            remaining.remove(edge);v=edge.other_vert(path[-1])
            if v==path[0]:break
            path.append(v)
        if len(path)>12:loops.append(path)
    for outer in loops:
        centroid=sum((v.co for v in outer),Vector())/len(outer)
        if not 1.61<centroid.z<1.69:continue
        sign=-1 if centroid.x<0 else 1;cx=sign*.040;cz=1.650;cy=face_y(cx,cz)+.019;radius=.025
        points=[v.co.copy() for v in outer];previous=outer;relax=[]
        for row in range(1,9):
            u=row/8;current=[]
            for q in points:
                a=math.atan2((q.z-cz)/.0188,(q.x-cx)/.0293)
                xx=.023*math.cos(a);zz=.0105*math.sin(a)+sign*xx*.035
                yy=cy-math.sqrt(max(.000001,radius*radius-xx*xx-zz*zz))-.0004
                inner=Vector((cx+xx,yy,cz+zz));pt=q.lerp(inner,u);pt.y-=.0012*math.sin(math.pi*u)
                new=bm.verts.new(pt);current.append(new)
                if row<8:relax.append(new)
            for j in range(len(outer)):
                k=(j+1)%len(outer);f=bm.faces.new((previous[j],previous[k],current[k],current[j]));f.smooth=True
            previous=current
        for _ in range(5):bmesh.ops.smooth_vert(bm,verts=relax,factor=.35,use_axis_x=True,use_axis_y=True,use_axis_z=True)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(head.data);bm.free();head.data.update()
    head.vertex_groups.get('Bip01 Head').add(list(range(len(head.data.vertices))),1.,'REPLACE')
    uv=[];colors=[]
    for vert in head.data.vertices:
        x,y,z=vert.co;rx,ry,cy=profile(z);a=math.atan2(x/max(.001,rx),(cy-y)/max(.001,ry));uv.append(((a/(2*math.pi))%1,(z-rows[0][0])/(rows[-1][0]-rows[0][0])));colors.append(tone(x,y,z))
    assign_uv(head,uv);color_texture(head,colors,here,'concept-skin-tone',2048)
    # A simple continuous neck, blending head motion into the original neck.
    nv=[];nf=[];neckrows=[(1.435,.060,.052,.012),(1.465,.050,.046,.010),(1.495,.043,.043,.005),(1.525,.043,.045,.002),(1.552,.043,.045,.001)]
    for i,(z,rx,ry,cy) in enumerate(neckrows):
        for j in range(64):
            a=2*math.pi*j/64;nv.append((rx*math.sin(a),cy-ry*math.cos(a),z))
            if i:nf.append(((i-1)*64+j,(i-1)*64+(j+1)%64,i*64+(j+1)%64,i*64+j))
    neck=G.mesh('Human Concept continuous neck',nv,nf,body_skin,'Bip01 Neck');neck.vertex_groups.clear()
    ng=neck.vertex_groups.new(name='Bip01 Neck');hg=neck.vertex_groups.new(name='Bip01 Head')
    for v in neck.data.vertices:
        w=smooth(1.49,1.545,v.co.z);ng.add([v.index],1-w,'REPLACE');hg.add([v.index],w,'REPLACE')
    for sign in [-1,1]:
        G.ellipsoid('Human Concept ear',(sign*.100,.006,1.627),(.019,.014,.029),body_skin)
        G.ellipsoid('Human Concept inner ear',(sign*.107,-.005,1.628),(.010,.0055,.019),earinner)
        G.ellipsoid('Human Concept ear fold',(sign*.099,-.009,1.619),(.006,.0045,.011),body_skin)
    # Real spherical eyes, with a single baked iris/sclera map on the sphere.
    for sign in [-1,1]:
        cx=sign*.040;cz=1.650;radius=.025;cy=face_y(cx,cz)+.019
        eye_mat=G.material('Human Concept brown eye '+str(sign),(1,1,1),.23)
        ep=eye_mat.node_tree.nodes.get('Principled BSDF');ep.inputs['Specular IOR Level'].default_value=.40;ep.inputs['IOR'].default_value=1.376
        ev=[];ef=[];eu=[];ec=[];lat=64;lon=128
        for i in range(lat+1):
            ph=math.pi*i/lat;rad=radius*math.sin(ph)
            for j in range(lon):
                a=2*math.pi*j/lon;x=cx+rad*math.cos(a);z=cz+rad*math.sin(a);y=cy-radius*math.cos(ph)
                ev.append((x,y,z));eu.append((j/lon,i/lat))
                c=(.85,.825,.76)
                if ph<math.pi/2 and rad<.0128:
                    striation=(math.sin(43*a+8*rad/.0128)+.5*math.sin(79*a-12*rad/.0128)+.3*math.sin(119*a))/1.8
                    t=(rad/.0128);c=(.155+.031*striation,.067+.018*striation,.024+.009*striation)
                    c=mix(c,(.24,.115,.04),.28*bell(t,.53,.19))
                    c=mix(c,(.026,.015,.010),smooth(.84,1.,t)*.92)
                    c=mix((.006,.004,.003),c,smooth(.0051,.0058,rad))
                ec.append(c)
                if i:ef.append(((i-1)*lon+j,i*lon+j,i*lon+(j+1)%lon,(i-1)*lon+(j+1)%lon))
        eye=G.mesh('Human Concept spherical eye',ev,ef,eye_mat);assign_uv(eye,eu);color_texture(eye,ec,here,'concept-eye-'+('left' if sign<0 else 'right'),1024)
        # Softly tapered eyebrow ribbon with a small arch and beveled edge.
        bv=[];bf=[];count=44
        for i in range(count+1):
            t=i/count;x=sign*(.015+.052*t);mid=1.674+.006*math.sin(math.pi*t)-.003*t
            width=.0032+.0018*math.sin(math.pi*t)**.6
            for k in range(7):
                q=-1+2*k/6;z=mid+q*width*(.4+.6*math.sin(math.pi*(.03+.94*t))**.5)
                bv.append((x,face_y(x,z)-.0015-.0018*max(0,1-q*q),z))
            if i:
                for k in range(6):bf.append(((i-1)*7+k,(i-1)*7+k+1,i*7+k+1,i*7+k))
        G.mesh('Human Concept arched brow',bv,bf,brow)
    # Short rounded nose has small underside nostrils, not a pointed spike.
    for sign in [-1,1]:
        pp=[];rr=[]
        for i in range(17):
            t=i/16;x=sign*(.009+.007*t);z=1.607-.0015*math.sin(math.pi*t)
            pp.append((x,face_y(x,z)-.0004,z));rr.append(.00015+.00035*math.sin(math.pi*t))
        G.tube('Human Concept soft nostril',pp,rr,crease,sides=8)
    # Closed relaxed smile with wider soft lower lip and upward corners.
    pp=[];rr=[]
    for i in range(73):
        t=-1+2*i/72;x=.033*t;z=1.582+.006*t*t+.0006*t
        pp.append((x,face_y(x,z)-.001,z));rr.append(.00018+.00032*(1-t*t))
    G.tube('Human Concept relaxed smile',pp,rr,crease,sides=8)
    # Glasses track the cheekbone width; rims sit near the nose, not in midair.
    for sign in [-1,1]:
        pp=[]
        for i in range(97):
            a=2*math.pi*i/96;pp.append((sign*.040+.031*math.cos(a),-.113+.007*math.cos(a)**2,1.645+.028*math.sin(a)))
        G.tube('Human Concept round glasses',pp,[.00095]*len(pp),gold,sides=10)
        G.tube('Human Concept spectacle temple',[(sign*.071,-.107,1.652),(sign*.090,-.064,1.651),(sign*.103,.002,1.644),(sign*.103,.025,1.629)],[.00105]*4,gold,sides=10)
    G.tube('Human Concept spectacle bridge',[(-.009,-.114,1.653),(0,-.122,1.658),(.009,-.114,1.653)],[.00095]*3,gold,sides=10)
    from hair_refinement import build_hair
    build_hair(G)
    return {'skin':'Human Concept softly colored skin','head_width_m':.204,'head_height_m':.243,'eyeball_radius_m':.025,'eye_center_z':1.650}
