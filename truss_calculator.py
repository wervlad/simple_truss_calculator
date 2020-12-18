#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from math import atan2, cos, sin, radians
import numpy

def calculate(truss):
    """
    Calculate reactions using method of joints.
    https://en.wikipedia.org/wiki/Structural_analysis#Method_of_Joints
    """
    def items_by_type(item_type):
        return tuple(filter(lambda x: x["type"] == item_type, truss))

    def beam_angle(beam, origin):
        end_id = beam["end1"] if origin["id"] == beam["end2"] else beam["end2"]
        end = list(filter(lambda x: end_id == x["id"], truss))[0]
        return atan2(origin["y"] - end["y"], origin["x"] - end["x"])

    def force_x_value(force):
        return force["value"] * cos(radians(force["angle"]))

    def force_y_value(force):
        return force["value"] * sin(radians(force["angle"]))

    forces = items_by_type("Force")
    beams = items_by_type("Beam")
    pinned_supports = items_by_type("PinnedSupport")
    roller_supports = items_by_type("RollerSupport")
    pin_joints = items_by_type("PinJoint")
    joints = (*pinned_supports, *roller_supports, *pin_joints)

    # a·x = b (https://en.wikipedia.org/wiki/System_of_linear_equations)
    a = []  # coefficients matrix
    x = []  # unknown reactions vector
    b = []  # constants vector (known forces)

    x += [(n, "") for n in beams]  # forces in beams
    x += [(n, "") for n in roller_supports]  # roller supports reactions
    x += [(n, "x") for n in pinned_supports]  # pinned supports x reactions
    x += [(n, "y") for n in pinned_supports]  # pinned supports y reactions

    # joint equilibrium equations
    for joint in joints:
        ax = [0] * len(x)
        ay = [0] * len(x)
        linked_beams = (beam for beam in beams
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

        known_forces = [f for f in forces if joint["id"] == f["applied_to"]]
        Fx_in_joint = sum(force_x_value(f) for f in known_forces)
        Fy_in_joint = -sum(force_y_value(f) for f in known_forces)
        b += [Fx_in_joint, Fy_in_joint]

    x_names = [i[0]["id"] + i[1] for i in x]
    x_values = numpy.linalg.lstsq(a, b, rcond=None)[0]
    return dict(zip(x_names, x_values))
