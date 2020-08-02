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

#########################################################
#
#  Character Importer 7/24/2011
#
#  Data Structure:
#
#   cr2.bones[].xyz (Translation)
#   cr2.bones[].angles
#   cr2.bones[].smoothPolys
#   cr2.bones[].parent
#   cr2.bones[].name
#   cr2.bones[].endpoint
#   cr2.bones[].origin
#   cr2.bones[].orientation
#   cr2.bones[].
#       twist(xyz).child1 (Not sure of order)
#           otheractor - (same)
#           angles - ABCD
#           center - xyz
#           sphereMatsRaw
#           posBulgeLeft - float
#           posBulgeRight - float
#           negBulgeLeft - float
#           negBulgeRight - float
#
#       joint(xyz).child1 (for all children)
#       joint(xyz).child1
#       taperY(?)
#       smoothScaleY(?).child1 (for all children)
#       (xyz)OffsetA
#       scale
#       scale(xyz)
#       rotate(xyz)
#       (xyz)OffsetB
#       translate(xyz) (Some have values)
#   cr2.name
#
#   cr2.material
#   cr2.geometry
#
#########################################################
#
# Goals:
#   Load CR2
#   Load morphs
#   Create Character Tag for Control panel Extras
#   Load only Armature / details for use as base for clothing or other props
#   Store joint order as property (name) for each bone to use for translation later
#
#
#########################################################

import bpy
import time
import os
import re

# Convenience Imports:
from mathutils import *
from math import *

from bpy_extras import *
from bpy_extras.image_utils import load_image
from bpy.props import StringProperty, BoolProperty, EnumProperty

import sys
local_module_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'libs')
print(local_module_path)
sys.path.append(local_module_path)

import PT2_open as ptl
import RuntimeFolder as Runtime
import GetStringRes
import Material as matlib #remove me
import shaderTrees as st
import shaderTreeParser as stp
import createBlenderMaterialfromP4 as cbm4
from ApplyMorph import ApplyMorph
from ReadPZMD import *

print ('\n')
print ('--- Starting Poser Character Importer Version 3 ---')

bpy.cr2count = 0

###########################################
#
#  CR2 Class
#
###########################################

class CR2Class():
    def __init__(self):
        self.geompath = ''
        self.morphBinaryFile = ''
        self.name = ''
        self.geomData = geomData()
#        self.materialData = materialData()
#        self.channels = channels()
        self.materials = []
        self.bones = []

class geomData():
    def __init__(self):
        self.verts = []
        self.UVverts = []
        self.faces = []

class materialData():
    def __init__(self):
        self.color = 55
        self.alpha = 75

class boneData():
    def __init__(self):
        self.xyz = ''
        self.name = ''
        self.parent = ''
        self.endpoint = ''
        self.origin = ''
        self.orientation = ''
        self.angles = ''


class channels():
    def __init__(self):
        PBM = 'partial body morph'
        xoffseta = 0
        #xyz = []

    # Example Fuction
    def xfactor(xyz):
        value=xyz*5
        return(value)

###########################################
#
#  Import Character Class
#
###########################################


class CharacterImport(bpy.types.Operator):


    #time_start = time.time()
    bl_idname = "import.poser_cr2"
    bl_label = "Load Character"
    filename_ext = ".CR2"

    filter_glob : StringProperty(default="*.cr2;*.crz", options={'HIDDEN'})
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

    def __init__(self):
        self.PropArray = []

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
        return(scale_factor)

    def execute(self, context):

        cr2 = CR2Class()
        
        print ('\n\n')
        print ('===================================================================')
        print ('Scale Factor = ', self.getScaleFactor() )

        #########################################
        #
        # Scan for multi obj's first:
        # (May not be needed)
        #

        print ('filepath:', self.filepath)
        runtime = Runtime.Runtime(self.filepath)
        #runtime.print()


        CharName = os.path.basename(self.filepath)[:-4] ## assuming a 3 char extension
        print ('CharName:', CharName)

        file = ptl.PT2_open(self.filepath, 'rt')
        #data = open('/media/disk/armData.txt','w')
        morphcounts = []
        propcounts  = []

        for y in file:
            x=y.strip()

            ##############################
            #
            # Create bone list
            #


            if x.startswith('actor ') is True:
               #print (x)
               tempstr = x
               tempstr = tempstr.replace('actor ', '')
               skipcheck = False
               tempstr = ptl.namecheck01(tempstr)
               #print ('actor:', tempstr)
               if len(cr2.bones) > 0:
                   for bone in cr2.bones:
                       #print ('bone.name:', bone.name)
                       if bone.name == tempstr:
                           skipcheck = True
                           #print (skipcheck)

               if skipcheck == False:
                  cr2.bones.append(boneData())
                  bonecount = len(cr2.bones)
                  thisbone = cr2.bones[bonecount-1]
                  tempstr = ptl.namecheck01(tempstr)
                  thisbone.name = tempstr

            elif x.startswith('targetGeom ') is True:
               tempstr = x
               if morphcounts.__contains__(tempstr) is False:
                  morphcounts.append(tempstr)

            elif x.startswith('prop ') is True:
               tempstr = x
               if propcounts.__contains__(tempstr) is False:
                  propcounts.append(tempstr)

            ##############################
            #
            # geompath
            #

            elif x.startswith('figureResFile ') is True:
                #print (x)
                tempstr = x
                tempstr = tempstr.replace('figureResFile ', '')
                cr2.geompath = tempstr
                #print ('GeomFile:', character.geompath)

            elif x.startswith('morphBinaryFile ') is True:
                tempstr = x
                tempstr = tempstr.replace('morphBinaryFile ', '')
                cr2.morphpath = tempstr
                print ('External Morph File:', cr2.morphpath)

        file.close()
        print ('Number of Morphs:', len(morphcounts))
        print ('Number of Props:',  len(propcounts))
        #print ('=======')
        #for bone in cr2.bones:
        #    print (bone.name)
        #print ('-------------')
        print ('=======')
        for prop in propcounts:
            print (prop)
        print ('-------------')

        depth = 0 # count of open braces
        # blacklist is a list of top-level sections we are not interested in right now
        blacklist = ['baseProp', 'controlProp', 'hairGrowthGroup', 'magnetDeformerProp',
                     'setGeomHandlerOffset', 'sphereZoneProp', 'prop', 'alternateGeom']

        current_mat = 'No Mat'
        raw_mats = [] # an array of the unparsed materials
        mat_name = ''
        mats = {}
        comps = []    # a list of the material unparsed lines
        readcomps = False
        mat_depth = 0

        morphs = []
        morph = Morph()
        morphloop = -1
        current_morph = ''
        mtrx_swap = Matrix((( 1, 0, 0, 0),
                            ( 0, 1, 0, 0),
                            ( 0, 0, 1, 0),
                            ( 0, 0, 0, 1)) )
        ###############################
        #
        #  Re-open file
        #

        file = ptl.PT2_open(self.filepath, 'rt')
        figureCheck = False
        currentActor='' # in Poser an 'actor' is a vertex group or bone


# start of parser loop
        for y in file: #file is already an iterable
            x = y.strip() # do we .strip() here instead of at every level below?
            try:
                (keyword, args) = x.split(maxsplit=1)
            except ValueError: # the value error should mean there are no args on this line
                keyword = x

            if keyword in blacklist and depth == 1:
                while True: # iterate through the file until the section ends
                    x=next(file).strip()
                    if x.startswith('{'):
                        depth += 1
                    elif x.startswith('}'):
                        depth -= 1
                        if depth < 2:
                            break

            elif keyword == 'actor':
                currentActor = ptl.namecheck01(args)

                for bone in cr2.bones:
                    if bone.name == currentActor:
                        currentbone = bone
                        outstr = str(currentbone.name) + ':'
                        #data.write(outstr)
            ###############################################

            elif keyword == 'angles':
                currentbone.angles = args

            elif keyword == 'origin':
                currentbone.origin = args

            elif keyword == 'endPoint':
                currentbone.endpoint = args

            elif keyword == 'parent':
                currentbone.parent = ptl.namecheck01(args)

            elif keyword == 'orientation':
                currentbone.orientation = args

            elif x.startswith('twistX twistx'):
                tempstr = x.replace(' ', '_')
                currentbone.xyz = currentbone.xyz + tempstr + ' '
                #print ('currentbone:', currentbone.name)
                #print ('adding:', tempstr)
            elif x.startswith('twistY twisty'):
                tempstr = x
                #print ('currentbone:', currentbone.name)
                #print ('adding:', tempstr)
                tempstr = tempstr.replace(' ', '_')
                currentbone.xyz = currentbone.xyz + tempstr + ' '

            elif x.startswith('twistZ twistz'):
                tempstr = x
                #print ('currentbone:', currentbone.name)
                #print ('adding:', tempstr)
                tempstr = tempstr.replace(' ', '_')
                currentbone.xyz = currentbone.xyz + tempstr + ' '

            elif x.startswith('jointX jointx'):
                tempstr = x
                #print ('currentbone:', currentbone.name)
                #print ('adding:', tempstr)
                tempstr = tempstr.replace(' ', '_')
                currentbone.xyz = currentbone.xyz + tempstr + ' '

            elif x.startswith('jointY jointy'):
                tempstr = x
                #print ('currentbone:', currentbone.name)
                #print ('adding:', tempstr)
                tempstr = tempstr.replace(' ', '_')
                currentbone.xyz = currentbone.xyz + tempstr + ' '

            elif x.startswith('jointZ jointz'):
                tempstr = x
                #print ('currentbone:', currentbone.name)
                #print ('adding:', tempstr)
                tempstr = tempstr.replace(' ', '_')
                currentbone.xyz = currentbone.xyz + tempstr + ' '


            elif keyword == 'figure' and figureCheck == False:
                figureCheck = True
                #print ('========= Figure check True !! ===============')

            elif keyword == 'name' and figureCheck == True:
                CharName = args
                figureCheck = False

            ##########################################################
            #  Morph Targets.
            #
            elif keyword == 'targetGeom':
                morph.name = args
                morphloop = depth
                morph.group = currentActor

            elif keyword == 'k' and depth >= morphloop:
                 morph.value = float(x.split()[2])

            elif keyword == 'min' and depth >= morphloop:
                 morph.min = float(x.split()[1])

            elif keyword == 'max' and depth >= morphloop:
                 morph.max = float(x.split()[1])

            elif keyword == 'trackingScale' and depth >= morphloop:
                 morph.trackingScale = float(x.split()[1])

            elif keyword == 'd' and depth >= morphloop:
                i, dx, dy, dz = [float(s) for s in args.split()]
                morph.deltas.append( { int(i) : Vector( (dx, dy, dz) ) } )

            elif keyword == 'indexes' and depth >= morphloop:
                 morph.indexes = float(args)

            elif keyword == 'numbDeltas' and depth >= morphloop:
                 morph.numbDeltas = float(args)

            elif keyword == '{':
                depth += 1
                # print('Depth++: ', depth, morphloop, matloop)

            elif keyword == '}':
                depth -= 1
                if morphloop >= depth:
                    # morph.print()
                    morphloop = -1
                    morphs.append(morph)
                    morph = Morph()
                    # print('Depth--: ', depth,  morphloop, matloop)

            ##########################################################
            #  Build material array
            #
            elif keyword == 'material':
                #print ('Mat:', line.replace('material', ''))
                readcomps = True # Turn on component reader
                mat_name = args
                print ('Mat Name:', mat_name)

                while readcomps:
                    line = next(file).strip()

                    if line.startswith('{') is True and readcomps is True:
                        mat_depth += 1

                    elif line.startswith('}') is True and mat_depth > 0:
                        mat_depth -= 1

                    comps.append([mat_depth, line.split()]) 

                    # print(mat_depth, line)
                    if mat_depth == 0 and readcomps is True:
                        readcomps=False
                        raw_mats.append([mat_name, comps])
                        mat_name = ''
                        comps = []

# end of parser loop

        #data.close()
        file.close()
        bpy.cr2count = bpy.cr2count + 1

        ###########################################
        #
        #  Create Armature
        #
        ###########################################

        # CharName not working, reset to default:
        CharName = 'Body'

        cr2.name = CharName + str(bpy.cr2count)

        print ('\nCharacter:', cr2.name)
        print ('=======================================')

        print (bpy.context.mode)

        while bpy.context.mode != 'OBJECT':
            bpy.ops.object.editmode_toggle()

        print ("Creating Armature 3")

        #bpy.ops.object.add(type='ARMATURE')
        #arm = bpy.context.object
        #bpy.context.scene.update()

        arm = bpy.data.armatures.new(cr2.name)
        object_utils.object_data_add(context, arm, operator=None)
        bpy.context.view_layer.update()
        arm = bpy.context.active_object
        arm.location.x = 0
        arm.location.y = 0
        arm.location.z = 0
        print (arm)


        arm.name = CharName + str(bpy.cr2count)
        armdata = arm.data
        armdata.name = CharName + str(bpy.cr2count)


        if bpy.context.mode != 'EDIT_MODE':
            bpy.ops.object.editmode_toggle()

        #print ('Object Name:', arm.name)
        #print ('Armature Name:', armdata.name)
        bones = armdata.edit_bones

        for bone in cr2.bones:
            #print (bone.name)

            if bone.name.startswith('BODY'):
                pass
            elif bone.origin == '':
                pass
            elif bone.name.startswith('bodyMorphs'):
                pass
            else:
                ebone = bones.new(bone.name)
                ebone.head = [float(s) for s in bone.origin.split()]
                #array = [float(s) for s in string.split()]
                ebone.tail = [float(s) for s in bone.endpoint.split()]
                #ebone.parent = bone.parent
                ebone.head_radius = 0.02
                ebone.tail_radius = 0.02
                ebone.envelope_distance = 0.05
                pass

                #####################################
                #
                #  Add xyz joint order property here:
                #
                #####################################

                xyzprop = bone.xyz.split()
                xyz = ''
                if len(xyzprop) > 2:
                    if xyzprop[0].__contains__('X'):
                        xyzprop[0] = 'X'
                    if xyzprop[1].__contains__('X'):
                        xyzprop[1] = 'X'
                    if xyzprop[2].__contains__('X'):
                        xyzprop[2] = 'X'
                    if xyzprop[0].__contains__('Y'):
                        xyzprop[0] = 'Y'
                    if xyzprop[1].__contains__('Y'):
                        xyzprop[1] = 'Y'
                    if xyzprop[2].__contains__('Y'):
                        xyzprop[2] = 'Y'
                    if xyzprop[0].__contains__('Z'):
                        xyzprop[0] = 'Z'
                    if xyzprop[1].__contains__('Z'):
                        xyzprop[1] = 'Z'
                    if xyzprop[2].__contains__('Z'):
                        xyzprop[2] = 'Z'
                    xyz = xyzprop[0] + xyzprop[1] + xyzprop[2]

                bone = ebone
                #print (bone)
                bone["joint order"] = xyz



                #####################################
                #
                #  Set Bone Roll:
                #  Negate the Z-axis
                #
                #####################################

                try:
                    #print ('joint order:', str(xyz)[1])
                    bonerollaxis = bone["joint order"][1]
                    flip = False
                    if bonerollaxis == 'Z':
                        flip = True
                    ebone.select = True
                    #bpy.ops.armature.calculate_roll(type=bonerollaxis, axis_flip=flip)
                    bpy.ops.armature.calculate_roll(type=bonerollaxis)
                    #print ('rolling bone to:', bonerollaxis)
                    ebone.select = False
                except:
                    pass




        ###########################################
        #
        #  Set bone parents
        #
        ###########################################
        print ('\n------- parenting bones ------------')
        for bone in cr2.bones:
            try:
                #print (bone.name)
                child = bones.get(bone.name)
                parent = bones.get(bone.parent)
                child.parent = parent
            except:
                pass

        ###########################################
        #
        #  Copy Joint Order to pose bones
        #
        ###########################################

        bpy.ops.object.mode_set(mode='EDIT')
        arm = bpy.context.active_object
        bones = arm.data.edit_bones
        temp = []
        xyza = []
        for bone in bones:
            temp = [bone.name, bone["joint order"]]
            xyza.append(temp)
            temp = []

        bpy.ops.object.mode_set(mode='POSE')
        pbones = arm.pose.bones
        for value in xyza:
            if value[1] != '':
                pbones[value[0]]["joint order"] = value[1]
        for bone in pbones:
            bone["bend"] = 1
            bone["side"] = 1
            bone["twist"] = 1




        ###########################################
        #
        #  Read Geometry
        #
        ###########################################

        print ('\n\n')
        print ('==================================================================')
        print ('=')
        print ('=  Creating Mesh ')
        print ('=')
        print ('==================================================================')


        ###########################################
        #
        #  Get Geom file path
        #
        ###########################################


        char = bpy.context.active_object
        char['GeomPath'] = cr2.geompath
        print (self.filepath)
        print ('geompath:', cr2.geompath)
        fullgeompath=runtime.find_geometry_path(cr2.geompath)
        print(fullgeompath)

        ###########################################
        #
        #  Open File
        #
        ###########################################

        # Or internal Mesh?

        vertcount = 0
        facecount = 0
        facearray = []
        UVvertices = []
        verts = []
        current_group = ''


        file3 = ptl.PT2_open(fullgeompath, 'rt')
        #print ('Pre-655 check')
        #linecount = 1
        for temp in file3:
            #print ('line:', linecount, 'temp:', temp)
            #linecount += 1

            temparray2 = []

            ###########################################
            #
            #  Create Vert List
            #
            ###########################################

            if temp.startswith('v '):
                vert = temp.split()
                vert.remove('v')
                vert = [float(i) for i in vert]
                vert = tuple(vert)
                cr2.geomData.verts.append(vert)

            ###########################################
            #
            #  Create Face List w/ Mats
            #  And vert group
            #
            ###########################################


            elif temp.startswith('old_f '):
                face = temp.split()
                face.remove('f')
                tempface = []
                for vert in face:
                    vert2 = vert.split('/')
                    #print (vert2)
                    tempface.append(int(vert2[0])-1)
                if len(tempface) > 4:
                    print ('Fgon Warning!!')
                    print (tempface)
                else:
                    cr2.geomData.faces.append(tempface)


            elif temp.startswith('f ') is True:
                tempstr1 = current_mat
                tempstr2 = temp.lstrip('f ')
                tempstr3 = current_group
                facearray.append([tempstr1, tempstr2, tempstr3])
                #print (tempstr1, tempstr2, tempstr3)

            ###########################################
            #
            #  Create UV Vert list
            #
            ###########################################

            elif temp.startswith('old_vt '):
                uvvert = temp.split()
                uvvert.remove('vt')
                uvvert = [float(i) for i in uvvert]
                cr2.geomData.UVverts.append(uvvert)

            elif temp.startswith('vt ') is True:
                tempstr = temp.lstrip('vt ')
                #print (tempstr)
                temparray1 = [float(s) for s in tempstr.split()]
                temparray2.append(temparray1[0])
                temparray2.append(temparray1[1])
                UVvertices.append(temparray2)
                #print ('UVvertices:', temparray2)



            elif temp.startswith('usemtl ') is True:
                current_mat = temp.split()[1]

            elif temp.startswith('g ') is True:
                tempstr = temp.split()[1]
                current_group = tempstr
                #print ('Current group:', current_group)



        ###########################################
        #
        #  Creat Mesh
        #
        ###########################################

        print (facearray[1])

        mesh = bpy.data.meshes.new('Mesh')
        #mesh = bpy.data.meshes.new()
        ob = bpy.data.objects.new('MeshObject', mesh)
        #ob = bpy.data.objects.new('Body', mesh)
        scn = bpy.context.scene #C = bpy.context, D = bpy.data
#        scn.objects.link(ob) D.collections['Collection 1'].objects.link(D.objects['MeshObject'])
#        scn.objects.active = ob
#        scn.update()
        bpy.context.view_layer.active_layer_collection.collection.objects.link(ob)

        mesh.from_pydata(cr2.geomData.verts, [], cr2.geomData.faces)
        mesh.update(calc_edges=True)

        facecount = 0
        extrafaces = []
        extrafacecount = 1
        print ('-----------------------------------')
        textureverts = []
        faces = []
        face_mat = []
        textureverts = []

        #
        #  Vert group data file
        #
        #

        #vertfile = open('k:\\vertgroup.txt', 'w')


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

                ###########################################
                #
                #  Creat Vert Groups
                #
                ###########################################

                #  face = (Mat, vertlist, group name)
                # ob = object
                #print (ob.vertex_groups)

                #################################
                #
                #  Create VGroup if not already
                #
                #################################

                #ob = bpy.context.object
                vg = ob.vertex_groups
                #groupname = 'lEye'
                groupname = face[2]
                g_exists = False
                if len(vg) > 0:
                    for g in vg:
                        #print (g.name)
                        if g.name == groupname:
                            g_exists = True
                if g_exists == True:
                    pass
                else:
                    vg.new(name=groupname)

                #################################
                #
                # Add Vert to Group
                # vg.add(index, weight, type)
                #
                #################################
                for y in eachvert:
                    splitverts = y.split('/') # equals ['30', '1', '4']
                    #geomface.append(splitverts[0]) # adds first vert index to geom face vert list
                    #print (vg[0])

                    '''
                    for vert in splitverts:
                        if groupname == 'lHindToes' and int(vert) < 100:
                            print ('Group:', groupname, ' vert:', vert)
                        vg[groupname].add([int(vert)], 1, 'ADD')
                        outstr = groupname + ' ' + str(vert) + '\n'
                        vertfile.write(outstr)
                    '''
                    vg[groupname].add([int(splitverts[0])-1], 1, 'ADD')
                    #outstr = groupname + ' ' + str(int(splitverts[0])-1) + '\n'
                    #vertfile.write(outstr)



                #vg.add(vertnum, 1, 'ADD')


        mesh.from_pydata(verts, [], faces)
        mesh.update()

        #vertfile.close()





        ###########################################
        #
        #  Creat UV Map
        #
        ###########################################
        facecount = 0
        longfaces = []
        if( len(UVvertices) > 0 ):
        #mesh.uv_textures.new()
            uvlayer = mesh.uv_layers.new()
            if uvlayer:
                mesh.uv_layers.active = uvlayer
                facecount = 0
                longfaces = []
                #print ('Len of textureverts:', len(textureverts))
                #print(textureverts[0])
                #print(UVvertices[0])
                for face in mesh.polygons:
                    k=0
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        textureindex = int(textureverts[face.index][k])-1
                        mesh.uv_layers.active.data[loop_idx].uv = UVvertices[textureindex]
                        k+=1

        object_utils.object_data_add(context, mesh, operator=None)

        #for face in cr2.geomData.faces:
        #    print (face)
        ##########################################################################
        #
        #  Morphs
        #

        print ('\n')
        print ('==================================================')
        print ('=         Creating Shapekeys                     =')
        print ('==================================================')
        # print ('Number of Morphs:', len(morphs))

        for morph in morphs:
            ApplyMorph(ob, morph, mtrx_swap=mtrx_swap )
            # print ("Morph:", morph.name, "Size:", len(morph.deltas) )

        doMaterials = True
        if doMaterials:


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
                if mesh.materials.__contains__(raw_mat[0]):
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
                #print ('=         Assigning Faces to Materials           =')
                #print ('==================================================')

                #print ('len of face_mat:', len(face_mat))
                for face in face_mat:
                    #print (face)
                    mat_count = 0
                    for mat in mesh.materials:
                        skip = 1
                        if mat_name_map[mat.name] == face[1]:
                            mesh.polygons[face[0]].material_index = mat_count
                        mat_count = mat_count + 1

##########################################################
##########################################################


            print ('Time to create Materials:', time.time()-time_start)
            #print ('\n\n')
            #print ('Len of verts:', len(cr2.geomData.verts))
            #print ('Sample Vert:', cr2.geomData.verts[0])
            #print ('Len of faces:', len(cr2.geomData.faces))
            #print ('sample face:', cr2.geomData.faces[0])
            #try:
            #    print ('Len of UVVerts:', len(cr2.geomData.UVverts))
            #    print ('sample UVvert:', cr2.geomData.UVverts[0])
            #except:
            #    pass

        bpy.ops.object.mode_set(mode='OBJECT')
        print ('=========================================================\n\n')

        ###########################################
        #
        #  Clear Variables / prevents multiple mesh contamination
        #
        ###########################################

        cr2.geomData.faces = []
        cr2.geomData.verts = []
        cr2.geomData.UVverts = []


        ###########################################
        #
        #  Create Materials
        #
        ###########################################


        ###########################################
        #
        #  Apply mats to Geometry
        #
        ###########################################



        ##############################################
        #
        # Results:
        #
        ##############################################



        print ('Results:')
        print ('geompath:', cr2.geompath)
        #print ('gemodata.verts:', cr2.geomData.verts)
        #for bone in cr2.bones:
            #print ('--------------------------')
            #print ('bone name:', bone.name)
            #print ('bone angles:', bone.angles.split())
            #print ('bone origin:', bone.origin.split())
            #print ('bone endpoint:', bone.endpoint.split())
            #print ('bone xyz:', bone.xyz)
            #print ('bone parent:', bone.parent)
            #print ('orientation:', bone.orientation)

        #print (cr2.bones[0].channels.xoffseta)
        print ('========================================')


        ###########################################
        #
        #  Create CR2 Running Data
        #
        ###########################################
        try:
            bpy.CR2data.append([cr2.name, cr2])
        except:
            bpy.CR2data =[[cr2.name, cr2]]
        #print (cr2.bones[0].xyz)
        print ('len bones:',  len(cr2.bones))
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

    def invoke(self, context, event):
        ###########################################
        #
        #  Popup Read Character / Morphs
        #
        ###########################################
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}




# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(CharacterImport.bl_idname, text="Poser Character Importer")

def register():
    bpy.utils.register_class(CharacterImport)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(CharacterImport)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()

