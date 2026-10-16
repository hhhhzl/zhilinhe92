"""Build the editable zhilinhe92 atelier and its web-ready glTF scene.

Run with Blender 4.5 LTS:
  G1_ASSET_DIR=/path/to/unitree_g1 HUMAN_ASSET_DIR=/path/to/Microsoft-Rocketbox \
    Blender -b --python build_scene.py
G1_ASSET_DIR contains g1.xml and assets/. HUMAN_ASSET_DIR contains LICENSE.md
and Assets/Avatars/Adults/Male_Adult_02/{Export,Textures}/. Source defaults are
documented below and in human_actor.py; the saved .blend packs runtime textures.
Native coordinates: Z up; Human y=.95 faces -Y; Robot y=-.95 faces +Y.
G1 geometry and kinematics are imported from the BSD-3-Clause MuJoCo Menagerie.
The stylized human uses a licensed body rig with newly modeled cartoon head,
solid wave hair and clean materials based on the selected concept sheet.
"""
from pathlib import Path
import math, json, shutil, os, sys, xml.etree.ElementTree as ET
import bpy
from mathutils import Vector, Quaternion

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
ROBOT_STUDY='--robot-study' in sys.argv
OUT = HERE.parent / 'public' / 'assets'
G1 = Path(os.environ.get('G1_ASSET_DIR', str(HERE / 'source' / 'unitree_g1')))
if not (G1 / 'g1.xml').is_file():
    raise FileNotFoundError('Set G1_ASSET_DIR to the MuJoCo Menagerie unitree_g1 directory containing g1.xml and assets/.')
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):
    bpy.data.materials.remove(block)

def material(name, color, roughness=.65, metallic=0, alpha=1):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, alpha)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Alpha'].default_value = alpha
    m.diffuse_color = (*color, alpha)
    if alpha < 1:
        m.surface_render_method = 'DITHERED'
        m.use_transparency_overlap = False
    return m

concrete = material('Indigo mineral concrete', (.080,.090,.175), .78)
floor_mat = material('Honed ultramarine terrazzo', (.027,.041,.103), .35)
plaster = material('Midnight mineral plaster', (.044,.058,.149), .87)
steel = material('Blue grey structural steel', (.048,.072,.155), .42, .22)
frame_mat = material('Slender anodised window frames', (.075,.117,.220), .30, .6)
glass = material('Almost clear window glass', (.24,.34,.60), .12, .02, .06)
joint_mat = material('Floor expansion joints', (.015,.024,.055), .87)
cyan = material('Quiet cyan enamel', (.10,.46,.50), .42, .2)
robot_metal = material('G1 satin aluminium', (.62,.65,.66), .30, .56)
robot_black = material('G1 charcoal polymer', (.055,.066,.073), .40, .03)
robot_logo = material('G1 light markings', (.80,.82,.80), .46)
cloth = material('Researcher charcoal cotton jacket', (.055,.066,.070), .96)
cloth_shadow = material('Jacket stitching and recessed seams', (.034,.039,.041), .97)
shirt = material('Researcher ivory shirt', (.76,.74,.68), .94)
pants = material('Researcher charcoal trousers', (.105,.116,.123), .96)
sole = material('Shoe sole', (.035,.043,.049), .81)
shoe = material('Black leather trainers', (.052,.060,.067), .61)
skin = material('Researcher skin', (.46,.285,.19), .69)
skin_shade = material('Soft facial features', (.28,.15,.11), .82)
hair = material('Researcher black hair', (.018,.021,.025), .86)
eye_mat = material('Researcher eyes', (.24,.15,.11), .86)
controller_mat = material('Handheld controller', (.035,.047,.05), .37, .10)

architecture = []
human_parts = []

def empty(name, location=(0,0,0), parent=None):
    o = bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    o.location = location
    o.parent = parent
    return o

def mesh_object(name, verts, faces, mat, parent=None, smooth=False):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    if mat: o.data.materials.append(mat)
    o.parent = parent
    if smooth:
        for p in mesh.polygons: p.use_smooth=True
    return o

def box(name, loc, size, mat, bevel=0, parent=None, group=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Small real edge radius','BEVEL')
        mod.width=bevel; mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.parent=parent
    if group is not None: group.append(o)
    return o

def ellipsoid(name,loc,scale,mat,parent=None,segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=16,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.parent=parent; o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth=True
    if parent == human: human_parts.append(o)
    return o

def loft(name, rings, mat, parent=None, steps=32):
    # Rings are (x, y, z, radius_x, radius_y); a real surface, not stacked primitives.
    verts=[]
    for x,y,z,rx,ry in rings:
        verts.extend([(x+rx*math.cos(2*math.pi*j/steps),y+ry*math.sin(2*math.pi*j/steps),z) for j in range(steps)])
    faces=[]
    for i in range(len(rings)-1):
        for j in range(steps):
            k=(j+1)%steps
            faces.append((i*steps+j,i*steps+k,(i+1)*steps+k,(i+1)*steps+j))
    faces.extend([tuple(reversed(range(steps))),tuple((len(rings)-1)*steps+j for j in range(steps))])
    o=mesh_object(name,verts,faces,mat,parent,True)
    if parent == human: human_parts.append(o)
    return o

def tube(name, points, radii, mat, parent=None, steps=16):
    verts=[]
    for i,pt in enumerate(points):
        t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
        t.normalize()
        ref=Vector((0,1,0)) if abs(t.y)<.90 else Vector((1,0,0))
        u=t.cross(ref).normalized(); v=t.cross(u).normalized()
        for j in range(steps):
            a=j*2*math.pi/steps
            verts.append(Vector(pt)+radii[i]*(math.cos(a)*u+math.sin(a)*v))
    faces=[]
    for i in range(len(points)-1):
        for j in range(steps):
            k=(j+1)%steps; faces.append((i*steps+j,i*steps+k,(i+1)*steps+k,(i+1)*steps+j))
    faces += [tuple(reversed(range(steps))),tuple((len(points)-1)*steps+j for j in range(steps))]
    o=mesh_object(name,verts,faces,mat,parent,True)
    if parent == human: human_parts.append(o)
    return o

def join_batch(objects,name):
    if not objects: return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    o=bpy.context.object; o.name=name
    return o

# A quiet, fully enclosed daylight atelier. Dimensions are metres.
human=None
floor=box('Floor',(0,0,-.12),(24,36,.24),floor_mat,.025)
floor['surface']='honed concrete terrazzo; top elevation 0 m'
for x in [-8,-4,0,4,8]:
    box('Floor_joint',(x,0,.001),(.012,36,.001),joint_mat,group=architecture)
for y in [-12,-6,0,6,12]:
    box('Floor_joint',(0,y,.001),(24,.012,.001),joint_mat,group=architecture)

for x in [-12,12]:
    box('Perimeter_plinth',(x,0,1.05),(.22,36,2.1),plaster,.012,group=architecture)
    box('High_fascia',(x,0,7.35),(.22,36,1.30),plaster,.012,group=architecture)
    for y in range(-18,19,6):
        box('Column',(x*.966,y,3.75),(.32,.42,7.5),concrete,.025,group=architecture)
    for y in range(-15,18,6):
        box('High_clear_glazing',(x, y,4.38),(.015,5.55,4.52),glass,group=architecture)
    for y in range(-18,19,2):
        box('Window_mullion',(x-.03 if x<0 else x+.03,y,4.38),(.10,.052,4.6),frame_mat,.004,group=architecture)
    for z in [2.12,4.4,6.66]:
        box('Window_transom',(x,0,z),(.10,36,.055),frame_mat,.004,group=architecture)
    box('Low_wall_reveal',(x*.985,0,.11),(.028,36,.07),steel,.003,group=architecture)

for y in [-18,18]:
    box('End_wall',(0,y,2.55),(24,.28,5.1),plaster,.016,group=architecture)
    box('End_wall_fascia',(0,y,7.5),(24,.28,1.0),plaster,.016,group=architecture)
    box('End_clerestory_glass',(0,y,6.05),(24,.018,1.9),glass,group=architecture)
    for x in range(-12,13,2):
        box('End_window_mullion',(x,y,6.05),(.055,.11,1.94),frame_mat,.004,group=architecture)
    for z in [5.1,7.0]:
        box('End_window_transom',(0,y,z),(24,.11,.055),frame_mat,.004,group=architecture)
    # Flush service doors offer a believable architectural scale without clutter.
    for x in [-8.7,8.7]:
        box('Flush_service_door',(x,y-math.copysign(.151,y),1.17),(1.35,.018,2.34),concrete,.01,group=architecture)
        box('Door_pull',(x+.47,y-math.copysign(.18,y),1.12),(.025,.03,.28),frame_mat,.008,group=architecture)

box('Ceiling',(0,0,8.12),(24,36,.22),plaster,.01,group=architecture)
for y in range(-18,19,6):
    box('Cross_beam',(0,y,7.62),(24,.30,.60),concrete,.025,group=architecture)
    box('Beam_lower_flange',(0,y,7.31),(24,.43,.06),steel,.005,group=architecture)
for x in [-8,-4,0,4,8]:
    box('Roof_purlin',(x,0,7.93),(.13,36,.24),steel,.012,group=architecture)

# A small neutral wayfinding stripe is the only environmental accent.
for y in [-16.5,16.5]:
    box('Quiet_enamel_marker',(-11.76,y,1.34),(.016,.06,.34),cyan,.004,group=architecture)

architecture_batches={mat:[o for o in architecture if o.data.materials[0] == mat] for mat in [concrete,plaster,steel,frame_mat,glass,joint_mat,cyan]}
for mat,batch in architecture_batches.items():
    joined=join_batch(batch,'Architecture_'+mat.name.replace(' ','_'))
    if joined:joined['category']='architecture'

# Authentic Unitree G1: retain articulated links and actual STL surfaces.
robot=empty('Robot',(0,-.95,0))
robot.rotation_euler.z=math.pi/2  # MuJoCo +X forward becomes Blender +Y.
robot['source']='MuJoCo Menagerie / Unitree G1 (BSD-3-Clause)'
robot['height_m']=1.32
xml=ET.parse(G1/'g1.xml').getroot()
meshfiles={e.get('name',Path(e.get('file')).stem): G1/'assets'/e.get('file') for e in xml.findall('./asset/mesh')}
cache={}
robot_joints={}
pose={}
for side in ['left','right']:
    for j,a in zip(['shoulder_pitch','shoulder_roll','shoulder_yaw','elbow','wrist_roll','wrist_pitch','wrist_yaw'],[.2,.2 if side=='left' else -.2,0,1.28,0,0,0]):
        pose[side+'_'+j+'_joint']=a

def floats(s,default):return tuple(map(float,s.split())) if s else default
def robot_body(el,parent):
    loc=floats(el.get('pos'),(0,0,0))
    if el.get('name')=='pelvis':loc=(0,0,.79)
    body=empty('Robot_'+el.get('name','body'),loc,parent)
    body.rotation_mode='QUATERNION'
    q=Quaternion(floats(el.get('quat'),(1,0,0,0)))
    for j in el.findall('joint'):
        robot_joints[j.get('name')]={'object':body,'base':q.copy(),'axis':Vector(floats(j.get('axis'),(0,0,1))),'range':floats(j.get('range'),(-math.pi,math.pi))}
        q=q @ Quaternion(Vector(floats(j.get('axis'),(0,0,1))),pose.get(j.get('name'),0))
    body.rotation_quaternion=q
    for g in el.findall('geom'):
        if g.get('class') != 'visual':continue
        key=g.get('mesh')
        if key not in cache:
            bpy.ops.wm.stl_import(filepath=str(meshfiles[key]))
            imported=bpy.context.object
            imported.name='Robot_'+key+'_visual'
            # Keep original engineering surfaces, with angle-based split normals.
            cache[key]=imported.data
            bpy.data.objects.remove(imported,do_unlink=True)
        o=bpy.data.objects.new('Robot_'+key+'_visual',cache[key].copy())
        bpy.context.collection.objects.link(o)
        o.parent=body
        o.location=floats(g.get('pos'),(0,0,0))
        o.rotation_mode='QUATERNION';o.rotation_quaternion=floats(g.get('quat'),(1,0,0,0))
        m=robot_black if g.get('material','metal')=='black' else robot_metal
        if key=='logo_link':m=robot_logo
        o.data.materials.clear();o.data.materials.append(m)
        for p in o.data.polygons:p.use_smooth=True
        # Imported STL meshes retain edges via weighted normals; decimation is unnecessary.
        o['source_mesh']=meshfiles[key].name
    for child in el.findall('body'):robot_body(child,body)

for e in xml.findall('./worldbody/body'):robot_body(e,robot)
bpy.context.view_layer.update()
robot_meshes=[o for o in robot.children_recursive if o.type=='MESH']
zmin=min((o.matrix_world@Vector(c)).z for o in robot_meshes for c in o.bound_box)
robot.location.z-=zmin
robot_eye=empty('RobotEye',(.115,0,1.205),robot)
robot_eye['usage']='Approximate observer eye; native coordinates relative to Robot root'
bpy.context.view_layer.update()
eye_world=robot_eye.matrix_world.translation.copy()
robot_eye.parent=robot_joints['waist_pitch_joint']['object']
robot_eye.location=robot_eye.parent.matrix_world.inverted() @ eye_world
from g1_echo import animate_g1
motion_audit=animate_g1(robot,robot_joints)
(HERE/'motion-audit.json').write_text(json.dumps(motion_audit,indent=2))

# The original geometric placeholder is replaced by a licensed, rigged human.
# --robot-study permits independent robot choreography QA while this asset is loaded.
if ROBOT_STUDY:
    human=empty('Human',(0,.95,0))
    human_eye=empty('HumanEye',(0,-.095,1.636),human)
else:
    from human_actor import build_human
    human,human_eye=build_human(HERE,OUT)

# Presentation lighting and camera live in the editable scene; the web uses its own.
scene=bpy.context.scene
scene.world.color=(.045,.065,.16)
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.07,.11,.30,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.42
def area(name,location,energy,size,target,color=(1,1,1)):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=location
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o
area('Peach side light',(-9,-1,5),3600,7,(0,0,1),(1,.48,.30))
area('Ultramarine bounce',(7,2,4.8),2400,9,(0,0,1),(.16,.28,1))
area('Amber window rim',(-3,9,5.7),2300,6,(0,0,1),(1,.64,.32))
sun_data=bpy.data.lights.new('Late afternoon parallel sunlight','SUN');sun_data.energy=1.8;sun_data.angle=.10;sun_data.color=(1,.58,.36)
sun=bpy.data.objects.new('Late afternoon parallel sunlight',sun_data);bpy.context.collection.objects.link(sun)
sun.rotation_euler=(math.radians(28),math.radians(-36),math.radians(-54))
camera_data=bpy.data.cameras.new('Architecture camera')
camera=bpy.data.objects.new('Architecture camera',camera_data);bpy.context.collection.objects.link(camera)
camera.location=(4.2,-4.8,2.0)
camera.rotation_euler=(Vector((0,0,1.35))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.lens=46
scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(HERE/'preview.png')
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.unit_settings.system='METRIC'
scene.render.fps=30
scene.frame_start=0;scene.frame_end=150
scene.frame_set(0)
scene.name='Echo'
scene['description']='zhilinhe92: 24 x 36 x 8 m industrial daylight atelier'

bpy.context.view_layer.update()
def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    if not pts:return None
    return {'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}
audit={'coordinates':'Blender Z up; export glTF +Y up (x,z,-y)', 'human_bounds':bounds([o for o in human.children_recursive if o.type=='MESH']), 'robot_bounds':bounds(robot_meshes), 'mesh_objects':len([o for o in scene.objects if o.type=='MESH']), 'triangles':sum(len(p.vertices)-2 for o in scene.objects if o.type=='MESH' for p in o.data.polygons), 'g1_visual_meshes':len(robot_meshes), 'g1_source':str(G1), 'human_eye_blender':list(human_eye.matrix_world.translation), 'robot_eye_blender':list(robot_eye.matrix_world.translation), 'motion':motion_audit}
(HERE/'scene-audit.json').write_text(json.dumps(audit,indent=2))
shutil.copy2(G1/'LICENSE',OUT/'UNITREE-G1-LICENSE.txt')
credits_path=OUT/'ASSET-CREDITS.txt'
extra_credits=credits_path.read_text().partition('\n\n')[2].strip() if credits_path.exists() else ''
credits_path.write_text('Unitree G1 mesh and kinematic model: MuJoCo Menagerie, Google DeepMind and Unitree Robotics. BSD-3-Clause; see UNITREE-G1-LICENSE.txt.\nHuman performer: Microsoft Rocketbox, Male_Adult_02. MIT; see ROCKETBOX-LICENSE.md. Source: https://github.com/microsoft/Microsoft-Rocketbox/tree/master/Assets/Avatars/Adults/Male_Adult_02\nAtelier, material adaptation and Echo choreography: built for zhilinhe92. Echo is an authored artistic animation, not a dynamics simulation, research result, captured motion, or deployable robot controller. The human is an intentionally stylized character of Zhilin He: selected ImageGen art direction translated into full native 3D geometry and skinned onto the licensed body rig. It is not a 3D scan.\n'+ ('\n'+extra_credits+'\n' if extra_credits else ''))
bpy.context.preferences.filepaths.save_version=0
for obj in list(bpy.data.objects):
    if obj.type!='MESH':continue
    used={poly.material_index for poly in obj.data.polygons}
    for index in reversed(range(len(obj.data.materials))):
        if index not in used:obj.data.materials.pop(index=index)
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/('robot-study.blend' if ROBOT_STUDY else 'zhilinhe92.blend')))
bpy.ops.export_scene.gltf(filepath=str((HERE/'robot-study.glb') if ROBOT_STUDY else (OUT/'atelier.glb')),export_format='GLB',export_yup=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_nla_strips_merged_animation_name='Echo',export_frame_range=True,export_force_sampling=True,export_apply=True,export_extras=True,export_materials='EXPORT')
print('SCENE_AUDIT '+json.dumps({k:audit[k] for k in ['mesh_objects','triangles','human_bounds','robot_bounds','human_eye_blender','robot_eye_blender']}))
if '--render' in __import__('sys').argv:
    bpy.ops.render.render(write_still=True)
print('DELIVERED '+str((HERE/'robot-study.glb') if ROBOT_STUDY else (OUT/'atelier.glb')))
