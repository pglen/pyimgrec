#!/usr/bin/env python

import math
import pyimgutils

#import outline

class IsLand():
    def __init__(self, data):
        self.data = data
        self.bounds = None
        self.center = None
        self.lenorg = 0
        self.data = data

    def __str__(self):
        return((self.center))

    def dump(self):
        strx =  "cnt: %s " % str(self.center)
        strx += "bnd: %s " % str(self.bounds)
        strx += "dat: %s " % str(self.data[:4])
        return strx

    def __repr__(self):
        return(str(self.center))

    def _cmp_one(self, item1, item2):
        tmp   = item1[0] - item2[0]
        tmp2  = item1[1] - item2[1]
        return (tmp, tmp2)

    def cmp(self, isl1, isl2):
        res = [0, 0]
        for aa in range(len(self.data)):
            tmp, tmp2  = self._cmp_one(isl1.data[aa], isl2.data[aa])
            #print(self.data[aa], "->", isl2.data[aa], (tmp, tmp2), end = "   ")
            res[0] += abs(tmp); res[1] += abs(tmp2)
        return res

    def find_similar(self, isl1, isl2, diff = 1):

        matches = []
        for aa in range(len(isl1.data)):
            for bb in range(len(isl2.data)):
                #tmp, tmp2  = self._cmp_one(self.data[aa], isl2.data[bb])
                tmp, tmp2  = self._cmp_one(isl1.data[aa], isl2.data[bb])
                #print(tmp, tmp2, end = " " )
                if abs(tmp) < diff and abs(tmp2) < diff:
                    #print(aa, bb, "->", tmp, tmp2, end = " ; ")
                    matches.append((aa, bb))
            #print("end")
        return matches

# EOF
