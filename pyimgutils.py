#!/usr/bin/env python

import os, sys, getopt, signal, array

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

#import gobject, gtk, pango, time,

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

        butts =  "OK", Gtk.ButtonsType.OK, "Cancel", Gtk.ButtonsType.CANCEL
        fc = Gtk.FileChooserDialog(msg, None, mode, butts)
        fc.set_current_folder(old_dir)

        fc.connect("key-press-event", self.area_key, fc)
        fc.connect("key-release-event", self.area_key, fc)

        fc.set_default_response(Gtk.ResponseType.ACCEPT)
        fc.connect("response", self._done_opendlg)
        fc.run()

    def _done_opendlg(self, win, resp):

        global old_dir

        os.chdir(self.old)
        if resp == Gtk.ButtonsType.OK:
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
                #print "Ret"
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
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DIALOG_DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.RESPONSE_REJECT,
                    Gtk.STOCK_OK, Gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(Gtk.RESPONSE_ACCEPT)
    dialog.set_position(Gtk.WIN_POS_CENTER)
    entry = Gtk.Entry();
    entry.set_activates_default(True)
    entry.set_width_chars(24)
    label1 = Gtk.Label("   ");   label2 = Gtk.Label("   ")
    label3 = Gtk.Label("   ");   label4 = Gtk.Label("   ")
    label1a = Gtk.Label(prompt); label1b = Gtk.Label("     ")
    hbox2 = Gtk.HBox()
    hbox2.pack_start(label1, False)
    hbox2.pack_start(label1a, False)
    hbox2.pack_start(label1b, False)
    hbox2.pack_start(entry)
    hbox2.pack_start(label2, False)


    dialog.vbox.pack_start(label3)
    dialog.vbox.pack_start(hbox2)
    dialog.vbox.pack_start(label4)


    dialog.show_all()
    response = dialog.run()
    gotxt = entry.get_text()
    dialog.destroy()
    if response == Gtk.RESPONSE_ACCEPT:
        resp = gotxt

    return resp

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep(msec):

    got_clock = time.clock() + float(msec) / 1000
    #print got_clock
    while True:
        if time.clock() > got_clock:
            break
        Gtk.main_iteration_do(False)








