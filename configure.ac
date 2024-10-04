#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.


AC_PREREQ([2.69])
AC_INIT([Image Recognition], [1.0], [peterglen99@gmail.com])
AC_CONFIG_SRCDIR([pyimgrec])
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE

AC_CONFIG_MACRO_DIR([m4])

# Checks for programs.

AC_PROG_CC
AC_PROG_MAKE_SET

#AC_LANG([C])
dnl AC_LANG_CONFTEST(
dnl     [AC_LANG_PROGRAM([[const char hw[] = "Hello, World\n";]],
dnl                      [[fputs (hw, stdout);]])])


# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

AM_PATH_PYTHON([2.6])
#AC_MSG_RESULT([Python Version is $PYTHON_VERSION])
AC_CHECK_HEADERS([/usr/include/python$PYTHON_VERSION/Python.h])

AM_PATH_GTK_2_0([2.0.0])
PYGOBJ_3_0([3.0])

AC_CONFIG_FILES([Makefile pyimgrec/Makefile])

AC_OUTPUT



