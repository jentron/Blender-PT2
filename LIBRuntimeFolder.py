import re

class Runtime:
    def __init__(self, file=''):
        self.runtime=""
        self.geometry=""
        self.texture=""

        if( file != ''):
            print(file)
    
    def getRuntimePath(self, file='' ):
        if( file == ''):
            return self.runtime
        # else
        
        return (self.runtime+file)
    
    def getGeometryPath(self):
        return (self.runtime+self.geometry)

    def getTexturePath(self):
        return (self.runtime+self.texture)
    
    def tokenize(self, file):
        ''' Convert a file path string to a list '''
        tokens=[]
        
        driveletter=re.match(r'[A-Z]:', file, flags=re.IGNORECASE)
        
        if(driveletter):
            print('Drive Letter:', driveletter[0])
            tokens.append(driveletter[0].lower())
            file=file.lstrip(driveletter[0])
        else:
            print('No Drive Letter')
        
        file=re.sub( r'(\\|:)', '/', file )
        tokens+=file.split('/')
        print(file)
        
        return(tokens)
        
def runtime_test():
    rt=Runtime()
    return(rt.tokenize(r'C:\tmp\Runtime\Geometry\bob.txt'))


print(runtime_test())
        
        

        
        
        
        
        