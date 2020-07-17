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
from bpy_extras import *
from bpy_extras.image_utils import load_image
from bpy.props import StringProperty, BoolProperty, EnumProperty

## Setup PT2/libs as a module path:
import sys
local_module_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'libs')
print(local_module_path)
sys.path.append(local_module_path)

import PT2_open as ptl
import RuntimeFolder as Runtime
import Material as matlib

print ('\n')
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

def find_file(poser_file, self_file_path):
    rt=Runtime(self_file_path)
    file_location = rt.find_texture_path(poser_file)
    return(file_location)
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
    
class Read_Mat(bpy.types.Operator):
    '''Read Poser material file for this object'''
    bl_idname = "read.mat"  
    bl_label = "Read Mat File"
    filename_ext = ".pp2"
    #filter_glob = StringProperty(default="*.pp2", options={'HIDDEN'})    
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")

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

        mats = []         
        mat = ''
        comps = []
        readcomps = False
        depth = 0
        
        for line in lines:
            #print (line)
            skip = 0
            if line.startswith('material') is True:
                #print ('Mat:', line.replace('material', ''))
                mat = line.replace('material', '').strip()
                readcomps = True # Turn on component reader
                print ('Mat Name:', mat)
                skip = 1
                
            elif line.startswith('{') is True and readcomps is True:
                depth += 1
               
                
            elif line.startswith('}') is True and depth > 0:
                depth -= 1
                
            if readcomps == True and skip != 1:
                #print(depth, line)
                comps.append(line.split()) 
               
            if depth == 0 and readcomps is True and skip != 1:
                readcomps=False
                mats.append([mat, comps])
                mat = ''
                comps = []
                

        #########################################
        #  
        # Displays Mat Array
        #                 
        print ('\n\nFinished creating array...\n')
        #for mat in mats:
        #    print (mat[0])                
        #    for comp in mat[1]:
        #        print (comp)
        #    print ('\n')

        #########################################
        #  
        # Change / Create Mats for selected Object:
        #             
                      
        obj = bpy.context.active_object
        
        #########################################
        #  
        # Check if Mat exists, if not - create
        # 
        #        
        print ('Checking Materials:')
        BMats = bpy.data.materials
        OBJMats = obj.data.materials
        add_list = []
        mat_check = False
        print ('Mats in file:')
        print ('-----------------------------------------\n')        
        for mat in mats:
            print (mat[0])
        print ('-----------------------------------------\n')
        
        

        for mat in mats:
            if BMats.__contains__(mat[0]) is False:
                bpy.data.materials.new(mat[0])
                print ('Adding:', mat[0])
   
           
            
                                    
                    
        #  Check if Slotted:
        #print (len(obj.material_slots))
        
        if len(obj.material_slots) > 0:
            for matslot in obj.material_slots:
                for mat in mats:
                    if mat[0] == matslot.name:
                        skip = True
                    else:
                        passthisone = True
                        #OBJMats.append(BMats[mat[0]])
                        #print ('Need to add slot for ', mat[0])

        else: #Add All:                        
            for mat in mats:
                print ('adding all mats...')
                OBJMats.append(BMats[mat[0]])
                
                
        

        for matslot in obj.material_slots:
            #print ('\n')
            #print (matslot.name)
            #print (bpy.data.materials[matslot.name].diffuse_color)       
            for mat in mats:
                # Does not create new mats - only change existing.
                if mat[0] == matslot.name:
                    material = bpy.data.materials[matslot.name]
                    
                    #Default settings for all Materials
                    material.specular_alpha = 0 # Turn off alpha spec
                    print ('\n-----------------------------------------------------------------')
                    print ('matname:', mat[0])
                    for comp in mat[1]:
                        
                        # Create unique texture names
                        texName = mat[0] + '_' + 'tex'
                        bumName = mat[0] + '_' + 'bum'
                        traName = mat[0] + '_' + 'tra'                        
                        

                        if comp[0] == 'KdColor':
                            print (comp)
                            color = []
                            color.append(float(comp[1]))
                            color.append(float(comp[2]))
                            color.append(float(comp[3]))
                            #print(color)
                            material.diffuse_color = color
                            color = []
                            
                        elif comp[0] == 'KsColor':
                            print (comp)
                            color = []
                            color.append(float(comp[1]))
                            color.append(float(comp[2]))
                            color.append(float(comp[3]))
                            #print(color)
                            material.specular_color = color
                            color = []   
                            
                        elif comp[0] == 'tMax': # Transparency Value
                            print (comp)
                            transparency = 1 - float(comp[1])
                            material.use_transparency = True
                            material.alpha = transparency
                                                     

                        ################################################
                        #
                        #  Texture Map
                        #
                        
                        elif comp[0] == 'textureMap' and comp[1] != 'NO_MAP':
                            print ('texture:', comp[1])
                            # Need to clear/replace any existing texture that uses color
                            slots = material.texture_slots
                            for x in range(0, len(slots)):
                                try:
                                    if slots[x].use_map_color_diffuse == True:
                                        material.texture_slots.clear(x)
                                        
                                except:
                                    pass
                                
                            
                            
                            # Check if image already loaded
                            temp = comp[1].split(':')
                            complen = len(comp[1].split(':'))-1
                            temp = temp[complen]
                            temp = temp.strip('"')
                            #print ('Image: ', temp)
                            imgs = bpy.data.images
                            already_loaded = False

                            for img in imgs:
                                if temp == img.name:
                                    already_loaded = True
                                    # May need to add check box to reload / overwrite images

                            if already_loaded == False:
                                #print ('Loading texture: ')
                                image_path = find_file(comp[1], self.filepath)
                                DIR = os.path.dirname(image_path)
                                newimage = load_image(image_path, DIR)
                                #print ('image path:', image_path)

                                already_loaded = True

                            if already_loaded == True:
                                #Check if texture already exists:
                                texture_exists = False
                                texs = bpy.data.textures
                                for tex in texs:
                                    if tex != None:
                                        if tex.name == texName:# Texture Exists
                                            tex.type = 'IMAGE'
                                            tex.image = bpy.data.images[temp]
                                            texture_exists = True
                                            
                                if texture_exists == False: # Creating Texture
                                    #print ('Creating Texture')
                                    tex = bpy.data.textures.new(name = texName, type = 'IMAGE')
                                    tex.image = bpy.data.images[temp]
                                    
                                    

                                # Check if slotted, if not add texture slot
                                # Add texture slot to material
                                tex = bpy.data.textures[texName]                               
                                if material.texture_slots.__contains__(texName): #slot exists
                                    ts = material.texture_slots[texName]
                                    ts.use_map_color_diffuse = True   
                                    ts.use_map_normal = False
                                    ts.texture_coords = 'UV'  
                                    ts.use = True
                                        
                                else: # Adding texture slot
                                    ts = material.texture_slots.add()            
                                    ts.texture = tex
                                    ts.texture_coords = 'UV'
                                    ts.use_map_color_diffuse = True              
                                    ts.use_map_normal = False                                        
                                    ts.use = True
                                    #print ('adding texture slot')

                                        
                        elif comp[0] == 'textureMap' and comp[1] == 'NO_MAP':  
                            # Remove texture from slots
                            if material.texture_slots.__contains__(texName):
                                for x in range(0, len(material.texture_slots)):
                                    ms = material.texture_slots[x]
                                    #print (ms)
                                    if ms != None:
                                        if ms.name == texName:
                                            material.texture_slots.clear(x)
                                            
                            # Need to clear/replace any existing texture that uses color
                            slots = material.texture_slots
                            for x in range(0, len(slots)):
                                try:
                                    if slots[x].use_map_color_diffuse == True:
                                        material.texture_slots.clear(x)
                                        
                                except:
                                    pass                                            
                                            
                                            
                        ################################################
                        #
                        #  Bump Map
                        #                                            

                        #elif comp[0] == 'Nothing':
                        elif comp[0] == 'bumpMap' and comp[1] != 'NO_MAP':
                            
                            # Bump image names end with .bum instead of .jpg?
                            #temp = comp[1]
                            if comp[1].endswith('.bum"'):
                                comp[1] = comp[1].replace('.bum', '.jpg')   
                            #print ('comp1:', comp[1])                            
                            
                            # Check if image already loaded
                            temp = comp[1]
                            temp = temp.split(':')
                            complen = len(temp)-1
                            temp = temp[complen]
                            temp = temp.strip('"')
                            #print ('Image: ', temp)
                            imgs = bpy.data.images
                            already_loaded = False

                            for img in imgs:
                                if temp == img.name:
                                    already_loaded = True
                                    # May need to add check box to reload / overwrite images

                            if already_loaded == False:
                                #print ('Loading texture: ')
                                #print ('comp[1]:', comp[1])
                                #print ('self.filepath:', self.filepath)                                
                                image_path = find_file(comp[1], self.filepath)
                                
                                DIR = os.path.dirname(image_path)
                                newimage = load_image(image_path, DIR)
                                #print ('image path:', image_path)
                                already_loaded = True

                            if already_loaded == True:
                                #print ('line 342:')
                                #Check if texture already exists:
                                texture_exists = False
                                texs = bpy.data.textures
                                for tex in texs:
                                    if tex != None:
                                        if tex.name == bumName:# Texture Exists
                                            tex.type = 'IMAGE'
                                            tex.image = bpy.data.images[temp]
                                            texture_exists = True
                                            
                                if texture_exists == False: # Creating Texture
                                    tex = bpy.data.textures.new(name = bumName, type = 'IMAGE')
                                    tex.image = bpy.data.images[temp]
                                    
                                # Check if slotted, if not add texture slot
                                # Add texture slot to material
                                tex = bpy.data.textures[bumName]
                                #print ('line360 tex.name:', tex.name)
                                if material.texture_slots.__contains__(bumName): #slot exists
                                    ts = material.texture_slots[bumName]
                                    ts.use_map_color_diffuse = False   
                                    ts.use_map_normal = True
                                    ts.normal_factor = .01
                                    ts.texture_coords = 'UV'  
                                    ts.use = True

                                else: # Adding texture slot
                                    ts = material.texture_slots.add()            
                                    ts.texture = tex
                                    ts.texture_coords = 'UV'
                                    ts.use_map_color_diffuse = False         
                                    ts.use_map_normal = True
                                    ts.normal_factor = .01                                        
                                    ts.use = True
                                    #print ('adding texture slot')
                                        
                        elif comp[0] == 'bumpMap' and comp[1] == 'NO_MAP':  
                            # Remove texture from slots
                            if material.texture_slots.__contains__(bumName):
                                for x in range(0, len(material.texture_slots)):
                                    ms = material.texture_slots[x]
                                    #print (ms)
                                    if ms != None:
                                        if ms.name == bumName:
                                            material.texture_slots.clear(x)
                            
                            
                            
                        ################################################
                        #
                        #  Transparency Map
                        #
                        
                        elif comp[0] == 'transparencyMap' and comp[1] != 'NO_MAP':
                            
                            # Need to clear/replace any existing texture that uses color
                            print ('Transparency:', comp[1])
                            slots = material.texture_slots
                            for x in range(0, len(slots)):
                                try:
                                    if slots[x].use_map_alpha == True:
                                        material.texture_slots.clear(x)
                                        
                                except:
                                    pass
                                
                            
                            
                            # Check if image already loaded
                            temp = comp[1].split(':')
                            complen = len(comp[1].split(':'))-1
                            temp = temp[complen]
                            temp = temp.strip('"')
                            #print ('Image: ', temp)
                            imgs = bpy.data.images
                            already_loaded = False

                            for img in imgs:
                                if temp == img.name:
                                    already_loaded = True
                                    # May need to add check box to reload / overwrite images

                            if already_loaded == False:
                                #print ('Loading texture: ')
                                image_path = find_file(comp[1], self.filepath)
                                DIR = os.path.dirname(image_path)
                                newimage = load_image(image_path, DIR)
                                #print ('image path:', image_path)

                                already_loaded = True

                            if already_loaded == True:
                                #Check if texture already exists:
                                texture_exists = False
                                texs = bpy.data.textures
                                for tex in texs:
                                    if tex != None:
                                        if tex.name == traName:# Texture Exists
                                            tex.type = 'IMAGE'
                                            tex.image = bpy.data.images[temp]
                                            tex.use_alpha = False
                                            texture_exists = True
                                            
                                if texture_exists == False: # Creating Texture
                                    #print ('Creating Texture')
                                    tex = bpy.data.textures.new(name = traName, type = 'IMAGE')
                                    tex.image = bpy.data.images[temp]
                                    tex.use_alpha = False
                                    
                                    

                                # Check if slotted, if not add texture slot
                                # Add texture slot to material
                                tex = bpy.data.textures[traName]                               
                                if material.texture_slots.__contains__(traName): #slot exists
                                    ts = material.texture_slots[traName]
                                    ts.use_map_color_diffuse = False   
                                    ts.use_map_alpha = True
                                    #ts.normal_factor = .01
                                    ts.texture_coords = 'UV'  
                                    ts.use = True
                                        
                                else: # Adding texture slot
                                    ts = material.texture_slots.add()            
                                    ts.texture = tex
                                    ts.texture_coords = 'UV'
                                    ts.use_map_color_diffuse = False         
                                    ts.use_map_alpha = True
                                    #ts.normal_factor = .01                                        
                                    ts.use = True
                                    #print ('adding texture slot')

                                        
                        elif comp[0] == 'transparencyMap' and comp[1] == 'NO_MAP':  
                            # Remove texture from slots
                            #print ('Removing Tra-Map from slot:', traName)
                            if material.texture_slots.__contains__(traName):
                                for x in range(0, len(material.texture_slots)):
                                    ms = material.texture_slots[x]
                                    #print (ms)
                                    if ms != None:
                                        if ms.name == traName:
                                            material.texture_slots.clear(x)
                                            
                            # Need to clear/replace any existing texture that uses alpha
                            slots = material.texture_slots
                            for x in range(0, len(slots)):
                                try:
                                    if slots[x].use_map_color_alpha == True:
                                        material.texture_slots.clear(x)
                                        
                                except:
                                    pass                              
                            
                        elif comp[0] == 'reflectionMap':
                            #print (comp[1])             
                            pass_this_step = True
                

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
        