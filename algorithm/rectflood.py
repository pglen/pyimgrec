#!/usr/bin/env python

import  os, sys, getopt, signal, array

from pyimgutils import *
import  stack

import imgrec.imgrec as imgrec

# Placeholder for lots of params for the floodfill function
# Passing a data class will make it private / reentrant data

rectflood_reenter = 0

class rfloodParm():

    def __init__(self, img, darr):

        self.cnt = 0;           self.depth = 0
        #self.hstep = 0;         self.vstep = 0
        self.tresh = 10;        self.breath = 1 #divider / 4
        self.darr = darr;       self.spaces = {}
        self.verbose = False;   self.ops = 0
        self.cmps = 0
        self.colx = 0x808080
        self.stack = stack.Stack()
        # Callback
        self.inval = None
        self.img = img

        #for aa in range(divider):
        #    self.spaces[aa] = {}

# ------------------------------------------------------------------------
# Rectangular flood fill.
#
# Synonyms for directions:
#            L-left R-right A-above B-below
#
# Scanning order:
#           A, AR, R, BR, B, BL, L, AL
#
# Most of the parameters are passed via the param class.
#

def rectflood(xxx, yyy, param):

    global rectflood_reenter

    # Safety net
    if rectflood_reenter:
        print( "Flood re-entry", xxx, yyy);
        return
    rectflood_reenter +=1

    # Mark initial position
    try:
        param.mark = param.darr[xxx][yyy]
    except KeyError:
        print( "Exceeded allocated array %d / %d (%d)" %( xxx, yyy, param.ddd))
        rectflood_reenter -= 1
        return

    param.stack.push((xxx, yyy))
    mark_done(xxx, yyy, 1, param)

    # Loop until done
    while True :

        param.cnt += 1;

        # To observe in action, if requested
        if param.inval:
            if param.cnt % param.breath == 0:
                param.inval(xxx, yyy, param);

        #print( "Scanning", xxx, yyy)

        # ----------------------------------------------------------------
        # Walk the patches

        while (True):
            xxx2 = xxx; yyy2 = yyy-1
            ret = scan_one(xxx, yyy, xxx2, yyy2, param)
            if  ret[0] == -1: break;
            if  ret[0] ==  1: xxx = ret[1]; yyy = ret[2]
            param.stack.push((xxx, yyy))
            print( "push", xxx, yyy)
            while(True):
                xxx2 = xxx+1; yyy2 = yyy
                ret = scan_one(xxx, yyy, xxx2, yyy2, param)
                if  ret[0] == -1:  break;
                if  ret[0] ==  1: xxx = ret[1]; yyy = ret[2]
            print( "org", xxx, yyy)
            un = param.stack.pop()
            #print("un", un)
            #xxx, yyy = un
            #print( "pop", xxx, yyy)

            if param.verbose:
                print( "A", ret[3],)

        '''while (True):
            xxx2 = xxx; yyy2 = yyy+1
            ret = scan_one(xxx, yyy, xxx2, yyy2, param)
            if  ret[0] == -1: break;
            if  ret[0] ==  1: xxx = ret[1]; yyy = ret[2]
            if param.verbose:
                print( "B", ret[3],)
        '''
        break;

        '''xxx2 = xxx+1; yyy2 = yyy
        ret = scan_one(xxx, yyy, xxx2, yyy2, param)
        if  ret[0] == -1: break;
        if  ret[0] ==  1: xxx = ret[1]; yyy = ret[2]
        if param.verbose:
            print( "R", ret[3],)
        '''


        '''xxx2 = xxx-1; yyy2 = yyy
        ret = scan_one(xxx, yyy, xxx2, yyy2, param)
        if  ret[0] == -1: break;
        if  ret[0] ==  1: xxx = ret[1]; yyy = ret[2]
        if param.verbose:
            print( "L", ret[3],)
        '''

        # ----------------------------------------------------------------

        if param.stack.stacklen() == 0:
            print( "while break end")
            break

    rectflood_reenter -=1

    print( "done cnt =", param.cnt, "ops =", param.ops, "cmps=", param.cmps)
    calc_bounds(param)

    return

def calc_bounds(param):
    print( "param len", len(param.spaces))

# ------------------------------------------------------------------------
# Scan new patch in direction specified by the caller
# Return (-1, 0, 0) if done, (0, xxx, yyy) if no, (1, xxx, yyy) if match

def scan_one(xxx, yyy, xxx2, yyy2, param):

    param.ops += 1

    try:
        diff = imgrec.diffcol(param.mark, param.darr[xxx2][yyy2])
        #print( "diff", diff)
    except:
        print_exception("diffcol")
        #print( "out of range for ", xxx2, yyy2)
        try:
            xxx3, yyy3 = param.stack.pop()
            param.depth -= 1
            return 1, xxx3, yyy3, 0
        except:
            mark_done(xxx, yyy, 0, param)
            #print( "scan_one done")
            return -1, 0, 0, 0

    if diff[1] < param.tresh:
        #print( "OK", xxx2, yyy2, diff[1])
        mark_done(xxx, yyy, 1, param)
        #param.stack.push((xxx2, yyy2))
        #param.depth += 1
        return 1, xxx2, yyy2, diff[1]
    else:
        #print( "NOK", xxx2, yyy2, diff[1])
        mark_done(xxx, yyy, 0, param)
        try:
            #xxx3, yyy3 = param.stack.pop()
            #param.depth -= 1
            return -1, xxx3, yyy3, 0
        except:
            #print( "scan_one 2 done")
            return -1, 0, 0, 0

    return 0, 0, 0

# ------------------------------------------------------------------------
# Return flag if visited before

def is_done(xxx, yyy, param):

    try:
        aa = param.spaces[xxx, yyy]
    except:
        aa = -1
    return aa

# ------------------------------------------------------------------------
# Mark a cell done

def mark_done(xxx, yyy, flag, param):

        param.spaces[xxx, yyy] = flag

 # EOF
