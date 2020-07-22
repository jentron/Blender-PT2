#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2020, Ronald Jensen
# All rights reserved.

from math import *
from mathutils import *

print ('==================================================')
print ('=         Creating Shapekeys                     =')
print ('==================================================')
# print ('Number of Morphs:', len(morphs))

mtrx_swap = Matrix((( 1, 0, 0, 0),
                    ( 0, 1, 0, 0),
                    ( 0, 0, 1, 0),
                    ( 0, 0, 0, 1)) )

def ApplyMorph(ob, morph, mtrx_swap=mtrx_swap ):
    len_deltas=len(morph.deltas)
    if(len_deltas == 0):
        print( 'Morph %s has no data!'%morph.name )
        return
    if(len_deltas != morph.indexes):
        print( 'Morph %s has wrong number of deltas! %d vs %d'%(morph.name, len_deltas, morph.indexes) )
        return

    try:
        sk_basis = ob.data.shape_keys.key_blocks['Basis']
    except:
        sk_basis = ob.shape_key_add(name="Basis", from_mix=False)

    ob.data.shape_keys.use_relative = False
    
    

    # print ("Morph:", morph.name, "Size:", len(morph.deltas) )
    try:
        vg_idx = ob.vertex_groups[morph.group].index # get group index
        vs = [ v for v in ob.data.vertices if vg_idx in [ vg.group for vg in v.groups ] ]
    except:
        vs = [ v for v in ob.data.vertices ]
    
    try:
        sk = ob.data.shape_keys.key_blocks[morph.name]
    except:
        try:
            sk = ob.vertex_groups[morph.group].id_data.shape_key_add(name=morph.name, from_mix=False)
        except:
            sk = ob.shape_key_add(name=morph.name, from_mix=False)
    sk.value = morph.value
    if abs(morph.max - morph.min) < 10: # all default min/max pairs will fail this test
        sk.slider_min = morph.min
        sk.slider_max = morph.max
    else:
        sk.slider_min = -1
        sk.slider_max = 1

    # position each vert 
    for d in morph.deltas:
        for i, v in d.items():
            v_idx = vs[i].index
            sk.data[v_idx].co = sk_basis.data[v_idx].co + mtrx_swap @ Vector(v)
    ob.data.shape_keys.use_relative = True
