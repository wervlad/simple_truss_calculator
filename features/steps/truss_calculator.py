#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@when("Betty loads truss from '{filename}'")
def load_truss_from_examples(context, filename):
    context.truss = context.truss_builder.load_from(filename)

@then("autocalculated results are the same as she caclucated manually")
def calculate_truss(context):
    # [
    # {"id": "PS1", "type": "PinnedSupport", "x": 0.0, "y": 0.0},
    # {"id": "PS2", "type": "PinnedSupport", "x": 50.0, "y": 0.0},
    # {"id": "PJ3", "type": "PinJoint", "x": 25.0, "y": 100.0},
    # {"end1": "PJ3", "end2": "PS1", "id": "B1", "type": "Beam"},
    # {"end1": "PJ3", "end2": "PS2", "id": "B2", "type": "Beam"},
    # {"angle": -90.0, "applied_to": "PJ3", "id": "F1", "type": "Force", "value": 5.0}
    # ]
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"], -2.5769410160, decimal=10)
    context.test.assertAlmostEqual(results["B2"], -2.5769410160, decimal=10)
    context.test.assertAlmostEqual(results["PS1_x"], 0.6250000000, decimal=10)
    context.test.assertAlmostEqual(results["PS2_x"], -0.6250000000, decimal=10)
    context.test.assertAlmostEqual(results["PS1_y"], 2.5000000000, decimal=10)
    context.test.assertAlmostEqual(results["PS2_y"], 2.5000000000, decimal=10)
