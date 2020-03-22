#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2011-2012, HEB Ventures, LLC
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

###################################################
#
#  Poser Mat Reader Version 11
#  1/8/2012
#  www.blender3dclub.com
#
###################################################

##########################################################
# Check system
#  



import bpy
import time
import sys
import os
from bpy_extras import *
from bpy_extras.image_utils import load_image
from bpy.props import StringProperty, BoolProperty, EnumProperty

print ('\n')
print ('--- Starting Poser Mat Reader Version 3 ---')
systemType = sys.platform
print ('System Type:', systemType)

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

def find_file(poserfile, selffilepath):
    poserfile = poserfile.strip('"')
    print ('Poser File:', poserfile)
    print ('SelfFilePath:', selffilepath)
    if systemType == 'win32':
        temp = selffilepath.split('\\')
        temp2 = poserfile.lstrip(':').replace(':', '\\')
        if temp2.startswith('runtime') is False and temp2.startswith('Runtime') is False:
            if temp2.startswith('textures') is False and temp2.startswith('Textures') is False:
                temp2 = 'textures\\' + temp2
            temp2 = 'runtime\\' + temp2
        print ('temp2:', temp2)            
        comp_path = ''
        #print ('temp=', temp)
        complete = False
        for temp3 in temp:
            if temp3 == 'Runtime' or temp3 == 'runtime':
                #comp_path = comp_path + temp3 + '\\'
                comp_path = comp_path + temp2
                complete = True
            #if temp3 == 'Textures' or temp3 == 'textures':
                #comp_path = comp_path + temp3 + '\\'
            #    comp_path = comp_path + temp2
            #    complete = True                
                
            else:
                if complete == False:
                    comp_path = comp_path + temp3 + '\\'
        print ('comp_path:', comp_path) 
        
    if systemType == 'linux2':
        temp = selffilepath.split('/')
        temp2 = poserfile.lstrip(':').replace(':', '/')
        if temp2.startswith('runtime') is False and temp2.startswith('Runtime') is False:
            if temp2.startswith('textures') is False and temp2.startswith('Textures') is False:
                temp2 = 'textures/' + temp2
            temp2 = 'runtime/' + temp2
        print ('temp2:', temp2)            
        comp_path = ''
        #print ('temp=', temp)
        complete = False
        for temp3 in temp:
            if temp3 == 'Runtime' or temp3 == 'runtime':
                #comp_path = comp_path + temp3 + '\\'
                comp_path = comp_path + temp2
                complete = True
            #if temp3 == 'Textures' or temp3 == 'textures':
                #comp_path = comp_path + temp3 + '\\'
            #    comp_path = comp_path + temp2
            #    complete = True                
                
            else:
                if complete == False:
                    comp_path = comp_path + temp3 + '/'
        print ('comp_path:', comp_path)            
                   
         
    file_location = comp_path
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
    bl_idname = "read.mat2"  
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
        
        file = open(self.filepath, 'r')
        lines = []
        for x in file:
            lines.append(x.strip())
        file.close() 

        mats = []         
        mat = ''
        comps = []
        readcomps = False
        
        for line in lines:
            line = line.strip()
            #print (line)
            skip = 0
            if line.startswith('material') is True:
                #print ('Mat:', line.replace('material', ''))
                mat = line.replace('material', '').strip()
                readcomps = True # Turn on component reader
                print ('Mat Name:', mat)
                skip = 1
                
            elif line.startswith('{') is True:
                skip = 1
               
                
            elif line.startswith('}') is True and readcomps == True:
                readcomps = False
                mats.append([mat, comps])
                mat = ''
                comps = []
                
            if readcomps == True and skip != 1:
                comps.append(line.split())                
               

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
    
        
class Mat_Reader(bpy.types.Panel):
    bl_label = "Poser Mat Reader "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
 
    def draw(self, context):
        
        #  Create Menu:

        #read_dir()
      

        layout = self.layout
 
        obj = context.object
        row = layout.row()
        
        row.label(text='Current Object: ' + bpy.context.active_object.name)
        row = layout.row()       
        #row.label(text=bpy.PoserTexturePath)             
        #row.operator("save.mat", icon = "DISK_DRIVE", text = 'Save Mat File')
	
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
    #bpy.utils.register_class(Mat_Reader)
    bpy.utils.register_class(Save_Mat)
    bpy.utils.register_class(Read_Mat)
    #bpy.utils.register_class(MatPopper)

def unregister():
    #bpy.utils.unregister_class(MatReader)
    #bpy.types.INFO_MT_file_import.remove(menu_func_import)
    #bpy.utils.unregister_class(Mat_Reader)    
    bpy.utils.unregister_class(Save_Mat)
    bpy.utils.unregister_class(Read_Mat)    
    #bpy.utils.unregister_class(MatPopper)

if __name__ == "__main__":
    register()        
        