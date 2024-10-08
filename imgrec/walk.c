// -----------------------------------------------------------------------
// Image recognition module. Walk routines.
//

#include <Python.h>

#include "imgrec.h"
#include "utils.h"

static int avg;             // Global for passing avg between parts

PyObject *_walk(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty", "endx", "endy", NULL };
    int arg1 = 0;  int arg2 = 0; int arg3 = 0;  int arg4 = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iiii", kwlist, &arg1, &arg2, &arg3, &arg4))
            return NULL;

    if( is_verbose())
        printf("Walk %d %d %d %d\n", arg1, arg2, arg3, arg4);

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
    if(reent)
        {
        PyErr_Format(PyExc_ValueError, "%s", "Cannot reenter");
        return NULL;
        }

    reent = 1;

    // Test cross markers
    #if 1
    int dist = 12;
    for (int loop = dist; loop < dim2 - dist; loop += dist) // yy
        {
        for (int loop2 = dist; loop2 < dim1 - dist; loop2 += dist) // xx
            {
            int xold = RGB(0x88, 0x88, 0x88);
            add_item(loop2, loop, xold, DOT2);
            }
        }
    #endif

    // Mark starting point
    int cdot = RGB(0x88, 0x88, 0x88);
    int xold = RGB(0, 0, 0);

    add_item(arg1, arg2, xold, XCROSS);
    avg = calc_avg();
    // Scan away
    int xxx = arg1, yyy = arg2;
    int *curr = anchor;
    for(;;) {

        // Boundary exit
        if(xxx < 0 || yyy < 0)
            break;
        if(xxx > dim1 || yyy > dim2)
            break;

        int offs = yyy * dim1;
        int val = curr[offs + xxx];
        if ((val & 0xff) < avg)
            {
            printf("found: %d %d\n", xxx, yyy);
            add_item(xxx, yyy, cdot, XCROSS);
            xxx += 1;
            break;
            }

        // Update coordinates
        xxx += 1;
        if (xxx >= dim1)
            {
            xxx = 0; yyy += 1;
            }
        if (yyy >= dim1)
            break;
    }

    //print_list();
    show_crosses();

    reent = 0;
    return Py_BuildValue("");
}
