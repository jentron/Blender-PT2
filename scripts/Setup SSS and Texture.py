import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *

#~ PYTHON INTERACTIVE CONSOLE 3.9.2 (default, Feb 25 2021, 12:19:39)  [GCC 9.3.1 20200408 (Red Hat 9.3.1-2)]
#~ 
#~ Builtin Modules:       bpy, bpy.data, bpy.ops, bpy.props, bpy.types, bpy.context, bpy.utils, bgl, blf, mathutils
#~ Convenience Imports:   from mathutils import *; from math import *
#~ Convenience Variables: C = bpy.context, D = bpy.data
#~ 

obj=bpy.context.active_object

for mat_slot in obj.material_slots:
    node_tree=mat_slot.material.node_tree
    node_tree.nodes["Principled BSDF"].inputs['Subsurface'].default_value = 0.05
    node_tree.nodes["Principled BSDF"].inputs['Subsurface Color'].default_value = (0.8, 0.01, 0.025, 1)
#    node_tree.nodes["Image Texture"].image=bpy.data.images['texture name']
    print(mat_slot.name)
    

