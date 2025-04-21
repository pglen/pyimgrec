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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

import imgrec.imgrec as imgrec

# --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

class ImgProc():

    def norm_image(self):

        #imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        print( "Norm Image")
        nnn = imgrec.normalize()
        #print(nnn)
        self.invalidate()

    def histo_image(self):

        #imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        #print( "Histogram Image")
        nnn = imgrec.histogram()
        print("histogram", nnn)
        self.invalidate()

    def grey_image(self):

        #imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        print( "Grey Image")
        imgrec.greyen()
        self.invalidate()

    def smooth_image(self):

        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        #print("Smooth")
        old = imgrec.verbose
        imgrec.verbose = 0
        imgrec.smooth(3)
        imgrec.smoothv(3)
        imgrec.verbose = old

        self.invalidate()

    def bri_image(self):

        pixb =  self.image2.get_pixbuf()
        iw = pixb.get_width(); ih = pixb.get_height()
        #print( "img dim", iw, ih)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        arr = pixb.get_pixels()

        imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.bridar(10)

        self.invalidate()

    def dar_image(self):

        imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.bridar(-10)
        self.invalidate()

    def line_image(self):

        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.verbose = 0

        #imgrec.line(10, 20, 10,  50,  0xffff0000)
        #imgrec.line(10, 20, 60, 20,  0xff0000ff)
        #imgrec.line(10, 20, 70, 70, 0xff00ff00)

        imgrec.line(10, 20, 0, 0, 0xff00ff00)

        imgrec.line(0, 0, self.iww, self.ihh, 0xff000000)
        imgrec.line(0, self.ihh, self.iww, 0, 0xff000000)
        arr = []
        for aa in range(30):
            arr.append(random.randint(1, self.iww))
            arr.append(random.randint(1, self.ihh))
        randcol = (0xff000000, 0xffff0000, 0xff00ff00, 0xff0000ff, 0xffffffff)
        idx = random.randint(0, len(randcol)-1)
        imgrec.poly(randcol[idx], tuple(arr))

        imgrec.verbose = 0
        self.invalidate()

    def frame_image(self):

        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.verbose = 0
        imgrec.frame(10, 10, 50, 50, 0xff0000ff)
        imgrec.verbose = 0
        self.invalidate()

    def blank_image(self):

        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        #imgrec.verbose = 1
        imgrec.blank() #color=0xffffffff)
        imgrec.verbose = 0
        #self.pb = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
        #                    True, 8, iww, ihh)
        #self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.iww, self.ihh)
        #
        self.invalidate()

    def walk_image(self, xx, yy):

        #print( "walk_image() dim =", iw, ih, "pos =", xx, yy )
        imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        ret2 = imgrec.walk(int(xx), int(yy))
        print("ret2", ret2)
        self.invalidate()

    def edge_image(self):

        #imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.edge()
        self.invalidate()

# Refresh image from original
    def get_img(self):

        print( "Do not call")
        return

        #iw = self.image.get_pixbuf().get_width()
        #ih = self.image.get_pixbuf().get_height()
        #ww, hh = self.get_size_request()
        #print( "Window Size:", ww, hh)
        #print( "Image Size:", iw, ih)
        #if iw > ih:
        #    self.scalef = float(ww)/iw
        #else:
        #    self.scalef = float(hh)/ih
        #    iww = iw * self.scalef
        #self.image.get_pixbuf().scale(self.image2.get_pixbuf(), 0, 0, ww, hh,
        #                    0, 0, self.scalef, self.scalef, Gtk.gdk.INTERP_TILES)
        #self.image.set_from_image(self.image2)

    def test_butt(self):
        #print("test_butt")
        imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        xdarr = {}; glarr = {}
        # Fill in 2D array
        for yy in range(self.ihh):
            offs = yy * self.iww * BPX
            for xx in range(self.iww):
                val = []
                for cc in range(BPX):
                    val.append(self.buf[offs + xx * BPX + cc])
                self._add_to_dict(xdarr, xx, yy, val)
        #print("xdarr len", len(xdarr) )

        fparam = flood.floodParm(self.iww, self.ihh, xdarr)
        imgrec.seek(10, 10, fparam, glarr)

# EOF
