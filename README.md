# Blender-PT2
This is a fork of the Poser Tools found here: https://www.renderosity.com/mod/freestuff/?item_id=76373

The original Poser Tools allowed Blender 2.61 to import Props, Characters, and Materials. It seems to have fallen out of development and even the parent website is gone.

I have a lot of old Poser content and thought it would be nifty to resurrect this project for Blender 2.8x

How far will I get?

# To INSTALL
Please rename the folder from Blender-PT2 to just PT2 and then import as any other Blender add-on

On Windows I do something like this (assuming Blender 2.93 and the git repository in Documents/source):
```dos
mklink /D %APPDATA%"\Blender Foundation\Blender\2.93\scripts\addons\PT2" %USERPROFILE%"\Documents\source\Blender-PT2\"
```
This allows me to keep my git repository in my normal source code folder and still have the addon installed.

# PCI2 Scripts
Here are some useful scripts for working with the character importer. They are experimental.
* scripts/PrepareCharacter.py -- remove the extra mesh PCI2 creates, adds weld and armature modifiers to the remaining mesh
* scripts/renameBones.py -- rename bones and vertex groups from Poser convention 'lBone' to Blender convention 'bone.L'

* scripts/Setup SSS and Texture.py -- for each material in the active object, set subsurface scattering to default values
* scripts/ApplyPMD.py -- attempt to read and insert PMD morphs as shapekeys. 
