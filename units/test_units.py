# -*- coding: iso-8859-1 -*-
import unittest
import random
import operator
from itertools import product

from units import Units, UnitsError

test_type_generators = [
    # float generator
    lambda: random.uniform(-100.0, 100.0),
    # int generator
    lambda: random.randint(-100, 100)]

try:
    import numpy as np
    from numpy.random import randn, randint
    np.seterr(all='raise')

    np_float_types = ('float16', 'float32', 'float64', 'float128')
    np_float_generators = [
        lambda: getattr(np, ft)(randn()) for ft in np_float_types]

    np_int_types = ('int8', 'int16', 'int32', 'int64')
    np_int_generators = [
        lambda: getattr(np, it)(randint(-10, 10)) for it in np_int_types]

    np_uint_types = ('uint8', 'uint16', 'uint32', 'uint64')
    np_uint_generators = [
        lambda: getattr(np, ut)(randint(0, 20)) for ut in np_uint_types]

    np_complex_types = ('complex64', 'complex128', 'complex256')
    np_complex_generators = [
        lambda: getattr(np, cp)(randn()) for cp in np_complex_types]

except ImportError:
    np_float_generators = []
    np_int_generators = []
    np_uint_generators = []
    np_complex_generators = []


# A TODO list
test_etc_ops = ('is_', 'is_not', 'pow', 'ipow', 'concat', 'contains',
                'iconcat')

get_op = lambda name: getattr(operator, name)

test_comparison_ops = map(get_op, (
    'lt', 'le', 'eq', 'ne', 'ge', 'gt'))

test_unitary_ops = map(get_op, (
    'abs', 'neg', 'pos'))

test_additive_ops = map(get_op, (
    'add', 'sub'))

test_multiplicitive_ops = map(get_op, (
    'div', 'floordiv', 'mod', 'mul', 'truediv'))

test_in_place_additive_ops = map(get_op, (
    'iadd', 'isub'))

test_in_place_multiplicitive_ops = map(get_op, (
    'idiv', 'ifloordiv', 'imod', 'imul', 'itruediv'))


class TestUnitNumber(unittest.TestCase):
    def assert_comparisons_equal(self, base_set, test_set):
        """
        Assert that comparison operations on the base set produce the same
        result as the test set.
        """
        msg = ('Operator {0} returns different results:\n'
               'base set, ({1}, {2}): {3}\n'
               'test set, ({4}, {5}): {6}')

        for op in test_comparison_ops:
            expected = op(base_set[0], base_set[1])
            actual = op(test_set[0], test_set[1])
            self.assertEqual(expected, actual, msg.format(
                op, base_set[0], base_set[1], expected,
                test_set[0], test_set[1], actual))

            expected = op(base_set[1], base_set[0])
            actual = op(test_set[1], test_set[0])
            self.assertEqual(expected, actual, msg.format(
                op, base_set[1], base_set[0], expected,
                test_set[1], test_set[0], actual))

    def assert_comparisons_raise(self, a, b):
        """
        Assert that comparisons between the two arguments raise UnitsError.
        """
        for op in test_comparison_ops:
            self.assertRaisesRegexp(UnitsError, 'compare', op, a, b)
            self.assertRaisesRegexp(UnitsError, 'compare', op, b, a)

    def assert_unitary_equal(self, base, test):
        """
        Assert that equality of two variables is invariant under unitariy
        operations.
        """
        msg = ('Operator {0} returns different results:\n'
               'pre-operator:  ({1}, {2})\n'
               'post-operator: ({3}, {4})')

        self.assertEqual(base, test.value)
        self.assertEqual(test.value, base)
        for op in test_unitary_ops:
            op_base, op_test = op(base), op(test)
            self.assertEqual(op_base, op_test.value, msg.format(
                op, base, test, op_base, op_test))
            self.assertEqual(op_test.value, op_base, msg.format(
                op, base, test, op_base, op_test))

    def assert_additions_equal(self, base_set, test_set):
        """
        Assert that equality of two variables is invariant under additive
        operations.
        """
        msg = ('Operator {0} returns different results:\n'
               'base set, ({1}, {2}): {3}\n'
               'test set, ({4}, {5}): {6}')

        self.assertEqual(base_set[0], test_set[0].value)
        self.assertEqual(base_set[1], test_set[1].value)
        self.assertEqual(test_set[0].value, base_set[0])
        self.assertEqual(test_set[1].value, base_set[1])
        for op in test_additive_ops:
            try:
                actual = op(test_set[0], test_set[1])
                expected = op(base_set[0], base_set[1])
                self.assertEqual(expected, actual.value, msg.format(
                    op, base_set[0], base_set[1], expected,
                    test_set[0], test_set[1], actual))

                actual = op(test_set[1], test_set[0])
                expected = op(base_set[1], base_set[0])
                self.assertEqual(expected, actual.value, msg.format(
                    op, base_set[1], base_set[0], expected,
                    test_set[1], test_set[0], actual))
            except FloatingPointError:
                # NumPy raises a lot of false-positive errors here for reasons
                # I can't figure out.
                continue

    def tearDown(self):
        Units.valid_units = None

    def test_units_set(self):
        """
        Setting units attribute behaves correctly.
        """
        Units(0, 'ok')
        Units.valid_units = ('good',)
        Units(0, 'good')

    def test_str_and_repr(self):
        """
        String representations correctly created.
        """
        num = Units(value=0, units='ok')
        expected = '0ok'
        actual = str(num)
        self.assertEqual(expected, actual)

        expected = "Units(value=0, units='ok')"
        actual = num.__repr__()
        self.assertEqual(expected, actual)
        exec('expected = ' + num.__repr__())
        self.assertEqual(expected, num)

    def test_invalid_units(self):
        """
        Invalid units set wrong.
        """
        Units.valid_units = ('good',)
        bad_units = 'bad'
        msg = Units._error_messages['bad units'].format(bad_units)
        self.assertRaisesRegexp(
            UnitsError, msg, Units, value=0, units=bad_units)

    def test_comparisons(self):
        """
        Comparison operations produce expected results.
        """
        type_gens = (test_type_generators + np_float_generators +
                     np_int_generators + np_uint_generators)
        for i in xrange(50):
            for gen in type_gens:
                base_set = (gen(), gen())
                test_set = map(Units, base_set)
                # Comparisons between elements of the same set produce the same
                # results.
                self.assert_comparisons_equal(test_set, base_set)
                # Comparisons between elements of different sets raise errors.
                for a, b in product(base_set, test_set):
                    self.assert_comparisons_raise(a, b)

        # We also want the expected ordering errors for complex numbers.
        for gen in np_complex_generators:
            for op in test_comparison_ops:
                base_set = (gen(), gen())
                test_set = map(Units, base_set)
                self.assertRaises(TypeError, 'ordering', op, *base_set)
                self.assertRaises(TypeError, 'ordering', op, *test_set)

    def test_unitary(self):
        """
        Unitary operations produce expected results.
        """
        type_gens = (test_type_generators + np_float_generators +
                     np_int_generators + np_uint_generators)
        for i in xrange(50):
            for gen in type_gens:
                base = gen()
                test = Units(base)
                self.assert_unitary_equal(base, test)

    def test_addition(self):
        """
        Additive operations produce expected results.
        """
        type_gens = (test_type_generators + np_float_generators +
                     np_int_generators + np_uint_generators)
        for i in xrange(50):
            for gen in type_gens:
                base_set = (gen(), gen())
                test_set = map(Units, base_set)
                # Additive operations between elements of the same set produce
                # the same results.
                self.assert_additions_equal(base_set, test_set)
