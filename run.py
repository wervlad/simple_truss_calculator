#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from collections import OrderedDict
from tkinter import (Button, Frame, PhotoImage, Tk,
                     BOTH, FLAT, LEFT, RAISED, TOP, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from tkinter.simpledialog import askfloat
from domain import Truss
from view import TrussView, TrussEditState, TrussPropertyEditor


# global variables
root = Tk()
truss = Truss()
truss_view = TrussView(root, truss)
property_editor = TrussPropertyEditor(root)
state = TrussEditState()

def main():
    root.title("Simple Truss Calculator")
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = OrderedDict({"new": truss.new,
                           "load": load,
                           "save": save,
                           "labels": truss_view.create_labels,
                           "refresh": truss_view.refresh,
                           "calculate": calculate,
                           "pinnedSupport": lambda: state.set_state("ps"),
                           "rollerSupport": lambda: state.set_state("rs"),
                           "pinJoint": lambda: state.set_state("pj"),
                           "beam": lambda: state.set_state("beam"),
                           "force": lambda: state.set_state("force")})
    images = {}  # variable exists until root.mainloop() is running
    for i, f in buttons.items():
        images[i] = PhotoImage(file=f"img/{i}.gif")  # prevent GC
        Button(toolbar, image=images[i], relief=FLAT, command=f
               ).pack(side=LEFT, padx=2, pady=2)
    toolbar.pack(side=TOP, fill=X)
    property_editor.pack(side=LEFT, fill=Y)
    truss_view.pack(expand=YES, fill=BOTH)
    root.bind("<Delete>", lambda _: state.send(dict(action="delete")))
    root.bind('<Escape>', lambda _: state_update(dict(action="cancel")))
    truss_view.bind("<Button-1>", on_click)
    truss_view.bind("<Motion>", on_mouse_move)
    truss.append_observer_callback(truss_view.update_truss)
    truss.append_observer_callback(truss_update)
    state.append_observer_callback(state_update)
    property_editor.append_observer_callback(state_update)
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
    state.send(dict(action="move", x=x, y=y))

def truss_update(msg):
    if msg["action"] == "invalid items removed":
        invalid = ", ".join(f"{i['type']} {i['id']}" for i in msg["items"])
        showerror("Warning", f"Invalid items were removed: {invalid}")
    elif msg["action"] == "truss modified":
        property_editor.clear()

def state_update(msg):
    i = msg.get("item")
    action = msg.get("action")
    if action == "select":
        truss_view.highlighted = i
        property_editor.show_properties(truss, i)
    if action == "cancel":
        state.set_state("default")
        truss_view.highlighted = None
        property_editor.clear()
    if action == "delete":
        truss.remove(i)
        truss_view.highlighted = None
    if action == "update tmp":
        property_editor.show_properties(truss, i)
        truss_view.delete("temporary")
        truss_view.create_item({**i, "id": "temporary"})
        truss_view.tag_lower("temporary")
    if action in ("create new", "replace"):
        state.set_state("default")
        if not i.get("id"):
            i["id"] = truss.get_new_id_for(i["type"])
        truss.replace(msg.get("old"), i)
    if action == "create force":
        i["value"] = askfloat("Force value", "Please enter force value",
                              initialvalue=0, parent=root)
        action = "create new" if i["value"] else "cancel"
        state_update(dict(action=action, item=i))

def calculate():
    state.set_state("default")
    try:
        property_editor.show_results(truss.calculate())
        truss_view.create_labels()
    except ValueError as e:
        showerror("Calculate", e)

def load():
    filename = askopenfilename(defaultextension=".json",
                               filetypes=[("Truss Data", ".json")],
                               title="Load Truss")
    if filename:
        try:
            state.set_state("default")
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
