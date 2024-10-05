#!/usr/bin/env python

import os, sys, getopt, signal, array, math
import time, random

mem = memoryview(bytearray(b"1234"))

print(mem, mem[0])
mem[0] = 12
print(mem, mem[0], mem.obj)

#