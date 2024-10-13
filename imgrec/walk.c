// -----------------------------------------------------------------------
// Image recognition module. Walk routines.
//

#include <Python.h>

#include "imgrec.h"
#include "utils.h"

static int avg;             // Global for passing avg between parts
static int reent_walk = 0;

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
    if(reent_walk)
        {
        PyErr_Format(PyExc_ValueError, "%s", "Cannot reenter");
        return NULL;
        }

    reent_walk = 1;

    // Test cross markers
    #if 0
    int dist = 20;
    for (int loop = 0; loop < dim2; loop += dist) // yy
        {
        for (int loop2 = 0; loop2 < dim1; loop2 += dist) // xx
            {
            int xcol = RGB(0, 0, 0xff);
            add_item(loop2, loop, xcol, XCROSS);
            }
        }
    #endif

    // Mark ref color
    //avg = calc_avg();
    avg = 0x55;

    // Scan away
    int xxx = arg1, yyy = arg2;
    int found = 0;
    int *curr = anchor;
    for(;;) {
        int offs = yyy * dim1;
        int val;
        val = curr[offs + xxx] & 0x00ffffff;
        //printf ("val: %x\n", val);
        int valx = val & 0xff; valx += (val >> 8) & 0xff;
        valx += (val >> 16) & 0xff;  valx /= 3;
        if (valx  < avg)
            {
            //printf("found at: xxx=%d yyy=%d val=%x\n", xxx, yyy, valx);
            int cdot = RGB(0, 0, 0xff);
            add_item(xxx, yyy, cdot, XCROSS);
            found = 1;
            break;
            }
        // Update coordinates
        xxx += 1;
        if (xxx >= dim1)
            {
            xxx = 0; yyy += 1;
            }
        if (yyy >= dim2)
            break;
    }

    //print_list();
    show_crosses();
    reent_walk = 0;

    if(found)
        return Py_BuildValue("ii", xxx, yyy);
    else
        return Py_BuildValue("");
}
