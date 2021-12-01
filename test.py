#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from inciweb_wildfires import get_inicidents


class InciwebWildfiresUnitTest(unittest.TestCase):

    def test_inciweb(self):
        get_inicidents()


if __name__ == '__main__':
    unittest.main()
