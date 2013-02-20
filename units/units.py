# -*- coding: iso-8859-1 -*-
import numbers
import operator


class UnitsError(Exception):
    pass


class UnitsNumber(numbers.Real):
    valid_units = None
    _error_messages = {
        'bad units':    'Invalid units {0}.'}

    def __init__(self, value, units=None):
        self.value = value
        self.units = units

    @property
    def units(self):
        return self.__units

    @units.setter
    def units(self, units):
        if self.valid_units is None or units in self.valid_units:
            self.__units = units
        else:
            raise UnitsError(self._error_messages['bad units'].format(units))

    # String and representational functions
    def __repr__(self):
        """
        Return string representation of an object.

        This calls the __repr__ methods of the value and units attributes.
        """
        return (self.__class__.__name__ +
                '(value=' + self.value.__repr__() + ', ' +
                'units=' + self.units.__repr__() + ')')

    def __str__(self):
        return '{0}{1}'.format(self.value, self.units)

    def in_self_units(self, other):
        return other.value

    # Comparison operators
    def __wrap_cmp(op_name):
        op = getattr(operator, op_name)

        def wrapped_op(self, other):
            return op(self.value, self.in_self_units(other))
        return wrapped_op

    __lt__ = __wrap_cmp('__lt__')
    __le__ = __wrap_cmp('__le__')
    __eq__ = __wrap_cmp('__eq__')
    __ne__ = __wrap_cmp('__ne__')
    __ge__ = __wrap_cmp('__ge__')
    __gt__ = __wrap_cmp('__gt__')

    # Math operators
    def __wrap_math(op_name):
        op = getattr(operator, op_name)

        def wrapped_math(self, other):
            return self.__class__(
                value=op(self.value, self.in_self_units(other)),
                units=self.units)
        return wrapped_math

    __add__ = __wrap_math('__add__')
    __div__ = __wrap_math('__div__')
    __mul__ = __wrap_math('__mul__')
    __mod__ = __wrap_math('__mod__')
    __pow__ = __wrap_math('__pow__')
    __truediv__ = __wrap_math('__truediv__')
    __floordiv__ = __wrap_math('__floordiv__')

    # R-math operators
    def __wrap_rmath(op_name):
        op = getattr(operator, op_name)

        def wrapped_rmath(self, other):
            return self.__class__(
                value=op(self.in_self_units(other), self.value),
                units=self.units)
        return wrapped_rmath

    __radd__ = __wrap_rmath('__add__')
    __rmod__ = __wrap_rmath('__mod__')
    __rmul__ = __wrap_rmath('__mul__')
    __rpow__ = __wrap_rmath('__pow__')
    __rdiv__ = __wrap_rmath('__div__')
    __rtruediv__ = __wrap_rmath('__truediv__')
    __rfloordiv__ = __wrap_rmath('__floordiv__')

    # Unitary operators
    def __wrap_unitary(op_name):
        op = getattr(operator, op_name)

        def wrapped_op(self):
            return self.__class__(value=op(self.value), units=self.units)
        return wrapped_op

    __abs__ = __wrap_unitary('__abs__')
    __neg__ = __wrap_unitary('__neg__')
    __pos__ = __wrap_unitary('__pos__')

    # Conversions to primitives - No wrapping here, these are not in the
    # operators module.
    def __trunc__(self):
        return self.value.__trunc__()

    def __float__(self):
        return float(self.value)
