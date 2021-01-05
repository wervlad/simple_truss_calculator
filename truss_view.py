#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from cmath import exp
from math import radians
from tkinter import Canvas, LAST
from misc import camel_to_snake


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
        self.bind("<Button-1>", self.on_click)
        self.bind('<Configure>', lambda _: self.refresh())
        self.__truss = truss
        self.__scale = self.__get_optimal_scale()
        self.__selected = None
        self.refresh()
        self.__observer_callbacks = []

    def update_truss(self, t):
        self.__truss = t
        self.__scale = self.__get_optimal_scale()
        self.selected = None
        self.refresh()

    @property
    def selected(self):
        return self.__selected

    @selected.setter
    def selected(self, item):
        self.__selected = item
        self.refresh()

    def refresh(self):
        self.delete("all")
        self.__scale = self.__get_optimal_scale()
        for i in self.__truss.items:
            self.create_item(i)
        self.highlight_active()
        for i in ("Force", "PinJoint", "PinnedSupport", "RollerSupport"):
            self.tag_raise(i)

    def append_observer_callback(self, callback):
        self.__observer_callbacks.append(callback)

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

    def highlight_active(self):
        if self.selected:
            for i in self.find_withtag(self.selected["id"]):
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
        joint1 = self.__truss.find_by_id(b["end1"])
        joint2 = self.__truss.find_by_id(b["end2"])
        end1 = self.to_canvas_pos(joint1["x"], joint1["y"])
        end2 = self.to_canvas_pos(joint2["x"], joint2["y"])
        self.create_line(*end1, *end2, tags=("Beam", b["id"]), width=2,
                         fill=color, activefill=activecolor)

    def create_force(self, f, color, activecolor):
        joint = self.__truss.find_by_id(f["applied_to"])
        x2, y2 = self.to_canvas_pos(joint["x"], joint["y"])
        x1, y1 = rotate((x2, y2), (x2 + self.FORCE_LENGTH, y2), f["angle"])

        self.create_line(x1, y1, x2, y2, tags=("Force", f["id"]), width=2,
                         arrow=LAST, fill=color, activefill=activecolor)

    def create_labels(self):
        for item in self.__truss.items:
            if item["type"] != "PinJoint":
                self.create_label(item)

    def create_label(self, i):
        x = y = 0
        if i["type"] == "Beam":
            end1 = self.__truss.find_by_id(i["end1"])
            end2 = self.__truss.find_by_id(i["end2"])
            x, y = self.to_canvas_pos((end1["x"] + end2["x"]) / 2,
                                      (end1["y"] + end2["y"]) / 2)
        if i["type"] == "Force":
            joint = self.__truss.find_by_id(i["applied_to"])
            x, y = self.to_canvas_pos(joint["x"], joint["y"])
            x, y = rotate((x, y), (x + self.FORCE_LENGTH / 2, y), i["angle"])
        if i["type"] in self.__truss.JOINTS:
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

    def on_click(self, event):
        items_under_cursor = self.find_withtag("current")
        if items_under_cursor:
            i = self.__truss.find_by_id(self.gettags(items_under_cursor[0])[1])
            self.__notify(dict(action="item_click", item=i))
        else:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            self.__notify(dict(action="click", x=x, y=y))

    def __notify(self, message):
        for callback in self.__observer_callbacks:
            callback(message)
