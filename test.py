#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from inciweb_wildfires import get_fires


class InciwebWildfiresUnitTest(unittest.TestCase):

    def test_inciweb(self):
        get_fires()


if __name__ == '__main__':
    unittest.main()
