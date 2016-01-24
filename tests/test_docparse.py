import unittest

from begin import docparse


class TestDocparse(unittest.TestCase):
    def _func(self):
        """Some help text

        Some more informative help text

        :param x: some parameter
                    that `spans` two lines
        :type x: int

        :type long_name: not an `int`, a ``foobar``
        :return: Not relevant to us
        :rtype: We don't use this

        Some trailing text.
        """

    def test_parse_doc(self):
        doc = docparse.parse_doc(self._func)

        self.assertEqual(doc.text, 'Some help text\n\nSome more informative '
                                   'help text\n\nSome trailing text.')
        self.assertEqual(doc.params['x'].text, 'some parameter\n'
                                               'that spans two lines')
        self.assertEqual(doc.params['x'].type, 'int')
        self.assertEqual(doc.params['long_name'].type, 'not an int, a foobar')

    def test_evaluate(self):
        x = 'myvar'
        self.assertEqual(docparse.evaluate('x', 0), 'myvar')
        self.assertEqual(self._evaluate(), 'myvar')
        self.assertEqual(docparse.evaluate('str'), str)
        self.assertEqual(docparse.evaluate('DummyClass.dummy_attr', 0), int)

    def _evaluate(self):
        """Helper to test evaluating in caller's frame."""
        return docparse.evaluate('x', stack_depth=1)


class DummyClass(object):
    dummy_attr = int
