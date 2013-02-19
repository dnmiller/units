import unittest


from units import UnitsNumber, UnitsError


class TestUnitNumber(unittest.TestCase):
    def test_units_set(self):
        """
        Setting units attribute behaves correctly.
        """
        num = UnitsNumber(0, 'ok')
