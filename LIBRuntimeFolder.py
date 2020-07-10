import re
import os

class Runtime:
    def __init__(self, file=''):
        self.runtime   = None
        self.geometry  = None
        self.texture   = None
        self.libraries = None
        self.props     = None
        self.source    = None

        if( file != ''):
            print(file)
            self.setRuntime(file)

    def save(self):
        pass

    def load(self, file):
        pass

    def print(self):
        print('Runtime:', self.runtime)
        print('Geometries:', self.geometry)
        print('Textures:', self.texture)
        print('Libraries:', self.libraries)
        print('Props:', self.props)

    def setRuntime(self, path):
        self.setRuntimePath(path)
        self.setGeometryPath(path)
        self.setTexturePath(path)
        self.setLibraryPath(path)
        self.setPropsPath(path)
        self.setSourcePath(path)

    def setSourcePath(self, path):
        ''' This is the dir name of the string used to create the Runtime '''
        self.source = os.path.dirname(path)
        
    def setRuntimePath(self, path):
        tokens=self.tokenize(path)
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'runtime')
            self.runtime = os.sep.join(tokens[0:idx+1])
        except StopIteration:
            self.runtime = os.path.dirname(path)

    def setGeometryPath(self, path):
        if( self.runtime == None ):
            self.setRuntime(path)

        tokens=os.listdir(self.runtime)
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'geometries')
            self.geometry = tokens[idx]
        except StopIteration:
            self.geometry = '.'

    def setTexturePath(self, path):
        if( self.runtime == None ):
            self.setRuntime(path)

        tokens=os.listdir(self.runtime)
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'textures')
            self.texture = tokens[idx]
        except StopIteration:
            self.texture = '.'


    def setLibraryPath(self, path):
        if( self.runtime == None ):
            self.setRuntime(path)

        tokens=os.listdir(self.runtime)
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'libraries')
            self.library = tokens[idx]
        except StopIteration:
            self.library = '.'

    def setPropsPath(self, path):
        if( self.runtime == None ):
            self.setRuntime(path)

        tokens=os.listdir(self.runtime)
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'props')
            self.props = tokens[idx]
        except StopIteration:
            self.props = '.'

    def getRuntimePath(self, file='' ):
        '''Returns the current Runtime path as a string
        file must be a clean filename string relative to the Runtime'''
        return (os.sep.join([self.runtime, file]))

    def getGeometryPath(self, file=''):
        return (os.sep.join([self.runtime, self.geometry, file]))

    def getTexturePath(self, file=''):
        return (os.sep.join([self.runtime, self.texture, file]))

    def getSourcePath(self, file=''):
        return (os.sep.join([self.source, file]))

    def find_texture_path(self, file):
        ''' find a texture in a runtime path. File is the string from a Poser config file'''
        tokens=self.tokenize(file)
        #TODO: Validate and case-insensitive
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'textures')
            texture = os.sep.join(tokens[idx+1:])
            texture = self.getTexturePath(texture)
        except StopIteration:
            texture = os.sep.join(tokens[-1:])
            texture = self.getSourcePath(texture)

        # print('find_texture_path', texture)
        return(texture)

    def find_geometry_path(self, file):
        ''' find a geometry in a runtime path. File is the string from a Poser config file'''
        tokens=self.tokenize(file)
        #TODO: Validate and case-insensitive
        try:
            idx = next(i for i,v in enumerate(tokens) if v.lower() == 'geometries')
            geometry = os.sep.join(tokens[idx+1:])
            geometry = self.getGeometryPath(geometry)
        except StopIteration:
            geometry = os.sep.join(tokens[-1:])

        return(geometry)


    def tokenize(self, file):
        ''' Convert a file path string to a list '''
        tokens=[]

        driveletter=re.match(r'[A-Z]:', file, flags=re.IGNORECASE)

        if(driveletter):
            # print('Drive Letter:', driveletter[0])
            tokens.append(driveletter[0].lower())
            file=re.sub(r'[A-Z]:[\\|/]*', '', file,  flags=re.IGNORECASE)
        else:
            # print('No Drive Letter')
            pass

        #file=re.sub( r'(\\|:)', '/', file )
        tokens+=re.split(r'[\\|/|:]', file)
        # print(file)

        return(tokens)

## Below is test code for this module
if __name__ == '__main__':
    import sys
    rt=Runtime()
    if sys.platform == 'win32':
        strings=[r'C:\tmp\Runtime\Geometries\bob.txt',
                 r'C:\tmp\Runtime\libraries\jentron\bob.pp2',
                 r'C:\tmp\bob.txt']
    else:
        strings=[r'/tmp/Runtime/Geometries/bob.txt',
                 r'/tmp/bob.txt']

    for s in strings:
        res=rt.tokenize(s)
        print(res)
        rt.setRuntime(s)
        rt.print()
        print('Runtime', rt.getRuntimePath(''))
        print('Runtime w/file', rt.getRuntimePath('bob.txt'))

        print('Geometry', rt.getGeometryPath(''))
        print('Geometry w/file', rt.getGeometryPath('bob.txt'))

        print('Texture', rt.getTexturePath())
        print('Texture w/file', rt.getTexturePath('bob.txt'))

        print(rt.find_texture_path(':Runtime:libraries:Props:aemi1970:boundset007:metalbound007.jpg'))
        print(rt.find_geometry_path(':Bob:Runtime:geometries:Something:object.obj'))






