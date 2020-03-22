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

import bpy
import os, glob, inspect, sys, PT2


new_drive = bpy.props.StringProperty()  
entries = []
bpy.src = []
src = bpy.src

#########################################################
#
#  Gets available drives at start up
#
######################################################### 

abc = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'
testdrives = abc.split()
drives = []
for drive in testdrives:
    try:
        path = drive + ':\\'
        x = os.listdir(path)
        drives.append(path)
    except:
        pass        
print (drives)

#########################################################
#
#  Read favorite folders list
#
######################################################### 
#def execution_path(filename):
#  return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), filename)

outstr = ''
folders = []

def read_dir():
    ############################################
    # Find PT2 Folder:

    outstr = PT2.__path__[0] + '\\'
    print ('outstr:', outstr)
    outstr = os.path.abspath(outstr)

    if sys.platform.startswith('win'):
       pass
    else:
       outstr = outstr.replace('\\', '/')
       
    #bpy.PT2path = outstr
    outstr = outstr + '/favorites.pt2'   
    bpy.PDBpath = outstr    
    file = open(outstr, 'r')
    line = []
    for x in file:
        line.append(x)
    file.close()
    #folders = []    
    props_folder = line[0].strip()
    chars_folder = line[1].strip()
    poses_folder = line[2].strip()
    folders.append(props_folder)
    folders.append(chars_folder)
    folders.append(poses_folder)
    
    
    print ('Props', props_folder)
    print ('chars', chars_folder)
    print ('poses', poses_folder)
    return (folders)

read_dir()
print (folders)


#src = []
#src.append("l:\\")

print ('\n\n\n\n')

class set_folder_props(bpy.types.Operator):
    '''Set Props Folder'''
    bl_idname = "set.props"  
    bl_label = "Set Props Folder"

    def execute(self, context):
        src = bpy.src
        print ('SRC:', src)
        print ('PT2Path', bpy.PDBpath)
        fp = bpy.PDBpath
        print ('fp:', fp)
        xstr = ''.join(src)
        folders[0] = xstr
        print ('folders[0]', folders[0])

        try:
            
            file = open(fp, 'w')
            output = folders[0] + '\n'
            file.write(output)
            output = folders[1] + '\n'
            file.write(output)
            output = folders[2] + '\n'
            file.write(output)
            file.close()                

        except:
            print ('Error')
        return {'FINISHED'} 
    
class set_folder_chars(bpy.types.Operator):
    '''Set Character Folder'''
    bl_idname = "set.chars"  
    bl_label = "Set Character Folder"

    def execute(self, context):
        src = bpy.src
        print ('SRC:', src)
        print ('PT2Path', bpy.PDBpath)
        fp = bpy.PDBpath
        print ('fp:', fp)
        xstr = ''.join(src)
        folders[1] = xstr
        print ('folders[1]', folders[1])

        try:
            
            file = open(fp, 'w')
            output = folders[0] + '\n'
            file.write(output)
            output = folders[1] + '\n'
            file.write(output)
            output = folders[2] + '\n'
            file.write(output)
            file.close()                

        except:
            print ('Error')
        return {'FINISHED'}  

class set_folder_poses(bpy.types.Operator):
    '''Set Pose Folder'''
    bl_idname = "set.poses"  
    bl_label = "Set Pose Folder"

    def execute(self, context):
        src = bpy.src
        #print ('SRC:', src)
        #print ('PDBPath', bpy.PDBpath)
        fp = bpy.PDBpath
        print ('fp:', fp)
        xstr = ''.join(src)
        folders[2] = xstr
        print ('folders[2]', folders[2])

        try:
            
            file = open(fp, 'w')
            output = folders[0] + '\n'
            file.write(output)
            output = folders[1] + '\n'
            file.write(output)
            output = folders[2] + '\n'
            file.write(output)
            file.close()                

        except:
            print ('Error')
        return {'FINISHED'} 

class open_folder_props(bpy.types.Operator):
    '''Open Props Folder'''
    bl_idname = "open.props"  
    bl_label = "Open Props Folder"

    def execute(self, context):
        print ('src in:', bpy.src)
        src = folders[0]
        src = src.split('\\')
        src.pop()
        for x in range(0,len(src)):
            src[x] = src[x] + '\\'
        print ('src out:', src)
        bpy.src = src
        return {'FINISHED'} 
    
class open_folder_chars(bpy.types.Operator):
    '''Open Character Folder'''
    bl_idname = "open.chars"  
    bl_label = "Open Character Folder"

    def execute(self, context):
        print ('src in:', bpy.src)
        src = folders[1]
        src = src.split('\\')
        src.pop()
        for x in range(0,len(src)):
            src[x] = src[x] + '\\'
        print ('src out:', src)
        bpy.src = src
        return {'FINISHED'}   
    
class open_folder_poses(bpy.types.Operator):
    '''Open Pose Folder'''
    bl_idname = "open.poses"  
    bl_label = "Open Pose Folder"

    def execute(self, context):
        print ('src in:', bpy.src)
        src = folders[2]
        src = src.split('\\')
        src.pop()
        for x in range(0,len(src)):
            src[x] = src[x] + '\\'
        print ('src out:', src)
        bpy.src = src
        return {'FINISHED'}     



class open_dir(bpy.types.Operator):
    '''Open Sub Directory'''
    bl_idname = "open.sub"  
    bl_label = "Open Sub Directory"
    location = bpy.props.StringProperty()
    newlocation = bpy.props.StringProperty()    
    #print ('location:', location)
    
    #@classmethod
    #def poll(cls, context):
        #return context.active_object != None
    #    return context.active_object != None        
        

    def execute(self, context):
        try:
            src = bpy.src
            print ('Location:', self.location) 
            print ('SRC:', src)
            #print ('Path:', path)
            newlocation = self.location + '\\'
            src.append(newlocation)
            bpy.src = src
            print ('src:', src)
        except:
            print ('Error')
        return {'FINISHED'}    
    
class open_prop(bpy.types.Operator):
    '''Open Prop'''
    bl_idname = "open.prop"  
    bl_label = "Open Poser Prop"
    filename = bpy.props.StringProperty()
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        try:
            print ("Open Prop:", self.filename)
            for x in src:
                filepath = filepath + x
            print ('filepath:', filepath)
        except:
            print ('Error loading prop')
        return {'FINISHED'}      

class up_button(bpy.types.Operator):
    '''Up One Sub Directory'''
    bl_idname = "up.button"  
    bl_label = "Up one sub directory"

    def execute(self, context):
        src = bpy.src
        try:
            src.pop()
            bpy.src = src
        except:
            print ('Error')
        return {'FINISHED'}  
    
class select_drive(bpy.types.Operator):
    '''Select Available Drive'''
    bl_idname = "select.drive"  
    bl_label = "Select available disk drives"
    new_drive = bpy.props.StringProperty()    
    
    
    def execute(self, context):
        src = bpy.src
        src.append(self.new_drive)           
        bpy.src = src
        #print ('New_drive:', self.new_drive)    
        return {'FINISHED'}          

        
class Poser_Browser(bpy.types.Panel):
    bl_label = "Poser Directory Browser"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        
        def print_dir(path):
            entries = os.listdir(path) 
            entries.sort()   
            return(entries)         
        
        path = ''
        src = bpy.src
        for x in src:
            path = path + str(x)
        
        if len(src) > 0:
            entries = print_dir(path) 
            bpy.current_path = path
            bpy.new_folder = ''

            layout = self.layout
            row = layout.row()
            
                        
            row.label(text = "Current Directory:")
            box = layout.box()
            curpath = ''
            for x in src:
                curpath = curpath + x
            box.label(text = curpath)
            
            # --------------------------------------
            # 
            #   Set favorite folders here:  IE - Props, Characters, Pose
            #
            #            
            row = layout.row()

            col = row.column()
            subrow = col.row(align = True)
            subrow.operator('set.props', text = '', icon = "FILE")
            subrow.operator('open.props', text = 'Props', icon = "FILE_FOLDER")

            col = row.column()
            subrow = col.row(align = True)
            subrow.operator('set.chars', text = '', icon = "FILE")
            subrow.operator('open.chars', text = 'Characters', icon = "FILE_FOLDER")
            
            col = row.column()
            subrow = col.row(align = True)
            subrow.operator('set.poses', text = '', icon = "FILE")
            subrow.operator('open.poses', text = 'Pose', icon = "FILE_FOLDER")                        
            
            

            
            

            # ----------------------
            # --   Folder List
            # --
            row = layout.row()     
            col = row.column()    
            
            col.label(text = 'Folders:')                    
            col.operator('up.button', text = '..', icon = "FILE_PARENT")
            for x in entries:
                if x.__contains__('.') is False:
                    #row = layout.row()
                    
                    col.operator('open.sub', text=x, icon = "FILE_FOLDER").location = x
                    #row.operator_menu_enum('open.sub', self.locaton, text=x, icon = "FILE_FOLDER").location = x
                    
                else:
                    skip = 1
                    
            # ----------------------
            # --   Prop List
            # --
            
            #row = layout.row()
            col = row.column()
            col.label(text = 'Props:')    
            for x in entries:
                if x.endswith('.pp2') is True:
                    #row = layout.row()
                    fp = ''
                    for y in src:
                        fp = fp + y
                    fp = fp + x   
                    col.operator('load.poser_prop', text = x, icon = "MESH_ICOSPHERE").filepath = fp
                    #row.alignment = 'LEFT'

            # ----------------------
            # --   Charcter List
            # --
            
            col.label(text = 'Characters:')    
            for x in entries:
                if x.endswith('.cr2') is True:
                    row = layout.row()
                    fp = ''
                    for y in src:
                        fp = fp + y
                    fp = fp + x   
                    col.operator('import2.poser_cr2', text = x, icon = "ARMATURE_DATA").filepath = fp
                    #col.label(text = x, icon = "ARMATURE_DATA")
                    #row.alignment = 'LEFT'   
                    
            # ----------------------
            # --   Mat File List
            # --
            
            # context = object selected
            
            col.label(text = 'Materials:')    
            for x in entries:
                if x.endswith('.pz2') is True:
                    row = layout.row()
                    fp = ''
                    for y in src:
                        fp = fp + y
                    fp = fp + x
                    #print ('Context:', context.active_object.type)
                    obj = context.active_object
                    if obj.type == 'MESH':
                        col.operator('read.mat2', text = x, icon = "MATERIAL").filepath = fp
                    else:
                        col.label(text = x, icon = "MATERIAL")
                    #row.alignment = 'LEFT'                                      
                
        else:
            layout = self.layout
            row = layout.row()   
            counter = 0         
            for drive in drives:
                counter = counter + 1
                row.operator('select.drive', text = drive, icon = "DISK_DRIVE").new_drive = drive
                if (counter/3) == int(counter/3):
                    row = layout.row()
                    
            if counter == 2:
                row.label(text='')
            elif counter == 1:
                row.label(text='')
                row.label(text='')
                                
                


def menu_func_import(self, context):
    skip = 1

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(Poser_Browser)
    bpy.utils.register_class(open_dir)
    bpy.utils.register_class(up_button)   
    bpy.utils.register_class(open_prop)       
    bpy.utils.register_class(select_drive)  
    bpy.utils.register_class(set_folder_props)      
    bpy.utils.register_class(set_folder_chars)          
    bpy.utils.register_class(set_folder_poses)   
    bpy.utils.register_class(open_folder_props)           
    bpy.utils.register_class(open_folder_chars)           
    bpy.utils.register_class(open_folder_poses)               
    #bpy.utils.register_class(SelectFolder2)           

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(Poser_Browser)   
    bpy.utils.unregister_class(open_dir)     
    bpy.utils.unregister_class(up_button)    
    bpy.utils.unregister_class(open_prop)       
    bpy.utils.unregister_class(select_drive)       
    bpy.utils.unregister_class(set_folder_props)
    bpy.utils.unregister_class(set_folder_chars)    
    bpy.utils.unregister_class(set_folder_poses)        
    bpy.utils.unregister_class(open_folder_props)
    bpy.utils.unregister_class(open_folder_chars)
    bpy.utils.unregister_class(open_folder_poses)        
    #bpy.utils.unregister_class(SelectFolder2)      

if __name__ == "__main__":
    register()        
        


