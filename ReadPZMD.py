# -*- coding: utf-8 -*-
"""
pmd (Poser Morph D...)
Created on Tue Jul  7 15:37:48 2020

@author: rjensen
"""
import struct

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

    def print(self):
        print ('Morph:', self.name,
               'Target:', self.group,
               'Indexes: ', self.indexes,
               'numbDeltas:', self.numbDeltas )

morph=Morph()


filename="M4.pmd"
file=open(filename, 'rb')

## 4bytes PZMD
foo=file.read(4)
if (foo==b'PZMD'):
    print("It's a Poser Morph File!")
else:
    print("Ooops, throw an error!")

## 4bytes Number of morphs, or version?
foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
print(foo)

## 4bytes pad?
foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
print(foo)

## 4bytes Size of morph header
foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
print(foo)

## 4bytes Number of morphs, or version?
foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
print(foo)

## bpl string [1 byte length, followed by ascii chars]
bpl_length=int.from_bytes(file.read(1), byteorder='big', signed=False)

morph.name=(file.read(bpl_length)).decode("ascii")
print(morph.name)

## bpl string [1 byte length, followed by ascii chars]
bpl_length=int.from_bytes(file.read(1), byteorder='big', signed=False)

morph.group=(file.read(bpl_length)).decode("ascii")
print(morph.group)

## 4 bytes number of deltas
morph.indexes=int.from_bytes(file.read(4), byteorder='big', signed=False)
print('indexes', morph.indexes)

## 4 bytes unknown
foo=int.from_bytes(file.read(4), byteorder='big', signed=False)
# foo=file.read(4)
print(foo)

## 4 bytes numDeltas
morph.numbDeltas=int.from_bytes(file.read(4), byteorder='big', signed=False)
print('numDeltas', morph.numbDeltas)


## 4 bytes index 3x4 bytes delta
for i in range(morph.numbDeltas):
    delta = file.read(16)
    idx=int.from_bytes(delta[0:4], byteorder='big', signed=False)
    vect=struct.unpack('>ifff', delta)
    morph.deltas.append( { int(idx) : vect } )
   # print(idx, vect)
print('actdeltas', len(morph.deltas))

file.close()
