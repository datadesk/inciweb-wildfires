import unittest

from inciweb_wildfires import get_incidents


class InciwebWildfiresUnitTest(unittest.TestCase):
    def test_inciweb(self):
        get_incidents()


if __name__ == "__main__":
    unittest.main()
