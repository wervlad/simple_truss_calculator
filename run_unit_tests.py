#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from unit_tests.test_misc import TestMisc
from unit_tests.test_observable import TestObservable
from unit_tests.test_history import TestHistory
from unit_tests.test_truss import TestTruss
from unit_tests.test_item_edit_state import TestItemEditState


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMisc))
    suite.addTest(unittest.makeSuite(TestObservable))
    suite.addTest(unittest.makeSuite(TestHistory))
    suite.addTest(unittest.makeSuite(TestTruss))
    suite.addTest(unittest.makeSuite(TestItemEditState))
    runner = unittest.TextTestRunner()
    runner.run(suite)
