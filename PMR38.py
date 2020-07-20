#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2011-2012, HEB Ventures, LLC
# Copyright (c) 2020, Ronald Jensen
# All rights reserved.

# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:

# *    Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
# *    Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#=============================================================================

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

###################################################
#
#  Poser Mat Reader Version 12
#  1/8/2012
#  www.blender3dclub.com
#
###################################################

##########################################################

import bpy
import time
import os

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

## Setup PT2/libs as a module path:
import sys
local_module_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'libs')
print(local_module_path)
sys.path.append(local_module_path)

import PT2_open as ptl
import RuntimeFolder as Runtime
import Material as matlib
import shaderTrees as st
import shaderTreeParser as stp
import createBlenderMaterialfromP4 as cbm4

print ('--- Starting Poser Mat Reader Version 3 ---')

# ------------ Missing texture pup -----------------------
class ErrorPup(bpy.types.Operator):
    bl_idname = "object.dialog_operator"
    label = "Missing texture file: "
    bl_label = label

    def execute(self, context):
        message = "Texture not found at listed directory"
    #        (self.my_float, self.my_bool, self.my_string)
        self.report({'INFO'}, message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
# ------------ Material Popper -----------------------
class MatPopper(bpy.types.Operator):
    bl_idname = "mat.popper"
    label = "Mat Popper"
    bl_label = label
    #mats = bpy.data.materials

    def execute(self, context):
        obj = bpy.context.active_object
        mats = obj.data.materials
        mat1 = bpy.data.materials
        for x in range(0, len(mats)):
            mats.pop(0)

        return {'FINISHED'}

# -----------------------------------------------------------

# def find_file(poser_file, self_file_path):
#     rt=Runtime(self_file_path)
#     file_location = rt.find_texture_path(poser_file)
#     return(file_location)
# -----------------------------------------------------------


class Save_Mat(bpy.types.Operator):
    '''Save Poser material file for this object'''
    bl_idname = "save.mat"  
    bl_label = "Save Mat File"

    
    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        try:
            Thumb = bpy.data.images['Render Result'] 
            print ('Saving Thumb nail...')
            print (Thumb)
            print (Thumb.file_format)
            Thumb.file_format = 'PNG'
            obj_name = bpy.context.active_object.name
            thumbpath = bpy.PoserPropPath + obj_name + '.png'
            Thumb.save_render(thumbpath)
            bpy.ops.object.ok_pup('INVOKE_DEFAULT')             
        except:
            print ('No Rendered Image to save')
            bpy.ops.object.missing_render('INVOKE_DEFAULT')    
            #break        

        return {'FINISHED'}  
    
class Read_Mat(Operator, ImportHelper):
    '''Read Poser material file for this object'''
    bl_idname = "read.mat"  
    bl_label = "Read Mat File"
    filename_ext = ".pp2"
    #filter_glob = StringProperty(default="*.pp2", options={'HIDDEN'})    
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    overwrite: BoolProperty(
        name="Overwrite Materials",
        description="Overwrite current materials with the same name",
        default=True,
    )

    create_slots: BoolProperty(
        name="Add Material Slots",
        description="Add missing materials slots to the current object",
        default=True,
    )

    shader_type: EnumProperty(
        name="Import Mode",
        description="Use P4 Materials or Shader Tree Materials",
        items=(
            ('OPT_P4', "P4 Materials", "Simple Principled BDSF"),
            ('OPT_ST', "Shader Tree", "Translate Shader Tree to Blender"),
        ),
        default='OPT_P4',
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print ('Reading Mat File:...\n\n')

        #########################################
        #  
        # Read Mat File
        # 
        
        file = ptl.PT2_open(self.filepath, 'rt')
        lines = []
        for x in file:
            lines.append(x.strip())
        file.close() 

        raw_mats = [] # an array of the unparsed materials
        mat_name = ''
        comps = []    # a list of the unparsed lines
        readcomps = False
        depth = 0
        
        for line in lines:
            #print (line)
            skip = 0
            if line.startswith('material') is True:
                #print ('Mat:', line.replace('material', ''))
                mat_name = line.replace('material', '').strip()
                readcomps = True # Turn on component reader
                print ('Mat Name:', mat_name)
                skip = 1
                
            elif line.startswith('{') is True and readcomps is True:
                depth += 1
                #skip = 1
               
                
            elif line.startswith('}') is True and depth > 0:
                depth -= 1
                #skip = 1
                
            if readcomps == True and skip != 1:
                #print(depth, line)
                comps.append([depth, line.split()]) 
               
            if depth == 0 and readcomps is True and len(comps) > 0:
                readcomps=False
                raw_mats.append([mat_name, comps])
                mat_name = ''
                comps = []
                

        #########################################
        #  
        # Displays Mat Array
        #                 
        print ('\n\nFinished creating array...\n')
        dumpfile=None
        #dumpfile=open(r'c:\tmp\dumpfile.txt', 'wt')
        if dumpfile:
            for mat in raw_mats:
                print (mat[0], file=dumpfile)
                for comp in mat[1]:
                    print (comp, file=dumpfile)
                print ('\n', file=dumpfile)
            dumpfile.close()

##
## At this point we need to call the material parser with raw_mats and get the parsed results back
##
        dumpfile=None
        #dumpfile=open(r'c:\tmp\dumpfile.mc6', 'wt')
        
        mats={}
        for raw_mat in raw_mats:
            mats[raw_mat[0]] = stp.parseMaterial( iter(raw_mat[1]), raw_mat[0] )
            if dumpfile:
                mats[raw_mat[0]].write(depth=1, file=dumpfile)
        
        if dumpfile:
            dumpfile.close()
        
        bpy.PT2_mats=mats # save the parsed array into the bpy for future use
        #########################################
        #  
        # Change / Create Mats for selected Object:
        #             
        runtime=Runtime.Runtime(self.filepath)
        newmats=[]
        
        # mats is a dictionary
        # so this iterates keys (names)
        for mat in mats: 
            newmats.append( 
                cbm4.createBlenderMaterialfromP4(mat, mats[mat], runtime, overwrite=self.overwrite)
                )
        
        if self.create_slots:
            obj = bpy.context.active_object

            objmats = obj.data.materials
            for mat in newmats:
                if mat.name in objmats:
                    pass
                else:
                    objmats.append(mat)
                    print ('Adding:', mat.name)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
        
class PT2_PT_Mat_Reader(bpy.types.Panel):
    bl_label = "Poser Mat Reader Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        
        #  Create Menu:

        #read_dir()
      

        layout = self.layout
 
        obj = context.object
        row = layout.row()
        try:        
           row.label(text='Current Object: ' + bpy.context.active_object.name)
        except:
           row.label(text='No object Selected')
        row = layout.row()       
        #row.label(text=bpy.PoserTexturePath)             
        row.operator("save.mat", icon = "DISK_DRIVE", text = 'Save Mat File')
        row.operator("read.mat", icon = "DISK_DRIVE", text = 'Read Mat File')   
        row = layout.row()                     
        
        #row.operator("mat.popper", text = 'Mat Popper')
        #row.operator("import.poser_cr2", icon = "ARMATURE", text = 'Import Character')
        

        #row.operator("export.prop", icon = "DISK_DRIVE", text = 'Save Prop')
        #row = layout.row()
        #row.operator("save.thumb", icon = "RENDER_RESULT", text = 'Save Thumb Nail')        
        #box = layout.box()

        #row = box.row()
        #row.label(text="Current Prop Path:")
        #row = box.row()
        #row.operator("set.proppath", icon = "FILE_FOLDER", text = '')
        #row.label(text=bpy.PoserPropPath)
        
        #box2 = layout.box()
        #row = box2.row()
        #row.label(text="Current Geometry Path:")
        #row = box2.row()
        #row.operator("set.geometrypath", icon = "FILE_FOLDER", text = '')
        #row.label(text=bpy.PoserGeometryPath)  
        
        # Commented because texture path doesnot exist on lap top. 1/24/12
        #box3 = layout.box()
        #row = box3.row()
        #row.label(text="Current Texture Path:")
        #row = box3.row()
        #row.operator("set.texturepath", icon = "FILE_FOLDER", text = '')
        #row.label(text=bpy.PoserTexturePath)          
        

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(MatReader.bl_idname, text="Poser Mat Reader")

def register():
    #bpy.utils.register_class(MatReader)
    #bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(PT2_PT_Mat_Reader)
    bpy.utils.register_class(Save_Mat)
    bpy.utils.register_class(Read_Mat)
    #bpy.utils.register_class(MatPopper)

def unregister():
    #bpy.utils.unregister_class(MatReader)
    #bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(PT2_PT_Mat_Reader)    
    bpy.utils.unregister_class(Save_Mat)
    bpy.utils.unregister_class(Read_Mat)    
    #bpy.utils.unregister_class(MatPopper)

if __name__ == "__main__":
    register()        
        