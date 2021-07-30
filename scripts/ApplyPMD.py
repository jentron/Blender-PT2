readmorph=bpy.data.texts['LIBReadPZMD.py'].as_module()
pmdPath='' # full path to the PMD file
morphs=readmorph.readPZMD(pmdPath)

applymorph=bpy.data.texts['LIBApplyMorph.py'].as_module()
for morph in morphs:
     applymorph.ApplyMorph(D.objects['MeshObject'], morph)
