#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from tkinter import (Button, Entry, Frame, Label, OptionMenu, PhotoImage,
                     StringVar, Tk, BOTH, FLAT, LEFT, RAISED, TOP, E, N,
                     S, W, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from truss_builder import add_item, remove_item, create_new_truss, load_from, save_as
import truss_calculator as calc
from truss_view import TrussView
from misc import camel_to_snake

JOINTS = ("PinJoint", "PinnedSupport", "RollerSupport")

# global variables
truss = create_new_truss()
root = Tk()
truss_view = TrussView(root, truss)
left_panel = Frame(root)

def main():
    root.title("Simple Truss Calculator")
    truss_view.append_observer_callback(update)
    left_panel.pack(side=LEFT, fill=Y)
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = OrderedDict({"new": new,
                           "load": load,
                           "save": save,
                           "labels": truss_view.create_labels,
                           "refresh": truss_view.refresh,
                           "calculate": calculate,
                           "pinnedSupport": pinned_support,
                           "rollerSupport": roller_support,
                           "pinJoint": pin_joint,
                           "beam": beam,
                           "force": force})
    images = {}
    for b, f  in buttons.items():
        images[b] = PhotoImage(file=f"img/{b}.gif")  # store in memory
        Button(toolbar,
               image=images[b],
               relief=FLAT,
               command=f).pack(side=LEFT, padx=2, pady=2)
    toolbar.pack(side=TOP, fill=X)
    truss_view.pack(expand=YES, fill=BOTH)
    truss_view.refresh()
    root.mainloop()

def update(item):
    globals()[camel_to_snake(item["type"])](**item)

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
    truss_view.refresh()
    truss_view.create_labels()

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
    truss_view.refresh()

def beam(**b):
    def add_beam():
        global truss
        item = dict(end1=end1.get(), end2=end2.get(),
                    type="Beam", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()
        truss_view.truss = truss

    def edit_beam():
        global truss
        truss = remove_item(truss, b)
        add_beam()

    def delete_beam():
        global truss
        truss = remove_item(truss, b)
        clear_left_pane()
        truss_view.truss = truss

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
        truss_view.truss = truss

    def edit_pinned_support():
        global truss
        truss = remove_item(truss, ps)
        add_pinned_support()

    def delete_pinned_support():
        global truss
        truss = remove_item(truss, ps)
        clear_left_pane()
        truss_view.truss = truss

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
    truss_view.refresh()

def roller_support(**rs):
    def add_roller_support():
        global truss
        item = dict(id=item_id.get(), x=float(x.get()), y=float(y.get()),
                    angle=float(angle.get()), type="RollerSupport")
        truss = add_item(truss, item)
        clear_left_pane()
        truss_view.truss = truss

    def edit_roller_support():
        global truss
        truss = remove_item(truss, rs)
        add_roller_support()

    def delete_roller_support():
        global truss
        truss = remove_item(truss, rs)
        clear_left_pane()
        truss_view.truss = truss

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
    truss_view.refresh()

def pin_joint(**pj):
    def add_pin_joint():
        global truss
        item = dict(x=float(x.get()), y=float(y.get()),
                    type="PinJoint", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()
        truss_view.truss = truss

    def edit_pin_joint():
        global truss
        truss = remove_item(truss, pj)
        add_pin_joint()

    def delete_pin_joint():
        global truss
        truss = remove_item(truss, pj)
        clear_left_pane()
        truss_view.truss = truss

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
    truss_view.refresh()

def force(**f):
    def add_force():
        global truss
        item = dict(applied_to=applied_to.get(), value=float(value.get()),
                    angle=float(angle.get()), type="Force", id=item_id.get())
        truss = add_item(truss, item)
        clear_left_pane()
        truss_view.truss = truss

    def edit_force():
        global truss
        truss = remove_item(truss, f)
        add_force()

    def delete_force():
        global truss
        truss = remove_item(truss, f)
        clear_left_pane()
        truss_view.truss = truss

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
    truss_view.refresh()

def clear_left_pane():
    for child in left_panel.winfo_children():
        child.destroy()
    Frame(left_panel).grid()  # hide left panel
    truss_view.refresh()

def get_new_id(truss):
    return "test"

def new():
    global truss
    truss = create_new_truss()
    truss_view.truss = truss

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
            truss_view.truss = truss
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
