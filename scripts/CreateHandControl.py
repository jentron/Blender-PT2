import bpy
#from mathutils import *
#from math import *

# for each finger

## add a control bone goes from base of 1st bone to tip of last bone 3 for fingers, 2 for thumb
hand_bones={
'f_Index': {'parent': 'Hand',  'joints': ('Index1','Index2','Index3',)},
'f_Mid'  : {'parent': 'Hand',  'joints': ('Mid1',  'Mid2',  'Mid3',)},
'f_Ring' : {'parent': 'Hand',  'joints': ('Ring1', 'Ring2', 'Ring3',)},
'f_Pinky': {'parent': 'Hand',  'joints': ('Pinky1','Pinky2','Pinky3',)},
'f_Thumb': {'parent': 'Thumb1','joints': ('Thumb2','Thumb3',)},
}

## Left on Layer 6, right on Layer 23
## for each bone in finger
### add a copy rotation constraint
### Move bone to its layer

# RIG = bpy.data.objects['Armature']
RIG = bpy.context.active_object
#todo, make sure its an armature
bpy.ops.object.mode_set(mode='EDIT') # start in edit mode

for s in ('.l', '.r'):
    for f in hand_bones:
        finger = f+s.upper()
        joints=hand_bones[f]['joints']
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
        RIG.data.edit_bones[finger].parent = RIG.data.edit_bones[hand_bones[f]['parent'] + s]


bpy.ops.object.mode_set(mode='POSE')
for s in ('.l', '.r'):
    for f in hand_bones:
        finger = f+s.upper()
        joints=hand_bones[f]['joints']
        first_joint=True
        for joint in joints:
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

