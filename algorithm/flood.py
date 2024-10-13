#!/usr/bin/env python

import  os, sys, getopt, signal, array

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from    pyimgutils import *
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

        self.cnt = 0;           self.depth = 0
        self.mark = 0;          self.divider = 0
        self.thresh = 50;       self.breath = 1
        self.verbose = 0;       self.ops = 0
        self.stepx = 0;         self.stepy = 0
        self.minx = 0;          self.miny = 0
        self.maxx = 0;          self.maxy = 0
        self.iww = 0;           self.ihh = 0
        self.dones = {};        self.bounds = {}
        self.body  = {}
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
#
# History:
#           Sept.2024           Resurrected from pyimgrec
#           Oct.2024            Python 3 conversion
#           Sat 12.Oct.2024     flood converted fron star to cross
#
# Relies on code from stack.py
#

def flood_one(xxx, yyy, param):

    global reenter
    # Safety net
    if reenter:
        print( "Flood re-entry", xxx, yyy)
        return
    reenter +=1

    # Mark initial position
    try:
        param.mark = param.darr[yyy][xxx]
    except KeyError:
        print( "Start pos past allocated array %d / %d (%d)" %( xxx, yyy, param.divider))
        reenter -= 1
        return -1

    print("flood_one: (xxx/yyy)", xxx, yyy, "mark:", param.mark)

    param.stack.push((xxx, yyy, 0))
    #mark_done(xxx, yyy, 1, param)

    # Walk the patches, loop until done
    startop = 0
    while True :
        #print("new loop", xxx, yyy, startop)
        param.cnt += 1;

        if param.stack.stacklen() == 0:
            print( "while break end")
            break

        #if param.cnt > 500:
        #    break

        # To observe in action, if requested
        if param.callb:
            if param.cnt % param.breath == 0:
                param.callb(xxx, yyy, param);
                #break
        ret = DOT_NO;
        # Iterate operators
        for nnn in range(startop, len(scan_ops)):
            #print("nnn", nnn)
            xxx2 = xxx + scan_ops[nnn+startop][0];
            yyy2 = yyy + scan_ops[nnn+startop][1]
            # possible outcomes: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
            ret = scan_one(xxx2, yyy2, param)
            mark_cell(xxx, yyy, 1, param.dones)

            if  ret == DOT_YES:
                mark_cell(xxx, yyy, 1, param.body)
                param.stack.push((xxx, yyy, nnn))
                xxx = xxx2; yyy = yyy2
                break  # jump
            elif  ret == DOT_NO or ret == DOT_BOUND:
                mark_cell(xxx, yyy, 1, param.bounds)
                pass
            elif  ret == DOT_MARKED:
                pass
            else:
                print("invalid ret from scan_one", ret)

        if  ret == DOT_YES:
            continue
        if  ret == DOT_NO or ret == DOT_BOUND:
            print("pop", param.stack.len())
            xxx, yyy, startop = param.stack.pop()
            continue

        # ----------------------------------------------------------------
        # All operations done, mark this one done
        if  nnn+startop == len(scan_ops):
            #mark_cell((xxx, yyy, nnn+startop), param.dones)
            xxx, yyy, startop = param.stack.pop()
            continue

    print("loop count", param.cnt)

    reenter -=1
    #print("dones", len(param.dones), param.dones)

    #print( "done cnt =", param.cnt, "ops =", param.ops)
    calc_bounds(param)
    return

def coldiff(colm, colx):

    ''' Substruct col avarage from ref avarage '''

    cc = (colm[1] + colm[2] + colm[3]) // 3
    dd = (colx[1] + colx[2] + colx[3]) // 3
    ret = abs(cc - dd)
    #print("coldiff", colm, colx, ret)
    return ret

def scan_one(xxx2, yyy2, param):
    ret = _scan_one(xxx2, yyy2, param)
    print("scan_one:", xxx2, yyy2, dot_strs[ret])
    return ret

# ------------------------------------------------------------------------
# Scan new patch in direction specified by the caller

def _scan_one(xxx2, yyy2, param):

    ''' Scan one pixel, specified by the caller coordinates
        Return one of: DOT_NO, DOT_YES, DOT_MARKED, DOT_BOUND
    '''

    ret = DOT_NO
    if is_pixel_done(xxx2, yyy2, param):
        # already marked
        ret =  DOT_MARKED
        return ret
    else:
        param.ops += 1
        try:
            diff = coldiff(param.mark, param.darr[yyy2][xxx2])
            #print( "diff: 0x%x" % diff, xxx2, yyy2)
        except:
            print_exception("coldiff")
            #print( "out of range ignoring: ", xxx2, yyy2)
            ret = DOT_BOUND
            return ret

        if diff < param.thresh:
            ret = DOT_YES
            return ret

    return ret

# ------------------------------------------------------------------------
# Return flag if visited before

def is_pixel_done(xxx, yyy, param):
    try:
        aa = param.dones[xxx, yyy]
    except:
        aa = 0
    return aa

# ------------------------------------------------------------------------
# Mark a cell done

def mark_cell(xxx, yyy, flag, dictx):

    try:
        dictx[xxx, yyy] = flag
    except:
        try:
            dictx[xxx] = {}
            dictx[xxx, yyy] = flag
        except:
            print("cell", sys.exc_info())

def calc_bounds(param):
    #print( "param len", len(param.dones))
    minx = 10000; maxx = 0; miny = 10000; maxy = 0
    for aa in param.bounds.keys():
        #print( aa,)
        if param.bounds[aa]:
            if minx > aa[0]: minx = aa[0]
            if miny > aa[1]: miny = aa[1]
            if maxx < aa[0]: maxx = aa[0]
            if maxy < aa[1]: maxy = aa[1]

    #print( "flood minx miny", minx, miny, "maxx maxy",  maxx, maxy)
    param.minx = minx
    param.miny = miny
    param.maxx = maxx
    param.maxy = maxy

    pass

# EOF
