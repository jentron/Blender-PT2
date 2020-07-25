#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2020, Ronald Jensen
# All rights reserved.

import gzip
from pathlib import Path
import re
import errno
import os

def PT2_open(name, mode):
    is_gzip=True
    
    myfile=Path(name)
    #print("Test Existance")
    if( myfile.exists() ):
        print(f"%s exists!"%myfile)
        new_file=myfile
    else:
        stem = list(myfile.suffix)
        print(stem)
        stem[-1] = 'z'
        new_file = Path(myfile.parents[0], myfile.stem + "".join(stem))

    if( new_file.exists()):
        pass
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), new_file)

    with gzip.open(new_file, mode) as fh:
        try:
            fh.read(1)
        except OSError:
            print(f'%s is not a gzip file by OSError'%new_file)
            is_gzip=False
    
    if(is_gzip):
        return( gzip.open(new_file, mode))

    return( open(new_file, mode))

def namecheck01(input):
    output = re.sub(r' *: *[0-9]+', '', input)
    return( output )