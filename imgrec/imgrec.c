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

//static  long anclen = 0;            // Length of buffer in bytes
//static  Py_ssize_t anclen = 0;      // Length of buffer in bytes

// -----------------------------------------------------------------------
// Anchor object is set here, nothing will function without it
// This assumes one image under the lens of the recognizer (global)

static PyObject *_anchor(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "ptr", "shape", NULL };
    PyObject *anc = 0, *sss = 0;

    //PyObject_Print(kwargs, stdout, 0);
    //printf("\n");
    //PyObject_Print(args, stdout, 0);
    //printf("\n");

    //printf("args = %s len=%ld \n", (char*)PyObject_Str(args), PyObject_Size(args));
    //printf("%24s len=%d ", (char*)
    //PyObject_Str(kwargs), PyObject_Size(kwargs));

    //printf("args: (%x) kwargs: (%x) STDOUT %x\n", args, kwargs, stdout);

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO", kwlist, &anc, &sss))
        return NULL;

    //PyObject_Print(anc, stdout, 0);
    //printf(" was: anc\n");
    //PyObject_Print(sss, stdout, 0);
    //printf("was; sss\n");

    Py_buffer *py_buffer = PyMemoryView_GET_BUFFER(anc);
    //printf(" pymem %p len=%ld ndim=%d\n",
    //                    py_buffer->buf, py_buffer->len, py_buffer->ndim);
    //Py_ssize_t *sxx  = py_buffer->shape;
    //printf(" %ld was shape\n", *sxx);
    //PyObject_Print(sxx, stdout, 0);
    //printf("check %d\n", PyTuple_Check(sxx));

    if (!PyTuple_Check(sss))
        {
        PyErr_Format(PyExc_TypeError, "%s", "expected tuple");
        return NULL;
        }
    if (PyTuple_GET_SIZE(sss) != 3)
        {
        //printf("shape dim must be 3");
        PyErr_Format(PyExc_ValueError, "%s", "shape dims must be 3");
        return NULL;
        }

    PyObject *d1 = PyTuple_GetItem(sss, 0);
    dim1 = PyLong_AsLong(d1);
    PyObject_SetAttrString(module, "dim1", Py_BuildValue("i", dim1));
    PyObject_SetAttrString(module, "height", Py_BuildValue("i", dim1));

    PyObject *d2 = PyTuple_GetItem(sss, 1);
    dim2 = PyLong_AsLong(d2);
    PyObject_SetAttrString(module, "dim2",  Py_BuildValue("i", dim2));
    PyObject_SetAttrString(module, "width", Py_BuildValue("i", dim2));

    PyObject *d3 = PyTuple_GetItem(sss, 2);
    dim3 = PyLong_AsLong(d3);
    PyObject_SetAttrString(module, "dim3", Py_BuildValue("i", dim3));

    anchor = py_buffer->buf;

    if (is_verbose() > 2)
        printf("imgrec anchor: %p dims: %ld %ld %ld\n", anchor, dim1, dim2, dim3);

    // Sanity check if buffer length correct
    if(dim1 * dim2 * dim3 != py_buffer->len)
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

static struct PyModuleDef Combinations =
{
    PyModuleDef_HEAD_INIT,
    "imgrec", /* name of module */
    "usage: imagrec\n", /* module documentation, may be NULL */
    -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    imgrec_functions
};

//DL_EXPORT(void)
PyMODINIT_FUNC PyInit_imgrec(void)
{
    //init_pygobject ();
    //module = Py_InitModule3("imgrec", imgrec_functions, "Image Recognition library for Python");
    //d = PyModule_GetDict (module);

    module = PyModule_Create(&Combinations);

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
    return module;
}

// EOF
