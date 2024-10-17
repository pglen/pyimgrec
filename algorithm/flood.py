#!/usr/bin/env python

import  os, sys, getopt, signal, array

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import pyimgutils as iut
import  stack

import imgrec.imgrec as imgrec

# Results of compare

DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND = range(4)
dot_strs = ("DOT_NO", "DOT_YES", "DOT_MARKED", "DOT_BOUND")

# Scanning order for xxx, yyy at: R B L A
scan_ops = ((1,0), (0,1), (-1,0), (0,-1))

reenter = 0

class floodParm():

    '''
        Placeholder for lots of params for the floodfill function
        Passing a data class will make it private / reentrant data
    '''

    def __init__(self, darr, callb = None):

        self.darr = darr;       self.callb = callb

        self.mark = [0,0,0,0];  self.exit = 0
        self.cnt = 0;           self.depth = 0;
        self.thresh = 20;       self.breath = 10
        self.markcol = 100
        self.verbose = 0;       self.ops = 0
        self.stepx = 0;         self.stepy = 0
        self.minx = 0;          self.miny = 0
        self.maxx = 0;          self.maxy = 0
        self.iww = 0;           self.ihh = 0
        self.grey = 0
        self.bounds = {};       self.body  = {};

        self.stack = stack.Stack()

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

def flood_one(xxx, yyy, param, dones):

    ret = 0
    global reenter
    # Safety net
    if reenter:
        print( "Flood re-entry", xxx, yyy)
        reenter =+ 1
        return -1

    reenter += 1

    # Mark initial position's color
    try:
        param.mark = param.darr[yyy][xxx]
    except KeyError:
        print( "Start pos past allocated array %d / %d (%d)" %( xxx, yyy, param.divider))
        reenter -= 1
        return -1

    param.stack.push((xxx, yyy, 0))
    #mark_done(xxx, yyy, 1, param)

    # Walk the patches, loop until done
    startop = 0
    while True :
        #print("new loop", xxx, yyy, startop)
        param.cnt += 1;

        if reenter > 1:
            reenter = 1
            ret = -1
            break

        if param.stack.stacklen() == 0:
            break
        #if param.cnt > 500:
        #    break

        ret = DOT_NO; nnn = 0
        # Iterate operators
        while 1:
            if nnn+startop >= len(scan_ops):
                break
            #print("nnn", nnn)
            xxx2 = xxx + scan_ops[nnn+startop][0];
            yyy2 = yyy + scan_ops[nnn+startop][1]
            # possible outcomes: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
            ret = _scan_one(xxx2, yyy2, param, dones)

            iut.mark_cell(xxx, yyy, 1, dones)
            if  ret == DOT_YES:
                iut.mark_cell(xxx2, yyy2, 1, param.body)
                param.stack.push((xxx, yyy, nnn))
                xxx = xxx2; yyy = yyy2
                # To observe fill action, if requested
                if param.callb:
                    param.callb(xxx, yyy, 2, param);
                break  # jump to next
            elif  ret == DOT_NO:
                #print("no", xxx2, yyy2, end = " ")
                xxxx = max(0, min(xxx2, param.iww-1))
                yyyy = max(0, min(yyy2, param.ihh-1))
                iut.mark_cell(xxxx, yyyy, 1, param.bounds)
                # To observe boundary action, if requested
                if param.callb:
                    param.callb(xxxx, yyyy, 0, param);
            elif ret == DOT_BOUND:
                #print("bound", xxx2, yyy2, end = " ")
                # Correct to within boundary
                xxxx = max(0, min(xxx2, param.iww-1))
                yyyy = max(0, min(yyy2, param.ihh-1))
                iut.mark_cell(xxxx, yyyy, 1, param.bounds)
                if param.callb:
                    param.callb(xxxx, yyyy, 1, param);
            elif  ret == DOT_MARKED:
                pass
            else:
                print("invalid ret from scan_one", ret)
            nnn += 1

        if  nnn+startop == len(scan_ops):
            #print("eval", nnn+startop, "stack", param.stack.stacklen())
            #iut.mark_cell((xxx, yyy, nnn+startop), dones)
            xxx, yyy, startop = param.stack.pop()

    # All operations done, pre-process

    xlen = len(param.bounds)
    if xlen > 16:
        print("flood_one: xxx", xxx, "yyy", yyy, "mark:", param.mark, "xlen", xlen)
        #print("loop count", param.cnt, "bounds len", len(param.bounds) )

    bound  = _calc_bounds(param.bounds)
    param.minx = bound[0]; param.miny = bound[1]
    param.maxx = bound[2]; param.maxy = bound[3]

    reenter -=1
    #print("dones", len(param.dones), dones)
    #print( "done cnt =", param.cnt, "ops =", param.ops)

    return ret

def seek(xxx, yyy, param, dones):

    ''' find next floodable region '''

    for yy in range(yyy, param.ihh):
        for xx in range(xxx, param.iww):
            if _is_pixel_done(xx, yy, dones):
                continue
            val = param.darr[yy][xx]
            cc = (val[1] + val[2] + val[3]) // 3
            #print(cc, end = " ")
            if cc < param.markcol:
                return (1, xx, yy)
    return  (0, xxx, yyy)

def _coldiff(colm, colx):

    ''' Substruct col avarage from ref avarage color version '''

    cc = abs(colm[0] - colx[0])
    dd = abs(colm[1] - colx[1])
    ee = abs(colm[2] - colx[2])

    #ret = (cc + dd + ee) // 3
    retx = max(cc, dd)
    ret = max(retx, ee)

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
        if bounds[aa]:
            if minx > aa[0]: minx = aa[0]
            if miny > aa[1]: miny = aa[1]
            if maxx < aa[0]: maxx = aa[0]
            if maxy < aa[1]: maxy = aa[1]

    #print("calc_bounds() minx =", minx, "miny =", miny,
    #                            "maxx =",  maxx,  "maxy =", maxy)
    return (minx, miny, maxx, maxy)

def _scan_one(xxx2, yyy2, param, dones):

    ''' Scan one pixel, specified by the caller coordinates
        Return one of: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
    '''

    param.ops += 1
    ret = DOT_NO
    while 1:        # Substitute goto
        if _is_pixel_done(xxx2, yyy2, dones):
            # already marked
            ret =  DOT_MARKED
            break
        else:
            try:
                if param.grey:
                    diff = _coldiffbw(param.mark, param.darr[yyy2][xxx2])
                else:
                    diff = _coldiff(param.mark, param.darr[yyy2][xxx2])
                #print( "diff: 0x%x" % diff, xxx2, yyy2)
            except KeyError:
                #print( "out of range: ", xxx2, yyy2)
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

# ------------------------------------------------------------------------
# Return flag if visited before

def _is_pixel_done(xxx, yyy, dones):
    try:
        aa = dones[xxx, yyy]
    except KeyError:
        aa = 0
    except:
        print("is done", sys.exc_info())
    return aa

# EOF
