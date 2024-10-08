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

from pyimgutils import *
from norm_outline import *
import  treehand

try:
    import imgrec.imgrec as imgrec
except:
    pass

import  algorithm.flood     as flood
import  algorithm.rectflood as rectflood

MAG_FACT    = 2
MAG_SIZE    = 300

#DIVIDER     = 256                # How many divisions
DIVIDER     = 25                 # How many divisions
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

        #print("expose:",  gc)
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
            #colormap = Gtk.widget_get_default_colormap()
            #gc.set_foreground(colormap.alloc_color("#%06x" % (col & 0xffffff) ))
            #self.window.draw_rectangle(gc, False, int(xx*self.stepx), int(yy*self.stepy),
            #                    int(self.stepx), int(self.stepy))
            pass

        for xx, yy, col in self.bframe:
            #colormap = Gtk.widget_get_default_colormap()
            #gc.set_foreground(colormap.alloc_color("#%06x" % (col & 0xffffff) ))
            #self.window.draw_rectangle(gc, False, int(xx*self.stepx), int(yy*self.stepy),
            #                    int(self.stepx), int(self.stepy))
            pass

        for xx, yy, func in self.annote:
            #func(self.window)
            pass

        if self.mag:
            print(  "paint mag:", self.event_x, self.event_y)
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
                self.pb2 = self.pb.scale_simple(MAG_SIZE, MAG_SIZE,
                                GdkPixbuf.InterpType.NEAREST)
            except:
                print_exception("get mag")

            '''self.window.draw_pixbuf(gc, self.pb,
                        0, 0, int(self.event_x), int(self.event_y),
                            int(magsx), int(magsy))'''

            #gc.draw_pixbuf(gc, self.pb2,
            #            0, 0, int(rendx), int(rendy), int(magsx), int(magsy))

        try:
            #Gdk.cairo_set_source_pixbuf(gc, self.pb2, 0, 0)
            #gc.paint()
            pass
        except:
            print("bm draw", sys.exc_info())

        gc.set_source_surface(self.surface)
        gc.paint()

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
        rect = self.get_allocation()
        rect = Gdk.Rectangle(rect)
        #winn.invalidate_rect(rect, False)
        self.queue_draw()
        #self.queue_draw_area(rect)

    # --------------------------------------------------------------------

    def load(self, fname):

        ''' Load image file '''

        try:
            self.fname = fname
            self.image = Gtk.Image()
            self.image.set_from_file(fname)

            pix = self.image.get_pixbuf()
            self.iww = pix.get_width();
            self.ihh = pix.get_height()
            self.set_size_request(self.iww, self.ihh)
            self.image2 = Gtk.Image()

            pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                            True, 8, self.iww, self.ihh)
            pixbuf2 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                            True, 8, self.iww, self.ihh)
            pix.copy_area(0, 0, self.iww, self.ihh, pixbuf, 0, 0)
            self.image2.set_from_pixbuf(pixbuf)

            # Set imagerec pixel buffer to image2
            self.pb =  self.image2.get_pixbuf()

            # Create guest surface
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.iww, self.ihh)
            #self.surface = cairo.ImageSurface.create_from_png(fname)
            #print("surface", self.surface, self.surface.get_width(), self.surface.get_height)

            self.pb2 = pixbuf2
            self.pb.copy_area(0, 0, self.iww, self.ihh, self.pb2, 0, 0)

            ctx = cairo.Context(self.surface)
            #ctx.scale(300, 300)  # Normalizing the canvas
            #pat = cairo.LinearGradient(0.0, 0.0, 1.0, 1.0)
            #pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
            #pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity
            #ctx.set_source(pat)
            #ctx.rectangle(0, 0, 300, 300)  # Rectangle(x0, y0, x1, y1)
            #ctx.fill()

            Gdk.cairo_set_source_pixbuf(ctx, self.pb2, 0, 0)
            ctx.paint()

            #arr = self.array_from_pixbuf(self.pb2)
            #print(type(arr))
            self.bpx = self.pb2.get_n_channels()
            #print("lens", self.iww, self.ihh, bpx, "mul",  self.iww*self.ihh*bpx, len(buf))
            imgrec.verbose = 1
            buf = self.surface.get_data()
            imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
            imgrec.verbose = 0

            self.stepx = float(self.iww)/self.divider;
            self.stepy = float(self.ihh)/self.divider;
        except:
            print("exc load", fname, sys.exc_info())
            print_exception("load")
            #msg("  Cannot load image:\n '%s' " % fname)
            raise

    def refresh(self):
        #pix = self.image.get_pixbuf()
        #iww = pix.get_width(); ihh = pix.get_height()
        #pixbuf = self.image2.get_pixbuf()
        #pix.copy_area(0, 0, iww, ihh, pixbuf, 0, 0)
        print("refresh")

        ctx = cairo.Context(self.surface)
        pbx = self.image.get_pixbuf()
        Gdk.cairo_set_source_pixbuf(ctx, pbx, 0, 0)
        ctx.paint()
        self.invalidate()

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

        #imgrec.verbose = 1
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        print( "Norm Image")
        imgrec.normalize()
        self.invalidate()

    def smooth_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        old = imgrec.verbose
        imgrec.verbose = 2
        imgrec.smooth(10)
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

        imgrec.verbose = 1
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.bridar(10)

        self.invalidate()

    def dar_image(self):

        imgrec.verbose = 1
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.bridar(-10)
        self.invalidate()

    def line_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.verbose = 0

        imgrec.line(10, 20, 10,  100,  0xffff0000)
        imgrec.line(10, 20, 100, 20,  0xff0000ff)
        imgrec.line(10, 20, 100, 100, 0xff00ff00)

        imgrec.line(10, 20, 0, 0, 0xff00ff00)

        imgrec.line(0, 0, self.iww, self.ihh, 0xff000000)
        imgrec.line(0, self.ihh, self.iww, 0, 0xff000000)

        arr = []
        for aa in range(30):
            arr.append(random.randint(1, 400))

        #print("arr", arr)
        imgrec.poly(0xff0000ff, tuple(arr))

        imgrec.verbose = 0
        self.invalidate()

    def frame_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.verbose = 1
        imgrec.frame(10, 10, 100, 100, 0xff0000ff)
        imgrec.verbose = 0
        self.invalidate()

    def blank_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.verbose = 1
        imgrec.blank() #color=0xffffffff)
        imgrec.verbose = 0
        #self.pb = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
        #                    True, 8, iww, ihh)
        #self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.iww, self.ihh)
        #
        self.invalidate()

    def walk_image(self, xx, yy):

        #print( "walk_image() dim =", iw, ih, "pos =", xx, yy )
        imgrec.verbose = 1
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.walk(int(xx), int(yy))
        self.invalidate()

    def edge_image(self):

        #imgrec.verbose = 1
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.edge()
        self.invalidate()

    # --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

    def anal_image(self, xxx = -1, yyy = -1):

        imgrec.verbose = 1
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        # Interpret defaults:
        #if xxx == -1: xxx = self.divider
        #if yyy == -1: yyy = self.divider

        if xxx == -1: xxx = 0
        if yyy == -1: yyy = 0

        print( "Anal image", xxx, yyy, self.stepx, self.stepy)

        imgrec.verbose = 0

        try:
            # Draw grid:
            if self.xparent.check1.get_active():
                #print("Grid")
                for xx in range(self.divider):
                    hor = int(xx * self.stepx)
                    imgrec.line(hor, 0, hor, self.ihh, 0xff888888)

                for yy in range(self.divider):
                    ver = int(yy * self.stepy)
                    imgrec.line(0, ver, self.iww-1, ver, 0xff888888)

                self.invalidate()
        except:
            print_exception("grid")
            raise

        # Get an array of median values
        try:
            xcnt = 0; ycnt = 0;
            darr = {};
            for yy in range(self.divider):
                xcnt = 0
                for xx in range(self.divider):
                    hor = int(xx * self.stepx); ver = int(yy * self.stepy)
                    med = imgrec.median(hor, ver, int(hor + self.stepx), int(ver + self.stepy))
                    #imgrec.blank(hor, ver, hor + stepx, ver + stepy, med)
                    med &= 0xffffff;  # Mask out alpha
                    #print( "hor", hor, "ver", ver, "med 0x%x" % med)

                    # Remember it in a dict
                    self.add_to_dict(darr, xcnt, ycnt, med)
                    xcnt += 1
                ycnt += 1;
        except:
            print_exception("median")

        #print("darr", darr)

        if self.xparent.radio1.get_active():
            self.xparent.clear_small_img()

            # Set up flood fill
            fparm = flood.floodParm(self.divider, darr);
            fparm.stepx = self.stepx; fparm.stepy = self.stepy
            fparm.tresh = TRESH
            fparm.inval = self.show_prog;    # Progress feedback
            fparm.colx = int(random.random() * 0xffffff)

            ret = flood.flood(xxx, yyy, fparm)
            if ret == -1:
                return

            # Only draw relative shape
            #maxx = fparm.maxx - fparm.minx; maxy = fparm.maxy - fparm.miny
            #print( "maxx maxy", maxx, maxy)
            #print( "minx miny", minx, miny)
            #img = Gtk.Image()
            #pixbuf = Gtk.gdk.Pixbuf(Gtk.gdk.COLORSPACE_RGB, True, 8,  maxx+1, maxy+1)
            #pixbuf.fill(0x000000ff)
            #arr = pixbuf.get_pixels()

            #print( "bounds",  fparm.bounds)

            self.xparent.narr = norm_array(fparm)
            #print(  "narr len ", len(self.xparent.narr))

            arr = self.surface.get_data()

            # Animate, so we see the correct winding
            #for bb in self.xparent.narr:
            #        #arr[aa[1] - miny, aa[0] - minx, 0] = 0x7f0000ff
            #        arr[bb[1], bb[0], 0] = 0xff
            #        arr[bb[1], bb[0], 1] = 0x00
            #        arr[bb[1], bb[0], 2] = 0x00
            #        arr[bb[1], bb[0], 3] = 0xff
            #        #print( bb[0], bb[1], "  ",)
            #        pixbuf2 = Gtk.gdk.pixbuf_new_from_array(arr, Gtk.gdk.COLORSPACE_RGB, 8)
            #        img.set_from_pixbuf(pixbuf2)
            #        self.xparent.fill_small_img(img)
            #        usleep(3)

            # Compare shape with saved ones
            cmp = []
            for cc in self.xparent.shapes:
                res = cmp_arrays(cc[1], self.xparent.narr)
                cmp.append((res, cc[0]))

            # Dictionary yet?
            if(len(cmp)):
                cmp.sort()
                print( "cmp", cmp)
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
        #rect = Gtk.gdk.Rectangle(int(minx * self.stepx), int(miny * self.stepy),
        #                int((maxx + 1) * self.stepx),
        #                        int((maxy + 1)  * self.stepy))

        #self.window.invalidate_rect(rect, False)
        self.invalidate()
        usleep(.005)


















