#!/usr/bin/env python

import math
import pyimgutils as iut

__doc__ = '''

  Process and shape image boundary data vectors. Misc routines to
  shape / normalize / sort compare arrays.
  The initial attempt was to convert them by sorting on rotational vector.
  However, the simple sort is just fine.

'''

#: This is the sample size that is stored in the shape array
ARRLEN = 100

def norm_array(fparm):

    '''
        Process the array for vector rotation. Return normalized coordinate array.
        This is superseeded by simple sorting, with similar results.
    '''

    resarr = [];

    # Correct order
    minx2 = min(fparm.minx, fparm.maxx);  miny2 = min(fparm.miny, fparm.maxy)
    maxx2 = max(fparm.minx, fparm.maxx);  maxy2 = max(fparm.miny, fparm.maxy)
    #print( "minx2", minx2, "maxx2", maxx2, "miny2", miny2, "maxy2", maxy2)
    maxwx = maxx2 - minx2; maxhy = maxy2 - miny2

    midx = maxwx // 2; midy = maxhy // 2;
    #print( "midx", midx, "midy", midy       )

    # Normalize to zero based for the small image, clean non zeros
    xarr = flush_upleft(fparm)

    #xsarr = sorted(xarr.keys())
    #xsarr = xarr.keys();

    # Quadrants. Visualizer tells us to parse in clock winding order.
    # Starting from upper left ...
    #     xx  yy      |-----|-----|
    #     -1, -1      |  1  |  2  |
    #     +1, -1      |-----|-----|
    #     +1, +1      |  4  |  3  |
    #     -1, +1      |-----|-----|

    carr1 = {}; carr2 = {};  carr3 = {};  carr4 = {}
    for bb in xarr:
        # Normalize it to the center
        # minx  ----  midx ----  maxx
        if bb[0] > midx: xx = bb[0] - midx;
        else: xx = - (midx - bb[0])
        if bb[1] > midy: yy = bb[1] - midy;
        else: yy = - (midy - bb[1])
        #print("xx", xx, "yy", yy)

        # Distribute quadrants
        if (xx <= 0) and (yy <= 0):   carr1[xx, yy] = 1
        elif (xx > 0) and (yy <= 0):  carr2[xx, yy] = 1
        elif (xx > 0) and (yy > 0):   carr3[xx, yy] = 1
        elif (xx <= 0) and (yy > 0):  carr4[xx, yy] = 1
        #else: print( "Bad juju")
        #print("carr1", carr1)

    # Sort them by angle
    resarr += order_vectors(carr1, midx, midy)
    resarr += order_vectors(carr2, midx, midy)
    resarr += order_vectors(carr3, midx, midy)
    resarr += order_vectors(carr4, midx, midy)
    #print( "shape arr len", len(resarr))
    #return resarr

    # Shape them uniform, number of elements, maximum magnitude
    resarr2 = scale_vectors(resarr, ARRLEN)
    #return resarr2
    resarr3 = scale_magnitude(resarr2, ARRLEN)
    return resarr3

def norm_vectors(vects, minx, miny, size = ARRLEN):

    ''' Call subsequent norm / scale routines '''

    ulf = flush_upleft(vects, minx, miny)
    nbs = scale_vectors(ulf, size)
    nbm = scale_magnitude(nbs, size)
    return nbm

def flush_upleft(vects, minx = 0, miny = 0):

    ''' Make sure vector origin at 0,0 (minx, miny)

    Parameters
    ----------

        vects           vectors to operate on
        minx, miny      flush reference point

    '''

    xarr = []
    for aa in vects:
        xarr.append(([aa[0] - minx, aa[1] - miny]))
    return xarr

def order_vectors(carr, midx, midy, rev = False):

    ''' Order vectors. Calculate vector tangent and sort by it.
        Obsolete. Kept because it may be useful in the future.
    '''

    vec = []; resarr = []
    for cc in carr.keys():
        if cc[0]:                           # prevent divide by zero
            vvv = float(cc[1]) / cc[0]
            vec.append((vvv, cc))
    vec.sort()
    for dd in vec:
        resarr.append((dd[1][0] + midx, dd[1][1] + midy))
    return resarr

def scale_vectors(carr, newsize):

    ''' Scale array to preset lenth. Discards the rest, or duplicates
    dependent on the array size and parameter newsize
    '''

    resarr = []; arrlen = len(carr)
    step = float(arrlen) / newsize
    for aa in range(newsize):
        try:
            resarr.append(carr[int(aa * step)] )
        except:
            print("exc scale", aa, arrlen) #, sys.exc_info())
    return resarr

def scale_magnitude(carr, newval):

    ''' Scale array to preset value range. Note that the value has
        to be index ARRLEN, which is one less than ARRLEN.
    '''

    resarr = [];  maxval = 0;
    # Calculate maximum value
    for aa in carr:
        maxval = max(maxval, aa[0]);
        maxval = max(maxval, aa[1])

    rat = float(maxval) / (newval - 1)
    #print( "maxval", maxval, "rat", rat, "len", len(carr))

    # Scale it
    for aa in range(len(carr)):
        xx = float(carr[aa][0]) / rat;  yy = float(carr[aa][1]) / rat
        resarr.append( (int(math.floor(xx)), int(math.floor(yy))) )
    #print("resarr", resarr)
    return resarr

def cmp_arrays(arr1, arr2, span = 3):

    ''' Compare two arrays, look sideways for closer match

        Parameters:  <br>

            arr1, arr2      arrays to compare
            span            how musch to look sideways
    '''

    xlen = min(len(arr1), len(arr2))
    if xlen < span + 2:
        print("Array not long enough")
        return

    ret = 0;
    for aa in range(span, xlen - (span+1)):
        ref = arr1[aa][0]; ref2 = arr1[aa][1]
        inter = 0xffff
        for bb in range(-span, span+1):
            xx1 = abs(ref - arr2[aa+bb][0])
            yy1 = abs(ref2 - arr2[aa+bb][1])
            #dd = math.sqrt(xx1 * xx1 + yy1 * yy1)
            dd = abs(xx1 + yy1)
            #print("eval %d %.2f " % (bb, dd), xx1, yy1)
            inter = min(dd, inter)
        ret += inter
    return int(ret)

def cmp_arrays2(arr1, arr2):

    ''' Compare two arrays, old version (never mind) '''

    ret = 0; xlen = min(len(arr1), len(arr2))
    for aa in range(1, xlen - 1):

        dd1 = arr1[aa][0] - arr2[aa-1][0]
        dd2 = arr1[aa][1] - arr2[aa-1][1]
        dd = math.sqrt(dd1 * dd1 + dd2 * dd2)

        ddd1 = arr1[aa][0] - arr2[aa][0]
        ddd2 = arr1[aa][1] - arr2[aa][1]
        ddd = math.sqrt(ddd1 * ddd1 + ddd2 * ddd2)

        dddd1 = arr1[aa+1][0] - arr2[aa+1][0]
        dddd2 = arr1[aa+1][1] - arr2[aa+1][1]
        dddd = math.sqrt(dddd1 * dddd1 + dddd2 * dddd2)

        inter = min(dd, ddd)
        ret += min(inter, dddd)

    return ret

def norm_array2(fparm):

    ''' Process the array for vector proximity (old)
    '''

    resarr = [];

    minx = fparm.minx;  miny = fparm.miny
    maxx = fparm.maxx - fparm.minx;
    maxy = fparm.maxy - fparm.miny

    #print( fparm.bounds)

    # Normalize to zero based for the small image, clean non zeros
    xarr = {}
    for aa in fparm.bounds.keys():
        if fparm.bounds[aa]:
            xarr[aa[0] - minx, aa[1] - miny] = 1
    #print( xarr    )

    # This will yield top left point as element 0
    xsarr = sorted(xarr.keys())
    #print( xsarr)
    #return xsarr

    # Assure winding. Look for closest right, then up, then down, then left
    progarr = []; prog = 0
    while True:
        if len(progarr) >= len(xsarr) - 1: break      # End cycle
        progarr.append(prog)                          # Mark point done
        curr =  xsarr[prog]; warr = []
        #print( "curr", curr, "prog", prog, "wlen", len(xsarr), )

        for cc in range(0, len(xsarr)):
            if cc == prog:                          # Self
                continue
            if cc in progarr:                       # Visited
                continue
            dist = sqrdiff(xsarr[cc][0] - curr[0], xsarr[cc][1] - curr[1])
            if dist !=  0:                  # Exclude self
                #print( xsarr[cc], "%.2d" % dist, "  ",)
                warr.append((dist, cc))

        if len(warr) > 1:                      # The end pos has no connection
            warr.sort(key=lambda val: val[0])  # Get the smallest distance
            #warr.sort()
            #print( "warr", warr)
            collision = warr[0][0] == warr[1][0]
            # After long delibaration, the simplest way to handle this is
            # to ignore collisions
            if collision:
                print( "warr collision", warr[0], warr[1])
                for dd in range(len(warr) - 1):
                    print( warr[dd], xsarr[warr[dd][1]] )
                    if warr[dd][0] != warr[dd+1][0]:
                        break
            else:
                resarr.append((xsarr[prog][0], xsarr[prog][1]))
                # Now go to the last found, repeat
            prog =  warr[0][1]
        #print()
    return resarr

def sqrdiff(aa, bb):

    ''' Math sugar for absolute difference. Not used, as it is too expensive. '''

    dist = math.sqrt(abs(math.pow(bb, 2) - \
                math.pow(aa, 2)))
    return dist

def norm_bounds(boundx, bounds):

    ''' Make it upper left aligned '''

    print("norm_bounds() boundx = ", boundx)
    retdict = {}
    for aa in bounds.keys():
        if bounds[aa]:
            iut.mark_cell(aa[0] - boundx[0], aa[1] - boundx[1],  1, retdict)
    return retdict

# EOF
