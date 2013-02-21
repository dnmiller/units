# -*- coding: iso-8859-1 -*-
import unittest
import random
import operator
from itertools import permutations, product

from units import Units, UnitsError


test_type_generators = [
    # float generator
    lambda: random.uniform(-100.0, 100.0),
    # int generator
    lambda: random.randint(-100, 100)]

try:
    import numpy as np
    from numpy.random import randn, randint

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
    'abs', 'index', 'neg', 'pos'))

test_additive_ops = map(get_op, (
    'add', 'sub'))

test_multiplicitive_ops = map(get_op, (
    'div', 'floordiv', 'mod', 'mul', 'truediv'))

test_in_place_additive_ops = map(get_op, (
    'iadd', 'isub'))

test_in_place_multiplicitive_ops = map(get_op, (
    'idiv', 'ifloordiv', 'imod', 'imul', 'itruediv'))

test_scaling_operations = [
    '__div__',
    '__mul__',
    '__mod__',
    '__truediv__',
    '__floordiv__',

    '__rmod__',
    '__rmul__',
    '__rdiv__',
    '__rtruediv__',
    '__rfloordiv__']

test_non_scaling_operations = [
    # Math operators
    '__add__',
    '__radd__']

test_math_operations = (
    test_non_scaling_operations + test_scaling_operations)

test_comparison_operations = (
    # Comparison operators
    '__lt__',
    '__le__',
    '__eq__',
    '__ne__',
    '__ge__',
    '__gt__')

test_unitary_operations = (
    # Unitary operators
    '__abs__',
    '__neg__',
    '__pos__')

wut = (
    '__trunc__',
    '__float__')


class TestUnitNumber(unittest.TestCase):
    def assert_comparisons_equal(self, base_set, test_set):
        """
        Assert that comparison operations on the two sets produce the same
        results.
        """
        msg = ('Operator {0} return different results:\n'
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

    def assert_pow_equal(self, non_unit_a, non_unit_b, unit_a, unit_b):
        self.assertEqual(non_unit_a, unit_a.value)
        self.assertEqual(non_unit_b, unit_b.value)

        # Zero is handled elsewhere.
        if non_unit_a == 0.0:
            non_unit_a = non_unit_a.__class__(1)
            unit_a = unit_a.__class__(1, units=unit_a.units)

        # Cannot raise negative value to a fraction.
        abs_non_unit_a = abs(non_unit_a)
        abs_unit_a = Units(value=abs_non_unit_a, units=unit_a.units)
        expected = pow(abs_non_unit_a, non_unit_b)
        actual = pow(abs_unit_a, unit_b)
        self.assertEqual(expected, actual.value)

        expected = non_unit_b.__rpow__(abs_non_unit_a)
        actual = unit_b.__rpow__(abs_unit_a)
        self.assertEqual(expected, actual.value)

        # Can raise negative value to rounded number.
        if non_unit_b == 0.0:
            non_unit_b = non_unit_b.__class__(1)

        rnd_non_unit_b = round(non_unit_b)
        rnd_unit_b = Units(value=rnd_non_unit_b, units=unit_b.units)
        expected = pow(non_unit_a, rnd_non_unit_b)
        actual = pow(unit_a, rnd_unit_b)

        self.assertEqual(expected, actual.value)

    def assert_pow_raises(self, non_unit_a, non_unit_b, unit_a, unit_b):
        non_unit_a = non_unit_a.__class__(0)
        unit_a = unit_a.__class__(0, units=unit_a.units)

        if non_unit_b < 0:
            self.assertRaises(ZeroDivisionError, pow, non_unit_a, non_unit_b)
            self.assertRaises(ZeroDivisionError, pow, unit_a, unit_b)
        else:
            expected = pow(non_unit_a, non_unit_b)
            actual = pow(unit_a, unit_b)
            self.assertEqual(expected, actual.value)

    def assert_math_equal(self, non_unit_a, non_unit_b, unit_a, unit_b):
        msg = ('Invalid result for {0}:\n'
               'Units:            {1}\n'
               'Base type result: {2}\n'
               'Base type:        {3}')
        for op_name in test_math_operations:
            try:
                expected = getattr(non_unit_a, op_name)(non_unit_b)
            except ZeroDivisionError:
                self.assertRaises(
                    ZeroDivisionError, getattr(unit_a, op_name), unit_b)
                return

            units = getattr(unit_a, op_name)(unit_b).value
            self.assertEqual(units, expected, msg.format(
                             op_name, units, expected, type(non_unit_a)))

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
        for i in xrange(50):
            type_gens = (
                test_type_generators +
                np_float_generators +
                np_int_generators +
                np_uint_generators)
            for gen in type_gens:
                base_set = (gen(), gen())
                test_set = map(Units, base_set)
                self.assert_comparisons_equal(test_set, base_set)
                for a, b in product(base_set, test_set):
                    self.assert_comparisons_raise(a, b)

        # We also want the expected ordering errors for complex numbers.
        for gen in np_complex_generators:
            for op in test_comparison_ops:
                base_set = (gen(), gen())
                test_set = map(Units, base_set)
                self.assertRaises(TypeError, 'ordering', op, *base_set)
                self.assertRaises(TypeError, 'ordering', op, *test_set)

    def _test_math_ops_with_no_units(self):
        """
        Math operations on Units with both units None.
        """
        for i in xrange(100):
            for gen in test_type_generators:
                a, b = gen(), gen()
                a_unit = Units(a, units=None)
                b_unit = Units(b, units=None)

                self.assert_pow_equal(a, b, a_unit, b_unit)
                self.assert_math_equal(a, b, a_unit, b_unit)
                self.assert_pow_raises(a, b, a_unit, b_unit)

        for a, b in permutations((0.0, -0.0, 1.0, -1.0), 2):
            a_unit = Units(a, units=None)
            b_unit = Units(b, units=None)

            self.assert_pow_equal(a, b, a_unit, b_unit)
            self.assert_math_equal(a, b, a_unit, b_unit)
            self.assert_pow_raises(a, b, a_unit, b_unit)

    def _test_math_ops_with_single_units(self):
        """
        Math operations on Units and other types.
        """
        for i in xrange(100):
            for gen in test_type_generators:
                num = gen()
                num_unit = Units(gen(), units=None)

                for op_name in test_comparison_operations:
                    # Getting the operator from the number's attribute
                    # results in NotImplemented.
                    op = getattr(operator, op_name)
                    self.assertRaisesRegexp(
                        UnitsError, 'cannot compare', op, num, num_unit)
                for op_name in test_non_scaling_operations:
                    if hasattr(operator, op_name):
                        op = getattr(operator, op_name)
                        self.assertRaisesRegexp(
                            UnitsError, 'cannot add/subtract', op, num,
                            num_unit)
                    if hasattr(num, op_name):
                        op = getattr(num, op_name)
                        try:
                            result = op(num_unit)
                            self.assertEqual(result, NotImplemented)
                        except UnitsError:
                            self.assertRaisesRegexp(
                                UnitsError, 'cannot add/subtract', op,
                                num_unit)
