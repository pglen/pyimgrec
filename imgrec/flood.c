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
        printf("flood: %d %d %d %d color=0x%x\n", arg1, arg2, arg3, arg4, arg5);

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

    return Py_BuildValue("i", 0);
}

PyObject *_average(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", NULL };

    int arg1 = 0;  int arg2 = 0; int arg3 = dim1;  int arg4 = dim2;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iiii", kwlist,
                                        &arg1, &arg2, &arg3, &arg4))
            return NULL;

    if( is_verbose())
        printf("flood: %d %d %d %d\n", arg1, arg2, arg3, arg4);

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
     if (arg1 > dim1 || arg2 > dim2 || arg3 > dim1 || arg4  > dim2 )
        {
        PyErr_Format(PyExc_ValueError, "%s (%ld %ld)", "must be within array limits", dim1, dim2);
        return NULL;
        }

    int *curr = anchor;
    int avg = 0, cnt = 0, loop, loop2;

    for (loop = arg2; loop < arg4; loop++)
        {
        int offs = loop * dim1;

        for (loop2 = arg1; loop2 < arg3; loop2++)
            {
            unsigned int ccc = curr[offs + loop2];
            int rr, gg, bb, xold;

            // Break color apart:
            APART(ccc, rr, gg, bb)
            xold = rr + gg + bb; xold /= 3;
            avg += xold;
            cnt += 1;
            }
        }
    int ret = 0;
    if(cnt)
        ret = avg / cnt;
    return Py_BuildValue("i", ret);
}


// implement Seek(xxx, yyy, param, gl_dones):

PyObject *_seek(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty", "param", "gl_dones", NULL };

    int arg1 = 0;  int arg2 = 0;
    PyObject *arg3 = NULL;  PyObject *arg4 = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiOO", kwlist,
                                        &arg1, &arg2, &arg3, &arg4))
            return NULL;

    if( is_verbose())
        printf("seek: %d %d %p %p\n", arg1, arg2, arg3, arg4);

    // Check types:
    PyObject *darr = PyObject_GetAttr(arg3, Py_BuildValue("s", "darr"));
    if (!darr)
        {
        PyErr_Format(PyExc_TypeError, "%s", "expected floodParm object");
        return NULL;
        }
    if (!PyDict_Check(darr))
        {
        PyErr_Format(PyExc_TypeError, "%s", "expected dict in floodparm.darr");
        return NULL;
        }
    if (PyDict_Size(darr) == 0)
        {
        PyErr_Format(PyExc_ValueError, "%s", "floodparm.darr cannot be empty");
        return NULL;
        }
    if (!PyDict_Check(arg4))
        {
        PyErr_Format(PyExc_TypeError, "%s", "expected dictionary");
        return NULL;
        }

    int iww = intfromclass(arg3, "iww");
    int ihh = intfromclass(arg3, "ihh");
    printf("_seek() iww = %d ihh = %d len = %ld\n", iww, ihh, PyDict_Size(darr));

    if(!anchor)
        {
        PyErr_Format(PyExc_ValueError, "%s", "anchor must be set before any operation");
        return NULL;
        }
    if (arg1 < 0 || arg2 < 0 )
        {
        PyErr_Format(PyExc_ValueError, "%s", "argument(s) cannot be negative");
        return NULL;
        }
     if (arg1 > dim1 || arg2 > dim2 )
        {
        PyErr_Format(PyExc_ValueError, "%s (%ld %ld)", "must be within array limits", dim1, dim2);
        return NULL;
        }

    //printf("Seek()");

    return Py_BuildValue("i", 0);

    #if 0
    int *curr = anchor;
    int avg = 0, cnt = 0, loop, loop2;

    for (loop = arg2; loop < arg4; loop++)
        {
        int offs = loop * dim1;

        for (loop2 = arg1; loop2 < arg3; loop2++)
            {
            unsigned int ccc = curr[offs + loop2];
            int rr, gg, bb, xold;

            // Break color apart:
            APART(ccc, rr, gg, bb)
            xold = rr + gg + bb; xold /= 3;
            avg += xold;
            cnt += 1;
            }
        }
    int ret = 0;
    if(cnt)
        ret = avg / cnt;
    return Py_BuildValue("i", ret);

    #endif
}

// # EOF



