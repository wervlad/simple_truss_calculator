#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from collections import OrderedDict
from math import atan2, degrees
from tkinter import (Button, Entry, Frame, Label, OptionMenu, PhotoImage,
                     StringVar, Tk, BOTH, FLAT, LEFT, RAISED, TOP, E, N,
                     S, W, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from tkinter.simpledialog import askfloat
from truss import Truss
from truss_view import TrussView
from misc import camel_to_snake


# global variables
root = Tk()
truss = Truss()
truss_view = TrussView(root, truss)
left_panel = Frame(root)
state = None

def main():
    root.title("Simple Truss Calculator")
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = OrderedDict({"new": truss.new,
                           "load": load,
                           "save": save,
                           "labels": truss_view.create_labels,
                           "refresh": truss_view.refresh,
                           "calculate": calculate,
                           "pinnedSupport": lambda: set_state("ps"),
                           "rollerSupport": lambda: set_state("rs"),
                           "pinJoint": lambda: set_state("pj"),
                           "beam": lambda: set_state("beam"),
                           "force": lambda: set_state("force")})
    images = {}
    for i, f in buttons.items():
        images[i] = PhotoImage(file=f"img/{i}.gif")  # prevent GC
        Button(toolbar, image=images[i], relief=FLAT, command=f
               ).pack(side=LEFT, padx=2, pady=2)
    toolbar.pack(side=TOP, fill=X)
    left_panel.pack(side=LEFT, fill=Y)
    truss_view.pack(expand=YES, fill=BOTH)
    root.bind("<Delete>", lambda _: state.send(dict(action="delete")))
    root.bind('<Escape>', lambda _: cancel())
    truss_view.bind("<Button-1>", on_click)
    truss_view.bind("<Motion>", on_mouse_move)
    set_state("default")
    truss.append_observer_callback(truss_view.update_truss)
    truss.append_observer_callback(truss_update)
    root.mainloop()

def on_click(_):
    items_under_cursor = truss_view.find_withtag("current")
    if items_under_cursor:
        i = truss.find_by_id(truss_view.gettags(items_under_cursor[0])[1])
        msg = dict(action="item click", item=i) if i else dict(action="click")
        state.send(msg)
    else:
        state.send(dict(action="click"))

def on_mouse_move(event):
    x, y = truss_view.to_truss_pos(event.x, event.y)
    try:
        state.send(dict(action="move", x=x, y=y))
    except ValueError as e:
        if str(e) != "generator already executing":
            raise e

def set_state(new_state):
    global state
    state = globals()[f"process_{new_state}"]()
    next(state)
    clear_left_panel()
    truss_view.highlighted = None

def truss_update(msg):
    if msg["action"] == "invalid items removed":
        invalid = ", ".join(f"{i['type']} {i['id']}" for i in msg["items"])
        showerror("Warning", f"Invalid items were removed: {invalid}")
    elif msg["action"] == "truss modified":
        clear_left_panel()

def process_default():
    while True:
        msg = yield
        if msg["action"] == "item click":
            truss_view.highlighted = i = msg["item"]
            globals()[camel_to_snake(i["type"])](**i)
        elif msg["action"] == "click":
            truss_view.highlighted = i = None
            clear_left_panel()
        elif msg["action"] == "delete":
            truss.remove(i)
            truss_view.highlighted = i = None

def process_pj():
    while True:
        msg = yield
        if msg["action"] == "move":
            i = dict(x=msg["x"], y=msg["y"], type="PinJoint")
            update_temporary_item(i)
        elif msg["action"] in ("click", "item click"):
            replace(None, i)

def process_ps():
    while True:
        msg = yield
        if msg["action"] == "move":
            i = dict(x=msg["x"], y=msg["y"], type="PinnedSupport")
            update_temporary_item(i)
        elif msg["action"] in ("click", "item click"):
            replace(None, i)

def process_rs():
    # specify position
    while True:
        msg = yield
        if msg["action"] == "move":
            i = dict(x=msg["x"], y=msg["y"], type="RollerSupport", angle=90)
            update_temporary_item(i)
        elif msg["action"] in ("click", "item click"):
            break
    # specify angle
    while True:
        msg = yield
        if msg["action"] == "move":
            i["angle"] = degrees(atan2(i["y"] - msg["y"], i["x"] - msg["x"]))
            update_temporary_item(i)
        elif msg["action"] in ("click", "item click"):
            replace(None, i)

def process_beam():
    # specify 1st end
    while True:
        m = yield
        beam(type="Beam")
        if m["action"] == "item click" and m["item"]["type"] in truss.JOINTS:
            j = m["item"]
            i = dict(end1=j["id"], x1=j["x"], y1=j["y"], type="Beam")
            break
    # specify 2nd end
    while True:
        m = yield
        if m["action"] == "move":
            i = {**i, "x2": m["x"], "y2": m["y"]}
            update_temporary_item(i)
            truss_view.tag_lower("temporary")
        elif m["action"] == "item click" and m["item"]["type"] in truss.JOINTS:
            i["end2"] = m["item"]["id"]
            replace(None, i)

def process_force():
    # specify application
    while True:
        m = yield
        force(type="Force")
        if m["action"] == "item click" and m["item"]["type"] in truss.JOINTS:
            j = m["item"]
            i = dict(applied_to=j["id"], x=j["x"], y=j["y"], type="Force")
            break
    # specify angle and value
    while True:
        m = yield
        if m["action"] == "move":
            i["angle"] = 180 - degrees(atan2(i["y"] - m["y"], i["x"] - m["x"]))
            update_temporary_item(i)
        elif m["action"] in ("click", "item click"):
            i["value"] = askfloat("Force value", "Please enter force value",
                                  initialvalue=0, parent=root)
            if i["value"]:
                replace(None, i)
            else:
                cancel()

def update_temporary_item(i):
    globals()[camel_to_snake(i["type"])](**i)
    truss_view.delete("temporary")
    truss_view.create_item({**i, "id": "temporary"})

def calculate():
    try:
        results = truss.calculate()
        params = [{"name": "Force", "value": "Value", "editable": False}]
        for n, v in results.items():
            params.append({"name": n, "value": f"{v:>.4f}", "editable": False})
        create_params_grid(params, clear_left_panel, clear_left_panel)
        truss_view.create_labels()
    except ValueError as e:
        showerror("Calculate", e)

def create_params_grid(params, ok, cancel):
    clear_left_panel()
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
    return variables

def clear_left_panel():
    for child in left_panel.winfo_children():
        child.destroy()
    Frame(left_panel).grid()  # hide left panel

def cancel():
    set_state("default")

def replace(old, new):
    set_state("default")
    new["id"] = new.get("id", truss.get_new_id_for(new["type"]))
    truss.replace(old, new)

def beam(**b):
    def ok():
        new = dict(end1=values["End 1"].get(), end2=values["End 2"].get(),
                   type="Beam", id=values["ID"].get())
        replace(b, new)

    nodes = tuple(n["id"] for n in truss.joints) + ("",)
    params = [{"name": b["type"], "value": b.get("id"), "editable": False},
              {"name": "End 1", "value": b.get("end1"), "values": nodes},
              {"name": "End 2", "value": b.get("end2"), "values": nodes}]
    values = create_params_grid(params, ok, cancel)

def pinned_support(**ps):
    def ok():
        new = dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                   type="PinnedSupport", id=values["ID"].get())
        replace(ps, new)

    params = [{"name": ps["type"], "value": ps.get("id"), "editable": False},
              {"name": "X", "value": ps.get("x", 0), "editable": True},
              {"name": "Y", "value": ps.get("y", 0), "editable": True}]
    values = create_params_grid(params, ok, cancel)

def roller_support(**rs):
    def ok():
        new = dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                   angle=float(values["Angle"].get()), type="RollerSupport",
                   id=values["ID"].get())
        replace(rs, new)

    params = [{"name": rs["type"], "value": rs.get("id"), "editable": False},
              {"name": "X", "value": rs.get("x", 0), "editable": True},
              {"name": "Y", "value": rs.get("y", 0), "editable": True},
              {"name": "Angle", "value": rs.get("angle", 0), "editable": True}]
    values = create_params_grid(params, ok, cancel)

def pin_joint(**pj):
    def ok():
        new = dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                   type="PinJoint", id=values["ID"].get())
        replace(pj, new)

    params = [{"name": pj["type"], "value": pj.get("id"), "editable": False},
              {"name": "X", "value": pj.get("x", 0), "editable": True},
              {"name": "Y", "value": pj.get("y", 0), "editable": True}]
    values = create_params_grid(params, ok, cancel)

def force(**f):
    def ok():
        new = dict(id=values["ID"].get(), value=float(values["Value"].get()),
                   applied_to=values["Applied to"].get(),
                   angle=float(values["Angle"].get()), type="Force")
        replace(f, new)

    nodes = tuple(n["id"] for n in truss.joints) + ("",)
    params = [
        {"name": f["type"], "value": f.get("id"), "editable": False},
        {"name": "Applied to", "value": f.get("applied_to"), "values": nodes},
        {"name": "Value", "value": f.get("value", 0), "editable": True},
        {"name": "Angle", "value": f.get("angle", 0), "editable": True}]
    values = create_params_grid(params, ok, cancel)

def load():
    filename = askopenfilename(defaultextension=".json",
                               filetypes=[("Truss Data", ".json")],
                               title="Load Truss")
    if filename:
        try:
            set_state("default")
            truss.load_from(filename)
        except IOError as error:
            showerror("Failed to load data", error)

def save():
    filename = asksaveasfilename(defaultextension=".json",
                                 filetypes=[("Truss Data", ".json")],
                                 title="Save Truss")
    if filename:
        try:
            truss.save_as(filename)
        except IOError as error:
            showerror("Failed to save data", error)

if __name__ == "__main__":
    main()
