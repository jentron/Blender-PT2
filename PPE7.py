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

###################################################
#
#  Poser Prop Exporter Version 6
#  7/26/2011
#  www.blender3dclub.com
#
###################################################

import bpy
import os, sys, inspect
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


print ('\n--- Starting Poser Prop Exporter Version 6 ---')
print (sys.platform)

bpy.PoserPropPath = "k:\\content\\runtime\\"
bpy.PoserTexturePath = "k:\\content\\runtime\\textures\\"   
bpy.PoserGeometryPath = "k:\\content\\runtime\\geometries\\" 

if sys.platform.startswith('win') is False:
    bpy.PoserPropPath = bpy.PoserPropPath.replace('\\', '/')
    bpy.PoserTexturePath = bpy.PoserTexturePath.replace('\\', '/')
    bpy.PoserGeometryPath = bpy.PoserGeometryPath.replace('\\', '/')
    
print (bpy.PoserPropPath)
print (bpy.PoserTexturePath)
print (bpy.PoserGeometryPath)    
    
# ---------- path finder --------------------
def execution_path(filename):
  return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), filename)

 
bpy.ImageType = ['PNG', '.png']
       

def offCalc(obj):
    tempobj = obj
    xtemp = 0
    ytemp = 0
    ztemp = 0
    
   
    parent_check = True
    while parent_check is True:
        
        if tempobj.parent != None:
            xtemp = xtemp + (tempobj.location[0] - tempobj.parent.location[0])
        else:
            xtemp = xtemp + tempobj.location[0]
            
        if tempobj.parent != None:
            ytemp = ytemp + (tempobj.location[1] - tempobj.parent.location[1])
        else:
            ytemp = ytemp + tempobj.location[1]
            
        if tempobj.parent != None:
            ztemp = ztemp + (tempobj.location[2] - tempobj.parent.location[2])        
        else:
            ztemp = ztemp + tempobj.location[2]            
            
        
        if tempobj.parent == None:
            parent_check = False
        else:
            tempobj = tempobj.parent

    return(xtemp, ytemp, ztemp)


def store_dir():
    # Save Directory Locations
    # Get blender path and store in PT2 Directory
    
    # Find PT2 Folder:
    ############################################
    #propsdir = '\\PT2\\props_dirs.pt2'
    #if sys.platform.startswith('win'):
    #   pass
    #else:
    #   propsdir = propsdir.replace('\\', '/')
    #outstr = os.path.abspath(execution_path('sample.txt'))
    outstr = bpy.PT2path
    outstr = outstr + 'prop_dirs.pt2'   
   
    #print (outstr)     
    ############################################
    
    file = open(outstr, 'w')
    outtext = bpy.PoserPropPath + '\n'
    file.write(outtext)
    outtext = bpy.PoserGeometryPath + '\n'
    file.write(outtext)
    outtext = bpy.PoserTexturePath + '\n'
    file.write(outtext)
    file.close()
    
def read_dir():
    # Find PT2 Folder:
    ############################################      
    #print ('\n---------------------------')

    # get the absolute path of PT2
    outstr = os.path.abspath(execution_path('PT2Main.py'))
    outstr = outstr.replace('PT2Main.py', '')
    #outstr = outstr + '\\PT2\\'
    if sys.platform.startswith('win'):
       pass
    else:
       outstr = outstr.replace('\\', '/')
    #print ('145 outstr:', outstr)
            
    bpy.PT2path = outstr
    outstr = outstr + 'prop_dirs.pt2'   
          
    file = open(outstr, 'r')
    line = []
    for x in file:
        line.append(x)
    file.close()
    bpy.PoserPropPath = line[0].strip()
    bpy.PoserGeometryPath = line[1].strip()
    bpy.PoserTexturePath = line[2].strip()
    return

class NoRender(bpy.types.Operator):
    bl_idname = "object.missing_render"
    label = "Error Message: "
    bl_label = label

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)
    
    def draw(self, context):

        layout = self.layout
        obj = context.object
        row = layout.row()
        col = row.column()        
        col.label(text="Render image not created.  Please create a")
        col.label(text="render at 91px x 91px to save as a thumbnail.")    
bpy.utils.register_class(NoRender)

class NotMesh(bpy.types.Operator):
    bl_idname = "object.not_mesh"
    label = "Error Message: "
    bl_label = label

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)
    
    def draw(self, context):

        layout = self.layout
        obj = context.object
        row = layout.row()
        col = row.column()        
        col.label(text="Please select only Mesh Objects for Exporting.")
        #col.label(text="render at 91px x 91px to save as a thumbnail.")        
bpy.utils.register_class(NotMesh)

class NotPacked(bpy.types.Operator):
    bl_idname = "object.not_packed"
    label = "Error Message: "
    bl_label = label

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)
    
    def draw(self, context):

        layout = self.layout
        obj = context.object
        row = layout.row()
        col = row.column()        
        col.label(text="Please pack all images before exporting.")
bpy.utils.register_class(NotPacked)

class OKpup(bpy.types.Operator):
    bl_idname = "object.ok_pup"
    label = "Export Completed Successfully: "
    bl_label = label

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    
    def draw(self, context):

        layout = self.layout
        obj = context.object
        row = layout.row()
        col = row.column()        
        #col.label(text="Export Comp.")
        #col.label(text="render at 91px x 91px to save as a thumbnail.")        
bpy.utils.register_class(OKpup)

class noUV(bpy.types.Operator):
    bl_idname = "object.no_uv"
    label = "No UVMap for this mesh."
    bl_label = label

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    
    def draw(self, context):

        layout = self.layout
        obj = context.object
        row = layout.row()
        col = row.column()        
        #col.label(text="Export Comp.")
        #col.label(text="render at 91px x 91px to save as a thumbnail.")        
bpy.utils.register_class(noUV)



class PT2_PT_Poser_Prop_Exporter(bpy.types.Panel):
    bl_label = "Poser Prop Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
#    bl_category = "Tool"
    bl_context = "scene"
 
    def draw(self, context):
        
        #  Create Menu:

        read_dir()
      

        layout = self.layout
 
        obj = context.object
        row = layout.row()

        row.operator("export.prop", icon = "DISK_DRIVE", text = 'Save Prop')
        row = layout.row()
        row.operator("save.thumb", icon = "RENDER_RESULT", text = 'Save Thumb Nail')        
        box = layout.box()

        row = box.row()
        row.label(text="Current Prop Path:")
        row = box.row()
        row.operator("set.proppath", icon = "FILE_FOLDER", text = '')
        row.label(text=bpy.PoserPropPath)
        
        box2 = layout.box()
        row = box2.row()
        row.label(text="Current Geometry Path:")
        row = box2.row()
        row.operator("set.geometrypath", icon = "FILE_FOLDER", text = '')
        row.label(text=bpy.PoserGeometryPath)  
        
        box3 = layout.box()
        row = box3.row()
        row.label(text="Current Texture Path:")
        row = box3.row()
        row.operator("set.texturepath", icon = "FILE_FOLDER", text = '')
        row.label(text=bpy.PoserTexturePath)    
        
        
   
class Save_Thumb(bpy.types.Operator):
    '''Save last render as a Thumb Nail for this prop'''
    bl_idname = "save.thumb"  
    bl_label = "Save Thumb"

    
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


class SetPropPath(bpy.types.Operator, ExportHelper):
    '''Select the Prop Folder where this prop will be saved as a .pp2.'''
    bl_idname = "set.proppath"  # this is important since its how bpy.ops.export.some_data is constructed
    bl_label = "Select Folder"

    # ExportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob : StringProperty(default="*.txt", options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        path = self.filepath
        if sys.platform.startswith('win'):
            path = path.split('\\')
        else:
            path = path.split('/')
        path.pop()
        temppath = ''
        for x in path:
            if sys.platform.startswith('win'):
                temppath = temppath + x + '\\'
            else:
                temppath = temppath + x + '/'                
        print (temppath)
        bpy.PoserPropPath = temppath
        store_dir()
        return {'FINISHED'}

    
class SetGeometryPath(bpy.types.Operator, ExportHelper):
    '''Select the Geometry Folder where this prop will save it's .obj file.'''
    bl_idname = "set.geometrypath"  # this is important since its how bpy.ops.export.some_data is constructed
    bl_label = "Select Folder"

    # ExportHelper mixin class uses this
    filename_ext = ".pp2"

    filter_glob : StringProperty(default="*.pp2", options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        path = self.filepath
        
        if sys.platform.startswith('win'):
            path = path.split('\\')
        else:
            path = path.split('/')
        path.pop()
        temppath = ''
        for x in path:
            if sys.platform.startswith('win'):
                temppath = temppath + x + '\\'
            else:
                temppath = temppath + x + '/'

        print (temppath)
        bpy.PoserGeometryPath = temppath
        store_dir()
        return {'FINISHED'}

    
class SetTexturePath(bpy.types.Operator, ExportHelper):
    '''Select the Texture Folder where this prop will save it's texture files.'''
    bl_idname = "set.texturepath"  # this is important since its how bpy.ops.export.some_data is constructed
    bl_label = "Select Folder"

    # ExportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob : StringProperty(default="*.txt", options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        path = self.filepath

        if sys.platform.startswith('win'):
            path = path.split('\\')
        else:
            path = path.split('/')
        path.pop()
        temppath = ''
        for x in path:
            if sys.platform.startswith('win'):
                temppath = temppath + x + '\\'
            else:
                temppath = temppath + x + '/'

        print (temppath)
        bpy.PoserTexturePath = temppath
        store_dir()
        return {'FINISHED'}
    
#################################################
#
#   Save Prop
#
#################################################    
    
class SaveProp(bpy.types.Operator):    
    bl_idname = "export.prop"
    bl_label = "Export Prop"
    
    
    def execute(self, context):
        print ('Saving Prop...')
        
        print ('\n-------------------')
        print (bpy.context.selected_objects)
        objs = bpy.context.selected_objects
        
        def fw(text):
            file.write(text)
            file.write('\n')
            return

        def fwnr(text):
            file.write(text)
            #file.write('\n')
            return        
        print ('\nOBJ List:')
        print (objs)
        print ('------------------------')
        fail_check = False
        for x in objs:
            print (x.type)
            # Check for all mesh type:
            fail_check = False
            if x.type != 'MESH':
                print ('Please select only Mesh Objects')
                #############
                #  error pup
                #############
                bpy.ops.object.not_mesh('INVOKE_DEFAULT')  
                fail_check = True
                
                
        if fail_check == False:
            geom_path = bpy.PoserGeometryPath
            tex_path = bpy.PoserTexturePath
            print ('Len of OBJS:', str(len(objs)))
            for obj in objs:
                    print ('\n\nWorking obj:', obj.name)
                
                    ###########################################
                    #
                    #  Save geometry to geometry folder
                    #
                    #  External OBJS:
                    #            
                    ###########################################
                    
                
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    ###########################################
                    # Apply Scale, location and Rotation First.
                    ###########################################
                    # Rotate X-90, apply, save, then reverse. to
                    # compensate for Poser Difference
                    
                    '''
                    Removed because of Blender 2.58
                    '''
                    #bpy.ops.object.scale_apply()
                    #bpy.ops.object.rotation_apply()
                    bpy.ops.object.transform_apply(rotation=True)
                    
                    #break                              
                    obj.rotation_euler[0] = -1.57
                    bpy.ops.object.transform_apply(rotation=True)                    
                    
                    
                    mesh = obj.data
                    mesh.update()  
                    #break  
                    ###########################################          
                    
                    print ('obj name:', obj.name)                   
                    geom_file = geom_path + obj.name + '.obj'
                    file = open(geom_file, 'w')
                    
                    fw('# File Created with Poser Tools 2 for Blender')
                    fw('# www.blender3dclub.com')
                    fw('')
        
                    ###########################################
                    # Verts
                    
                    # Must add in offset to verts
                    offset = offCalc(obj)
                    
                    verts = obj.data.vertices
                    for vert in verts:
                        xyz = 'v ' + str(vert.co[0]+offset[0]) + ' ' + str(vert.co[1]+offset[2]) + ' ' + str(vert.co[2]-offset[1])
                        fw(xyz)
                    fw('')
                    
                    ###########################################            
                    # UV Verts:
                    # Check first:
                    
                    mesh = obj.data
                    try:
                        uv = mesh.uv_textures[0].data
                        for face in uv:
                            for vertex in face.uv:
                                xy = 'vt ' + str(vertex[0]) + ' ' + str(vertex[1])
                                fw(xy)
                        fw('')
                    except:
                        bpy.ops.object.no_uv('INVOKE_DEFAULT')                         
                        pass                         

                    ###########################################            
                    # Faces
                        
                    faces = obj.data.polygons
                    facecounter = 0
                    vertcounter = 0
                    matlist = mesh.materials   
                    
                    ###########################################            
                    # Mat name space fix:
                    
                    for mat in matlist:
                        mat.name = mat.name.replace(' ','_')
                    
                             
                    currentmat = ''
                        
                    for face in faces:
                        #######################################
                        # 'usemtl' here
                        #
                        #print ('len:', len(matlist))

                        if len(matlist) > 0 and matlist[face.material_index].name != currentmat:
                            print ('usemtl', matlist[face.material_index].name)
                            usemat = '\nusemtl ' + str(matlist[face.material_index].name)
                            fw(usemat)
                            currentmat = matlist[face.material_index].name

                            
                        facetext = 'f '
                        vertlen = len(face.vertices)
                        for verts in range(0,vertlen):
                                ###################
                                # V:
                                facetext = facetext + str(face.vertices[verts]+1)
                                ###################
                                # VT:
                                facetext = facetext + '/' + str(vertcounter+1)
                                ###################
                                #VN:
                                vertcounter += 1
                                facetext = facetext + ' '
                        facecounter +=1
                        fw(facetext)
                   
                        
                    #########################################
                    # Return to original rotation:            
                    obj.rotation_euler[0] = 1.57
                    
                    bpy.ops.object.transform_apply(rotation=True) 
                    
                    
                    mesh.update()
                    #break
                    #########################################
                    file.close()
                    
                    ###########################################
                    #
                    #  Save images to texture folder
                    #            
                    ###########################################
                    mats = mesh.materials
                    for mat in mats:
                        print (mat.name)
                        
                        this_mat = bpy.data.materials[mat.name]
                        textures = this_mat.texture_slots
                        for tex_slot in textures:
                            if tex_slot != None:
                                texture = tex_slot.texture
                                image = texture.image
                                
                                ###########################
                                #
                                #  Check if packed first:
                                #
                                if image.packed_file == None:
                                    bpy.ops.object.not_packed('INVOKE_DEFAULT')  
                                    print ('Image not packed')
                                    fail_check = True
                                    

                                print (dir(image))
                                print ('Pack check:', image.packed_file)
                                
                                #except:
                                #bpy.ops.object.not_packed('INVOKE_DEFAULT')  
                                
                                
                                
                                tex_path = bpy.PoserTexturePath
                                ###################################
                                # 
                                #  Keep format fix
                                #
                                file_ext = ''
                                if image.file_format == 'JPEG':
                                    file_ext = '.jpg'
                                elif image.file_format == 'PNG':
                                    file_ext = '.png'
                                
                                tex_file = tex_path + image.name + file_ext
                                image.filepath = tex_file
                                ###############################
                                # User Select type via toggles
                                print (image.name, image.file_format)
                                
                                #image.file_format = bpy.ImageType[0]
                                image.save()
                                
                    ###########################################
                    #
                    #  Save prop to prop folder
                    #            
                    ###########################################  
                    
                    
                    
                    
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    obj = bpy.context.active_object
                    obj_list = bpy.context.selected_objects
                    
                    ############
                    # cycle through all meshes materials
                    #############
                    
                    
                    mesh = obj.data
                    mats = mesh.materials
                    
                    prop_name = bpy.context.active_object.name
                    prop_file = bpy.PoserPropPath + prop_name + '.pp2'
                    pt2path = bpy.PT2path
                    
                    
                    
                    #file = open(prop_file, 'w')    
                    
                    ####################
                    #
                    #  Version 4 stuff:
                    #
                    ####################
                    print ('\n\n Saving Prop...')
                    #print (bpy.PT2path)   
                    template = bpy.PT2path + 'PropTemplate.pt2' 
                    
                    templfile = open(template, 'r')
                    print('prop file', prop_file)
                    file = open(prop_file, 'w')
                    
                    # Get obj path
                    if sys.platform.startswith('win'):
                        geo_path = bpy.PoserGeometryPath.split('\\')
                    else:
                        geo_path = bpy.PoserGeometryPath.split('/')                  
                    check = 0
                    gp = ''
                    for path in geo_path:
                        if check == 1:
                            gp = gp + ':' + path   
                        elif path == 'geometries' or path == 'Geometries':
                            check = 1                 
                    gp = ':Runtime:geometries' + gp
                    print ('gp:', gp)  
                    geometry_path = gp 
                    
                    # Get texture path
                    if sys.platform.startswith('win'):
                        image_path = bpy.PoserTexturePath.split('\\')
                    else:
                        image_path = bpy.PoserTexturePath.split('/')                
                        
                    check = 0
                    tp = ''
                    for path in image_path:
                        if check == 1:
                            tp = tp + ':' + path
                        elif path == 'textures' or path == 'Textures':
                            check = 1
                    tp = ':Runtime:Textures' + tp        
                    print ('tp:', tp)  
                    texture_path = tp     
                    
                        
                    
                    #print ('image_path:', image_path)
                    
                    for line in templfile:
                        #print (line)
                        if line.startswith('[version]') is True:
                            outstr = '\tversion 4'
                            fw(outstr)
                        elif line.startswith('[prop]') is True:
                            outstr = 'prop ' + obj.name
                            fw(outstr)
                        elif line.startswith('[prop name]') is True:
                            outstr = '\tname ' + obj.name
                            fw(outstr)  
                        elif line.startswith('[objfile]') is True:
                            # cycle through multiple objs
                            for this_obj in obj_list:
                                outstr = 'prop ' + this_obj.name
                                fw(outstr)
                                outstr = '\t{\n\tstorageOffset 0 0.3487 0'
                                fw(outstr)
                                outstr = '\tobjFileGeom 0 0 ' + geometry_path + this_obj.name + '.obj'
                                fw(outstr)
                                outstr = '\t}'
                                fw(outstr)
                                
                        elif line.startswith('[prop details]') is True:
                            print ('Starting prop details')
                            # add details for each prop
                            details = bpy.PT2path + 'PropDetails4.pt2' 
                            for this_obj in obj_list:
                                
                                #
                                #origin = this_obj.location
                                #print ('origin:', origin)
                                #bpy.ops.object.location_apply()    
                                #print ('origin2:', origin)         
                                
                                file3 = open(details, 'r')
                                outstr = 'prop ' + this_obj.name
                                fw(outstr)            
                                        
                                for Dline in file3:
                                    if Dline.startswith('[prop name]') is True:
                                        outstr = '\tname ' + this_obj.name
                                        fw(outstr) 

                                    elif Dline.startswith('[origin]') is True:
                                        #outstr = '\torigin ' + str(this_obj.location[0])+ ' ' + str(this_obj.location[2]) + ' ' + str(this_obj.location[1]*-1)
                                        #fw(outstr)
                                        #print ('origin', outstr)
                                        
                                        #############################
                                        #  Must change to offset amount
                                        
                                        x = offCalc(this_obj)[0]
                                        y = offCalc(this_obj)[2]
                                        z = offCalc(this_obj)[1]
                                        outstr = '\torigin ' + str(x) + ' ' + str(y) + ' ' + str(z*-1)
                                        fw(outstr)

                                    elif Dline.startswith('[parent]') is True:
                                        this_parent = this_obj.parent
                                        if this_parent == None:
                                            this_parent = 'UNIVERSE'
                                        else:
                                            this_parent = this_parent.name
                                        outstr = '\tparent ' + this_parent
                                        fw(outstr)
                                        
                                    elif Dline.startswith('[xOffA]') is True:
                                        outstr = '\t\t\tinitValue'
                                        xoff = offCalc(this_obj)[0]
                                        outstr = outstr + ' ' + str(xoff)
                                        #print (this_obj.name, outstr)
                                        #print (outstr)  
                                        fw(outstr)
                                        
                                    elif Dline.startswith('[xOffB]') is True:
                                        outstr = '\t\t\tinitValue'
                                        xoff = offCalc(this_obj)[0]
                                        outstr = outstr + ' ' + str((xoff)*-1)
                                        #print (this_obj.name, outstr)
                                        #print (outstr)  
                                        fw(outstr)                                         
                                        
                                    elif Dline.startswith('[yOffA]') is True:
                                        outstr = '\t\t\tinitValue'
                                        yoff = offCalc(this_obj)[2]
                                        outstr = outstr + ' ' + str(yoff)
                                        #print (this_obj.name, outstr)
                                        #print (outstr)  
                                        fw(outstr)
                                        
                                    elif Dline.startswith('[yOffB]') is True:
                                        outstr = '\t\t\tinitValue'
                                        yoff = offCalc(this_obj)[2]
                                        outstr = outstr + ' ' + str((yoff)*-1)
                                        #print (this_obj.name, outstr)
                                        #print (outstr)  
                                        fw(outstr)                                        
                                        
                                    elif Dline.startswith('[zOffA]') is True:
                                        outstr = '\t\t\tinitValue'
                                        zoff = offCalc(this_obj)[1]
                                        outstr = outstr + ' ' + str(zoff)
                                        #print (this_obj.name, outstr)
                                        #print (outstr)  
                                        fw(outstr)  
                                        
                                    elif Dline.startswith('[zOffB]') is True:
                                        outstr = '\t\t\tinitValue'
                                        zoff = offCalc(this_obj)[1]
                                        outstr = outstr + ' ' + str((zoff)*-1)
                                        #print (this_obj.name, outstr)
                                        #print (outstr)  
                                        fw(outstr)                                                                                                                                                                                                                     
                                                                               
                                    #########################################
                                    #
                                    #  Rotation Locks:
                                    #
                                    #########################################
                                    
                                    
                                    elif Dline.startswith('[xrotlock]') is True:
                                        if this_obj.lock_rotation[0] is True:
                                            outstr = '\t\t\thidden 1'
                                        else:
                                            outstr = '\t\t\thidden 0'
                                        fw(outstr)

                                    elif Dline.startswith('[yrotlock]') is True:
                                        if this_obj.lock_rotation[2] is True:
                                            outstr = '\t\t\thidden 1'
                                        else:
                                            outstr = '\t\t\thidden 0'
                                        fw(outstr)
                                        
                                    elif Dline.startswith('[zrotlock]') is True:
                                        if this_obj.lock_rotation[1] is True:
                                            outstr = '\t\t\thidden 1'
                                        else:
                                            outstr = '\t\t\thidden 0'
                                        fw(outstr)                                                                                
                                    
                                                       
                    
                                        
                                    #########################################
                                    #
                                    #  Materials:
                                    #
                                    #########################################
                    
                    
                    
                                    elif Dline.startswith('[materials]') is True:
                                        # Cycle though obj materials:
                                        #mesh = obj.data
                                        mats = this_obj.data.materials                    
                                        
                                        for mat in mats:
                                            ######################################
                                            #
                                            #  Mat name space fix:
                                            #
                                            
                                            #mat.name = mat.name.replace(' ','_')
                                            
                                            print (mat.name)
                                            
                                            
                                            outstr = '\tmaterial ' + mat.name
                                            fw(outstr)
                                            outstr = '\t\t{'
                                            fw(outstr)
                                            mat_temp = bpy.PT2path + 'MaterialTemplate.pt2'
                                            mat_file = open(mat_temp, 'r')
                                            for line2 in mat_file:
                                                if line2.startswith('[kd]') is True:
                                                    outstr = '\t\tKdColor ' + str(mat.diffuse_color[0]) + ' ' + str(mat.diffuse_color[1]) + ' ' + str(mat.diffuse_color[2]) + ' 1'
                                                    fw(outstr)
                                                elif line2.startswith('[ka]') is True:
                                                    #outstr = '\t\tkaColor 0 0 0' + str(mat.alpha)
                                                    outstr = '\t\tKaColor 0 0 0 1'
                                                    fw(outstr)                    
                                                elif line2.startswith('[ks]') is True:
                                                    outstr = '\t\tKsColor ' + str(mat.specular_color[0]) + ' ' + str(mat.specular_color[1]) + ' ' + str(mat.specular_color[2]) + ' 1'
                                                    fw(outstr)
                                                    
                                                elif line2.startswith('[tMax]') is True:
                                                    this_mat = bpy.data.materials[mat.name]
                                                    textures = this_mat.texture_slots
                                                    alphacheck = False
                                                    for tex_slot in textures:
                                                        if tex_slot != None and tex_slot.use_map_alpha is True:
                                                            alphacheck = True
                                                            outstr = '\t\ttMax 1.0'
                                                            fw(outstr)
                                                    if alphacheck == False:
                                                        outstr = '\t\ttMax 0'
                                                        fw(outstr)                                                                        
                                                      
                                                elif line2.startswith('[textureMap]') is True:
                                                    this_mat = bpy.data.materials[mat.name]
                                                    textures = this_mat.texture_slots
                                                    mapcheck = False
                                                    for tex_slot in textures:
                                                        if tex_slot != None and tex_slot.use_map_color_diffuse is True and tex_slot.use == True:
                                                            print (tex_slot.texture.image.name, tex_slot.texture.image.file_format)
                                                            
                                                            ###################################
                                                            # 
                                                            #  Keep format fix
                                                            #
                                                            image = tex_slot.texture.image
                                                            file_ext = ''
                                                            if image.file_format == 'JPEG':
                                                                file_ext = '.jpg'
                                                            elif image.file_format == 'PNG':
                                                                file_ext = '.png'                                        
                                                            
                                                            tex_file = texture_path + tex_slot.texture.image.name + file_ext
                                                            outstr = '\t\ttextureMap "' + tex_file + '"\n\t\t\t0 0'
                                                            fw(outstr)
                                                            mapcheck = True
                                                    if mapcheck == False:
                                                        outstr = '\t\ttextureMap NO_MAP'
                                                        fw(outstr)
                                                            
                                                            
                                                            
                                                elif line2.startswith('[bumpMap]') is True:
                                                    this_mat = bpy.data.materials[mat.name]
                                                    textures = this_mat.texture_slots
                                                    mapcheck = False
                                                    for tex_slot in textures:
                                                        if tex_slot != None and tex_slot.use_map_normal is True and tex_slot.use == True:
                                                            print (tex_slot.texture.image.name, tex_slot.texture.image.file_format)
                                                            ###################################
                                                            # 
                                                            #  Keep format fix
                                                            #
                                                            image = tex_slot.texture.image                                        
                                                            file_ext = ''
                                                            if image.file_format == 'JPEG':
                                                                file_ext = '.jpg'
                                                            elif image.file_format == 'PNG':
                                                                file_ext = '.png'                                        
                                                            
                                                            tex_file = texture_path + tex_slot.texture.image.name + file_ext
                                                            outstr = '\t\tbumpMap "' + tex_file + '"\n\t\t\t0 0'
                                                            fw(outstr)  
                                                            mapcheck = True
                                                    if mapcheck == False:
                                                        outstr = '\t\tbumpMap NO_MAP'
                                                        fw(outstr)                                                          
                                                            
                                                              
                                                            
                                                elif line2.startswith('[alphaMap]') is True:
                                                    this_mat = bpy.data.materials[mat.name]
                                                    textures = this_mat.texture_slots
                                                    mapcheck = False
                                                    for tex_slot in textures:
                                                        if tex_slot != None and tex_slot.use_map_alpha is True and tex_slot.use == True:
                                                            print (tex_slot.texture.image.name, tex_slot.texture.image.file_format)
                                                            ###################################
                                                            # 
                                                            #  Keep format fix
                                                            #
                                                            image = tex_slot.texture.image                                        
                                                            file_ext = ''
                                                            if image.file_format == 'JPEG':
                                                                file_ext = '.jpg'
                                                            elif image.file_format == 'PNG':
                                                                file_ext = '.png'                                        
                                                            tex_file = texture_path + tex_slot.texture.image.name + file_ext
                                                            outstr = '\t\ttransparencyMap "' + tex_file + '"\n\t\t\t0 0'
                                                            fw(outstr) 
                                                            mapcheck = True
                                                    if mapcheck == False:
                                                        outstr = '\t\ttransparencyMap NO_MAP'
                                                        fw(outstr)                                                              
                                                            
                                                            
                                                elif line2.startswith('[reflectionMap]') is True:
                                                    this_mat = bpy.data.materials[mat.name]
                                                    textures = this_mat.texture_slots
                                                    mapcheck = False
                                                    for tex_slot in textures:
                                                        if tex_slot != None and tex_slot.use_map_mirror is True and tex_slot.use == True:
                                                            print (tex_slot.texture.image.name, tex_slot.texture.image.file_format)
                                                            ###################################
                                                            # 
                                                            #  Keep format fix
                                                            #
                                                            image = tex_slot.texture.image                                        
                                                            file_ext = ''
                                                            if image.file_format == 'JPEG':
                                                                file_ext = '.jpg'
                                                            elif image.file_format == 'PNG':
                                                                file_ext = '.png'                                        
                                                            tex_file = texture_path + tex_slot.texture.image.name + file_ext
                                                            outstr = '\t\treflectionMap "' + tex_file + '"\n\t\t\t0 0'
                                                            fw(outstr)
                                                            mapcheck = True
                                                    if mapcheck == False:
                                                        outstr = '\t\treflectionMap NO_MAP'
                                                        fw(outstr)                                                            
                                
                                                                      
                                                    
                                                else:
                                                    fwnr(line2)
                                            mat_file.close()
                                
                                            
                                            outstr = '\t\t}'
                                            fw(outstr)                    
                                        
                                        
                                    else:
                                        fwnr(Dline)                                   
                                outstr = '\t}'
                                fw(outstr)
          
                                
                        elif line.startswith('[addActor]') is True:
                            # Cycle through objs
                            for this_obj in obj_list:
                                outstr = '\taddActor ' + this_obj.name
                                fw(outstr)        
                        else:
                            fwnr(line)
                    
                    templfile.close()    
                    file.close()                    
                    if fail_check == False:
                        bpy.ops.object.ok_pup('INVOKE_DEFAULT')                     
                    
                    
        return {'FINISHED'}



 
# registering and menu integration
def register():
    bpy.utils.register_class(PT2_PT_Poser_Prop_Exporter)
    bpy.utils.register_class(SetPropPath)    
    bpy.utils.register_class(SetGeometryPath)      
    bpy.utils.register_class(SetTexturePath)  
    bpy.utils.register_class(SaveProp)
    bpy.utils.register_class(Save_Thumb)
 
# unregistering and removing menus
def unregister():
    bpy.utils.unregister_class(PT2_PT_Poser_Prop_Exporter)
    bpy.utils.unregister_class(SetPropPath)        
    bpy.utils.unregister_class(SetGeometryPath)            
    bpy.utils.unregister_class(SetTexturePath)    
    bpy.utils.unregister_class(SaveProp)  
    bpy.utils.unregister_class(Save_Thumb)  
    
 
if __name__ == "__main__":
    register()
    
