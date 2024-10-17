#!/usr/bin/env python

import os, sys, getopt, signal, array, pickle
import time, traceback, warnings

#warnings.simplefilter("ignore")

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

import cairo

from timeit import Timer
from random import *

from pyimgutils import *

import treehand, img_main

try:
    import imgrec.imgrec as imgrec
    #print("ImgRec Lib Version:", imgrec.version(), "Built:", imgrec.builddate())

except:
    print_exception("import imgrec")
    print( "Cannot import imgrec") #, using py implementation")
    raise

# ------------------------------------------------------------------------
# This is open source image recognition program. Written in python with
# plugins in 'C'

version = 0.12
verbose = False
xstr = ""

# Profile line, use it on bottlenecks
#got_clock = time.clock()
# profiled code here
#print(  "Str", time.clock() - got_clock        )


# Where things are stored (backups, orgs, macros)
config_dir = os.path.expanduser("~/.pyimgrec")

def help():

    print( )
    print( "PyImgRec version: ", version)
    print( )
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [[filename] ... [filenameN]]")
    print( )
    print( "Options:")
    print( )
    print( "            -d level  - Debug level 1-10. (Limited implementation)")
    print( "            -v        - Verbose (to stdout and log)")
    print( "            -c        - Dump Config")
    print( "            -h        - Help")
    print()

# ------------------------------------------------------------------------

class MainWin():

    def __init__(self):

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Python Image Recognition")
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.smrc = None
        self.narr = []; self.shapes = []
        ic = Gtk.Image(); ic.set_from_file("images/shapes.png")
        #stock(Gtk.DialogType.INFO, Gtk.GtkIconSize.BUTTON)
        self.window.set_icon(ic.get_pixbuf())

        #self.window.set_flags(Gtk.CAN_FOCUS | SENSITIVE)
        #self.window.set_events(  Gdk.POINTER_MOTION_MASK |
        #                    Gdk.POINTER_MOTION_HINT_MASK |
        #                    Gdk.BUTTON_PRESS_MASK |
        #                    Gdk.BUTTON_RELEASE_MASK |
        #                    Gdk.KEY_PRESS_MASK |
        #                    Gdk.KEY_RELEASE_MASK |
        #                    Gdk.FOCUS_CHANGE_MASK )

        self.window.connect("destroy", self.OnExit)
        self.window.connect("button-press-event", self.area_button)
        self.window.connect("key-press-event", self.key_press_event)
        self.window.connect("configure-event", self.config_event)

        self.pangolayout = self.window.create_pango_layout("a")
        try:
            self.window.set_icon_from_file("icon.png")
        except:
            pass

        warnings.simplefilter("ignore")

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        #print("Window size", www, hhh)
        #if www / hhh > 2:
        #    self.window.set_default_size(5*www/8, 7*hhh/8)
        #else:
        #    self.window.set_default_size(7*www/8, 7*hhh/8)

        self.window.set_default_size(6*www/8, 6*hhh/8)

        warnings.simplefilter("default")

        #print( www, hhh)
        self.wwww = 3 * www / 4;  self.hhhh = 3 * hhh / 4

        self.hbox_s = Gtk.HBox()
        self.hbox_s2 = Gtk.HBox()
        self.hbox = Gtk.HBox()
        self.mainbox = Gtk.HBox()
        self.hbox2 = Gtk.HBox()
        self.hbox2a = Gtk.HBox()
        self.hbox3 = Gtk.HBox()

        self.area = img_main.ImgMain(self)
        self.vport = Gtk.Viewport()
        self.scroller = Gtk.ScrolledWindow()
        self.vport.add(self.area)
        self.scroller.add(self.vport)
        self.mainbox.pack_start(self.scroller, 1, 1, 0)

        self.vport2 = Gtk.Viewport()
        self.scroller2 = Gtk.ScrolledWindow()

        #self.simg = Gtk.Image.new_from_file("images/star.png")
        #a2 = self.simg.get_pixbuf()
        #self.scroller2.set_size_request(a2.get_width(), a2.get_width())

        self.simg = Imagex(200, 200)

        self.win2 =  Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.win2.set_title("Image Show")
        self.win2.simg = Imagex(200, 200)
        self.win2.ww = self.win2.simg.ww;
        self.win2.hh = self.win2.simg.hh
        #self.win2.set_size_request(self.win2.ww,  self.win2.hh)
        self.win2.add(self.win2.simg)

        self.win2.move(100, 100)
        #win2.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.win2.show_all()

        try:
            # Load default image(s)
            #self.load("images/african.jpg")
            #self.load("images/IMG_0823.jpg")
            #self.load("images/shapes.png")
            self.load("images/shapex.png")
            #self.load("images/Untitled.png")
            #self.load("images/line.png")
            #self.load("images/star.png")
            #self.load("images/rect.png")
            #self.load("images/IMG_0827.jpg")
            #self.load("images/enrolled.pgm")
        except:
            print_exception("Load Image")
            #msg("Cannot load file " + self.fname)
            raise

        pix = self.area.image.get_pixbuf()
        iww = pix.get_width(); ihh = pix.get_height()

        self.vport2.add(self.simg)
        self.scroller2.add(self.vport2)
        self.mainbox.pack_start(self.scroller2, 1, 1, 0)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL, 0, 255, 1)
        self.scale.set_value(128)
        self.scale.set_inverted(True)
        self.scale.set_tooltip_text("Mark value")
        self.mainbox.pack_start(self.scale, 0, 0, 0)
        self.scale2 = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL, 0, 255, 1)
        self.mainbox.pack_start(self.scale2, 0, 0, 0)
        self.scale2.set_value(32)
        self.scale2.set_inverted(True)
        self.scale2.set_tooltip_text("Threshold diff")

        #if iww > self.wwww or ihh > self.hhhh:
        #    self.scroller.set_size_request(self.wwww, self.hhhh)
        #else:
        #    self.scroller.set_size_request(iww + 30, ihh + 30)

        vbox2 = Gtk.VBox()
        self.tree = treehand.TreeHand(self.tree_sel_row)
        vbox2.pack_start(self.tree.stree, 0, 0, 0)

        #self.area3 = DrawingArea()
        #vbox2.pack_start(self.area3)

        #lab2 = Gtk.Label("Test Image")
        #vbox2.pack_start(lab2, False, 0, 0)
        #self.img = Gtk.Image();
        #self.img.set_from_stock(Gtk.STOCK_ABOUT, Gtk.IconSize.DIALOG)

        self.buttons(self.hbox, self.window)
        self.buttons2(self.hbox2, self.window)
        self.buttons3(self.hbox2a, self.window)
        self.checks(self.hbox3, self.window)

        self.spacer(self.hbox_s, False)
        self.spacer(self.hbox_s2, False)

        self.vbox = Gtk.VBox();

        #self.vbox.pack_start(self.hbox_s, False, 0, 0)
        self.vbox.pack_start(self.mainbox, True, True, 4)
        #self.vbox.pack_start(self.hbox_s2, False, 0, 0)
        self.vbox.pack_start(vbox2, False, 0, 0)
        self.vbox.pack_start(self.hbox3, False, 0, 0)
        self.vbox.pack_start(self.hbox, False, 0, 0)
        self.vbox.pack_start(self.hbox2a, False, 0, 0)
        self.vbox.pack_start(self.hbox2, False, 0, 0)

        #frame = Gtk.Frame(); frame.add(self.img)
        #vbox2.pack_start(frame, 1, 1, 0)
        #
        #self.lab = Gtk.Label("idle")
        #self.vbox.pack_start(self.lab, False, 0, 0)

        self.window.add(self.vbox)
        GLib.timeout_add(100, self.after)

    def after(self):
        # Move to current app corner
        xxx, yyy = self.window.get_position()
        #print("curr", xxx, yyy)
        self.win2.move(xxx - 100, yyy)

    def set_small_text(self, txt):
        self.lab.set_text(txt)

    def clear_small_img(self, color = 0xffffffff):
        # Only get this once after resize
        #if not self.smrc:
        #    self.smrc = self.simg.get_allocation()
        #rc = self.simg.get_allocation()
        #pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
        #                                    rc.width, rc.height)
        #pixbuf.fill(color)
        #self.simg.set_from_pixbuf(pixbuf)
        #rc = self.mainbox.get_allocation()
        #self.mainbox.window.invalidate_rect(rc, False)
        pass

    def fill_small_img(self, img):

        pass
        # Only get this once after resize
        #if not self.smrc:
        #    self.smrc = self.img.get_allocation()
        #print( "fill small", self.smrc.width, self.smrc.height)

        #rc = self.simg.get_allocation()
        #print( "fill small", img, rc.width, rc.height)
        #nnn = img.get_pixbuf().scale_simple(rc.width, rc.height,
        #                GdkPixbuf.InterpType.NEAREST)
        #self.simg.set_from_pixbuf(nnn)
        #self.mainbox.show_now()
        #rc = self.mainbox.get_allocation()
        #self.mainbox.window.invalidate_rect(rc, False)

    # --------------------------------------------------------------------
    def checks(self, hbox, window):

        self.spacer(hbox, True )

        self.check1 = Gtk.CheckButton.new_with_mnemonic(" Draw Grid ")
        self.check1.connect("clicked", self.check_hell, window)
        hbox.pack_start(self.check1, False, 0, 0)

        self.spacer(hbox, False )

        self.check2 = Gtk.CheckButton.new_with_mnemonic(" _Prompt for save Shape ")
        self.check2.connect("clicked", self.check_hell, window)
        hbox.pack_start(self.check2, False, 0, 0)

        self.spacer(hbox, False )

        self.check3 = Gtk.CheckButton.new_with_mnemonic(" Grayscale compare ")
        self.check3.connect("clicked", self.check_hell, window)
        hbox.pack_start(self.check3, False, 0, 0)

        self.spacer(hbox, False )

        self.radio1 = Gtk.RadioButton.new_with_mnemonic_from_widget(None, " Flood ")
        self.radio1.connect("clicked", self.check_hell, window)
        hbox.pack_start(self.radio1, False, 0, 0)

        self.spacer(hbox, False )

        self.radio2 = Gtk.RadioButton.new_with_mnemonic_from_widget(self.radio1, " Rect Flood ")
        self.radio2.connect("clicked", self.check_hell, window)
        hbox.pack_start(self.radio2, False, 0, 0)

        self.spacer(hbox, False )

        self.radio3 = Gtk.RadioButton.new_with_mnemonic_from_widget(self.radio1, " Walk ")
        self.radio3.connect("clicked", self.check_hell, window)
        hbox.pack_start(self.radio3, False, 0, 0)

        self.spacer(hbox, True )

    def check_hell(self, arg, ww):
        #print( "check1", self.check1.get_active())
        #print( "check2", self.check2.get_active())
        #print( "radio1", self.radio1.get_active())
        #print( "radio2", self.radio2.get_active())
        pass

    # --------------------------------------------------------------------
    # Load image

    def load(self, fname):

        self.fname = fname
        self.area.load(fname)

        self.simg.resize(self.area.iww, self.area.ihh)
        self.simg.clear()
        self.win2.simg.resize(self.area.iww, self.area.ihh)
        self.win2.simg.clear()

        if self.area.iww < 500:
            self.scroller.set_size_request(self.area.iww, self.area.ihh)
            self.scroller2.set_size_request(self.area.iww, self.area.ihh)

    # --------------------------------------------------------------------
    def buttons3(self, hbox, window):

        self.spacer(hbox, True )

        butt6 = Gtk.Button.new_with_mnemonic(" Save Last S_hape ")
        butt6.connect("clicked", self.save_shape, window)
        hbox.pack_start(butt6, False, 0, 0)

        self.spacer(hbox)

        butt7 = Gtk.Button.new_with_mnemonic(" Show All Shapes ")
        butt7.connect("clicked", self.show_all_shapes, window)
        hbox.pack_start(butt7, False, 0, 0)

        self.spacer(hbox)

        butt8 = Gtk.Button.new_with_mnemonic(" Pickle Shapes ")
        butt8.set_tooltip_text("Will save it to disk")
        butt8.connect("clicked", self.pickle_shapes, window)
        hbox.pack_start(butt8, False, 0, 0)

        self.spacer(hbox)

        butt9 = Gtk.Button.new_with_mnemonic(" unPickle Shapes ")
        butt9.connect("clicked", self.unpickle_shapes, window)
        butt9.set_tooltip_text("Will append it from disk")
        hbox.pack_start(butt9, False, 0, 0)

        self.spacer(hbox, False )

        butt9a = Gtk.Button.new_with_mnemonic(" Clear Shapes ")
        butt9a.connect("clicked", self.clear_shapes, window)
        butt9a.set_tooltip_text("Will clear current shapes")
        hbox.pack_start(butt9a, False, 0, 0)

        self.spacer(hbox, True )

    def clear_shapes(self, win, a3):
        self.shapes = []

    # --------------------------------------------------------------------
    def buttons(self, hbox, window):

        self.spacer(hbox, True )

        butt1 = Gtk.Button.new_with_mnemonic(" _Load Image ")
        butt1.connect("clicked", self.load_image, window)
        hbox.pack_start(butt1, False, 0, 0)

        self.spacer(hbox)

        butt1 = Gtk.Button.new_with_mnemonic(" _Save Image ")
        butt1.connect("clicked", self.save_image, window)
        hbox.pack_start(butt1, False, 0, 0)

        self.spacer(hbox)

        butt1 = Gtk.Button.new_with_mnemonic(" _Analize Image ")
        butt1.connect("clicked", self.anal_image, window)
        hbox.pack_start(butt1, False, 0, 0)

        self.spacer(hbox)

        butt3 = Gtk.Button.new_with_mnemonic(" _Refresh Image ")
        butt3.connect("clicked", self.refr_image, window)
        hbox.pack_start(butt3, False, 0, 0)

        self.spacer(hbox)

        butt4 = Gtk.Button.new_with_mnemonic(" _Magnifier ")
        butt4.connect("clicked", self.mag_image, window)
        hbox.pack_start(butt4, False, 0, 0)

        self.spacer(hbox)

        butt5 = Gtk.Button.new_with_mnemonic(" _Clear Annote ")
        butt5.connect("clicked", self.clear_annote, window)
        hbox.pack_start(butt5, False, 0, 0)
        self.spacer(hbox)

        self.spacer(hbox, True )


    def buttons2(self, hbox, window):

        self.spacer(hbox, True )

        butt6 = Gtk.Button.new_with_mnemonic(" _Normalize ")
        butt6.connect("clicked", self.norm, window)
        hbox.pack_start(butt6, False, 0, 0)

        self.spacer(hbox)

        butt7 = Gtk.Button.new_with_mnemonic(" _Brighten ")
        butt7.connect("clicked", self.bri, window)
        hbox.pack_start(butt7, False,0 ,0)

        self.spacer(hbox)

        butt8 = Gtk.Button.new_with_mnemonic(" _Darken ")
        butt8.connect("clicked", self.dar, window)
        hbox.pack_start(butt8, False,0 ,0)

        self.spacer(hbox)

        butt9 = Gtk.Button.new_with_mnemonic(" _Walk ")
        butt9.connect("clicked", self.walk, window)
        hbox.pack_start(butt9, False,0 ,0)

        self.spacer(hbox)

        butt9 = Gtk.Button.new_with_mnemonic(" _Edge ")
        butt9.connect("clicked", self.edge, window)
        hbox.pack_start(butt9, False,0 ,0)

        self.spacer(hbox)

        butt91 = Gtk.Button.new_with_mnemonic(" Smooth ")
        butt91.connect("clicked", self.smooth, window)
        hbox.pack_start(butt91, False,0 ,0)

        self.spacer(hbox)

        butt92 = Gtk.Button.new_with_mnemonic(" Blan_k ")
        butt92.connect("clicked", self.blank, window)
        hbox.pack_start(butt92, False,0 ,0)

        self.spacer(hbox)

        butt92a = Gtk.Button.new_with_mnemonic(" Line ")
        butt92a.connect("clicked", self.line, window)
        hbox.pack_start(butt92a, False, 0 ,0)

        self.spacer(hbox)

        butt92b = Gtk.Button.new_with_mnemonic(" Frame ")
        butt92b.connect("clicked", self.frame, window)
        hbox.pack_start(butt92b, False, 0 ,0)

        self.spacer(hbox)

        butt99 = Gtk.Button.new_with_mnemonic(" E_xit ")
        butt99.connect("clicked", self.exit, window)
        hbox.pack_start(butt99, False,0 ,0)

        self.spacer(hbox, True )

    def exit(self, butt, window):
        self.OnExit(1)

    def blank(self, butt, window):
        self.area.blank_image()

    def line(self, butt, window):
        self.area.line_image()

    def frame(self, butt, window):
        self.area.frame_image()

    def smooth(self, butt, window):
        self.area.smooth_image()

    def dar(self, butt, window):
        self.area.dar_image()

    def bri(self, butt, window):
        self.area.bri_image()

    def norm(self, butt, window):
        #print( "Norm" #,butt, window)
        self.area.norm_image()

    def walk(self, butt, window):
        #print( "Walk" #,butt, window)
        self.area.walk_image(4, 4)

    def edge(self, butt, window):
        #print( "Walk" #,butt, window)
        self.area.edge_image()

    def spacer(self, hbox, flag = False ):
        lab14 = Gtk.Label(label=" ");
        hbox.pack_start(lab14, flag, 0, 0)

    # Refresh image from original
    def mag_image(self, area, a3):
        self.area.toggle_mag()

    # Paint the image
    def area_motion(self, area, event):
        #print(  "area_motion", event.x, event.y)
        pass
        #gc.set_line_attributes(6, Gtk.gdk.LINE_SOLID,Gtk.gdk.CAP_NOT_LAST, gdk.JOIN_MITER)
        #gc.set_foreground(colormap.alloc_color("#aaaaaa"))
        #winn.draw_line(gc, 0, 7, rc.width, rc.height+7 )
        #gc.set_foreground(colormap.alloc_color("#ffffff"))
        #winn.draw_line(gc, 0, 0, rc.width, rc.height)

    def load_image(self, arg, ww):
        self.fname = ofd("Open Image File").result
        if not self.fname:
            return
        try:
            self.load(self.fname)
        except:
            msg("Cannot load file:\n%s" % self.fname)

    def save_image(self, arg, ww):
        fname = ofd("Save Image File", Gtk.FileChooserAction.SAVE).result
        if not fname:
            return
        try:
            if fname[-4:] != ".jpg":
                fname += ".jpg"
            pix = self.area.image2.get_pixbuf()
            pix.save(fname, "jpeg", {"quality":"100"});
        except:
            print( sys.exc_info())
            msg("Cannot save file:\n%s" % fname)

    def anal_image(self, win, a3):
        self.clear_small_img()
        self.area.anal_image(0, 0)
        self.area.invalidate()

    def refr_image(self, arg, ww):
        self.area.refresh()
        self.area.invalidate()
        self.simg.clear()

    def invalidate(self):
        self.area.invalidate()

    def config_event(self, win, event):
        rc = self.window.get_allocation()
        #print( "rc", rc)
        if rc.width != event.width or rc.height != event.height:
            #print( "config_event resize", event)
            self.smrc = None

    def  area_button(self, win, event):
        #print( "main", event)
        #self.fill_small_img(self.area.image2)
        pass

    def clear_annote(self, win, a3):
        self.area.clear_annote()
        #self.set_small_text("annote cleared")

    def pickle_shapes(self, win, a3):
        try:
            fp = open("shapes.txt", "wb")
            pickle.dump(self.shapes, fp)
            fp.close()
        except:
            print(_exception("pickle"))

    def unpickle_shapes(self, win, a3):
        try:
            fp = open("shapes.txt", "rb")
            self.shapes = pickle.load( fp)
            fp.close()
        except:
            print(_exception("pickle"))

    def save_shape(self, win, a3):
        #print( "Save shape data", len(self.narr))
        if len(self.narr) == 0:
            msg("No shape yet")
            return

        sss = get_str("Enter name for (the last) shape:")
        if sss != "":
            #print( "Adding shape", sss)
            self.shapes.append((sss, self.narr[1],
                    self.narr[2], self.narr[3], self.narr[4]) )

    def show_all_shapes(self, win, a3):
        if not self.shapes:
            print("No shapes saved")
            return
        self.win2.simg.clear()
        for ss in self.shapes:
            print( ss[0:4], "len:", len(ss[4]), ss[4][:3], "...")
            ctx = cairo.Context(self.win2.simg.surface)
            for aa in ss[4]:
                #print(aa[0], aa[1])
                offs = 4 * (aa[0] + aa[1] * self.area.iww)
                try:
                    self.win2.simg.data[offs]   = 0xff
                    self.win2.simg.data[offs+1] = 0xff
                    self.win2.simg.data[offs+2] = 0xff
                    self.win2.simg.data[offs+3] = 0xff
                except:
                    print("exc nbounds", sys.exc_info())
                    pass
                self.win2.simg.invalidate()
                self.win2.queue_draw()
                usleep(5)

    # --------------------------------------------------------------------

    def exit_all(self, area):
        Gtk.main_quit()

    def OnExit(self, aa):
        Gtk.main_quit()

    def tree_sel_row(self, xtree):
        #print( "tree sel")
        global xstr
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected_rows()
        for aa in xiter:
            xstr = xmodel.get_value(xmodel.get_iter(aa), 0)
            break

    def key_press_event(self, win, event):
        #print( "main key_press_event", win, event)
        if event.state & Gdk.ModifierType.MOD1_MASK:
            if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
                sys.exit(0)

        if event.keyval == Gdk.KEY_Escape:
            self.mag = False
            self.invalidate()

# Start of program:

if __name__ == '__main__':

    global mainwin

    autohide = False
    print()
    print( "Imgrec Version", imgrec.version(), imgrec.builddate())
    #print( "Imgrec   ", imgrec.__dict__)

    try:
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
    except: pass

    # Let the user know it needs fixin'
    if not os.path.isdir(config_dir):
        print( "Cannot access config dir:", config_dir)
        sys.exit(1)

    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hva")
    except getopt.GetoptError as err:
        print( "Invalid option(s) on command line:", err)
        sys.exit(1)

    #print( "opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
            except:
                pgdebug = 0

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": verbose = True
        if aa[0] == "-a": autohide = True

    if verbose:
        print( "PyImgRec running on", "'" + os.name + "'",
            "GTK", Gtk.gtk_version, "PyGtk", pygtk_version )

    mainwin = MainWin()
    mainwin.window.show_all()

    if autohide:
        mainwin.window.iconify()
    Gtk.main()

# EOF
