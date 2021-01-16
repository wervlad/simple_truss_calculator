#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import Mock
from domain import History


class TestHistory(TestCase):
    def setUp(self):
        self.history = History(None)

    def test_can_not_undo_empty_history(self):
        self.assertFalse(self.history.can_undo())

    def test_can_not_redo_empty_history(self):
        self.assertFalse(self.history.can_redo())

    def test_can_undo_history_with_one_state(self):
        self.history.append(1)
        self.assertTrue(self.history.can_undo())

    def test_can_not_redo_history_without_calling_undo(self):
        self.history.append(1)
        self.assertFalse(self.history.can_redo())

    def test_can_redo_history_after_calling_undo(self):
        self.history.append(1)
        self.history.undo()
        self.assertTrue(self.history.can_redo())

    def test_can_not_redo_history_after_undo_and_append(self):
        self.history.append(1)
        self.history.undo()
        self.history.append(2)
        self.assertFalse(self.history.can_redo())

    def test_can_not_undo_history_with_one_state_after_one_undo(self):
        self.history.append(1)
        self.assertTrue(self.history.can_undo())
        self.history.undo()
        self.assertFalse(self.history.can_undo())

    def test_undo(self):
        initial_state = 0
        self.history = History(initial_state)
        self.history.append(1)
        self.assertEqual(self.history.undo(), initial_state)

    def test_redo(self):
        state = 1
        self.history.append(state)
        self.history.undo()
        self.assertEqual(self.history.redo(), state)

    def test_notify_on_append(self):
        callback = Mock()
        self.history.append_observer_callback(callback)
        self.history.append(1)
        callback.assert_called_with(dict(action="history changed"))

    def test_notify_on_undo(self):
        self.history.append(1)
        callback = Mock()
        self.history.append_observer_callback(callback)
        self.history.undo()
        callback.assert_called_with(dict(action="history changed"))

    def test_notify_on_redo(self):
        self.history.append(1)
        self.history.undo()
        callback = Mock()
        self.history.append_observer_callback(callback)
        self.history.redo()
        callback.assert_called_with(dict(action="history changed"))

    def test_notify_on_reset(self):
        callback = Mock()
        self.history.append_observer_callback(callback)
        self.history.reset("test")
        callback.assert_called_with(dict(action="history changed"))
