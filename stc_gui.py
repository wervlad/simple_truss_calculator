#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
from cmath import exp
from math import radians
from re import sub
from tkinter import (Button, Canvas, Entry, Frame, Label, OptionMenu, PhotoImage,
                     StringVar, Tk, BOTH, FLAT, LAST, LEFT, RAISED, TOP, E, N,
                     S, W, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from truss_builder import add_item, remove_item, create_new_truss, load_from, save_as
import truss_calculator as calc

# global constants
FORCE_LENGTH = 50
X_OFFSET = FORCE_LENGTH + 10
Y_OFFSET = FORCE_LENGTH + 10
LABEL_COLOR = "darkred"
BACKGROUND_COLOR = "white"
LINE_COLOR = "black"
ACTIVE_LINE_COLOR = "green"
JOINTS = ("PinJoint", "PinnedSupport", "RollerSupport")

# global variables
truss = create_new_truss()
root = Tk()
truss_view = Canvas(root, bg=BACKGROUND_COLOR)
left_panel = Frame(root)

def main():
    root.title("Simple Truss Calculator")
    left_panel.pack(side=LEFT, fill=Y)
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = ["new", "load", "save", "labels", "refresh", "calculate",
               "pinnedSupport", "rollerSupport", "pinJoint", "beam", "force"]
    images = {}
    for b in buttons:
        images[b] = PhotoImage(file=f"img/{b}.gif")  # store in memory
        Button(toolbar,
               image=images[b],
               relief=FLAT,
               command=globals()[camel_to_snake(b)]
               ).pack(side=LEFT, padx=2, pady=2)
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
    try:
        results = calc.calculate(truss)
    except ValueError as e:
        showerror("Calculate", e)
        return
    clear_left_pane()
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    Label(left_panel, text="Force").grid(column=0, row=0, **options)
    Label(left_panel, text="Value").grid(column=1, row=0, **options)
    for row, (l, v) in enumerate(results.items(), 1):
        Label(left_panel, text=l).grid(column=0, row=row, **options)
        Label(left_panel, text=f"{v:>.4f}").grid(column=1, row=row, **options)
    Button(left_panel, text="Hide", command=clear_left_pane).grid(columnspan=2,
                                                                  **options)
    refresh()
    labels()

def fill_left_pane(widgets):
    def add_widget(w):
        w.grid(column=column, row=row, columnspan=columnspan, **options)

    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    col_count = 2
    cell = 0
    clear_left_pane()
    for w in widgets:
        row, column = divmod(cell, col_count)
        columnspan = w.get("columnspan", 1)
        if w["type"] == "Label":
            add_widget(Label(left_panel, text=w["text"]))
        elif w["type"] == "Entry":
            add_widget(Entry(left_panel, textvariable=w["var"]))
        elif w["type"] == "OptionMenu":
            add_widget(OptionMenu(left_panel, w["var"], *w["nodes"]))
        elif w["type"] == "Button":
            add_widget(Button(left_panel, text=w["text"], command=w["command"]))
        cell += columnspan
    refresh()

def beam(**b):
    def add_beam():
        global truss
        item = dict(end1=end1.get(), end2=end2.get(),
                    type="Beam", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()

    def edit_beam():
        global truss
        truss = remove_item(truss, b)
        add_beam()

    def delete_beam():
        global truss
        truss = remove_item(truss, b)
        clear_left_pane()

    nodes = [n["id"] for n in filter(lambda x: x["type"] in JOINTS, truss)]
    if not nodes:
        nodes.append("")
    end1 = StringVar()
    end2 = StringVar()
    item_id = StringVar()
    widgets = [{"type": "Label", "text": "Add new beam", "columnspan": 2},
               {"type": "Label", "text": "ID"},
               {"type": "Entry", "var": item_id},
               {"type": "Label", "text": "End 1"},
               {"type": "OptionMenu", "var": end1, "nodes": nodes},
               {"type": "Label", "text": "End 2"},
               {"type": "OptionMenu", "var": end2, "nodes": nodes},
               {"type": "Button", "text": "Add", "command": add_beam},
               {"type": "Button", "text": "Cancel", "command": clear_left_pane}
               ]
    if b:
        end1.set(b["end1"])
        end2.set(b["end2"])
        item_id.set(b["id"])
        widgets[0] = {"type": "Label", "text": f"Edit beam {item_id.get()}",
                      "columnspan": 2}
        widgets[7] = {"type": "Button", "text": "Edit", "command": edit_beam}
        widgets.append({"type": "Button", "text": "Delete",
                        "command": delete_beam, "columnspan": 2})
    fill_left_pane(widgets)

def pinned_support(**ps):
    def add_pinned_support():
        global truss
        item = dict(x=float(x.get()), y=float(y.get()),
                    type="PinnedSupport", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()

    def edit_pinned_support():
        global truss
        truss = remove_item(truss, ps)
        add_pinned_support()

    def delete_pinned_support():
        global truss
        truss = remove_item(truss, ps)
        clear_left_pane()

    clear_left_pane()
    x = StringVar()
    y = StringVar()
    item_id = StringVar()
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    if ps:
        item_id.set(ps["id"])
        x.set(ps["x"])
        y.set(ps["y"])
        Label(left_panel, text=f"Edit pinned support {item_id.get()}").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Edit", command=edit_pinned_support).grid(column=0, row=4, **options)
        Button(left_panel, text="Delete", command=delete_pinned_support).grid(row=5, columnspan=2, **options)
    else:
        Label(left_panel, text="Add new pinned support").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Add", command=add_pinned_support).grid(column=0, row=4, **options)
        item_id.set(get_new_id(truss))
        x.set(0)
        y.set(0)
    Label(left_panel, text="ID").grid(column=0, row=1, **options)
    Entry(left_panel, textvariable=item_id).grid(column=1, row=1, **options)
    Label(left_panel, text="X").grid(column=0, row=2, **options)
    Entry(left_panel, textvariable=x).grid(column=1, row=2, **options)
    Label(left_panel, text="Y").grid(column=0, row=3, **options)
    Entry(left_panel, textvariable=y).grid(column=1, row=3, **options)
    Button(left_panel, text="Cancel", command=clear_left_pane).grid(column=1, row=4, **options)
    refresh()

def roller_support(**rs):
    def add_roller_support():
        global truss
        item = dict(id=item_id.get(), x=float(x.get()), y=float(y.get()),
                    angle=float(angle.get()), type="RollerSupport")
        truss = add_item(truss, item)
        clear_left_pane()

    def edit_roller_support():
        global truss
        truss = remove_item(truss, rs)
        add_roller_support()

    def delete_roller_support():
        global truss
        truss = remove_item(truss, rs)
        clear_left_pane()

    clear_left_pane()
    item_id = StringVar()
    x = StringVar()
    y = StringVar()
    angle = StringVar()
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    if rs:
        item_id.set(rs["id"])
        x.set(rs["x"])
        y.set(rs["y"])
        angle.set(rs["angle"])
        Label(left_panel, text=f"Edit roller support {item_id.get()}").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Edit", command=edit_roller_support).grid(column=0, row=5, **options)
        Button(left_panel, text="Delete", command=delete_roller_support).grid(row=6, columnspan=2, **options)
    else:
        Label(left_panel, text="Add new roller support").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Add", command=add_roller_support).grid(column=0, row=5, **options)
        item_id.set(get_new_id(truss))
        x.set(0)
        y.set(0)
        angle.set(0)
    Label(left_panel, text="ID").grid(column=0, row=1, **options)
    Entry(left_panel, textvariable=item_id).grid(column=1, row=1, **options)
    Label(left_panel, text="X").grid(column=0, row=2, **options)
    Entry(left_panel, textvariable=x).grid(column=1, row=2, **options)
    Label(left_panel, text="Y").grid(column=0, row=3, **options)
    Entry(left_panel, textvariable=y).grid(column=1, row=3, **options)
    Label(left_panel, text="Angle").grid(column=0, row=4, **options)
    Entry(left_panel, textvariable=angle).grid(column=1, row=4, **options)
    Button(left_panel, text="Cancel", command=clear_left_pane).grid(column=1, row=5, **options)
    refresh()

def pin_joint(**pj):
    def add_pin_joint():
        global truss
        item = dict(x=float(x.get()), y=float(y.get()),
                    type="PinJoint", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()

    def edit_pin_joint():
        global truss
        truss = remove_item(truss, pj)
        add_pin_joint()

    def delete_pin_joint():
        global truss
        truss = remove_item(truss, pj)
        clear_left_pane()

    clear_left_pane()
    x = StringVar()
    y = StringVar()
    item_id = StringVar()
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    if pj:
        item_id.set(pj["id"])
        x.set(pj["x"])
        y.set(pj["y"])
        Label(left_panel, text=f"Edit pin joint {item_id.get()}").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Edit", command=edit_pin_joint).grid(column=0, row=4, **options)
        Button(left_panel, text="Delete", command=delete_pin_joint).grid(row=5, columnspan=2, **options)
    else:
        Label(left_panel, text="Add new pin joint").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Add", command=add_pin_joint).grid(column=0, row=4, **options)
        item_id.set(get_new_id(truss))
        x.set(0)
        y.set(0)
    Label(left_panel, text="ID").grid(column=0, row=1, **options)
    Entry(left_panel, textvariable=item_id).grid(column=1, row=1, **options)
    Label(left_panel, text="X").grid(column=0, row=2, **options)
    Entry(left_panel, textvariable=x).grid(column=1, row=2, **options)
    Label(left_panel, text="Y").grid(column=0, row=3, **options)
    Entry(left_panel, textvariable=y).grid(column=1, row=3, **options)
    Button(left_panel, text="Cancel", command=clear_left_pane).grid(column=1, row=4, **options)
    refresh()

def force(**f):
    def add_force():
        global truss
        item = dict(applied_to=applied_to.get(), value=float(value.get()),
                    angle=float(angle.get()), type="Force", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()

    def edit_force():
        global truss
        truss = remove_item(truss, f)
        add_force()

    def delete_force():
        global truss
        truss = remove_item(truss, f)
        clear_left_pane()

    clear_left_pane()
    nodes = [n["id"] for n in filter(lambda x: x["type"] in JOINTS, truss)]
    if not nodes:
        nodes.append("")
    item_id = StringVar()
    applied_to = StringVar()
    value = StringVar()
    angle = StringVar()
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    if f:
        applied_to.set(f["applied_to"])
        value.set(f["value"])
        angle.set(f["angle"])
        item_id.set(f["id"])
        Label(left_panel, text=f"Edit force {item_id.get()}").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Edit", command=edit_force).grid(column=0, row=5, **options)
        Button(left_panel, text="Delete", command=delete_force).grid(row=6, columnspan=2, **options)
    else:
        item_id.set(get_new_id(truss))
        value.set(0)
        angle.set(0)
        Label(left_panel, text="Add new force").grid(row=0, columnspan=2, **options)
        Button(left_panel, text="Add", command=add_force).grid(column=0, row=5, **options)
    Label(left_panel, text="ID").grid(column=0, row=1, **options)
    Entry(left_panel, textvariable=item_id).grid(column=1, row=1, **options)
    Label(left_panel, text="Applied to").grid(column=0, row=2, **options)
    OptionMenu(left_panel, applied_to, *nodes).grid(column=1, row=2, **options)
    Label(left_panel, text="Value").grid(column=0, row=3, **options)
    Entry(left_panel, textvariable=value).grid(column=1, row=3, **options)
    Label(left_panel, text="Angle").grid(column=0, row=4, **options)
    Entry(left_panel, textvariable=angle).grid(column=1, row=4, **options)
    Button(left_panel, text="Cancel", command=clear_left_pane).grid(column=1, row=5, **options)
    refresh()

def clear_left_pane():
    for child in left_panel.winfo_children():
        child.destroy()
    Frame(left_panel).grid()  # hide left panel
    refresh()

def create_item(item, scale):
    globals()[f"create_{camel_to_snake(item['type'])}"](item, scale)

def camel_to_snake(s):
    return sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()

def get_optimal_scale():
    width, height = get_truss_size(truss)
    truss_view.update()
    view_width = truss_view.winfo_width() - 2 * X_OFFSET
    view_height = truss_view.winfo_height() - 2 * Y_OFFSET
    x_scale = view_width / width if width else view_width
    y_scale = view_height / height if height else view_height
    return min(x_scale, y_scale)

def get_truss_size(truss):
    xs = tuple(filter(None.__ne__, (item.get("x") for item in truss)))
    ys = tuple(filter(None.__ne__, (item.get("y") for item in truss)))
    return (max(xs, default=0) - min(xs, default=0),
            max(ys, default=0) - min(ys, default=0))

def get_item(truss, item_id):
    return list(filter(lambda x: item_id == x["id"], truss))[0]

def get_new_id(truss):
    return "test"

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
    truss_view.tag_bind(pj["id"], '<Button-1>', lambda _: pin_joint(**pj))

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
    truss_view.tag_bind(ps["id"], '<Button-1>', lambda _: pinned_support(**ps))

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
    truss_view.tag_bind(rs["id"], '<Button-1>', lambda _: roller_support(**rs))

def rotate(center, target, angle):
    ccenter = complex(*center)
    ctarget = complex(*target)
    cangle = exp(radians(angle) * 1j)
    ret = (ctarget - ccenter) * cangle + ccenter
    return ret.real, ret.imag

def create_beam(b, scale):
    pj1 = get_item(truss, b["end1"])
    pj2 = get_item(truss, b["end2"])
    end1 = to_canvas_pos(pj1["x"], pj1["y"], scale)
    end2 = to_canvas_pos(pj2["x"], pj2["y"], scale)
    truss_view.create_line(*end1, *end2, activefill=ACTIVE_LINE_COLOR,
                           width=2, fill=LINE_COLOR, tags=("Beam", b["id"]))
    truss_view.tag_bind(b["id"], '<Button-1>', lambda _: beam(**b))

def create_force(f, scale):
    joint = get_item(truss, f["applied_to"])
    x2, y2 = to_canvas_pos(joint["x"], joint["y"], scale)
    x1, y1 = rotate((x2, y2), (x2 + FORCE_LENGTH, y2), f["angle"])
    truss_view.create_line(x1, y1, x2, y2, fill="red", width=2, arrow=LAST,
                           activefill=ACTIVE_LINE_COLOR,
                           tags=("Force", f["id"]))
    truss_view.tag_bind(f["id"], '<Button-1>', lambda _: force(**f))

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
