#!/usr/bin/env python

import  os, sys, getopt, signal, array, random, math, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from  pyimgutils import *
import  stack

import imgrec.imgrec as imgrec

__doc__ = \
'''
    The flood routines use a local and global 'done' list.
    It is kept procedural (no class) in anticipation of converting it
    to a 'C'  module.
    The local list is copied to global at the end of every scan.
'''
# Results of compare, and more enums
dot_strs = ("DOT_NO", "DOT_YES", "DOT_BOUND", "DOT_MARK",
                    "DOT_POP", "DOT_INVALIDATE")
# Create enums
create_enums(dot_strs, locals())

# Verify enums
#for aaa in dot_strs:
#    print("%s=%d" % (aaa, locals().get(aaa)), end = " ")
#print()
#print("verify:", DOT_NO, DOT_YES, DOT_BOUND)
#print("enums:", DOT_MARK, DOT_POP, DOT_INVALIDATE)

gl_reenter = 0

# Scanning order for xxx, yyy at: R B L A
scan_ops = ((1,0), (0,1), (-1,0), (0,-1))
scan_idx = len(scan_ops) - 1

# Shorthand for testing power manipulations (expensive, not essencial)

def _sqr(val):
    return val * val


class floodParm():

    '''
        Placeholder for lots of params for the floodfill function
        Passing a data class as an argument will make it a
        private / reentrent data.
    '''

    def __init__(self, iww, ihh, darr):

        self.darr = darr;       self.seekstep = 1
        self.iww = iww;         self.ihh = ihh
        self.callb = None;
        self.mark = [0,0,0,0];  self.exit = 0
        self.cnt = 0;           self.ops = 0
        self.depth = 0;         self.verbose = 0;
        self.thresh = 20;       self.breath = 20
        self.markcol = 100;     self.grey = 0
        self.stepx = 0;         self.stepy = 0
        self.minx = 0;          self.miny = 0
        self.maxx = 0;          self.maxy = 0

        self.tmesub = [];       self.dones = {}
        self.bounds = [];       self.body  = []
        self.no = []
        self.stack = stack.Stack()

# Seek(xxx, yyy, param, gl_dones)
# History:
#           Sat 19.Oct.2024  start xxx from zero
#           Wed 30.Oct.2024  cross marked - wtf
#

def Seek(xxx, yyy, param, gl_dones):

    '''
    Find next flood - able region / non background pixel.

    Parameters:<br>

            xxx         start coordinate
            yyy         start coordinate
            param       the floodParm class (as for the Flood routine)
            gl_dones    the global flood dones dictionary

    Return:  <br>

        new xxx, yyy
        or -1, -1 if no more matches

    '''
    #print("Seek:", xxx, yyy)
    rxx = -1; ryy = -1
    breakout = False
    while True:
        xxx += param.seekstep
        if xxx >= param.iww:
            xxx = 0; yyy += param.seekstep
        if yyy >= param.ihh:
            break
        if _is_cell_done(xxx, yyy, gl_dones):
                #print("Skipping to " , xx, yy)
                continue
        val = param.darr[yyy][xxx]
        ##if val[1] < 200:
        ##    print("val", xx, yy, val, end = " ")
        cc = (val[0] + val[1] + val[2]) // 3
        ##print(cc, end = " ")
        if cc < param.markcol:
            #print("got:", xxx, yyy)
            rxx = xxx; ryy = yyy
            break

    # -1 -1 if No more found
    return  rxx, ryy

def __callb(xxxx, yyyy, kind, param):

    ''' Extracted routine to subtract time spent in callback '''

    if not param.callb:
        return

    ttt2 = time.time()
    param.callb(xxxx, yyyy, kind, param);

    # We accumulate the timing taken by the display
    param.tmesub.append(time.time() - ttt2)

# ------------------------------------------------------------------------
# FYI: python only does 1000 deep recursion.
#     If two functions are recursed, that goes to 500 ...
#     Example: func1() calls func2() recurses to func1() -- 500 of these
#     ... never mind ... converted to python 3 table based
#
#     History:
#
#           Sept.2024           Resurrected from pyimgrec
#           Oct.2024            Python 3 conversion
#           Sat 12.Oct.2024     flood converted fron star to cross
#           Wed 30.Oct.2024     docs, separate inner and outer 'dones'
#
# Relies on code from stack.py
#

def Flood(xxx, yyy, param, gl_dones):

    '''
    Flood fill function. Fills the area in cross formation, clockwise.
    Re-written from recursive to stack based.

    Synonyms for directions:
                R-right B-below L-left A-above

    Scanning order: <br>

                       R B L A
                 (right, below, left, above)

    Parameters: <br>

        xxx, yyy        start coordinates
        fparam          pre-filled floodParm parameter class
                        ... most of the parameters are passed via this class.
        dones           dictionary to store global done flags

    Return Value: <br>

        value of -1 if no more flooding

    '''

    global gl_reenter

    #print(hex(id(gl_dones)))

    ret = 0

    # Safety net
    if gl_reenter:
        print( "Flood re-entry", xxx, yyy)
        gl_reenter =+ 1
        return -1
    gl_reenter += 1

    ttt = time.time()
    # Mark initial position's color
    try:
        # Attempt averaging the staring point: (+x,+y)
        # |  o      |  o +1+0 |
        # |  o +0+1 |  o +1+1 |
        ''' try:
            pt1 = param.darr[yyy][xxx]
            pt2 = param.darr[yyy][xxx+1]
            pt3 = param.darr[yyy+1][xxx+1]
            pt4 = param.darr[yyy+1][xxx]
            arr = (pt1, pt2, pt3,  pt4)
            sumr = 0; sumg = 0; sumb = 0;
            for aaa in arr:
                #print("aaa", aaa)
                sumr += aaa[0]
                sumg += aaa[1]
                sumb += aaa[2]
            param.mark  = (sumr//3, sumg//3, sumb//3, 255)
            #param.mark  = param.darr[yyy][xxx]
            #print("mark", param.mark,  "darr", param.darr[yyy][xxx])
        except:
            #print("mark dist", xxx, yyy, sys.exc_info())
            param.mark = param.darr[yyy][xxx]
        '''
        # Just mark one
        param.mark = param.darr[yyy][xxx]  # override
    except KeyError:
        print( "Start pos past end %d / %d" % (xxx, yyy))
        gl_reenter = 0
        return -1

    param.tmesub = []
    param.stack.push((xxx, yyy, 0))
    # Scanning order:
    #         4
    #         x
    #    3  x x x 1
    #         x
    #         2

    #print("iww", param.iww, "ihh", param.ihh)

    # Walk the patches, loop until done
    startop = 0
    while True :
        #print("new loop", xxx, yyy, "start", startop)

        #usleep(1)
        # If someone called it with reentry, bail out.
        # This is to allow the developer to terminate scan early, on demand.
        if gl_reenter > 1:
            gl_reenter =  0
            ret = -1
            break

        if param.stack.stacklen() == 0:
            break

        param.cnt += 1
        # Used during development
        #if param.cnt > 500:
        #    break

        nnn = 0

        # Iterate operators: Right - Down - Left - Up
        while 1:
            # Used during development
            param.cnt += 1
            #if param.cnt > 500:
            #    raise RuntimeError("Excceeded loop count")

            if nnn+startop > scan_idx:
                #print("break op loop", xxx, yyy,  "start", startop, "nnn", nnn)
                startop = 0
                break

            #print("op: xxx", xxx, "yyy", yyy, "nnn", nnn)
            xxx2 = xxx + scan_ops[nnn+startop][0];
            yyy2 = yyy + scan_ops[nnn+startop][1]

            # Contain boundaries
            xxxx = max(0, min(xxx2, param.iww-1))
            yyyy = max(0, min(yyy2, param.ihh-1))

            # Here we contain the boundaries by compare
            #           (as opposed to raising an exception for ---> 'C')
            if xxx2 < 0 or yyy2 < 1 or \
                    xxx2 >= param.iww or yyy2 >= param.ihh:
                param.bounds.append((xxxx, yyyy))
                #print("bound lz", xxx2, yyy2)
                nnn += 1
                __callb(xxxx, yyyy, DOT_BOUND, param);
                continue

            if _is_cell_done(xxx2, yyy2, param.dones):
                #print("cell done", xxx2, yyy2)
                nnn += 1
                continue

            #if _is_cell_done(xxx2, yyy2, gl_dones):
            #    print("cell done", xxx2, yyy2)
            #    nnn += 1
            #    continue

            # possible outcomes: DOT_NO, DOT_YES, DOT_BOUND
            retx = _scan_one(xxx2, yyy2, param, gl_dones)
            #print(xxx2, yyy2, ret, end = " - ")

            if  retx == DOT_YES:
                _mark_cell_done(xxx2, yyy2, param.dones)
                #print("Jump", xxx2, yyy2, "start", startop, "nnn", nnn)
                param.stack.push((xxx, yyy, startop+nnn))
                param.body.append((xxxx, yyyy))
                xxx = xxx2; yyy = yyy2
                #xxx = xxxx; yyy = yyyy
                __callb(xxxx, yyyy, DOT_YES, param);
                break  # jump to next
            elif  retx == DOT_NO:
                #print("no", xxx2, yyy2, end = " ")
                param.no.append((xxxx, yyyy))
                __callb(xxxx, yyyy, DOT_NO, param);
            elif retx == DOT_BOUND:
                #print("bound", xxx2, yyy2, end = " ")
                # Correct to within boundary
                param.bounds.append((xxxx, yyyy))
                __callb(xxxx, yyyy, DOT_BOUND, param);
                pass
            else:
                pass
                print("invalid ret from scan_one", retx)
            nnn += 1

        if nnn+startop > scan_idx:
            # It is less costly to scan it again
            #xxx, yyy, startop = param.stack.pop()
            #_mark_cell_done(xxx, yyy, param.dones)
            #xxx, yyy, startop = param.stack.pop()
            xxx, yyy, _ = param.stack.pop()
            #param.bounds.append((xxx, yyy))
            #print("popped", xxx, yyy, "start", startop, "nnn", nnn, )
            #__callb(xxxx, yyyy, DOT_POP, param);

    # All operations done, post-process
    xlen = len(param.bounds)
    bound  = calc_flood_bounds(param.bounds)
    param.minx = bound[0]; param.miny = bound[1]
    param.maxx = bound[2]; param.maxy = bound[3]
    param.ww = param.maxx - param.minx
    param.hh = param.maxy - param.miny

    __callb(0, 0, DOT_INVALIDATE, param);

    if xlen > 4:
        treal = (time.time() - ttt)
        tsum = 0
        for taa in param.tmesub:
            tsum += taa

        #print("tsum %.2f ms" % (tsum * 1000) )
        #print("treal %.2f ms" % (treal * 1000) )

        # subtract time spent in printing
        tstr = "%.2f ms" % ((treal-tsum) * 1000)

        #print("Flood(): xxx", xxx, "yyy", yyy, "ww", param.ww, "hh", param.hh,
        #            "xlen", xlen, "ops", param.ops, "tstr", tstr)
        #print("loop count", param.cnt, "bounds len", len(param.bounds) )

    #print("dones", len(param.dones), dones)
    #print( "done cnt =", param.cnt, "ops =", param.ops)
    #print("dones", dones)

    __callb(xxx, yyy, DOT_MARK, param)

    # Output marked cells to global pool:
    for aaa in param.dones:
        #print(cnt, aaa, end = " - ")
        try:
            _mark_cell_done(aaa[0], aaa[1], gl_dones)
        except:
            pass
            print("cpmark", cnt, aaa, sys.exc_info())

    #print("gl_dones records", len(gl_dones), len(param.dones))

    # Unlock flood rentry
    gl_reenter = 0
    return ret

def _scan_one(xxx2, yyy2, param, gl_dones):

    ''' Scan one pixel, specified by the caller coordinates
        Return one of: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
    '''

    ret = DOT_NO
    param.ops += 1

    while 1:        # Substitute goto
        if _is_cell_done(xxx2, yyy2, gl_dones):
            #print("cell done", xxx2, yyy2)
            ret = DOT_BOUND
            break
        try:
            if param.grey:
                diff = coldiffbw(param.mark, param.darr[yyy2][xxx2])
            else:
                diff = coldiff(param.mark, param.darr[yyy2][xxx2])
            #print( "diff: 0x%x" % diff, xxx2, yyy2)
        except KeyError:
            print( "out of range: ", xxx2, yyy2)
            ret = DOT_BOUND
            break
        except:
            print_exception("coldiff")

        if diff < param.thresh:
            ret = DOT_YES
            break
        else:
            ret = DOT_NO
            break
        # Just in case
        break

    #print("scan_one:", xxx2, yyy2, dot_strs[ret])
    return ret

def _mark_cell_done(xxx, yyy, dones):

    '''  Mark a cell done. Create dimension and value if not present '''

    #print(id(dones))

    dones[xxx, yyy] = 1

    #try:
    #    old = dones[xxx, yyy]
    #except:
    #    #print("create", xxx, yyy, sys.exc_info())
    #    dones[xxx, yyy] = 1
    #try:
    #    #print("inc", xxx, yyy)
    #    dones[xxx, yyy] += 1
    #except:
    #    print("exc mark cell", sys.exc_info())

    #for cnt, aaaa in enumerate(dones):
    #    print("dones", cnt, aaaa, dones[aaaa])
    #    if cnt > 20:
    #        break

# ------------------------------------------------------------------------
# Return flag if visited before

def _is_cell_done(xxx, yyy, dones):
    try:
        aa = dones[xxx, yyy]
    except KeyError:
        aa = 0
    except:
        print("is done", sys.exc_info())
    return aa

def coldiff(refcol, colx):

    ''' Subtract color average from ref average. RGB version '''

    #cc = math.sqrt(abs(_sqr(refcol[0]) - SQR(colx[0]) ))
    #dd = math.sqrt(abs(_sqr(refcol[1]) - SQR(colx[1]) ))
    #ee = math.sqrt(abs(_sqr(refcol[2]) - SQR(colx[2]) ))

    cc = abs(refcol[0] - colx[0])
    dd = abs(refcol[1] - colx[1])
    ee = abs(refcol[2] - colx[2])

    # Average:
    #ret = cc + dd + ee) // 3

    # Looks like this one is better, picking dominant color diff
    # Maxdiff:   Mon 21.Oct.2024
    ret = max(max(cc, dd), ee)
    #print("coldiff", refcol, colx, ret)
    return ret

def coldiffbw(refcol, colx):

    ''' Subtract col average from ref average; gray scale version '''

    cc = (refcol[0] + refcol[1] + refcol[2]) // 3
    dd = (colx[0] + colx[1] + colx[2]) // 3
    ret = abs(cc - dd)
    #print("coldiffbw", refcol, colx, ret)
    return ret

def calc_flood_bounds(bounds):

    ''' Calculate boundaries of the data '''

    minx = miny = 0xffffffff;
    maxx = maxy = 0

    for aa in bounds:
        #print( aa,)
        if minx > aa[0]: minx = aa[0]
        if miny > aa[1]: miny = aa[1]
        if maxx < aa[0]: maxx = aa[0]
        if maxy < aa[1]: maxy = aa[1]

    #print("calc_bounds() minx =", minx, "miny =", miny,
    #                            "maxx =",  maxx,  "maxy =", maxy)
    return (minx, miny, maxx, maxy)

# EOF
