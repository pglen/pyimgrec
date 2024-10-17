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
import  treehand

try:
    import imgrec.imgrec as imgrec
except:
    pass

import  algorithm.flood  as flood
import  algorithm.norm_outline as norm

MAG_FACT    = 2
MAG_SIZE    = 300
DIVIDER     = 64                 # How many divisions, testing
THRESH      = 20                 # Color diff for boundary
MARKCOL     = 180                # Color counts as mark

class ImgMain(Gtk.DrawingArea):

    def __init__(self, xparent, wwww = 100, hhhh = 100):

        self.xparent = xparent
        Gtk.DrawingArea.__init__(self);

        self.pb = GdkPixbuf.Pixbuf.new \
                   (GdkPixbuf.Colorspace.RGB, True, 8,
                         MAG_SIZE / MAG_FACT , MAG_SIZE / MAG_FACT)
        self.pb.fill(0x888888ff)

        self.divider = DIVIDER;
        self.wwww = wwww; self.hhhh = hhhh
        #self.set_size_request(wwww, hhhh)

        self.annote = []; self.aframe = []; self.bframe = []
        self.atext = []

        self.mag = False
        self.event_x = self.event_y = 0
        self.image  = None
        #self.colormap = Gtk.get_default_colormap()
        #self.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

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

    def add_to_dict(self, xdic, xxx, yyy, val):
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

        rc = self.get_allocation()
        #print( "img button", event.x, event.y, rc.width, rc.height)

        curs = Gdk.Cursor.new_from_name(Gdk.Display.get_default(), "wait")
        self.get_window().set_cursor(curs)

        self.anal_image(int(event.x), int(event.y), True)
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
            #print("loaded:", self.iww, self.ihh, self.bpx)

            # "mul",  self.iww*self.ihh*bpx, len(buf))
            imgrec.verbose = 0
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

        #imgrec.verbose = 0
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        print( "Norm Image")
        imgrec.normalize()
        self.invalidate()

    def smooth_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        old = imgrec.verbose
        imgrec.verbose = 0
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

        imgrec.verbose = 0
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.bridar(10)

        self.invalidate()

    def dar_image(self):

        imgrec.verbose = 0
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
            arr.append(random.randint(1, self.iww))
            arr.append(random.randint(1, self.ihh))
        randcol = (0xff000000, 0xffff0000, 0xff00ff00, 0xff0000ff, 0xffffffff)
        idx = random.randint(0, len(randcol)-1)
        imgrec.poly(randcol[idx], tuple(arr))

        imgrec.verbose = 0
        self.invalidate()

    def frame_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
        imgrec.verbose = 0
        imgrec.frame(10, 10, 100, 100, 0xff0000ff)
        imgrec.verbose = 0
        self.invalidate()

    def blank_image(self):

        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

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
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))
        ret2 = imgrec.walk(int(xx), int(yy))
        print("ret2", ret2)
        self.invalidate()

    def edge_image(self):

        #imgrec.verbose = 0
        buf = self.surface.get_data()
        ret = imgrec.anchor(buf, shape=(self.iww, self.ihh, self.bpx))

        imgrec.edge()
        self.invalidate()

    def callb(self, xxx, yyy, kind, fparam):
        #print( "callb", xxx, yyy, fparam)
        #return
        try:
            if kind == 2:
                self.xparent.win2.simg.buf[4*xxx + 4*yyy * self.iww]   = 0x00
            elif kind == 1:
                self.xparent.win2.simg.buf[4*xxx + 4*yyy * self.iww]    = 0x00
                self.xparent.win2.simg.buf[4*xxx + 4*yyy * self.iww +1] = 0x00

                self.xparent.simg.buf[4*xxx + 4*yyy * self.iww]    = 0x00
                self.xparent.simg.buf[4*xxx + 4*yyy * self.iww +1] = 0x00
                self.xparent.simg.buf[4*xxx + 4*yyy * self.iww +2] = 0x00
            elif kind == 0:
                pass
                self.xparent.win2.simg.buf[4*xxx + 4*yyy * self.iww]    = 0x00
                self.xparent.win2.simg.buf[4*xxx + 4*yyy * self.iww +1] = 0x00
                self.xparent.win2.simg.buf[4*xxx + 4*yyy * self.iww +2] = 0x00

                self.xparent.simg.buf[4*xxx + 4*yyy * self.iww]    = 0x00
                self.xparent.simg.buf[4*xxx + 4*yyy * self.iww +1] = 0x00
                self.xparent.simg.buf[4*xxx + 4*yyy * self.iww +2] = 0x00

                #if fparam.cnt % fparam.breath == 0:
                #    #self.xparent.win2.simg.invalidate()
                #    self.xparent.simg.invalidate()
                #    usleep(5)
            else:
                print("unkown kind in callb")

            if fparam.cnt % fparam.breath == 0:
                self.xparent.win2.simg.invalidate()
                self.xparent.simg.invalidate()

        except:
            print("callb", xxx, yyy, kind, sys.exc_info())
            pass


    # --------------------------------------------------------------------
    # Using an arrray to manipulate the underlying buffer

    def anal_image(self, xxx, yyy, single = False):

        imgrec.verbose = 0
        self.buf = self.surface.get_data()
        ret = imgrec.anchor(self.buf, shape=(self.iww, self.ihh, self.bpx))

        MARKCOL = int(self.xparent.scale.get_value())
        THRESH  = int(self.xparent.scale2.get_value())

        #imgrec.verbose = 1
        #avg = imgrec.average()
        #print( "Anal image", xxx, yyy, "ww", self.iww, "hh", self.ihh,
        #                "thresh", THRESH, "markcol", MARKCOL, "avg", avg)
        #imgrec.verbose = 0

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
            except:
                print_exception("grid")

        darr = {};

        # Fill in 2D array
        for yy in range(self.ihh):
            offs = yy * self.iww * 4
            for xx in range(self.iww):
                val = []
                for cc in range(4):
                    val.append(self.buf[offs + xx * 4 + cc])
                self.add_to_dict(darr, xx, yy, val)

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

        #imgrec.blank()  #self.invalidate()   #usleep(1)

        self.xparent.simg.clear()
        self.xparent.win2.simg.clear()

        dones = {}
        nbounds = []
        found = 0
        # Iterate all shapes
        while True:
            # Set up flood fill parameters
            fparam = flood.floodParm(darr, self.callb);
            fparam.iww = self.iww;  fparam.ihh = self.ihh
            fparam.stepx = self.stepx; fparam.stepy = self.stepy
            fparam.thresh = THRESH
            fparam.markcol = MARKCOL
            #fparam.colx = int(random.random() * 0xffffff)
            #fparam.verbose = 1
            if self.xparent.check3.get_active():
                #print("Grey compare")
                fparam.grey = True

            if not single:
                ret, xxx, yyy = flood.seek(xxx, yyy, fparam, dones)
                #print("seek:", ret, xxx, yyy)
                if not ret:
                    if xxx > 0:
                        xxx = 0; yyy += 1
                        continue
                    else:
                        break
            ttt = time.time()
            ret = flood.flood_one(xxx, yyy, fparam, dones)
            if ret == -1:
                break

            if len(fparam.bounds) < 32:
                print("Short buffer", xxx, yyy, "len",
                            len(fparam.bounds), fparam.bounds[:4])
                xxx+= 1
                yyy+= 1
                continue

            print("flood_one: %.2f ms" % (1000 * (time.time() - ttt)))
            found += 1

            #self.xparent.simg.clear()

            # Process data from flood
            #nbounds = norm.norm_array(fparam)
            uls = norm.flush_upleft(fparam)
            nbs = norm.scale_vectors(uls, norm.ARRLEN)
            nbounds = norm.scale_magnitude(nbs, norm.ARRLEN)
            nbounds.sort()
            print("nbounds len", len(nbounds))
            # Save last
            if nbounds:
                self.xparent.narr = ("", fparam.minx, fparam.miny, fparam.mark, nbounds)

            # Compare with stock
            self.compare(nbounds)

            # Display results
            self.xparent.simg2.clear()
            for aa in nbounds:
                #print(aa[0], aa[1])
                offs = 4 * (aa[0] + aa[1] * self.xparent.simg2.ww)
                #offs += 4 * fparam.minx
                #offs += 4 * self.xparent.simg2.ww * fparam.miny
                try:
                    self.xparent.simg2.buf[offs]   = 0x00
                    self.xparent.simg2.buf[offs+1] = 0x00
                    self.xparent.simg2.buf[offs+2] = 0x00
                    self.xparent.simg2.buf[offs+3] = 0xff
                except:
                    #print("disp nbounds", offs, sys.exc_info())
                    pass
                self.xparent.simg2.invalidate()
                #usleep(15)

            if self.xparent.check2.get_active():
                if len(nbounds) == 0:
                    msg("No shape yet")

                sss = get_str("Enter name for shape:")
                if sss != "":
                    #print( "Adding shape", sss)
                    self.xparent.shapes.append(
                            (sss, fparam.minx, fparam.miny, fparam.mark, nbounds))

            #for aa in fparam.body:
            #    #print(aa[0], aa[1])
            #    offs = 4 * (aa[0] + aa[1] * self.xparent.area.iww)
            #    try:
            #        self.xparent.simg.data[offs]   = 0xff
            #        self.xparent.simg.data[offs+1] = 0x00
            #        self.xparent.simg.data[offs+2] = 0x00
            #        self.xparent.simg.data[offs+3] = 0xff
            #    except:
            #        pass
            #self.xparent.simg.invalidate()

            if single:
                break

        print("%d segments found." % found)

    def compare(self, xarr):

        # Compare shape with saved ones
        cmp = []
        for cc in self.xparent.shapes:
            res = norm.cmp_arrays(cc[4], xarr)
            #print("comp", res, cc[0])
            cmp.append((res, cc[0]))

        if(len(cmp)):
            cmp.sort()
            for aa in cmp:
                print( "cmp %.2f %s" % (aa[0], aa[1]) )
            #self.xparent.set_small_text("Recognized shape: %s" % cmp[0][1])
            self.xparent.tree.append_treestore(cmp[0][1])

        #self.aframe += self.bframe
        ## Reference position
        #self.aframe.append((xxx, yyy, 0xff8888ff))

        # Display final image
        #self.invalidate()

# EOF
