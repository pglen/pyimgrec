// -----------------------------------------------------------------------
// Image recognition module. Flood fill primitives.

#include <Python.h>
//#include <pygobject.h>

#include "imgrec.h"
#include "utils.h"

PyObject *_flood(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", "color", NULL };
    
    int arg1 = 0;  int arg2 = 0; int arg3 = 0;  int arg4 = 0; int arg5 = 0;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiiiI", kwlist, &arg1, &arg2, &arg3, &arg4, &arg5))
            return NULL;
    
    if( is_verbose())
        printf("Blanking %d %d %d %d color=0x%x\n", arg1, arg2, arg3, arg4, arg5);
    
    if(!anchor)
        {
        PyErr_Format(PyExc_ValueError, "%s", "anchor must be set before any operation");
        return NULL;
        }
    if (arg1 < 0 || arg2 < 0 ||  arg3 < 0 ||  arg4  < 0 )
        {
        PyErr_Format(PyExc_ValueError, "%s", "argument(s) cannot be negative");
        return NULL;
        }
     if (arg1 > dim2 || arg2 > dim1 || arg3 > dim2 || arg4  > dim1 )
        {
        PyErr_Format(PyExc_ValueError, "%s (%ld %ld)", "must be within array limits", dim1, dim2);
        return NULL;
        }
        
    // All set, flush it out
    int *curr = anchor, loop2;
    
    int offs = dim2 * arg2;
    for (loop2 = arg1; loop2 < arg3; loop2++)
        curr[offs + loop2]  = arg5;
        
    int offs2 = dim2 * arg4;
    for (loop2 = arg1; loop2 < arg3; loop2++)
        curr[offs2 + loop2]  = arg5;
        
    for (loop2 = arg2; loop2 < arg4; loop2++)
        curr[dim2 * loop2 + arg1]  = arg5;
    
    for (loop2 = arg2; loop2 < arg4; loop2++)
        curr[dim2 * loop2 + arg3]  = arg5;
        
    //for (loop = arg2; loop < arg4; loop++)
    //    {
    //    }
    
    return Py_BuildValue("");
} 





