import bpy

# get the material
mat = bpy.data.materials['1 hair']
# get the nodes
nodes = mat.node_tree.nodes

# clear all nodes to start clean
for node in nodes:
    nodes.remove(node)


node_output  = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = 400,0
node_pbsdf    = nodes.new(type='ShaderNodeBsdfPrincipled')
node_pbsdf.location = 0,0
node_texture = nodes.new(type='ShaderNodeTexImage')
node_texture.location = -400,0
node_texture.label = 'KD Map'
node_trtext  = nodes.new(type='ShaderNodeTexImage')
node_trtext.location = -400,-250
node_trtext.label = 'Transparent Map'
node_bump    = nodes.new(type='ShaderNodeBump')
node_bump.location = -300,-500
node_bumptext= nodes.new(type='ShaderNodeTexImage')
node_bumptext.location = -700,-500
node_bumptext.label = 'Bump Map'

node_mapping = nodes.new(type='ShaderNodeMapping')
node_mapping.location = -1000, 0

node_texcoord = nodes.new(type='ShaderNodeTexCoord')
node_texcoord.location = -1200, 0

# link nodes
links = mat.node_tree.links
link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])
link = links.new(node_texture.outputs['Color'], node_pbsdf.inputs['Base Color'])
link = links.new(node_trtext.outputs['Color'], node_pbsdf.inputs['Alpha'])
link = links.new(node_bumptext.outputs['Color'], node_bump.inputs['Height'])
link = links.new(node_bump.outputs['Normal'], node_pbsdf.inputs['Normal'])

link = links.new(node_texcoord.outputs['UV'], node_mapping.inputs['Vector'])

link = links.new(node_mapping.outputs['Vector'], node_texture.inputs['Vector'])
link = links.new(node_mapping.outputs['Vector'], node_trtext.inputs['Vector'])
link = links.new(node_mapping.outputs['Vector'], node_bumptext.inputs['Vector'])

mat.blend_method = 'CLIP'
