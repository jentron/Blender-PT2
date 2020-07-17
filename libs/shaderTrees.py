# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 11:03:12 2020

@author: rjensen
"""
import sys

NO_PARM = None
NO_NODE = None
NO_MAP  = None

class nodeValue(list):
    ''' A list with a different string converion '''

    def __str__(self):
        if len(self) == 0:
            return('NO_PARM')
        
        return(' '.join(map(str, self)))

class material():
    name=''
    blender_name=''
    p4={}
    shaderTree={}
    
    def write(self, depth=0, file=sys.stdout ):
        prefix='\t'*depth
        print('%smaterial %s'%(prefix, self.name), file=file)
        print( '%s\t{'%(prefix,), file=file)
        for key in self.p4.keys():
            print('%s\t%s %s'%(prefix, key, self.p4[key]), file=file)
        self.shaderTree.write(depth=depth+1, file=file)
        
    def __init__(self, name='Material'):
        self.name=name
    
    def __str__(self):
        ret='\n'.join([self.name, self.blender_name, str(self.p4), str(self.shaderTree)] )
        return(ret)

class shaderTree():
    nodes={}
    fireflyRoot  = None  # FIXME: These point to a valid shader node name
    superflyRoot = None
    
    def write(self, depth=0, file=sys.stdout):
        prefix='\t'*depth
        print('%sshaderTree'%(prefix, ), file=file)
        print( '%s\t{'%(prefix,), file=file)
        for key in self.nodes.keys():
            self.nodes[key].write(depth+1, file)
# Note about any material with just 1 root node:
# Both Superfly and Firefly boxes need to be checked when 
# there is only 1 root node in any material.          
        print( '%s\tfireflyRoot "%s"'%(prefix, self.fireflyRoot), file=file )
        print( '%s\tsuperflyRoot "%s"'%(prefix, self.superflyRoot), file=file )
        print( '%s\t}'%(prefix,), file=file)        

class baseNode():
    name = None
    type = 'baseNode'
    key  = 'baseNode'
    params = {'pos':nodeValue((0, 0))}
    nodeInputs = {}
    
    def __init__(self, node_type, node_key=None, name=None, pos=nodeValue((0,0)) ):
        self.type = node_type
        if(name):
            self.name=name
        else:
            self.name=self.type
        if(node_key):
            self.key = node_key
        else:
            self.key  = node_type # append a _# if more than one of a node type exists
        self.nodeInputs={}
        
    def __str__(self):
        return(self.type+':'+self.key)

    def write(self, depth=0, file=sys.stdout):
        prefix='\t'*depth
        print('%snode "%s" "%s"'%(prefix, self.type, self.key), file=file)
        print( '%s\t{'%(prefix,), file=file)
        print( '%s\tname "%s"'%(prefix, self.name), file=file)
        for param in self.params:
            print('%s\t%s'%(prefix,param), self.params[param], file=file )
        for key in self.nodeInputs.keys():
            self.nodeInputs[key].write(depth+1, file)
        
        print( '%s\t}'%(prefix,), file=file)        


class nodeInput():
    type  = None    # Node type
    key   = None    # Node Internal name
    name  = None    # Node Display name
    value = nodeValue([0,0,0])
    parmR = NO_PARM
    parmG = NO_PARM
    parmB = NO_PARM
    node  = NO_NODE
    file  = NO_MAP
    exposedAs = None    # alternate name
    
    def __init__(self, node_type, name=None, value=nodeValue([0,0,0]), exposedAs=None):
        self.type = node_type
        if(name):
            self.name=name
        else:
            self.name=self.type
        self.value=value
        self.exposedAs = exposedAs
    
    def getName(self):
        if (self.exposedAs):
            return(self.exposedAs)
        else:
            return(self.name)
        
    def write(self, depth=0, file=sys.stdout):
        prefix='\t'*depth
        print('%snodeInput "%s"'%(prefix, self.type), file=file)
        print( '%s\t{'%(prefix,), file=file)
        print( '%s\tname "%s"'%(prefix, self.name), file=file)
        print( '%s\tvalue'%(prefix), self.value, file=file)
        print( '%s\tparmR'%(prefix,), (self.parmR if self.parmR else 'NO_PARM'), file=file)
        print( '%s\tparmG'%(prefix,), (self.parmG if self.parmG else 'NO_PARM'), file=file)
        print( '%s\tparmB'%(prefix,), (self.parmB if self.parmB else 'NO_PARM'), file=file)
        print( '%s\tnode'%(prefix,),  (self.node  if self.node  else 'NO_NODE'), file=file)
        print( '%s\tfile'%(prefix,),  (self.file  if self.file  else 'NO_MAP'),  file=file)
        if(self.exposedAs):
            print( '%s\texposedAs "%s"'%(prefix,self.exposedAs,), file=file)
        print( '%s\t}'%(prefix,), file=file)        


if __name__ == '__main__':
    st=shaderTree()
    
    bn=baseNode('CyclesSurface')
    bn.name="CyclesSurface"
    bn.key ="CyclesSurface"
    bn.params['pos'] = nodeValue([570, 62])
    bn.params['advancedInputsCollapsed']= 0
    bn.nodeInputs['Surface'] = nodeInput('Surface', 
                                   value=nodeValue([1, 1, 1]))
    
    bn.nodeInputs['Volume'] = nodeInput('Volume', 
                                   value=nodeValue([1, 1, 1]))

    bn.nodeInputs['Displacement'] = nodeInput('Displacement', 
                                   name='Displacement',
                                   value=nodeValue([0.1, 0, -1]))
    st.nodes[bn.key] = bn

    bn=baseNode('TestNode')
    bn.params['pos'] = nodeValue([10,10])

    bn.nodeInputs['TestNodeInput'] = nodeInput('TestNodeInput', 
                                   value=nodeValue([0.1, 0.2, 0.3]))
    
    bn.nodeInputs['TestNodeInput2'] = nodeInput('TestNodeInput2', 
                                   value=nodeValue([0, -1, 10000]),
                                   exposedAs='something')

    bn.nodeInputs['Transparency_Max'] = nodeInput('Transparency_Max', 
                                   name='Transparency',
                                   value=nodeValue([0, -1, 10000]))
                         
    st.nodes[bn.key] = bn
    
    ffile=open(r'c:\tmp\bob.txt', 'wt')    
    st.write(depth=1, file=ffile)
    ffile.close()
    

    
    
