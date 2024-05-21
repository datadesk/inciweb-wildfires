import unittest

from inciweb_wildfires import get_incidents, get_prescribed_fires


class InciwebWildfiresUnitTest(unittest.TestCase):
    def test_inciweb(self):
        get_incidents()
        get_prescribed_fires()


if __name__ == "__main__":
    unittest.main()
