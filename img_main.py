#!/usr/bin/env python

# Main image for pyimgrec. Creates wwo images image and image2. Manipulate / draw image2
#
# The floowing code will squash warnings if you have no pynum installed:
#
# import warnings
# with warnings.catch_warnings():
#    warnings.simplefilter("ignore")
# arr = pixb.get_pixels_array()

import os, sys, getopt, signal, array, math
import time, random
#import gobject, gtk, pango,

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

from pyimgutils import *
from norm_outline import *

import  algorithm.flood     as flood
import  algorithm.rectflood as rectflood
import  treehand

try:
    import pyimgrec.imgrec as imgrec
except:
    pass


MAG_FACT    = 2
MAG_SIZE    = 300

DIVIDER     = 256                # How many divisions
TRESH       = 50                 # Color difference

def printarr(arr):
    for aa in arr:
        print( "%.2d %d  " % (aa[0], aa[1]),)
    print()

class img_main(Gtk.DrawingArea):

    def __init__(self, xparent, wwww = 100, hhhh = 100):

        self.xparent = xparent
        Gtk.DrawingArea.__init__(self);

        self.pb = GdkPixbuf.Pixbuf.new \
                   (GdkPixbuf.Colorspace.RGB, True, 8,
                         MAG_SIZE / MAG_FACT , MAG_SIZE / MAG_FACT)
        self.pb.fill(0x888888ff)

        self.divider = DIVIDER;
        self.wwww = wwww; self.hhhh = hhhh
        self.set_size_request(wwww, hhhh)

        self.annote = []; self.aframe = []; self.bframe = []
        self.atext = []

        self.mag = False
        self.event_x = self.event_y = 0
        self.image  = None
        #self.colormap = Gtk.get_default_colormap()
        #self.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)
        #self.area.set_events(Gtk.gdk.ALL_EVENTS_MASK)

        #self.set_events(  Gtk.gdk.POINTER_MOTION_MASK |
        #                    Gtk.gdk.POINTER_MOTION_HINT_MASK |
        #                    Gtk.gdk.BUTTON_PRESS_MASK |
        #                    Gtk.gdk.BUTTON_RELEASE_MASK |
        #                    Gtk.gdk.KEY_PRESS_MASK |
        #                    Gtk.gdk.KEY_RELEASE_MASK |
        #                    Gtk.gdk.FOCUS_CHANGE_MASK )

        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.area_button)
        #self.connect("expose-event", self.expose)
        self.connect("draw", self.draw)
        self.connect("motion-notify-event", self.area_motion)

    def add_to_dict(self, xdic, hor, ver, med):
        try:
            xdic[hor][ver] = med
        except KeyError:
            xdic[hor] = {}
            xdic[hor][ver] = med
        except:
            print( "add to dict", sys.exc_info())

    def area_motion(self, area, event):
        #print(  event.x, event.y)
        self.event_x = event.x
        self.event_y = event.y
        if self.mag:
            self.invalidate()

    # Paint the image
    def draw(self, me, gc):

        #print("expose:", "GC", me, gc, me.get_window())
        rc = self.get_allocation()
        #print(dir(gc))

        #gc = Gdk.GC(self.window);
        #colormap = Gtk.widget_get_default_colormap()
        #self.window.draw_pixbuf(gc, self.image2.get_pixbuf(), 0, 0, 0, 0)
        #self.draw_pixbuf(gc, self.image2.get_pixbuf(), 0, 0, 0, 0)

        # Paint annotations:
        for xx, yy, txt in self.atext:
            self.pangolayout.set_text(txt)
            #self.window.draw_layout(gc, xx, yy, self.pangolayout)

        for xx, yy, col in self.aframe:
            colormap = Gtk.widget_get_default_colormap()
            gc.set_foreground(colormap.alloc_color("#%06x" % (col & 0xffffff) ))
            #self.window.draw_rectangle(gc, False, int(xx*self.stepx), int(yy*self.stepy),
            #                    int(self.stepx), int(self.stepy))

        for xx, yy, col in self.bframe:
            colormap = Gtk.widget_get_default_colormap()
            gc.set_foreground(colormap.alloc_color("#%06x" % (col & 0xffffff) ))
            #self.window.draw_rectangle(gc, False, int(xx*self.stepx), int(yy*self.stepy),
            #                    int(self.stepx), int(self.stepy))

        for xx, yy, func in self.annote:
            #func(self.window)
            pass

        if self.mag:
            #print(  "paint mag:", self.event_x, self.event_y)
            #iw = self.image.get_pixbuf().get_width()
            #ih = self.image.get_pixbuf().get_height()
            iw2 = self.image2.get_pixbuf().get_width()
            ih2 = self.image2.get_pixbuf().get_height()
            #print( iw, ih, iw2, ih2)

            magsx =  MAG_SIZE; magsy = MAG_SIZE

            rendx =  self.event_x - MAG_SIZE / MAG_FACT;
            if rendx < 0: rendx = 0
            rendy =  self.event_y - MAG_SIZE / MAG_FACT;
            if rendy < 0: rendy = 0

            src_x = self.event_x  - MAG_SIZE / (2*MAG_FACT)
            if src_x + MAG_SIZE >= iw2: src_x = iw2 - MAG_SIZE / MAG_FACT;
            if src_x < 0: src_x = 0

            src_y = self.event_y - MAG_SIZE / (2*MAG_FACT)
            if src_y < 0: src_y = 0
            if src_y + MAG_SIZE >= ih2: src_y = ih2 - MAG_SIZE / MAG_FACT;

            #print( self.image2.get_pixbuf().get_has_alpha(), self.pb.get_has_alpha())
            #print( "src_x", src_x, "src_y", src_y)

            pixb = self.image2.get_pixbuf()
            try:
                # Bug in the scaling routine, fetching buffer and scaling it new
                '''pixb.scale(self.pb, 0, 0, MAG_SIZE, MAG_SIZE, int(src_x), int(src_y),
                        MAG_FACT, MAG_FACT, Gtk.gdk.INTERP_NEAREST)'''

                pixb.copy_area(int(src_x), int(src_y),
                        MAG_SIZE/MAG_FACT, MAG_SIZE/MAG_FACT, self.pb, 0, 0)
                self.pb2 = self.pb.scale_simple(MAG_SIZE, MAG_SIZE, Gtk.gdk.INTERP_NEAREST)

            except:
                print_exception("get mag")

            '''self.window.draw_pixbuf(gc, self.pb,
                        0, 0, int(self.event_x), int(self.event_y),
                            int(magsx), int(magsy))'''

            #gc.draw_pixbuf(gc, self.pb2,
            #            0, 0, int(rendx), int(rendy), int(magsx), int(magsy))
        else:
            try:
                Gdk.cairo_set_source_pixbuf(gc, self.pb, 0, 0)
                gc.paint()

                #    0, 0, int(rendx), int(rendy), int(magsx), int(magsy))
            except:
                print(sys.exc_info())
    # --------------------------------------------------------------------
    def key_press_event(self, win, event):

        #print( "img key_press_event", win, event)
        if event.state & Gtk.gdk.MOD1_MASK:
            if event.keyval == Gdk.KEY_x or event.keyval == Gtk.KEY_X:
                sys.exit(0)

        if event.keyval == Gtk.keysyms.Escape:
            self.mag = False
            self.invalidate()

    def clear_annote(self):
        self.annote = [];        self.atext = []
        self.aframe = [];        self.bframe = []
        self.invalidate()

    def  area_button(self, win, event):

        self.window.set_cursor(Gtk.gdk.Cursor(Gtk.gdk.CLOCK))

        #rc = self.get_allocation()
        #print( "img button", event.x, event.y, rc.width, rc.height)
        #stepx = float(rc.width)/self.divider; stepy = float(rc.height)/self.divider;
        #print( event.x / stepx,      event.y / stepy)
        self.anal_image(int(event.x / self.stepx), int(event.y / self.stepy))
        self.window.set_cursor(None)

    def toggle_mag(self):
        self.mag = not self.mag
        if self.mag and self.event_x == 0:
            rc = self.get_allocation()
            self.event_x = rc.width/2; self.event_y = rc.height/2
        self.invalidate()

    def invalidate(self):
        winn = self.window
        ww, hh = winn.get_size()
        rect = Gtk.gdk.Rectangle(0, 0, ww, hh)
        winn.invalidate_rect(rect, False)


    # --------------------------------------------------------------------
    # Load image

    def load(self, fname):

        try:
            self.fname = fname
            self.image = Gtk.Image()
            self.image.set_from_file(fname)

            pix = self.image.get_pixbuf()
            iww = pix.get_width(); ihh = pix.get_height()
            self.set_size_request(iww, ihh)
            self.image2 = Gtk.Image()
            pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                            True, 8, iww, ihh)
            pix.copy_area(0, 0, iww, ihh, pixbuf, 0, 0)
            self.image2.set_from_pixbuf(pixbuf)

            # Set imagerec pixel buffer to image2
            pixb =  self.image2.get_pixbuf()
            self.pb = pixb
            #arr = pixb.get_pixels()
            #print(type(arr))
            #imgrec.anchor(arr)

            self.stepx = float(imgrec.width)/self.divider;
            self.stepy = float(imgrec.height)/self.divider;
        except:
            print("load", sys.exc_info())
            print_exception("load")


    def refresh(self):
        pix = self.image.get_pixbuf()
        iww = pix.get_width(); ihh = pix.get_height()
        pixbuf = self.image2.get_pixbuf()
        pix.copy_area(0, 0, iww, ihh, pixbuf, 0, 0)

    # Refresh image from original
    def get_img(self):

        print( "Do not call")
        return

        iw = self.image.get_pixbuf().get_width()
        ih = self.image.get_pixbuf().get_height()
        #ww, hh = self.get_size_request()
        #print( "Window Size:", ww, hh)
        print( "Image Size:", iw, ih)
        if iw > ih:
            self.scalef = float(ww)/iw
        else:
            self.scalef = float(hh)/ih
            iww = iw * self.scalef

        #self.image.get_pixbuf().scale(self.image2.get_pixbuf(), 0, 0, ww, hh,
        #                    0, 0, self.scalef, self.scalef, Gtk.gdk.INTERP_TILES)

        #self.image.set_from_image(self.image2)

    # --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

    def norm_image(self):

        pixb =  self.image2.get_pixbuf()
        iw = pixb.get_width(); ih = pixb.get_height()
        #print( "img dim", iw, ih)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        arr = pixb.get_pixels_array()

        #imgrec.verbose = 1
        imgrec.anchor(arr)

        #print( "Norm Image")
        #imgrec.normalize(1,2,3)
        imgrec.bw(1,2,3)

        rc = self.get_allocation()
        self.window.invalidate_rect(rc, False)

    def smooth_image(self):

        pixb =  self.image2.get_pixbuf()
        iw = pixb.get_width(); ih = pixb.get_height()
        #print( "img dim", iw, ih)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        arr = pixb.get_pixels_array()

        imgrec.verbose = 1
        imgrec.anchor(arr)
        imgrec.smooth(10)
        self.invalidate()

    def bri_image(self):

        pixb =  self.image2.get_pixbuf()
        iw = pixb.get_width(); ih = pixb.get_height()
        #print( "img dim", iw, ih)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        arr = pixb.get_pixels_array()

        imgrec.verbose = 1
        imgrec.anchor(arr)

        imgrec.bridar(10)

        self.invalidate()


    def dar_image(self):

        pixb =  self.image2.get_pixbuf()
        iw = pixb.get_width(); ih = pixb.get_height()
        #print( "img dim", iw, ih)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        arr = pixb.get_pixels_array()

        imgrec.verbose = 1
        imgrec.anchor(arr)

        imgrec.bridar(-10)

        self.invalidate()


    def blank_image(self):

        pixb =  self.image2.get_pixbuf()
        iw = pixb.get_width(); ih = pixb.get_height()
        #print( "img dim", iw, ih)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
        arr = pixb.get_pixels_array()

        imgrec.verbose = 1
        imgrec.anchor(arr)

        imgrec.blank(color=0xffffffff)

        self.invalidate()

    def walk_image(self, xx, yy):

        #print( "walk_image() dim =", iw, ih, "pos =", xx, yy )
        arr = self.image2.get_pixbuf().get_pixels_array()
        imgrec.verbose = 1
        imgrec.anchor(arr)
        imgrec.walk(int(xx), int(yy))
        self.invalidate()

    def edge_image(self):

        arr = self.image2.get_pixbuf().get_pixels_array()
        #imgrec.verbose = 1
        imgrec.anchor(arr)

        imgrec.edge()
        self.invalidate()

    def invalidate(self):
        rc = self.get_allocation()
        #self.window.invalidate_rect(rc, False)
        #self.invalidate_rect(rc, False)

    # --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

    def anal_image(self, xxx = -1, yyy = -1):

        # Get img props.
        pixb =  self.image2.get_pixbuf()
        arr = pixb.get_pixels_array()
        iw = pixb.get_width(); ih = pixb.get_height()

        #imgrec.verbose = 1
        imgrec.anchor(arr)

        #print( "dims", imgrec.dim1, imgrec.dim2, imgrec.dim3)
        #print( "width", imgrec.width, "height", imgrec.height)

        #hstep = imgrec.width / self.divider; vstep = imgrec.height / self.divider
        #hstep = float(iw) / self.divider; vstep = float(ih) / self.divider
        #print( "steps", hstep, vstep, self.stepx, self.stepy)

        # Interpret defaults:
        if xxx == -1: xxx = self.divider/2
        if yyy == -1: yyy = self.divider/2

        #print( "Anal image", xxx, yyy, self.stepx, self.stepy)

        try:
            # Draw grid:
            if self.xparent.check1.get_active():
                for xx in range(self.divider):
                    hor = int(xx * self.stepx)
                    imgrec.line(hor, 0, hor, imgrec.height, 0xff888888)
                for yy in range(self.divider):
                    ver = int(yy * self.stepy)
                    imgrec.line(0, ver, imgrec.width, ver, 0xff888888)
                self.invalidate()
        except:
            print_exception("grid")

        # Get an array of median values
        try:
            xcnt = 0; ycnt = 0; darr = {};
            for yy in range(self.divider):
                xcnt = 0
                for xx in range(self.divider):
                    hor = int(xx * self.stepx); ver = int(yy * self.stepy)
                    #print( "hor", hor, "ver", ver)
                    med = imgrec.median(hor, ver, int(hor + self.stepx), int(ver + self.stepy))
                    #imgrec.blank(hor, ver, hor + stepx, ver + stepy, med)
                    med &= 0xffffff;  # Mask out alpha

                    # Remember it in a dict
                    self.add_to_dict(darr, xcnt, ycnt, med)
                    xcnt += 1
                ycnt += 1;
        except:
            print_exception("median")


        if self.xparent.radio1.get_active():
            self.xparent.clear_small_img()
            # Set up flood fill
            fparm = flood.floodParm(self.divider, darr);
            #fparm.stepx = self.stepx; fparm.stepy = self.stepy
            fparm.tresh = TRESH
            fparm.inval = self.show_prog;    # Progress feedback
            fparm.colx = int(random.random() * 0xffffff)
            flood.flood(xxx, yyy, fparm)

            # Only draw relative shape
            maxx = fparm.maxx - fparm.minx; maxy = fparm.maxy - fparm.miny
            #print( "maxx maxy", maxx, maxy)
            #print( "minx miny", minx, miny)
            img = Gtk.Image()
            pixbuf = Gtk.gdk.Pixbuf(Gtk.gdk.COLORSPACE_RGB, True, 8,  maxx+1, maxy+1)
            pixbuf.fill(0x000000ff)
            arr = pixbuf.get_pixels_array()

            #print( "bounds",  fparm.bounds)

            self.xparent.narr = norm_array(fparm)
            #print(  "narr len ", len(self.xparent.narr))

            # Animate, so we see the correct winding
            for bb in self.xparent.narr:
                    #arr[aa[1] - miny, aa[0] - minx, 0] = 0x7f0000ff
                    arr[bb[1], bb[0], 0] = 0xff
                    arr[bb[1], bb[0], 1] = 0x00
                    arr[bb[1], bb[0], 2] = 0x00
                    arr[bb[1], bb[0], 3] = 0xff
                    #print( bb[0], bb[1], "  ",)
                    pixbuf2 = Gtk.gdk.pixbuf_new_from_array(arr, Gtk.gdk.COLORSPACE_RGB, 8)
                    img.set_from_pixbuf(pixbuf2)
                    self.xparent.fill_small_img(img)
                    usleep(3)

            # Compare shape with saved ones
            cmp = []
            for cc in self.xparent.shapes:
                res = cmp_arrays(cc[1], self.xparent.narr)
                cmp.append((res, cc[0]))

            # Dictionary yet?
            if(len(cmp)):
                cmp.sort()
                print( cmp        )
                self.xparent.set_small_text("Recognized shape: %s" % cmp[0][1])

            self.show_prog(fparm)

        elif self.xparent.radio2.get_active():
            # Set up flood fill
            fparm = rectflood.floodParm(self.divider, darr);
            #fparm.stepx = self.stepx; fparm.stepy = self.stepy
            fparm.tresh = TRESH
            fparm.inval = self.show_prog;    # Progress feedback
            fparm.colx = int(random.random() * 0xffffff)
            #fparm.verbose = True
            fparm.breath = 4
            rectflood.rectflood(xxx, yyy, fparm)
            self.show_prog(fparm)

        else:
            #print( "No opeartion selected")
            self.walk_image(self.event_x, self.event_y)

        self.aframe += self.bframe

        # Reference position
        self.aframe.append((xxx, yyy, 0xff8888ff))

        # Display final image
        self.invalidate()

    def show_prog(self, fparm):
        rc = self.get_allocation()
        minx =  rc.width;  miny = rc.height;  maxx = maxy = 0

        self.bframe = []
        #print( "Showing progress:", "minx", minx, "miny", miny, "len", len(fparm.spaces))
        for aa in fparm.spaces.keys():
            #print( aa,)
            if fparm.spaces[aa]:
                self.bframe.append((aa[0], aa[1], fparm.colx))
                if minx > aa[0]: minx = aa[0]
                if miny > aa[1]: miny = aa[1]
                if maxx < aa[0]: maxx = aa[0]
                if maxy < aa[1]: maxy = aa[1]

        #print( "minx", minx, "maxx", maxx, "miny", miny, "maxy", maxy)
        #print( "inval", minx * self.stepx, miny * self.stepy,
        #                (maxx + 1)* self.stepx, (maxy+1) * self.stepy )
        rect = Gtk.gdk.Rectangle(int(minx * self.stepx), int(miny * self.stepy),
                        int((maxx + 1) * self.stepx),
                                int((maxy + 1)  * self.stepy))

        self.window.invalidate_rect(rect, False)
        #self.invalidate()
        usleep(.005)


















