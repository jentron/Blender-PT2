# -*- coding: utf-8 -*-
#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2020, Ronald Jensen
# All rights reserved.

import shaderTrees as st

def parseShaderTree(x, xs):
    tree=st.shaderTree()
    level=x[0]
    lastKeyword = ''
    lastArgs = ''

    while True:
        x=next(xs)
        keyword = x[1][0]
        args = x[1][1:]
        currentLevel = x[0]

        if keyword == '}':
            break

        elif currentLevel > level:
            if lastKeyword == 'node':
                node_type=lastArgs[0].strip('"')
                node_key =lastArgs[1].strip('"')
                # print('Create a node of type %s with key %s'%(node_type, node_key) )
                tree.nodes[node_key] = parseNode(node_type, node_key, x, xs)
            else:
                skipSection(x, xs)


        elif keyword == 'node':
            node_key =args[1].strip('"')
            node_type=args[0].strip('"')
            # print('Create a node of type %s with key %s'%(node_type, node_key) )
            # Creating the node here is mostly redundant, but in the event there is no nested node data...
            tree.nodes[node_key] = st.baseNode(node_type, node_key=node_key )

        elif keyword == 'fireflyRoot':
            tree.fireflyRoot = args[0].strip('"')

        elif keyword == 'superflyRoot':
            tree.superflyRoot = args[0].strip('"')

        else:
            print('Unparsed shaderTree keyword:', keyword, args)
            #tree[keyword] = x[1][1:]

        lastKeyword = keyword
        lastArgs = args

    return(tree)

nodeParams = ['pos', 'advancedInputsCollapsed', 'showPreview', 'inputsCollapsed']
## found in compoundNodes
nodeParams += ['gamma', 'compoundOutputsPos', 
               'compoundInputsPos', 'compoundShowPreview']
def parseNode(node_type, node_key, x, xs):
    level=x[0]
    lastKeyword=''
    lastArgs=''
    node = st.baseNode(node_type, node_key=node_key )
    
    while True:
        x=next(xs)
        keyword = x[1][0]
        args = x[1][1:]
        
        if keyword.startswith('}'):
            break
        elif keyword == 'name':
            node.name=' '.join(args).strip('"')
        elif keyword == 'selectedOutput':
            node.selectedOutput =' '.join(args).strip('"')
        elif keyword == 'nodeInput':
            node_type=' '.join(args).strip('"')
            node.nodeInputs[node_type]=st.nodeInput(node_type)
        elif keyword == 'output':
            pass # will parse on the '{'
        elif x[0] > level:
            if lastKeyword == 'nodeInput':
                node_type = ' '.join(lastArgs).strip('"')
                node.nodeInputs[node_type]=parseNodeInput(node_type, x, xs)
            elif lastKeyword == 'output':
                node_type = ' '.join(lastArgs).strip('"')
                node.nodeOutputs[node_type]=parseNodeOutput(node_type, x, xs)
            elif lastKeyword == 'shaderTree':
                node.subTrees.append( parseShaderTree(x, xs) )
            else:
                print('Skipping %s, unknown node'%lastKeyword)
                skipSection(x, xs)
        elif keyword == 'shaderTree':
            pass # will pick up on the '{'
        elif keyword in nodeParams:
            node.params[keyword] = st.nodeValue(args)
        else:
            print('Unparsed nodeParam', keyword, args)
        lastKeyword=keyword
        lastArgs=args

    return(node)

def parseNodeOutput(node_type, x, xs):
    level=x[0]
    nodeOutput = st.nodeOutput(node_type)
    while True:
        x=next(xs)
        keyword = x[1][0]
        args = x[1][1:]
        if keyword.startswith('}'):
            break
        elif keyword == 'name':
            nodeOutput.name = ' '.join(args).strip('"')
        elif keyword == 'exposedAs':
            nodeOutput.exposedAs = ' '.join(args).strip('"')
        elif x[0] > level:
            print('Error!')
        else:
            print('Unparsed nodeOutput', keyword, args)
            
    return(nodeOutput)

def skipSection(x, xs):
    while True:
        x=next(xs)
        keyword = x[1][0]
        if keyword.startswith('}'):
            break

    
def parseNodeInput(node_type, x, xs):
    level=x[0]
    nodeInput = st.nodeInput(node_type)
    while True:
        x=next(xs)
        keyword = x[1][0]
        args = x[1][1:]
        if keyword.startswith('}'):
            break
        elif keyword == 'name':
            nodeInput.name = ' '.join(args).strip('"')
        elif keyword == 'value':
            nodeInput.value = st.nodeValue(args)
        elif keyword == 'parmR':
            nodeInput.parmR = st.nodeValue(args)
        elif keyword == 'parmG':
            nodeInput.parmG = st.nodeValue(args)
        elif keyword == 'parmB':
            nodeInput.parmB = st.nodeValue(args)
        elif keyword == 'node':
            if args[0] != 'NO_NODE':
                nodeInput.node = ' '.join(args).strip('"')
        elif keyword == 'file':
            if args[0] != 'NO_MAP':
                nodeInput.file = ' '.join(args).strip('"')
        elif keyword == 'exposedAs':
            nodeInput.exposedAs = ' '.join(args).strip('"')
        elif x[0] > level:
            print('Error!')
        else:
            print('Unparsed nodeInput', keyword, args)
            
    return(nodeInput)


p4_colorNames = ['KdColor', 'KaColor', 'KsColor', 'TextureColor', 'ReflectionColor']
p4_mapNames = ['textureMap', 'bumpMap', 'reflectionMap', 'transparencyMap']
p4_parmNames = ['NsExponent', 'tMin', 'tMax', 'tExpo',
                'bumpStrength', 'ksIgnoreTexture', 'reflectThruLights',
                'reflectThruKd', 'reflectionStrength']


def parseMaterial(xs, name='Material'):
    mat=st.Material(name)

    try:
        lastKeyword = next(xs) # entering with a '{' on top
        while True:
            x=next(xs)
            keyword = x[1][0]
            args = x[1][1:]
            # print(keyword, args)
            if keyword.startswith('{') and lastKeyword.startswith('shaderTree') :
                mat.shaderTree = parseShaderTree(x, xs)
            elif keyword == 'shaderTree':
                pass # will pick up on the '{'
            elif keyword in p4_colorNames :
                mat.p4[ keyword ] = st.nodeValue([float(i) for i in args])
            elif keyword in p4_mapNames :
                mat.p4[ keyword ] = 'NO_MAP' if args[0] == 'NO_MAP' else ' '.join(args).strip('"')
            elif keyword == '0' and lastKeyword in p4_mapNames:
                pass # some texture maps end in a linebreak 0 0
            elif keyword in p4_parmNames :
                mat.p4[ keyword ] = st.nodeValue([float(i) for i in args])
            elif keyword == 'fireflyRoot':
                mat.fireflyRoot = ' '.join(args).strip('"')
            elif keyword == 'superflyRoot':
                mat.superflyRoot = ' '.join(args).strip('"')
            elif keyword.startswith('}'):
                break
            else:
                print('Top Level: ', keyword, args)
            lastKeyword = keyword

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
        [1, ['bumpMap', ':Runtime:Textures:bump.jpg']],
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
        [3, ['nodeInput', '"Transparency"']],
        [4, ['{']],
        [4, ['name', '"Transparency"']],
        [4, ['value', '0.01', '0', '1']],
        [4, ['parmR', 'NO_PARM']],
        [4, ['parmG', 'NO_PARM']],
        [4, ['parmB', 'NO_PARM']],
        [4, ['node', 'NO_NODE']],
        [4, ['file', 'NO_MAP']],
        [3, ['}']],
        [2, ['}']],
        [2, ['fireflyRoot', '"PoserSurface"']],
        [2, ['superflyRoot', '"PhysicalSurface"']],
        [1, ['}']],
        [0, ['}']],
    ]
    newmat = parseMaterial(iter(xs[1:]), 'TestMaterial')
    newmat.write()
