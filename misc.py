#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from re import sub


def camel_to_snake(s):
    return sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()
