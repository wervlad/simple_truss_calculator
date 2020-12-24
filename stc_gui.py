#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
from cmath import exp
from math import radians
from re import sub
from tkinter import (Button, Canvas, Frame, Label, PhotoImage, Tk,
                     BOTH, FLAT, LAST, LEFT, RAISED, TOP, E, N, S, W, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from truss_builder import create_new_truss, load_from, save_as
import truss_calculator as calc

# global constants
FORCE_LENGTH = 50
X_OFFSET = FORCE_LENGTH + 10
Y_OFFSET = FORCE_LENGTH + 10
LABEL_COLOR = "darkred"
BACKGROUND_COLOR = "white"
LINE_COLOR = "black"
ACTIVE_LINE_COLOR = "green"

# global variables
truss = create_new_truss()
root = Tk()
truss_view = Canvas(root, bg=BACKGROUND_COLOR)
left_panel = Frame(root)

def main():
    root.title("Simple Truss Calculator")
    left_panel.pack(side=LEFT, fill=Y)
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = ["new", "load", "save", "labels", "refresh", "calculate"]
    images = {}
    for b in buttons:
        images[b] = PhotoImage(file=f"img/{b}.gif")  # store in memory
        Button(toolbar,
               image=images[b],
               relief=FLAT,
               command=globals()[b]).pack(side=LEFT, padx=2, pady=2)
    toolbar.pack(side=TOP, fill=X)
    truss_view.pack(expand=YES, fill=BOTH)
    refresh()
    root.mainloop()

def refresh():
    truss_view.delete("all")
    scale = get_optimal_scale()
    for item in truss:
        create_item(item, scale)
    for item_type in ("Force", "PinJoint", "PinnedSupport", "RollerSupport"):
        truss_view.tag_raise(item_type)

def calculate():
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    Label(left_panel, text="Force").grid(column=0, row=0, **options)
    Label(left_panel, text="Value").grid(column=1, row=0, **options)
    results = calc.calculate(truss)
    for row, (l, v) in enumerate(results.items(), 1):
        Label(left_panel, text=l).grid(column=0, row=row, **options)
        Label(left_panel, text=f"{v:>.4f}").grid(column=1, row=row, **options)
    Button(left_panel, text="Hide", command=clear_left_pane).grid(columnspan=2,
                                                                  **options)
    refresh()
    labels()

def clear_left_pane():
    for child in left_panel.winfo_children():
        child.destroy()
    Frame(left_panel).grid()  # hide left panel
    refresh()  # notify observers

def create_item(item, scale):
    globals()[f"create_{camel_to_snake(item['type'])}"](item, scale)

def camel_to_snake(s):
    return sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()

def get_optimal_scale():
    width, height = get_truss_size(truss)
    truss_view.update()
    try:
        x_scale = (truss_view.winfo_width() - 2 * X_OFFSET) / width
        y_scale = (truss_view.winfo_height() - 2 * Y_OFFSET) / height
        return min(x_scale, y_scale)
    except ZeroDivisionError:
        return 1

def get_truss_size(truss):
    xs = tuple(filter(None.__ne__, (item.get("x") for item in truss)))
    ys = tuple(filter(None.__ne__, (item.get("y") for item in truss)))
    return (max(xs, default=0) - min(xs, default=0),
            max(ys, default=0) - min(ys, default=0))

def get_item(truss, item_id):
    return list(filter(lambda x: item_id == x["id"], truss))[0]

def to_canvas_pos(x, y, scale):
    canvas_x = x * scale + X_OFFSET
    canvas_y = int(truss_view.winfo_height()) - Y_OFFSET - y * scale
    return canvas_x, canvas_y

def create_circle(x, y, radius, activefill, tags):
    truss_view.create_oval(x - radius, y - radius, x + radius, y + radius,
                           width=2, outline=LINE_COLOR, fill=BACKGROUND_COLOR,
                           activefill=activefill, tags=tags)

def create_pin_joint(pj, scale):
    x, y = to_canvas_pos(pj["x"], pj["y"], scale)
    create_circle(x, y, 4, ACTIVE_LINE_COLOR, ("PinJoint", pj["id"]))

def create_triangle(x, y, angle, tags):
    point2 = rotate((x, y), (x - 30, y + 10), angle)
    point3 = rotate((x, y), (x - 30, y - 10), angle)
    truss_view.create_polygon(x, y, *point2, *point3, x, y, width=2,
                              fill=BACKGROUND_COLOR, outline=LINE_COLOR,
                              tags=tags)

def create_ground(x, y, distance, angle, tags):
    ground_point1 = rotate((x, y), (x - distance, y - 15), angle)
    ground_point2 = rotate((x, y), (x - distance, y + 15), angle)
    hatching_point1 = rotate((x, y), (x - distance - 5, y - 15), angle)
    hatching_point2 = rotate((x, y), (x - distance - 5, y + 15), angle)

    truss_view.create_line(*ground_point1, *ground_point2, width=2, tags=tags)
    truss_view.create_line(*hatching_point1, *hatching_point2, width=10,
                           dash=(2, 2), tags=tags)

def create_pinned_support(ps, scale):
    tags = "PinnedSupport", ps["id"]
    x, y = to_canvas_pos(ps["x"], ps["y"], scale)

    create_triangle(x, y, angle=-90, tags=tags)
    create_ground(x, y, distance=30, angle=-90, tags=tags)
    create_circle(x, y, 4, activefill=ACTIVE_LINE_COLOR, tags=tags)

def create_roller_support(rs, scale):
    tags = "RollerSupport", rs["id"]
    x, y = to_canvas_pos(rs["x"], rs["y"], scale)
    angle = -rs["angle"]
    radius = 4
    wheel1_pos = rotate((x, y), (x - radius - 30, y + radius - 10), angle)
    wheel2_pos = rotate((x, y), (x - radius - 30, y - radius + 10), angle)

    create_triangle(x, y, angle, tags=tags)
    create_ground(x, y, distance=(30 + 2 * radius), angle=angle, tags=tags)
    create_circle(*wheel1_pos, 4, activefill=None, tags=tags)
    create_circle(*wheel2_pos, 4, activefill=None, tags=tags)
    create_circle(x, y, 4, activefill=ACTIVE_LINE_COLOR, tags=tags)

def rotate(center, target, angle):
    ccenter = complex(*center)
    ctarget = complex(*target)
    cangle = exp(radians(angle) * 1j)
    ret = (ctarget - ccenter) * cangle + ccenter
    return ret.real, ret.imag

def create_beam(beam, scale):
    pj1 = get_item(truss, beam["end1"])
    pj2 = get_item(truss, beam["end2"])
    end1 = to_canvas_pos(pj1["x"], pj1["y"], scale)
    end2 = to_canvas_pos(pj2["x"], pj2["y"], scale)
    truss_view.create_line(*end1, *end2, activefill=ACTIVE_LINE_COLOR,
                           width=2, fill=LINE_COLOR, tags=("Beam", beam["id"]))

def create_force(force, scale):
    joint = get_item(truss, force["applied_to"])
    x2, y2 = to_canvas_pos(joint["x"], joint["y"], scale)
    x1, y1 = rotate((x2, y2), (x2 + FORCE_LENGTH, y2), force["angle"])
    truss_view.create_line(x1, y1, x2, y2, fill="red", width=2, arrow=LAST,
                           activefill=ACTIVE_LINE_COLOR,
                           tags=("Force", force["id"]))

def labels():
    scale = get_optimal_scale()
    for item in truss:
        create_label(item, scale)

def create_label(item, scale):
    x = y = 0
    if item["type"] == "Beam":
        end1 = get_item(truss, item["end1"])
        end2 = get_item(truss, item["end2"])
        x, y = to_canvas_pos((end1["x"] + end2["x"]) / 2,
                             (end1["y"] + end2["y"]) / 2, scale)
    if item["type"] == "Force":
        joint = get_item(truss, item["applied_to"])
        x, y = to_canvas_pos(joint["x"], joint["y"], scale)
        x, y = rotate((x, y), (x + FORCE_LENGTH / 2, y), item["angle"])
    if item["type"] in ("PinnedSupport", "RollerSupport"):
        x, y = to_canvas_pos(item["x"], item["y"], scale)
    if item["type"] == "PinJoint":
        return
    t = truss_view.create_text(x, y, fill=LABEL_COLOR, font="Arial 10",
                               text=item["id"], tags="Label")
    b = truss_view.create_rectangle(truss_view.bbox(t), fill=BACKGROUND_COLOR,
                                    outline=BACKGROUND_COLOR, tags="Label")
    truss_view.tag_lower(b, t)

def new():
    global truss
    truss = create_new_truss()
    refresh()

def load():
    options = {"defaultextension": ".json",
               "filetypes": [("Truss Data", ".json")],
               "initialdir": os.path.dirname(os.path.abspath(__file__)),
               "title": "Load Truss"}
    filename = askopenfilename(**options)
    if filename:
        try:
            global truss
            truss = load_from(filename)
            refresh()
        except IOError as error:
            showerror("Failed to load data", error)

def save():
    options = {"defaultextension": ".json",
               "filetypes": [("Truss Data", ".json")],
               "initialdir": os.path.dirname(os.path.abspath(__file__)),
               "title": "Save Truss"}
    filename = asksaveasfilename(**options)
    if filename:
        try:
            save_as(truss, filename)
        except IOError as error:
            showerror("Failed to save data", error)

if __name__ == "__main__":
    main()
