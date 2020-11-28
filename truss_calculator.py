#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from sys import stdin
import json


VALID_ITEMS = [
    "Beam",
    "PinnedSupport",
]

truss = []
while True:
    print("> ", end="", flush=True)
    cmd = stdin.readline().strip()
    if cmd == "print":
        print(truss, flush=True)
    elif cmd.startswith("add"):
        item = cmd[4:]
        if item in VALID_ITEMS:
            truss.append(item)
    elif cmd.startswith("del"):
        item = cmd[4:]
        truss.remove(item)
    elif cmd == "new":
        truss = []
    elif cmd.startswith("save"):
        filename = cmd[5:]
        with open(filename, "w") as f:
            f.write(json.dumps(truss))
    elif cmd.startswith("load"):
        filename = cmd[5:]
        with open(filename, "r") as f:
            truss = json.load(f)
    else:
        raise NotImplementedError(cmd)
