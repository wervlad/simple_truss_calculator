#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from sys import stdin

truss = []
while True:
    print("> ", end="", flush=True)
    cmd = stdin.readline().strip()
    if cmd == "print":
        print(truss, flush=True)
    elif cmd.startswith("add"):
        truss.append(cmd[4:])
    elif cmd == "new":
        truss = []
