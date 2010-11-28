#!/usr/bin/env python
# encoding: utf-8

"""
This file properly imports the open CV libraries and returns them
as an object. This function goes a longer way to try to find them
since especially on MacOS X Library Paths are not clearly defined.

This module also removes the code duplication in __init__ and
opencv_cv
"""

__all__ = ["cv", "cxcore"]

import ctypes
import sys
import os.path
import warnings


def _extract_windows_prefix_and_version(cxcore_dll_name):
    """
    Extract the prefix and the version strings, from the cxcore DLL name. 
            
    Example: 
        - with the compiled OpenCV2.0 binaries
        libcxcore200.dll -> returns ("lib", "200")
        
        - with the compiled OpenCV2.1 binaries
        cxcore210.dll -> returns ("", "210")
    """
    prefix, version = cxcore_dll_name.split("cxcore")
    return prefix, version



def _detect_windows_opencv_prefix_and_version():
    """
    Checks the windows %PATH% and tries to guess the naming scheme of 
    the installed OpenCV 2.x binaries.
    """
    import os
    windows_path = os.getenv("PATH").split(";")
    opencv_paths = [s for s in windows_path if s.lower().find("opencv")!=-1]
    if not opencv_paths:
        warning.warn("No OpenCV found in path. Please install OpenCV >= 2.0")
    opencv_bin_path = opencv_paths[0]
    opencv_release_dlls = [f for f in os.listdir(opencv_bin_path) if 
                                    f.endswith(".dll") and 
                                    not f.endswith("d.dll")]
    
    # we use cxcore as reference because it's not an optionnal library, 
    # and the substring "cv" is found in both cv and cvaux
    cxcore_dll_name = [f for f in opencv_release_dlls if f.find("cxcore") != -1][0]    
    return _extract_windows_prefix_and_version(cxcore_dll_name.rstrip(".dll"))



def _import_opencv_lib(which="cv"):
    """
    Try to import a shared library of OpenCV.

    which - Which library ["cv", "cxcore", "highgui"]
    """
    library_paths = ['',
                     '/lib/',
                     '/usr/lib/',
                     '/usr/local/lib/',
                     '/opt/local/lib/', # MacPorts
                     '/sw/lib/', # Fink
                     ]

    lib, version = ("", "")
    if sys.platform.startswith('linux'):
        extensions = ['.so', '.so.1']
        lib = 'lib' + which
    elif sys.platform.startswith("darwin"):
        extensions = ['.dylib']
        lib = 'lib' + which
    else:
        extensions = ['.dll']
        prefix, version = _detect_windows_opencv_prefix_and_version()
        lib = prefix + which + version
        library_paths = ['']

    shared_lib = None

    for path in library_paths:
        for ext in extensions:
            try:
                shared_lib = ctypes.CDLL(os.path.join(path, lib + ext))
            except OSError:
                pass
            else:
                return shared_lib

    warnings.warn(RuntimeWarning(
        'The opencv libraries were not found.  Please ensure that they '
        'are installed and available on the system path. '))

cv = _import_opencv_lib("cv")
cxcore = _import_opencv_lib("cxcore")
