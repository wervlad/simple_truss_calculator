#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from itertools import repeat
from math import atan2, cos, sin, radians
import json
import numpy


class Truss:
    JOINTS = ("PinJoint", "PinnedSupport", "RollerSupport")

    def __init__(self):
        self.__items = ()
        self.__left = 0
        self.__right = 0
        self.__bottom = 0
        self.__top = 0
        self.__observer_callbacks = []

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, t):
        self.__items = tuple(t)
        self.__update_dimensions()
        self.__notify(self)

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    @property
    def bottom(self):
        return self.__bottom

    @property
    def top(self):
        return self.__top

    def append_observer_callback(self, callback):
        self.__observer_callbacks.append(callback)

    def new(self):
        self.items = ()

    def append(self, item):
        self.items = self.items + (item,)

    def remove(self, item):
        self.items = tuple(x for x in self.items if item != x)

    def replace(self, old, new):
        self.items = tuple(x for x in self.items if old != x) + (new,)

    def save_as(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(self.items))

    def load_from(self, filename):
        with open(filename, "r") as f:
            self.items = json.load(f)

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    def __update_dimensions(self):
        xs = tuple(filter(None.__ne__, (item.get("x") for item in self.items)))
        ys = tuple(filter(None.__ne__, (item.get("y") for item in self.items)))
        self.__left = min(xs, default=0)
        self.__right = max(xs, default=0)
        self.__bottom = min(ys, default=0)
        self.__top = max(ys, default=0)

    def find_by_id(self, item_id):
        items = tuple(filter(lambda x: item_id == x["id"], self.items))
        return items[0] if items else None

    def find_by_type(self, item_type):
        return tuple(filter(lambda x: x["type"] == item_type, self.items))

    @property
    def joints(self):
        return tuple(filter(lambda x: x["type"] in self.JOINTS, self.items))

    def __notify(self, message):
        for callback in self.__observer_callbacks:
            callback(message)

    def calculate(self):
        """
        Calculate reactions using method of joints.
        https://en.wikipedia.org/wiki/Structural_analysis#Method_of_Joints
        """
        def beam_angle(b, origin):
            end_id = b["end1"] if origin["id"] == b["end2"] else b["end2"]
            end = self.find_by_id(end_id)
            return atan2(origin["y"] - end["y"], origin["x"] - end["x"])

        def force_x_value(force):
            return force["value"] * cos(radians(force["angle"]))

        def force_y_value(force):
            return force["value"] * sin(radians(force["angle"]))

        # a·x = b (https://en.wikipedia.org/wiki/System_of_linear_equations)
        a = []  # coefficients matrix
        x = []  # unknown reactions vector
        b = []  # constants vector (known forces)

        forces_in_beams = zip(self.find_by_type("Beam"), repeat(""))
        rs_reactions = zip(self.find_by_type("RollerSupport"), repeat(""))
        ps_x_reactions = zip(self.find_by_type("PinnedSupport"), repeat("x"))
        ps_y_reactions = zip(self.find_by_type("PinnedSupport"), repeat("y"))
        x = [*forces_in_beams, *rs_reactions, *ps_x_reactions, *ps_y_reactions]

        # joint equilibrium equations
        for joint in self.joints:
            ax = [0] * len(x)
            ay = [0] * len(x)
            linked_beams = (beam for beam in self.find_by_type("Beam")
                            if joint["id"] in (beam["end1"], beam["end2"]))
            for beam in linked_beams:
                ax[x.index((beam, ""))] = cos(beam_angle(beam, joint))
                ay[x.index((beam, ""))] = sin(beam_angle(beam, joint))
            if joint["type"] == "RollerSupport":
                ax[x.index((joint, ""))] = cos(radians(joint["angle"]))
                ay[x.index((joint, ""))] = sin(radians(joint["angle"]))
            if joint["type"] == "PinnedSupport":
                ax[x.index((joint, "x"))] = 1
                ay[x.index((joint, "y"))] = 1
            a += [ax, ay]

            known_forces = [f for f in self.find_by_type("Force")
                            if joint["id"] == f["applied_to"]]
            Fx_in_joint = sum(force_x_value(f) for f in known_forces)
            Fy_in_joint = -sum(force_y_value(f) for f in known_forces)
            b += [Fx_in_joint, Fy_in_joint]

        # check that system has exactly one solution
        # https://en.wikipedia.org/wiki/Rouché–Capelli_theorem
        if len(x) > numpy.linalg.matrix_rank(a):
            # https://en.wikipedia.org/wiki/Statically_indeterminate
            raise ValueError("truss is statically indeterminate")
        a_b = numpy.concatenate((numpy.matrix(a).T, numpy.matrix(b))).T # (a|b)
        if numpy.linalg.matrix_rank(a) < numpy.linalg.matrix_rank(a_b):
            raise ValueError("unbalanced truss")

        x_names = [i[0]["id"] + i[1] for i in x]
        x_values = numpy.linalg.lstsq(a, b, rcond=None)[0]
        return dict(zip(x_names, x_values))
