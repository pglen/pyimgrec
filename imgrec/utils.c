// -----------------------------------------------------------------------
// Image recognition module. Misc. utilities.

#include <Python.h>
//#include <pygobject.h>

#include "imgrec.h"
#include "utils.h"

// -----------------------------------------------------------------------
// Get module property value

int get_int(char *name)

{
    int ret = 0;
    PyObject *res = PyObject_GetAttrString(module, name);
    if(res)
        ret = (int)PyLong_AsLong(res);
    return ret;
}

// Set module property value

int set_int(char *name, int val)

{
    int ret = PyObject_SetAttrString(module, name,  Py_BuildValue("i", val));
    return ret;
}

// Return verbose flag / level

int is_verbose(void)

{
    int ret = 0;
    PyObject *res = PyObject_GetAttrString(module, "verbose");
    if(res)
        ret = PyLong_AsLong(res);
    return ret;
}

//# ------------------------------------------------------------------------
// Marker utilities


//# Draw a cross into the image

int cross(int xx, int yy, int xold)

{
    int *curr = anchor;
    int loop2 = xx, offs = yy * dim1;

    //curr[offs + loop2] = 0xffff0000;

    curr[offs + loop2 - 2 ] = xold;
    curr[offs + loop2 - 1 ] = xold;
    curr[offs + loop2]      = xold;
    curr[offs + loop2 + 1 ] = xold;
    curr[offs + loop2 + 2 ] = xold;

    curr[offs + loop2 - dim1] = xold;
    curr[offs + loop2 - 2 * dim1] = xold;
    curr[offs + loop2 + dim1] = xold;
    curr[offs + loop2 + 2 * dim1] = xold;

    return 0;
}

int xcross(int xx, int yy, int xold)

{
    int *curr = anchor;
    int loop2 = xx;
    int offs = yy * dim1;
    //printf("dim1 %ld\n", dim1);

    curr[offs + loop2] =    xold;

    curr[offs + loop2 - 2 - 2 * dim1] = xold;
    curr[offs + loop2 - 2 + 2 * dim1] = xold;
    curr[offs + loop2 - 3 - 3 * dim1] = xold;
    curr[offs + loop2 - 3 + 3 * dim1] = xold;

    curr[offs + loop2 + 2 - 2 * dim1] = xold;
    curr[offs + loop2 + 2 + 2 * dim1] = xold;
    curr[offs + loop2 + 3 - 3 * dim1] = xold;
    curr[offs + loop2 + 3 + 3 * dim1] = xold;

    return 0;
}

//# Draw a small circle into the image

int circ(int xx, int yy, int xold)

{
    int *curr = anchor, loop2 = xx;
    int offs = yy * dim1;

    // LL, RR, UU, DD
    curr[offs + loop2 - 2 ] = xold;
    curr[offs + loop2 + 2 ] = xold;
    curr[offs + loop2 - 2 * dim1] = xold;
    curr[offs + loop2 + 2 * dim1] = xold;

    // UL, UR, LL, LR
    curr[offs + loop2 - 2 - 2 * dim1] = xold;
    curr[offs + loop2 + 2 - 2 * dim1] = xold;
    curr[offs + loop2 - 2 + 2 * dim1] = xold;
    curr[offs + loop2 + 2 + 2 * dim1] = xold;

    return 0;
}

//# Draw a dot

int dot(int xx, int yy, int xold)

{
    int *curr = anchor, loop2 = xx;
    int offs = yy * dim1;
    curr[offs + loop2 ] = xold;
    return 0;
}

//# Draw a different dot

int dot2(int xx, int yy, int xold)

{
    int *curr = anchor, loop2 = xx;
    int offs = yy * dim1;

    //curr[offs + loop2 ] = 0xf0000ff;

    curr[offs + loop2 ] = xold;
    curr[offs + loop2 + 1 ] = xold;
    curr[offs + loop2 - 1 ] = xold;
    curr[offs + loop2 + dim1  ] = xold;
    curr[offs + loop2 - dim1  ] = xold;
    return 0;
}

// -----------------------------------------------------------------------
// A doubly linked list for storing crosses. This was needed as we
// did not want to pollute the screen while processing.

struct _item
    {
    struct _item *next, *prev;
    int xx, yy, cc, shape;
    };

struct _item *root = 0;

void    add_item(int xx, int yy, int cc, int shape)

{
    //printf("add_item: %d %d %x %d\n", xx, yy, cc, shape);

    struct _item *ptr = malloc(sizeof(struct _item));
    if (!ptr)
        {
        printf("Malloc error\n");
        return;
        }
    memset(ptr, 0, sizeof(struct _item) );
    ptr->xx = xx;   ptr->yy = yy;
    ptr->cc = cc;   ptr->shape = shape;

    if(!root)
        {
        root = ptr;
        }
    else
        {
        ptr->next = root;
        root = ptr;
        }
}

// ff 00 00 00

void    print_list(void)

{
    struct _item *ptr = root;

    if (!ptr) {
        printf("Empty list\n"); return;
    }

    for(;;) {
        if (!ptr) break;
        printf("%d -- %d %d %x\n", ptr->shape, ptr->xx, ptr->yy, ptr->cc);
        ptr = ptr->next;
    }
    printf("\n");
}

void    dealloc(void)

{
    struct _item *ptr = root, *old_ptr = NULL;

    if (!ptr) {
        return;
    }
    for(;;) {
        if (!ptr) break;
        old_ptr = ptr;
        ptr = ptr->next;
        free(old_ptr);
    }
    root = NULL;
}

void    show_crosses(void)
{
    struct _item *ptr = root;

    if (!ptr) {
        printf("Empty cross list\n"); return;
    }
    for(;;) {
        if (!ptr) break;

        //printf("show_item: %d %d %x %d\n", ptr->xx, ptr->yy, ptr->cc, ptr->shape);

        if(ptr->shape == CROSS)
            cross(ptr->xx, ptr->yy, ptr->cc);
        else if(ptr->shape == XCROSS)
            xcross(ptr->xx, ptr->yy, ptr->cc);
        else if(ptr->shape == CIRC)
            circ(ptr->xx, ptr->yy, ptr->cc);
        else if(ptr->shape == DOT)
            dot(ptr->xx, ptr->yy, ptr->cc);
        else if(ptr->shape == DOT2)
            dot2(ptr->xx, ptr->yy, ptr->cc);
        //else
        //    printf("Invalid shape in cross list\n");

        ptr = ptr->next;
    }
    dealloc();
}

// Get int from class

int intfromclass(PyObject *classx, const char *method)

{
    PyObject *namex = PyObject_GetAttr(classx,
                                    Py_BuildValue("s", method));
    if (!namex)
        {
        printf("Warn: no such method %s", method);
        return -1;
        }
    int ret = (int) PyLong_AsLong(namex);
    //printf(" %d\n", ret);
    return ret;
}

// EOF
