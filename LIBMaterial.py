import bpy


class Material:

    def __init__(self, name='Material', overwrite=True):
        self.diffuse = (1.0, 1.0, 1.0, 1.0)
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
            
        self.useTextures=False
        self.diffuseText=False #FIXME: Map to a texture class object
        self.bumpText=False #FIXME: Map to a texture class object
        self.transparentText=False #FIXME: Map to a texture class object
        self.hasTransparency=False # set for transparentText or alpha value < 1.0

    def createBlenderMaterial(self):
        #lazy typist
        links=self.links
        nodes=self.nodes
        
        #create the basic material nodes
        node_output  = self.nodes.new(type='ShaderNodeOutputMaterial')
        node_output.location = 400,0
        node_pbsdf    = self.nodes.new(type='ShaderNodeBsdfPrincipled')
        node_pbsdf.location = 0,0
        node_pbsdf.inputs['Base Color'].default_value = self.diffuse
        link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

        # create the texture mapping nodes

        if(self.useTextures):
            node_mapping = nodes.new(type='ShaderNodeMapping')
            node_mapping.location = -1000, 0
            
            node_texcoord = nodes.new(type='ShaderNodeTexCoord')
            node_texcoord.location = -1200, 0
            link = links.new(node_texcoord.outputs['UV'], node_mapping.inputs['Vector'])
        
        # create diffuse texture
        if(self.diffuseText):
            node_texture = nodes.new(type='ShaderNodeTexImage')
            node_texture.location = -600,0
            node_texture.label = 'Diffuse Map'
            node_texture.image = self.diffuseText
            node_diffuseColor = nodes.new(type='ShaderNodeRGB')
            node_diffuseColor.location = -500,250
            node_diffuseColor.outputs['Color'].default_value=self.diffuse
            node_diffuseMix = nodes.new(type='ShaderNodeMixRGB')
            node_diffuseMix.location = -300, 25
            node_diffuseMix.blend_type='MULTIPLY' 
            node_diffuseMix.inputs['Fac'].default_value = 1
            link = links.new(node_diffuseColor.outputs['Color'], node_diffuseMix.inputs['Color1'])
            link = links.new(node_texture.outputs['Color'], node_diffuseMix.inputs['Color2'])            
            link = links.new(node_diffuseMix.outputs['Color'], node_pbsdf.inputs['Base Color'])
            link = links.new(node_mapping.outputs['Vector'], node_texture.inputs['Vector'])

        # create transparent texture
        if(self.transparentText):
            node_trtext  = nodes.new(type='ShaderNodeTexImage')
            node_trtext.location = -600,-250
            node_trtext.label = 'Transparent Map'
            node_trtext.image = self.transparentText
            link = links.new(node_mapping.outputs['Vector'], node_trtext.inputs['Vector'])
            link = links.new(node_trtext.outputs['Color'], node_pbsdf.inputs['Alpha'])

        # create bump texture
        if(self.bumpText):
            node_bump    = nodes.new(type='ShaderNodeBump')
            node_bump.location = -300,-500
            node_bumptext= nodes.new(type='ShaderNodeTexImage')
            node_bumptext.location = -600,-500
            node_bumptext.label = 'Bump Map'
            node_bumptext.image = self.bumpText
            link = links.new(node_mapping.outputs['Vector'], node_bumptext.inputs['Vector'])
            link = links.new(node_bumptext.outputs['Color'], node_bump.inputs['Height'])
            link = links.new(node_bump.outputs['Normal'], node_pbsdf.inputs['Normal'])
        
        if(self.hasTransparency):
            self.mat.blend_method = 'CLIP'
        
        # return the material
        return( self.mat )

if __name__ == "__main__":
    myMat = Material(name='3 mat2', overwrite=True)
   # myMat.diffuse = (.757, .757,.757, 1)
    myMat.diffuse = (.455,.455,.455,1)
    myMat.transparentText=False
    myMat.bumpText=True
    myMat.createBlenderMaterial()
