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

from    pyimgutils import *
import  treehand

try:
    import imgrec.imgrec as imgrec
except:
    pass

import  algorithm.flood  as flood
import  algorithm.outline as outline
import  algorithm.island as island

import imgproc, imgflood

DIVIDER     = 32                 # How many divisions, mostly for testing
MAG_FACT    = 2
MAG_SIZE    = 300


class ImgMain(Gtk.DrawingArea, imgproc.ImgProc, imgflood.Flood):

    def __init__(self, xparent, wwww = 100, hhhh = 100):

        Gtk.DrawingArea.__init__(self);

        self.bpx = imgflood.BPX
        self.fname = ""
        self.gl_dones = {};
        self.reanal = 0
        self.xparent = xparent
        #self.wwww = wwww; self.hhhh = hhhh
        self.iww = wwww
        self.ihh = hhhh
        self.divider = DIVIDER

        self.stepx = float(self.iww)/self.divider;
        self.stepy = float(self.ihh)/self.divider;
        self.pb = GdkPixbuf.Pixbuf.new \
                   (GdkPixbuf.Colorspace.RGB, True, 8,
                         MAG_SIZE / MAG_FACT , MAG_SIZE / MAG_FACT)
        self.pb.fill(0x888888ff)
        self.image = Gtk.Image()
        self.image.set_from_pixbuf(self.pb)
        self.image2 = Gtk.Image()

        # Create default surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, wwww, hhhh)
        self.buf = self.surface.get_data()
        self.set_size_request(wwww, hhhh)

        self.annote = []; self.aframe = []; self.bframe = []
        self.atext = []
        self.islands = []
        self.mag = False
        self.event_x = self.event_y = 0
        self.sumxx = []
        self.sumf = []

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.laststate = 0

        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.area_button)
        self.connect("draw", self.draw)
        self.connect("motion-notify-event", self.area_motion)
        self.connect("leave_notify_event", self.area_leave)

    def area_leave(self, win, area):
        self.xparent.labx.set_text("")
        self.xparent.laby.set_text("")
        self.xparent.labz.set_text("")

    def _add_to_dict(self, xdic, xxx, yyy, val):
        try:
            xdic[yyy][xxx] = val
        except KeyError:
            xdic[yyy] = {}
            xdic[yyy][xxx] = val
        except:
            print( "add to dict", sys.exc_info())

    def area_motion(self, area, event):
        #print(  event.x, event.y)
        self.event_x = event.x
        self.event_y = event.y

        self.xparent.labx.set_text("x = %.2f" % (event.x))
        self.xparent.laby.set_text("y = %.2f" % (event.y))

        xxx = int(event.x); yyy = int(event.y)

        try:
            col  =  self.buf[BPX * (xxx + yyy * self.iww)   ]
            col2 =  self.buf[BPX * (xxx + yyy * self.iww)+1 ]
            col3 =  self.buf[BPX * (xxx + yyy * self.iww)+2 ]
            self.xparent.labz.set_text("%x%x%x" % (col, col2, col3))
        except:
            pass
            #print(sys.exc_info())

        #if self.mag:
        #    self.invalidate()

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

        #gc.set_source_rgba(111, 0, 0 )
        #gc.rectangle(0, 0, 100, 100)
        #gc.fill()
        #gc.move_to(100, 100)
        #gc.line_to(200, 200)
        #gc.stroke()

        gc.set_source_surface(self.surface)
        gc.paint()

    # --------------------------------------------------------------------
    def key_press_event(self, win, event):

        self.laststate = event.state

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

        self.laststate = event.state

        rc = self.get_allocation()
        #print( "img button", event.x, event.y, rc.width, rc.height)

        curs = Gdk.Cursor.new_from_name(Gdk.Display.get_default(), "wait")
        self.get_window().set_cursor(curs)

        addx = event.state & Gdk.ModifierType.SHIFT_MASK
        #print("mou", event.state)

        self.anal_image(int(event.x), int(event.y), True, addx)

        self.get_window().set_cursor(None)

    def toggle_mag(self):
        self.mag = not self.mag
        if self.mag and self.event_x == 0:
            rc = self.get_allocation()
            self.event_x = rc.width/2; self.event_y = rc.height/2
        self.invalidate()

    def invalidate(self):
        #rect = self.get_allocation()
        #rect = Gdk.Rectangle(rect)
        #winn.invalidate_rect(rect, False)
        #self.queue_draw_area(rect)
        self.queue_draw()

    def from_pixbuf(self, pixbuf):
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        pix = image.get_pixbuf()
        self._create(pix)

    def from_image(self, image):
        self.image = image
        pix = self.image.get_pixbuf()
        self._create(pix)

    # --------------------------------------------------------------------

    def load(self, fname):

        ''' Load image file '''
        try:
            self.image.set_from_file(fname)
            pix = self.image.get_pixbuf()
            self._create(pix)
        except:
            print("exc load", fname, sys.exc_info())

    def _create(self, pix):

        self.iww = pix.get_width();
        self.ihh = pix.get_height()
        self.set_size_request(self.iww, self.ihh)

        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                        True, 8, self.iww, self.ihh)

        pix.copy_area(0, 0, self.iww, self.ihh, pixbuf, 0, 0)
        #return

        pixbuf2 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                        True, 8, self.iww, self.ihh)

        self.image2.set_from_pixbuf(pixbuf)

        # Set imagerec pixel buffer to image2
        self.pb =  self.image2.get_pixbuf()

        # Create guest surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.iww, self.ihh)
        self.buf = self.surface.get_data()
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
        #print("loaded:", self.iww, self.ihh, self.bpx)

        # "mul",  self.iww*self.ihh*bpx, len(buf))
        imgrec.verbose = 0
        imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))
        #imgrec.verbose = 0

        self.stepx = float(self.iww)/self.divider;
        self.stepy = float(self.ihh)/self.divider;

        self.xparent.tree.append_treestore("Loaded: '%s'" % self.fname)
        self.invalidate()

    def refresh(self):
        #pix = self.image.get_pixbuf()
        #iww = pix.get_width(); ihh = pix.get_height()
        #pixbuf = self.image2.get_pixbuf()
        #pix.copy_area(0, 0, iww, ihh, pixbuf, 0, 0)
        #print("refresh")

        ctx = cairo.Context(self.surface)
        pbx = self.image.get_pixbuf()
        Gdk.cairo_set_source_pixbuf(ctx, pbx, 0, 0)
        ctx.paint()
        self.invalidate()

# EOF
