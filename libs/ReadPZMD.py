# -*- coding: utf-8 -*-
#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2020, Ronald Jensen
# All rights reserved.
"""
pmd (Poser Morph D...)
"""

import struct
import os

import logging
logger = logging.getLogger(__name__)

class Morph:
    def __init__(self):
        self.deltas=[]
        self.min = 0
        self.max = 1
        self.trackingScale = 0.02
        self.value = 0
        self.name = 'shape'
        self.group = ''
        self.indexes = -1    # this is the number of vertexes in the morph! ITS BACKWARDS
        self.numbDeltas = -1 # this is the number of vertexes in target!
        self.fileOffset = -1

    def print(self):
        print('Morph:', self.name,
               'Target:', self.group,
               'Indexes: ', self.indexes,
               'numbDeltas:', self.numbDeltas )

    def log(self, level=logging.INFO):
        logger.log(level, 'Morph: %s\tTarget: %s\tIndexes: %s\tnumbDeltas: %s'%
               (self.name, self.group, self.indexes, self.numbDeltas ) )

def readPZMD(filename):
    filesize=os.stat(filename).st_size
    file=open(filename, 'rb')
    
    ## 4bytes PZMD
    foo=file.read(4)
    if (foo==b'PZMD'):
        logger.info("%s is a Poser Morph File!"%filename)
    else:
        logger.critical("%s is not a PZMD Morph File!" % filename)
        raise ValueError("%s is not a PZMD Morph File!" % filename)
    
    ## 4bytes Number of morphs, or version?
    foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
    logger.debug('Version: %d' % foo)
    if(foo > 1):
        logger.warning('Unexpected version %d' % foo )
    
    ## 4bytes pad? or should header size by 64 bits?
    foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
    if(foo==0):
        logger.debug('Always 0?\t%d' % foo)
    else:
        logger.critical('Pad is not zero! Contact Developer!')
    
    ## 4bytes Size of morph header
    header_length=int.from_bytes(file.read(4), byteorder='big', signed=False)
    logger.debug('Header Length?\t%d'%header_length)
    
    ## 4bytes Number of morphs, or version?
    morphs_count=int.from_bytes(file.read(4), byteorder='big', signed=False)
    logger.debug('Number of morphs?\t%d' % morphs_count)
    
    morphs=[]
    for m in range(morphs_count):
        morph=Morph()
        ## bpl string [1 byte length, followed by ascii chars]
        bpl_length=int.from_bytes(file.read(1), byteorder='big', signed=False)
        
        morph.name=(file.read(bpl_length)).decode("ascii")
        
        ## bpl string [1 byte length, followed by ascii chars]
        bpl_length=int.from_bytes(file.read(1), byteorder='big', signed=False)
        
        morph.group=(file.read(bpl_length)).decode("ascii")
        
        ## 4 bytes number of verts in group
        morph.numbDeltas=int.from_bytes(file.read(4), byteorder='big', signed=False)
    
        ## 4 bytes numDeltas
        morph.fileOffset=int.from_bytes(file.read(4), byteorder='big', signed=False)
        morphs.append( morph )
    
    # Calculate number of indexes by finding the file offset of the next morph, subtract
    # the file offset of this morph, subtract 4 for the size, then divide by 16
    for i in range(morphs_count-1):
        morphs[i].indexes=int( (morphs[i+1].fileOffset - morphs[i].fileOffset - 4) / 16 )
        morphs[i].log()
    
    # handle last morph separately
    morphs[-1].indexes=int( (filesize - morphs[-1].fileOffset - 4) / 16 )
    morphs[-1].log()
    
    for morph in morphs:
        file.seek(morph.fileOffset)
        indexes = int.from_bytes(file.read(4), byteorder='big', signed=False)
        if indexes == morph.indexes:
            logger.debug('%s indexes count matched!' % morph.name)
        ## ## 4 bytes index 3x4 bytes delta
            for i in range(morph.indexes):
                delta = file.read(16)
                idx=int.from_bytes(delta[0:4], byteorder='big', signed=False)
                vect=struct.unpack('>fff', delta[4:17])
                morph.deltas.append( { int(idx) : vect } )
            # print(idx, vect)
            if indexes == len(morph.deltas):
                logger.debug('%s all delta indexes read!'%morph.name )
        else:
            logger.critical('Expected %d deltas but found %d' %(morph.indexes, indexes) )
            raise ValueError('Morphs were not parsed correctly!')
    
    file.close()
    logger.info('Read %d morphs, expected %d' % (len(morphs), morphs_count) )
    return(morphs)

if __name__ == '__main__':
    import sys
    print (sys.argv[1])
    logging.basicConfig(level=logging.DEBUG)
    morphs = readPZMD(filename=sys.argv[1])

