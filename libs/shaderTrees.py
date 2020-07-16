# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 11:03:12 2020

@author: rjensen
"""
import sys
import mathutils

NO_PARM = None
NO_NODE = None
NO_MAP  = None



class nodeInput():
    name  = None    # Node type     
    value = NO_PARM # 3 position color vector
    parmR = NO_PARM
    parmG = NO_PARM
    parmB = NO_PARM
    node  = NO_NODE
    file  = NO_MAP
    exposedAs = None    # alternate name
    
    def __init__(self, name):
        self.name = name
    
    def getName(self):
        if (self.exposedAs):
            return(self.exposedAs)
        else:
            return(self.name)
        
    def write(self, depth=0, file=sys.stdout):
        prefix='\t'*depth
        print('%snodeInput "%s"'%(prefix, self.name), file=file)
        print( '%s\t{'%(prefix,), file=file)
        print( '%s\tname "%s"'%(prefix, self.name), file=file)
        print( '%s\tvalue'%(prefix,), ('%g %g %g'%(self.value.r, self.value.g, self.value.b) if self.value else 'NO_PARM'), file=file)
        print( '%s\tparmR'%(prefix,), (self.parmR if self.parmR else 'NO_PARM'), file=file)
        print( '%s\tparmG'%(prefix,), (self.parmG if self.parmG else 'NO_PARM'), file=file)
        print( '%s\tparmB'%(prefix,), (self.parmB if self.parmB else 'NO_PARM'), file=file)
        print( '%s\tnode'%(prefix,),  (self.node  if self.node  else 'NO_NODE'), file=file)
        print( '%s\tfile'%(prefix,),  (self.file  if self.file  else 'NO_MAP'),  file=file)
        if(self.exposedAs):
            print( '%s\texposedAs "%s"'%(prefix,self.exposedAs,), file=file)
        print( '%s\t}'%(prefix,), file=file)        


if __name__ == '__main__':
    tt=nodeInput('TestNode')
    ffile=open(r'c:\tmp\bob.txt', 'wt')    
    tt.write(depth=2, file=ffile)
    tt.value=mathutils.Color([1,1,0.5])
    tt.exposedAs='something'
    tt.write(depth=2, file=ffile)
    ffile.close()
    

    
    
