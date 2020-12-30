#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from cmath import exp
from math import radians
from tkinter import Canvas, LAST
from truss_builder import add_item, remove_item, create_new_truss, load_from, save_as
from misc import camel_to_snake

def rotate(center, target, angle):
    ccenter = complex(*center)
    ctarget = complex(*target)
    cangle = exp(radians(angle) * 1j)
    ret = (ctarget - ccenter) * cangle + ccenter
    return ret.real, ret.imag

def get_truss_size(truss):
    xs = tuple(filter(None.__ne__, (item.get("x") for item in truss)))
    ys = tuple(filter(None.__ne__, (item.get("y") for item in truss)))
    return (max(xs, default=0) - min(xs, default=0),
            max(ys, default=0) - min(ys, default=0))

def get_item(truss, item_id):
    return list(filter(lambda x: item_id == x["id"], truss))[0]

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

    def __init__(self, master):
        super().__init__(master, bg=self.BACKGROUND_COLOR)
        master.bind("<Delete>", self.delete_selected)
        self.__truss = create_new_truss()
        self.__scale = self.get_optimal_scale()
        self.__selected = None
        self.refresh()
        self.observer_callbacks = []

    @property
    def truss(self):
        return self.__truss

    @truss.setter
    def truss(self, t):
        self.__truss = t
        self.__scale = self.get_optimal_scale()
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
        self.__scale = self.get_optimal_scale()
        for i in self.truss:
            self.create_item(i)
        for i in ("Force", "PinJoint", "PinnedSupport", "RollerSupport"):
            self.tag_raise(i)

    def append_observer_callback(self, callback):
        self.observer_callbacks.append(callback)

    def remove_observer_callback(self, callback):
        self.observer_callbacks.remove(callback)

    def get_optimal_scale(self):
        width, height = get_truss_size(self.truss)
        self.update()
        view_width = self.winfo_width() - 2 * self.X_OFFSET
        view_height = self.winfo_height() - 2 * self.Y_OFFSET
        x_scale = view_width / width if width else view_width
        y_scale = view_height / height if height else view_height
        return min(x_scale, y_scale)

    def create_item(self, item):
        if item == self.selected:
            color = self.HIGHLIGHT_COLOR
            activefill = None
        else:
            if item["type"] == "Force":
                color = self.FORCE_COLOR
            else:
                color = self.LINE_COLOR
            activefill = self.ACTIVE_COLOR
        create = getattr(self, f"create_{camel_to_snake(item['type'])}")
        create(item, color, activefill)

    def create_circle(self, x, y, radius, color, activefill, tags):
        self.create_oval(x - radius, y - radius, x + radius, y + radius,
                         tags=tags, width=2, outline=color,
                         fill=self.BACKGROUND_COLOR, activefill=activefill)

    def create_pin_joint(self, pj, color, activefill):
        x, y = self.to_canvas_pos(pj["x"], pj["y"])
        self.create_circle(x, y, 4, color, activefill, ("PinJoint", pj["id"]))
        self.tag_bind(pj["id"], "<Button-1>", lambda _: self.item_click(pj))

    def notify(self, message):
        for callback in self.observer_callbacks:
            callback(message)

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
        self.tag_bind(ps["id"], "<Button-1>", lambda _: self.item_click(ps))

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
        self.tag_bind(rs["id"], "<Button-1>", lambda _: self.item_click(rs))

    def create_beam(self, b, color, activecolor):
        pj1 = get_item(self.truss, b["end1"])
        pj2 = get_item(self.truss, b["end2"])
        end1 = self.to_canvas_pos(pj1["x"], pj1["y"])
        end2 = self.to_canvas_pos(pj2["x"], pj2["y"])
        self.create_line(*end1, *end2, tags=("Beam", b["id"]), width=2,
                         fill=color, activefill=activecolor)
        self.tag_bind(b["id"], "<Button-1>", lambda _: self.item_click(b))

    def create_force(self, f, color, activecolor):
        joint = get_item(self.truss, f["applied_to"])
        x2, y2 = self.to_canvas_pos(joint["x"], joint["y"])
        x1, y1 = rotate((x2, y2), (x2 + self.FORCE_LENGTH, y2), f["angle"])

        self.create_line(x1, y1, x2, y2, tags=("Force", f["id"]), width=2,
                         arrow=LAST, fill=color, activefill=activecolor)
        self.tag_bind(f["id"], "<Button-1>", lambda _: self.item_click(f))

    def create_labels(self):
        for item in self.truss:
            self.create_label(item)

    def create_label(self, i):
        x = y = 0
        if i["type"] == "Beam":
            end1 = get_item(self.truss, i["end1"])
            end2 = get_item(self.truss, i["end2"])
            x, y = self.to_canvas_pos((end1["x"] + end2["x"]) / 2,
                                      (end1["y"] + end2["y"]) / 2)
        if i["type"] == "Force":
            joint = get_item(self.truss, i["applied_to"])
            x, y = self.to_canvas_pos(joint["x"], joint["y"])
            x, y = rotate((x, y), (x + self.FORCE_LENGTH / 2, y), i["angle"])
        if i["type"] in ("PinnedSupport", "RollerSupport"):
            x, y = self.to_canvas_pos(i["x"], i["y"])
        if i["type"] == "PinJoint":
            return
        t = self.create_text(x, y, text=i["id"], tags="Label", font="Arial 10",
                             fill=self.LABEL_COLOR)
        b = self.create_rectangle(self.bbox(t), fill=self.BACKGROUND_COLOR,
                                  outline=self.BACKGROUND_COLOR, tags="Label")
        self.tag_lower(b, t)

    def to_canvas_pos(self, x, y):
        canvas_x = x * self.__scale + self.X_OFFSET
        canvas_y = int(self.winfo_height()) - self.Y_OFFSET - y * self.__scale
        return canvas_x, canvas_y

    def item_click(self, item):
        self.selected = item
        self.notify(dict(action="edit", item=item))

    def delete_selected(self, _):
        self.notify(dict(action="delete", item=self.selected))
        self.__truss = remove_item(self.truss, self.selected)
        self.selected = None

    def add_item(self, i):
        self.truss = add_item(self.truss, i)
    
    def replace_item(self, old, new):
        self.truss = add_item(remove_item(self.truss, old), new)

    def new_truss(self):
        self.truss = create_new_truss()

    def load_from(self, filename):
        self.truss = load_from(filename)

    def save_as(self, filename):
        save_as(self.truss, filename)
