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

from . import encode
from . import decode

optionnames = set(["branchlength"])

class Converter:
    def __init__(self, rings=False, branches=False, options=None):
        """Initialise a Converter object.

        By default, nothing is converted, so you probably should specify
        a keyword option:
        1. rings=True, branches=True gives DeepSMILES/RS+PN
        2. rings=True gives DeepSMILES/RS
        3. branches=True gives DeepSMILES/PN
        """
        self.rings = rings
        self.branches = branches
        options = {} if options is None else options
        self.branchlength = options.pop("branchlength", False)
        for k in options.keys():
            raise ConverterError(k, optionnames)
    def encode(self, smiles):
        """Encode a SMILES string as DeepSMILES"""
        return encode.encode(smiles, rings=self.rings, branches=self.branches)
    def decode(self, deepsmiles):
        """Decode a DeepSMILES string back to SMILES"""
        return decode.decode(deepsmiles, rings=self.rings, branches=self.branches)
    def __str__(self):
        """Return a string representation"""
        optionstring = "'branchlength': %s" % str(self.branchlength)
        return "Converter(rings=%s, branches=%s, options={%s})" % (
                str(self.rings),
                str(self.branches),
                optionstring)

