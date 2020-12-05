#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import json

VALID_ITEMS = [
    "Beam",
    "PinnedSupport",
]

def create_new_truss():
    return ()

def add_item(truss, item):
    return truss + (item,)

def remove_item(truss, item):
    return tuple(x for x in truss if item != x)

def save_as(truss, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(truss))

def load_from(filename):
    with open(filename, "r") as f:
        return tuple(item for item in json.load(f))
