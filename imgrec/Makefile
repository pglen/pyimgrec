# ------------------------------------------------------------------------
# Makefile for imgrec python module
#
# Simplified for CentOS compile. Edit path for your system.
# Fri 04.Oct.2024 ubuntu compile success
#
# Converted to automake dec/1/2015
#

#COPT = -DNDEBUG -g -O3 -Wall -Wstrict-prototypes -fPIC -DMAJOR_VERSION=1 \
#    -DMINOR_VERSION=0 -I/usr/include/pygtk-2.0 -I/usr/include/glib-2.0 \
#        -I/usr/include/python2.6 -I/usr/local/lib/glib-2.0/include \
#            -I/usr/include/libxml2 -I/usr/include/gnome-vfs-2.0 \
#             -I/usr/lib/gnome-vfs-2.0/include -I/usr/include/gconf/2 \
#              -I/usr/include/orbit-2.0 -I/usr/include/dbus-1.0 \
#                -I/usr/lib/dbus-1.0/include

# Simplified for CentOS 7 compile. Edit path for your system.

#COPT = -DNDEBUG -g -O3 -Wall -Wstrict-prototypes -fPIC -DMAJOR_VERSION=1 \
#    -DMINOR_VERSION=0 -I/usr/include/pygtk-2.0 -I/usr/include/glib-2.0 \
#        -I/usr/include/python2.7 -I/usr/local/lib/glib-2.0/include \
#            -I/usr/include/libxml2 -I/usr/include/gnome-vfs-2.0 \
#             -I/usr/lib/gnome-vfs-2.0/include -I/usr/include/gconf/2 \
#              -I/usr/include/orbit-2.0 -I/usr/include/dbus-1.0 \
#                -I/usr/lib/dbus-1.0/include


#COPT = -DNDEBUG -g -O3 -Wall -Wstrict-prototypes -fPIC \
#    -DMAJOR_VERSION=1 -DMINOR_VERSION=0 \
#        -I/usr/include/python3.10  \
#            -pthread -I/usr/include/gtk-3.0 -I/usr/include/at-spi2-atk/2.0 -I/usr/include/at-spi-2.0 -I/usr/include/dbus-1.0 -I/usr/lib/x86_64-linux-gnu/dbus-1.0/include -I/usr/include/gtk-3.0 -I/usr/include/gio-unix-2.0 -I/usr/include/cairo -I/usr/include/pango-1.0 -I/usr/include/harfbuzz -I/usr/include/pango-1.0 -I/usr/include/fribidi -I/usr/include/harfbuzz -I/usr/include/atk-1.0 -I/usr/include/cairo -I/usr/include/pixman-1 -I/usr/include/uuid -I/usr/include/freetype2 -I/usr/include/gdk-pixbuf-2.0 -I/usr/include/libpng16 -I/usr/include/x86_64-linux-gnu -I/usr/include/libmount -I/usr/include/blkid -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include

COPT = -fPIC -DNDEBUG -g -O3 -Wall -Wstrict-prototypes  \
    -DMAJOR_VERSION=1 -DMINOR_VERSION=0 \
        -I/usr/include/python3.10  \
            -pthread -I/usr/include/gtk-3.0 -I/usr/include/at-spi2-atk/2.0 -I/usr/include/at-spi-2.0 -I/usr/include/dbus-1.0 -I/usr/lib/x86_64-linux-gnu/dbus-1.0/include -I/usr/include/gtk-3.0 -I/usr/include/gio-unix-2.0 -I/usr/include/cairo -I/usr/include/pango-1.0 -I/usr/include/harfbuzz -I/usr/include/pango-1.0 -I/usr/include/fribidi -I/usr/include/harfbuzz -I/usr/include/atk-1.0 -I/usr/include/cairo -I/usr/include/pixman-1 -I/usr/include/uuid -I/usr/include/freetype2 -I/usr/include/gdk-pixbuf-2.0 -I/usr/include/libpng16 -I/usr/include/x86_64-linux-gnu -I/usr/include/libmount -I/usr/include/blkid -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include

# This way inference rules can be used.
CFLAGS=${COPT}

# Add targets here
TARGS = imgrec.o line.o square.o utils.o color.o flood.o norm.o walk.o

# ------------------------------------------------------------------------

all:  imgrec.so

imgrec.so: ${TARGS} Makefile
	./bdate.py > bdate.h
	gcc  -shared ${TARGS} -lgtk-3 -lgdk-3 -lpangocairo-1.0 -lpango-1.0 -lharfbuzz -latk-1.0 -lcairo-gobject -lcairo -lgdk_pixbuf-2.0 -lgio-2.0 -lgobject-2.0 -lglib-2.0  \
		     -o imgrec.so

utils.o:  utils.h

clean:
	@rm -f *.o

# EOF
