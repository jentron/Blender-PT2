#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2020, Ronald Jensen
# All rights reserved.

## cmt=D.texts['createBlenderMaterialfromP4.py'].as_module()
## newmat=cmt.createBlenderMaterialfromP4('Preview', mat['Preview'])

import bpy
import os
from math import sqrt
from bpy_extras.image_utils import load_image

import RuntimeFolder as Runtime

def getTexture( texturePath, runtime ):
    if texturePath == 'NO_MAP':
        return(None)
    
    if texturePath.endswith(' 0 0') is True: # this should be done elsewhere, like runtime
        texturePath = texturePath.rstrip(' 0 0')
    
    file_location = runtime.find_texture_path(texturePath)
    try:
        tempfile = open(file_location, 'r')
        tempfile.close()

        # Create texture
        # get texture name from image name
        texture_name = os.path.basename(file_location)
        if len(texture_name) > 20: #why this limit?
            print ('short name', texture_name[:21])
            texture_name = texture_name[:21]
        # create texture
        try: # check if exists first
            tex1 = bpy.data.textures[texture_name]
            newimage = tex1.image
        except KeyError:
            tex1 = bpy.data.textures.new(texture_name, type='IMAGE')
            DIR = os.path.dirname(file_location)
            newimage = load_image(file_location, DIR)

            # Use new image
            tex1.image = newimage
    except FileNotFoundError:
        bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        print ('Texture Map not found: %s'%file_location)
        newimage=-1 #-1 causes the Texture setup to happen


    return(newimage)


def createBlenderMaterialfromP4(name, mat, runtime, overwrite=False):
    try:
        #expect the first 3 at a minimum
        diffuse_color   = mat.p4['KdColor'] 
        specular_color  = mat.p4['KsColor']
        ambient_color   = mat.p4['KaColor']
        texture_color   = mat.p4['TextureColor']             if    'TextureColor' in mat.p4 else (1,1,1)
        reflection_color= mat.p4['ReflectionColor']          if 'ReflectionColor' in mat.p4 else (1,1,1)
        reflect_factor =  mat.p4['reflectionStrength'][0]    if 'reflectionStrength' in mat.p4 else 0
        ns_exponent =     mat.p4['NsExponent'][0]            if 'NsExponent' in mat.p4 else 0 ### TODO: NsExponent/100 into specular value
        tMax =            mat.p4['tMax'][0]                  if 'tMax' in mat.p4 else 0 ### TODO: Minimum transparency?
        tMin =            mat.p4['tMin'][0]                  if 'tMin' in mat.p4 else 0
        tExpo =           mat.p4['tExpo'][0]                 if 'tExpo' in mat.p4 else 0     ### TODO: Change between transparencies?
        bumpStrength =    mat.p4['bumpStrength'][0]          if 'bumpStrength' in mat.p4 else 0
        ks_ignore_texture = mat.p4['ksIgnoreTexture'][0]     if 'ksIgnoreTexture' in mat.p4 else 0
        reflect_thru_lights = mat.p4['reflectThruLights'][0] if 'reflectThruLights' in mat.p4 else 0
        reflect_thru_kd = mat.p4['reflectThruKd'][0]         if 'reflectThruKd' in mat.p4 else 0
    except:
        raise ValueError('Function requires a shaderTree material')

    # load the textures
    diffuse_texture    = getTexture(mat.p4['textureMap'], runtime)       if 'textureMap' in mat.p4 else None
    bump_texture       = getTexture(mat.p4['bumpMap'], runtime)          if 'bumpMap' in mat.p4 else None
    reflection_texture = None # getTexture(mat.p4['reflectionMap'], runtime)
    transparent_texture = getTexture(mat.p4['transparencyMap'], runtime) if 'transparencyMap' in mat.p4 else None

    # Set custom values
    alpha = 1 - tMax
    if(alpha < 1):
        use_transparency = True
    else:
        use_transparency=False     # set for transparent_texture or alpha value < 1.0

    specular = sqrt(ns_exponent/100)  # or 0.5
    roughness = reflect_factor # or 0.5

    if(overwrite is True) and ( name in bpy.data.materials ):
        blenderMat = bpy.data.materials[name]

    else:
        # get the material
        blenderMat = bpy.data.materials.new(name)
        name = blenderMat.name

    # get the nodes
    blenderMat.use_nodes=True
    nodes = blenderMat.node_tree.nodes
    # clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)
    # link nodes
    links = blenderMat.node_tree.links

    #create the basic material nodes
    node_output  = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = 400,0
    node_pbsdf    = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_pbsdf.location = 0,0
    node_pbsdf.inputs['Base Color'].default_value = diffuse_color
    node_pbsdf.inputs['Alpha'].default_value = alpha
    node_pbsdf.inputs['Roughness'].default_value = roughness
    node_pbsdf.inputs['Specular'].default_value = specular
    link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

    # create the texture mapping nodes

    if( diffuse_texture or bump_texture or transparent_texture):
        node_mapping = nodes.new(type='ShaderNodeMapping')
        node_mapping.location = -1000, 0

        node_texcoord = nodes.new(type='ShaderNodeTexCoord')
        node_texcoord.location = -1200, 0
        link = links.new(node_texcoord.outputs['UV'], node_mapping.inputs['Vector'])

    # create diffuse texture node
    if(diffuse_texture):
        node_texture = nodes.new(type='ShaderNodeTexImage')
        node_texture.location = -600,0
        node_texture.label = 'Diffuse Map'
        if diffuse_texture != -1:
            node_texture.image = diffuse_texture
        node_diffuseColor = nodes.new(type='ShaderNodeRGB')
        node_diffuseColor.location = -500,250
        node_diffuseColor.outputs['Color'].default_value=diffuse_color
        node_diffuseMix = nodes.new(type='ShaderNodeMixRGB')
        node_diffuseMix.location = -300, 25
        node_diffuseMix.blend_type='MULTIPLY'
        node_diffuseMix.inputs['Fac'].default_value = 1
        link = links.new(node_diffuseColor.outputs['Color'], node_diffuseMix.inputs['Color1'])
        link = links.new(node_texture.outputs['Color'], node_diffuseMix.inputs['Color2'])
        link = links.new(node_diffuseMix.outputs['Color'], node_pbsdf.inputs['Base Color'])
        link = links.new(node_mapping.outputs['Vector'], node_texture.inputs['Vector'])

    # create transparent texture
    if(transparent_texture):
        use_transparency = True
        node_trtext  = nodes.new(type='ShaderNodeTexImage')
        node_trtext.location = -600,-250
        node_trtext.label = 'Transparent Map'
        if transparent_texture != -1:
            node_trtext.image = transparent_texture
        node_trtext.image.colorspace_settings.name = 'Non-Color'
        link = links.new(node_mapping.outputs['Vector'], node_trtext.inputs['Vector'])
        link = links.new(node_trtext.outputs['Color'], node_pbsdf.inputs['Alpha'])

    # create bump texture
    if(bump_texture):
        node_bump    = nodes.new(type='ShaderNodeBump')
        node_bump.location = -300,-500
        node_bump.inputs['Strength'].default_value = bumpStrength
        node_bumptext= nodes.new(type='ShaderNodeTexImage')
        node_bumptext.location = -600,-500
        node_bumptext.label = 'Bump Map'
        if bump_texture != -1:
            node_bumptext.image = bump_texture
        node_bumptext.image.colorspace_settings.name = 'Non-Color'
        link = links.new(node_mapping.outputs['Vector'], node_bumptext.inputs['Vector'])
        link = links.new(node_bumptext.outputs['Color'], node_bump.inputs['Height'])
        link = links.new(node_bump.outputs['Normal'], node_pbsdf.inputs['Normal'])

    if(reflection_texture):
        print('I don\'t do reflective textures')

    if(use_transparency):
        blenderMat.blend_method = 'HASHED'
        blenderMat.shadow_method = 'HASHED'

    # return the material
    return( blenderMat )

