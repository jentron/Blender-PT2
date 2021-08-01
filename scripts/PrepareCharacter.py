import bpy
C = bpy.context
'''
'PNU_0', "No Scale", "Import model without scaling"
'PNU_4', "Poser 4 Scale", "1 PNU = 8 feet (or 96 inches/2.43 meters)"
'GEEP' , "Dr Geep Scale", "1 PNU = 8 feet 4 inches (or 100 inches/2.54 meters)"
'PNU_6', "Poser 6+ Scale", "1 PNU = 8.6 feet (or 103.2 inches/2.62 meters)"
'''

pnu = 103.2 # in inches
bnu =  C.scene.unit_settings.scale_length

scale_factor = pnu * 0.0254 / bnu
print('Scale Factor: ', scale_factor)

if 'Mesh' in bpy.data.objects:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Mesh'].select_set(True)
    bpy.ops.object.delete(use_global=False)
    
armkey='Body'+str(bpy.cr2count)
if armkey in bpy.data.objects:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[armkey].select_set(True)
    while  bpy.context.mode != 'OBJECT':
        bpy.ops.object.posemode_toggle()
        
    bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.data.objects[armkey].data.display_type = 'STICK'
    bpy.data.objects[armkey].show_in_front = True
    bpy.ops.object.select_all(action='DESELECT')
#    bpy.data.objects[armkey].select_set(False)
#    bpy.data.objects[armkey].hide_viewport = True
mesh_name = 'MeshObject'
if mesh_name in bpy.data.objects:
    ob=bpy.data.objects[mesh_name]
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    if  bpy.context.mode != 'OBJECT':
        bpy.ops.object.posemode_toggle()
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
 #   bpy.context.space_data.context = 'MODIFIER'
    bpy.ops.object.modifier_add(type='WELD')
    bpy.context.object.modifiers["Weld"].merge_threshold = 0.0001
    bpy.context.object.modifiers["Weld"].show_expanded = False
    bpy.ops.object.modifier_add(type='ARMATURE')
    bpy.context.object.modifiers["Armature"].object = bpy.data.objects[armkey]
    bpy.ops.object.shade_smooth()
