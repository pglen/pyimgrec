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
        ret = (int)PyInt_AsLong(res);
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
        ret = PyInt_AsLong(res);
    return ret;
}

//# ------------------------------------------------------------------------
// Marker utilities


//# Draw a cross into the image

int cross(int xx, int yy, int xold)

{
    int *curr = anchor;
    int loop2 = xx, offs = yy * dim2;
                                       
    curr[offs + loop2 - 2 ] = xold;
    curr[offs + loop2 - 1 ] = xold;
    curr[offs + loop2]      = xold;           
    curr[offs + loop2 + 1 ] = xold;
    curr[offs + loop2 + 2 ] = xold;
    
    curr[offs + loop2 - dim2] = xold;           
    curr[offs + loop2 - 2 * dim2] = xold;           
    curr[offs + loop2 + dim2] = xold;           
    curr[offs + loop2 + 2 * dim2] = xold;           
    
    return 0;    
}

int xcross(int xx, int yy, int xold)

{
    int *curr = anchor;
    int loop2 = xx, offs = yy * dim2;
                                       
    curr[offs + loop2]      = xold;           
    
    curr[offs + loop2 -2 - 2 * dim2] = xold;           
    curr[offs + loop2 -2 + 2 * dim2] = xold;           
    
    curr[offs + loop2 +2 - 2 * dim2] = xold;           
    curr[offs + loop2 +2 + 2 * dim2] = xold;           
    
    return 0;    
}

//# Draw a small circle into the image

int circ(int xx, int yy, int xold)

{
    int *curr = anchor, loop2 = xx;
    int offs = yy * dim2;
    
    // LL, RR, UU, DD
    curr[offs + loop2 - 2 ] = xold;
    curr[offs + loop2 + 2 ] = xold;
    curr[offs + loop2 - 2 * dim2] = xold;           
    curr[offs + loop2 + 2 * dim2] = xold;           
    
    // UL, UR, LL, LR
    curr[offs + loop2 - 2 - 2 * dim2] = xold;           
    curr[offs + loop2 + 2 - 2 * dim2] = xold;           
    curr[offs + loop2 - 2 + 2 * dim2] = xold;           
    curr[offs + loop2 + 2 + 2 * dim2] = xold;           
    
    return 0;    
}

//# Draw a dot

int dot(int xx, int yy, int xold)

{
    int *curr = anchor, loop2 = xx;
    int offs = yy * dim2;
    
    curr[offs + loop2 ] = xold;
    
    return 0;    
}

//# Draw a bigger dot

int dot2(int xx, int yy, int xold)

{
    int *curr = anchor, loop2 = xx;
    int offs = yy * dim2;
    
    curr[offs + loop2 ] = xold;
    curr[offs + loop2 + 1 ] = xold;
    curr[offs + loop2 - 1 ] = xold;
    curr[offs + loop2 + dim2  ] = xold;
    curr[offs + loop2 - dim2  ] = xold;
    
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

void    print_list(void)

{
    struct _item *ptr = root;
    
    if (!ptr) {
        printf("Empty list\n"); return;
    }
        
    for(;;) {
        if (!ptr) break;
        printf("%d %d  ", ptr->xx, ptr->yy);
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
        else
            printf("Invalid shape in cross list\n");
            
        ptr = ptr->next;
    }
    dealloc();
}

// Calc avg

int calc_avg(void)

{
    int avg = 0, cnt = 0, *curr = anchor, loop, loop2;
    
    for (loop = 0; loop < dim1; loop++)
        {
        int offs = loop * dim2;
        
        for (loop2 = 0; loop2 < dim2; loop2++)
            {
            unsigned int ccc = curr[offs + loop2];
            int rr, gg, bb, xold;
            
            // Break color apart:
            APART(ccc, rr, gg, bb)
            xold = rr + gg + bb; xold /= 3;
            avg += xold; cnt += 1;
            }
        }
    return avg / cnt;    
}


