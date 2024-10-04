// -----------------------------------------------------------------------
// Image recognition module. Line primitives.

#include <Python.h>
//#include <pygobject.h>

#include "imgrec.h"
#include "utils.h"

// -----------------------------------------------------------------------
//   blank(x, y, x2, y2, color) - blank rect with color

PyObject *_blank(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", "color", NULL };
    
    // Defaults
    int arg1 = 0;  int arg2 = 0; 
    int arg3 = dim2;  int arg4 = dim1; int arg5 = 0xFF000000;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iiiiI", kwlist, &arg1, &arg2, &arg3, &arg4, &arg5))
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
    int *curr = anchor, loop, loop2;
    for (loop = arg2; loop < arg4; loop++)  // yy
        {
        int offs = loop * dim2;
        for (loop2 = arg1; loop2 < arg3; loop2++)  //xx
             curr[offs + loop2]  = arg5;
        }
    return Py_BuildValue("");
}    

PyObject *_grayen(PyObject *self, PyObject *args, PyObject *kwargs)
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
    int *curr = anchor, loop, loop2;
    for (loop = arg2; loop < arg4; loop++)
        {
        unsigned char rr, gg, bb;
        
        int old, offs = loop * dim2;
        for (loop2 = arg1; loop2 < arg3; loop2++)
            {
             old = curr[offs + loop2];
             
             // Break apart
             rr = old & 0xff; gg = (old>>8) & 0xff; bb = (old>>16) & 0xff;
             // Clip to 0
             if (rr > arg5) rr -= arg5; else  rr = 0;
             if (gg > arg5) gg -= arg5; else  gg = 0;
             if (bb > arg5) bb -= arg5; else  bb = 0;
             // Assemble            
             old = 0xff; old <<= 8; old |= bb; old <<= 8; 
             old |= gg; old <<= 8; old |= rr; 
             
             curr[offs + loop2] = old;
             }
        }
    return Py_BuildValue("");
}    

PyObject *_whiten(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", "color", NULL };
    
    int arg1 = 0;  int arg2 = 0; int arg3 = 0;  int arg4 = 0; int arg5 = 0;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiiiI", kwlist, &arg1, &arg2, &arg3, &arg4, &arg5))
            return NULL;
    
    if( is_verbose())
        printf("Whitening %d %d %d %d color=0x%x\n", arg1, arg2, arg3, arg4, arg5);
    
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
    int *curr = anchor, loop, loop2;
    for (loop = arg2; loop < arg4; loop++)
        {
        unsigned char rr, gg, bb;
        
        int old, offs = loop * dim2;
        for (loop2 = arg1; loop2 < arg3; loop2++)
            {
             old = curr[offs + loop2];
             
             // Break apart
             rr = old & 0xff; gg = (old>>8) & 0xff; bb = (old>>16) & 0xff;
             // Clip to 255
             if (rr + arg5 < 255) rr += arg5; else  rr = 255;
             if (gg + arg5 < 255) gg += arg5; else  gg = 255;
             if (bb + arg5 < 255) bb += arg5; else  bb = 255;
             // Assemble            
             old = 0xff; old <<= 8; old |= bb; old <<= 8; 
             old |= gg; old <<= 8; old |= rr; 
             
             curr[offs + loop2] = old;
             }
        }
    return Py_BuildValue("");
}    

PyObject *_median(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", NULL };
    
    int arg1 = 0; int arg2 = 0; int arg3 = 0;  int arg4 = 0; 
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiii", kwlist, &arg1, &arg2, &arg3, &arg4))
            return NULL;
    
    if( is_verbose())
        printf("Median %d %d %d %d\n", arg1, arg2, arg3, arg4);
    
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
     
    if (arg1 > arg3 || arg2 > arg4)
        {
        PyErr_Format(PyExc_ValueError, "%s", "coordinates need to be in increasing order");
        return NULL;
        }
        
    int dx = arg3 - arg1; int dy = arg4 - arg2, old;
    
    int aarr = 0, aagg = 0, aabb = 0;                  // Main accumulators
    int *curr = anchor, loop, loop2;
    for (loop = arg2; loop < arg4; loop++)
        {
        int offs = loop * dim2;
        int arr = 0, agg = 0, abb = 0;                  // Accumulators
        for (loop2 = arg1; loop2 < arg3; loop2++)
            {
            old = curr[offs + loop2];
            // Break apart
            int rr = old & 0xff; int gg = (old>>8) & 0xff; 
            int bb = (old>>16) & 0xff;
            arr += rr; agg += gg; abb += bb;
            }
        arr /= dx; agg /= dx; abb /= dx;
        aarr += arr; aagg += agg; aabb += abb;
        }
    aarr /= dy; aagg /= dy; aabb /= dy;

    // Assemble            
    old = 0xff; old <<= 8; 
    old |= aabb; old <<= 8;  old |= aagg; 
    old <<= 8;   old |= aarr; 
    
    if( is_verbose())
        printf("Median result 0x%x\n", old);
    
    return Py_BuildValue("I", (int)old);
}    

PyObject *_medianmulti(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", NULL };
    
    int arg1 = 0; int arg2 = 0; int arg3 = 0;  int arg4 = 0; 
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiii", kwlist, &arg1, &arg2, &arg3, &arg4))
            return NULL;
    
    if( is_verbose())
        printf("Median %d %d %d %d\n", arg1, arg2, arg3, arg4);
    
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
     
    if (arg1 > arg3 || arg2 > arg4)
        {
        PyErr_Format(PyExc_ValueError, "%s", "coordinates need to be in increasing order");
        return NULL;
        }
        
    int dx = arg3 - arg1; int dy = arg4 - arg2, old;
    
    int aarr = 0, aagg = 0, aabb = 0;                  // Main accumulators
    int *curr = anchor, loop, loop2;
    for (loop = arg2; loop < arg4; loop++)
        {
        int offs = loop * dim2;
        int arr = 0, agg = 0, abb = 0;                  // Accumulators
        for (loop2 = arg1; loop2 < arg3; loop2++)
            {
            old = curr[offs + loop2];
            // Break apart
            int rr = old & 0xff; int gg = (old>>8) & 0xff; 
            int bb = (old>>16) & 0xff;
            arr += rr; agg += gg; abb += bb;
            }
        arr /= dx; agg /= dx; abb /= dx;
        aarr += arr; aagg += agg; aabb += abb;
        }
    aarr /= dy; aagg /= dy; aabb /= dy;

    // Assemble            
    old = 0xff; old <<= 8; 
    old |= aabb; old <<= 8;  old |= aagg; 
    old <<= 8;   old |= aarr; 
    
    if( is_verbose())
        printf("Median result 0x%x\n", old);
    
    return Py_BuildValue("I", (int)old);
}    








