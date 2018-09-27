from setuptools import setup

PKG_NAME = 'deepsmiles'
AUTHOR = "Noel M O'Boyle"
AUTHOR_EMAIL = "noel@nextmovesoftware.com"
DOCSTRING = "DeepSMILES, a SMILES-like syntax suited to machine learning"
VERSION = "1.0.1"

long_description = """DeepSMILES
==========

This Python module can convert well-formed SMILES (that is, as writen by a cheminformatics toolkit) to DeepSMILES. It also does the reverse conversion.

Install the latest version with::

  pip install --upgrade deepsmiles

DeepSMILES is a SMILES-like syntax suited to machine learning. Rings are indicated using a single symbol instead of two, while branches do not use matching parentheses but rather use a right parenthesis as a 'pop' operator.

For example, benzene is `c1ccccc1` in SMILES but `cccccc6` in DeepSMILES (where the `6` indicates the ring size). As a branch example, the SMILES `C(Br)(OC)I` can be converted to the DeepSMILES `CBr)OC))I`. For more information, please see the corresponding preprint.

The library is used as follows:

.. code-block:: python

        import deepsmiles
        print("DeepSMILES version: %s" % deepsmiles.__version__)
        converter = deepsmiles.Converter(rings=True, branches=True)
        print(converter) # record the options used

        encoded = converter.encode("c1cccc(C(=O)Cl)c1")
        print("Encoded: %s" % encoded)

        try:
            decoded = converter.decode(encoded)
        except deepsmiles.DecodeError as e:
            decoded = None
            print("DecodeError! Error message was '%s'" % e.message)

        if decoded:
            print("Decoded: %s" % decoded)
"""

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    description=DOCSTRING,
    license='License :: OSI Approved :: MIT License',
    long_description=long_description,
    name=PKG_NAME,
    packages=[PKG_NAME],
    platforms='any',
    test_suite = "deepsmiles.testsuite",
    url='http://github.com/nextmovesoftware/deepsmiles',
    version=VERSION,
)
