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

import unittest
import deepsmiles as ds

class ConverterTest(unittest.TestCase):
    def testStringRep(self):
        self.assertEqual(str(ds.Converter()),
                "Converter(rings=False, branches=False)")
        self.assertEqual(str(ds.Converter(rings=True)),
                "Converter(rings=True, branches=False)")
        self.assertEqual(str(ds.Converter(branches=True)),
                "Converter(rings=False, branches=True)")
        self.assertEqual(str(ds.Converter(rings=True, branches=True)),
                "Converter(rings=True, branches=True)")

class Encoding(unittest.TestCase):
    def testRingEncoding(self):
        ringconverter = ds.Converter(rings=True)
        allconverter = ds.Converter(rings=True, branches=True)
        data = [ # smi, DeepSmiles/RC, DeepSMILES/RC+PN (if different)
                ("C1CCCC1", "CCCCC5"),
                ("C%10CCC%10", "CCCC4"),
                ("C1CCCCCCCCC1", "CCCCCCCCCC%10"),
                ("C1CC(OC)CC1", "CCC(OC)CC5", "CCCOC))CC5"),
                (r"N1CC=C/1\Br", r"NCC=C/4\Br"),
                (r"N\1CC=C1\Br", r"NCC=C/4\Br"),
                (r"C1=C/CCCCCC/1", "C=C/CCCCCC/8"),
                (r"C\1=C/CCCCCC1", "C=C/CCCCCC/8"),
                (r"C\1=C/CCCCCC/1", "C=C/CCCCCC/8"),
                ("C1N[C@@]12CO2", "CN[C@@]3CO3"),
                ("[C@@]12(NC1)CO2", "[C@@](NC3)CO3", "[C@@]NC3))CO3"),
                ("CC1CCCO[C@]21CCCCO2", "CCCCCO[C@@]6CCCCO6"),
                ("CC1CCCO[C@@]12CCCCO2", "CCCCCO[C@@]6CCCCO6"),
                ("NC[C@]12CCCC1C3CC2CC3", "NC[C@]CCCC5CCC8CC5"),
                ("NC[C@]12CCCC2C3CC1CC3", "NC[C@@]CCCC5CCC8CC5"),
                ("C2C1=C/CCCCCC/12", "CC=C/CCCCCC/89"),
                ("C1C2=C/CCCCCC1/2", "CC=C/CCCCCC9/8"),
                ]
        for d in data:
            encoded = ringconverter.encode(d[0])
            self.assertEqual(d[1], encoded)
            encodedB = allconverter.encode(d[0])
            if len(d) == 2:
                self.assertEqual(d[1], encodedB)
            else:
                self.assertEqual(d[2], encodedB)

    def testBranchEncoding(self):
        branchconverter = ds.Converter(branches=True)
        allconverter = ds.Converter(rings=True, branches=True)
        data = [ # smi, DeepSmiles/PN, DeepSMILES/RC+PN (if different)
                ("C(O)C", "CO)C"),
                ("C([O])C", "C[O])C"),
                ("C(OF)C", "COF))C"),
                ("C(F)(F)C", "CF)F)C"),
                ("C(Cl)(Cl)C", "CCl)Cl)C"),
                ("C(=O)Cl", "C=O)Cl"),
                ("C(OC(=O)Cl)I", "COC=O)Cl)))I"),
                ("[C@@H](Br)(Cl)I", "[C@@H]Br)Cl)I"),
                ("B(c1ccccc1)(O)O", "Bc1ccccc1))))))O)O", "Bcccccc6))))))O)O"),
                ("Cn1cccc-2nccc12", "Cn1cccc-2nccc12", "Cnccccnccc9-5")
                ]
        for d in data:
            encoded = branchconverter.encode(d[0])
            self.assertEqual(d[1], encoded)
            encodedB = allconverter.encode(d[0])
            if len(d) == 2:
                self.assertEqual(d[1], encodedB)
            else:
                self.assertEqual(d[2], encodedB)

class Decoding(unittest.TestCase):

    def testBranchDecoding(self):
        branchconverter = ds.Converter(branches=True)
        data = [ # smi, DeepSmiles/PN
                ("COC", "COC"),
                ("C(O)C", "CO)C"),
                ("C(=O)C", "C=O)C"),
                ("C[O]C", "C[O]C"),
                ("C(OC(=O)Cl)I", "COC=O)Cl)))I"),
                ("C(F)(F)C", "CF)F)C"),
                ("Cn1ccnc1", "Cn1ccnc1"),
                ("c1ccn(cc1)O", "c1ccncc1))O"),
                ("Cn1cccc-2nccc12", "Cn1cccc-2nccc12"),
                ]
        for d in data:
            decoded = branchconverter.decode(d[1])
            self.assertEqual(d[0], decoded)

    def testRingDecoding(self):
        ringconverter = ds.Converter(rings=True)
        allconverter = ds.Converter(rings=True, branches=True)
        data = [ # smi, DeepSmiles/RC
                ("C1CCC1", "CCCC4"),
                ("C2CC1CCC1C2", "CCCCCC4C7"),
                ("c1c[nH]cc1", "cc[nH]cc5"),
                ("C1CCCCCCCCC1", "CCCCCCCCCC%10"),
                ("C1CCCCCCCCC1", "CCCCCCCCCC%(10)"),
                ("CCCCCCC1CCC1", "CCCCCCCCCC%(4)"),
                ("C1=C/CCCCCC/1", "C=C/CCCCCC/8"),
                ("C1C1C2C2C3C3C4C4C5C5C6C6C7C7C8C8C9C9C%10C%10", "CC2CC2CC2CC2CC2CC2CC2CC2CC2CC2"),
                ("C(CS)N", "C(CS)N", ""),
                ("C[C@@H]1CCCO[C@]12CCCCO2", "C[C@@H]CCCO[C@]6CCCCO6"),
                ("C2C1=C/CCCCCC/12", "CC=C/CCCCCC/89"),
                ("C1C2=C/CCCCCC1/2", "CC=C/CCCCCC9/8"),
                ]
        for d in data:
            decoded = ringconverter.decode(d[1])
            self.assertEqual(d[0], decoded)
            minput = d[2] if len(d)==3 else d[1]
            if minput:
                decodedB = allconverter.decode(minput)
                self.assertEqual(d[0], decodedB)

    def testDecodingExceptions(self):
        converter = ds.Converter(rings=True, branches=True)
        data = ["C8", "C))I", "%10C", "9C", "CCCCCC%(3CC", "C%(100)",
                "C[C@@CCl", "C%CC", "-5cc[nH]9"]
        for dsmi in data:
            self.assertRaises(ds.DecodeError, converter.decode, dsmi)
        # Test just the ring decoder
        converter = ds.Converter(rings=True)
        data = ["C8", "%10C", "9C", "C%(100)",
                "C[C@@CCl", "C%CC", "-5cc[nH]9"]
        for dsmi in data:
            self.assertRaises(ds.DecodeError, converter.decode, dsmi)

    def testDecodingBasic(self):
        converter = ds.Converter()
        dsmi = converter.decode("C")
        self.assertEqual("C", dsmi)

    def testRoundTripRingClosures(self):
        smi = "C%(1)C%(2)C%(3)C%(4)C%(5)C%(6)C%(7)C%(8)C%(9)C%(10)C%(11)C%(12)C%(13)C%(14)C%(15)C%(16)C%(17)C%(18)C%(19)C%(20)C%(21)C%(22)C%(23)C%(24)C%(25)C%(26)C%(27)C%(28)C%(29)C%(30)C%(31)C%(32)C%(33)C%(34)C%(35)C%(36)C%(37)C%(38)C%(39)C%(40)C%(41)C%(42)C%(43)C%(44)C%(45)C%(46)C%(47)C%(48)C%(49)C%(50)C%(51)C%(52)C%(53)C%(54)C%(55)C%(56)C%(57)C%(58)C%(59)C%(60)C%(61)C%(62)C%(63)C%(64)C%(65)C%(66)C%(67)C%(68)C%(69)C%(70)C%(71)C%(72)C%(73)C%(74)C%(75)C%(76)C%(77)C%(78)C%(79)C%(80)C%(81)C%(82)C%(83)C%(84)C%(85)C%(86)C%(87)C%(88)C%(89)C%(90)C%(91)C%(92)C%(93)C%(94)C%(95)C%(96)C%(97)C%(98)C%(99)C%(100)C%(100)C%(99)C%(98)C%(97)C%(96)C%(95)C%(94)C%(93)C%(92)C%(91)C%(90)C%(89)C%(88)C%(87)C%(86)C%(85)C%(84)C%(83)C%(82)C%(81)C%(80)C%(79)C%(78)C%(77)C%(76)C%(75)C%(74)C%(73)C%(72)C%(71)C%(70)C%(69)C%(68)C%(67)C%(66)C%(65)C%(64)C%(63)C%(62)C%(61)C%(60)C%(59)C%(58)C%(57)C%(56)C%(55)C%(54)C%(53)C%(52)C%(51)C%(50)C%(49)C%(48)C%(47)C%(46)C%(45)C%(44)C%(43)C%(42)C%(41)C%(40)C%(39)C%(38)C%(37)C%(36)C%(35)C%(34)C%(33)C%(32)C%(31)C%(30)C%(29)C%(28)C%(27)C%(26)C%(25)C%(24)C%(23)C%(22)C%(21)C%(20)C%(19)C%(18)C%(17)C%(16)C%(15)C%(14)C%(13)C%(12)C%(11)C%(10)C%(9)C%(8)C%(7)C%(6)C%(5)C%(4)C%(3)C%(2)C%(1)"
        for branches in [True, False]:
            converter = ds.Converter(rings=True, branches=branches)
            encoded = converter.encode(smi)
            decoded = converter.decode(encoded)
            self.assertTrue("%(100)" in decoded)

if __name__ == "__main__":
    unittest.main()
