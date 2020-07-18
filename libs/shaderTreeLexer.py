import shaderTreeParser as stp
import PT2_open as ptl 

## lexer=D.texts['shaderTreesLexer.py'].as_module()
## mat=lexer.shaderTreeLexer(r'c:\tmp\Runtime\Libraries\materials\TransparentBsdf.mt5', dumpfilepath=r'c:\tmp\TransparentBsdf.mt5')

def shaderTreeLexer(filepath, dumpfilepath=None, rawdumpfilepath=None):
    ''' Read in a Poser file and extract the material section 
    which is returned as a list of lines.
    filepath: is the full path to the file to parse
    dumpfilepath: optional output file of the Poser materials.
    rawdumpfilepath: optional output file of the lexer output'''
    
    print ('Reading Mat File:...\n\n')

    #########################################
    #  
    # Read Mat File
    # 
    
    file = ptl.PT2_open(filepath, 'rt')
    lines = []
    for x in file:
        lines.append(x.strip())
    file.close() 

    raw_mats = [] # an array of the unparsed materials
    mat_name = ''
    comps = []    # a list of the unparsed lines
    readcomps = False
    depth = 0
    
    for line in lines:
        #print (line)
        skip = 0
        if line.startswith('material') is True:
            #print ('Mat:', line.replace('material', ''))
            mat_name = line.replace('material', '').strip()
            readcomps = True # Turn on component reader
            print ('Mat Name:', mat_name)
            skip = 1
            
        elif line.startswith('{') is True and readcomps is True:
            depth += 1
            #skip = 1
           
            
        elif line.startswith('}') is True and depth > 0:
            depth -= 1
            #skip = 1
            
        if readcomps == True and skip != 1:
            #print(depth, line)
            comps.append([depth, line.split()]) 
           
        if depth == 0 and readcomps is True and len(comps) > 0:
            readcomps=False
            raw_mats.append([mat_name, comps])
            mat_name = ''
            comps = []
            

    #########################################
    #  
    # Displays Mat Array
    #                 
    print ('\n\nFinished creating array...\n')
    dumpfile=None
    if rawdumpfilepath:
        dumpfile=open(rawdumpfilepath, 'wt')
        
    if dumpfile:
        for mat in raw_mats:
            print (mat[0], file=dumpfile)
            for comp in mat[1]:
                print (comp, file=dumpfile)
            print ('\n', file=dumpfile)
        dumpfile.close()

    dumpfile=None
    if dumpfilepath:
        dumpfile=open(dumpfilepath, 'wt')
    
    mats={}
    for raw_mat in raw_mats:
        mats[raw_mat[0]] = stp.parseMaterial( iter(raw_mat[1]), raw_mat[0] )
        if dumpfile:
            mats[raw_mat[0]].write(depth=1, file=dumpfile)
    
    dumpfile.close()
    return(mats)


