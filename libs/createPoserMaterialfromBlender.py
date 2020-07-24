
import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *

st = D.texts['shaderTrees.py'].as_module()
mat=st.Material(name='test')

mat.p4 = {
     'KdColor': [1.0, 1.0, 1.0, 1.0],
     'KaColor': [0.0, 0.0, 0.0, 0.0],
     'KsColor': [0.0, 0.0, 0.0, 1.0],
     'TextureColor': [1.0, 1.0, 1.0, 1.0], 
     'NsExponent': [50], 
     'tMin': [0.0], 
     'tMax': [0.0], 
     'tExpo': [0.6], 
     'bumpStrength': [1.0], 
     'ksIgnoreTexture': [0.0], 
     'reflectThruLights': [0.0], 
     'reflectThruKd': [0.0], 
     'textureMap': 'NO_MAP',
     'bumpMap': 'NO_MAP',
     'reflectionMap': 'NO_MAP', 
     'transparencyMap': 'NO_MAP', 
     'ReflectionColor': [1.0, 1.0, 1.0, 1.0], 
     'reflectionStrength': [0.0]
     }
 
mat.write(depth=0)

bpy.context.object.active_material


for mat in  C.active_object.material_slots:
    print(mat.name)
    
    for node in D.materials[mat.name].node_tree.nodes:
        print('\t', node.type, node.name )

print('Done')
