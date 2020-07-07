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
#  Poser Prop Importer Version 11
#  7/22/2011
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
import re
import errno

from . import PT2_Library as ptl

# Convenience Imports:
from mathutils import *
from math import *

from bpy_extras import *
from bpy_extras.image_utils import load_image
from bpy.props import StringProperty, BoolProperty, EnumProperty

print ('\n')
print ('--- Starting Poser Prop Importer Version 14 ---')
systemType = sys.platform
print ('System Type:', systemType)

class Morph:
    def __init__(self):
        self.data=[]
        self.min = 0
        self.max = 1
        self.name = 'shape'

def adjustvert(objmesh, x, y, z):
    print (objmesh, x,y,z)
    mesh = bpy.data.meshes[objmesh]
    #print ('check1')
    verts = mesh.vertices
    print ('len of verts', len(verts))
    #print ('check2')
    for vert in verts:
        vert.co[0] = vert.co[0] + x
        vert.co[1] = vert.co[1] + y
        vert.co[2] = vert.co[2] + z
    return

def adjustorigin(obj, x, y, z):
    obj = bpy.data.objects[obj]
    obj.location[0] = obj.location[0] + x
    obj.location[1] = obj.location[1] + y
    obj.location[2] = obj.location[2] + z
    #obj.delta_location[0] = obj.delta_location[0] + x
    #obj.delta_location[1] = obj.delta_location[1] + y
    #obj.delta_location[2] = obj.delta_location[2] + z
    return 

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

bpy.utils.register_class(ErrorPup)
# -----------------------------------------------------------


class LoadPoserProp(bpy.types.Operator):

    PropArray = []
    time_start = time.time()
    bl_idname = "load.poser_prop"
    bl_label = "Load Prop"
    filename : bpy.props.StringProperty()
    filename_ext = ".pp2"

    filter_glob : StringProperty(default="*.pp2;*.ppz", options={'HIDDEN'})
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    CPT = []
    child_parent = []

    def execute(self, context):
        print ('\n\n')
        PropArray = []
        geompath = ''
        file_error = ''
        #global contentloc

        #########################################
        #  
        # Scan for multi obj's first:
        # 
        time_start = time.time()
        file = ptl.PT2_open(self.filepath, 'rt')
        objcounts = []
        morphcounts = []
        for x in file:
            #PropArray.append(x.strip())
            # check for geom path here
            if x.strip().startswith('prop ') is True:
               tempstr = x.strip()
               if objcounts.__contains__(tempstr) is False:
                  objcounts.append(tempstr)

            if x.strip().startswith('targetGeom ') is True:
               tempstr = x.strip()
               if morphcounts.__contains__(tempstr) is False:
                  morphcounts.append(tempstr)

        print ('Time to read file:', time.time()-time_start)
        print ('Number of Props:', len(objcounts))
        print ('Number of Morphs:', len(morphcounts))
        file.close()


        
        ##########################################################
        # Mat counter - to fix duplicate material names    

        print ('==================================================')
        print ('=          checking mat names                    =')
        print ('==================================================')    
      
        mat_counter = 0
        try:
            mat_counter = bpy.mat_counter
        except:
            pass
        bpy.mat_counter = mat_counter            
        #bpy.mat_counter = bpy.mat_counter + 1            
        mat_counter = bpy.mat_counter
        

        ##########################################################
        # get content location
        # 
        
        ##########################################################
        # Check system
        #         
        print (systemType)     
        
        if systemType.startswith('win'):           
            array = [str(s) for s in self.filepath.split('\\')]
        else:
            array = [str(s) for s in self.filepath.split('/')]                        
        skip = 0
        contentloc = []
        for y in array:
            if y == 'Runtime':
                skip = 1
            if skip == 0:
                contentloc.append(y)

        ###########################################################            


        ##########################################################
        # Read and store file
        #    
        #
        #  Create multiple prop arrays for multiple custom geometry?
        #

        total_props = []

        if len(objcounts) < 2:
            print ('==================================================')
            print ('=       len of objcounts < 2                     =')
            print ('==================================================')    
       
            file = ptl.PT2_open(self.filepath, 'rt')
            time_start = time.time()
            for x in file:
                PropArray.append(x.strip())
                # check for geom path here
                
                ##########################################################
                # Check system
                #  
                if systemType.startswith('win'):
                    if x.strip().startswith('objFileGeom 0 0') is True:
                        subpath = x.strip().lstrip('objFileGeom 0 0')
                        subpath = subpath.strip()
                        subpath = subpath.replace(':', '\\')                
                        geompath = '\\'.join(contentloc) + subpath
                    if x.strip().startswith('geomCustom') is True:
                       print ('Next obj\n')
                else:
                    if x.strip().startswith('objFileGeom 0 0') is True:
                        subpath = x.strip().lstrip('objFileGeom 0 0')
                        subpath = subpath.strip()
                        subpath = subpath.replace(':', '/')                
                        geompath = '/'.join(contentloc) + subpath
                    if x.strip().startswith('geomCustom') is True:
                       print ('Next obj\n')                      
                       
                       
            print ('Time to read file:', time.time()-time_start)                
            file.close()
    
            ##########################################################
            #  read/add separate geometry file if there is one.
            #         
            if geompath > '':
                try:
                    file = ptl.PT2_open(geompath, 'rt')
                    for x in file:
                        PropArray.append(x.strip())           
                    file.close()                        
                except:
                    print ('File not found:', geompath)
                    file_error = 'Geometry file not found'

        total_props.append(PropArray)
        
        bpy.total_props = total_props

        if len(objcounts) > 1:
            print ('==================================================')
            print ('=          objcounts > 1                         =')
            print ('==================================================')    

            ######################################
            #  Start change here:
            #  read file, add data to current prop
            #  change prop when prop listing encountered.
            #  continue to add data to current prop
            #
            #total_props = objcounts #creates array of prop names
            total_props = []
            for obj1 in objcounts:
                total_props.append([obj1])

            print ('total_props:', total_props)
            current_prop = ''

            PropArray = []
            file = ptl.PT2_open(self.filepath, 'rt')
            objcounter = 1
            proploop = False
            currentPropArray = []

            print ('==================================================')
            print ('=        Settin up Prop Array                    =')
            print ('==================================================')                  
            for x in file:
                if x.strip().startswith('prop ') is True:
                    new_prop = x.strip()
                    counter1 = 0
                    # swap out array
                    for y in total_props:
                        if y[0] == PropArray[0]:
                           total_props[counter1] = PropArray
                        counter1 = counter1 + 1
                    counter1 = 0
                    for y in total_props:  
                        if y[0] == new_prop:
                           PropArray = total_props[counter1]
                        counter1 = counter1 + 1
                else:           
                    PropArray.append(x.strip())
                
                # Added 7/9/2011
                
                ############################
                #
                #  System Check
                
                
                if systemType == 'win':
                    if x.strip().startswith('objFileGeom 0 0') is True:
                        # Read outside OBJ file here.
                        subpath = x.strip().lstrip('objFileGeom 0 0')
                        subpath = subpath.strip()
                        subpath = subpath.replace(':', '\\')                
                        geompath = '\\'.join(contentloc) + subpath
                        try:
                            file = ptl.PT2_open(geompath, 'rt')
                            for x in file:
                                PropArray.append(x.strip())           
                            file.close()                        
                        except:
                            print ('File not found:', geompath)
                            file_error = 'Geometry file not found'
                        
                else:
                    #print ('Linux >1 section') 
                    if x.strip().startswith('objFileGeom 0 0') is True:
                       subpath = x.strip().lstrip('objFileGeom 0 0')
                       subpath = subpath.strip()
                       subpath = subpath.replace(':', '/')                
                       geompath = '/'.join(contentloc) + subpath
                       print ('geompath:', geompath)
                        #if x.strip().startswith('geomCustom') is True:
                           #print (x)
                       
                       try:
                           file = ptl.PT2_open(geompath, 'rt')
                           for x in file:
                               PropArray.append(x.strip())           
                           file.close()                        
                       except:
                           print ('File not found:', geompath)
                           file_error = 'Geometry file not found'                       


            file.close()

##############################################################################
 
                                                                                        

        ##########################################################
        #  Build arrays
        # 
        time_start = time.time()
        if file_error == '':

          child_parent = []
          origin_list = []
          CPT = []
          rotationlist = []
          scalelist = []

          mtrx_swap = Matrix((( 1, 0, 0, 0),
                              ( 0, 0,-1, 0),
                              ( 0, 1, 0, 0),
                              ( 0, 0, 0, 1)) )


          for PropArray in total_props:
            #print ('255:PropArray', PropArray)
            depth = 0 # count of open braces
            vertcount = 0
            facecount = 0
            facearray = []
            UVvertices = []
            verts = []
            mats = []
            mat = []
            matloop = 0
            current_mat = 'No Mat'
            face_mat = []
            textureverts = []
            morphs = []
            morph = Morph()
            morphloop = 0
            current_morph = ''
            prop_name = ''
            ytranscheck = False
            ytransamount = 0
            xtranscheck = False
            xtransamount = 0
            ztranscheck = False
            ztransamount = 0
            yoffsetcheck = False
            xoffsetcheck = False
            zoffsetcheck = False
            yoffsetamount = 0
            zoffsetamount = 0
            xoffsetamount = 0
            xscalecheck = False
            yscalecheck = False
            zscalecheck = False
            xscaleamount = 0
            yscaleamount = 0
            zscaleamount = 0
            xrotatecheck = False
            yrotatecheck = False
            zrotatecheck = False
            xrotate = 0
            yrotate = 0
            zrotate = 0
            xoffsetb = False
            yoffsetb = False
            zoffsetb = False
            xoffsetbamount = 0
            yoffsetbamount = 0
            zoffsetbamount = 0
            obj_origin = [0,0,0]
            #scalelist = []
            scaletemp = ['',0,0,0]
            #rotationlist = []
            rotationtemp =['',0,0,0]


            bpy.mat_counter = bpy.mat_counter + 1            
            mat_counter = bpy.mat_counter

            print ('Len of Prop Array:', len(PropArray))
            #print (PropArray)
            print ('==================================================')
            print ('=        Gathering data from prop array          =')
            print ('==================================================') 
            for x in PropArray:
              
                skip = 0
                temparray2 = []
                #print (x)
                if x.startswith('prop ') is True:
                    print (x)
                    prop_name = x.lstrip('prop ')
                    rotationtemp[0] = prop_name
                    scaletemp[0] = prop_name
                    #bpy.context.object.name=(name)
                    
    
                elif x.startswith('v ') is True:
                    #print (x)
                    tempvert = x.lstrip('v ')
                    temp_array = [float(s) for s in tempvert.split()]
                    # array = Vector(temp_array) @ mtrx_swap
                    array = [temp_array[0], -temp_array[2], temp_array[1]]  #hardcode Y Z swap
                    verts.append(array)
                    
                elif x.startswith('usemtl ') is True:
                    current_mat = x.split(' ')[1]
                    #current_mat = current_mat.strip()
                    #
                    #  dupli mat name fix:
                    #
                    current_mat = str(mat_counter) + ' ' + current_mat
                    
                elif x.startswith('g\t') is True:
                    tempstr = x.lstrip('g\t')
                    tempstr = tempstr.replace('\t', ' ')
                    face_to_group = tempstr
    
                elif x.startswith('f ') is True:
                    tempstr1 = current_mat
                    tempstr2 = x.lstrip('f ')
                    facearray.append([tempstr1, tempstr2])
                    
                elif x.startswith('vt ') is True:
                    tempstr = x.lstrip('vt ')
                    #print (tempstr)
                    temparray1 = [float(s) for s in tempstr.split()]
                    temparray2.append(temparray1[0])
                    temparray2.append(temparray1[1])
                    UVvertices.append(temparray2)
            ##########################################################
            #  Morph Targets.
            #
                elif x.startswith('targetGeom ') is True:
                    morph.name = x.lstrip('targetGeom ')
                    morphloop = depth
                    # print ("Morph:", morph.name )
                elif x.startswith('k ') is True and depth >= morphloop:
                     morph.amount = float(x.split()[2])
                elif x.startswith('min ') is True and depth >= morphloop:
                     morph.min = float(x.split()[1])
                elif x.startswith('max ') is True and depth >= morphloop:
                     morph.max = float(x.split()[1])
                elif x.startswith('d ') is True and depth >= morphloop:
                    # print('d', x)
                    tempmorph = x.lstrip('d ')
                    i, dx, dy, dz = [float(s) for s in tempmorph.split()]
                    morph.data.append( { int(i) : Vector( (dx, dy, dz) ) } )
                elif x.startswith ('{'):
                    depth += 1
                    # print('Depth++: ', depth, morphloop, matloop)
                elif x.startswith ('}'):
                    depth -= 1
                    if morphloop >= depth:
                        morphloop = -1
                        morphs.append(morph)
                        morph = Morph()
                    if matloop >= depth:
                        matloop = -1
                        mats.append(mat)
                        mat = []
                    # print('Depth--: ', depth,  morphloop, matloop)

            ##########################################################
            #  Check for parent.
            #
                elif x.startswith('smartparent') is True:
                    parent_object = x.split()[1]
                    child_parent.append([prop_name, parent_object])
                    print ('parent to:', parent_object)  

            ##########################################################
            #  Origin
            #
                elif x.startswith('origin ') is True:
                     tempstring = x.strip()
                     tempstring = tempstring.lstrip('origin ')
                     tempstring = tempstring.split()
                     print ('tempstring:', tempstring)
                     obj_origin = (float(tempstring[0]), -float(tempstring[2]), float(tempstring[1])) #hardcode Y Z swap
                     # obj_origin = Vector( (float(tempstring[0]), float(tempstring[1]), float(tempstring[2])) ) @ mtrx_swap
                     print ('Origin:', obj_origin)
                     origin_list.append([prop_name, obj_origin])



            ##########################################################
            #  Rotation factor
            #   

                elif x.startswith('rotateX ') is True:
                     xrotatecheck = True
                elif x.startswith('k ') is True and xrotatecheck == True:
                     xrotatecheck = False
                     xrotate = float(x.split()[2])
                     rotationtemp[1] = xrotate
                elif x.startswith('rotateZ ') is True: #hardcode Y Z swap
                     yrotatecheck = True
                elif x.startswith('k ') is True and yrotatecheck == True:
                     yrotatecheck = False
                     yrotate = float(x.split()[2])
                     rotationtemp[2] = yrotate
                elif x.startswith('rotateY ') is True: #hardcode Y Z swap
                     zrotatecheck = True
                elif x.startswith('k ') is True and zrotatecheck == True:
                     zrotatecheck = False
                     zrotate = float(x.split()[2])
                     rotationtemp[3] = zrotate   


            ##########################################################
            #  Scale factor
            #   

                elif x.startswith('propagatingScaleX ') is True:
                     xscalecheck = True
                elif x.startswith('k ') is True and xscalecheck == True:
                     xscalecheck = False
                     xscaleamount = float(x.split()[2])
                     scaletemp[1] = xscaleamount
                elif x.startswith('propagatingScaleZ ') is True: #hardcode Y Z swap
                     yscalecheck = True
                elif x.startswith('k ') is True and yscalecheck == True:
                     yscalecheck = False
                     yscaleamount = float(x.split()[2])
                     scaletemp[2] = yscaleamount
                elif x.startswith('propagatingScaleY ') is True: #hardcode Y Z swap
                     zscalecheck = True
                elif x.startswith('k ') is True and zscalecheck == True:
                     zscalecheck = False
                     zscaleamount = float(x.split()[2])
                     scaletemp[3] = zscaleamount   
                



            ##########################################################
            #  Location Translations from parents' origin
            #   

                elif x.startswith('translateZ ') is True: #hardcode Y Z swap
                     ytranscheck = True
                elif x.startswith('k ') is True and ytranscheck == True:
                     ytranscheck = False
                     ytransamount = -float(x.split()[2])
                elif x.startswith('translateY ') is True: #hardcode Y Z swap
                     ztranscheck = True
                elif x.startswith('k ') is True and ztranscheck == True:
                     ztranscheck = False
                     ztransamount = float(x.split()[2])
                elif x.startswith('translateX ') is True:
                     xtranscheck = True
                elif x.startswith('k ') is True and xtranscheck == True:
                     xtranscheck = False
                     xtransamount = float(x.split()[2])

            ##########################################################
            #  mesh offsetB
            #   

                elif x.startswith('xOffsetB ') is True:
                     xoffsetb = True
                     #print (x)
                elif x.startswith('initValue ') is True and xoffsetb == True:
                     xoffsetb = False
                     print (x)
                     xoffsetbamount = float(x.split()[1])
                elif x.startswith('zOffsetB ') is True: #hardcode Y Z swap
                     yoffsetb = True
                     #print (x)
                elif x.startswith('initValue ') is True and yoffsetb == True:
                     yoffsetb = False
                     print (x)
                     yoffsetbamount = -float(x.split()[1])
                elif x.startswith('yOffsetB ') is True: #hardcode Y Z swap
                     zoffsetb = True
                     #print (x)
                elif x.startswith('initValue ') is True and zoffsetb == True:
                     zoffsetb = False
                     print (x)
                     zoffsetbamount = float(x.split()[1])
    
            ##########################################################
            #  Build material array
            #                 
                elif x.startswith('material ') is True:
                    matloop = depth
                    #tempstr = x.lstrip('material ')
                    tempstr = x.split(' ')[1]
                    #
                    #  double mat name fix - add prop name
                    #
                    tempstr = str(mat_counter) + ' ' + tempstr
                    #print ('mat name:', tempstr)
                    mat.append(tempstr)
                    
                elif x.startswith ('KdColor ') and depth >= matloop:
                    mat.append(x)
                    
                elif x.startswith ('KaColor ') and depth >= matloop:
                    mat.append(x)
    
                elif x.startswith ('KsColor ') and depth >= matloop:
                    mat.append(x)                
                    
                elif x.startswith ('TextureColor ') and depth >= matloop:
                    mat.append(x)                
                    
                elif x.startswith ('NsExponent ') and depth >= matloop:
                    mat.append(x)             
    
                elif x.startswith ('tMin ') and depth >= matloop:
                    mat.append(x)                  
                    
                elif x.startswith ('tMax ') and depth >= matloop:
                    mat.append(x)
    
                elif x.startswith ('tExpo ') and depth >= matloop:
                    mat.append(x)
                    
                elif x.startswith ('bumpStrength ') and depth >= matloop:
                    mat.append(x)                
                    
                elif x.startswith ('ksIgnoreTexture ') and depth >= matloop:
                    mat.append(x)                
                    
                elif x.startswith ('reflectThruLights ') and depth >= matloop:
                    mat.append(x)
                    
                elif x.startswith ('reflectThruKd ') and depth >= matloop:
                    mat.append(x)                
                    
                elif x.startswith ('textureMap ') and depth >= matloop:
                    mat.append(x)             
                    
                elif x.startswith ('bumpMap ') and depth >= matloop:
                    mat.append(x)                   
                    
                elif x.startswith ('reflectionMap ') and depth >= matloop:
                    mat.append(x)                
                    
                elif x.startswith ('transparencyMap ') and depth >= matloop:
                    mat.append(x)           
                    
                elif x.startswith ('ReflectionColor ') and depth >= matloop:
                    mat.append(x)                  
                    
                elif x.startswith ('reflectionStrength ') and depth >= matloop:
                    mat.append(x)                
                    
                ## elif x.startswith ('}') and matloop == 1:
                ##     matloop = 0
                ##     mats.append(mat)
                ##     mat = []

            ##########################################################
            #
            # Append Rotation & Scale List    
            print ('\n')
            print ('==================================================')
            print ('=          Updating Rotation / Scale List        =')
            print ('==================================================')            

            rotationlist.append(rotationtemp)
            scalelist.append(scaletemp)
            
            ##########################################################
            #
            #  Add xyz Trans to child_parent
            #
            #if len(child_parent)>0:
            #   indexc = len(child_parent) - 1
            #   entry = child_parent[indexc]
            #   entry.append(xtransamount)
            #   entry.append(ytransamount)
            #   entry.append(ztransamount)
            #   child_parent[indexc] = entry
           

                       
            print ('Time to build prop array:', time.time()-time_start)  

            ##########################################################
            ##########################################################
            # build prop
            # 
            #

            # Create new mesh
            mesh = bpy.data.meshes.new(prop_name)
            print ('New mesh name:', mesh.name)
            edges = []
            faces = []
            ##########################################################
            # Create array of faces
            #         
            print ('\n')
            print ('==================================================')
            print ('=        Creating Face array                     =')
            print ('==================================================')                
            
            # mesh.uv_layers.new()
            time_start = time.time()
           
            facecount = 0
            extrafaces = []
            extrafacecount = 1
            print ('-----------------------------------')
            textureverts = []
            for face in facearray:
                TempTextureVerts = []
                temparray = []
                facemat = face[0] #mat this face is assigned to
                vertlist = face[1] # list of all verts in face: 30/1/4 32/2/9
                eachvert = vertlist.split() # equals ['30/1/4', '32/2/9', ...]
                #print ('eachvert:', eachvert)
                geomface = []
                for y in eachvert:
                    splitverts = y.split('/') # equals ['30', '1', '4']
                    geomface.append(splitverts[0]) # adds first vert index to geom face vert list
                    if len(splitverts) > 1:
                       TempTextureVerts.append(splitverts[1])

                for vert in geomface:
                    temparray.append(int(vert)-1)
                
                ##########################################################################
                #
                #   Must deal with face and UV face together to match up texture map
                #    
                
                if len(temparray) < 5:
                    faces.append(temparray) # list of vert indices [1,2,3,4]
                    temp_mat_array = [facecount, facemat] # face index, mat name
                    face_mat.append(temp_mat_array) # add face# and mat name to list
                    textureverts.append(TempTextureVerts)# add texture verts to list
                    facecount = facecount + 1
                else:
                    y = len(temparray)
                    faces.append([temparray[0], temparray[1], temparray[2]])# adds the first face
                    if len(TempTextureVerts) > 0:
                       textureverts.append([TempTextureVerts[0], TempTextureVerts[1], TempTextureVerts[2]]) # Add matching UV face
                    temp_mat_array = [facecount, facemat] # face index, mat name
                    face_mat.append(temp_mat_array) # add face# and mat name to list
                    facecount = facecount + 1
                    
                    for q in range(2,y-1): 
                        # Creates triangles out of remaining vertex list                             
                        faces.append([temparray[0], temparray[q], temparray[q+1]])
                        if len(TempTextureVerts) > 0:
                           textureverts.append([TempTextureVerts[0], TempTextureVerts[q], TempTextureVerts[q+1]]) # Add matching UV face
                        temp_mat_array = [facecount, facemat] # face index, mat name
                        face_mat.append(temp_mat_array) # add face# and mat name to list
                        facecount = facecount + 1
   
            mesh.from_pydata(verts, edges, faces)
            mesh.update()  
            print ('Time to create face array:', time.time()-time_start)               
            print ('\n')
            print ('==================================================')
            print ('=         Creating UV Verts                      =')
            print ('==================================================')    
            
            ##########################################################################
            #
            #  Create UV Verts
            #  Skip if no UVmap on incomming mesh
            #  
#            from random import random
            time_start = time.time()    
            ## print ('Len of textureverts:', len(textureverts))
            ## print(textureverts[0])
            ## print(UVvertices[0])
            if( len(UVvertices) > 0 ):
                uvlayer = mesh.uv_layers.new()
    
                mesh.uv_layers.active = uvlayer
                facecount = 0
                longfaces = []
                for face in mesh.polygons:
                    k=0
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        textureindex = int(textureverts[face.index][k])-1
                        mesh.uv_layers.active.data[loop_idx].uv = UVvertices[textureindex]
                        k+=1

            import bpy_extras
            bpy_extras.object_utils.object_data_add(context, mesh, operator=None)

            ##########################################################################            
            ##########################################################################
            # 
            #  Adjustmenst from scale, rotation, offsets
            bpy.context.view_layer.update()    
        
            newobj = bpy.context.active_object
            print ('newobj:', newobj.name)


            # Set origin:
            print ('Origin:', obj_origin)
            newobj.location = obj_origin

            ##########################################################################
            #
            #  Morphs
            # 
            
            print ('\n')
            print ('==================================================')
            print ('=         Creating Shapekeys                     =')
            print ('==================================================')    

            if( len(morphs) > 0):
                sk_basis = newobj.shape_key_add(name="Basis")
                newobj.data.shape_keys.use_relative = False
                for morph in morphs:
                    print ("Morph:", morph.name, "Size:", len(morph.data) )
                    sk = newobj.shape_key_add(name=morph.name)
                    sk.value = morph.amount
                    sk.slider_min = morph.min
                    sk.slider_max = morph.max
                    
                    # position each vert FIXME: there must be a better way...
                    for d in morph.data:
                        for i, v in d.items():
                            sk.data[i].co = sk_basis.data[i].co + mtrx_swap @ v 
                    newobj.data.shape_keys.use_relative = True


            ##########################################################################
            #
            #  Materials
            # 
            
            print ('\n')
            print ('==================================================')
            print ('=         Creating Materials                     =')
            print ('==================================================')    

            bpy.mat_counter = bpy.mat_counter + 1            
            mat_counter = bpy.mat_counter
                                  
            time_start = time.time()
            for mat in mats:
                mat_name = mat[0]
                mesh_name = mesh.name
                
                # Create material sub
                #create_material(mat, mat_name, mesh_name, contentloc)
                for info in mat:
                    try: # check if exists first
                        mat1 = bpy.data.materials[mat_name]
                    except:
                        mat1 = bpy.data.materials.new(mat_name)
                    
                    mat1 = bpy.data.materials[mat_name]
                    ## mat1.use_transparent_shadows = True #OBSOLETE
                    mat1.use_nodes = True
                    
                    ###
                    #
                    #  Set material Color values
                    #
                    ###
            
                    #  Diffuse Color
                    if info.startswith('KdColor ') is True:
                        tempstr = info.lstrip('KdColor ')
                        array = [float(s) for s in tempstr.split()]
                        if len(array) < 3:
                            array[3] = 0
                        mat1.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = array
                        
#                    #  Specular Color
#                    if info.startswith('KsColor ') is True:
#                        tempstr = info.lstrip('KsColor ')
#                        array = [float(s) for s in tempstr.split()]
#                        if len(array) < 3:
#                            array[3] = 0
#                        mat1.node_tree.nodes['Principled BSDF'].inputs['Specular Tint'].default_value = array
#
#                    #  Reflection Strength
#                    if info.startswith('reflectionStrength ') is True:
#                        tempstr = info.replace('reflectionStrength ', '')
#                        tempstr = tempstr.strip()
#                        mat1.raytrace_mirror.reflect_factor = float(tempstr)
#                        
#                    if info.startswith('tMax ') is True:
#                        tempstr = info.replace('tMax ','')
#                        tempstr = tempstr.strip()
#                        if float(tempstr) > 0:
#                            transparency = 1 - float(tempstr)
#                            mat1.use_transparency = True
#                            mat1.alpha = transparency
                        
                    ####    
                    #
                    #  Set Texture values
                    #
                    ####

                    #############################################################
                    # 
                    #  Texture Map
                    #
                    
                    ##########################################################
                    # Check system
                    #                      
                    
                    if info.startswith('textureMap ') is True and info.endswith('NO_MAP') is False:
                        tempstr=info.lstrip('textureMap ')
                        if tempstr.endswith(' 0 0') is True:
                            tempstr = tempstr.rstrip(' 0 0')
                        tempstr = tempstr.strip('"')
                        
                        if systemType.startswith('win'):
                            tempstr = tempstr.replace(':', '\\')
                        else:
                            tempstr = re.sub(r'^[a-zA-Z]*:', '/', tempstr) #drop the drive letter
                            tempstr = re.sub(r'[:\\]', '/', tempstr)
                            
                        if systemType.startswith('win'):                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '\\'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '\\'.join(contentloc) + '\\Runtime\\textures' + tempstr
                        else:                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '/'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '/'.join(contentloc) + '/Runtime/textures' + tempstr
                                    
    
                        #######################################            
                        # Load image
                        #
                        
                        try:
                            tempfile = open(texturepath, 'r')
                            tempfile.close()
                            DIR = os.path.dirname(texturepath)
                            newimage = load_image(texturepath, DIR)
                            
                            # Create texture
                            # get texture name from image name
                            if systemType.startswith('win'):   
                                texture_name = texturepath.split('\\')
                            else:    
                                texture_name = texturepath.split('/')                                
                            texture_name = texture_name[len(texture_name)-1]
                            if len(texture_name) > 20:
                                print ('short name', texture_name[:21])
                                texture_name = texture_name[:21]
                            # create texture
                            try: # check if exists first
                                tex1 = bpy.data.textures[texture_name]
                            except:
                                tex1 = bpy.data.textures.new(texture_name, type='IMAGE')    
                            tex1 = bpy.data.textures[texture_name]            
                            
                            # Use new image
                            tex1.image = newimage
                            
                            # Add texture slot to material
                            if mat1.texture_slots.__contains__(tex1.name):
                                ts = mat1.texture_slots[tex1.name]
                                ts.use_map_color_diffuse = True                                
                            else:
                                ts = mat1.texture_slots.add()            
                                ts.texture = tex1
                                ts.texture_coords = 'UV'
                                ts.use_map_color_diffuse = True  
                        except:
                            bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
                            print ('Texture not found:', texturepath)  
                                

                    #############################################################
                    # 
                    #  Bump Map
                    #
                    
                    ##########################################################
                    # Check system
                    #                        
                    
                    if info.startswith('bumpMap ') is True and info.endswith('NO_MAP') is False:
                        tempstr=info.lstrip('bumpMap ')
                        if tempstr.endswith(' 0 0') is True:
                            tempstr = tempstr.rstrip(' 0 0')
                        tempstr = tempstr.strip('"')
                        if systemType.startswith('win'):
                            tempstr = tempstr.replace(':', '\\')
                        else:
                            tempstr = tempstr.replace(':', '/')  
                            
                        if systemType.startswith('win'):                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '\\'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '\\'.join(contentloc) + '\\Runtime\\textures' + tempstr
                        else:                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '/'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '/'.join(contentloc) + '/Runtime/textures' + tempstr
                                    

                        #######################################            
                        # Load image
                        #
                        
                        try:
                            tempfile = open(texturepath, 'r')
                            tempfile.close()
                            DIR = os.path.dirname(texturepath)
                            newimage = load_image(texturepath, DIR)
                            
                            # Create texture
                            # get texture name from image name   
                            if systemType.startswith('win'):   
                                texture_name = texturepath.split('\\')
                            else:    
                                texture_name = texturepath.split('/')
                            texture_name = texture_name[len(texture_name)-1]
                            if len(texture_name) > 20:
                                print ('short name', texture_name[:21])
                                texture_name = texture_name[:21]
                            # create texture
                            try: # check if exists first
                                tex1 = bpy.data.textures[texture_name]
                            except:
                                tex1 = bpy.data.textures.new(texture_name, type='IMAGE')    
                            tex1 = bpy.data.textures[texture_name]            
                            
                            # Use new image
                            tex1.image = newimage
                            
                            # Add texture slot to material
                            if mat1.texture_slots.__contains__(tex1.name):
                                ts = mat1.texture_slots[tex1.name]
                                ts.use_map_normal = True
                                ts.normal_factor = .025 
                            else:
                                ts = mat1.texture_slots.add()            
                                ts.texture = tex1
                                ts.texture_coords = 'UV'
                                ts.use_map_normal = True
                                ts.use_map_color_diffuse = False   
                                ts.normal_factor = .025
                                
                            ###########################################
                            # 
                            #  Adjust mat settings for Alpha texture                                    
                            #
                            
                            mat1.specular_intensity = 0                                  
                                                             
                        except:
                            print ('Texture not found:', texturepath)                                  
                                

                    #############################################################
                    # 
                    #  Alpha Map
                    #

                    ##########################################################
                    # Check system
                    #                        
                    
                    if info.startswith('transparencyMap ') is True and info.endswith('NO_MAP') is False:
                        tempstr=info.lstrip('transparencyMap ')
                        if tempstr.endswith(' 0 0') is True:
                            tempstr = tempstr.rstrip(' 0 0')
                        tempstr = tempstr.strip('"')
                        if systemType.startswith('win'):
                            tempstr = tempstr.replace(':', '\\')
                        else:
                            tempstr = tempstr.replace(':', '/')  
                            
                        if systemType.startswith('win'):                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '\\'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '\\'.join(contentloc) + '\\Runtime\\textures' + tempstr
                        else:                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '/'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '/'.join(contentloc) + '/Runtime/textures' + tempstr
                                    

                        #######################################            
                        # Load image
                        #
                        
                        try:
                            tempfile = open(texturepath, 'r')
                            tempfile.close()
                            DIR = os.path.dirname(texturepath)
                            newimage = load_image(texturepath, DIR)
                          
                            # Create texture
                            # get texture name from image name   
                            if systemType.startswith('win'):   
                                texture_name = texturepath.split('\\')
                            else:    
                                texture_name = texturepath.split('/')
                            texture_name = texture_name[len(texture_name)-1]
                            if len(texture_name) > 20:
                                print ('short name', texture_name[:21])
                                texture_name = texture_name[:21]
                            # create texture
                            try: # check if exists first
                                tex1 = bpy.data.textures[texture_name]
                            except:
                                tex1 = bpy.data.textures.new(texture_name, type='IMAGE')    
                            tex1 = bpy.data.textures[texture_name]            
                            
                            # Use new image
                            tex1.image = newimage
                            tex1.use_calculate_alpha = True
                            tex1.invert_alpha = True
                            tex1.use_alpha = False
                            
                            # Add texture slot to material
                            if mat1.texture_slots.__contains__(tex1.name):
                                ts = mat1.texture_slots[tex1.name]
                                ts.use_map_alpha = True 
                            else:
                                ts = mat1.texture_slots.add()            
                                ts.texture = tex1
                                ts.texture_coords = 'UV'
                                ts.use_map_alpha = True                                
                                ts.use_map_color_diffuse = False    

                            ###########################################
                            # 
                            #  Adjust mat settings for Alpha texture                                    
                            #
                            
                            mat1.use_transparency = True
                            mat1.alpha = 0 
                            mat1.specular_intensity = 0                         
                                                            
                        except:
                            print ('Texture not found:', texturepath)

                    #############################################################
                    # 
                    #  Reflection Map
                    #

                    ##########################################################
                    # Check system
                    #                        
                    
                    if info.startswith('reflectionMap ') is True and info.endswith('NO_MAP') is False:
                        tempstr=info.lstrip('reflectionMap ')
                        if tempstr.endswith(' 0 0') is True:
                            tempstr = tempstr.rstrip(' 0 0')
                        tempstr = tempstr.strip('"')
                        if systemType.startswith('win'):
                            tempstr = tempstr.replace(':', '\\')
                        else:
                            tempstr = tempstr.replace(':', '/')  
                            
                        if systemType.startswith('win'):                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '\\'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '\\'.join(contentloc) + '\\Runtime\\textures' + tempstr
                        else:                            
                            if tempstr.__contains__('textures') is True or tempstr.__contains__('Textures') is True:
                                texturepath = '/'.join(contentloc) + tempstr
                            else:                    
                                # Sometimes yes:  Sometimes no?:
                                texturepath = '/'.join(contentloc) + '/Runtime/textures' + tempstr
                                    

                        #######################################            
                        # Load image
                        #
                        
                        try:
                            tempfile = open(texturepath, 'r')
                            tempfile.close()
                            DIR = os.path.dirname(texturepath)
                            newimage = load_image(texturepath, DIR)
                          
                            # Create texture
                            # get texture name from image name   
                            if systemType.startswith('win'):   
                                texture_name = texturepath.split('\\')
                            else:    
                                texture_name = texturepath.split('/')
                            texture_name = texture_name[len(texture_name)-1]
                            if len(texture_name) > 20:
                                print ('short name', texture_name[:21])
                                texture_name = texture_name[:21]
                            # create texture
                            try: # check if exists first
                                tex1 = bpy.data.textures[texture_name]
                            except:
                                tex1 = bpy.data.textures.new(texture_name, type='IMAGE')    
                            tex1 = bpy.data.textures[texture_name]            
                            
                            # Use new image
                            tex1.image = newimage
                            #tex1.use_calculate_alpha = True
                            #tex1.invert_alpha = True
                            #tex1.use_alpha = False
                            
                            # Add texture slot to material
                            if mat1.texture_slots.__contains__(tex1.name):
                                ts = mat1.texture_slots[tex1.name]
                                ts.use_map_mirror = True 
                            else:
                                ts = mat1.texture_slots.add()            
                                ts.texture = tex1
                                ts.texture_coords = 'UV'
                                ts.use_map_mirror = True                                
                                ts.use_map_color_diffuse = False    

                            ###########################################
                            # 
                            #  Adjust mat settings for Mirror texture                                    
                            #
                            
                            mat1.raytrace_mirror.use = True
                            #mat1.alpha = 0 
                            #mat1.specular_intensity = 0                         
                                                            
                        except:
                            print ('Texture not found:', texturepath)                                                             
                               
####################################################################################################################
        
                if mesh.materials.__contains__(mat1.name):
                    #print ('True')
                    skip = 1
                else:
                    mesh.materials.append(mat1)
                    skip = 1
                    #print ('False')            
                    

                #############################################################
                # 
                #  Assign faces to materials
                #
                
                #print ('\n')
                #print ('==================================================')
                #print ('=         Assinging Faces to Materials           =')
                #print ('==================================================')    
                
                for face in face_mat:
                    #print (face)
                    mat_count = 0
                    for mat in mesh.materials:
                        skip = 1
                        if mat.name == face[1]:
                            mesh.polygons[face[0]].material_index = mat_count
                        mat_count = mat_count + 1
                
##########################################################
##########################################################
    
            print ('Time to create Materials:', time.time()-time_start)  
            print ('\n\n')     
            print ('len of verts:;', len(verts))
            print ('len of facearray:', len(facearray))  
            print ('  Example:', facearray[0])  
            print ('len of UVverts:', len(UVvertices))
            print ('Number of Mats:', len(mats))
            print ('Len Faces:', len(faces))
            print ('example:', faces[0])
            print ('face_mat:', len(face_mat))
            print ('example:', face_mat[0])
            print ('last face_mat:', face_mat[len(face_mat)-1])

        ############################################    
        # Adjust mesh and locations:
        #
        print ('\n')
        print ('==================================================')
        print ('=          Getting Offsetb and Trans data        =')
        print ('==================================================')    

        
        file = ptl.PT2_open(self.filepath, 'rt')        
        
        '''
        prop name, parent, prop's offsetb
        adjust locations by child and all parent translations
        adjust child mesh only by child's offsetb
        
        values' 
        name
        smartparent
        Xoffsetb
        Yoffsetb
        Zoffsetb
        '''
        proparray = []
        prop = []
        xcheck = 0
        ycheck = 0
        zcheck = 0
        transxcheck = 0
        transycheck = 0
        transzcheck = 0
        
        for x in file:
        
            if x.startswith('prop ') is True:
                prop = x.strip().replace('prop ', '')
                prop = prop.strip()
                #print ('prop:', prop)   
                skipcheck = False
                for y in proparray:
                    if y[0] == prop:
                        skipcheck = True
                if skipcheck == False:
                    proparray.append([prop])
           
            if x.startswith('\tsmartparent ') is True:
                parent = x.strip().replace('smartparent ', '')
                parent = parent.strip()
                #print ('parent:', parent)  
                for y in proparray:
                    if y[0] == prop:
                        y.append(parent)
                        
            #  Check for parent first!!! Before adding offsets:      
            #
            #  This adds offset ASSUMING it's always in XYZ order.
            #
        
            if x.startswith('\t\txOffsetB ') is True:
                xcheck = 1
                
            if x.startswith('\t\t\tinitValue ') is True and xcheck == 1:
                xoff = x.strip().replace('initValue ', '')
                xoff = xoff.strip()
                xoff = float(xoff)
                for y in proparray:
                    if y[0] == prop:
                        if len(y) == 1:
                            y.append('no parent')
                        y.append(xoff)
                xcheck = 0                
                
            if x.startswith('\t\tyOffsetB ') is True:
                ycheck = 1
                
            if x.startswith('\t\t\tinitValue ') is True and ycheck == 1:
                yoff = x.strip().replace('initValue ', '')
                yoff = yoff.strip()
                yoff = float(yoff)
                for y in proparray:
                    if y[0] == prop:
                        if len(y) == 1:
                            y.append('no parent')
                        y.append(yoff)
                ycheck = 0
                
            if x.startswith('\t\tzOffsetB ') is True:
                zcheck = 1
                
            if x.startswith('\t\t\tinitValue ') is True and zcheck == 1:
                zoff = x.strip().replace('initValue ', '')
                zoff = zoff.strip()
                zoff = float(zoff)
                for y in proparray:
                    if y[0] == prop:
                        if len(y) == 1:
                            y.append('no parent')
                        y.append(zoff)
                zcheck = 0  
                
            #########################################################################
            
            if x.startswith('\t\ttranslateX ') is True:
                transxcheck = 1
                
            if x.startswith('\t\t\t\tk ') is True and transxcheck == 1:
                xtran = x.strip().replace('k ', '')
                xtran = xtran.strip().split()
                xtran = float(xtran[1])
                for y in proparray:
                    if y[0] == prop:
                        if len(y) == 1:
                            y.append('no parent')
                        y.append(xtran)
                transxcheck = 0    
                
            if x.startswith('\t\ttranslateZ ') is True: #hardcode Y Z swap
                transycheck = 1
                
            if x.startswith('\t\t\t\tk ') is True and transycheck == 1:
                ytran = x.strip().replace('k ', '')
                ytran = ytran.strip().split()
                ytran = -float(ytran[1])
                for y in proparray:
                    if y[0] == prop:
                        if len(y) == 1:
                            y.append('no parent')
                        y.append(ytran)
                transycheck = 0   
                
            if x.startswith('\t\ttranslateY ') is True: #hardcode Y Z swap
                transzcheck = 1
                
            if x.startswith('\t\t\t\tk ') is True and transzcheck == 1:
                ztran = x.strip().replace('k ', '')
                ztran = ztran.strip().split()
                ztran = float(ztran[1])
                for y in proparray:
                    if y[0] == prop:
                        if len(y) == 1:
                            y.append('no parent')
                        y.append(ztran)
                transzcheck = 0  
            #########################################################################              
            
        file.close()
        print ('\n---------------------------------------------------------------------')
        counter = 0
        print ('\n')
        print ('==================================================')
        print ('=         Adjusting origin and mesh              =')
        print ('==================================================')    
        for x in proparray:
            counter = counter + 1
            print ('Counter:', counter)
            print (x[0], 'offsetb:', x[5], -x[7], x[6])  #hardcode Y Z swap
            print (x[0], 'origin: ', x[2], -x[4], x[3])  #hardcode Y Z swap
            adjustvert(x[0], x[5], -x[7], x[6]) #hardcode Y Z swap
            adjustorigin(x[0], x[2], -x[4], x[3]) #hardcode Y Z swap
            print ('x[1]', x[1])
            objslist = bpy.data.objects
            
            parentcheck = 0
            for d in objslist:
                print (d.name)
                if d.name == x[1]:
                    print ('Found Parent!')
                    parentcheck = 1

            if x[1] != 'no parent' and parentcheck == 1:
                offsearch = 1
                parent = x[1]
                while offsearch == 1:
                    for z in proparray:
                        if z[0] == parent:
                            adjustorigin(x[0], z[2], z[3], z[4])
                            parent = z[1]
                    if parent == 'no parent':
                        offsearch = 0
        
            print ('\n')
        print ('--------------------------------------------------------------------')

        bpy.context.view_layer.update()

        ############################################    
        # collect locations / parent / reset locations
        #
        print ('----------------------------------------')
        location_array = []

        for x in proparray:
            obj = bpy.data.objects[x[0]]
            location = obj.matrix_world[3]
            print ('prop:', obj.matrix_world[3])
            location_array.append([obj, location])
            print ('----------------------------------------')
        
        bpy.context.view_layer.update()

        #----------------------------------------------

        ############################################    
        # Parent objects After adjusting mesh & locations:
        #
        print ('\n')
        print ('==================================================')
        print ('=          Parenting Objects                     =')
        print ('==================================================')    
        if len(child_parent)>0:
            print ('child_parent list:', child_parent)
            for x in child_parent:
                print ('-----------------------------')
                print ('Child Parent:')
                print (x)
                #child = bpy.data.objects(x[0])
                child = bpy.data.objects.get(x[0])
                #bpy.data.objects.get('sink')
                parent = bpy.data.objects.get(x[1])
                child.parent = parent
            print ('\n\n')


        ############################################    
        # reset locations:
        #
        for x in location_array:
            obj = x[0]
            print ('Resetting location', x[1])
            #obj.location = x[1]
            obj.matrix_world[3] = x[1]
        #----------------------------------------------

        bpy.context.view_layer.update()

        ############################################    
        # 
        #  Scale and rotate props
        #
        print ('\n')
        print ('==================================================')
        print ('=          Scaling and Rotatin                   =')
        print ('==================================================')    

        # Rotation
        # degr = (3.14*2) / 360 better to hard-code more exact values
        degr = 0.017453292519943295
        pihalf = 1.5707963267948966
        
        print ('--------------------------------------------------------')
        print ('Rotating:')
        for x in rotationlist:
            print (x)
            obj = bpy.data.objects[x[0]]
            obj.rotation_euler = (x[1]*degr, x[2]*degr, x[3]*degr)
            bpy.context.view_layer.update()

        # Scale
        print ('--------------------------------------------------------')
        print ('Scaling:')
        for x in scalelist:
            print (x)
            obj = bpy.data.objects[x[0]]
            if x[1] > 0 and x[2] > 0 and x[3] > 0:
                obj.scale = (x[1], x[2], x[3])
            bpy.context.view_layer.update()
            

        ###########################################################
        ###########################################################
        ##
        ##  Blender X rotation:
        ##

        print ('Props len:', len(total_props))
        if len(total_props) > 1:
            for x in total_props:
                propstring = x[0].lstrip('prop ')
                propstring = propstring.strip()
                check_prop = bpy.data.objects.get(propstring)
                print (propstring)
                #print (x[0])
                #print (dir(x[0]))
                if check_prop.parent == None:
                   # check_prop.delta_rotation_euler = (pihalf, 0, 0)
                   pass
        else:
             # newobj.delta_rotation_euler = (pihalf, 0, 0)  
             pass
        ###########################################################
  

            
        total_time = time.time() - time_start
        print ("Seconds: %.2f" % (total_time))
        print("Minutes: %.2f" % (total_time/60))  
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(LoadPoserProp.bl_idname, text="Poser Prop (.pp2/.ppz)")

def register():
    bpy.utils.register_class(LoadPoserProp)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(LoadPoserProp)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
