#!/usr/bin/env python

# Main image for pyimgrec. Creates wwo images image and image2. Manipulate / draw image2
#
# The floowing code will squash warnings if you have no pynum installed:
#
# import warnings
# with warnings.catch_warnings():
#    warnings.simplefilter("ignore")
# arr = pixb.get_pixels()

import os, sys, getopt, signal, array, math
import time, random
import cairo

THRESH      = 20                 # Color diff for boundary
MARKCOL     = 180                # Color counts as mark
MAXFOUND    = 200
MINFOUND    = 150
MINMAXFACT  = 3
MARKDIFF    = 30

BPX         = 4                  # Bytes per pixel

from pyimgutils import *

import  algorithm.flood  as flood
import  algorithm.outline as outline
import  algorithm.island as island

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

import imgrec.imgrec as imgrec

class Flood():

# --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

    def anal_image(self, xxx, yyy, single = False, addx = False):

        imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        global MARKCOL, THRESH
        MARKCOL = int(self.xparent.scale.get_value())
        THRESH  = int(self.xparent.scale2.get_value())

        #imgrec.verbose = 1
        #avg = imgrec.average()
        if xconfig.verbose:
            print( "Anal image xxx:", xxx, "yyy:", yyy, "www", self.iww, "hhh", self.ihh,
                        "thresh", THRESH, "markcol", MARKCOL)
            #print("divider", self.divider)


        #imgrec.verbose = 0

        self.xparent.tree.append_treestore("Anal image xxx: %d yyy: %d" % (xxx, yyy))

        # Draw grid:
        if self.xparent.check1.get_active():
            try:
                #print("Grid")
                for xx in range(self.divider):
                    hor = int(xx * self.stepx)
                    imgrec.line(hor, 0, hor, self.ihh, 0xff888888)
                for yy in range(self.divider):
                    ver = int(yy * self.stepy)
                    imgrec.line(0, ver, self.iww-1, ver, 0xff888888)

                self.invalidate()
                #usleep(10)
            except:
                print_exception("grid")

        self.darr = {};

        # Fill in 2D array
        for yy in range(self.ihh):
            offs = yy * self.iww * BPX
            for xx in range(self.iww):
                val = []
                for cc in range(BPX):
                    val.append(self.buf[offs + xx * BPX + cc])
                self._add_to_dict(self.darr, xx, yy, val)

        # TEST: Put it back to img
        #imgrec.blank(color=0xff888888)
        #for yy in range(self.ihh):
        #    for xx in range(self.iww):
        #        offs = yy * self.iww * 4
        #        for cc in range(4):
        #            try: buf[offs + xx * 4 + cc] = darr[yy][xx][cc]
        #            except: pass
        #    self.invalidate(); usleep(.1)
        #return

        self.reanal += 1
        if self.reanal > 1:
            print("Stopping Anal .. please wait")
            flood.gl_reenter += 1
            self.reanal = 0
            return

        # See if repeated request for scanning the same image
        if not self.laststate & Gdk.ModifierType.SHIFT_MASK:
            self.xparent.simg.clear()
            #self.xparent.win2.simg.clear()
            self.gl_dones = {}

        self._anal_image_worker(xxx, yyy, single, addx)
        self.reanal = 0

    def compare(self, xarr, fbounds):

        # Compare shape with saved ones
        cmp = []; coord = []
        for cc in self.xparent.shapes:
            res = outline.cmp_arrays(cc[4], xarr)
            #print("comp", res, cc[0])
            cmp.append( (res, cc[0]) )
            coord.append( (fbounds.minx, fbounds.miny, fbounds.mark,) )
        if(len(cmp)):
            cmp.sort()
            #for aa in cmp:
            #    print( "cmp %.2f %s" % (aa[0], aa[1]) )
            #self.xparent.set_small_text("Recognized shape: %s" % cmp[0][1])

            strx = "%-8s x=%2d y=%2d col=%s cmp=%.f " % \
                            (cmp[0][1], coord[0][0], coord[0][1],
                                    coord[0][2], cmp[0][0], )
            self.xparent.tree.append_treestore(strx)
            print("compare:", strx)
            return cmp[0][1], cmp[0][0]

        return ("")

        #self.aframe += self.bframe
        ## Reference position
        #self.aframe.append((xxx, yyy, 0xff8888ff))

        # Display final image
        #self.invalidate()

    def callb(self, xxx, yyy, kind, fparam):

        #print("callb", xxx, yyy, kind);
        #print("callb", flood.str_enum(kind))

        #return

        bpx = self.xparent.simg.bpx

        row =  bpx * yyy * self.iww
        newcol = None
        try:
            if kind == flood.DOT_YES:
                #newcol = fparam.mark
                #newcol = (0x00, 0x00, 0x00, 0xff)
                pass
            elif kind == flood.DOT_NO:
                #newcol = (0xff, 0xff, 0x00, 0xff)
                pass
            elif kind == flood.DOT_BOUND:
                newcol = (0x00, 0xff, 0xff, 0xff)
                pass
            elif kind == flood.DOT_POP:
                #newcol = (0x00, 0xff, 0xff, 0xff)
                pass
            elif kind == flood.DOT_MARK:
                #newcol = (0xff, 0xff, 0xff, 0xff)
                #self.xparent.simg.drawcross(xxx, yyy, newcol)
                pass
            elif kind == flood.DOT_INVALIDATE:
                pass
            else:
                print("unkown kind in callb")
                #newcol = (0x00, 0x00, 0x00, 0x00)  # transparent
                pass
            if newcol:
                for cnt, aa in enumerate(newcol):
                    self.xparent.simg.buf[cnt + bpx * xxx + row] = newcol[cnt]
                    #self.buf[cnt + bpx * xxx + row] = newcol[cnt]
                pass

            if fparam.cnt % fparam.breath == 0:
                #self.xparent.win2.simg.invalidate()
                #self.xparent.win3.simg.invalidate()
                self.xparent.simg.invalidate()
                if self.xparent.check4.get_active():
                    usleep(1)
        except:
            print("callb", xxx, yyy, kind, sys.exc_info())
            print_exception("callb")

    def _anal_image_worker(self, xxx, yyy, single, addx):

        ''' Work until reasonable matche=s found '''

        allcnt = 0
        thresh = THRESH
        ttt = time.time()

        while True:
            # Limit it to maximum number of iterations
            if allcnt > 6:
                break
            allcnt += 1

            self.gl_dones = {}
            found = self._anal_image_worker2(xxx, yyy, single, thresh, addx)
            if xconfig.verbose:
                print("worker2() found", found, "with thresh", thresh)
                pass

            # BREAK out, no dancing here
            break

            # Image is too simple, break
            if found < 10:
                print("Image too simple")
                break

            # Got optimal count in range, stop
            if found < MAXFOUND and found > MINFOUND:
                break

            if found > MAXFOUND:
                thresh += (found - MAXFOUND) // MINMAXFACT
            else:
                thresh -= (found - MINFOUND) // MINMAXFACT

        print("anal time: %.2f ms" % ((time.time() - ttt) * 1000))

    def _anal_image_worker2(self, xxx, yyy, single, thresh, addx):

        found = 0
        self.islands = []

        # Iterate all shapes
        while True:
            if self.reanal > 1:
                break

            # Set up flood fill parameters
            fparam = flood.floodParm(self.iww, self.ihh, self.darr)
            fparam.callb = self.callb
            fparam.stepx = self.stepx; fparam.stepy = self.stepy
            fparam.thresh = thresh;    fparam.markcol = MARKCOL
            fparam.breath = 30;        fparam.verbose = 0
            fparam.seekstep = self.iww // 50

            if not single:
                # pre step, skip past dones
                xxx += fparam.seekstep
                if xxx >= fparam.iww:
                    xxx = 0; yyy += fparam.seekstep
                if yyy >= self.ihh:
                        break

                xxx, yyy = flood.Seek(xxx, yyy, fparam, self.gl_dones)
                if xxx < 0 or yyy < 0:
                    break
                #print("flood.Seek found at", xxx, yyy)
                pass
            if yyy >= self.ihh:
                break

            if self.xparent.check3.get_active():
                #print("Grey compare")
                fparam.grey = True

            try:
                retf = flood.Flood(xxx, yyy, fparam, self.gl_dones)
            except:
                print_exception("Flood")
                #print("flood:", sys.exc_info())
                break

            if retf == -1:
                break

            if len(fparam.bounds) < 24:
                #print("Short buffer", xxx, yyy, "len",
                #            len(fparam.bounds), fparam.bounds[:4])
                #xxx += 10; yyy += 10
                continue

            #print("flood_one: %.2f ms" % (1000 * (time.time() - ttt)))
            found += 1
            if self.xparent.check4.get_active():
                usleep(100)

            # Process data from flood
            #uls = outline.flush_upleft(fparam.bounds, fparm.minx, fpar.miny)
            #nbs = outline.scale_vectors(uls, outline.ARRLEN)
            #nbounds = outline.scale_magnitude(nbs, outline.ARRLEN)

            # Save last
            coords = (fparam.minx, fparam.miny, fparam.maxx, fparam.maxy,)
            self.xparent.narr = [str(found), coords, fparam.mark,
                                                fparam.body, fparam.bounds]
            # Save cummulative
            #self.sumxx.append(self.xparent.narr)

            # Compare with stock
            #sss = self.compare(nbounds, fparam)
            #if not addx:
            #    self.xparent.simg2.clear()

            # Scan for results
            self.island(fparam.bounds)
            if hasattr(self.xparent, "check2") and self.xparent.check2.get_active():
                if len(nbounds) == 0:
                    msg("No shape yet")

            if single:
                break
            #print()

        #for aa in self.sumxx:
        #    print("aa", aa)
        #    try:
        #        print(aa[0:5], aa[5][0:3], aa[6], aa[7][:2], "...")
        #    except IndexError:
        #        #print("exc sumxx", sys.exc_info())
        #        pass
        #    except:
        #        print("exc sumxx", sys.exc_info())

        # Display results
        lenx = 0
        for aa in self.islands:
            #print(aa.center, aa.bounds, aa.lenorg )
            lenx += len(aa.data)
        #print("lenx", lenx)

        self.sumf.append(self.fname)
        #print("%d segments found." % found)
        self.sumxx.append(self.islands)
        print("%d islands scanned. %d points" % (len(self.islands), lenx))

        return found

    def island(self, nbounds):

        ''' Display one island '''

        #print("nbounds len:", len(nbounds))

        if len(nbounds) == 0:  # Is it an island?
            return
        if len(nbounds) > 300:  # Is it a small island?
            return

        #for aa in nbounds:
        #    print(aa, end = " ")
        #print("nbounds end")

        # Process it
        nbounds2 = outline.sort_by_angles(nbounds)
        nbounds3 = outline.scale_vectors(nbounds2, 16)
        nbounds4 = outline.flush_upleft(nbounds3)

        #print("nbouns4:", end = " ")
        #for aa in nbounds4:
        #    print(aa, end = " ")
        #print()

        col = (0xff, 0xff, 0xff, 0xff)
        col2 = (0x00, 0x00, 0x0, 0xff)

        prev = list(nbounds3[0])
        org = nbounds3[0]
        end  = nbounds3[len(nbounds3)-1]

        for aa in nbounds3:
            #print(aa, end = " ")
            try:
                #print("parms",  prev[0], prev[1], aa[0], aa[1])
                self.xparent.simg2.drawline(prev[0], prev[1], aa[0], aa[1], col)
                #self.xparent.simg2.setcol(aa[0], aa[1], col2)
            except:
                #print("disp nbounds", prev, aa, sys.exc_info())
                pass
            self.xparent.simg2.invalidate()
            if self.xparent.check4.get_active():
                usleep(10   )
            #prev[0] = aa[0]; prev[1] = aa[1]
            prev = list(aa)

        # Connect last to first
        self.xparent.simg2.drawline(end[0], end[1], org[0], org[1], col)

        col3 = (0xff, 0x00, 0x00, 0xff)
        self.xparent.simg2.setcol(org[0], org[1], col3)
        col4 = (0x00, 0xff, 0xff, 0xff)
        self.xparent.simg2.setcol(end[0], end[1], col4)

        #usleep(10)

        # Show center
        #ccc = outline.calc_center(outline.calc_bounds(nbounds))
        #newcol = (0xff, 0x00, 0x00, 0xff)
        #self.xparent.simg2.drawcross(ccc[0], ccc[1], newcol)

        # Add to collection
        islandx = island.IsLand(nbounds4)
        #islandx.dataorg = nbounds
        islandx.lenorg = len(nbounds)
        islandx.bounds = outline.calc_bounds(nbounds)
        islandx.center = nbounds2[0]
        #islandx.center = outline.calc_center(islandx.bounds)
        self.islands.append(islandx)


# EOF
