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
images = {}
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
    for i, f in buttons.items():
        images[i] = PhotoImage(file=f"img/{i}.gif")  # prevent GC
        Button(toolbar, image=images[i], relief=FLAT, command=f
               ).pack(side=LEFT, padx=2, pady=2)
    toolbar.pack(side=TOP, fill=X)
    left_panel.pack(side=LEFT, fill=Y)
    truss_view.pack(expand=YES, fill=BOTH)
    root.bind("<Delete>", lambda _: state.send(dict(action="delete")))
    set_state("default")
    truss.append_observer_callback(truss_view.update_truss)
    truss.append_observer_callback(truss_update)
    truss_view.append_observer_callback(lambda m: state.send(m))
    root.mainloop()

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
            truss_view.highlighted = cur_item = msg["item"]
            globals()[camel_to_snake(cur_item["type"])](**cur_item)
        elif msg["action"] == "click":
            truss_view.highlighted = cur_item = None
            clear_left_panel()
        elif msg["action"] == "delete":
            truss.remove(cur_item)
            truss_view.highlighted = cur_item = None

def process_pj():
    while True:
        msg = yield
        if msg["action"] == "move":
            truss_view.delete("tmp")
            cur_item = dict(x=msg["x"], y=msg["y"], type="PinJoint", id="tmp")
            truss_view.create_item(cur_item)
        elif msg["action"] == "item click":
            set_state("default")
            cur_item = {**cur_item, "id": truss.get_new_id("PinJoint")}
            truss.append(cur_item)

def process_ps():
    while True:
        msg = yield
        if msg["action"] == "move":
            truss_view.delete("tmp")
            cur_item = dict(x=msg["x"], y=msg["y"],
                            type="PinnedSupport", id="tmp")
            truss_view.create_item(cur_item)
        elif msg["action"] == "item click":
            set_state("default")
            cur_item = {**cur_item, "id": truss.get_new_id("PinnedSupport")}
            truss.append(cur_item)

def process_rs():
    # specify position
    while True:
        msg = yield
        if msg["action"] == "move":
            truss_view.delete("tmp")
            cur_item = dict(x=msg["x"], y=msg["y"],
                            angle=90, type="RollerSupport", id="tmp")
            truss_view.create_item(cur_item)
        elif msg["action"] == "item click":
            break
    # specify angle
    while True:
        msg = yield
        if msg["action"] == "move":
            truss_view.delete("tmp")
            angle = degrees(atan2(cur_item["y"] - msg["y"],
                                  cur_item["x"] - msg["x"]))
            cur_item = {**cur_item, "angle": angle}
            truss_view.create_item(cur_item)
        elif msg["action"] in ("click", "item click"):
            set_state("default")
            cur_item = {**cur_item, "id": truss.get_new_id("RollerSupport")}
            truss.append(cur_item)

def process_beam():
    # specify 1st end
    while True:
        m = yield
        if m["action"] == "item click" and m["item"]["type"] in truss.JOINTS:
            j = m["item"]
            cur_item = dict(x1=j["x"], y1=j["y"], x2=j["x"], y2=j["y"],
                            end1=j["id"], type="Beam", id="tmp")
            break
    # specify 2nd end
    while True:
        m = yield
        if m["action"] == "move":
            truss_view.delete("tmp")
            cur_item = {**cur_item, "x2": m["x"], "y2": m["y"]}
            truss_view.create_item(cur_item)
            truss_view.tag_lower("tmp")
        elif m["action"] == "item click" and m["item"] and m["item"]["type"] in truss.JOINTS:
            set_state("default")
            j = m["item"]
            cur_item = {**cur_item, "end2": j["id"], "id": truss.get_new_id("Beam")}
            truss.append(cur_item)

def process_force():
    # specify application
    while True:
        m = yield
        if m["action"] == "item click" and m["item"]["type"] in truss.JOINTS:
            j = m["item"]
            cur_item = dict(applied_to=j["id"], x=j["x"], y=j["y"],
                            angle=0, value=0, type="Force", id="tmp")
            break
    # specify angle and value
    while True:
        m = yield
        if m["action"] == "move":
            truss_view.delete("tmp")
            angle = 180 - degrees(atan2(cur_item["y"] - m["y"],
                                        cur_item["x"] - m["x"]))
            cur_item = {**cur_item, "angle": angle}
            truss_view.create_item(cur_item)
        elif m["action"] in ("click", "item click"):
            set_state("default")
            value = askfloat("Force value", "Please enter force value",
                             initialvalue=0, parent=root)
            cur_item = {**cur_item, "value": float(value or 0),
                        "id": truss.get_new_id("Force")}
            truss.append(cur_item)

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

def add(item):
    clear_left_panel()
    truss.append(item)

def replace(old, new):
    clear_left_panel()
    truss.replace(old, new)

def beam(**b):
    def new_beam():
        return dict(end1=values["End 1"].get(), end2=values["End 2"].get(),
                    type="Beam", id=values["ID"].get())

    nodes = [n["id"] for n in truss.joints]
    if not nodes:
        nodes.append("")
    item_id = b.get("id", truss.get_new_id("Beam"))
    params = [{"name": "ID", "value": item_id, "editable": False},
              {"name": "End 1", "value": b.get("end1"), "values": nodes},
              {"name": "End 2", "value": b.get("end2"), "values": nodes}]
    ok = (lambda: replace(b, new_beam())) if b else (lambda: add(new_beam()))
    values = create_params_grid(params, ok, clear_left_panel)

def pinned_support(**ps):
    def new_ps():
        return dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                    type="PinnedSupport", id=values["ID"].get())

    item_id = ps.get("id", truss.get_new_id("PinnedSupport"))
    params = [{"name": "ID", "value": item_id, "editable": False},
              {"name": "X", "value": ps.get("x", 0), "editable": True},
              {"name": "Y", "value": ps.get("y", 0), "editable": True}]
    ok = (lambda: replace(ps, new_ps())) if ps else (lambda: add(new_ps()))
    values = create_params_grid(params, ok, clear_left_panel)

def roller_support(**rs):
    def new_rs():
        return dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                    angle=float(values["Angle"].get()), type="RollerSupport",
                    id=values["ID"].get())

    item_id = rs.get("id", truss.get_new_id("RollerSupport"))
    params = [{"name": "ID", "value": item_id, "editable": False},
              {"name": "X", "value": rs.get("x", 0), "editable": True},
              {"name": "Y", "value": rs.get("y", 0), "editable": True},
              {"name": "Angle", "value": rs.get("angle", 0), "editable": True}]
    ok = (lambda: replace(rs, new_rs())) if rs else (lambda: add(new_rs()))
    values = create_params_grid(params, ok, clear_left_panel)

def pin_joint(**pj):
    def new_pj():
        return dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                    type="PinJoint", id=values["ID"].get())

    item_id = pj.get("id", truss.get_new_id("PinJoint"))
    params = [{"name": "ID", "value": item_id, "editable": False},
              {"name": "X", "value": pj.get("x", 0), "editable": True},
              {"name": "Y", "value": pj.get("y", 0), "editable": True}]
    ok = (lambda: replace(pj, new_pj())) if pj else (lambda: add(new_pj()))
    values = create_params_grid(params, ok, clear_left_panel)

def force(**f):
    def new_force():
        return dict(id=values["ID"].get(), value=float(values["Value"].get()),
                    applied_to=values["Applied to"].get(),
                    angle=float(values["Angle"].get()), type="Force")

    nodes = [n["id"] for n in truss.joints]
    if not nodes:
        nodes.append("")
    item_id = f.get("id", truss.get_new_id("Force"))
    params = [
        {"name": "ID", "value": item_id, "editable": False},
        {"name": "Applied to", "value": f.get("applied_to"), "values": nodes},
        {"name": "Value", "value": f.get("value", 0), "editable": True},
        {"name": "Angle", "value": f.get("angle", 0), "editable": True}]
    ok = (lambda: replace(f, new_force())) if f else (lambda: add(new_force()))
    values = create_params_grid(params, ok, clear_left_panel)

def load():
    filename = askopenfilename(defaultextension=".json",
                               filetypes=[("Truss Data", ".json")],
                               title="Load Truss")
    if filename:
        try:
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
