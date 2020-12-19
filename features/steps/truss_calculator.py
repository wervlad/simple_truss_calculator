#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@when("Betty loads truss from '{filename}'")
def load_truss_from_examples(context, filename):
    context.truss = context.truss_builder.load_from(filename)

@then("results for 1st truss are the same as she caclucated manually")
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

@then("results for 4th truss are the same as she caclucated manually")
def calculate_truss_4(context):
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"],    2.5769, places=4)
    context.test.assertAlmostEqual(results["B2"],    2.5769, places=4)
    context.test.assertAlmostEqual(results["B3"],   -0.6250, places=4)
    context.test.assertAlmostEqual(results["PS1x"],  0.0000, places=4)
    context.test.assertAlmostEqual(results["PS1y"],  2.5000, places=4)
    context.test.assertAlmostEqual(results["RS1"],   2.5000, places=4)

@then("results for 5th truss are the same as she caclucated manually")
def calculate_truss_5(context):
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"],    3.5355, places=4)
    context.test.assertAlmostEqual(results["B2"],    3.5355, places=4)
    context.test.assertAlmostEqual(results["PS1x"],  2.5000, places=4)
    context.test.assertAlmostEqual(results["PS1y"],  2.5000, places=4)
    context.test.assertAlmostEqual(results["RS1"],   3.5355, places=4)
