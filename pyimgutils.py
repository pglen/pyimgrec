#!/usr/bin/env python

import os, sys, getopt, signal, array, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

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

old_dir = ""

class ofd():

    def __init__(self, msg = "Open File", mode=Gtk.FileChooserAction.OPEN):

        self.result = None
        self.old    = os.getcwd()

        global old_dir
        if not old_dir:
            old_dir = self.old
        print("old_dir:", old_dir)

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

        print("Done", resp)

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

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                print("Ret", win)
                win.response(Gtk.ResponseType.ACCEPT)
                #area.destroy()
                return

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_BackSpace:
                os.chdir("..")
                populate(self)
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


# --------------------------------------------------------------------

def msg(xstr, xtype = Gtk.MessageType.INFO):
    md = Gtk.MessageDialog( flags=Gtk.DialogFlags.MODAL,
                type=xtype, buttons=Gtk.ButtonsType.OK)
    md.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    md.set_markup(xstr);
    md.run();
    md.destroy()

def  get_str(prompt):

    resp = ""
    dialog = Gtk.Dialog("Enter string",
                   None,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   ("OK", Gtk.ResponseType.REJECT,
                    "Cancel", Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    #dialog.set_position(Gtk.WIN_POS_CENTER)
    entry = Gtk.Entry();
    entry.set_activates_default(True)
    entry.set_width_chars(24)
    label1 = Gtk.Label("   ");   label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");   label4 = Gtk.Label("   ")
    label1a = Gtk.Label(prompt); label1b = Gtk.Label("     ")
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
    if response == Gtk.ResponseType.ACCEPT:
        resp = gotxt

    return resp

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

if sys.version_info[0] < 3 or \
    (sys.version_info[0] == 3 and sys.version_info[1] < 3):
    timefunc = time.clock
else:
    timefunc = time.process_time

def  usleep(msec):

    got_clock = timefunc() + float(msec) / 1000
    #print( got_clock)
    while True:
        if timefunc() > got_clock:
            break
        #print ("Sleeping")
        Gtk.main_iteration_do(False)

# EOF
