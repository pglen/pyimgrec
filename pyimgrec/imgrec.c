// -----------------------------------------------------------------------
// Image recognition module. The 'c' module is 2000 times faster than
// the 'py' version. See blank function for timings.
//
// Usage:   Feed an anchor array (pointer to buffer, dim1, dim2, dim3) 
//          then call appropriate function(s).
//
// Functions:
//
//   anchor(arr)                    - associate image arr
//   blank(x, y, x2, y2, color)     - blank rect with color
//   grayen(x, y, x2, y2, addcolor) - blank rect with color
//   whiten(x, y, x2, y2, subcolor) - blank rect with color
//   frame(x, y, x2, y2, color)     - draw frame with color
//   line(x, y, x2, y2, color)      - draw line with color
//
// ColorSpec:   32 bit, 0xAABBGGRR
//              AA = Alpha ; BB = Blue ; GG = Green ; RR = Red 
//              In the range of  0 - 255 (0x0 - 0xff)
//
// Grayen / Whiten addcolor/subcolor spec:  
//              0 - 255  (0x0 - 0xff)
//
// Coordinates:
//              x  = start x-axis ; y  = start y-axis 
//              x2 = end x-axis   ; y2 = end y-axis
//
//      o Coordinates are checked for out of bounds
//

#include <Python.h> 

#include "imgrec.h"
#include "bdate.h"
#include "utils.h"

#define OPEN_IMAGE 1
 
// -----------------------------------------------------------------------
// Vars:

int *anchor = NULL;                 //
long dim1 = 0, dim2 = 0, dim3 = 0;  // Replaced by python props
PyObject *module;                   // This is us

int     reent = 0;                  // Stupid sanity check
static  char version[] = "1.0";     // Can be queried
static  int anclen = 0;             // Length of buffer in bytes

//static  Py_ssize_t anclen = 0;      // Length of buffer in bytes

// -----------------------------------------------------------------------
// Anchor object is set here, nothing will function without it
// This assumes one image under the lens of the recognizer (global)

static PyObject *_anchor(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "imgarr", NULL };
    PyObject *anc = 0;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &anc))
        return NULL;

    char *pname = "shape";
    if (PyObject_HasAttrString(anc, pname))
        {
        PyObject *res2 = PyObject_GetAttrString(anc, pname);
        if (PyTuple_Check(res2))
            {
            if (PyTuple_GET_SIZE(res2) == 3)
                {                    
                PyObject *d1 = PyTuple_GetItem(res2, 0);
                dim1 = PyInt_AsLong(d1);
                PyObject_SetAttrString(module, "dim1", Py_BuildValue("i", dim1));
                PyObject_SetAttrString(module, "height", Py_BuildValue("i", dim1));
                
                PyObject *d2 = PyTuple_GetItem(res2, 1);
                dim2 = PyInt_AsLong(d2);
                PyObject_SetAttrString(module, "dim2",  Py_BuildValue("i", dim2));
                PyObject_SetAttrString(module, "width", Py_BuildValue("i", dim2));
                
                PyObject *d3 = PyTuple_GetItem(res2, 2);
                dim3 = PyInt_AsLong(d3);
                PyObject_SetAttrString(module, "dim3", Py_BuildValue("i", dim3));
                }
           else {                                
                //printf("shape dim must be 3");
                PyErr_Format(PyExc_ValueError, "%s", "shape dim must be 3");
                return NULL;
                }
            }
        else
            {
            //printf("shape must be tuple");
            PyErr_Format(PyExc_ValueError, "%s", "shape must be tuple");
            return NULL;
            }
        }
    else
        {
        //printf("must have shape attr");
        PyErr_Format(PyExc_ValueError, "%s", "argument must have shape property (like: arr)");
        return NULL;
        }
    
    //printf("_anchor %p %d %p\n", anc, res, res2); 
                        
    // Cast it, so int * - s will not complain                        
    int ret3 = PyObject_AsWriteBuffer(anc, (void**)&anchor, (Py_ssize_t*)&anclen);
    if(ret3 < 0)
        {
        //printf("Cannot get pointer to buffer");
        PyErr_Format(PyExc_ValueError, "%s", "Cannot get pointer to buffer");
        return NULL;
        }
  
    if(is_verbose())
        printf("Anchor Dimensions: ww=%ld hh=%ld dd=%ld Pointer: %p\n", 
                dim2, dim1, dim3, anchor);
        
    // Sanity check
    if(dim1*dim2*dim3 != anclen)
        {
        PyErr_Format(PyExc_ValueError, "%s", "Buffer len != dim[1]*dim[2]*dim[3]");
        return NULL;
        }
        
    //printf("ret3 %d buff %p len %d\n", ret3, anchor, anclen);
    //printf("*buff %s", (char*)buff); printf("\n");
    
    return Py_BuildValue("");
}

static PyObject *_bdate(PyObject *self, PyObject *args, PyObject *kwargs)
{
  return Py_BuildValue("s", bdate);
}
  
static PyObject *_version(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return Py_BuildValue("s", version);
}

char blankdoc[] = "Blank part of an image. Args: startx, starty, endx, endy.";

PyMethodDef imgrec_functions[] = 
    {
    
    { "version",   (PyCFunction)_version, METH_VARARGS|METH_KEYWORDS, "Image recognition version."},
    { "builddate", (PyCFunction)_bdate,   METH_VARARGS|METH_KEYWORDS, "Image recognition build date."},
    { "anchor",    (PyCFunction)_anchor,  METH_VARARGS|METH_KEYWORDS, "Set anchor to image."},
    { "blank",     (PyCFunction)_blank,   METH_VARARGS|METH_KEYWORDS,  blankdoc },
    { "median",    (PyCFunction)_median,  METH_VARARGS|METH_KEYWORDS,  "Calculate median of range." },
    { "medianmulti",(PyCFunction)_medianmulti,  METH_VARARGS|METH_KEYWORDS,  
                                                        "Calculate median of range, multiple colors" },
    { "grayen",    (PyCFunction)_grayen,  METH_VARARGS|METH_KEYWORDS,  "Grayen range." },
    { "whiten",    (PyCFunction)_whiten,  METH_VARARGS|METH_KEYWORDS,  "Whiten range." },
    { "frame",     (PyCFunction)_frame,   METH_VARARGS|METH_KEYWORDS,  "Frame range." },
    { "line",      (PyCFunction)_line,    METH_VARARGS|METH_KEYWORDS,  "Draw a line." },
    { "poly",      (PyCFunction)_poly,    METH_VARARGS|METH_KEYWORDS,  "Draw a poly line." },
    { "diffcol",   (PyCFunction)_diffcol, METH_VARARGS|METH_KEYWORDS,  "Diff two colors" },
    { "diffmulcol",(PyCFunction)_diffcol, METH_VARARGS|METH_KEYWORDS,  "Diff multiple colors" },
    
    { "normalize", (PyCFunction)_norm,    METH_VARARGS|METH_KEYWORDS,  "Normalize image" },
    { "bridar",    (PyCFunction)_bridar,  METH_VARARGS|METH_KEYWORDS,  "Brighten / Darken" },
    { "bw",        (PyCFunction)_bw,      METH_VARARGS|METH_KEYWORDS,  "Convert to B/W" },
    { "walk",      (PyCFunction)_walk,    METH_VARARGS|METH_KEYWORDS,  "Walk on equiline" },
    { "edge",      (PyCFunction)_edge,    METH_VARARGS|METH_KEYWORDS,  "Edge out ridge lines" },
    { "smooth",    (PyCFunction)_smooth,  METH_VARARGS|METH_KEYWORDS,  "Smooth image" },
    
    {  NULL },
    };

// -----------------------------------------------------------------------
// Init:

DL_EXPORT(void) 
initimgrec(void)
{
 
    //init_pygobject ();

    module = Py_InitModule3("imgrec", imgrec_functions, "Image Recognition library for Python");
    //d = PyModule_GetDict (module);
    
    // Constants
    PyModule_AddIntConstant(module, (char *)"OPEN_IMAGE", OPEN_IMAGE);
    PyModule_AddStringConstant(module, (char *)"author", "Peter Glen");

    // Values:
    PyModule_AddObject(module, "verbose",   Py_BuildValue("i", 0));
    PyModule_AddObject(module, "dim1",      Py_BuildValue("i", 0));
    PyModule_AddObject(module, "dim2",      Py_BuildValue("i", 0));
    PyModule_AddObject(module, "dim3",      Py_BuildValue("i", 0));

    PyModule_AddObject(module, "height",    Py_BuildValue("i", 0));
    PyModule_AddObject(module, "width",     Py_BuildValue("i", 0));

    if (PyErr_Occurred ()) {       
	   Py_FatalError ("can't initialise imgrec module");
    }
}





