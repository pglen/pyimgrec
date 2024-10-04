# Configure paths for PyGobj

dnl PYGOBJ_3_0([MINIMUM-VERSION, [ACTION-IF-FOUND [, ACTION-IF-NOT-FOUND [, MODULES]]]])
dnl Test for PY_GOBJ, and define PYGOBJ_CFLAGS and PYGOBJ_LIBS
if gmodule, gobject,
dnl gthread, or gio is specified in MODULES, pass to pkg-config
dnl
AC_DEFUN([PYGOBJ_3_0],
[dnl 
dnl Get the cflags and libraries from pkg-config
dnl
AC_ARG_ENABLE(glibtest, [  --disable-glibtest      do not try to compile and run a test GLIB program],
		    , enable_pygobjtest=yes)

  pkg_config_args=pygobject-3.0

  PKG_PROG_PKG_CONFIG([0.16])

  no_pygobj=""

  if test "x$PKG_CONFIG" = x ; then
    no_pygobj=yes
    PKG_CONFIG=no
  fi

  min_pygobj_version=ifelse([$1], ,3.0,$1)
  AC_MSG_CHECKING(for PyGOBJ - version >= $min_pygobj_version)

  if test x$PKG_CONFIG != xno ; then
    ## don't try to run the test against uninstalled libtool libs
    if $PKG_CONFIG --uninstalled $pkg_config_args; then
	  echo "Will use uninstalled version of GLib found in PKG_CONFIG_PATH"
	  enable_pygobjtest=no
    fi

    if $PKG_CONFIG --atleast-version $min_pygobj_version $pkg_config_args; then
	  :
    else
	  no_pygobj=yes
    fi
  fi

  if test x"$no_pygobj" = x ; then

    AC_MSG_RESULT([yes])
    PYGOBJ_CFLAGS=`$PKG_CONFIG --cflags $pkg_config_args`
    PYGOBJ_LIBS=`$PKG_CONFIG --libs $pkg_config_args`
    
    AC_SUBST(PYGOBJ_CFLAGS)
    AC_SUBST(PYGOBJ_LIBS)
  else
    AC_MSG_RESULT([no])
  fi
  
])


