#=============================================================================
# Simplified BSD License, see http://www.opensource.org/licenses/
#-----------------------------------------------------------------------------
# Copyright (c) 2011-2012, HEB Ventures, LLC
# All rights reserved.

# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:

# *    Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
# *    Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#=============================================================================

bl_info = {
    "name": "Poser Tools 2",
    "author": "Scott Brickwood, Ron Jensen",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "api": 41098,
    "location": "File > Import-Export",
    "description": "Tool for importing & exporting Poser props and characters",
    "warning": "Work in progress",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Import-Export/Poser_Tools",
    "category": "Import-Export"}

import bpy

from . import PPI12
from . import PPI11
from . import PPE7
from . import PCI1
from . import PCI2
from . import PMR38
from . import PMR39
from . import PDB1

class LoadPT2:
    bl_idname = "PT Tools 2"
    bl_label = "PT2 tools label"
    import PT2

def register():
    #import PT2
    LoadPT2().PT2.PPI11.register()
    LoadPT2().PT2.PPI12.register()
    LoadPT2().PT2.PPE7.register()
    LoadPT2().PT2.PCI1.register()
    LoadPT2().PT2.PCI2.register()
    LoadPT2().PT2.PMR38.register()
    LoadPT2().PT2.PMR39.register()
    LoadPT2().PT2.PDB1.register()

def unregister():
    LoadPT2().PT2.PPI11.unregister()
    LoadPT2().PT2.PPI12.unregister()
    LoadPT2().PT2.PPE7.unregister()
    LoadPT2().PT2.PCI1.unregister()
    LoadPT2().PT2.PCI2.unregister()
    LoadPT2().PT2.PMR38.unregister()
    LoadPT2().PT2.PMR39.unregister()
    LoadPT2().PT2.PDB1.unregister()
   
if __name__ == "__main__":
    register()
