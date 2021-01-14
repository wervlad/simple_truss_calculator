#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from itertools import repeat
from math import atan2, cos, sin, radians
import json
import re
import numpy  # type: ignore # pylint: disable=import-error
from misc import Observable


class History(Observable):
    def __init__(self, state):
        super().__init__()
        self.__state = state
        self.__undo_history = []
        self.__redo_history = []
        self.reset(state)

    def append(self, state):
        if state != self.__state:
            self.__undo_history.append(self.__state)
            self.__state = state
            self.__redo_history.clear()
            self.notify(dict(action="history changed"))

    def undo(self):
        if self.can_undo():
            self.__redo_history.append(self.__state)
            self.__state = self.__undo_history.pop()
            self.notify(dict(action="history changed"))
        return self.__state

    def redo(self):
        if self.can_redo():
            self.__undo_history.append(self.__state)
            self.__state = self.__redo_history.pop()
            self.notify(dict(action="history changed"))
        return self.__state

    def can_undo(self):
        return bool(self.__undo_history)

    def can_redo(self):
        return bool(self.__redo_history)

    def reset(self, state):
        self.__state = state
        self.__undo_history.clear()
        self.__redo_history.clear()
        self.notify(dict(action="history changed"))


class Truss(Observable):
    JOINTS = ("PinJoint", "PinnedSupport", "RollerSupport")
    MANDATORY_FIELDS = dict(
        PinJoint=("type", "id", "x", "y"),
        PinnedSupport=("type", "id", "x", "y"),
        RollerSupport=("type", "id", "x", "y", "angle"),
        Beam=("type", "id", "end1", "end2"),
        Force=("type", "id", "angle", "applied_to", "value"))

    def __init__(self):
        super().__init__()
        self.__items = ()
        self.__left = 0
        self.__right = 0
        self.__bottom = 0
        self.__top = 0

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, t):
        self.__items = tuple(t)
        self.__remove_invalid()
        self.__update_cache()
        self.__update_dimensions()
        self.notify(dict(action="truss modified"))

    def __iter__(self):
        return iter(self.items)

    def __remove_invalid(self):
        invalid_beams = tuple(b for b in self.find_by_type("Beam")
                              if None in (self.find_by_id(b["end1"]),
                                          self.find_by_id(b["end2"])))
        invalid_forces = tuple(f for f in self.find_by_type("Force")
                               if self.find_by_id(f["applied_to"]) is None)
        invalid = invalid_beams + invalid_forces
        if invalid:
            self.__items = tuple(i for i in self.items if i not in invalid)
            self.notify(dict(action="invalid items removed", items=invalid))

    def __update_cache(self):
        for beam in self.find_by_type("Beam"):
            end1 = self.find_by_id(beam["end1"])
            end2 = self.find_by_id(beam["end2"])
            beam.update(dict(x1=end1["x"], y1=end1["y"],
                             x2=end2["x"], y2=end2["y"]))
        for force in self.find_by_type("Force"):
            joint = self.find_by_id(force["applied_to"])
            force.update(dict(x=joint["x"], y=joint["y"]))

    def __update_dimensions(self):
        xs = tuple(j["x"] for j in self.joints)
        ys = tuple(j["y"] for j in self.joints)
        self.__left = min(xs, default=0)
        self.__right = max(xs, default=0)
        self.__bottom = min(ys, default=0)
        self.__top = max(ys, default=0)

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

    def new(self):
        self.items = ()

    def append(self, item):
        self.items = self.items + (item,)

    def remove(self, item):
        self.items = tuple(x for x in self.items if item != x)

    def replace(self, old, new):
        self.items = tuple(x for x in self.items if old != x) + (new,)

    def save_as(self, filename):
        def drop_cache(items):
            return tuple({f: i[f] for f in self.MANDATORY_FIELDS[i["type"]]}
                         for i in items)

        with open(filename, "w") as f:
            f.write(json.dumps(drop_cache(self.items)))

    def load_from(self, filename):
        with open(filename, "r") as f:
            self.items = json.load(f)

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    def find_by_id(self, item_id):
        items = tuple(filter(lambda x: item_id == x["id"], self.items))
        return items[0] if items else None

    def find_by_type(self, item_type):
        return (i for i in self.items if i["type"] == item_type)

    def get_new_id_for(self, item_type):
        def extract_index(item_id):
            return int(re.findall(r'\d+', item_id)[0])

        prefix = re.sub("[^A-Z]", "", item_type)
        max_id = max([extract_index(i["id"])
                      for i in self.find_by_type(item_type)], default=0)
        return f"{prefix}{max_id + 1}"

    @property
    def joints(self):
        return (i for i in self.items if self.is_joint(i))

    @classmethod
    def is_joint(cls, item):
        return item.get("type") in cls.JOINTS

    def linked_beams(self, joint):
        return tuple(beam for beam in self.find_by_type("Beam")
                     if joint["id"] in (beam["end1"], beam["end2"]))

    def linked_forces(self, joint):
        return tuple(force for force in self.find_by_type("Force")
                     if joint["id"] == force["applied_to"])

    def calculate(self):  # pylint: disable=too-many-locals
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
            for beam in self.linked_beams(joint):
                ax[x.index((beam, ""))] = cos(beam_angle(beam, joint))
                ay[x.index((beam, ""))] = sin(beam_angle(beam, joint))
            if joint["type"] == "RollerSupport":
                ax[x.index((joint, ""))] = cos(radians(joint["angle"]))
                ay[x.index((joint, ""))] = sin(radians(joint["angle"]))
            if joint["type"] == "PinnedSupport":
                ax[x.index((joint, "x"))] = 1
                ay[x.index((joint, "y"))] = 1
            a += [ax, ay]

            known_forces = self.linked_forces(joint)
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
