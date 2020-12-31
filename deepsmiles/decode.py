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

import itertools
from collections import defaultdict

from . import exceptions

bondchars = "-=#$:/\\"

def is_ring_symbol(char):
    return char.isdigit() or char=='%'

class Tree:
    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(list)
        self.rev_edges = {}
        self.rc_digit = 0

    def add_node(self, text):
        self.nodes.append(text)
        return len(self.nodes)-1

    def add_edge(self, _from, to):
        self.edges[_from].append(to)
        self.rev_edges[to] = _from

    def add_ring_closure(self, _from, rc, bondchar):
        curr = _from
        for i in range(rc-1):
            try:
                curr = self.rev_edges[curr]
            except:
                return False
        self.rc_digit += 1
        if self.rc_digit < 10:
            smi_bcsymbol = str(self.rc_digit)
        elif self.rc_digit < 100:
            smi_bcsymbol = "%" + str(self.rc_digit)
        else:
            smi_bcsymbol = "%(" + str(self.rc_digit) + ")"
        self.nodes[_from] += bondchar + smi_bcsymbol
        self.nodes[curr] += smi_bcsymbol
        return True

    def to_smiles(self):

        def visit(N):
            children = self.edges[N]
            if not children:
                return self.nodes[N]
            if len(children) == 1:
                return self.nodes[N] + visit(children[0])
            ans = []
            for child in children[:-1]:
                ans.append('(%s)' % visit(child))
            ans.append(visit(children[-1]))
            return self.nodes[N] + "".join(ans)

        return visit(0)

def decode_branches(deepsmiles, rings):
    """
    Decode DeepSMILES/Branches and DeepSMILES/Branches+Rings to SMILES
    """
    stack = []
    tree = Tree()
    i = 0
    idx = -1
    while i < len(deepsmiles):
        x = deepsmiles[i]
        if x == ')':
            if len(stack) == 0:
                raise exceptions.DecodeError(deepsmiles, i, "Too many close parentheses - there is no corresponding atom to pop off the stack")
            stack.pop()
        elif x in bondchars:
            pass
        elif x == '%':
            if i == 0:
                raise exceptions.DecodeError(deepsmiles, i, "'%' not allowed as first character")
            bondchar = deepsmiles[i-1] if i > 0 and deepsmiles[i-1] in bondchars else ""
            if deepsmiles[i+1] == '(':
                closebracket = deepsmiles.find(')', i+2)
                if closebracket == -1:
                    raise exceptions.DecodeError(deepsmiles, i, "'%(' is missing the corresponding close parenthesis")
                digit = int(deepsmiles[i+2:closebracket])
                i = closebracket
            else:
                try:
                    digit = int(deepsmiles[i+1:i+3])
                    num_digits = 2
                    try: # Check if three digits follow the %
                        digit = int(deepsmiles[i+1:i+4])
                        num_digits = 3
                    except:
                        pass
                except ValueError:
                    raise exceptions.DecodeError(deepsmiles, i, "'%' should be followed by at least two digits")
                i += num_digits
            ok = tree.add_ring_closure(idx, digit, bondchar)
            if not ok:
                raise exceptions.DecodeError(deepsmiles, i, "There is no corresponding atom on which to place the ring opening symbol for the ring sized %s" % digit)
        elif x.isdigit():
            if i == 0:
                raise exceptions.DecodeError(deepsmiles, i, "digit not allowed as first character")
            bondchar = deepsmiles[i-1] if i > 0 and deepsmiles[i-1] in bondchars else ""
            ok = tree.add_ring_closure(idx, int(x), bondchar)
            if not ok:
                raise exceptions.DecodeError(deepsmiles, i, "There is no corresponding atom on which to place the ring opening symbol for the ring sized %s" % deepsmiles[i])
        else: # add atom
            bondchar = deepsmiles[i-1] if i > 0 and deepsmiles[i-1] in bondchars else ""
            if i < len(deepsmiles) - 1 and ((x=='C' and deepsmiles[i+1]=='l') or (x=='B' and deepsmiles[i+1]=='r')):
                idx = tree.add_node(bondchar + x + deepsmiles[i+1])
                i += 1
            elif x=='[':
                closebracket = deepsmiles.find(']', i)
                if closebracket == -1:
                    raise exceptions.DecodeError(deepsmiles, i, "There is a '[' without the corresponding ']'")
                idx = tree.add_node(bondchar + deepsmiles[i:closebracket+1])
                i = closebracket
            else:
                idx = tree.add_node(bondchar + x)
            # If we are not handling ring closures specially just hoover them up and bung them
            # on the end of the atom
            if not rings:
                tmpi = i+1
                while tmpi < len(deepsmiles) and (is_ring_symbol(deepsmiles[tmpi]) or (deepsmiles[tmpi] in bondchars and is_ring_symbol(deepsmiles[tmpi+1]))):
                    tmpi += 1
                if tmpi > i+1:
                    tree.nodes[-1] += deepsmiles[i+1:tmpi]
                    i = tmpi-1
            if stack:
                tree.add_edge(stack[-1], idx)
            stack.append(idx)
        i += 1

    return tree.to_smiles()

# From the itertools docs
def nth(iterable, n):
    """Returns the nth item"""
    return next(itertools.islice(iterable, n, None))

def flatten_in_reverse(sequence):
    for item in reversed(sequence):
        if isinstance(item, list):
            for subitem in flatten_in_reverse(item):
                yield subitem
        else:
            yield item

def decode_only_rings(deepsmiles):
    """
    Decode DeepSMILES/Rings to SMILES
    """
    # smi_prev is a list, for each bracket level, of the atom lookups seen at that level
    # When we come to a close bracket, smi_prev.pop() is called.
    # This means that the length of this list, at any point, gives the distance along the
    # shortest branch from the first atom
    smi_prev = [[]]

    ans = []
    bondclosures = defaultdict(str) # ans idx -> string

    digit = 1

    i = 0
    while i < len(deepsmiles):
        x = deepsmiles[i]
        if x == ')':
            lastbranch = smi_prev.pop()
            ans.append(')')
        elif x == '(':
            smi_prev.append([])
            ans.append('(')
        elif x in bondchars:
            pass
        elif is_ring_symbol(x):
            if i == 0 or not ans:
                raise exceptions.DecodeError(deepsmiles, i, "Ring closure symbol must be preceded by an atom")
            bondchar = deepsmiles[i-1] if deepsmiles[i-1] in bondchars else ""
            depth = sum(len(z) for z in smi_prev)
            if x == "%":
                if deepsmiles[i+1] == '(':
                    closebracket = deepsmiles.find(')', i+2)
                    if closebracket == -1:
                        raise exceptions.DecodeError(deepsmiles, i, "'%(' is missing the corresponding close parenthesis")
                    ringsize = int(deepsmiles[i+2:closebracket])
                    i = closebracket
                else:
                    try:
                        ringsize = int(deepsmiles[i+1:i+3])
                    except ValueError:
                        raise exceptions.DecodeError(deepsmiles, i, "'%' should be followed by two digits")
                    i += 2
            else:
                ringsize = int(x)
            if digit < 10:
                smi_bcsymbol = str(digit)
            elif digit < 100:
                smi_bcsymbol = "%" + str(digit)
            else:
                smi_bcsymbol = "%(" + str(digit) + ")"
            ans[-1] += bondchar + smi_bcsymbol
            try:
                ring_open_atom_idx = nth(flatten_in_reverse(smi_prev), ringsize - 1)
            except StopIteration:
                raise exceptions.DecodeError(deepsmiles, i, "There is no corresponding atom on which to place the ring opening symbol for the ring sized %d" % ringsize)
            bondclosures[ring_open_atom_idx] += smi_bcsymbol
            digit += 1
        else:
            smi_prev[-1].append(len(ans))
            bondchar = deepsmiles[i-1] if i > 0 and deepsmiles[i-1] in bondchars else ""
            if x == '[':
                closebracket = deepsmiles.find(']', i)
                if closebracket == -1:
                    raise exceptions.DecodeError(deepsmiles, i, "There is a '[' without the corresponding ']'")
                ans.append(bondchar + deepsmiles[i:closebracket+1])
                i = closebracket
            elif i < len(deepsmiles) - 1 and deepsmiles[i:i+2] in ["Cl", "Br"]:
                ans.append(bondchar + deepsmiles[i:i+2])
                i += 1
            else:
                ans.append(bondchar + x)
        i += 1

    finalans = []
    for idx, x in enumerate(ans):
        finalans.append(x)
        bcsymbols = bondclosures.get(idx, None)
        if bcsymbols:
            finalans.append("".join(bcsymbols))
    return "".join(finalans)

def decode(deepsmiles, rings=False, branches=False):
    """
    Decode DeepSMILES to SMILES
    """
    if not rings and not branches:
        return deepsmiles

    if not branches:
        return decode_only_rings(deepsmiles)

    return decode_branches(deepsmiles, rings=rings)
