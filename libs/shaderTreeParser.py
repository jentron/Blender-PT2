# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 05:15:05 2020

@author: rjensen
"""

import shaderTrees as st

def parseShaderTree(x, xs):
    tree=st.shaderTree()
    level=x[0]
    lastCommand = x[1]
    while True:
        x=next(xs)
        if x[1][0].startswith('}'):
            break
        elif x[0] > level: 
            if lastCommand[0] == 'node':
                node_key =lastCommand[2].strip('"')
                node_type=lastCommand[1].strip('"')
                print('Create a node of type %s with key %s'%(node_type, node_key) )
                tree.nodes[node_key] = parseNode(node_type, node_key, x, xs)
        elif x[1][0] == 'node':
            node_key =x[1][2].strip('"')
            node_type=x[1][1].strip('"')
            print('Create a node of type %s with key %s'%(node_type, node_key) )
            tree.nodes[node_key] = st.baseNode(node_type, node_key=node_key )
        else:
            print('Unparsed shaderTree command:', x[1])
            #tree[x[1][0]] = x[1][1:]
        lastCommand = x[1]
        
    return(tree)

nodeParams = ['pos', 'advancedInputsCollapsed', 'showPreview', ]
def parseNode(node_type, node_key, x, xs):
    level=x[0]
    lastCommand=''
    node = st.baseNode(node_type, node_key=node_key )
    while True:
        x=next(xs)
        if x[1][0].startswith('}'):
            break
        elif x[1][0] == 'name':
            node.name=x[1][1].strip('"')
        elif x[1][0] in nodeParams:
            node.params[x[1][0]] = st.nodeValue(x[1][1:])
        elif x[0] > level:
            if lastCommand[0] == 'nodeInput':
                parseNodeInput( x, xs)
        else:
            print('Unparsed nodeParam', x[1])
        lastCommand=x

    return(node)

def parseNodeInput(x, xs):
    level=x[0]
    while True:
        x=next(xs)
        if x[1][0].startswith('}'):
            break
        elif x[0] > level:
            print('Error!')
        else:
            print('Fourth Level', x[1])


p4_colorNames = ['KdColor', 'KaColor', 'KsColor', 'TextureColor', 'ReflectionColor']
p4_mapNames = ['textureMap', 'bumpMap', 'reflectionMap', 'transparencyMap']
p4_parmNames = ['NsExponent', 'tMin', 'tMax', 'tExpo',
                'bumpStrength', 'ksIgnoreTexture', 'reflectThruLights',
                'reflectThruKd', 'reflectionStrength']


def parseMaterial(xs, name='Material'):
    mat=st.material(name)
    
    lastKeyword=''
    
    try:
        while True:
            x=next(xs)
            if x[1][0].startswith('{') and lastKeyword.startswith('shaderTree') :
                mat.shaderTree = parseShaderTree(x, xs)
            elif x[1][0] in p4_colorNames :
                mat.p4[ x[1][0] ] = st.nodeValue(x[1][1:])
            elif x[1][0] in p4_mapNames :
                mat.p4[ x[1][0] ] = x[1][1:]
            elif x[1][0] in p4_parmNames :
                mat.p4[ x[1][0] ] = st.nodeValue(x[1][1:])
            else:
                print('Top Level: ', x[1])
            lastKeyword = x[1][0]
    
    except StopIteration:
        pass
    return(mat)
    

if __name__ == '__main__':
    xs = [
        [1, ['{']],
        [1, ['KdColor', '0.8', '0.8', '0.8', '1']],
        [1, ['KaColor', '0', '0', '0', '1']],
        [1, ['NsExponent', '50']],
        [1, ['textureMap', 'NO_MAP']],
        [1, ['shaderTree']],
        [2, ['{']],
        [2, ['node', '"PhysicalSurface"', '"PhysicalSurface_1"']],
        [3, ['{']],
        [3, ['name', '"MyPhysicalSurface"']],
        [3, ['pos', '20', '43']],
        [3, ['nodeInput', '"Color"']],
        [4, ['{']],
        [4, ['name', '"Color"']],
        [4, ['value', '0.8', '0.8', '0.8']],
        [4, ['parmR', 'NO_PARM']],
        [4, ['parmG', 'NO_PARM']],
        [4, ['parmB', 'NO_PARM']],
        [4, ['node', '"ccl_DiffuseBsdf:BSDF"']],
        [4, ['file', 'NO_MAP']],
        [3, ['}']],
        [2, ['}']],
        [1, ['}']],
        [0, ['}']],
    ]
    newmat = parseMaterial(iter(xs[1:]), 'TestMaterial')
    newmat.write()
