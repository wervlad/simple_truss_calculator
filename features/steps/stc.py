#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@given("new truss created")
def create_new_truss(context):
    context.conapp.writeline("new")
    context.test.assertTrue(is_truss_empty(context))

@when("Betty adds pinned support")
def add_pinned_support(context):
    context.conapp.writeline("add PinnedSupport")

@then("she will see a pinned support on print command")
def pinned_support_shown_by_print_command(context):
    context.conapp.writeline("print")
    context.test.assertIn("PinnedSupport", context.conapp.readline())

@when("then adds a beam")
def add_beam(context):
    context.conapp.writeline("add Beam")

@then("she will see a pinned support and a beam on print command")
def pinned_support_and_beam_shown_by_print_command(context):
    context.conapp.writeline("print")
    truss = context.conapp.readline()
    context.test.assertIn("PinnedSupport", truss)
    context.test.assertIn("Beam", truss)

@when("Betty misstypes and tries to add a Ream")
def attempt_to_add_misstyped_item(context):
    context.conapp.writeline("add Ream")

@then("she will see nothing on print command")
def nothing_shown_by_print_command(context):
    context.test.assertTrue(is_truss_empty(context))

@when("then deletes pinned support")
def delete_pinned_support(context):
    context.conapp.writeline("del PinnedSupport")

@given("some elements added to new truss")
def add_some_elements_to_new_truss(context):
    create_new_truss(context)
    add_pinned_support(context)
    add_beam(context)

@when("Betty saves truss to file '{filename}'")
def save_to_file(context, filename):
    context.conapp.writeline(f"save {filename}")
    context.conapp.writeline("print")
    context.truss = context.conapp.readline()

@then("she can load exactly the same truss from file '{filename}'")
def load_from_file(context, filename):
    context.conapp.writeline(f"load {filename}")
    context.conapp.writeline("print")
    context.test.assertTrue(context.truss == context.conapp.readline())

@when("Betty loads truss from examples")
def load_truss_from_examples(context):
    raise NotImplementedError("STEP: When Betty loads truss from examples")

@then("autocalculated results are the same as she caclucated manually")
def calculate_truss(context):
    raise NotImplementedError("STEP: Then autocalculated results are the same as she caclucated manually")

def is_truss_empty(context):
    context.conapp.writeline("print")
    truss = context.conapp.readline()
    return truss == "[]"
