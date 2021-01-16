#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from view import ItemEditState


class TestItemEditState(TestCase):
    def setUp(self):
        self.state = ItemEditState()

    def test_new_pin_joint(self):
        self.state.new("PinJoint")

        item = dict(type="PinJoint", x=13, y=33)
        self.assertEqual(self.state.process(dict(action="move", x=13, y=33)),
                         dict(action="update tmp", item=item))

        item.update(**dict(x=47, y=138))
        self.assertEqual(self.state.process(dict(action="click", x=47, y=138)),
                         dict(action="finish editing", item=item))

    def test_new_pinned_support(self):
        self.state.new("PinnedSupport")

        item = dict(type="PinnedSupport", x=13, y=33)
        self.assertEqual(self.state.process(dict(action="move", x=13, y=33)),
                         dict(action="update tmp", item=item))

        item.update(**dict(x=47, y=18))
        self.assertEqual(self.state.process(dict(action="click", x=47, y=18)),
                         dict(action="finish editing", item=item))

    def test_new_roller_support(self):
        self.state.new("RollerSupport")

        item = dict(type="RollerSupport", x=13, y=33, angle=90)
        self.assertEqual(self.state.process(dict(action="move", x=13, y=33)),
                         dict(action="update tmp", item=item))

        item = dict(type="RollerSupport", x=47, y=18, angle=0)
        self.assertEqual(self.state.process(dict(action="click", x=47, y=18)),
                         dict(action="update tmp", item=item))

        item = dict(type="RollerSupport", x=47, y=18, angle=90)
        self.assertEqual(self.state.process(dict(action="click", x=47, y=10)),
                         dict(action="finish editing", item=item))

    def test_new_beam(self):
        self.state.new("Beam")

        item = dict(type="Beam", x1=13, y1=33, x2=13, y2=33)
        self.assertEqual(self.state.process(dict(action="move", x=13, y=33)),
                         dict(action="update tmp", item=item))

        end1 = dict(type="PinnedSupport", id="PS1", x=0.0, y=0.0)
        item.update(**dict(end1=end1["id"], x1=end1["x"], y1=end1["y"]))
        self.assertEqual(self.state.process(dict(action="item click",
                                                 x=13, y=33, item=end1)),
                         dict(action="update tmp", item=item))

        end2 = dict(type="PinnedSupport", id="PS2", x=2.0, y=0.0)
        item.update(**dict(end2=end2["id"], x2=end2["x"], y2=end2["y"]))
        self.assertEqual(self.state.process(dict(action="item click",
                                                 x=13, y=33, item=end2)),
                         dict(action="finish editing", item=item))

    def test_new_force(self):
        self.state.new("Force")

        item = dict(type="Force", x=13, y=33, angle=-45)
        self.assertEqual(self.state.process(dict(action="move", x=13, y=33)),
                         dict(action="update tmp", item=item))

        j = dict(type="PinnedSupport", id="PS1", x=0.0, y=0.0)
        item.update(**dict(applied_to=j["id"], x=j["x"], y=j["y"], angle=180))
        self.assertEqual(self.state.process(dict(action="item click", item=j,
                                                 x=j["x"], y=j["y"])),
                         dict(action="update tmp", item=item))

        item.update(**dict(angle=90))
        self.assertEqual(self.state.process(dict(action="click", x=j["x"],
                                                 y=j["y"] - 10)),
                         dict(action="specify force value", item=item))

    def test_edit_force(self):
        f = dict(type="Force", id="F1", applied_to="PJ1", x=0, y=0, value=3.0)
        self.state.edit(f)

        item = {**f, "angle": 0}
        self.assertEqual(self.state.process(dict(action="move", x=13, y=0)),
                         dict(action="update tmp", item=item))

        item["angle"] = 90.0
        self.assertEqual(self.state.process(dict(action="click", x=0, y=-1)),
                         dict(action="specify force value", item=item))

    def test_default(self):
        self.state.default()

        j = {"id": "PS1", "type": "PinnedSupport", "x": 0.0, "y": 0.0}
        self.assertEqual(self.state.process(dict(action="item click", item=j,
                                                 x=0, y=0)),
                         dict(action="select", item=j))

        self.assertEqual(self.state.process(dict(action="delete")),
                         dict(action="delete", item=j))

        self.assertEqual(self.state.process(dict(action="delete")),
                         dict(action="delete", item=None))

        self.assertEqual(self.state.process(dict(action="click", x=0, y=0)),
                         dict(action="cancel"))
