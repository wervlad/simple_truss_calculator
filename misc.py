#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from cmath import exp
from math import radians
from re import sub


def camel_to_snake(s):
    return sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def rotate(center, target, angle):
    ccenter = complex(*center)
    ctarget = complex(*target)
    cangle = exp(radians(angle) * 1j)
    ret = (ctarget - ccenter) * cangle + ccenter
    return ret.real, ret.imag


class Observable:
    def __init__(self):
        self.observer_callbacks = []

    def notify(self, message):
        for callback in self.observer_callbacks:
            callback(message)

    def append_observer_callback(self, callback):
        self.observer_callbacks.append(callback)
