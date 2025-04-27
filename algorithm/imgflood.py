#!/usr/bin/env python
#
# pylint: disable=C0103 disable=C0321 disable=C0116

import sys, time

DIVIDER     = 16                 # How many divisions, mostly for testing
THRESH      = 20                 # Color diff for boundary
MARKCOL     = 180                # Color counts as mark
MAXFOUND    = 200                # Max islas (inactive)
MINFOUND    = 150                # Min islas
MINMAXFACT  = 3                  # Change for resacn
MARKDIFF    = 30                 #
BPX         = 4                  # Bytes per pixel

import pyimgutils

import  algorithm.flood  as flood
import  algorithm.outline as outline

import imgrec.imgrec as imgrec

class Flooder():

    ''' Class to drive floodfill '''

    def __init__(self):

        self.gl_dones = {}
        self.darr = {}
        self.markcol = None
        self.thresh = 60
        self.grid = False
        self.animate = False
        self.verbose = 0
        self.grey = False
        self.treestore = None
        self.xparent = None
        self.single = False
        self.addx = False
        self.reanal = False
        self.stepx = 1
        self.stepy = 1
        self.divider = DIVIDER
        self.islands = []
        self.ihh = 0
        self.iww = 0
        self.buf = []
        self.bpx = 0
        pass

    # --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

    def anal_image(self, xxx, yyy):

        # New outputs
        self.islands = []
        self.darr = {}

        imgrec.verbose = self.verbose
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        self.stepx = float(self.iww)/self.divider
        self.stepy = float(self.ihh)/self.divider

        #imgrec.verbose = 1
        #avg = imgrec.average()
        if self.verbose:
            print( "Anal image xxx:", xxx, "yyy:", yyy, "www", self.iww, "hhh", self.ihh,
                        "thresh", self.thresh, "markcol", self.markcol)
            #print("divider", self.divider)

        #imgrec.verbose = 0

        if self.xparent:
            self.xparent.tree.append_treestore("Anal image xxx: %d yyy: %d" % (xxx, yyy))

        # Draw grid:
        if self.grid:
            try:
                #print("Grid")
                for xx in range(self.divider):
                    hor = int(xx * self.stepx)
                    imgrec.line(hor, 0, hor, self.ihh, 0xff888888)
                for yy in range(self.divider):
                    ver = int(yy * self.stepy)
                    imgrec.line(0, ver, self.iww-1, ver, 0xff888888)
                #self.invalidate()
                #pyimgutils.usleep(10)
            except:
                pyimgutils.print_exception("grid")

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
        #    self.invalidate(); pyimgutils.usleep(.1)
        #return

        self.reanal += 1
        if self.reanal > 1:
            print("Stopping Anal .. please wait")
            flood.gl_reenter += 1
            self.reanal = 0
            return

        # See if repeated request for scanning the same image
        #if not self.laststate & Gdk.ModifierType.SHIFT_MASK:
        #    self.xparent.simg.clear()
        #    #self.xparent.win2.simg.clear()
        #    self.gl_dones = {}

        self._anal_image_worker(xxx, yyy)
        self.reanal = 0

        #self.aframe += self.bframe
        ## Reference position
        #self.aframe.append((xxx, yyy, 0xff8888ff))

        # Display final image
        #self.invalidate()

    def _add_to_dict(self, xdic, xxx, yyy, val):
        try:
            xdic[yyy][xxx] = val
        except KeyError:
            xdic[yyy] = {}
            xdic[yyy][xxx] = val
        except:
            print( "add to dict", sys.exc_info())

    def _anal_image_worker(self, xxx, yyy):

        ''' Work until reasonable matche(s) found '''

        allcnt = 0
        ttt = time.time()

        while True:
            # Limit it to maximum number of iterations
            if allcnt > 6:
                break
            allcnt += 1

            self.gl_dones = {}
            found = self._anal_image_worker2(xxx, yyy)
            if self.verbose:
                print("worker2() found", found, "with thresh", self.thresh)

            # BREAK out, no dancing here for now
            break

            # Image is too simple, break
            if found < 10:
                print("Image too simple")
                break

            # Got optimal count in range, stop
            if found < MAXFOUND and found > MINFOUND:
                break

            if found > MAXFOUND:
                self.thresh += (found - MAXFOUND) // MINMAXFACT
            else:
                self.thresh -= (found - MINFOUND) // MINMAXFACT

        print("anal time: %.2f ms" % ((time.time() - ttt) * 1000))

    def _anal_image_worker2(self, xxx, yyy):

        found = 0

        # Iterate all shapes
        while True:
            if self.reanal > 1:
                break

            # Set up flood fill parameters
            fparam = flood.floodParm(self.iww, self.ihh, self.bpx, self.darr)
            fparam.callb = callb
            fparam.stepx = self.stepx
            fparam.stepy = self.stepy
            fparam.thresh = self.thresh
            fparam.markcol = MARKCOL
            fparam.breath = 30
            fparam.xparent = self.xparent
            fparam.verbose = self.verbose
            fparam.seekstep = self.iww // 50

            if not self.single:
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
            if yyy >= self.ihh:
                break

            if self.grey:
                #print("Grey compare")
                fparam.grey = True

            try:
                retf = flood.Flood(xxx, yyy, fparam, self.gl_dones)
            except:
                pyimgutils.print_exception("Flood")
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
            if self.animate:
                pyimgutils.usleep(100)

            # Process data from flood
            #uls = outline.flush_upleft(fparam.bounds, fparm.minx, fpar.miny)
            #nbs = outline.scale_vectors(uls, outline.ARRLEN)
            #nbounds = outline.scale_magnitude(nbs, outline.ARRLEN)

            # Save last
            coords = (fparam.minx, fparam.miny, fparam.maxx, fparam.maxy,)

            if self.xparent:
                self.xparent.narr = [str(found), coords, fparam.mark,
                                                fparam.body, fparam.bounds]
            # Scan for results
            self.island(fparam.bounds)
            if self.single:
                break

        # Display results
        lenx = 0
        for aa in self.islands:
            #print(aa.center, aa.bounds, aa.lenorg )
            lenx += len(aa.data)
        #print("lenx", lenx)
        #print("%d segments found." % found)
        print("%d islands scanned. %d points" % (len(self.islands), lenx))

        if self.verbose > 1:
            for aa in self.islands:
                print(aa.dump())
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
        col2 = (0x00, 0x00, 0x00, 0xff)

        prev = list(nbounds3[0])
        org = nbounds3[0]
        end  = nbounds3[len(nbounds3)-1]

        for aa in nbounds3:
            #print(aa, end = " ")
            try:
                #print("parms",  prev[0], prev[1], aa[0], aa[1])
                self.xparent.simg2.drawline(prev[0], prev[1], aa[0], aa[1], col)
                #self.xparent.simg3.setcol(aa[0], aa[1], col2)
            except:
                #print("disp nbounds", prev, aa, sys.exc_info())
                pass
            if self.xparent:
                if self.animate:
                    self.xparent.simg2.invalidate()
                    self.xparent.simg3.invalidate()
                    pyimgutils.usleep(10   )
            prev = list(aa)

        # Connect last to first
        if self.xparent:
            cole = (0xff, 0x00, 0x00, 0xff)
            self.xparent.simg2.drawline(end[0], end[1], org[0], org[1], cole)
            #self.xparent.simg3.drawline(end[0], end[1], org[0], org[1], cole)
            col3 = (0xff, 0x00, 0x00, 0xff)
            #self.xparent.simg3.setcol(org[0], org[1], col3)
            col4 = (0x00, 0xff, 0xff, 0xff)
            #self.xparent.simg3.setcol(end[0], end[1], col4)

            self.xparent.simg2.invalidate()
            self.xparent.simg3.invalidate()

        minxx, minyy, maxxx, maxyy = outline.calc_bounds(nbounds3)

        # Show boundaries
        newcol = (0xff, 0xff, 0x00, 0xff)
        #self.xparent.simg3.drawline(minxx, minyy, minxx, maxyy, newcol)
        #self.xparent.simg3.drawline(maxxx, maxyy, maxxx, minyy, newcol)
        #self.xparent.simg3.drawline(maxxx, minyy, minxx, minyy, newcol)
        #self.xparent.simg3.drawline(maxxx, maxyy, minxx, maxyy, newcol)

        # Show center
        #cccc = outline.calc_center((minxx, minyy, maxxx, maxyy))
        #newcol = (0x00, 0x00, 0xff, 0xff)
        #self.xparent.simg3.drawcross(cccc[0], cccc[1], newcol, 2)

        # Show boundary members
        eeee = outline.find_extremes(nbounds3)
        #print(eeee, end = " ")

        # Add to collection
        islandx = IsLand(nbounds4)
        #islandx.dataorg = nbounds
        islandx.lenorg = len(nbounds)
        islandx.bounds = outline.calc_bounds(nbounds)
        #islandx.center = nbounds2[0]
        islandx.center = outline.calc_center(islandx.bounds)
        self.islands.append(islandx)

    def recog2(self, sumx, sumf):

        ref =  sumx[0]
        for aa in range(1, len(sumx)):
            targ = sumx[aa]

            cmp_extents


    def recog(self, sumx, sumf):

        if len(sumx) < 2:
            print("Recog: must have more than one scan")
            return

        ref =  sumx[0]
        print("ref len:", len(ref), sumf[0])
        for aa in range(1, len(sumx)):
            matchsum = 0; ressum = []
            targ = sumx[aa]
            print("targ len: ", len(targ), sumf[aa])
            #print("compare:", aa, sumf[aa])
            for cnt, curr in enumerate(ref):
                for cnt2, curr2 in enumerate(targ):
                    res = curr.cmp(curr2, 1)
                    #print("curr:", curr.center, "curr2:", curr2.center)
                    #print("len res:", len(res))
                    if res[0] > 3 or res[1] > 3:
                        continue
                    ressum.append((cnt, cnt2, res))
                    #print("isl:", cnt, cnt2, "res:", res)

            #for sss in ressum:
            #    rr = ref[sss[0]]; tt = targ[sss[1]]
            #    print(sss, rr.bounds[:2], tt.bounds[:2])

            ordxy = []; matchxy = [];
            for aaaa in ressum:
                for bbbb in ressum:
                    if aaaa == bbbb:
                        #print("aaaa == bbbb", aaaa)
                        continue
                    rr = ref[aaaa[0]]; tt = targ[bbbb[1]]

                    xx = 0; yy = 0
                    deltax = rr.bounds[0] - tt.bounds[0]
                    deltay = rr.bounds[1] - tt.bounds[1]
                    #print("deltas at:", aaaa, bbbb, "val:", deltax, deltay)
                    if (deltax, deltay) not in ordxy:
                        ordxy.append((deltax, deltay))
                    else:
                        matchxy.append((deltax, deltay, aaaa, bbbb))
            print("matchxy len:", len(matchxy))
            #if matchxy:
            #    print("matchxy:", matchxy)
        self.xparent.simg3.invalidate()
        print("end recog")

def callb(xxx, yyy, kind, fparam):

    #print("callb", xxx, yyy, kind)
    #print("callb", flood.str_enum(kind))
    #return

    newcol = None
    row =  fparam.bpx * yyy * fparam.iww
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
        elif kind == flood.DOT_POP:
            #newcol = (0x00, 0xff, 0xff, 0xff)
            pass
        elif kind == flood.DOT_MARK:
            #newcol = (0xff, 0xff, 0xff, 0xff)
            #fparam.xparent.simg.drawcross(xxx, yyy, newcol)
            pass
        elif kind == flood.DOT_INVALIDATE:
            pass
        else:
            print("unkown kind in callb")
            #newcol = (0x00, 0x00, 0x00, 0x00)  # transparent
        if newcol:
            for cnt in range(len(newcol)):
                if fparam.xparent:
                    fparam.xparent.simg.buf[cnt + fparam.bpx * xxx + row] = \
                        newcol[cnt]
                #self.buf[cnt + bpx * xxx + row] = newcol[cnt]

        if fparam.cnt % fparam.breath == 0:
            #self.xparent.win2.simg.invalidate()
            #self.xparent.win3.simg.invalidate()
            if fparam.xparent:
                fparam.xparent.simg.invalidate()
                if fparam.xparent.check4.get_active():
                    pyimgutils.usleep(1)
    except:
        print("callb", xxx, yyy, kind, sys.exc_info())
        pyimgutils.print_exception("callb")


def compare(self, xarr, fbounds):

    # Compare shape with saved ones
    cmp = []; coord = []
    for cc in self.xparent.shapes:
        res = outline.cmp_arrays(cc[4], xarr)
        #print("comp", res, cc[0])
        cmp.append( (res, cc[0]) )
        coord.append( (fbounds.minx, fbounds.miny, fbounds.mark,) )
    if len(cmp) != 0:
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

    return ""

class IsLand():
    def __init__(self, data):
        self.data = data
        self.bounds = None
        self.center = None
        self.lenorg = 0
        self.data = data

    #def __str__(self):
    #    return(self.__qualname__, "\n<class IsLand> at " + str((self.center)))

    #def __repr__(self):
    #    return ("<class " + IsLand.__name__ +  "> at " + str(self.center))

    def dump(self):
        strx =  "cnt: %s " % str(self.center)
        strx += "bnd: %s " % str(self.bounds)
        strx += "dat: %s " % str(self.data[:3])
        return strx

    def cmp_extents(self, isl2, diff = 1):
        #print(self.bounds, isl2.bounds)
        diff = 0
        for aa in range(self.bounds):
            diff += abs(self.bounds[aa] - isl2.bounds[aa])
            #print("end")
        return diff

    def _cmp_one(self, item1, item2):
        tmp   = item1[0] - item2[0]
        tmp2  = item1[1] - item2[1]
        return (tmp, tmp2)

    def cmp(self, isl2, diff = 1):
        res = [0, 0]
        for aa in range(len(self.data)):
            tmp, tmp2  = self._cmp_one(self.data[aa], isl2.data[aa])
            #print(self.data[aa], "->", isl2.data[aa], (tmp, tmp2), end = "   ")
            res[0] += abs(tmp); res[1] += abs(tmp2)
        return res

    def find_similar(self, isl2, diff = 1):

        #print("find similar", isl2)
        matches = []
        for aa in range(len(self.data)):
            for bb in range(len(isl2.data)):
                tmp, tmp2  = self._cmp_one(self.data[aa], isl2.data[bb])
                #print(tmp, tmp2, end = " " )
                if abs(tmp) < diff and abs(tmp2) < diff:
                    #print(aa, bb, "->", tmp, tmp2, end = " ; ")
                    matches.append((aa, bb))
            #print("end")
        return matches

# EOF
