# -*- coding: iso-8859-1 -*-
import unittest
import random
from itertools import permutations

from units import UnitsNumber, UnitsError


test_type_generators = (
    # float generator
    lambda: random.uniform(-100.0, 100.0),
    # int generator
    lambda: random.randint(-100, 100))

test_math_operations = (
    # Math operators
    '__add__',
    '__div__',
    '__mul__',
    '__mod__',
    '__truediv__',
    '__floordiv__',

    # R-math operators
    '__radd__',
    '__rmod__',
    '__rmul__',
    '__rdiv__',
    '__rtruediv__',
    '__rfloordiv__')

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
    def assert_comparisons_equal(self, non_unit_a, non_unit_b, unit_a, unit_b):
        self.assertEqual(non_unit_a, unit_a.value)
        self.assertEqual(non_unit_b, unit_b.value)

        # Int types have __cmp__ in python 2.
        cmp_map = {
            '__lt__': {-1: True,  0: False, 1: False},
            '__le__': {-1: True,  0: True,  1: False},
            '__eq__': {-1: False, 0: True,  1: False},
            '__ne__': {-1: True,  0: False, 1: True},
            '__ge__': {-1: False, 0: True,  1: True},
            '__gt__': {-1: False, 0: False, 1: True}}

        cmp_msg = '{0} does not have __cmp__ or {1}'.format
        neq_msg = 'For operator {0}\nExpected: {1}\nActual: {2}\n'.format
        for op_name in test_comparison_operations:
            if hasattr(non_unit_a, '__cmp__'):
                expected = cmp_map[op_name][non_unit_a.__cmp__(non_unit_b)]
            else:
                if not hasattr(non_unit_a, op_name):
                    self.fail(cmp_msg(type(non_unit_a, op_name)))
                expected = getattr(non_unit_a, op_name)(non_unit_b)
            actual = getattr(unit_a, op_name)(unit_b)
            self.assertEqual(expected, actual,
                             neq_msg(op_name, expected, actual))

    def assert_pow_equal(self, non_unit_a, non_unit_b, unit_a, unit_b):
        self.assertEqual(non_unit_a, unit_a.value)
        self.assertEqual(non_unit_b, unit_b.value)

        # Zero is handled elsewhere.
        if non_unit_a == 0.0:
            non_unit_a = non_unit_a.__class__(1)
            unit_a = unit_a.__class__(1, units=unit_a.units)

        # Cannot raise negative value to a fraction.
        abs_non_unit_a = abs(non_unit_a)
        abs_unit_a = UnitsNumber(value=abs_non_unit_a, units=unit_a.units)
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
        rnd_unit_b = UnitsNumber(value=rnd_non_unit_b, units=unit_b.units)
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
               'UnitsNumber:      {1}\n'
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
        UnitsNumber.valid_units = None

    def test_units_set(self):
        """
        Setting units attribute behaves correctly.
        """
        UnitsNumber(0, 'ok')
        UnitsNumber.valid_units = ('good',)
        UnitsNumber(0, 'good')

    def test_str_and_repr(self):
        """
        String representations correctly created.
        """
        num = UnitsNumber(value=0, units='ok')
        expected = '0ok'
        actual = str(num)
        self.assertEqual(expected, actual)

        expected = "UnitsNumber(value=0, units='ok')"
        actual = num.__repr__()
        self.assertEqual(expected, actual)
        exec('expected = ' + num.__repr__())
        self.assertEqual(expected, num)

    def test_invalid_units(self):
        """
        Invalid units set wrong.
        """
        UnitsNumber.valid_units = ('good',)
        bad_units = 'bad'
        msg = UnitsNumber._error_messages['bad units'].format(bad_units)
        self.assertRaisesRegexp(
            UnitsError, msg, UnitsNumber, value=0, units=bad_units)

    def test_math_ops_with_no_units(self):
        """
        Math operations on unit-less numbers.
        """
        for i in xrange(100):
            for gen in test_type_generators:
                a, b = gen(), gen()
                a_unit = UnitsNumber(a, units=None)
                b_unit = UnitsNumber(b, units=None)

                self.assert_comparisons_equal(a, b, a_unit, b_unit)
                self.assert_pow_equal(a, b, a_unit, b_unit)
                self.assert_math_equal(a, b, a_unit, b_unit)
                self.assert_pow_raises(a, b, a_unit, b_unit)

        for a, b in permutations((0.0, -0.0, 1.0, -1.0), 2):
            a_unit = UnitsNumber(a, units=None)
            b_unit = UnitsNumber(b, units=None)

            self.assert_comparisons_equal(a, b, a_unit, b_unit)
            self.assert_pow_equal(a, b, a_unit, b_unit)
            self.assert_math_equal(a, b, a_unit, b_unit)
            self.assert_pow_raises(a, b, a_unit, b_unit)
