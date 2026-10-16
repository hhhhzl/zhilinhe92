"""Import the MIT Rocketbox performer and author the human side of Echo.

This is an authored artistic performance with a photo-referenced approximate likeness.
Original texture detail, facial rig, hands and skin weights are retained.
"""
from pathlib import Path
import os, math, json, shutil
import bpy
from mathutils import Vector, Matrix, Quaternion
from g1_echo import GESTURE_KEYS,FPS,DURATION,linearize_action

def build_human(here,out):
    source=Path(os.environ.get('HUMAN_ASSET_DIR',str(here.parents[2]/'work'/'rocketbox-source')))
    avatar=source/'Assets/Avatars/Adults/Male_Adult_02'
    before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(avatar/'Export/Male_Adult_02.fbx'),use_anim=False)
    imported=[o for o in bpy.data.objects if o not in before]
    rig=next(o for o in imported if o.type=='ARMATURE')
    meshes=[o for o in imported if o.type=='MESH']
    for o in imported:
        if o.type=='EMPTY' and 'Footsteps' in o.name:bpy.data.objects.remove(o,do_unlink=True)
    human=bpy.data.objects.new('Human',None);bpy.context.collection.objects.link(human)
    human.location=(0,.95,0)
    human['source']='Microsoft Rocketbox / Male_Adult_02 (MIT)'
    human['identity']='Licensed generic performer; not a likeness of Zhilin He'
    human['performance']='Authored artistic gesture; not captured research motion'
    asset=bpy.data.objects.new('Human_Asset',None);bpy.context.collection.objects.link(asset);asset.parent=human
    # Source FBX is correctly upright and looks along Blender -Y after import.
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    low=min(p.z for p in pts);high=max(p.z for p in pts)
    s=1.78/(high-low)
    asset.scale=(s,s,s);asset.location.z=-low*s
    rig.parent=asset
    rig.name='Human_Rig'
    rig.animation_data_clear()
    for o in meshes:
        o.name='Human_Textured_Performer'
        for p in o.data.polygons:p.use_smooth=True
        # One subdivision level softens silhouette while retaining the existing skin.
        bpy.context.view_layer.objects.active=o
        o.select_set(True)
        sub=o.modifiers.new('Refined original surface','SUBSURF');sub.levels=1;sub.render_levels=1
        bpy.ops.object.modifier_move_to_index(modifier=sub.name,index=0)
        bpy.ops.object.modifier_apply(modifier=sub.name)
        o.select_set(False)
    # The source's body atlas also contains the hands and shoes. Split only
    # sweater faces, using the rig weights, so a navy tint never recolors skin.
    navy_materials=set()
    for o in meshes:
        body_index=next(i for i,m in enumerate(o.data.materials) if 'body' in m.name)
        navy=o.data.materials[body_index].copy();navy.name='m003_sweater_navy'
        o.data.materials.append(navy);navy_index=len(o.data.materials)-1
        navy_materials.add(navy)
        groups={g.index:g.name for g in o.vertex_groups}
        cloth_groups={i for i,n in groups.items() if any(s in n for s in ['Spine','Clavicle','UpperArm','Forearm'])}
        skin_groups={i for i,n in groups.items() if any(s in n for s in ['Hand','Finger','Neck','Head'])}
        for p in o.data.polygons:
            if p.material_index!=body_index:continue
            vertices=[o.data.vertices[i] for i in p.vertices]
            cw=sum(g.weight for v in vertices for g in v.groups if g.group in cloth_groups)/len(vertices)
            sw=sum(g.weight for v in vertices for g in v.groups if g.group in skin_groups)/len(vertices)
            center=sum((human.matrix_world.inverted() @ o.matrix_world @ v.co for v in vertices),Vector())/len(vertices)
            torso_hem=center.z>.86 and abs(center.x)<.255 and sw<.15
            if (cw>.40 and sw<.55) or torso_hem:p.material_index=navy_index
    texdir=here/'textures';texdir.mkdir(exist_ok=True)
    texture_audit=[]
    texture_cache={}
    def load_texture(stem,kind):
        if (stem,kind) in texture_cache:return texture_cache[stem,kind]
        path=(here/'textures'/'zhilin-head-albedo.png') if stem=='m003_head_color' else avatar/'Textures'/(stem+'.tga')
        image=bpy.data.images.load(str(path),check_existing=False)
        if kind=='normal':image.colorspace_settings.name='Non-Color'
        max_side=2048 if kind=='color' and 'body' in stem else 1024
        if max(image.size)>max_side:
            factor=max_side/max(image.size);image.scale(round(image.size[0]*factor),round(image.size[1]*factor))
        output_format='PNG' if kind in ['normal','alpha'] else 'JPEG'
        image.filepath_raw=str(texdir/(stem+('.png' if output_format=='PNG' else '.jpg')))
        image.file_format=output_format
        image.save();image.pack()
        texture_audit.append({'name':stem,'size':list(image.size),'format':image.file_format})
        texture_cache[stem,kind]=image
        return image
    for m in {m for o in meshes for m in o.data.materials}:
        is_head='head' in m.name;is_alpha='opacity' in m.name
        stem='m003_opacity' if is_alpha else ('m003_head' if is_head else 'm003_body')
        m.name='Human navy knitted sweater' if m in navy_materials else {'m003_opacity':'Human hair and lashes','m003_head':'Human photographed skin','m003_body':'Human trousers shoes and hands'}[stem]
        m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
        output=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');links.new(p.outputs['BSDF'],output.inputs['Surface'])
        p.inputs['Roughness'].default_value=.58 if is_head else .90
        p.inputs['Specular IOR Level'].default_value=.30 if is_head else .24
        p.inputs['Metallic'].default_value=0
        c=n.new('ShaderNodeTexImage');c.image=load_texture(stem+'_color','alpha' if is_alpha else 'color')
        if m in navy_materials:
            tint=n.new('ShaderNodeMix');tint.data_type='RGBA';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
            tint.inputs[7].default_value=(.06,.115,.23,1)
            links.new(c.outputs['Color'],tint.inputs[6]);links.new(tint.outputs[2],p.inputs['Base Color'])
        elif is_alpha:
            tint=n.new('ShaderNodeMix');tint.data_type='RGBA';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
            tint.inputs[7].default_value=(.12,.14,.17,1);links.new(c.outputs['Color'],tint.inputs[6]);links.new(tint.outputs[2],p.inputs['Base Color'])
        else:links.new(c.outputs['Color'],p.inputs['Base Color'])
        if is_alpha:
            threshold=n.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.42
            links.new(c.outputs['Alpha'],threshold.inputs[0]);links.new(threshold.outputs[0],p.inputs['Alpha'])
            m.surface_render_method='DITHERED';m.use_transparency_overlap=False
        else:
            t=n.new('ShaderNodeTexImage');t.image=load_texture(stem+'_normal','normal')
            normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.30 if is_head else .85
            links.new(t.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],p.inputs['Normal'])
        m.use_backface_culling=False
    bpy.context.view_layer.update()
    from avatar_custom import customize
    customize(human,rig,meshes,here)
    bpy.context.view_layer.update()
    # Record actual imported rest transforms; FBX bone tails are display widgets,
    # so limb lengths come from child joint heads rather than Blender tail length.
    actor_inv=human.matrix_world.inverted()
    rest={b.name:actor_inv @ rig.matrix_world @ b.matrix_local for b in rig.data.bones}
    arm_world_inverse=rig.matrix_world.inverted()
    def pos(name):return rest[name].translation.copy()
    def set_global_delta(name,delta,head=None):
        m=rest[name].copy()
        rotated=delta.to_matrix() @ m.to_3x3()
        for r in range(3):
            for c in range(3):m[r][c]=rotated[r][c]
        if head is not None:m.translation=head
        pb=rig.pose.bones[name]
        pb.rotation_mode='QUATERNION'
        pb.matrix=arm_world_inverse @ human.matrix_world @ m
        pb.location=(0,0,0)
        pb.scale=(1,1,1)
        bpy.context.view_layer.update()
    def frame_rotation(direction,normal):
        y=direction.normalized();z=(normal-y*normal.dot(y)).normalized();x=y.cross(z).normalized()
        return Matrix((x,y,z)).transposed()
    def delta_frame(rest_direction,rest_normal,direction,normal):
        return (frame_rotation(direction,normal) @ frame_rotation(rest_direction,rest_normal).transposed()).to_quaternion()
    limb={}
    for side in ['R','L']:
        names=['Bip01 '+side+' '+x for x in ['UpperArm','Forearm','Hand']]
        shoulder,elbow,wrist=[pos(n) for n in names]
        upper=elbow-shoulder;fore=wrist-elbow
        index=pos('Bip01 '+side+' Finger1');pinky=pos('Bip01 '+side+' Finger4')
        finger=(index+pinky)/2-wrist
        normal=finger.cross(index-pinky).normalized()
        if side=='L':normal=-normal
        limb[side]={'names':names,'shoulder':shoulder,'elbow':elbow,'wrist':wrist,'upper':upper,'fore':fore,'normal':upper.cross(fore).normalized(),'finger':finger,'palm':normal}
    def pose_arm(side,wrist_target,pole):
        l=limb[side];shoulder=l['shoulder'];target=Vector(wrist_target)
        d=target-shoulder;length=d.length;axis=d.normalized()
        a=l['upper'].length;b=l['fore'].length
        # Keep a visible elbow bend: neither a locked elbow nor a deep fold.
        minimum=math.sqrt(a*a+b*b+2*a*b*math.cos(math.radians(135)))
        maximum=math.sqrt(a*a+b*b+2*a*b*math.cos(math.radians(15)))
        length=min(maximum,max(minimum,length));target=shoulder+axis*length
        along=(a*a-b*b+length*length)/(2*length)
        height=math.sqrt(max(0,a*a-along*along))
        bend=Vector(pole)-shoulder;bend=(bend-axis*bend.dot(axis)).normalized()
        elbow=shoulder+axis*along+bend*height
        normal=(elbow-shoulder).cross(target-elbow).normalized()
        set_global_delta(l['names'][0],delta_frame(l['upper'],l['normal'],elbow-shoulder,normal),shoulder)
        set_global_delta(l['names'][1],delta_frame(l['fore'],l['normal'],target-elbow,normal),elbow)
        # Preserve the source's neutral hand-to-forearm relationship. Never aim
        # the hand separately at a world-space palm normal or finger direction.
        hand=rig.pose.bones[l['names'][2]]
        hand.rotation_mode='QUATERNION';hand.rotation_quaternion=Quaternion()
        hand.location=(0,0,0);hand.scale=(1,1,1)
    # All coordinates below are metres in actor space: -Y points to the G1.
    # Fixed poles sit behind the shoulder plane. Their projected directions stay
    # clear of the shoulder-to-wrist axis throughout the loop, preventing the
    # rapid elbow-plane roll that a nearby pole produced on the return.
    gestures={
      'rest':{'R':((-.230,-.015,.868),(-.40,.40,1.15)), 'L':((.230,-.015,.868),(.40,.40,1.15)), 'head':.14,'neck':.04,'curl':1.0},
      'chest':{'R':((-.10,-.15,1.225),(-.40,.40,1.15)), 'L':((.230,-.015,.868),(.40,.40,1.15)), 'head':.12,'neck':.035,'curl':.60},
      'reach':{'R':((-.18,-.43,1.25),(-.40,.40,1.15)), 'L':((.230,-.015,.868),(.40,.40,1.15)), 'head':.09,'neck':.025,'curl':.45},
      'open':{'R':((-.58,-.13,1.30),(-.40,.40,1.15)), 'L':((.58,-.13,1.30),(.40,.40,1.15)), 'head':-.11,'neck':-.045,'curl':.45}}
    # Small additional finger flexion follows each source phalanx toward its
    # palm. The hands remain relaxed in every pose rather than forming a fan.
    fingers={}
    for side in ['R','L']:
        for digit in range(5):
            names=['Bip01 '+side+' Finger'+str(digit)+suffix for suffix in ['', '1', '2']]
            for k,name in enumerate(names):
                direction=pos(names[k+1])-pos(name) if k<2 else pos(name)-pos(names[k-1])
                axis_actor=direction.normalized().cross(-limb[side]['palm']).normalized()
                axis_local=rest[name].to_quaternion().inverted() @ axis_actor
                degrees=([5,8,5] if digit==0 else [12,20,10])[k]
                if digit>0:degrees*=.85+.10*(digit-1)
                fingers[name]=(axis_local,math.radians(degrees))
    animated=['Bip01 '+s+' '+n for s in ['R','L'] for n in ['UpperArm','Forearm','Hand']]+['Bip01 Head','Bip01 Neck','Bip01 Spine1']+list(fingers)
    previous={}
    for frame in range(int(FPS*DURATION)+1):
        t=frame/FPS
        for (a,pa),(b,pb) in zip(GESTURE_KEYS,GESTURE_KEYS[1:]):
            if a<=t<=b:
                u=(t-a)/(b-a);u=u*u*(3-2*u)
                break
        values={k:gestures[pa][k]*(1-u)+gestures[pb][k]*u for k in ['head','neck','curl']}
        for side in ['R','L']:
            values[side]=[Vector(gestures[pa][side][i]).lerp(Vector(gestures[pb][side][i]),u) for i in range(2)]
        bpy.context.scene.frame_set(frame)
        for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
        bpy.context.view_layer.update()
        for side in ['R','L']:pose_arm(side,*values[side])
        for suffix in ['Neck','Head']:
            name='Bip01 '+suffix
            # Local head rotations are converted from the actual imported axes.
            axis=rest[name].to_quaternion().inverted() @ Vector((1,0,0))
            rig.pose.bones[name].rotation_mode='QUATERNION'
            rig.pose.bones[name].rotation_quaternion=Quaternion(axis,values[suffix.lower()])
        # Very small upper-body breathing keeps the planted feet unchanged.
        breathing=rig.pose.bones['Bip01 Spine1'];breathing.rotation_mode='QUATERNION'
        breath_axis=rest['Bip01 Spine1'].to_quaternion().inverted() @ Vector((1,0,0))
        breathing.rotation_quaternion=Quaternion(breath_axis,.0035*math.sin(2*math.pi*t/DURATION))
        for name,(axis,angle) in fingers.items():
            bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION'
            bone.rotation_quaternion=Quaternion(axis,angle*values['curl'])
        for name in animated:
            bone=rig.pose.bones[name];q=bone.rotation_quaternion.normalized()
            if name in previous and previous[name].dot(q)<0:q.negate()
            bone.rotation_quaternion=q;previous[name]=q.copy()
            bone.keyframe_insert('rotation_quaternion',frame=frame,group='Echo')
    rig.animation_data.action.name='Echo_Human'
    linearize_action(rig.animation_data.action)
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
    # Eye anchor comes from the source's two eye bones, with a 1 cm front offset.
    left=rig.matrix_world @ rig.pose.bones['Bip01 LEye'].head
    right=rig.matrix_world @ rig.pose.bones['Bip01 REye'].head
    eye_world=(left+right)/2+Vector((0,-.01,0))
    eye=bpy.data.objects.new('HumanEye',None);bpy.context.collection.objects.link(eye)
    eye.parent=rig;eye.parent_type='BONE';eye.parent_bone='Bip01 Head'
    eye.matrix_world=Matrix.Translation(eye_world)
    human['height_m']=1.78
    human['eye_height_m']=eye_world.z
    human['gesture_duration_seconds']=DURATION
    human['response_delay_seconds']=0.
    shutil.copy2(source/'LICENSE.md',out/'ROCKETBOX-LICENSE.md')
    (here/'human-animation-audit.json').write_text(json.dumps({'source':str(avatar),'rig':rig.name,'mesh':[o.name for o in meshes],'bones':len(rig.data.bones),'animated_bones':animated,'source_height':high-low,'normalization_scale':s,'eye_world_blender':list(eye_world),'texture_audit':texture_audit,'gesture_keys':GESTURE_KEYS,'wrist_policy':'Both hand bones retain identity matrix_basis rotation: source neutral wrist orientation follows the forearm','elbow_flexion_limits_degrees':[15,135],'finger_additional_flexion_degrees':[2.25,23.0],'interpolation':'Per-frame two-link arm IK; quaternion hemisphere continuity; linear baked samples'},indent=2))
    return human,eye
