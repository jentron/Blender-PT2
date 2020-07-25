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
#  Poser Prop Importer Version 11
#  7/22/2011
#  www.blender3dclub.com
#
###################################################

import bpy
import time
import os
import re
import errno

import sys
local_module_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'libs')
print(local_module_path)
sys.path.append(local_module_path)

import PT2_open as ptl
import RuntimeFolder as Runtime
import GetStringRes
import shaderTrees as st
import shaderTreeParser as stp
import createBlenderMaterialfromP4 as cbm4
from ApplyMorph import ApplyMorph
from ReadPZMD import *

# Convenience Imports:
from mathutils import *
from math import *

from bpy_extras import *
from bpy_extras.image_utils import load_image
from bpy.props import StringProperty, BoolProperty, EnumProperty

print ('\n')
print ('--- Starting Poser Prop Importer Version 15 ---')

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

    filter_glob : StringProperty(default="*.pp2;*.ppz;*.hr2;*.hrz", options={'HIDDEN'})
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    
    overwrite: BoolProperty(
        name="Overwrite Materials",
        description="Overwrite current materials with the same name",
        default=False,
    )

    pnu: EnumProperty(
        name="Scale Factor",
        description="",
        items=(
            ('PNU_0', "No Scale", "Import model without scaling"),
            ('PNU_4', "Poser 4 Scale", "1 PNU = 8 feet (or 96 inches/2.43 meters)"),
            ('GEEP' , "Dr Geep Scale", "1 PNU = 8 feet 4 inches (or 100 inches/2.54 meters)"),
            ('PNU_6', "Poser 6+ Scale", "1 PNU = 8.6 feet (or 103.2 inches/2.62 meters)"),
        ),
        default='GEEP'
    )

    def getScaleFactor(self):
        bnu =  bpy.context.scene.unit_settings.scale_length
        if self.pnu == 'GEEP':
            scale_factor = 100 * 0.0254 / bnu
        elif self.pnu == 'PNU_4':
            scale_factor = 96 * 0.0254 / bnu
        elif self.pnu == 'PNU_6':
            scale_factor = 103.2 * 0.0254 / bnu
        else:
            scale_factor = 1
        print('Scale Factor:', scale_factor)
        return(scale_factor)

    CPT = []
    child_parent = []

    def execute(self, context):
        print ('\n\n')
        PropArray = []
        geompath = ''
        file_error = ''

        #########################################
        #
        # Scan for multi obj's first:
        #
        time_start = time.time()
        file = ptl.PT2_open(self.filepath, 'rt')

        runtime = Runtime.Runtime(self.filepath)
        #runtime.print()

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
                if x.strip().startswith('objFileGeom 0 0') is True:
                    subpath = x.strip().lstrip('objFileGeom 0 0') #FIXME: borked
                    subpath = subpath.strip()
                    subpath = subpath.replace(':', '\\')
                    geompath = runtime.find_geometry_path(subpath)

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

        # bpy.total_props = total_props ## what the heck is this?

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

                if x.strip().startswith('objFileGeom 0 0') is True:
                    # Read outside OBJ file here.
                    subpath = x.strip().lstrip('objFileGeom 0 0') #FIXME: borked
                    subpath = subpath.strip()
                    geompath = runtime.find_geometry_path(subpath)
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

            current_mat = 'No Mat'
            raw_mats = [] # an array of the unparsed materials
            mat_name = ''
            mats = {}
            comps = []    # a list of the material unparsed lines
            readcomps = False
            mat_depth = 0

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

            print ('Len of Prop Array:', len(PropArray))
            #print (PropArray)
            print ('==================================================')
            print ('=        Gathering data from prop array          =')
            print ('==================================================')
# start of parser loop
            iPropArray = iter(PropArray)
            try:
                while True:
                    x =next(iPropArray)
                    skip = 0
                    temparray2 = []
                    #print (x)
                    if x.startswith('prop ') is True:
                        prop_name = re.sub(r'^prop[\t ]+', '', x)
                        print("Prop name: ", prop_name)
                        rotationtemp[0] = prop_name
                        scaletemp[0] = prop_name
                        #bpy.context.object.name=(name)


                    elif x.startswith('v ') is True:
                        #print (x)
                        tempvert = re.sub(r'^v[\t ]+', '', x)
                        temp_array = [float(s) for s in tempvert.split()]
                        # array = Vector(temp_array) @ mtrx_swap
                        array = [temp_array[0], -temp_array[2], temp_array[1]]  #hardcode Y Z swap
                        verts.append(array)

                    elif x.startswith('usemtl ') is True:
                        current_mat = x.split(' ')[1]
                        current_mat = current_mat.strip()

                    elif x.startswith('g\t') is True:
                        tempstr = re.sub(r'^g[\t ]+', '', x)
                        tempstr = tempstr.replace('\t', ' ')
                        face_to_group = tempstr

                    elif x.startswith('f ') is True:
                        tempstr1 = current_mat
                        tempstr2 = re.sub(r'^f[\t ]+', '', x)
                        facearray.append([tempstr1, tempstr2])

                    elif x.startswith('vt ') is True:
                        tempstr = re.sub(r'^vt[\t ]+', '', x)
                        #print (tempstr)
                        temparray1 = [float(s) for s in tempstr.split()]
                        temparray2.append(temparray1[0])
                        temparray2.append(temparray1[1])
                        UVvertices.append(temparray2)
                ##########################################################
                #  Morph Targets.
                #
                    elif x.startswith('targetGeom ') is True:
                        morph.name = re.sub(r'^targetGeom[\t ]+', '', x)
                        morphloop = depth
                        morph.group = prop_name
                        # print ("Morph:", morph.name )
                    elif x.startswith('k ') is True and depth >= morphloop:
                        morph.value = float(x.split()[2])
                    elif x.startswith('min ') is True and depth >= morphloop:
                        morph.min = float(x.split()[1])
                    elif x.startswith('max ') is True and depth >= morphloop:
                        morph.max = float(x.split()[1])
                    elif x.startswith('d ') is True and depth >= morphloop:
                        # print('d', x)
                        tempmorph = re.sub(r'^d[\t ]+', '', x)
                        i, dx, dy, dz = [float(s) for s in tempmorph.split()]
                        morph.deltas.append( { int(i) : Vector( (dx, dy, dz) ) } )
                    elif x.startswith('indexes ') is True and depth >= morphloop:
                        morph.indexes = float(x.split()[1])
                    elif x.startswith('numbDeltas ') is True and depth >= morphloop:
                        morph.numbDeltas = float(x.split()[1])
                    elif x.startswith ('{'):
                        depth += 1
                        # print('Depth++: ', depth, morphloop, matloop)
                    elif x.startswith ('}'):
                        depth -= 1
                        if morphloop >= depth:
                            morphloop = -1
                            morphs.append(morph)
                            morph = Morph()

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
                        tempstring = re.sub(r'^origin[\t ]+', '', x)
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
                        #print ('Mat:', line.replace('material', ''))
                        mat_name = x.replace('material', '').strip()
                        readcomps = True # Turn on component reader
                        print ('Mat Name:', mat_name)

                        while readcomps:
                            line = next(iPropArray)
                            # print(mat_depth, line)

                            if line.startswith('{') is True and readcomps is True:
                                mat_depth += 1

                            elif line.startswith('}') is True and mat_depth > 0:
                                mat_depth -= 1

                            comps.append([mat_depth, line.split()]) 
                               
                            if mat_depth == 0 and readcomps is True:
                                readcomps=False
                                raw_mats.append([mat_name, comps])
                                mat_name = ''
                                comps = []

            except StopIteration:
                pass
# end of parser loop
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
                    # I have encountered files in the wild with some unmapped faces
                    # so set them to zero so the indexes match
                    else:
                        TempTextureVerts.append(0)

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

            for morph in morphs:
                morph.print()
                ApplyMorph(newobj, morph, mtrx_swap=mtrx_swap )


            ##########################################################################
            #
            #  Materials
            #

            print ('==================================================')
            print ('=         Creating Materials                     =')
            print ('==================================================')

            time_start = time.time()
            # the name that comes back from createBlenderMaterial
            # may not be the name we asked for so we'll make a mapping
            mat_name_map = {}
            
            bpy.PT2_raw_mats = raw_mats
            bpy.PT2_mats={} # save the parsed array into the bpy for future use

            for raw_mat in raw_mats: # raw_mat[0] contains material name
                bpy.PT2_mats[raw_mat[0]] = stp.parseMaterial( iter(raw_mat[1]), raw_mat[0] )
                # print(raw_mat[0], type(bpy.PT2_mats[raw_mat[0]]))
                mat1 = cbm4.createBlenderMaterialfromP4(raw_mat[0], bpy.PT2_mats[raw_mat[0]], runtime, overwrite=self.overwrite)
                mat_name_map[mat1.name] = raw_mat[0]

####################################################################################################################

                if mesh.materials.__contains__(mat1.name):
                    #print ('True')
                    pass
                else:
                    mesh.materials.append(mat1)
                    #print ('False')


                #############################################################
                #
                #  Assign faces to materials
                #

                #print ('\n')
                #print ('==================================================')
                #print ('=         Assigning Faces to Materials           =')
                #print ('==================================================')

                for face in face_mat:
                    #print (face)
                    mat_count = 0
                    for mat in mesh.materials:
                        if mat_name_map[mat.name] == face[1]:
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
                propstring = re.sub(r'^prop[\t ]+', '', x[0])
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
