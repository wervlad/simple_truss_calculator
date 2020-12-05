#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from sys import stdin
import json
import truss_builder


VALID_ITEMS = [
    "Beam",
    "PinnedSupport",
]

truss = truss_builder.create_new_truss()
while True:
    print("> ", end="", flush=True)
    cmd = stdin.readline().strip()
    if cmd == "print":
        print(truss, flush=True)
    elif cmd.startswith("add"):
        item = cmd[4:]
        if item in VALID_ITEMS:
            truss = truss_builder.add_item(truss, item)
    elif cmd.startswith("del"):
        item = cmd[4:]
        truss = truss_builder.remove_item(truss, item)
    elif cmd == "new":
        truss = truss_builder.create_new_truss()
    elif cmd.startswith("save"):
        filename = cmd[5:]
        truss_builder.save_as(truss, filename)
    elif cmd.startswith("load"):
        filename = cmd[5:]
        truss = truss_builder.load_from(filename)
    else:
        raise NotImplementedError(cmd)
