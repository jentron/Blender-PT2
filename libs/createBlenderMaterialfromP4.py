## cmt=D.texts['createBlenderMaterialfromP4.py'].as_module()
## newmat=cmt.createBlenderMaterialfromP4('Preview', mat['Preview'])

import bpy
import RuntimeFolder as Runtime

def getTexture( texturePath ):
    if texturePath == 'NO_MAP':
        return(None)
    return(None)

def createBlenderMaterialfromP4(name, mat, overwrite=False):
    try:
        diffuse_color   = mat.p4['KdColor']
        specular_color  = mat.p4['KsColor']
        ambient_color   = mat.p4['KaColor']
        texture_color   = mat.p4['TextureColor']
        reflection_color= mat.p4['ReflectionColor']
        reflect_factor =  mat.p4['reflectionStrength'][0]
        ns_exponent =     mat.p4['NsExponent'][0] ### TODO: NsExponent/100 into specular value
        tMax =            mat.p4['tMax'][0]       ### TODO: Minimum transparency?
        tMin =            mat.p4['tMin'][0]
        tExpo =           mat.p4['tExpo'][0]      ### TODO: Change between transparencies?
        bumpStrength =    mat.p4['bumpStrength'][0]
        ks_ignore_texture = mat.p4['ksIgnoreTexture'][0]
        reflect_thru_lights = mat.p4['reflectThruLights'][0]
        reflect_thru_kd = mat.p4['reflectThruKd'][0]
    except:
        raise ValueError('Function requires a shaderTree material')

    # load the textures
    diffuse_texture    = getTexture(mat.p4['textureMap'])
    bump_texture       = getTexture(mat.p4['bumpMap'])
    transparent_texture= None # getTexture(mat.p4['reflectionMap'])
    reflection_texture = getTexture(mat.p4['transparencyMap'])

    # Set custom values
    alpha = 1 - tMax
    if(alpha < 1):
        use_transparency = True
    else:
        use_transparency=False     # set for transparent_texture or alpha value < 1.0

    specular = ns_exponent/100     # or 0.5
    roughness = 1 - reflect_factor # or 0.5

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
        node_trtext.image = transparent_texture
        node_trtext.image.colorspace_settings.name = 'Non-Color'
        link = links.new(node_mapping.outputs['Vector'], node_trtext.inputs['Vector'])
        link = links.new(node_trtext.outputs['Color'], node_pbsdf.inputs['Alpha'])

    # create bump texture
    if(bump_texture):
        node_bump    = nodes.new(type='ShaderNodeBump')
        node_bump.location = -300,-500
        node_bump.inputs['Strength'].default_value = mat.p4['bumpStrength']
        node_bumptext= nodes.new(type='ShaderNodeTexImage')
        node_bumptext.location = -600,-500
        node_bumptext.label = 'Bump Map'
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

