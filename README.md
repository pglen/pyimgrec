                        README
                        
  Python image recognition. Drives the 'C' imgrec python extension.

GNU / Linux:

 Usual (autoconf) ./configure and make cycle works


How to compile / use on Windows. 

  1.) Install python 2.7
  
  2.) Update pip

python -m pip install --upgrade pip

  3.) Install numpy, scipy and family

python -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose

  4.) Download / install python tools for Visual C
  
Start VC command line for python, set environment  (see env.txt for different versions of VC)

SET VS90COMNTOOLS=%VS140COMNTOOLS%

Then:	
	
python setup.py build

