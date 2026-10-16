"""Layered, solid S-wave locks fitted directly to the scalp surface."""
import math,bpy
from mathutils import Vector

def catmull(points,t):
    n=len(points)-1;p=min(n-1,int(t*n));u=t*n-p
    a=Vector(points[max(0,p-1)]);b=Vector(points[p]);c=Vector(points[p+1]);d=Vector(points[min(n,p+2)])
    return .5*(2*b+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)
def build_hair(G):
    mat=G.material('Human Concept layered espresso waves',(.035,.020,.016),.57)
    p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Specular IOR Level'].default_value=.18
    # A shallow continuous foundation follows the skull. The central part is
    # higher, while the sides dip irregularly around the temples and ears.
    def scalp(a,t,offset=0):
        return Vector(((.115+offset)*math.sin(t)*math.sin(a),.012-(.130+offset)*math.sin(t)*math.cos(a),1.686+(.123+offset)*math.cos(t)))
    vs=[];fs=[];nr=48;ns=128
    for i in range(nr+1):
        for j in range(ns):
            a=2*math.pi*j/ns;front=max(0,math.cos(a))
            bottom=1.598+.108*front**.60+.006*math.exp(-(math.sin(a)/.24)**2)*front
            bottom+=.0035*math.sin(3*a)*front
            end=math.acos(max(-1,min(1,(bottom-1.686)/.123)))
            q=scalp(a,end*i/nr,-.004)
            vs.append(q)
            if i:fs.append(((i-1)*ns+j,(i-1)*ns+(j+1)%ns,i*ns+(j+1)%ns,i*ns+j))
    fs.append(tuple(reversed([nr*ns+j for j in range(ns)])))
    G.mesh('Human Concept continuous hair foundation',vs,fs,mat)
    # Coordinates are (azimuth around skull, polar angle, surface lift). Each
    # medium lock is fitted to this same surface rather than floating in space.
    paths=[
      ([(-.005,-.035,1.790),(-.028,-.077,1.808),(-.067,-.106,1.788),(-.075,-.113,1.748),(-.050,-.113,1.719),(-.028,-.105,1.716)],.023,.012),
      ([(-.020,.000,1.785),(-.055,-.056,1.800),(-.091,-.088,1.774),(-.102,-.095,1.731),(-.081,-.096,1.703),(-.055,-.080,1.700)],.022,.011),
      ([(-.041,.028,1.779),(-.089,-.015,1.786),(-.117,-.040,1.756),(-.121,-.050,1.715),(-.110,-.041,1.684),(-.090,-.025,1.681)],.021,.010),
      ([(-.050,.054,1.769),(-.097,.032,1.782),(-.119,.015,1.740),(-.119,.022,1.682),(-.099,.065,1.640)],.022,.011),
      ([(-.020,.070,1.774),(-.075,.104,1.762),(-.100,.113,1.714),(-.089,.105,1.663),(-.053,.082,1.614)],.025,.010),
      ([(.007,-.025,1.790),(.031,-.075,1.801),(.061,-.103,1.775),(.078,-.111,1.743),(.103,-.092,1.733),(.104,-.073,1.744)],.023,.012),
      ([(.025,.015,1.783),(.068,-.030,1.801),(.093,-.074,1.777),(.110,-.084,1.736),(.122,-.049,1.716),(.106,-.020,1.713)],.023,.011),
      ([(.045,.050,1.774),(.091,.014,1.786),(.119,-.020,1.751),(.124,-.010,1.706),(.110,.024,1.680)],.022,.011),
      ([(.048,.069,1.767),(.095,.063,1.767),(.121,.062,1.718),(.107,.082,1.664),(.073,.075,1.624)],.023,.010),
      ([(.006,.073,1.775),(.047,.112,1.756),(.061,.123,1.712),(.046,.114,1.660),(.015,.092,1.614)],.026,.011),
      ([(-.007,-.093,1.764),(-.030,-.113,1.747),(-.055,-.116,1.719),(-.060,-.100,1.700)],.019,.0075),
      ([(.005,-.090,1.765),(.026,-.114,1.745),(.048,-.115,1.721),(.071,-.096,1.706)],.020,.008),
    ]
    for num,(params,width,depth) in enumerate(paths):
        vv=[];ff=[];color=[];steps=76;sides=64
        for i in range(steps+1):
            t=i/steps;center=catmull(params,t)
            relative=center-Vector((0,.012,1.686));rho=math.sqrt((relative.x/.115)**2+(relative.y/.130)**2+(relative.z/.123)**2)
            shell=Vector((0,.012,1.686))+relative/max(.01,rho)
            center=shell*.88+center*.12
            before=catmull(params,max(0,t-.003));after=catmull(params,min(1,t+.003))
            tangent=(after-before).normalized()
            normal=Vector((center.x/.104,(center.y-.012)/.113,(center.z-1.686)/.109)).normalized()
            across=normal.cross(tangent).normalized();out=tangent.cross(across).normalized()
            taper=(.42+.58*math.sin(math.pi*(.05+.90*t))**.6)*(1-.50*max(0,(t-.82)/.18)**1.5)
            for j in range(sides):
                a=2*math.pi*j/sides;side=math.cos(a);height=math.sin(a)
                # Fine grouped ridges follow the flow. They are only 0.2–0.4 mm
                # deep; the medium lock's changing S direction remains dominant.
                fluting=.00075*(math.cos(side*math.pi*5+1.4*t)+.45*math.cos(side*math.pi*9-.8*t))*max(0,height)**2
                point=center+across*(width*taper*side)+out*((depth*taper*height+fluting) if height>=0 else .004*height)
                vv.append(point)
                variation=.92+.06*math.cos(side*12+2*t)+.035*math.sin(side*31-t)
                color.append((.040*variation,.024*variation,.018*variation,1))
                if i:ff.append(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j))
        ff.append(tuple(reversed(range(sides))));ff.append(tuple(steps*sides+j for j in range(sides)))
        lock=G.mesh('Human Concept medium S lock '+str(num+1),vv,ff,mat)
        attr=lock.data.color_attributes.new(name='WaveTone',type='FLOAT_COLOR',domain='CORNER')
        for poly in lock.data.polygons:
            for li in poly.loop_indices:attr.data[li].color=color[lock.data.loops[li].vertex_index]
    # A smaller curl returns toward the central forehead, breaking mirror
    # symmetry without becoming a disconnected hook or a large floating leaf.
    control=[(-.006,-.065,1.785),(-.025,-.121,1.765),(-.042,-.126,1.731),(-.025,-.112,1.708)]
    G.bezier_lock('Human Concept small returning forelock',control,.013,.007,mat)
    G.bezier_lock('Human Concept front right sweep',[(.006,-.063,1.785),(.022,-.117,1.763),(.056,-.123,1.728),(.079,-.103,1.721)],.017,.008,mat)
    # Match the hair foundation to the vertex-color shaded lock material.
    n=mat.node_tree.nodes;l=mat.node_tree.links;v=n.new('ShaderNodeVertexColor');v.layer_name='WaveTone';l.new(v.outputs['Color'],p.inputs['Base Color'])
    for obj in G.objects:
        if obj.type=='MESH' and obj.data.materials and obj.data.materials[0]==mat and not obj.data.color_attributes.get('WaveTone'):
            a=obj.data.color_attributes.new(name='WaveTone',type='FLOAT_COLOR',domain='CORNER')
            for loop in a.data:loop.color=(.035,.021,.017,1)
