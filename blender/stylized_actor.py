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
    # Smooth silhouette profile: a grown-up oval with full cheeks and round chin.
    rows=[(1.516,.008,.012,-.015),(1.526,.035,.036,-.017),(1.542,.060,.055,-.010),(1.565,.073,.074,-.005),(1.595,.086,.090,-.004),(1.625,.091,.097,-.003),(1.650,.088,.100,-.001),(1.680,.086,.100,.003),(1.709,.084,.093,.010),(1.735,.073,.078,.013),(1.754,.050,.053,.016),(1.765,.005,.007,.017)]
    def profile(z):
        for i in range(len(rows)-1):
            if rows[i][0]<=z<=rows[i+1][0]:
                t=(z-rows[i][0])/(rows[i+1][0]-rows[i][0]);a=rows[max(0,i-1)];b=rows[i];c=rows[i+1];d=rows[min(len(rows)-1,i+2)]
                return [(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)) for k in range(1,4)]
        return list(rows[0 if z<rows[0][0] else -1][1:])
    def face_y(x,z):
        rx,ry,cy=profile(z);y=cy-ry*math.sqrt(max(.001,1-(x/rx)**2))
        y-=.025*gauss(x,0,.019)*gauss(z,1.617,.017) # small broad nose, continuous with face
        y-=.0045*gauss(x,0,.013)*gauss(z,1.642,.029) # gentle bridge
        y-=.0065*(gauss(x,-.051,.023)+gauss(x,.051,.023))*gauss(z,1.609,.027)
        y+=.009*(gauss(x,-.037,.020)+gauss(x,.037,.020))*gauss(z,1.648,.014)
        y-=.003*gauss(x,0,.038)*gauss(z,1.578,.014)
        return y
    verts=[];faces=[];nz=104;nt=128
    for i in range(nz+1):
        z=rows[0][0]+(rows[-1][0]-rows[0][0])*i/nz;rx,ry,cy=profile(z)
        for j in range(nt):
            a=2*math.pi*j/nt;x=rx*math.sin(a);y=cy-ry*math.cos(a)
            if math.cos(a)>0:
                base=cy-ry*math.sqrt(max(.001,1-(x/rx)**2));y+=(face_y(x,z)-base)*smooth(0,.5,math.cos(a))
            verts.append((x,y,z))
            if i:faces.append(((i-1)*nt+j,(i-1)*nt+(j+1)%nt,i*nt+(j+1)%nt,i*nt+j))
    faces.append(tuple(reversed(range(nt))));faces.append(tuple(nz*nt+j for j in range(nt)))
    head=G.mesh('Human sculpted animated face',verts,faces,skin)
    # Replace the entire old neck, including its cut boundary, with one smooth
    # tapered surface. A soft bone-weight blend follows the existing head tilt.
    nv=[];nf=[];neckrows=[(1.435,.060,.052,.012),(1.465,.050,.046,.010),(1.495,.043,.043,.005),(1.525,.042,.044,.002),(1.550,.041,.044,.001)]
    for i,(z,rx,ry,cy) in enumerate(neckrows):
        for j in range(64):
            a=2*math.pi*j/64;nv.append((rx*math.sin(a),cy-ry*math.cos(a),z))
            if i:nf.append(((i-1)*64+j,(i-1)*64+(j+1)%64,i*64+(j+1)%64,i*64+j))
    neck=G.mesh('Human continuous stylized neck',nv,nf,skin,'Bip01 Neck')
    neck.vertex_groups.clear();ng=neck.vertex_groups.new(name='Bip01 Neck');hg=neck.vertex_groups.new(name='Bip01 Head')
    for v in neck.data.vertices:
        w=smooth(1.49,1.54,v.co.z);ng.add([v.index],1-w,'REPLACE');hg.add([v.index],w,'REPLACE')
    sub=neck.modifiers.new('Smooth neck connection','SUBSURF');sub.levels=2
    bpy.context.view_layer.objects.active=neck;bpy.ops.object.modifier_move_to_index(modifier=sub.name,index=0);bpy.ops.object.modifier_apply(modifier=sub.name)
    # Ears are full geometry, with a recessed colored concha and a soft helix.
    for sign in [-1,1]:
        G.ellipsoid('Human rounded ear',(sign*.090,.005,1.625),(.019,.014,.030),skin)
        G.ellipsoid('Human recessed ear',(sign*.098,-.006,1.626),(.010,.006,.020),earinner)
        G.ellipsoid('Human ear tragus',(sign*.089,-.009,1.617),(.006,.005,.010),skin)
    # One continuous eye surface contains the pupil, iris and white. No
    # stacked ellipsoids can detach the iris or produce a button-eye silhouette.
    for sign in [-1,1]:
        cx=sign*.037;cz=1.648;ey=face_y(cx,cz)-.0035;w=.021;h=.011
        vs=[(cx,ey,cz)];fs=[];indices=[];steps=64
        radial=[.0015,.003,.0046,.0058,.007,.0085,.25,.5,.75,1.]
        border=[]
        for r,rr in enumerate(radial):
            for j in range(steps):
                a=2*math.pi*j/steps;xx=w*math.cos(a);zz=(h if math.sin(a)>0 else .008)*math.sin(a)*(.72+.28*abs(math.sin(a)))+sign*xx*.055
                if r<6:
                    xoff=rr*math.cos(a);zoff=rr*math.sin(a);blend=(rr/.021)**2
                else:
                    xoff=(.0085*math.cos(a))*(1-rr)+xx*rr;zoff=(.0085*math.sin(a))*(1-rr)+zz*rr;blend=(.4+.6*rr)**2
                x=cx+xoff;z=cz+zoff;edge=face_y(cx+xx,cz+zz)-.001
                y=ey*(1-blend)+edge*blend;vs.append((x,y,z))
                if r==0:fs.append((0,1+j,1+(j+1)%steps))
                else:
                    a0=1+(r-1)*steps;a1=1+r*steps
                    fs.append((a0+j,a1+j,a1+(j+1)%steps,a0+(j+1)%steps))
                indices.append(2 if r<3 else 1 if r<6 else 0)
                if r==len(radial)-1:border.append((x,y-.0006,z))
        eye=G.mesh('Human continuous almond eye',vs,fs,white);eye.data.materials.append(iris);eye.data.materials.append(pupil)
        for poly,mi in zip(eye.data.polygons,indices):poly.material_index=mi
        G.ellipsoid('Human tiny reflected light',(cx-.0025,ey-.0007,cz+.003),(.00085,.0003,.00085),highlight,rings=8,sectors=12)
        upper=border[:33];lower=border[32:]+border[:1]
        G.tube('Human upper eyelid',upper,[.0014+.0006*math.sin(math.pi*i/(len(upper)-1)) for i in range(len(upper))],skin,sides=10)
        G.tube('Human lower eyelid',lower,[.0012]*len(lower),skin,sides=10)
        lash=[(x,y-.0003,z-.0002) for x,y,z in upper]
        G.tube('Human upper lash edge',lash,[.00025+.00035*math.sin(math.pi*i/(len(lash)-1)) for i in range(len(lash))],brow,sides=8)
        # A shaped brow tapers toward the temple, softly raised at the outside.
        bp=[];br=[]
        for i in range(25):
            t=i/24;x=sign*(.015+.047*t);z=1.674+.004*math.sin(math.pi*t)-.005*t
            bp.append((x,face_y(x,z)-.003,z));br.append(.0022+.0020*math.sin(math.pi*t)**.5)
        G.tube('Human expressive brow',bp,br,brow,sides=12,flatten=.55)
    # A broad quiet smile: a recessed curved line with soft integrated lip volume.
    pts=[];r=[]
    for i in range(61):
        t=-1+2*i/60;x=t*.031;z=1.578+.0055*t*t
        pts.append((x,face_y(x,z)-.0015,z));r.append(.00045+.00045*(1-t*t))
    G.tube('Human calm smile',pts,r,mouth,sides=8)
    for lower in [False,True]:
        vs=[];fs=[]
        for i in range(61):
            t=-1+2*i/60;x=.031*t;z=1.578+.0055*t*t
            for k in range(6):
                u=k/5;zz=z+(-1 if lower else 1)*(.004 if lower else .0027)*math.sin(math.pi*(t+1)/2)*u
                yy=face_y(x,zz)-.0006-.0015*math.sin(math.pi*u)*(1-t*t)
                vs.append((x,yy,zz))
            if i:
                for k in range(5):fs.append(((i-1)*6+k,(i-1)*6+k+1,i*6+k+1,i*6+k))
        G.mesh('Human softly modeled lip',vs,fs,lip)
    # Eyeglasses are clean thin gold, kept close to the face and open at the lens.
    for sign in [-1,1]:
        cx=sign*.037;cz=1.645;points=[]
        for i in range(81):
            a=2*math.pi*i/80;points.append((cx+.029*math.cos(a),-.113+.003*math.cos(a)**2,cz+.027*math.sin(a)))
        G.tube('Human gold round frame',points,[.00115]*len(points),gold,sides=10)
        G.tube('Human gold temple',[(sign*.066,-.111,1.650),(sign*.084,-.075,1.651),(sign*.093,.005,1.640),(sign*.091,.025,1.625)],[.00125]*4,gold,sides=10)
    G.tube('Human gold bridge',[(-.008,-.114,1.651),(0,-.122,1.657),(.008,-.114,1.651)],[.00115]*3,gold,sides=10)
    # Closed continuous base with two asymmetrical large wave masses. Shallow
    # lofts intersect the base and are fused to it, so curls never float apart.
    hair_objects=[];vs=[];fs=[];nr=44;ns=112
    for i in range(nr+1):
        for j in range(ns):
            a=2*math.pi*j/ns;front=max(0,math.cos(a));bottom=1.596+.115*front**3
            bottom+=.005*math.sin(2*a)*front
            theta=(i/nr)*math.acos(max(-1.,min(1.,(bottom-1.682)/.101)))
            wav=.0025*math.sin(4*a+3.1*i/nr)*math.sin(theta)
            vs.append(((.097+wav)*math.sin(theta)*math.sin(a),.010-(.108+wav)*math.sin(theta)*math.cos(a),1.682+.101*math.cos(theta)))
            if i:fs.append(((i-1)*ns+j,(i-1)*ns+(j+1)%ns,i*ns+(j+1)%ns,i*ns+j))
    fs.append(tuple(reversed([nr*ns+j for j in range(ns)])))
    hair_objects.append(G.mesh('Human continuous dark scalp',vs,fs,hair[0]))
    locks=[
      ([(-.004,-.021,1.777),(-.043,-.077,1.800),(-.090,-.109,1.755),(-.073,-.082,1.704)],.034,.013,0),
      ([(-.025,.016,1.775),(-.081,-.028,1.792),(-.108,-.080,1.739),(-.096,-.016,1.694)],.028,.011,0),
      ([(.011,-.018,1.776),(.047,-.075,1.792),(.079,-.111,1.731),(.100,-.062,1.731)],.031,.013,0),
      ([(.024,.019,1.774),(.086,-.020,1.787),(.103,-.065,1.714),(.101,.012,1.693)],.028,.011,0),
      ([(-.038,.039,1.770),(-.092,.100,1.753),(-.103,.097,1.672),(-.049,.081,1.614)],.031,.012,0),
      ([(.039,.040,1.769),(.093,.102,1.749),(.098,.100,1.673),(.044,.084,1.611)],.031,.012,0),
      ([(0,.048,1.773),(.012,.119,1.749),(-.005,.119,1.670),(-.002,.091,1.610)],.034,.011,0),
      ([(-.027,-.093,1.747),(-.011,-.111,1.722),(-.009,-.114,1.699),(-.026,-.101,1.698)],.005,.004,0),
    ]
    for i,(controls,w,d,m) in enumerate(locks):
        controls=[(x*.87,.010+(y-.010)*.88,z) for x,y,z in controls]
        hair_objects.append(G.bezier_lock('Human sculpted S wave '+str(i),controls,w*.89,d*.85,hair[m]))
    hair_objects.append(G.ellipsoid('Human left continuous wave mass',(-.040,-.043,1.744),(.049,.057,.044),hair[0],rings=24,sectors=48))
    hair_objects.append(G.ellipsoid('Human right continuous wave mass',(.039,-.037,1.744),(.048,.057,.043),hair[0],rings=24,sectors=48))
    bpy.ops.object.select_all(action='DESELECT')
    for o in hair_objects:o.select_set(True)
    bpy.context.view_layer.objects.active=hair_objects[0];bpy.ops.object.join();ho=hair_objects[0]
    for o in hair_objects[1:]:G.objects.remove(o)
    ho.modifiers.clear();ho.vertex_groups.clear()
    rem=ho.modifiers.new('Fuse broad sculpted waves','REMESH');rem.mode='VOXEL';rem.voxel_size=.0018;rem.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=ho.modifiers.new('Soft clay wave transitions','SMOOTH');sm.factor=.65;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
    dec=ho.modifiers.new('Retain sculpted silhouette efficiently','DECIMATE');dec.ratio=.46;bpy.ops.object.modifier_apply(modifier=dec.name)
    vg=ho.vertex_groups.new(name='Bip01 Head');vg.add(list(range(len(ho.data.vertices))),1.,'REPLACE')
    ar=ho.modifiers.new('Original performer skeleton','ARMATURE');ar.object=rig;ho.select_set(False)
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
    G.join_by_material()
    human['identity']='Stylized adult character of Zhilin He, designed from selected imagegen concept and supplied photos; deliberately animated, not a scan'
    human['art_direction']='Adult animation proportions; sculpted full cheeks and smile; almond eyes; champagne frames; asymmetric solid S-wave hair; blue/ivory broad-stripe polo'
    human['outfit']='Oversized blue and ivory horizontal stripe polo, continuous soft collar, wide charcoal trousers, ivory sneakers'
    print('STYLIZED_ACTOR_READY',flush=True)
