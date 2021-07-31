
import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *


readmorph=bpy.data.texts['ReadPZMD.py'].as_module()
pmdPath=r'' # full path to the PMD file
morphs=readmorph.readPZMD(pmdPath)

applymorph=bpy.data.texts['ApplyMorph.py'].as_module()
for morph in morphs:
     applymorph.ApplyMorph(D.objects['MeshObject'], morph)
