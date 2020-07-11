# -*- coding: utf-8 -*-
"""
pmd (Poser Morph D...)
Created on Tue Jul  7 15:37:48 2020

@author: rjensen
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
        self.value = 0
        self.name = 'shape'
        self.group = ''
        self.indexes = -1
        self.numbDeltas = -1
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
        morph.indexes=int.from_bytes(file.read(4), byteorder='big', signed=False)
    
        ## 4 bytes numDeltas
        morph.fileOffset=int.from_bytes(file.read(4), byteorder='big', signed=False)
        morphs.append( morph )
    
    # Calculate numDeltas by finding the file offset of the next morph, subtract
    # the file offset of this morph, subtract 4 for the size, then divide by 16
    for i in range(morphs_count-1):
        morphs[i].numbDeltas=int( (morphs[i+1].fileOffset - morphs[i].fileOffset - 4) / 16 )
        morphs[i].log()
    
    # handle last morph separately
    morphs[-1].numbDeltas=int( (filesize - morphs[-1].fileOffset - 4) / 16 )
    morphs[-1].log()
    
    for morph in morphs:
        file.seek(morph.fileOffset)
        numbDeltas = int.from_bytes(file.read(4), byteorder='big', signed=False)
        if numbDeltas == morph.numbDeltas:
            logger.debug('%s numbDeltas matched!' % morph.name)
        ## ## 4 bytes index 3x4 bytes delta
            for i in range(morph.numbDeltas):
                delta = file.read(16)
                idx=int.from_bytes(delta[0:4], byteorder='big', signed=False)
                vect=struct.unpack('>fff', delta[4:17])
                morph.deltas.append( { int(idx) : vect } )
            # print(idx, vect)
            if numbDeltas == len(morph.deltas):
                logger.debug('%s all deltas read!'%morph.name )
        else:
            logger.critical('Expected %d deltas but found %d' %(morph.numbDeltas, numbDeltas) )
            raise ValueError('Morphs were not parsed correctly!')
    
    file.close()
    logger.info('Read %d morphs, expected %d' % (len(morphs), morphs_count) )
    return(morphs)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    morphs = readPZMD(filename="P7Kate.pmd")
    print(type(morphs[0].deltas[0] ) )
    