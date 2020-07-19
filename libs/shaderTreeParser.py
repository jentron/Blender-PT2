# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 05:15:05 2020

@author: rjensen
"""

import shaderTrees as st

def parseShaderTree(x, xs):
    tree=st.shaderTree()
    level=x[0]
    lastCommand = ''
    lastArgs = ''

    while True:
        x=next(xs)
        command = x[1][0]
        args = x[1][1:]
        currentLevel = x[0]

        if command.startswith('}'):
            break

        elif currentLevel > level:
            if lastCommand == 'node':
                node_type=lastArgs[0].strip('"')
                node_key =lastArgs[1].strip('"')
                # print('Create a node of type %s with key %s'%(node_type, node_key) )
                tree.nodes[node_key] = parseNode(node_type, node_key, x, xs)
            else:
                skipSection(x, xs)


        elif command == 'node':
            node_key =args[1].strip('"')
            node_type=args[0].strip('"')
            # print('Create a node of type %s with key %s'%(node_type, node_key) )
            # Creating the node here is mostly redundant, but in the event there is no nested node data...
            tree.nodes[node_key] = st.baseNode(node_type, node_key=node_key )

        elif command == 'fireflyRoot':
            tree.fireflyRoot = args[0].strip('"')

        elif command == 'superflyRoot':
            tree.superflyRoot = args[0].strip('"')

        else:
            print('Unparsed shaderTree command:', command, args)
            #tree[command] = x[1][1:]

        lastCommand = command
        lastArgs = args

    return(tree)

nodeParams = ['pos', 'advancedInputsCollapsed', 'showPreview', ]
## found in compoundNodes
nodeParams += ['gamma', 'compoundOutputsPos', 
               'compoundInputsPos', 'compoundShowPreview']
def parseNode(node_type, node_key, x, xs):
    level=x[0]
    lastCommand=''
    lastArgs=''
    node = st.baseNode(node_type, node_key=node_key )
    
    while True:
        x=next(xs)
        command = x[1][0]
        args = x[1][1:]
        
        if command.startswith('}'):
            break
        elif command == 'name':
            node.name=' '.join(args).strip('"')
        elif command == 'selectedOutput':
            node.selectedOutput =' '.join(args).strip('"')
        elif command == 'nodeInput':
            node_type=' '.join(args).strip('"')
            node.nodeInputs[node_type]=st.nodeInput(node_type)
        elif command == 'output':
            pass # will parse on the '{'
        elif x[0] > level:
            if lastCommand == 'nodeInput':
                node_type = ' '.join(lastArgs).strip('"')
                node.nodeInputs[node_type]=parseNodeInput(node_type, x, xs)
            elif lastCommand == 'output':
                node_type = ' '.join(lastArgs).strip('"')
                node.nodeOutputs[node_type]=parseNodeOutput(node_type, x, xs)
            elif lastCommand == 'shaderTree':
                node.subTrees.append( parseShaderTree(x, xs) )
            else:
                print('Skipping %s, unknown node'%lastCommand)
                skipSection(x, xs)
        elif command == 'shaderTree':
            pass # will pick up on the '{'
        elif command in nodeParams:
            node.params[command] = st.nodeValue(args)
        else:
            print('Unparsed nodeParam', command, args)
        lastCommand=command
        lastArgs=args

    return(node)

def parseNodeOutput(node_type, x, xs):
    level=x[0]
    nodeOutput = st.nodeOutput(node_type)
    while True:
        x=next(xs)
        command = x[1][0]
        args = x[1][1:]
        if command.startswith('}'):
            break
        elif command == 'name':
            nodeOutput.name = ' '.join(args).strip('"')
        elif command == 'exposedAs':
            nodeOutput.exposedAs = ' '.join(args).strip('"')
        elif x[0] > level:
            print('Error!')
        else:
            print('Unparsed nodeOutput', command, args)
            
    return(nodeOutput)

def skipSection(x, xs):
    while True:
        x=next(xs)
        command = x[1][0]
        if command.startswith('}'):
            break

    
def parseNodeInput(node_type, x, xs):
    level=x[0]
    nodeInput = st.nodeInput(node_type)
    while True:
        x=next(xs)
        command = x[1][0]
        args = x[1][1:]
        if command.startswith('}'):
            break
        elif command == 'name':
            nodeInput.name = ' '.join(args).strip('"')
        elif command == 'value':
            nodeInput.value = st.nodeValue(args)
        elif command == 'parmR':
            nodeInput.parmR = st.nodeValue(args)
        elif command == 'parmG':
            nodeInput.parmG = st.nodeValue(args)
        elif command == 'parmB':
            nodeInput.parmB = st.nodeValue(args)
        elif command == 'node':
            if args[0] != 'NO_NODE':
                nodeInput.node = ' '.join(args).strip('"')
        elif command == 'file':
            if args[0] != 'NO_MAP':
                nodeInput.file = ' '.join(args).strip('"')
        elif command == 'exposedAs':
            nodeInput.exposedAs = ' '.join(args).strip('"')
        elif x[0] > level:
            print('Error!')
        else:
            print('Unparsed nodeInput', command, args)
            
    return(nodeInput)


p4_colorNames = ['KdColor', 'KaColor', 'KsColor', 'TextureColor', 'ReflectionColor']
p4_mapNames = ['textureMap', 'bumpMap', 'reflectionMap', 'transparencyMap']
p4_parmNames = ['NsExponent', 'tMin', 'tMax', 'tExpo',
                'bumpStrength', 'ksIgnoreTexture', 'reflectThruLights',
                'reflectThruKd', 'reflectionStrength']


def parseMaterial(xs, name='Material'):
    mat=st.material(name)

    try:
        lastKeyword = next(xs) # entering with a '{' on top
        while True:
            x=next(xs)
            command = x[1][0]
            args = x[1][1:]
            # print(command, args)
            if command.startswith('{') and lastKeyword.startswith('shaderTree') :
                mat.shaderTree = parseShaderTree(x, xs)
            elif command == 'shaderTree':
                pass # will pick up on the '{'
            elif command in p4_colorNames :
                mat.p4[ command ] = st.nodeValue([float(i) for i in args])
            elif command in p4_mapNames :
                mat.p4[ command ] = 'NO_MAP' if args[0] == 'NO_MAP' else ' '.join(args).strip('"')
            elif command in p4_parmNames :
                mat.p4[ command ] = st.nodeValue([float(i) for i in args])
            elif command == 'fireflyRoot':
                mat.fireflyRoot = ' '.join(args).strip('"')
            elif command == 'superflyRoot':
                mat.superflyRoot = ' '.join(args).strip('"')
            elif command.startswith('}'):
                break
            else:
                print('Top Level: ', x[1])
            lastKeyword = command

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
