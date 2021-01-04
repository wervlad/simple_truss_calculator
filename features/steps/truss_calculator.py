#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@when("Betty loads truss from '{filename}'")
def load_truss_from_examples(context, filename):
    context.truss.load_from(filename)

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

@then("results for 6th truss are the same as she caclucated manually")
def calculate_truss_6(context):
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"],    2.5000, places=4)
    context.test.assertAlmostEqual(results["B10"], -10.5000, places=4)
    context.test.assertAlmostEqual(results["B11"],   0.0000, places=4)
    context.test.assertAlmostEqual(results["B2"],   -1.5000, places=4)
    context.test.assertAlmostEqual(results["B3"],   -2.0000, places=4)
    context.test.assertAlmostEqual(results["B4"],    7.5000, places=4)
    context.test.assertAlmostEqual(results["B5"],    7.5000, places=4)
    context.test.assertAlmostEqual(results["B6"],   -6.0000, places=4)
    context.test.assertAlmostEqual(results["B7"],   -6.0000, places=4)
    context.test.assertAlmostEqual(results["B8"],   12.0000, places=4)
    context.test.assertAlmostEqual(results["B9"],    7.5000, places=4)
    context.test.assertAlmostEqual(results["PS1x"],  6.0000, places=4)
    context.test.assertAlmostEqual(results["PS1y"], 16.5000, places=4)
    context.test.assertAlmostEqual(results["RS1"], -10.5000, places=4)

@then("results for 7th truss are the same as she caclucated manually")
def calculate_truss_7(context):
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"],   -11.1905, places=4)
    context.test.assertAlmostEqual(results["B10"],   -9.0000, places=4)
    context.test.assertAlmostEqual(results["B11"],   -3.9992, places=4)
    context.test.assertAlmostEqual(results["B12"],    3.4632, places=4)
    context.test.assertAlmostEqual(results["B2"],     6.4625, places=4)
    context.test.assertAlmostEqual(results["B3"],   -12.9226, places=4)
    context.test.assertAlmostEqual(results["B4"],     6.0030, places=4)
    context.test.assertAlmostEqual(results["B5"],    11.2603, places=4)
    context.test.assertAlmostEqual(results["B6"],    -4.5028, places=4)
    context.test.assertAlmostEqual(results["B7"],   -13.0003, places=4)
    context.test.assertAlmostEqual(results["B8"],     9.0039, places=4)
    context.test.assertAlmostEqual(results["B9"],     3.4632, places=4)
    context.test.assertAlmostEqual(results["PS1x"], -11.1905, places=4)
    context.test.assertAlmostEqual(results["PS1y"],   0.0000, places=4)
    context.test.assertAlmostEqual(results["PS2x"],  15.1905, places=4)
    context.test.assertAlmostEqual(results["PS2y"],  11.0000, places=4)

@then("results for 8th truss are the same as she caclucated manually")
def calculate_truss_8(context):
    results = context.truss_calculator.calculate(context.truss)
    context.test.assertAlmostEqual(results["B1"],    8.2616, places=4)
    context.test.assertAlmostEqual(results["B10"], -11.3924, places=4)
    context.test.assertAlmostEqual(results["B11"],  -5.5949, places=4)
    context.test.assertAlmostEqual(results["B12"],  11.5950, places=4)
    context.test.assertAlmostEqual(results["B13"],  -5.7976, places=4)
    context.test.assertAlmostEqual(results["B2"],   -3.1309, places=4)
    context.test.assertAlmostEqual(results["B3"],   -8.2616, places=4)
    context.test.assertAlmostEqual(results["B4"],   10.2618, places=4)
    context.test.assertAlmostEqual(results["B5"],   -3.1308, places=4)
    context.test.assertAlmostEqual(results["B6"],  -11.3924, places=4)
    context.test.assertAlmostEqual(results["B7"],   19.7321, places=4)
    context.test.assertAlmostEqual(results["B8"],   11.5951, places=4)
    context.test.assertAlmostEqual(results["B9"],   -5.7975, places=4)
    context.test.assertAlmostEqual(results["PS1x"],  1.0000, places=4)
    context.test.assertAlmostEqual(results["PS1y"],  7.1547, places=4)
    context.test.assertAlmostEqual(results["RS1"],  10.0415, places=4)
