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

import textwrap

class Error(Exception):
    """Base class for DeepSMILES exceptions."""
    pass

class ConverterError(Error):
    """Exception raised for errors initialising a Converter"""
    def __init__(self, expression, allowedvalues):
        self.expression = expression
        self.allowedvalues = allowedvalues

    def __str__(self):
        return """The specified option '%s' was not recognised.
Supported options are:
   %s""" % (self.expression, ", ".join(self.allowedvalues))


class DecodeError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, idx, message):
        self.expression = expression
        self.idx = idx
        self.message = message

    def __str__(self):
        return """DeepSMILES cannot be decoded to SMILES
%s:
  %s
  %s^
        """ % ("\n".join(textwrap.wrap(self.message, width=70)), self.expression, " "*self.idx)
