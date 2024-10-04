// -----------------------------------------------------------------------
// Image recognition module. Local utility header.
                 
// -----------------------------------------------------------------------
//# Macros for assembling / dissasembling RGBA colors

//# Construct it into a var

#define RGB(xrr, xgg, xbb)         \
            ( ((( (0xff << 8) | xbb) << 8 | xgg) << 8) | xrr)

#define xRGB(var, xrr, xgg, xbb)         \
            var = 0xff;  var <<= 8;     \
            var |= xbb;  var <<= 8;     \
            var |= xgg;  var <<= 8;     \
            var |= xrr; 

#define RGBA(xaa, xrr, xgg, xbb)         \
            ( ((( (xaa << 8) | xbb) << 8 | xgg) << 8) | xrr)

#define xRGBA(var, axx, xrr, xgg, xbb)   \
            var = axx;  var <<= 8;      \
            var |= xbb;  var <<= 8;     \
            var |= xgg;  var <<= 8;     \
            var |= xrr; 
            
//# Break components from var into a set of vars

#define APART(var, rrx, ggx, bbx)       \
            rrx = (var) & 0xff;         \
            ggx = (var >> 8) & 0xff;    \
            bbx = (var >> 16) & 0xff;
            
//# Construct it from vars into a var

#define ASSEM(var, rrx, ggx, bbx)       \
            var = 0xff; var <<= 8;      \
            var |= bbx; var <<= 8;      \
            var |= ggx; var <<= 8;      \
            var |= rrx; 

//# Macros for clipping color values (clip - up, down, both)

#define CLIP(ccx) if(ccx > 255) ccx = 255;
#define DCLIP(ccx) if(ccx < 0)  ccx = 0;
    
#define XCLIP(ccx)  if(ccx < 0) ccx = 0;     \
                    if(ccx > 255) ccx = 255;


// Funcs shared between modules

// Utils:

int get_int(char *name);
int set_int(char *name, int val);
int is_verbose(void);

//# ------------------------------------------------------------------------
// Marker utilities

#define NOMARK  0
#define CROSS   1
#define CIRC    2
#define XCROSS  3
#define DOT     4
#define DOT2    5

int cross(int xx, int yy, int xold);
int xcross(int xx, int yy, int xold);
int circ(int xx, int yy, int xold);
int dot(int xx, int yy, int xold);
int dot2(int xx, int yy, int xold);

void    add_item(int xx, int yy, int cc, int shape);
void    print_list(void);
void    show_crosses(void);

int calc_avg(void);









