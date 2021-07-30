import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import re

for vg in D.objects['MeshObject'].vertex_groups:
    new_name = re.sub(r'^([a-z])([A-Z])(.+)',r'\2\3.\1',vg.name)
    if new_name == vg.name:
        if vg.name.startswith('right'):
            new_name = re.sub(r'^(right)([A-Z])(.+)',r'\2\3.r',vg.name)
        elif vg.name.startswith('left'):
            new_name = re.sub(r'^(left)([A-Z])(.+)',r'\2\3.l',vg.name)
    
    print(vg.name, '->', new_name)
    if new_name != vg.name:
        vg.name = new_name

armkey='Body'+str(bpy.cr2count)
for vg in D.objects[armkey].data.bones:
    new_name = re.sub(r'^([a-z])([A-Z])(.+)',r'\2\3.\1',vg.name)
    if new_name == vg.name:
        if vg.name.startswith('right'):
            new_name = re.sub(r'^(right)([A-Z])(.+)',r'\2\3.r',vg.name)
        elif vg.name.startswith('left'):
            new_name = re.sub(r'^(left)([A-Z])(.+)',r'\2\3.l',vg.name)
    print(vg.name, '->', new_name)
    if new_name != vg.name:
        vg.name = new_name
