#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import json

class Truss:
    JOINTS = ("PinJoint", "PinnedSupport", "RollerSupport")

    def __init__(self):
        self.__items = ()
        self.__left = 0
        self.__right = 0
        self.__bottom = 0
        self.__top = 0
        self.__observer_callbacks = []

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, t):
        self.__items = t
        self.__update_dimensions()
        self.__notify(self)

    @property
    def left(self):
        return self.__left

    @property
    def right(self):
        return self.__right

    @property
    def bottom(self):
        return self.__bottom

    @property
    def top(self):
        return self.__top

    def append_observer_callback(self, callback):
        self.__observer_callbacks.append(callback)

    def new(self):
        self.items = ()

    def append(self, item):
        self.items = self.items + (item,)

    def remove(self, item):
        self.items = tuple(x for x in self.items if item != x)

    def replace(self, old, new):
        self.items = tuple(x for x in self.items if old != x) + (new,)

    def save_as(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(self.items))

    def load_from(self, filename):
        with open(filename, "r") as f:
            self.items = [item for item in json.load(f)]

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    def __update_dimensions(self):
        xs = tuple(filter(None.__ne__, (item.get("x") for item in self.items)))
        ys = tuple(filter(None.__ne__, (item.get("y") for item in self.items)))
        self.__left = min(xs, default=0)
        self.__right = max(xs, default=0)
        self.__bottom = min(ys, default=0)
        self.__top = max(ys, default=0)

    def find_by_id(self, item_id):
        items = tuple(filter(lambda x: item_id == x["id"], self.items))
        return items[0] if items else None

    @property
    def joints(self):
        return tuple(filter(lambda x: x["type"] in self.JOINTS, self.items))

    def __iter__(self):
        return iter(self.items)

    def __notify(self, message):
        for callback in self.__observer_callbacks:
            callback(message)
