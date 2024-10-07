from distutils.core import setup, Extension

module1 = Extension('imgrec',
                    sources = ['imgrec.c', 'line.c', 'norm.c', 'square.c', 'utils.c', 'walk.c', 'color.c', 'flood.c'])

setup (name = 'imgrec',
       version = '1.0',
       description = 'Image recognition for python',
       ext_modules = [module1])

