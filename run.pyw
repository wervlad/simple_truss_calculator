#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import OrderedDict
from tkinter import (Button, Frame, PhotoImage, Tk,
                     BOTH, FLAT, LEFT, RAISED, TOP, X, Y, YES)
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning
from tkinter.simpledialog import askfloat  # type: ignore
from domain import History, Truss
from view import TrussView, ItemEditState, TrussPropertyEditor


# global variables
root = Tk()
truss = Truss()
history = History(truss.items)
truss_view = TrussView(root, truss, name="truss view")
property_editor = TrussPropertyEditor(root, name="property editor")
state = ItemEditState()
images = {}

def main():
    root.title("Simple Truss Calculator")
    toolbar = create_toolbar()
    toolbar.pack(side=TOP, fill=X)
    property_editor.pack(side=LEFT, fill=Y)
    truss_view.pack(expand=YES, fill=BOTH)

    bind_hotkeys()
    truss.append_observer_callback(truss_view.update_truss)
    truss.append_observer_callback(truss_update)
    history.append_observer_callback(history_update)
    property_editor.append_observer_callback(state_update)
    new()

    root.mainloop()

def create_toolbar():
    toolbar = Frame(root, bd=1, name="toolbar", relief=RAISED)
    buttons = OrderedDict({"new": new,
                           "load": load,
                           "save": save,
                           "undo": undo,
                           "redo": redo,
                           "labels": truss_view.create_labels,
                           "refresh": truss_view.refresh,
                           "calculate": calculate,
                           "pinnedSupport": lambda: state.new("PinnedSupport"),
                           "rollerSupport": lambda: state.new("RollerSupport"),
                           "pinJoint": lambda: state.new("PinJoint"),
                           "beam": lambda: state.new("Beam"),
                           "force": lambda: state.new("Force")})
    for i, f in buttons.items():
        images[i] = PhotoImage(file=f"img/{i}.gif")  # prevent GC
        Button(toolbar, name=i, image=images[i], relief=FLAT, command=f
               ).pack(side=LEFT, padx=2, pady=2)
    return toolbar

def bind_hotkeys():
    root.bind("<Delete>", on_del_click)
    root.bind('<Escape>', lambda _: state_update(dict(action="cancel")))
    root.bind("<Control-n>", lambda _: truss.new())
    root.bind("<Control-l>", lambda _: load())
    root.bind("<Control-s>", lambda _: save())
    root.bind("<Control-z>", lambda _: undo())
    root.bind("<Control-y>", lambda _: redo())
    root.bind("<Control-a>", lambda _: truss_view.create_labels())
    root.bind("<Control-u>", lambda _: truss_view.refresh())
    root.bind("<Control-c>", lambda _: calculate())
    root.bind("<Control-p>", lambda _: state.new("PinnedSupport"))
    root.bind("<Control-r>", lambda _: state.new("RollerSupport"))
    root.bind("<Control-j>", lambda _: state.new("PinJoint"))
    root.bind("<Control-b>", lambda _: state.new("Beam"))
    root.bind("<Control-f>", lambda _: state.new("Force"))
    truss_view.bind("<Button-1>", on_click)
    truss_view.bind("<Motion>", on_mouse_move)

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

def history_update(msg):
    if msg["action"] == "history changed":
        undo_button = root.nametowidget("toolbar.undo")
        undo_button["state"] = "normal" if history.can_undo() else "disabled"
        redo_button = root.nametowidget("toolbar.redo")
        redo_button["state"] = "normal" if history.can_redo() else "disabled"

def truss_update(msg):
    if msg["action"] == "invalid items removed":
        invalid = ", ".join(f"{i['type']} {i['id']}" for i in msg["items"])
        showwarning("Warning", f"Invalid items were removed: {invalid}")
    elif msg["action"] == "truss modified":
        property_editor.clear()
        history.append(truss.items)

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
        if msg["field"] in item:
            item = item.copy()
            item.pop(msg["field"])
            state.edit(item)
            state_update(state.process(dict(action="update", x=0, y=0)))

def calculate():
    state.default()
    try:
        property_editor.show_results(truss.calculate())
        truss_view.create_labels()
    except ValueError as error:
        showwarning("Calculate", error)

def new():
    truss.new()
    history.reset(truss.items)

def load():
    filename = askopenfilename(defaultextension=".json",
                               filetypes=[("Truss Data", ".json")],
                               title="Load Truss")
    if filename:
        try:
            state.default()
            truss.load_from(filename)
            history.reset(truss.items)
        except IOError as error:
            showwarning("Failed to load data", error)

def save():
    filename = asksaveasfilename(defaultextension=".json",
                                 filetypes=[("Truss Data", ".json")],
                                 title="Save Truss")
    if filename:
        try:
            truss.save_as(filename)
        except IOError as error:
            showwarning("Failed to save data", error)

def undo():
    truss.items = history.undo()

def redo():
    truss.items = history.redo()

if __name__ == "__main__":
    main()
