#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@given("new truss created")
def create_new_truss(context):
    context.truss = context.truss_builder.create_new_truss()
    turss_is_empty(context)

@when("Betty adds pinned support")
def add_pinned_support(context):
    context.truss = context.truss_builder.add_item(context.truss, "PinnedSupport")

@then("she will see a pinned support in the truss")
def pinned_support_is_in_the_truss(context):
    context.test.assertIn("PinnedSupport", context.truss)

@when("then adds a beam")
def add_beam(context):
    context.truss = context.truss_builder.add_item(context.truss, "Beam")

@then("she will see a pinned support and a beam in the truss")
def pinned_support_and_beam_is_in_the_truss(context):
    context.test.assertIn("PinnedSupport", context.truss)
    context.test.assertIn("Beam", context.truss)

@when("then deletes pinned support")
def delete_pinned_support(context):
    context.truss = context.truss_builder.remove_item(context.truss, "PinnedSupport")

@then("the truss is empty")
def turss_is_empty(context):
    context.test.assertTrue(not context.truss)

@given("some elements added to new truss")
def add_some_elements_to_new_truss(context):
    create_new_truss(context)
    add_pinned_support(context)
    add_beam(context)

@when("Betty saves truss to file '{filename}'")
def save_to_file(context, filename):
    context.truss_builder.save_as(context.truss, filename)

@then("she can load exactly the same truss from file '{filename}'")
def load_from_file(context, filename):
    context.test.assertEqual(context.truss_builder.load_from(filename),
                             context.truss)
