import bpy
#from mathutils import *
#from math import *

# for each finger

## add a control bone goes from base of 1st bone to tip of last bone 3 for fingers, 2 for thumb
hand_bones={
'f_Index': ('Index1','Index2','Index3',),
'f_Mid'  : ('Mid1',  'Mid2',  'Mid3',),
'f_Ring' : ('Ring1', 'Ring2', 'Ring3',),
'f_Pinky': ('Pinky1','Pinky2','Pinky3',),
'f_Thumb': ('Thumb2','Thumb3',),
}


# RIG = bpy.data.objects['Armature']
RIG = bpy.context.active_object
#todo, make sure its an armature
bpy.ops.object.mode_set(mode='EDIT') # start in edit mode
bpy.ops.object.mode_set(mode='OBJECT') # start in edit mode
bpy.ops.object.mode_set(mode='EDIT') # start in edit mode

for s in ('.l', '.r'):
    for f in hand_bones:
        finger = f+s.upper()
        joints=hand_bones[f]
        parent=RIG.data.edit_bones[joints[ 0] + s ].parent
        head = RIG.data.bones[joints[ 0] + s ].head_local
        tail = RIG.data.bones[joints[-1] + s ].tail_local
        roll = 0
        for joint in joints:
            roll+=RIG.data.edit_bones[joint+s].roll 
        roll /= len(joints)

        RIG.data.edit_bones.new(finger)
        RIG.data.edit_bones[finger].head = head
        RIG.data.edit_bones[finger].tail = tail
        RIG.data.edit_bones[finger].roll = roll
        RIG.data.edit_bones[finger].parent = parent


bpy.ops.object.mode_set(mode='POSE')
### add a copy rotation constraint
### first bone copies all rotations, other bones just copy main rotation
layer=6

## Left on Layer 6, right on Layer 22
### Move each bone to its layer setting on pose.bones and removing on data.bones seems to be the secret sauce in pose mode.

for s in ('.l', '.r'):
    for f in hand_bones:
        finger = f+s.upper()
        RIG.pose.bones[finger].bone.layers[layer]=True
        RIG.data.bones[finger].layers[0]=False
        joints=hand_bones[f]
        first_joint=True
        for joint in joints:
            RIG.pose.bones[joint+s].bone.layers[layer+1]=True
            RIG.data.bones[joint+s].layers[0]=False
            bob=RIG.pose.bones[joint+s].constraints.new("COPY_ROTATION")
            bob.use_x=first_joint
            bob.use_y=first_joint
            bob.use_z=True
            bob.mix_mode='OFFSET'
            bob.target_space='LOCAL'
            bob.owner_space='LOCAL'
            bob.target=RIG
            bob.subtarget=finger
            first_joint=False
    layer+=16
