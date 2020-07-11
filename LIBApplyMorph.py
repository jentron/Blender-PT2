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

def ApplyMorph(ob, morph ):
    try:
        sk_basis = ob.data.shape_keys.key_blocks['Basis']
    except:
        sk_basis = ob.shape_key_add(name="Basis", from_mix=False)

    ob.data.shape_keys.use_relative = False
    
    

    # print ("Morph:", morph.name, "Size:", len(morph.deltas) )
    vg_idx = ob.vertex_groups[morph.group].index # get group index
    vs = [ v for v in ob.data.vertices if vg_idx in [ vg.group for vg in v.groups ] ]
    
    try:
        sk = ob.data.shape_keys.key_blocks[morph.name]
    except:
        sk = ob.vertex_groups[morph.group].id_data.shape_key_add(name=morph.name, from_mix=False)
    sk.value = morph.value
    sk.slider_min = morph.min
    sk.slider_max = morph.max
    
    # position each vert FIXME: there must be a better way...
    for d in morph.deltas:
        for i, v in d.items():
            v_idx = vs[i].index
            sk.data[v_idx].co = sk_basis.data[v_idx].co + mtrx_swap @ Vector(v)
#            sk.data[v_idx].co = sk_basis.data[v_idx].co +  Vector(v)
    ob.data.shape_keys.use_relative = True
