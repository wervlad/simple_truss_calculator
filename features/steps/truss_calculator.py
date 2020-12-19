#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@when("Betty loads truss from '{filename}'")
def load_truss_from_examples(context, filename):
    context.truss = context.truss_builder.load_from(filename)

@then("autocalculated results are the same as she caclucated manually")
def calculate_truss(context):
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"],    2.5769, places=4)
    context.test.assertAlmostEqual(results["B2"],    2.5769, places=4)
    context.test.assertAlmostEqual(results["PS1x"],  0.6250, places=4)
    context.test.assertAlmostEqual(results["PS2x"], -0.6250, places=4)
    context.test.assertAlmostEqual(results["PS1y"],  2.5000, places=4)
    context.test.assertAlmostEqual(results["PS2y"],  2.5000, places=4)

@then("calculate raises exception '{msg}'")
def calculate_raises_exception(context, msg):
    with context.test.assertRaisesRegex(ValueError, msg):
        results = context.truss_calculator.calculate(context.truss)
