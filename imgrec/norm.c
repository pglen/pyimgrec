// -----------------------------------------------------------------------
// Image recognition module. Normalizer and misc. primitives.
//
//

#include <Python.h>
//#include <pygobject.h>

#include "imgrec.h"
#include "utils.h"

//static int avg;             // Global for passing avg between parts

// -----------------------------------------------------------------------

PyObject *_norm(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", NULL };

    int arg1 = 0;  int arg2 = 0; int arg3 = dim1;  int arg4 = dim2;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iiii", kwlist, &arg1, &arg2, &arg3, &arg4))
            return NULL;

    if( is_verbose())
        printf("Normalizing %d %d %d %d\n", arg1, arg2, arg3, arg4);

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
     if (arg3 > dim1 || arg4  > dim2 )
        {
        PyErr_Format(PyExc_ValueError, "%s (%ld %ld)", "must be within array limits", dim1, dim2);
        return NULL;
        }

    // All set, flush it out
    int *curr = anchor, loop, loop2;

    int avg = calc_avg();

    for (loop = 0; loop < dim2; loop++)
        {
        int offs = loop * dim1;

        for (loop2 = 0; loop2 < dim1; loop2++)
            {
            unsigned int ccc = curr[offs + loop2];
            int rr, gg, bb, xold, rrr, ggg, bbb;

            // Break apart
            APART(ccc, rr, gg, bb)

            // Operate: add / clip
            rrr = rr - 10; DCLIP(rrr)
            ggg = gg - 10; DCLIP(ggg)
            bbb = bb - 10; DCLIP(bbb)

            // Assemble
            ASSEM(xold, rrr, ggg, bbb)

            // disabled for now
            //curr[offs + loop2] = xold;
            }
        }
    return Py_BuildValue("");
}

PyObject *_bridar(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "coladj", NULL };

    int arg1 = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i", kwlist, &arg1))
            return NULL;

    if (1) //if( is_verbose())
        printf("BriDar with %d\n", arg1);

    if(!anchor)
        {
        PyErr_Format(PyExc_ValueError, "%s", "anchor must be set before any operation");
        return NULL;
        }

    // All set, flush it out
    int *curr = anchor, loop, loop2;

    for (loop = 0; loop < dim1; loop++)
        {
        int offs = loop * dim2;

        for (loop2 = 0; loop2 < dim2; loop2++)
            {
            unsigned int ccc = curr[offs + loop2];
            int rr, gg, bb, xold, rrr, ggg, bbb;

            // Break apart
            APART(ccc, rr, gg, bb)

            // Operate: add / clip
            rrr = rr + arg1; XCLIP(rrr)
            ggg = gg + arg1; XCLIP(ggg)
            bbb = bb + arg1; XCLIP(bbb)

            // Assemble
            ASSEM(xold, rrr, ggg, bbb)

            curr[offs + loop2] = xold;
            }
        }
    return Py_BuildValue("");
}


/// ----------------------------------------------------------------------

PyObject *_bw(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "startx", "starty","endx", "endy", NULL };

    int arg1 = 0;  int arg2 = 0; int arg3 = 0;  int arg4 = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iiii", kwlist, &arg1, &arg2, &arg3, &arg4))
            return NULL;

    if( is_verbose())
        printf("Black / White %d %d %d %d\n", arg1, arg2, arg3, arg4);

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
    int *curr = anchor, loop, loop2, avg = 0;

    avg = calc_avg();

    for (loop = 0; loop < dim1; loop++)
        {
        int offs = loop * dim2;

        for (loop2 = 0; loop2 < dim2; loop2++)
            {
            unsigned int ccc = curr[offs + loop2];
            int rr, gg, bb, xold, rrr, ggg, bbb;

            // Break apart:
            APART(ccc, rr, gg, bb)

            // Operate: add / clip
            rrr = rr + gg + bb; rrr /= 3;
            //printf("rr %d gg %d bb %d -- %d\n", rr,gg,bb, rrr);

            if (rrr > avg)
                rrr = ggg = bbb = 255;
            else
                rrr = ggg = bbb = 0;

            // Assemble:
            ASSEM(xold, rrr, ggg, bbb)
            curr[offs + loop2] = xold;
            }
        }
    return Py_BuildValue("");
}

/// ----------------------------------------------------------------------
// Reimplement skew free smooth. (did it for sound earlier)
// We create a new line buffer and output averages to it. Then we copy
// it back to the original line.

PyObject *_smooth(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "cycles", NULL };

    int arg1 = 1;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|i", kwlist, &arg1))
            return NULL;

    if( is_verbose() >  1)
        printf("Smooth factor: %d\n", arg1);

    if(!anchor)
        {
        PyErr_Format(PyExc_ValueError, "%s", "anchor must be set before any operation");
        return NULL;
        }
    if (arg1 < 0)
        {
        PyErr_Format(PyExc_ValueError, "%s", "argument(s) cannot be negative");
        return NULL;
        }
    if(reent)
        {
        PyErr_Format(PyExc_ValueError, "%s", "Cannot reenter");
        return NULL;
        }
    reent = 1;

    int *bline = malloc(dim1 * sizeof(int));
    if (!bline)
        {
        PyErr_Format(PyExc_ValueError, "%s", "Cannot alloc memory for temp line");
        return NULL;
        }

    int *curr = anchor, loop, loop2, loop3, xold;
    unsigned int ccc, prev, pprev, offs;

    //printf("sizeof(int) %d\n", sizeof(int) );

    for(loop3 = 0; loop3 < arg1; loop3++)           // Smooth Level
        {
        for (loop = 0; loop < dim2; loop++)        // yy
            {
            offs = loop * dim1;
            pprev = curr[offs];
            prev = curr[offs + 1];

            int rr, gg, bb, rrr, ggg, bbb, rrrr, gggg, bbbb, rr2, gg2, bb2;

            memset(bline, '\0', dim1 * sizeof(int));
            for (loop2 = 2; loop2 < dim1; loop2++) // xx
                {
                ccc = curr[offs + loop2];

                APART(ccc,  rr,   gg,   bb);
                APART(prev, rrr,  ggg,  bbb);
                APART(pprev, rrrr, gggg, bbbb);

                rr2 = (rr + rrr + rrrr) / 3;
                gg2 = (gg + ggg + gggg) / 3;
                bb2 = (bb + bbb + bbbb) / 3;

                ASSEM(xold, rr2, gg2, bb2);

                // Write back
                bline[loop2-1] = xold;

                pprev = prev; prev = ccc;
                }

            // Put line back
            memcpy(&curr[offs], bline, dim1 * sizeof(int));
            }
        }
    free(bline);
    reent = 0;
    return Py_BuildValue("");
}


// This is to prevent the macros from polluting the compilation screen

//pragma GCC diagnostic push
//pragma GCC diagnostic ignored "-Wunused-but-set-variable"

// -----------------------------------------------------------------------
#if 0

static int  smooth_line(int arg1, int arg2, int loop)

{
    int *curr = anchor, loop2, xold, offs =  arg2 * dim2;
    unsigned int prev = curr[offs + arg1], ccc;

    for (loop2 = arg1 + 1; loop2 < dim2; loop2++) // xx
        {
        int rr, gg, bb, rrr, ggg, bbb, rrrr, gggg, bbbb;
        ccc = curr[offs + loop2];

        APART(ccc, rr, gg, bb);
        APART(prev, rrr, ggg, bbb);

        rrrr = (rr + rrr) / 2;
        gggg = (gg + ggg) / 2;
        bbbb = (bb + bbb) / 2;

        ASSEM(xold, rrrr, gggg, bbbb);
        //printf("%d %d %d - %d %d %d = %d %d %d\n",
        //             rr, gg, bb, rrr,ggg,bbb,rrrr,gggg,bbbb);

        // Write back
        curr[offs + loop2 - 1] = xold;
        prev = ccc;
    }
    return 0;
}

#endif

//pragma GCC diagnostic pop

// --------------------------------------------------------------------

#define IDLE    0
#define LOW     1
#define HIGH    2

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"

// -----------------------------------------------------------------------

static  int  edge_line(int loop)

{
    int *curr = anchor, loop2;
    int state = IDLE;

    int offs = loop * dim1;
    unsigned int prev = curr[offs];

    for (loop2 = 1; loop2 < dim1; loop2++) // xx
        {
        int mark = NOMARK;
        int rr, gg, bb, rrr, ggg, bbb;
        unsigned int ccc = curr[offs + loop2];

        // Break apart:
        APART(ccc, rr, gg, bb); APART(prev, rrr, ggg, bbb)

        //printf("%d-%d-%d ", rr, gg, bb);
        // Edge detection:
        if (state == LOW)
            {
            if(rr > rrr)
                {
                state = HIGH;
                mark = DOT2;
                }
            }
        else if (state == HIGH)
            {
            if(rr < rrr)
                {
                state = LOW;
                mark = DOT;
                }
            }
        else if (state == IDLE)
            {
            if(rr < rrr)
                {
                state = LOW;
                mark = DOT2;
                }
            else
                {
                state = HIGH;
                mark = DOT;
                }
            }

        // Mark
        if (mark != NOMARK)
            {
            int xold, rrrr = 0, gggg = 000, bbbb = 0;
            ASSEM(xold, rrrr, gggg, bbbb)
            add_item(loop2, loop, xold, mark);
            //mark = NOMARK;
            }
        prev = ccc;
        }
    //printf("\n");
    return 0;
}

#pragma GCC diagnostic pop

//////////////////////////////////////////////////////////////////////////

PyObject *_edge(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "step",  NULL };

    int arg1 = 1;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|i", kwlist, &arg1))
            return NULL;

    if( is_verbose())
        printf("Edge: step= %d\n", arg1);

    if(!anchor)
        {
        PyErr_Format(PyExc_ValueError, "%s", "anchor must be set before any operation");
        return NULL;
        }
    if (arg1 < 0)
        {
        PyErr_Format(PyExc_ValueError, "%s", "argument(s) cannot be negative");
        return NULL;
        }
    if(reent)
        {
        PyErr_Format(PyExc_ValueError, "%s", "Cannot reenter");
        return NULL;
        }
    int loop, loop2;
    reent = 1;

    //avg = calc_avg();
    //printf("Average: %d\n", avg);

    // Scan lines
    for (loop = 0; loop < dim2; loop += 1) // yy
        {
        edge_line(loop);
        }
    #if 1
    // Blank image
    int *curr = anchor;
    for (loop = 0; loop < dim2; loop++)  // yy
        {
        int offs = loop * dim1;
        for (loop2 = 0; loop2 < dim1; loop2++)  //xx
             curr[offs + loop2]  = 0xfffffff;
        }
    //print_list();
    show_crosses();
    #endif

    reent = 0;
    return Py_BuildValue("");
}

// EOF
