import bpy


class Material:

    def __init__(self, name='Material', overwrite=True):
        self.diffuse_color   = (1.0, 1.0, 1.0, 1.0)
        self.specular_color  = (1.0, 1.0, 1.0, 1.0)
        self.ambient_color   = (1.0, 1.0, 1.0, 1.0)
        self.texture_color   = (1.0, 1.0, 1.0, 1.0)
        self.reflection_color= (1.0, 1.0, 1.0, 1.0)
        self.reflect_factor = 0.5
        self.ns_exponent = 50
        self.tMax = 0
        self.tMin = 0
        self.tExpo = 0.6
        self.bumpStrength = 1.0
        self.ks_ignore_texture = 0
        self.reflect_thru_lights = 0
        self.reflect_thru_kd = 0
            
        self.diffuse_texture    =False #FIXME: Map to a texture class object
        self.bump_texture       =False #FIXME: Map to a texture class object
        self.transparent_texture=False #FIXME: Map to a texture class object
        self.reflection_texture =False #FIXME: Map to a texture class object

        self.use_transparency=False # set for transparent_texture or alpha value < 1.0
        self.specular = 0.5
        self.roughness = 0.5
        self.alpha = 1.0
        if(overwrite is True) and ( name in bpy.data.materials ):
            self.name=name
            self.mat = bpy.data.materials[self.name]
                
        else:
            # get the material
            self.mat = bpy.data.materials.new(name)
            self.name = self.mat.name
            
        # get the nodes         
        self.mat.use_nodes=True
        self.nodes = self.mat.node_tree.nodes
        # clear all nodes to start clean
        for node in self.nodes:
            self.nodes.remove(node)
        # link nodes
        self.links = self.mat.node_tree.links

    def createBlenderMaterial(self):
        #lazy typist
        links=self.links
        nodes=self.nodes

        # Set custom values
        self.alpha = 1 - self.tMax
        if(self.alpha < 1):
            self.use_transparency = True


        #create the basic material nodes
        node_output  = self.nodes.new(type='ShaderNodeOutputMaterial')
        node_output.location = 400,0
        node_pbsdf    = self.nodes.new(type='ShaderNodeBsdfPrincipled')
        node_pbsdf.location = 0,0
        node_pbsdf.inputs['Base Color'].default_value = self.diffuse_color
        node_pbsdf.inputs['Alpha'].default_value = self.alpha
        link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

        # create the texture mapping nodes

        if( self.diffuse_texture or self.bump_texture or self.transparent_texture):
            node_mapping = nodes.new(type='ShaderNodeMapping')
            node_mapping.location = -1000, 0
            
            node_texcoord = nodes.new(type='ShaderNodeTexCoord')
            node_texcoord.location = -1200, 0
            link = links.new(node_texcoord.outputs['UV'], node_mapping.inputs['Vector'])
        
        # create diffuse texture
        if(self.diffuse_texture):
            node_texture = nodes.new(type='ShaderNodeTexImage')
            node_texture.location = -600,0
            node_texture.label = 'Diffuse Map'
            node_texture.image = self.diffuse_texture
            node_diffuseColor = nodes.new(type='ShaderNodeRGB')
            node_diffuseColor.location = -500,250
            node_diffuseColor.outputs['Color'].default_value=self.diffuse_color
            node_diffuseMix = nodes.new(type='ShaderNodeMixRGB')
            node_diffuseMix.location = -300, 25
            node_diffuseMix.blend_type='MULTIPLY' 
            node_diffuseMix.inputs['Fac'].default_value = 1
            link = links.new(node_diffuseColor.outputs['Color'], node_diffuseMix.inputs['Color1'])
            link = links.new(node_texture.outputs['Color'], node_diffuseMix.inputs['Color2'])            
            link = links.new(node_diffuseMix.outputs['Color'], node_pbsdf.inputs['Base Color'])
            link = links.new(node_mapping.outputs['Vector'], node_texture.inputs['Vector'])

        # create transparent texture
        if(self.transparent_texture):
            self.use_transparency = True
            node_trtext  = nodes.new(type='ShaderNodeTexImage')
            node_trtext.location = -600,-250
            node_trtext.label = 'Transparent Map'
            node_trtext.image = self.transparent_texture
            node_trtext.image.colorspace_settings.name = 'Non-Color'
            link = links.new(node_mapping.outputs['Vector'], node_trtext.inputs['Vector'])
            link = links.new(node_trtext.outputs['Color'], node_pbsdf.inputs['Alpha'])

        # create bump texture
        if(self.bump_texture):
            node_bump    = nodes.new(type='ShaderNodeBump')
            node_bump.location = -300,-500
            node_bump.inputs['Strength'].default_value = self.bumpStrength
            node_bumptext= nodes.new(type='ShaderNodeTexImage')
            node_bumptext.location = -600,-500
            node_bumptext.label = 'Bump Map'
            node_bumptext.image = self.bump_texture
            node_bumptext.image.colorspace_settings.name = 'Non-Color'
            link = links.new(node_mapping.outputs['Vector'], node_bumptext.inputs['Vector'])
            link = links.new(node_bumptext.outputs['Color'], node_bump.inputs['Height'])
            link = links.new(node_bump.outputs['Normal'], node_pbsdf.inputs['Normal'])
        
        if(self.reflection_texture):
            print('I don\'t do reflective textures')

        if(self.use_transparency):
            self.mat.blend_method = 'HASHED'
            self.mat.shadow_method = 'HASHED'
        
        # return the material
        return( self.mat )

if __name__ == "__main__":
    myMat = Material(name='3 mat2', overwrite=True)
   # myMat.diffuse_color = (.757, .757,.757, 1)
    myMat.diffuse_color = (.455,.455,.455,1)
    myMat.transparent_texture=False
    myMat.bump_texture=True
    myMat.createBlenderMaterial()
