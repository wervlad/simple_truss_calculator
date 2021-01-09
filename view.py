#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from cmath import exp
from math import atan2, degrees, radians
from tkinter import Canvas, LAST
from misc import camel_to_snake
from domain import Truss


def rotate(center, target, angle):
    ccenter = complex(*center)
    ctarget = complex(*target)
    cangle = exp(radians(angle) * 1j)
    ret = (ctarget - ccenter) * cangle + ccenter
    return ret.real, ret.imag


class TrussView(Canvas):
    FORCE_LENGTH = 50
    X_OFFSET = FORCE_LENGTH + 10
    Y_OFFSET = FORCE_LENGTH + 10
    LABEL_COLOR = "darkred"
    BACKGROUND_COLOR = "white"
    HIGHLIGHT_COLOR = "lightgreen"
    LINE_COLOR = "black"
    FORCE_COLOR = "red"
    ACTIVE_COLOR = "green"

    def __init__(self, master, truss):
        super().__init__(master, bg=self.BACKGROUND_COLOR)
        self.bind('<Configure>', lambda _: self.refresh())
        self.__truss = truss
        self.__scale = self.__get_optimal_scale()
        self.__highlighted = None
        self.refresh()

    def update_truss(self, message):
        if message["action"] == "truss modified":
            self.highlighted = None
            self.refresh()

    @property
    def highlighted(self):
        return self.__highlighted

    @highlighted.setter
    def highlighted(self, item):
        self.__highlighted = item
        self.refresh()

    def refresh(self):
        self.delete("all")
        self.__scale = self.__get_optimal_scale()
        for i in self.__truss:
            self.create_item(i)
        self.highlight()
        for i in ("Force", "PinJoint", "PinnedSupport", "RollerSupport"):
            self.tag_raise(i)

    def __get_optimal_scale(self):
        width = self.__truss.width
        height = self.__truss.height
        self.update()
        view_width = self.winfo_width() - 2 * self.X_OFFSET
        view_height = self.winfo_height() - 2 * self.Y_OFFSET
        x_scale = view_width / width if width else view_width
        y_scale = view_height / height if height else view_height
        return min(x_scale, y_scale)

    def create_item(self, i):
        create = getattr(self, f"create_{camel_to_snake(i['type'])}")
        color = self.FORCE_COLOR if i["type"] == "Force" else self.LINE_COLOR
        create(i, color, self.ACTIVE_COLOR)

    def highlight(self):
        if self.highlighted:
            for i in self.find_withtag(self.highlighted["id"]):
                self.itemconfig(i, fill=self.HIGHLIGHT_COLOR, activefill="")

    def create_circle(self, x, y, radius, color, activefill, tags):
        self.create_oval(x - radius, y - radius, x + radius, y + radius,
                         tags=tags, width=2, outline=color,
                         fill=self.BACKGROUND_COLOR, activefill=activefill)

    def create_pin_joint(self, pj, color, activefill):
        x, y = self.to_canvas_pos(pj["x"], pj["y"])
        self.create_circle(x, y, 4, color, activefill, ("PinJoint", pj["id"]))

    def create_triangle(self, x, y, angle, color, tags):
        point2 = rotate((x, y), (x - 30, y + 10), angle)
        point3 = rotate((x, y), (x - 30, y - 10), angle)
        self.create_polygon(x, y, *point2, *point3, x, y, outline=color,
                            tags=tags, width=2, fill=self.BACKGROUND_COLOR)

    def create_ground(self, x, y, distance, angle, color, tags):
        ground_point1 = rotate((x, y), (x - distance, y - 15), angle)
        ground_point2 = rotate((x, y), (x - distance, y + 15), angle)
        hatching_point1 = rotate((x, y), (x - distance - 5, y - 15), angle)
        hatching_point2 = rotate((x, y), (x - distance - 5, y + 15), angle)

        self.create_line(*ground_point1, *ground_point2,
                         width=2, fill=color, tags=tags)
        self.create_line(*hatching_point1, *hatching_point2,
                         width=10, fill=color, dash=(2, 2), tags=tags)

    def create_pinned_support(self, ps, color, activecolor):
        tags = "PinnedSupport", ps["id"]
        x, y = self.to_canvas_pos(ps["x"], ps["y"])

        self.create_triangle(x, y, angle=-90, color=color, tags=tags)
        self.create_ground(x, y, 30, angle=-90, color=color, tags=tags)
        self.create_circle(x, y, 4, color, activefill=activecolor, tags=tags)

    def create_roller_support(self, rs, color, activecolor):
        tags = "RollerSupport", rs["id"]
        x, y = self.to_canvas_pos(rs["x"], rs["y"])
        angle = -rs["angle"]
        r = 4
        wheel1_pos = rotate((x, y), (x - r - 30, y + r - 10), angle)
        wheel2_pos = rotate((x, y), (x - r - 30, y - r + 10), angle)

        self.create_triangle(x, y, angle, color, tags=tags)
        self.create_ground(x, y, 30 + 2 * r, angle, color, tags)
        self.create_circle(*wheel1_pos, r, color, activefill=None, tags=tags)
        self.create_circle(*wheel2_pos, r, color, activefill=None, tags=tags)
        self.create_circle(x, y, r, color, activefill=activecolor, tags=tags)

    def create_beam(self, b, color, activecolor):
        end1 = self.to_canvas_pos(b["x1"], b["y1"])
        end2 = self.to_canvas_pos(b["x2"], b["y2"])
        self.create_line(*end1, *end2, tags=("Beam", b["id"]), width=2,
                         fill=color, activefill=activecolor)

    def create_force(self, f, color, activecolor):
        x2, y2 = self.to_canvas_pos(f["x"], f["y"])
        x1, y1 = rotate((x2, y2), (x2 + self.FORCE_LENGTH, y2), f["angle"])

        self.create_line(x1, y1, x2, y2, tags=("Force", f["id"]), width=2,
                         arrow=LAST, fill=color, activefill=activecolor)

    def create_labels(self):
        for item in self.__truss:
            if item["type"] != "PinJoint":
                self.create_label(item)

    def create_label(self, i):
        x = y = 0
        if i["type"] == "Beam":
            x, y = self.to_canvas_pos((i["x1"] + i["x2"]) / 2,
                                      (i["y1"] + i["y2"]) / 2)
        if i["type"] == "Force":
            x, y = self.to_canvas_pos(i["x"], i["y"])
            x, y = rotate((x, y), (x + self.FORCE_LENGTH / 2, y), i["angle"])
        if Truss.is_joint(i):
            x, y = self.to_canvas_pos(i["x"], i["y"])
        t = self.create_text(x, y, text=i["id"], tags="Label", font="Arial 10",
                             fill=self.LABEL_COLOR)
        b = self.create_rectangle(self.bbox(t), fill=self.BACKGROUND_COLOR,
                                  outline=self.BACKGROUND_COLOR, tags="Label")
        self.tag_lower(b, t)

    def to_canvas_pos(self, x, y):
        rx = x - self.__truss.left
        canvas_x = rx * self.__scale + self.X_OFFSET
        ry = y - self.__truss.bottom
        canvas_y = int(self.winfo_height()) - self.Y_OFFSET - ry * self.__scale
        return canvas_x, canvas_y

    def to_truss_pos(self, x, y):
        rx = (x - self.X_OFFSET) / self.__scale
        truss_x = rx + self.__truss.left
        ry = (int(self.winfo_height()) - self.Y_OFFSET - y) / self.__scale
        truss_y = ry + self.__truss.bottom
        return truss_x, truss_y


class TrussEditState:
    """This is FSM for truss editing GUI."""
    def __init__(self):
        self.__state = None
        self.__observer_callbacks = []
        self.set_state("default")

    def set_state(self, new_state):
        self.__state = getattr(self, f"process_{new_state}")()
        next(self.__state)

    def send(self, message):
        try:
            self.__state.send(message)
        except ValueError as e:
            if str(e) != "generator already executing":
                raise e

    def process_default(self):
        while True:
            m = yield
            if m["action"] == "item click":
                i = m["item"]
                self.__notify(dict(action="select", item=i))
            elif m["action"] == "click":
                self.__notify(dict(action="deselect"))
                i = None
            elif m["action"] == "delete":
                self.__notify(dict(action="delete", item=i))
                i = None

    def process_pj(self):
        while True:
            m = yield
            if m["action"] == "move":
                i = dict(x=m["x"], y=m["y"], type="PinJoint")
                self.__notify(dict(action="update tmp", item=i))
            elif m["action"] in ("click", "item click"):
                self.__notify(dict(action="create new", item=i))

    def process_ps(self):
        while True:
            m = yield
            if m["action"] == "move":
                i = dict(x=m["x"], y=m["y"], type="PinnedSupport")
                self.__notify(dict(action="update tmp", item=i))
            elif m["action"] in ("click", "item click"):
                self.__notify(dict(action="create new", item=i))

    def process_rs(self):
        # specify position
        while True:
            m = yield
            if m["action"] == "move":
                i = dict(x=m["x"], y=m["y"], type="RollerSupport", angle=90)
                self.__notify(dict(action="update tmp", item=i))
            elif m["action"] in ("click", "item click"):
                break
        # specify angle
        while True:
            m = yield
            if m["action"] == "move":
                i["angle"] = degrees(atan2(i["y"] - m["y"], i["x"] - m["x"]))
                self.__notify(dict(action="update tmp", item=i))
            elif m["action"] in ("click", "item click"):
                self.__notify(dict(action="create new", item=i))

    def process_beam(self):
        # specify 1st end
        while True:
            m = yield
            if m["action"] == "move":
                i = dict(x1=0, y1=0, x2=0, y2=0, type="Beam")
                self.__notify(dict(action="update tmp", item=i))
            if (m["action"] == "item click" and Truss.is_joint(m["item"])):
                j = m["item"]
                i = dict(end1=j["id"], x1=j["x"], y1=j["y"], type="Beam")
                break
        # specify 2nd end
        while True:
            m = yield
            if m["action"] == "move":
                i = {**i, "x2": m["x"], "y2": m["y"]}
                self.__notify(dict(action="update tmp", item=i))
            elif (m["action"] == "item click" and Truss.is_joint(m["item"])):
                i["end2"] = m["item"]["id"]
                self.__notify(dict(action="create new", item=i))

    def process_force(self):
        # specify application
        while True:
            m = yield
            if m["action"] == "move":
                i = dict(x=m["x"], y=m["y"], angle=-45, type="Force")
                self.__notify(dict(action="update tmp", item=i))
            if (m["action"] == "item click" and Truss.is_joint(m["item"])):
                j = m["item"]
                i = dict(applied_to=j["id"], x=j["x"], y=j["y"], type="Force")
                break
        # specify angle
        while True:
            m = yield
            if m["action"] == "move":
                i["angle"] = 180 - degrees(atan2(i["y"] - m["y"],
                                                 i["x"] - m["x"]))
                self.__notify(dict(action="update tmp", item=i))
            elif m["action"] in ("click", "item click"):
                self.__notify(dict(action="create force", item=i))

    def __notify(self, message):
        for callback in self.__observer_callbacks:
            callback(message)

    def append_observer_callback(self, callback):
        self.__observer_callbacks.append(callback)
