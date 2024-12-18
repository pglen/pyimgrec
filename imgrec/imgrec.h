// -----------------------------------------------------------------------
// Image recognition module. Local header.


// Vars and funcs shared between modules

#define MAX(aa,bb) ((aa) > (bb) ? (aa) : (bb))

extern int *anchor;
extern int  reent;
extern long dim1, dim2, dim3;
extern PyObject *module;

// Flood

PyObject *_flood(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_average(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_seek(PyObject *self, PyObject *args, PyObject *kwargs);

// Lines:

PyObject *_frame(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_poly(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_line(PyObject *self, PyObject *args, PyObject *kwargs);

// Squares:

PyObject *_median(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_whiten(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_median(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_blank(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_greyen(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_medianmulti(PyObject *self, PyObject *args, PyObject *kwargs);

// Colors:

PyObject *_diffcol(PyObject *self, PyObject *args, PyObject *kwargs);

// Norm

PyObject *_norm(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_histo(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_bw(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_bridar(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_walk(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_edge(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_smooth(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject *_smoothv(PyObject *self, PyObject *args, PyObject *kwargs);

//# EOF
