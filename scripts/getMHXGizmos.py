import sys, os.path
import json
import bpy

target='import_runtime_mhx2/armature/data/mhx/gizmos.json'
gizmos={}

for path in sys.path:
    full_path=os.path.join(path, target)
    if os.path.exists(full_path):
        print('Found gizmos at'+full_path)
        with open(full_path) as f_in:
            gizmos=json.load(f_in)
        break

gizmo='GZM_Knuckle'
print(gizmos[gizmo])

collection=bpy.data.collections.get('Hidden')
if not collection:
    collection=bpy.data.collections.new('Hidden')
    bpy.context.collection.children.link(collection)

mesh = bpy.data.meshes.new(gizmo)
gizmoObj = bpy.data.objects.new(gizmo, mesh)
collection.objects.link(gizmoObj)

mesh.from_pydata(gizmos[gizmo]['verts'], gizmos[gizmo]['edges'], [])
