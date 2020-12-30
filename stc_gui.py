#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from tkinter import (Button, Entry, Frame, Label, OptionMenu, PhotoImage,
                     StringVar, Tk, BOTH, FLAT, LEFT, RAISED, TOP, E, N,
                     S, W, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
import truss_calculator as calc
from truss_view import TrussView
from misc import camel_to_snake


# global variables
root = Tk()
truss_view = TrussView(root)
left_panel = Frame(root)

def main():
    root.title("Simple Truss Calculator")
    truss_view.append_observer_callback(update)
    left_panel.pack(side=LEFT, fill=Y)
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = OrderedDict({"new": truss_view.new_truss,
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

def update(message):
    if message["action"] == "edit":
        item = message["item"]
        globals()[camel_to_snake(item["type"])](**item)
    elif message["action"] == "delete":
        clear_left_pane()

def calculate():
    try:
        results = calc.calculate(truss_view.truss)
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

def create_params_grid(params, ok, cancel):
    clear_left_pane()
    options = dict(padx=5, pady=5, sticky=W+E+N+S)
    variables = {}
    for i, p in enumerate(params):
        name = p["name"]
        Label(left_panel, text=name).grid(column=0, row=i, **options)
        variables[name] = StringVar(value=p["value"])
        if p.get("values") is None:
            if p.get("editable"):
                w = Entry(left_panel, textvariable=variables[name])
            else:
                w = Label(left_panel, text=p["value"])
        else:
            w = OptionMenu(left_panel, variables[name], *p["values"])
        w.grid(column=1, row=i, **options)
    i += 1
    Button(left_panel, text="OK", command=ok).grid(column=0, row=i, **options)
    Button(left_panel, text="Cancel", command=cancel
           ).grid(column=1, row=i, **options)
    truss_view.refresh()
    return variables

def add(item):
    clear_left_pane()
    truss_view.add_item(item)

def replace(old, new):
    clear_left_pane()
    truss_view.replace_item(old, new)

def beam(**b):
    def new_beam():
        return dict(end1=values["End 1"].get(), end2=values["End 2"].get(),
                    type="Beam", id=values["ID"].get())

    nodes = [n["id"] for n in get_joints(truss_view.truss)]
    if not nodes:
        nodes.append("")
    params = [{"name": "ID", "value": b.get("id"), "editable": False},
              {"name": "End 1", "value": b.get("end1"), "values": nodes},
              {"name": "End 2", "value": b.get("end2"), "values": nodes}]
    ok = (lambda: replace(b, new_beam())) if b else (lambda: add(new_beam()))
    values = create_params_grid(params, ok, clear_left_pane)

def pinned_support(**ps):
    def new_ps():
        return dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                    type="PinnedSupport", id=values["ID"].get())

    params = [{"name": "ID", "value": ps.get("id"), "editable": False},
              {"name": "X", "value": ps.get("x", 0), "editable": True},
              {"name": "Y", "value": ps.get("y", 0), "editable": True}]
    ok = (lambda: replace(ps, new_ps())) if ps else (lambda: add(new_ps()))
    values = create_params_grid(params, ok, clear_left_pane)

def roller_support(**rs):
    def new_rs():
        return dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                    angle=float(values["Angle"].get()), type="RollerSupport",
                    id=values["ID"].get())

    params = [{"name": "ID", "value": rs.get("id"), "editable": False},
              {"name": "X", "value": rs.get("x", 0), "editable": True},
              {"name": "Y", "value": rs.get("y", 0), "editable": True},
              {"name": "Angle", "value": rs.get("angle", 0), "editable": True}]
    ok = (lambda: replace(rs, new_rs())) if rs else (lambda: add(new_rs()))
    values = create_params_grid(params, ok, clear_left_pane)

def pin_joint(**pj):
    def new_pj():
        return dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                    type="PinJoint", id=values["ID"].get())

    params = [{"name": "ID", "value": pj.get("id"), "editable": False},
              {"name": "X", "value": pj.get("x", 0), "editable": True},
              {"name": "Y", "value": pj.get("y", 0), "editable": True}]
    ok = (lambda: replace(pj, new_pj())) if pj else (lambda: add(new_pj()))
    values = create_params_grid(params, ok, clear_left_pane)

def force(**f):
    def new_force():
        return dict(id=values["ID"].get(), value=float(values["Value"].get()),
                    applied_to=values["Applied to"].get(),
                    angle=float(values["Angle"].get()), type="Force")

    nodes = [n["id"] for n in get_joints(truss_view.truss)]
    if not nodes:
        nodes.append("")
    params = [
        {"name": "ID", "value": f.get("id"), "editable": False},
        {"name": "Applied to", "value": f.get("applied_to"), "values": nodes},
        {"name": "Value", "value": f.get("value", 0), "editable": True},
        {"name": "Angle", "value": f.get("angle", 0), "editable": True}]
    ok = (lambda: replace(f, new_force())) if f else (lambda: add(new_force()))
    values = create_params_grid(params, ok, clear_left_pane)


def clear_left_pane():
    for child in left_panel.winfo_children():
        child.destroy()
    Frame(left_panel).grid()  # hide left panel
    truss_view.refresh()

def get_new_id(truss):
    return "test"

def get_joints(truss):
    joints = ("PinJoint", "PinnedSupport", "RollerSupport")
    return tuple(filter(lambda x: x["type"] in joints, truss))

def load():
    options = {"defaultextension": ".json",
               "filetypes": [("Truss Data", ".json")],
               "initialdir": os.path.dirname(os.path.abspath(__file__)),
               "title": "Load Truss"}
    filename = askopenfilename(**options)
    if filename:
        try:
            truss_view.load_from(filename)
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
            truss_view.save_as(filename)
        except IOError as error:
            showerror("Failed to save data", error)

if __name__ == "__main__":
    main()
