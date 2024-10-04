// -----------------------------------------------------------------------
// Image recognition module. Line primitives.

#include <Python.h>
//#include <pygobject.h>

#include <math.h>
#include "imgrec.h"

//#define MAX(aa, bb) (aa) > (bb) ? aa : bb

static int sqr(int aa)
    {
    return aa * aa;
    }
    
// -----------------------------------------------------------------------
// diffcol(col1, col2) - diff color
// Return [cd, diff, xdiff] 
// cd=color difference as RGB, diff = sqrt(sqr(r)+sqr(b)+sqr(g)) xdiff = max3(r,g,b)

PyObject *_diffcol(PyObject *self, PyObject *args, PyObject *kwargs)

{
    static char *kwlist[] = { "color1", "color2",  NULL };
    
    int arg1 = 0;  int arg2 = 0; 
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "II", kwlist, &arg1, &arg2))
            return NULL;
    
    if( is_verbose())
        printf("Sub Color %x %x\n", arg1, arg2);
    
    // Break apart
    int rr = arg1 & 0xff; int gg = (arg1>>8) & 0xff; 
    int bb = (arg1>>16) & 0xff;
    
    int rrr = arg2 & 0xff; int ggg = (arg2>>8) & 0xff; 
    int bbb = (arg2>>16) & 0xff;
     
    int rrrr = abs(rr - rrr);
    int gggg = abs(gg - ggg);
    int bbbb = abs(bb - bbb);
     
    // Assemble
    int xold = 0xff; xold <<= 8; xold |= bbbb; xold <<= 8; 
    xold |= gggg; xold <<= 8; xold |= rrrr; 

    // Sum up
    int xsin = sqr(rrrr) + sqr(gggg) + sqr(bbbb);  xsin = sqrt(xsin);
    int xmax = MAX(bbbb, gggg); xmax = MAX(xmax, rrrr);
    
    if( is_verbose())
        printf("Sub Color ret %x %x %x\n", xold, xsin, xmax);
        
    return Py_BuildValue("Iii", xold, xsin, xmax);
}    

// -----------------------------------------------------------------------
//   diffcol(col1, col2) - diff color

PyObject *_diffmulcol(PyObject *self, PyObject *args, PyObject *kwargs)

{
    static char *kwlist[] = { "color1", "color2",  NULL };
    
    int arg1 = 0;  int arg2 = 0; 
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "II", kwlist, &arg1, &arg2))
            return NULL;
    
    if( is_verbose())
        printf("Sub Color %x %x\n", arg1, arg2);
    
    // Break apart
    int rr = arg1 & 0xff; int gg = (arg1>>8) & 0xff; 
    int bb = (arg1>>16) & 0xff;
    
    int rrr = arg2 & 0xff; int ggg = (arg2>>8) & 0xff; 
    int bbb = (arg2>>16) & 0xff;
     
    int rrrr = abs(rr - rrr);
    int gggg = abs(gg - ggg);
    int bbbb = abs(bb - bbb);
     
    // Assemble
    int xold = 0xff; xold <<= 8; xold |= bbbb; xold <<= 8; 
    xold |= gggg; xold <<= 8; xold |= rrrr; 

    // Sum up
    int xsin = sqr(rrrr) + sqr(gggg) + sqr(bbbb);  xsin = sqrt(xsin);

        int xmax = MAX(bbbb, gggg); xmax = MAX(xmax, rrrr);
    
    if( is_verbose())
        printf("Sub Color ret %x %x %x\n", xold, xsin, xmax);
        
    return Py_BuildValue("Iii", xold, xsin, xmax);
}    








