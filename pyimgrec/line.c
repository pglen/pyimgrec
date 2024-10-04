// -----------------------------------------------------------------------
// Image recognition module. Line primitives.

#include <Python.h>
//#include <python2.7/pygobject.h>

#include "imgrec.h"
#include "utils.h"

// Textbook line drawing. Using double as the slope. While it is not
// optimzed, it does short circuit vertical / horizontal lines.
// As python is 2000 times slower, no effort is needed to sqeeze 
// performance.

static int __line(int arg1, int arg2, int arg3, int arg4, int arg5)

{
    int loop2, tmp;
    int *curr = anchor;

    // Special cases:
    if (arg2 == arg4)               // Horiz
        {
        if(is_verbose())
            printf("horiz\n");
            
        if (arg1 > arg3) {              // Swap them, if needed
            tmp = arg2, arg2 = arg4, arg4 = tmp;  
            tmp = arg1, arg1 = arg3, arg3 = tmp; 
            }
        int offs = dim2 * arg2;
        for (loop2 = arg1; loop2 < arg3; loop2++)
            curr[offs + loop2]  = arg5;
        }
    else if (arg1 == arg3)        // Vert
        {       
        if(is_verbose())
            printf("vert\n");
        if (arg2 > arg4) {
            tmp = arg2, arg2 = arg4, arg4 = tmp;  
            tmp = arg1, arg1 = arg3, arg3 = tmp; 
            }
        for (loop2 = arg2; loop2 < arg4; loop2++)
            curr[dim2 * loop2 + arg1]  = arg5;
        }
    else                       // General case
        {
        //   x=arg1, y=arg2  -- |
        //                      |-- x2=arg3 y2=arg4
        
        if( abs(arg3-arg1) > abs(arg4-arg2))
            {
            // x - major
            if (arg1 > arg3) {                       // Swap them, if needed
                tmp = arg2, arg2 = arg4, arg4 = tmp;  
                tmp = arg1, arg1 = arg3, arg3 = tmp; 
                }
            int dx = arg3 - arg1; int dy =  arg4 - arg2;
            double slope = ((double)dy) / dx;
            if(is_verbose())
                printf("x - major %f\n", slope);
            for (loop2 = 0; loop2 < dx; loop2++)
                {
                int offs = slope * loop2 + arg2;
                curr[offs * dim2 + loop2 + arg1]  = arg5;
                }
            }
        else                
            {
            // y - major
            if (arg2 > arg4) {                      // Swap them, if needed
                tmp = arg2, arg2 = arg4, arg4 = tmp;  
                tmp = arg1, arg1 = arg3, arg3 = tmp; 
                }
            int dx = arg3 - arg1; int dy =  arg4 - arg2;
            double slope = ((double)dx) / dy;
            if(is_verbose())
                printf("y - major %f\n", slope);
            for (loop2 = 0; loop2 < dy; loop2++)
                {
                int offs = slope * loop2 + arg1;
                curr[(loop2 + arg2) * dim2 + offs]  = arg5;
                }
            }
        }
    return 0;

}

PyObject *_frame(PyObject *self, PyObject *args, PyObject *kwargs)
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

PyObject *_line(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", "color", NULL };
    
    int arg1 = 0; int arg2 = 0; int arg3 = 0;  int arg4 = 0; int arg5 = 0;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiiiI", kwlist, &arg1, &arg2, &arg3, &arg4, &arg5))
            return NULL;
    
    if( is_verbose())
        printf("Line %d %d %d %d color=0x%x\n", arg1, arg2, arg3, arg4, arg5);
    
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
    __line(arg1, arg2, arg3, arg4, arg5);
    
    return Py_BuildValue("");
} 

PyObject *_poly(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "color", "points", NULL };
    
    int arg5 = 0; PyObject *tup = 0; 
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IO", kwlist, &arg5, &tup))
            return NULL;
    
    int len = PyTuple_GET_SIZE(tup);
    if(len % 2 != 0 || len < 4)
        {
        PyErr_Format(PyExc_ValueError, "%s", "num of coords must be dvisible 2 and >= 4");
        return NULL;
        }
        
    if( is_verbose())
        printf("Poly color=%x len=%d\n", arg5, len);
    
    if(!anchor)
        {
        PyErr_Format(PyExc_ValueError, "%s", "anchor must be set before any operation");
        return NULL;
        }
        
    int arg1, arg2, loop;
    // Inital points
    PyObject *d1 = PyTuple_GetItem(tup, 0); arg1 = PyInt_AsLong(d1);
    PyObject *d2 = PyTuple_GetItem(tup, 1); arg2 = PyInt_AsLong(d2);
        
    // Collect valuses, paint
    for(loop = 2; loop < len; loop += 2)
        {
        PyObject *d11 = PyTuple_GetItem(tup, loop);
        int arg3 = PyInt_AsLong(d11);
        
        PyObject *d21 = PyTuple_GetItem(tup, loop+1);
        int arg4 = PyInt_AsLong(d21);

        if( is_verbose())
            printf("Drawing line: %d %d %d %d\n", arg1, arg2, arg3, arg4);
            
         __line(arg1, arg2, arg3, arg4, arg5);
         
         arg1 = arg3; arg2 = arg4;
        }    
        
    return Py_BuildValue("");
} 




