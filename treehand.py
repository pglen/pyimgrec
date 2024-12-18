#!/usr/bin/env python

import os, sys, getopt, signal, gtk

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

class   TreeHand():

    def __init__(self, tree_sel_row):
        self.treestore = None
        self.tree = self.create_tree(self)
        self.tree.set_headers_visible(False)
        #self.tree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.tree.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

        self.tree.set_size_request(200, 200)

        self.stree =  Gtk.ScrolledWindow()
        self.stree.add(self.tree)
        self.tree.connect("cursor-changed",  tree_sel_row)

    # Tree handlers
    def start_tree(self):

        if not self.treestore:
            self.treestore = Gtk.TreeStore(str)

        # Delete previous contents
        try:
            while True:
                root = self.treestore.get_iter_first()
                self.treestore.remove(root)
        except:
            #print  sys.exc_info()
            pass

        #piter = self.treestore.append(None, ["Ready."])
        #self.treestore.append(piter, ["None .."])

    # -------------------------------------------------------------------------
    def create_tree(self,  match, text = None):

        self.start_tree()
        tv = Gtk.TreeView(model=self.treestore)
        tv.set_enable_search(True)
        cell = Gtk.CellRendererText()
        tvcolumn = Gtk.TreeViewColumn()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tv.append_column(tvcolumn)
        return tv

    def update_treestore(self, text):

        #print "was", was

        # Delete previous contents
        try:
            while True:
                root = self.treestore.get_iter_first()
                self.treestore.remove(root)
        except:
            pass
            #print  sys.exc_info()
        if not text:
            self.treestore.append(None, ["Matches",])
            return

        cnt = 0; piter2 = None; next = False
        try:
            for line in text:
                piter = self.treestore.append(None, [line])
                if next:
                    next = False; piter2 = piter
                #if cnt == was:
                #    next = True
                cnt += 1
        except:
            pass
            #print  sys.exc_info()

        if piter2:
            self.tree.set_cursor(self.treestore.get_path(piter2))
        else:
            root = self.treestore.get_iter_first()
            self.tree.set_cursor(self.treestore.get_path(root))

    def append_treestore(self, text):
        piter = self.treestore.append(None, [text])
        self.sel_last()

    def sel_last(self):
        #print("sel last ...")
        sel = self.tree.get_selection()
        if not sel:
            return
        xmodel, xiter = sel.get_selected()
        iterx = self.treestore.get_iter_first()
        if not iterx:
            return
        while True:
            iter2 = self.treestore.iter_next(iterx)
            if not iter2:
                break
            iterx = iter2.copy()
        sel.select_iter(iterx)
        ppp = self.treestore.get_path(iterx)
        self.tree.set_cursor(ppp, self.tree.get_column(0), False)
        #pgutils.usleep(1)
        self.tree.scroll_to_cell(ppp, None, True, 0., 0. )


# EOF
