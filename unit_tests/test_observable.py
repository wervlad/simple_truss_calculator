#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import Mock
from misc import Observable


class TestObservable(TestCase):
    def test_notify(self):
        observable = Observable()
        callback = Mock()
        observable.append_observer_callback(callback)
        message = "hey there!"

        observable.notify(message)

        callback.assert_called_with(message)
