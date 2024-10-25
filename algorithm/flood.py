#!/usr/bin/env python

import  os, sys, getopt, signal, array, random, math, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import  pyimgutils as iut
import  stack

import imgrec.imgrec as imgrec

# Results of compare

dot_strs = ("DOT_NO", "DOT_YES", "DOT_MARKED", "DOT_BOUND", "DOT_POP", "DOT_INVALID")
# Create enums
iut.do_enums(dot_strs, locals())

# Verify enums
#for aaa in dot_strs:
#    print("%s=%d" % (aaa, locals().get(aaa)), end = " ")
#print()

#print(DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND, DOT_POP, DOT_INVALID)

# Scanning order for xxx, yyy at: R B L A
scan_ops = ((1,0), (0,1), (-1,0), (0,-1))
scan_idx = len(scan_ops) - 1
reenter = 0

def SQR(val):
    return val * val

class floodParm():

    '''
        Placeholder for lots of params for the floodfill function
        Passing a data class will make it private / reentrant data
    '''

    def __init__(self, darr, callb = None):

        self.darr = darr;       self.callb = callb

        self.mark = [0,0,0,0];  self.exit = 0
        self.cnt = 0;           self.ops = 0
        self.depth = 0;         self.verbose = 0;
        self.thresh = 20;       self.breath = 20
        self.markcol = 100;     self.grey = 0
        self.stepx = 0;         self.stepy = 0
        self.minx = 0;          self.miny = 0
        self.maxx = 0;          self.maxy = 0
        self.iww = 0;           self.ihh = 0
        self.tmesub = [];
        self.bounds = [];       self.body  = []
        self.stack = stack.Stack()

def Seek(xxx, yyy, param, dones):

    ''' find next floodable region / non background pixel.
    History:
            Sat 19.Oct.2024  start xxx from zero
    '''

    xx = xxx; yy = yyy

    for yy in range(yyy, param.ihh):
        for xx in range(0, param.iww):
            if is_cell_done(xx, yy, dones):
                continue
            val = param.darr[yy][xx]

            #if val[1] < 200:
            #    print("val", xx, yy, val, end = " ")

            cc = (val[0] + val[1] + val[2]) // 3
            #print(cc, end = " ")
            if cc <= param.markcol:
                return (1, xx, yy)
    return  (0, xx, yy)

def __callb(xxxx, yyyy, kind, param):
    if param.callb:
        ttt2 = time.time()
        param.callb(xxxx, yyyy, kind, param);
        param.tmesub.append(time.time() - ttt2)

# ------------------------------------------------------------------------
# Flood fill. Fill in cross formation, clockwise. Re-written from recursive
# to stack based. FYI: python (2.6) only does 1000 deep recursion.
# If two functions are recursed, that goes to 500 ...
# Example: func1() calls func2() recurses to func1() -- 500 of these
#
# ... never mind ... converted to python 3 table based
#
# Synonyms for directions:
#            L-left R-right A-above B-below
#
# Scanning order:
#                   R B L A
# Parms:
#   xxx, yyy    start coordinates
#    fparm      pre filled parameter class
#               ... most of the parameters are passed via this class.
#    dones      dictioanry to store done flags
#
# History:
#           Sept.2024           Resurrected from pyimgrec
#           Oct.2024            Python 3 conversion
#           Sat 12.Oct.2024     flood converted fron star to cross
#
# Relies on code from stack.py
#

def Flood(xxx, yyy, param, dones):

    ret = 0
    global reenter
    # Safety net
    if reenter:
        print( "Flood re-entry", xxx, yyy)
        reenter =+ 1
        return -1
    reenter += 1

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
            print("mark", param.mark,  "darr", param.darr[yyy][xxx])
        except:
            print("mark dist", xxx, yyy, sys.exc_info())
            param.mark = param.darr[yyy][xxx]
        '''
        param.mark = param.darr[yyy][xxx]  # override
    except KeyError:
        print( "Start pos past end %d / %d" % (xxx, yyy))
        reenter -= 1
        return -1

    param.tmesub = []
    param.stack.push((xxx, yyy, 0))
    # Scanning order:
    #         4
    #         x
    #    3  x x x 1
    #         x
    #         2
    # Walk the patches, loop until done
    startop = 0
    while True :
        #print("new loop", xxx, yyy, "start", startop)
        if reenter > 1:
            reenter = 1
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

            #print("xxx", xxx, "yyy", yyy, "nnn", nnn)
            xxx2 = xxx + scan_ops[nnn+startop][0];
            yyy2 = yyy + scan_ops[nnn+startop][1]

            # Contain boundaries
            xxxx = max(0, min(xxx2, param.iww-1))
            yyyy = max(0, min(yyy2, param.ihh-1))

            if xxx2 < 0 or yyy2 < 1 or \
                    xxx2 >= param.iww or yyy2 >= param.ihh:
                param.bounds.append((xxxx, yyyy))
                #print("bound lz", xxx2, yyy2)
                nnn += 1
                __callb(xxxx, yyyy, DOT_BOUND, param);
                continue

            if is_cell_done(xxx2, yyy2, dones):
                nnn += 1
                continue

            # possible outcomes: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
            retx = _scan_one(xxx2, yyy2, param, dones)
            #print("scan", xxx2, yyy2, "ret", ret, "start", startop, "nnn", nnn)

            # Note: we mark all cells, including boundary
            _mark_cell_done(xxx2, yyy2, dones)

            if  retx == DOT_YES:
                #_mark_cell_done(xxx2, yyy2, dones)
                #print("Jump", xxx2, yyy2, "start", startop, "nnn", nnn)
                param.stack.push((xxx2, yyy2, startop+nnn))
                param.body.append((xxxx, yyyy))
                xxx = xxx2; yyy = yyy2
                #xxx = xxxx; yyy = yyyy
                __callb(xxxx, yyyy, DOT_YES, param);
                break  # jump to next
            elif  retx == DOT_NO:
                #print("no", xxx2, yyy2, end = " ")
                param.bounds.append((xxxx, yyyy))
                __callb(xxxx, yyyy, DOT_NO, param);
            elif retx == DOT_BOUND:
                #print("bound", xxx2, yyy2, end = " ")
                # Correct to within boundary
                #param.bounds.append((xxxx, yyyy))
                #__callb(xxxx, yyyy, DOT_BOUND, param);
                pass
            elif retx == DOT_MARKED:
                # No action
                pass
                param.bounds.append((xxxx, yyyy))
                #if param.callb:
                #    param.callb(xxxx, yyyy, DOT_MARKED, param);
            else:
                pass
                #print("invalid ret from scan_one", retx)
            nnn += 1

        if nnn+startop > scan_idx:
            # It is less costly to scan it again
            #xxx, yyy, startop = param.stack.pop()
            #_mark_cell_done(xxx, yyy, dones)
            xxx, yyy, _ = param.stack.pop()
            param.bounds.append((xxx, yyy))
            #print("popped", xxx, yyy, "start", startop, "nnn", nnn, )
            #__callb(xxxx, yyyy, DOT_POP, param);

    # All operations done, pre-process
    xlen = len(param.bounds)
    bound  = _calc_bounds(param.bounds)
    param.minx = bound[0]; param.miny = bound[1]
    param.maxx = bound[2]; param.maxy = bound[3]
    param.ww = param.maxx - param.minx
    param.hh = param.maxy - param.miny

    if param.callb:  # To flush all
        __callb(0, 0, DOT_INVALID, param);

    if xlen > 4:
        treal = (time.time() - ttt)
        tsum = 0
        for taa in param.tmesub:
            tsum += taa

        #print("tsum %.2f ms" % (tsum * 1000) )
        #print("treal %.2f ms" % (treal * 1000) )

        # subtract time spent in printing
        tstr = "%.2f ms" % ((treal-tsum) * 1000)

        print("Flood(): xxx", xxx, "yyy", yyy, "ww", param.ww, "hh", param.hh,
                    "xlen", xlen, "ops", param.ops, "tstr", tstr)
        #print("loop count", param.cnt, "bounds len", len(param.bounds) )

    #print("dones", len(param.dones), dones)
    #print( "done cnt =", param.cnt, "ops =", param.ops)
    #print("dones", dones)

    reenter -=1

    return ret

def _scan_one(xxx2, yyy2, param, dones):

    ''' Scan one pixel, specified by the caller coordinates
        Return one of: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
    '''

    ret = DOT_NO
    while 1:        # Substitute goto
        param.ops += 1
        try:
            if param.grey:
                diff = _coldiffbw(param.mark, param.darr[yyy2][xxx2])
            else:
                diff = _coldiff(param.mark, param.darr[yyy2][xxx2])
            #print( "diff: 0x%x" % diff, xxx2, yyy2)
        except KeyError:
            print( "out of range: ", xxx2, yyy2)
            ret = DOT_BOUND
            break
        except:
            iut.print_exception("coldiff")

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

    try:
        old = dones[xxx]
    except:
       dones[xxx] = {}
    try:
        old = dones[xxx, yyy]
        dones[xxx, yyy] += 1
    except:
        try:
            dones[xxx, yyy] = 0
            dones[xxx, yyy] += 1
        except:
            print("exc mark cell", sys.exc_info())

# ------------------------------------------------------------------------
# Return flag if visited before

def is_cell_done(xxx, yyy, dones):
    try:
        aa = dones[xxx, yyy]
    except KeyError:
        aa = 0
    except:
        print("is done", sys.exc_info())
    return aa

def _coldiff(colm, colx):

    ''' Substruct col avarage from ref avarage. RGB version '''

    #cc = math.sqrt(abs(sqr(colm[0]) - SQR(colx[0]) ))
    #dd = math.sqrt(abs(sqr(colm[1]) - SQR(colx[1]) ))
    #ee = math.sqrt(abs(sqr(colm[2]) - SQR(colx[2]) ))

    cc = abs(colm[0] - colx[0])
    dd = abs(colm[1] - colx[1])
    ee = abs(colm[2] - colx[2])

    # Average
    #ret = cc + dd + ee) // 3

    # Maxdiff   Mon 21.Oct.2024 looks like this one
    ret = max(max(cc, dd), ee)
    #print("coldiff", colm, colx, ret)
    return ret

def _coldiffbw(colm, colx):

    ''' Substruct col avarage from ref avarage; grayscale version '''

    cc = (colm[0] + colm[1] + colm[2]) // 3
    dd = (colx[0] + colx[1] + colx[2]) // 3
    ret = abs(cc - dd)
    #print("coldiffbw", colm, colx, ret)
    return ret

def _calc_bounds(bounds):

    ''' Calculate boundaries of the data '''

    minx = 10000; maxx = 0; miny = 10000; maxy = 0

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
