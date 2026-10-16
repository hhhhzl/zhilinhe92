"""Kinematic art choreography for the G1. This is not a robot controller.

Every authored angle is clamped to the original Menagerie joint range. Feet stay
in the imported standing pose. No dynamics, balance, or hardware feasibility is
claimed. The head is rigid to the torso, as in the source G1 model.
"""
import math
import numpy as np
import bpy
from mathutils import Vector, Quaternion

FPS=30
DURATION=5.0
DELAY=.12
GESTURE_KEYS=[(0.,'rest'),(.30,'rest'),(1.20,'chest'),(1.55,'chest'),(2.50,'reach'),(2.75,'reach'),(3.90,'open'),(4.00,'open'),(4.85,'rest'),(5.,'rest')]

def linearize_action(action):
    """Dense baked samples must not receive a second, overshooting spline."""
    curves=[]
    if hasattr(action,'fcurves'):curves.extend(action.fcurves)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
    for curve in {c.as_pointer():c for c in curves}.values():
        for key in curve.keyframe_points:key.interpolation='LINEAR'

def set_pose(joints, values):
    for name,j in joints.items():
        angle=max(j['range'][0],min(j['range'][1],values.get(name,0.)))
        j['object'].rotation_quaternion=j['base'] @ Quaternion(j['axis'],angle)
    bpy.context.view_layer.update()

def hand_state(robot,joints,side):
    o=joints[side+'_wrist_yaw_joint']['object']
    m=robot.matrix_world.inverted() @ o.matrix_world
    return np.array(m @ Vector((.091,0,0))), np.array(m.to_3x3() @ Vector((1,0,0))), np.array(m.to_3x3() @ Vector((0,0,1)))

def fit_hand(robot,joints,side,start,target):
    """Position-only shoulder/elbow fit; the hand continues its forearm.

    No palm-normal objective and no wrist DOFs participate in the solve. These
    conservative art limits are stricter than the original G1 hardware ranges.
    """
    names=[side+'_'+s+'_joint' for s in ['shoulder_pitch','shoulder_roll','shoulder_yaw','elbow']]
    limits=[(-1.30,.40),(-.95,.10) if side=='right' else (-.10,.95),(-.70,.70),(-.65,1.40)]
    values=dict(start)
    for name in values:
        if 'wrist_' in name:values[name]=0.
    base=np.array([start.get(n,0.) for n in names])
    target=np.array(target)
    def residual():
        p,_,_=hand_state(robot,joints,side)
        return (p-target)*2.5
    set_pose(joints,values)
    for iteration in range(110):
        error=residual()
        if np.linalg.norm(error)<.006:break
        jac=[]
        for n in names:
            a=values.get(n,0.)
            values[n]=a+.001
            set_pose(joints,values)
            jac.append((residual()-error)/.001)
            values[n]=a
        jac=np.array(jac).T
        current=np.array([values.get(n,0.) for n in names])
        regularization=.001
        delta=np.linalg.solve(jac.T@jac+np.eye(4)*.012,jac.T@(-error)-regularization*(current-base))
        delta=np.clip(delta,-.10,.10)
        for n,d,art_range in zip(names,delta,limits):
            lo=max(joints[n]['range'][0],art_range[0]);hi=min(joints[n]['range'][1],art_range[1])
            values[n]=float(np.clip(values.get(n,0.)+d,lo+.015,hi-.015))
        set_pose(joints,values)
    p,x,z=hand_state(robot,joints,side)
    return values,{'target':target.tolist(),'achieved':p.tolist(),'error_m':float(np.linalg.norm(p-target)),'finger_axis':x.tolist(),'palm_normal':z.tolist()}

def interpolate_pose(poses,t):
    t=max(0.,min(DURATION,t))
    for (a,pa),(b,pb) in zip(GESTURE_KEYS,GESTURE_KEYS[1:]):
        if a<=t<=b:
            u=(t-a)/(b-a)
            u=u*u*(3-2*u)
            return {n:poses[pa].get(n,0.)*(1-u)+poses[pb].get(n,0.)*u for n in poses['rest']}
    return dict(poses['rest'])

def animate_g1(robot,joints):
    rest={n:0. for n in joints}
    for side in ['left','right']:
        rest[side+'_shoulder_pitch_joint']=.08
        rest[side+'_shoulder_roll_joint']=.12 if side=='left' else -.12
        rest[side+'_elbow_joint']=1.28
    poses={'rest':rest}
    diagnostics={}
    # Native robot axes: +X forward, +Y to robot's left, +Z up.
    seed=dict(rest)
    seed.update(right_shoulder_pitch_joint=-.50,right_shoulder_roll_joint=-.12,right_shoulder_yaw_joint=.25,right_elbow_joint=-.40)
    poses['chest'],diagnostics['chest']=fit_hand(robot,joints,'right',seed,(.21,-.085,.98))
    seed=dict(rest);seed.update(right_shoulder_pitch_joint=-.85,right_shoulder_roll_joint=-.10,right_shoulder_yaw_joint=.10,right_elbow_joint=.50,waist_pitch_joint=-.02)
    poses['reach'],diagnostics['reach']=fit_hand(robot,joints,'right',seed,(.40,-.14,.98))
    seed=dict(rest);seed['waist_pitch_joint']=-.05
    seed.update(right_shoulder_pitch_joint=-.35,right_shoulder_roll_joint=-.70,right_shoulder_yaw_joint=.15,right_elbow_joint=.55,left_shoulder_pitch_joint=-.35,left_shoulder_roll_joint=.70,left_shoulder_yaw_joint=-.15,left_elbow_joint=.55)
    poses['open'],diagnostics['open_right']=fit_hand(robot,joints,'right',seed,(.18,-.43,1.02))
    poses['open'],diagnostics['open_left']=fit_hand(robot,joints,'left',poses['open'],(.18,.43,1.02))
    # The performance is baked to ordinary object transforms, retaining G1 links.
    previous={}
    for frame in range(0,int(FPS*DURATION)+1):
        values=interpolate_pose(poses,frame/FPS-DELAY)
        set_pose(joints,values)
        for name,j in joints.items():
            if name.startswith(('left_shoulder','right_shoulder','left_elbow','right_elbow','left_wrist','right_wrist','waist_')):
                q=j['object'].rotation_quaternion.normalized()
                if name in previous and previous[name].dot(q)<0:q.negate()
                j['object'].rotation_quaternion=q;previous[name]=q.copy()
                j['object'].keyframe_insert('rotation_quaternion',frame=frame,group='Echo')
    for j in joints.values():
        o=j['object']
        if o.animation_data and o.animation_data.action:
            o.animation_data.action.name='Echo_'+o.name
            linearize_action(o.animation_data.action)
    robot['performance']='Authored kinematic art loop; not dynamics or a deployable controller'
    robot['response_delay_seconds']=DELAY
    robot['gesture_duration_seconds']=DURATION
    set_pose(joints,rest)
    return {'duration_seconds':DURATION,'delay_seconds':DELAY,'keys':GESTURE_KEYS,'poses':poses,'hand_fit':diagnostics,'wrist_policy':'All six wrist hinge angles are 0 rad in every pose; no end-effector orientation optimization','interpolation':'Smoothstep authoring, quaternion hemisphere continuity, linear baked samples'}
