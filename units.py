import numbers


class UnitsError(Exception):
    pass


class UnitsNumber(numbers.Real):
    valid_units = None

    _error_messages = {
        'bad units':    'Invalid units {0}.'}

    def __init__(self, value=None, units=None):
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

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __repr__(self):
        return (self.__class__.__name__ +
                '(value=' + self.value.__repr__() + ', ' +
                'units=' + self.units.__repr__() + ')')

    def __str__(self):
        return '{0}{1}'.format(self.value, self.units)

    def __abs__(self):
        pass

    def __add__(self, other):
        pass

    def __div__(self, other):
        pass

    def __eq__(self, other):
        pass

    def __float__(self):
        pass

    def __floordiv__(self, other):
        pass

    def __le__(self, other):
        pass

    def __lt__(self, other):
        pass

    def __mod__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __neg__(self, other):
        pass

    def __pos__(self):
        pass

    def __pow__(self, other):
        pass

    def __radd__(self, other):
        pass

    def __rdiv__(self, other):
        pass

    def __rfloordiv__(self, other):
        pass

    def __rmod__(self, other):
        pass

    def __rmul__(self, other):
        pass

    def __rpow__(self, other):
        pass

    def __rtruediv__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __trunc__(self):
        pass
