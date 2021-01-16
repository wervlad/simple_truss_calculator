#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from misc import camel_to_snake, rotate
from numpy.testing import assert_almost_equal


CENTER = (0, 0)
POINT = (1, 0)


class TestMisc(TestCase):
    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake("PinJoint"), "pin_joint")

    def test_rotate45(self):
        assert_almost_equal(rotate(CENTER, POINT, 45), (0.7071, 0.7071), 4)

    def test_rotate90(self):
        assert_almost_equal(rotate(CENTER, POINT, 90), (0, 1))

    def test_rotate135(self):
        assert_almost_equal(rotate(CENTER, POINT, 135), (-0.7071, 0.7071), 4)

    def test_rotate180(self):
        assert_almost_equal(rotate(CENTER, POINT, 180), (-1, 0))

    def test_rotate225(self):
        assert_almost_equal(rotate(CENTER, POINT, 225), (-0.7071, -0.7071), 4)

    def test_rotate270(self):
        assert_almost_equal(rotate(CENTER, POINT, 270), (0, -1))

    def test_rotate315(self):
        assert_almost_equal(rotate(CENTER, POINT, 315), (0.7071, -0.7071), 4)

    def test_rotate360(self):
        assert_almost_equal(rotate(CENTER, POINT, 360), POINT)
