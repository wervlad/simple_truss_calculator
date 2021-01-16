#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import Mock
from domain import Truss


class TestTruss(TestCase):
    def setUp(self):
        self.truss = Truss()

    def test_left(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(ps)
        self.truss.append(pj)
        self.assertEqual(0, self.truss.left)

    def test_right(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(ps)
        self.truss.append(pj)
        self.assertEqual(3, self.truss.right)

    def test_top(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(ps)
        self.truss.append(pj)
        self.assertEqual(5, self.truss.top)

    def test_bottom(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(ps)
        self.truss.append(pj)
        self.assertEqual(0, self.truss.bottom)

    def test_width(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(ps)
        self.truss.append(pj)
        self.assertEqual(abs(pj["x"] - ps["x"]), self.truss.width)

    def test_height(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(ps)
        self.truss.append(pj)
        self.assertEqual(abs(pj["y"] - ps["y"]), self.truss.height)

    def test_append_item(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(pj)
        self.assertIn(pj, self.truss)

    def test_append_force_with_inexistent_support(self):
        force = {"type": "Force", "id": "F1", "applied_to": "PJ1",
                 "angle": 180.0, "value": 2.0}
        self.truss.append(force)
        self.assertNotIn(force, self.truss)

    def test_append_force_with_existent_support(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 0.0}
        force = {"type": "Force", "id": "F1", "applied_to": "PJ1",
                 "angle": 180.0, "value": 2.0}
        self.truss.append(pj)
        self.truss.append(force)
        self.assertIn(force, self.truss)

    def test_append_beam_with_inexistent_supports(self):
        beam = {"type": "Beam", "id": "B1", "end1": "PJ1", "end2": "PS1"}
        self.truss.append(beam)
        self.assertNotIn(beam, self.truss)

    def test_append_beam_with_existent_supports(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 0.0}
        beam = {"type": "Beam", "id": "B1", "end1": "PJ1", "end2": "PS1"}
        self.truss.append(ps)
        self.truss.append(pj)
        self.truss.append(beam)
        self.assertIn(beam, self.truss)

    def test_force_pos(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": -9.0}
        force = {"type": "Force", "id": "F1", "applied_to": "PJ1",
                 "angle": 180.0, "value": 2.0}
        self.truss.append(pj)
        self.truss.append(force)
        self.assertEqual(self.truss.find_by_id("F1")["x"], pj["x"])
        self.assertEqual(self.truss.find_by_id("F1")["y"], pj["y"])

    def test_beam_pos(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5.0}
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        beam = {"type": "Beam", "id": "B1", "end1": "PJ1", "end2": "PS1"}
        self.truss.append(ps)
        self.truss.append(pj)
        self.truss.append(beam)
        self.assertEqual(self.truss.find_by_id("B1")["x1"], pj["x"])
        self.assertEqual(self.truss.find_by_id("B1")["y1"], pj["y"])
        self.assertEqual(self.truss.find_by_id("B1")["x2"], ps["x"])
        self.assertEqual(self.truss.find_by_id("B1")["y2"], ps["y"])

    def test_remove_item(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(pj)
        self.truss.remove(pj)
        self.assertNotIn(pj, self.truss)

    def test_replace_item(self):
        old = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        new = {"type": "PinJoint", "id": "PJ1", "x": 0.0, "y": 0.0}
        self.truss.append(old)
        self.truss.replace(old, new)
        self.assertIn(new, self.truss)
        self.assertNotIn(old, self.truss)

    def test_create_new_truss(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(pj)
        self.truss.new()
        self.assertEqual(tuple(self.truss), ())

    def test_find_by_id(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        self.truss.append(pj)
        self.assertEqual(pj, self.truss.find_by_id(pj["id"]))

    def test_find_by_type(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        self.truss.append(pj)
        self.truss.append(ps)
        self.assertIn(pj, self.truss.find_by_type("PinJoint"))
        self.assertNotIn(ps, self.truss.find_by_type("PinJoint"))

    def test_get_new_id_for_pin_joint_in_empty_truss(self):
        self.assertEqual(self.truss.get_new_id_for("PinJoint"), "PJ1")

    def test_get_new_id_for_pin_joint_in_non_empty_truss(self):
        pj = {"type": "PinJoint", "id": "PJ10", "x": 3.0, "y": 5}
        self.truss.append(pj)
        self.assertEqual(self.truss.get_new_id_for("PinJoint"), "PJ11")

    def test_pin_joint_is_in_joints(self):
        pj = {"type": "PinJoint", "id": "PJ10", "x": 3.0, "y": 5}
        self.truss.append(pj)
        self.assertIn(pj, self.truss.joints)

    def test_force_not_in_joints(self):
        pj = {"type": "PinJoint", "id": "PJ1", "x": 3.0, "y": 5}
        force = {"type": "Force", "id": "F1", "applied_to": "PJ1",
                 "angle": 180.0, "value": 2.0}
        self.truss.append(pj)
        self.truss.append(force)
        self.assertNotIn(force, self.truss.joints)
        self.assertIn(force, self.truss)

    def test_pin_joint_is_joint(self):
        pj = {"type": "PinJoint", "id": "PJ10", "x": 3.0, "y": 5}
        self.assertTrue(self.truss.is_joint(pj))

    def test_roller_support_is_joint(self):
        rs = {"type": "RollerSupport", "id": "RS1",
              "x": 9.0, "y": 2.598, "angle": 90}
        self.assertTrue(self.truss.is_joint(rs))

    def test_pinned_support_is_joint(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0}
        self.assertTrue(self.truss.is_joint(ps))

    def test_beam_is_not_joint(self):
        beam = {"type": "Beam", "id": "B1", "end1": "PJ1", "end2": "PS1"}
        self.assertFalse(self.truss.is_joint(beam))

    def test_force_is_not_joint(self):
        force = {"type": "Force", "id": "F1", "applied_to": "PJ1",
                 "angle": 180.0, "value": 2.0}
        self.assertFalse(self.truss.is_joint(force))

    def test_linked_beams(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0.0}
        rs = {"type": "RollerSupport", "id": "RS1",
              "x": 50.0, "y": 0.0, "angle": 90.0}
        pj = {"type": "PinJoint", "id": "PJ1", "x": 25.0, "y": 100.0}
        beam1 = {"type": "Beam", "id": "B1", "end1": "PJ1", "end2": "PS1"}
        beam2 = {"type": "Beam", "id": "B2", "end1": "PJ1", "end2": "RS1"}
        beam3 = {"type": "Beam", "id": "B3", "end1": "PS1", "end2": "RS1"}
        for i in (ps, rs, pj, beam1, beam2, beam3):
            self.truss.append(i)
        self.assertIn(beam1, self.truss.linked_beams(pj))
        self.assertIn(beam2, self.truss.linked_beams(pj))
        self.assertNotIn(beam3, self.truss.linked_beams(pj))

    def test_linked_forces(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0.0}
        rs = {"type": "RollerSupport", "id": "RS1",
              "x": 50.0, "y": 0.0, "angle": 90.0}
        force1 = {"type": "Force", "id": "F1", "applied_to": "PS1",
                  "angle": 0, "value": 2}
        force2 = {"type": "Force", "id": "F2", "applied_to": "RS1",
                  "angle": 0, "value": 3}
        for i in (ps, rs, force1, force2):
            self.truss.append(i)
        self.assertIn(force1, self.truss.linked_forces(ps))
        self.assertNotIn(force1, self.truss.linked_forces(rs))
        self.assertIn(force2, self.truss.linked_forces(rs))
        self.assertNotIn(force2, self.truss.linked_forces(ps))

    def test_calculate(self):
        ps = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0.0}
        rs = {"type": "RollerSupport", "id": "RS1",
              "x": 50.0, "y": 0.0, "angle": 90.0}
        beam = {"type": "Beam", "id": "B1", "end1": "PS1", "end2": "RS1"}
        force = {"type": "Force", "id": "F1", "applied_to": "RS1",
                 "angle": 0, "value": 2}
        for i in (ps, rs, beam, force):
            self.truss.append(i)
        results = self.truss.calculate()
        self.assertAlmostEqual(results["B1"], 2)
        self.assertAlmostEqual(results["RS1"], 0)
        self.assertAlmostEqual(results["PS1x"], 2)
        self.assertAlmostEqual(results["PS1y"], 0)

    def test_calculate_statically_undeterminate_truss_raises_exception(self):
        ps1 = {"type": "PinnedSupport", "id": "PS1", "x": 0.0, "y": 0.0}
        ps2 = {"type": "PinnedSupport", "id": "PS2", "x": 2.0, "y": 0.0}
        beam = {"type": "Beam", "id": "B1", "end1": "PS1", "end2": "PS2"}
        force = {"type": "Force", "id": "F1", "applied_to": "PS1",
                 "angle": 0, "value": 2}
        for i in (ps1, ps2, beam, force):
            self.truss.append(i)
        with self.assertRaises(ValueError) as c:
            self.truss.calculate()
        self.assertEqual("truss is statically indeterminate", str(c.exception))

    def test_calculate_unbalanced_truss_raises_exception(self):
        rs = {"type": "RollerSupport", "id": "RS1",
              "x": 50.0, "y": 0.0, "angle": 90.0}
        force = {"type": "Force", "id": "F1", "applied_to": "RS1",
                 "angle": 0, "value": 2}
        self.truss.append(rs)
        self.truss.append(force)
        with self.assertRaises(ValueError) as c:
            self.truss.calculate()
        self.assertEqual("unbalanced truss", str(c.exception))

    def test_notify_on_new_truss(self):
        callback = Mock()
        self.truss.append_observer_callback(callback)
        self.truss.new()
        callback.assert_called_with(dict(action="truss modified"))

    def test_notify_on_append(self):
        callback = Mock()
        self.truss.append_observer_callback(callback)
        ps = dict(type="PinnedSupport", id="PS1", x=0.0, y=0.0)
        self.truss.append(ps)
        callback.assert_called_with(dict(action="truss modified"))

    def test_notify_on_remove(self):
        ps = dict(type="PinnedSupport", id="PS1", x=0.0, y=0.0)
        self.truss.append(ps)
        callback = Mock()
        self.truss.append_observer_callback(callback)
        self.truss.remove(ps)
        callback.assert_called_with(dict(action="truss modified"))

    def test_notify_on_replace(self):
        ps1 = dict(type="PinnedSupport", id="PS1", x=0.0, y=0.0)
        ps2 = dict(type="PinnedSupport", id="PS1", x=2.0, y=0.0)
        self.truss.append(ps1)
        callback = Mock()
        self.truss.append_observer_callback(callback)
        self.truss.replace(ps1, ps2)
        callback.assert_called_with(dict(action="truss modified"))
