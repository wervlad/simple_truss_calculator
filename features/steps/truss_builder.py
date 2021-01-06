#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
@given("new truss created")
def create_new_truss(context):
    context.truss.new()
    turss_is_empty(context)

@when("Betty adds pinned support")
def add_pinned_support(context):
    ps = {"id": "PS1", "type": "PinnedSupport", "x": 0.0, "y": 0.0}
    context.truss.append(ps)

@then("she will see a pinned support in the truss")
def pinned_support_is_in_the_truss(context):
    ps = {"id": "PS1", "type": "PinnedSupport", "x": 0.0, "y": 0.0}
    context.test.assertIn(ps, context.truss.items)

@when("then adds a roller support")
def add_beam(context):
    rs = {"id": "PS1", "type": "RollerSupport", "x": 5.0, "y": 0.0, "angle": 0}
    context.truss.append(rs)

@then("she will see a pinned support and a roller support in the truss")
def pinned_support_and_beam_is_in_the_truss(context):
    ps = {"id": "PS1", "type": "PinnedSupport", "x": 0.0, "y": 0.0}
    rs = {"id": "PS1", "type": "RollerSupport", "x": 5.0, "y": 0.0, "angle": 0}
    context.test.assertIn(ps, context.truss.items)
    context.test.assertIn(rs, context.truss.items)

@when("then deletes pinned support")
def delete_pinned_support(context):
    ps = {"id": "PS1", "type": "PinnedSupport", "x": 0.0, "y": 0.0}
    context.truss.remove(ps)

@then("the truss is empty")
def turss_is_empty(context):
    context.test.assertTrue(not context.truss.items)

@given("some elements added to new truss")
def add_some_elements_to_new_truss(context):
    create_new_truss(context)
    add_pinned_support(context)
    add_beam(context)

@when("Betty saves truss to file '{filename}'")
def save_to_file(context, filename):
    context.truss.save_as(filename)

@then("she can load exactly the same truss from file '{filename}'")
def load_from_file(context, filename):
    original = context.truss.items
    context.truss.load_from(filename)
    loaded = context.truss.items
    context.test.assertSequenceEqual(original, loaded)
