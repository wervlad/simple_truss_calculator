#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@given("new truss created")
def create_new_truss(context):
    context.conapp.writeline("new")
    context.test.assertTrue(is_truss_empty(context))

@when("Betty adds pinned support")
def add_pinned_support(context):
    context.conapp.writeline("add PinnedSupport")

@then("Betty will see a pinned support on print command")
def pinned_support_shown_by_print_command(context):
    context.conapp.writeline("print")
    context.test.assertIn("PinnedSupport", context.conapp.readline())

@when("Betty adds a beam")
def add_beam(context):
    context.conapp.writeline("add Beam")

@then("Betty will see a pinned support and a beam on print command")
def pinned_support_and_beam_shown_by_print_command(context):
    context.conapp.writeline("print")
    truss = context.conapp.readline()
    context.test.assertIn("PinnedSupport", truss)
    context.test.assertIn("Beam", truss)

@when("Betty misstypes and tries to add a ream")
def attempt_to_add_misstyped_item(context):
    context.conapp.writeline("add Ream")

@then("Betty will see nothing on print command")
def nothing_shown_by_print_command(context):
    context.test.assertTrue(is_truss_empty(context))

def is_truss_empty(context):
    context.conapp.writeline("print")
    truss = context.conapp.readline()
    return truss == "[]"
