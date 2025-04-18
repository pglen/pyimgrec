#!/usr/bin/env python

import os, sys, getopt, signal, array, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import cairo

import traceback

# ------------------------------------------------------------------------
# Print an exception as the system would print it

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                        "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())
    print( cumm)

# pyimgutils
# --------------------------------------------------------------------

def timeit(fn):
    def wrapped(*args, **keyw):
        ttt = time.time()
        ret = fn(*args, **keyw)
        print("func: '%s' %.3f ms" % (fn.__name__, (time.time() - ttt)*1000))
        return ret
    return wrapped

# Configure app here for sharing on submodules

class Config():
    verbose = 0
    pgdebug = 0
    pass

# ONE instance
xconfig = Config()

class Imagex(Gtk.DrawingArea):

    ''' Utility class to operate on images'''

    def __init__(self, xparent, ww = 20, hh = 20):
        super().__init__()
        self.ww = ww; self.hh = hh
        self.xparent = xparent
        self.set_size_request(ww, hh)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ww, hh)
        self.bpx = 4    # From FORMAT specifier - ARGB32
        self.buf = self.surface.get_data()
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect("draw", self._draw)
        self.connect("motion-notify-event", self.area_motion)
        self.clear()
        #print("Imagex create", self.ww, self.hh)

    def resize(self, ww, hh):

        ''' drop old, alloc new '''

        self.ww = ww; self.hh = hh
        #print("Imagex resize", self.ww, self.hh)
        self.set_size_request(ww, hh)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ww, hh)
        self.buf = self.surface.get_data()

    def clear(self, rr=0.5, gg=0.5, bb=0.4):

        ''' Fill in color. We default to a tainted shade of grey for
        recognizing content better  '''

        ctx = cairo.Context(self.surface)
        ctx.set_source_rgba(rr, gg, bb)
        ctx.rectangle(0, 0, self.ww, self.hh)
        ctx.fill()
        self.invalidate()
        #print("Imagex clear", self.ww, self.hh)

    #@timeit
    def copyfrom(self, ww, hh, xbuf):

        ''' Duplicate image from buffer'''

        #self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ww, hh)
        self.ww = ww
        self.hh = hh
        self.resize(self.ww, self.hh)
        #for aa in range(len(xbuf)):
        #    self.buf[aa] = xbuf[aa]
        self.buf[:] = xbuf[:]

    #@timeit
    def copyto(self, target):

        ''' Display Image on target '''

        target.resize(self.ww, self.hh)
        #for aa in range(len(self.buf)):
        #    target.buf[aa] = self.buf[aa]
        target.buf[:] = self.buf[:]

    def getcol(self, xx, yy):

        ''' Return color tuple from coordinate.
            Tuple is RGBA in machine byte order '''

        val = 0
        offs = self.bpx * yy * self.ww + self.bpx * xx
        for aa in range(self.bpx-1):
            val += self.buf[aa + offs]
        val //=  self.bpx - 1
        return val

    def setcol(self, xx, yy, colorx):

        ''' Set color tuple at coordinate.
            Color is RGBA in machine byte order '''

        offs = self.bpx * yy * self.ww + self.bpx * xx
        for aa in range(self.bpx):
            self.buf[aa + offs] = colorx[aa]

    def drawline(self, xxx, yyy, xxx2, yyy2, newcol = (0xff, 0xff, 0xff, 0xff)):

        # No zero len line
        if xxx2 - xxx == 0:
            return
        if yyy2 - yyy == 0:
            return

        # Swap (obsolete)
        #if xxx > xxx2:
        #    xxx3 = xxx2 ;xxx2 = xxx; xxx = xxx3
        #    yyy3 = yyy2 ; yyy2 = yyy ; yyy = yyy3

        if (xxx2 - xxx) > (yyy2 - yyy):
            slope = (yyy2 - yyy) / (xxx2 - xxx)
            #print("slope", slope)
            cnt = 0;
            for xx in range(xxx, xxx2):
                yy = int(yyy + slope * cnt)
                self.setcol(xx, yy, newcol)
                cnt += 1
        else:
            slope = (xxx2 - xxx) / (yyy2 - yyy)
            #print("slope", slope)
            cnt = 0;
            for yy in range(yyy, yyy2):
                xx = int(xxx + slope * cnt)
                self.setcol(xx, yy, newcol)
                cnt += 1

    def drawcross(self, xxx, yyy, newcol = (0xff, 0xff, 0xff, 0xff), size = 4):

        ''' Just a cross on screen '''

        row =  self.bpx * yyy * self.ww
        try:
            for line in range(-size, +size):
                for cnt, aa in enumerate(newcol):
                    offs = self.bpx * line + cnt + self.bpx * xxx + row
                    self.buf[offs] = newcol[cnt]
            for vline in range(-size, +size):
                for cnt, aa in enumerate(newcol):
                    offs = cnt + self.bpx * xxx + row + self.bpx * vline * self.ww
                    self.buf[offs] = newcol[cnt]
        except:
            pass

    def _draw(self, me, gc):
        #print("Imagex draw")
        gc.set_source_surface(self.surface)
        gc.paint()
        #return True

    def invalidate(self):

        ''' Output changed to actual screen '''

        ctx = cairo.Context(self.surface)
        # Needs some op to actually draw. We fake a pixel into 0, 0
        ctx.set_source_rgba(0, 0, 0, .1 )
        ctx.move_to(0, 0)
        ctx.line_to(1, 0)
        ctx.stroke()
        self.queue_draw()

    def area_motion(self, area, event):
        #print("motion", event.x, event.y)

        ''' Dynamic display of current point '''

        self.event_x = event.x
        self.event_y = event.y

        self.xparent.labx.set_text("x = %.2f" % (event.x))
        self.xparent.laby.set_text("y = %.2f" % (event.y))

        buf = self.surface.get_data()
        xxx = int(event.x); yyy = int(event.y)

        try:
            col  =  buf[4 * (xxx + yyy * self.iww)   ]
            col2 =  buf[4 * (xxx + yyy * self.iww)+1 ]
            col3 =  buf[4 * (xxx + yyy * self.iww)+2 ]
            self.xparent.labz.set_text("%x%x%x" % (col, col2, col3))
        except:
            pass
            #print(sys.exc_info())


old_dir = ""
''' Remember previous directory here '''

class ofd():

    def __init__(self, msg = "Open File", startdir = "images",
                                        mode=Gtk.FileChooserAction.OPEN):
        self.result = None

        global old_dir
        if not old_dir:
            os.chdir(startdir)

        self.old = os.getcwd()
        old_dir = self.old

        #print("old_dir:", old_dir)

        fc = Gtk.FileChooserDialog( title = msg, transient_for = None,
                                        action = mode)
        butts =  ("OK", Gtk.ButtonsType.OK, "Cancel", Gtk.ButtonsType.CANCEL,)
        fc.add_buttons(*butts)
        fc.set_current_folder(old_dir)

        fc.connect("key-press-event", self.area_key, fc)
        fc.connect("key-release-event", self.area_key, fc)
        fc.connect("key-release-event", self.area_key, fc)

        fc.set_default_response(Gtk.ButtonsType.OK)
        fc.connect("response", self._done_opendlg)
        fc.run()

    def _done_opendlg(self, win, resp):

        global old_dir

        #print("Done", resp)
        os.chdir(self.old)
        if resp == Gtk.ButtonsType.OK or resp == Gtk.ResponseType.ACCEPT:
            try:
                fname = win.get_filename()
                if not fname:
                    msg("Must have filename")
                else:
                    self.result = fname
                old_dir = os.path.dirname(fname)
            except:
                msg("Cannot open file", fname)
        win.destroy()

    # Call key handler
    def area_key(self, area, event, win):

        #print ("area_key", event)
        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                return
                #area.destroy()

            if event.keyval == Gdk.KEY_Return:
                #print("Ret", win)
                fname = win.get_filename()
                if os.path.isfile(fname):
                    win.response(Gtk.ResponseType.ACCEPT)
                    #area.destroy()
                else:
                    #print("Dir", fname)
                    win.set_current_folder(fname)
                return True

            if event.keyval == Gdk.KEY_BackSpace:
                os.chdir("..")
                #populate(self)
                #print "BS"

            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                self.alt = True;

            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if self.alt:
                    area.destroy()

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;

        return None

def msg(*xstr, xtype = Gtk.MessageType.INFO):

    ''' Message Dialog '''

    xstr2 = ""
    if type(xstr) == type(()):
        for aa in xstr:
            xstr2 += aa + " "
    else:
        xstr2 = xstr

    md = Gtk.MessageDialog( modal=1, #flags=Gtk.DialogFlags.MODAL,
                message_type=xtype, buttons=Gtk.ButtonsType.OK)
    md.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    md.set_markup(xstr2);
    md.run();
    md.destroy()

def  get_str(prompt):

    ''' Get string Dialog '''

    resp = ""
    dialog = Gtk.Dialog(title="Enter string", modal = True, destroy_with_parent = True)
    dialog.add_buttons("OK", Gtk.ResponseType.REJECT, "Cancel", Gtk.ResponseType.ACCEPT,)
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    entry = Gtk.Entry();
    entry.set_activates_default(True)
    entry.set_width_chars(24)
    label1 = Gtk.Label(label="   ");   label2 = Gtk.Label(label="   ")
    label3 = Gtk.Label(label="   ");   label4 = Gtk.Label(label="   ")
    label1a = Gtk.Label(label=prompt); label1b = Gtk.Label(label="     ")
    hbox2 = Gtk.HBox()
    hbox2.pack_start(label1, False, 0, 0)
    hbox2.pack_start(label1a, False, 0, 0)
    hbox2.pack_start(label1b, False, 0, 0)
    hbox2.pack_start(entry, False, 0, 0)
    hbox2.pack_start(label2, False, 0, 0)

    dialog.vbox.pack_start(label3, False, 0, 0)
    dialog.vbox.pack_start(hbox2, False, 0, 0)
    dialog.vbox.pack_start(label4, False, 0, 0)

    dialog.show_all()
    response = dialog.run()
    gotxt = entry.get_text()
    dialog.destroy()
    if response != Gtk.ResponseType.CANCEL:
        resp = gotxt

    #print("resp", resp)
    return resp

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

if sys.version_info[0] < 3 or \
    (sys.version_info[0] == 3 and sys.version_info[1] < 3):
    timefunc = time.clock
else:
    timefunc = time.process_time

def  usleep(msec):

    ''' sleep msec milliseconds ...
         ...  timefunc workaround to allow PY Ver < 3.3
    '''

    got_clock = timefunc() + float(msec) / 1000
    #print( got_clock)
    while True:
        if timefunc() > got_clock:
            break
        #print ("Sleeping")
        Gtk.main_iteration_do(False)

def printarr(arr):
    for aa in arr:
        print( "%.2d %d  " % (aa[0], aa[1]),)
    print()

def create_enums(dot_strs, localx):

    ''' Create enum variables from string array, place it in local scope.
        Arguments: <br>

            dot_strs    tuple / list of strings
            localx      scope to create it in
    '''

    for cnt, aa in enumerate(dot_strs):
        localx.setdefault(aa, cnt)
        #print("%s = %d" % (aa, localx.get(aa)))

# EOF
