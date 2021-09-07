

from classes.parsers.ParamParser import ParamParser
import xml.etree.ElementTree as et


import unittest


class TestParamParserMethods(unittest.TestCase):
    
    def setUp(self):
        tree = et.ElementTree()
        self.pp = ParamParser(tree)

    def test_get_data_elem_type_1(self):
        option_list = ['genome1.fasta', 'genome2.fasta']
        ext = self.pp.get_common_extension(option_list)
        self.assertEqual(ext, 'fasta')

    def test_get_data_elem_type_2(self):
        option_list = ['genome1.fasta', 'genome2.fa']
        ext = self.pp.get_common_extension(option_list)
        self.assertEqual(ext, 'fasta')


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)