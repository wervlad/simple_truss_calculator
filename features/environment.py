#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
from unittest import TestCase

TEST_FILENAME = "truss.json"

def before_all(context):
    context.test = TestCase()
    import truss_builder
    context.truss_builder = truss_builder

def after_all(context):
    os.remove(TEST_FILENAME)

def before_scenario(context, scenario):
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return
