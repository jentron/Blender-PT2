import gzip
from pathlib import Path

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
        new_file = Path(myfile.parents[0],  myfile.stem + "".join(stem))

    if( new_file.exists()):
        pass
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)

    with gzip.open(new_file, mode) as fh:
        try:
            fh.read(1)
        except OSError:
            print(f'%s is not a gzip file by OSError'%new_file)
            is_gzip=False
    
    if(is_gzip):
        return( gzip.open(new_file, mode))

    return( open(new_file, mode))
