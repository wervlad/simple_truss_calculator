#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from collections import OrderedDict
from tkinter import (Button, Frame, PhotoImage, Tk,
                     BOTH, FLAT, LEFT, RAISED, TOP, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from tkinter.simpledialog import askfloat
from domain import Truss
from view import TrussView, ItemEditState, TrussPropertyEditor


# global variables
root = Tk()
truss = Truss()
truss_view = TrussView(root, truss)
property_editor = TrussPropertyEditor(root)
state = ItemEditState()

def main():
    root.title("Simple Truss Calculator")
    toolbar = Frame(root, bd=1, relief=RAISED)
    buttons = OrderedDict({"new": truss.new,
                           "load": load,
                           "save": save,
                           "labels": truss_view.create_labels,
                           "refresh": truss_view.refresh,
                           "calculate": calculate,
                           "pinnedSupport": lambda: state.new("PinnedSupport"),
                           "rollerSupport": lambda: state.new("RollerSupport"),
                           "pinJoint": lambda: state.new("PinJoint"),
                           "beam": lambda: state.new("Beam"),
                           "force": lambda: state.new("Force")})
    images = {}  # variable exists until root.mainloop() is running
    for i, f in buttons.items():
        images[i] = PhotoImage(file=f"img/{i}.gif")  # prevent GC
        Button(toolbar, image=images[i], relief=FLAT, command=f
               ).pack(side=LEFT, padx=2, pady=2)
    toolbar.pack(side=TOP, fill=X)
    property_editor.pack(side=LEFT, fill=Y)
    truss_view.pack(expand=YES, fill=BOTH)
    root.bind("<Delete>", on_del_click)
    root.bind('<Escape>', lambda _: state_update(dict(action="cancel")))
    truss_view.bind("<Button-1>", on_click)
    truss_view.bind("<Motion>", on_mouse_move)
    truss.append_observer_callback(truss_view.update_truss)
    truss.append_observer_callback(truss_update)
    property_editor.append_observer_callback(state_update)
    root.mainloop()

def on_click(event):
    x, y = truss_view.to_truss_pos(event.x, event.y)
    msg = dict(action="click", x=x, y=y)
    items_under_cursor = truss_view.find_withtag("current")
    if items_under_cursor:
        item = truss.find_by_id(truss_view.gettags(items_under_cursor[0])[1])
        if item:
            msg.update(dict(action="item click", item=item))
    state_update(state.process(msg))

def on_del_click(_):
    state_update(state.process(dict(action="delete")))

def on_mouse_move(event):
    x, y = truss_view.to_truss_pos(event.x, event.y)
    state_update(state.process(dict(action="move", x=x, y=y)))

def truss_update(msg):
    if msg["action"] == "invalid items removed":
        invalid = ", ".join(f"{i['type']} {i['id']}" for i in msg["items"])
        showerror("Warning", f"Invalid items were removed: {invalid}")
    elif msg["action"] == "truss modified":
        property_editor.clear()

def state_update(msg):
    item = msg.get("item")
    truss_view.selected = item
    action = msg.get("action")
    if action == "select":
        property_editor.show_properties(item)
    if action == "cancel":
        state.default()
        property_editor.clear()
    if action == "delete":
        truss.remove(item)
    if action == "update tmp":
        property_editor.show_properties(item)
        truss_view.delete("temporary")
        truss_view.create_item({**item, "id": "temporary"})
        truss_view.tag_lower("temporary")
    if action == "finish editing":
        state.default()
        if item.get("id"):
            old = truss.find_by_id(item.get("id"))
        else:
            old = None
            item["id"] = truss.get_new_id_for(item["type"])
        truss.replace(old, item)
    if action == "specify force value":
        if item.get("value") is None:
            item["value"] = askfloat("Force value", "Please enter force value",
                                     initialvalue=0, parent=root)
        action = "finish editing" if item["value"] else "cancel"
        state_update(dict(action=action, item=item))
    if action == "edit field":
        item = item.copy()
        item.pop(msg["field"])
        state.edit(item)

def calculate():
    state.default()
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
            state.default()
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
