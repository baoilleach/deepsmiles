# Copyright 2018 NextMove Software
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from collections import defaultdict

bondchars = "-=#$:\\/"
CLOSE, OPEN = range(2)

def invertStereo(smifragment):
    """
    >>> invertStereo("C")
    'C'
    >>> invertStereo("[C@@]")
    '[C@]'
    >>> invertStereo("[C@]")
    '[C@@]'
    >>> invertStereo("[C@H]")
    '[C@@H]'
    >>> invertStereo("[C@@H]")
    '[C@H]'
    """
    ans = []
    i = 0
    while i < len(smifragment):
        x = smifragment[i]
        ans.append(x)
        if x == '@':
            if smifragment[i+1] == '@':
                i += 1
            else:
                ans.append('@')
        i += 1
    return "".join(ans)

def shouldInvertStereo(bcinfo):
    """
    Opens should be in idx order by their closing index
    (OPEN, idx of opening symbol, idx of corresponding closing symbol)
    Closes should be in idx order
    (CLOSE, idx of closing symbol, ring size)
    Closes should come before opens
    >>> shouldInvertStereo([(OPEN, 7, 12), (OPEN, 6, 17)])
    True
    >>> shouldInvertStereo([(OPEN, 7, 17), (OPEN, 6, 12)])
    False
    >>> shouldInvertStereo([(CLOSE, 7, '6'), (CLOSE, 6, '6')])
    False
    >>> shouldInvertStereo([(CLOSE, 6, '6'), (CLOSE, 7, '6')])
    False
    >>> shouldInvertStereo([(OPEN, 5, 12), (CLOSE, 6, '6')])
    True
    >>> shouldInvertStereo([(OPEN, 5, 12), (CLOSE, 6, '6'), (CLOSE, 7, '6')])
    False
    """
    if len(bcinfo) <= 1:
        return False

    data = []
    for bc in bcinfo:
        if bc[0]==OPEN:
            data.append( (bc[1], (1, bc[2])) ) # the sort order is based on the closing index
        else:
            data.append( (bc[1], (0, bc[1])) ) # the sort order should be the symbol index

    data.sort(key=lambda x:x[1])

    # Check the permutation parity (even/odd) after sorting
    outOfOrder = 0
    for i in range(len(data)-1):
        for j in range(i+1, len(data)):
            if data[i][0] > data[j][0]:
                outOfOrder += 1
    return outOfOrder % 2 == 1

class BondClosureInfo:
    def __init__(self):
        self.ringopenings = {} # rc_symbol -> (depth, bondchar)

        # Where a bond opening is on a stereoatom, we need to record the 'ans' index associated
        # with that symbol so that when we come to the closing we can match it up
        self.roindex = {} # ring_opening_symbol -> ans_idx (where the symbol is on a stereoatom)

        # This is a map from 'ans' idx to bond closure information
        # This information will be used to generate the final string
        self.symbolinfo = defaultdict(list)

def encode(smi, rings=False, branches=False):
    """Encode SMILES as DeepSMILES"""

    if not rings and not branches:
        return smi

    i = 0 # the index in the smiles string
    ans = []
    idx = -1 # the atom index, the first atom having idx 0
    # smi_prev is a list, for each bracket level, of the atom indices seen at that level
    # When we come to a close bracket, smi_prev.pop() is called.
    # This means that the length of this list, at any point, gives the distance along the
    # shortest branch from the first atom
    smi_prev = [[]]
    bci = BondClosureInfo()

    while i < len(smi):
        x = smi[i]
        if x == ')':
            lastbranch = smi_prev.pop()
            if branches:
                ans.append(')'*len(lastbranch))
            else:
                ans.append(')')
        elif x == '(':
            smi_prev.append([])
            if not branches:
                ans.append('(')
        elif x in bondchars:
            pass
        elif x.isdigit() or x=='%':
            if not rings:
                bondchar = smi[i-1] if i > 0 and smi[i-1] in bondchars else ""
                ans.append(bondchar + x)
            else:
                depth = sum(len(z) for z in smi_prev)
                bondchar = smi[i-1] if i > 0 and smi[i-1] in bondchars else ""
                if x == "%":
                    bcsymbol = smi[i:i+3]
                    i += 2
                else:
                    bcsymbol = x
                if bcsymbol in bci.ringopenings:
                    open_depth, open_bondchar, open_ans, open_i = bci.ringopenings.pop(bcsymbol)
                    digit = depth - open_depth + 1
                    outbondchar = bondchar
                    if not outbondchar:
                        outbondchar = open_bondchar
                        if outbondchar == "\\": # invert the sense
                            outbondchar = "/"
                        elif outbondchar == "/":
                            outbondchar = "\\"
                    if "@" in ans[open_ans]:
                        bci.symbolinfo[open_ans].append( (OPEN, open_i, i) )
                    formatstr = "%s%d" if digit < 10 else "%s%%%d" if digit < 100 else "%s%%(%d)"
                    bci.symbolinfo[len(ans)-1].append( (CLOSE, i, formatstr % (outbondchar, digit)) )
                else:
                    bci.ringopenings[bcsymbol] = (depth, bondchar, len(ans)-1, i)
        else:
            bondchar = smi[i-1] if i > 0 and smi[i-1] in bondchars else ""
            idx += 1
            smi_prev[-1].append(idx)
            if x == '[':
                closeparens = smi.find(']', i)
                ans.append(bondchar + smi[i:closeparens+1])
                i = closeparens
            elif i < len(smi) - 1 and smi[i:i+2] in ["Cl", "Br"]:
                ans.append(bondchar + smi[i:i+2])
                i += 1
            else:
                ans.append(bondchar + x)
        i += 1

    # Stitch together the answer from the 'ans' string, plus ring sizes.
    # While doing this, if necessary, invert the stereo of tet centers
    # based on ring info.
    finalans = []
    for i, x in enumerate(ans):
        bcinfo = bci.symbolinfo.get(i, [])
        if bcinfo:
            if shouldInvertStereo(bcinfo):
                finalans.append(invertStereo(x))
            else:
                finalans.append(x)
            for y in bcinfo:
                if y[0] == CLOSE:
                    finalans.append(y[2])
        else:
            finalans.append(x)
    return "".join(finalans)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
