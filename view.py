#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import atan2, degrees
from tkinter import (Button, Canvas, Entry, Frame, Label, StringVar,
                     LAST, E, N, S, W)
from tkinter.messagebox import showwarning
from misc import camel_to_snake, rotate, Observable
from domain import Truss


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

    def __init__(self, master, truss, **kw):
        super().__init__(master, bg=self.BACKGROUND_COLOR, **kw)
        self.bind('<Configure>', lambda _: self.refresh())
        self.__truss = truss
        self.__scale = self.__get_optimal_scale()
        self.__selected = None
        self.refresh()

    def update_truss(self, message):
        if message["action"] == "truss modified":
            self.selected = None
            self.refresh()

    @property
    def selected(self):
        return self.__selected

    @selected.setter
    def selected(self, item):
        self.dehighlight(self.__selected)
        self.__selected = item
        self.highlight(self.__selected)

    def refresh(self):
        self.delete("all")
        self.__scale = self.__get_optimal_scale()
        for i in self.__truss:
            self.create_item(i)
        for i in ("Force", "PinJoint", "PinnedSupport", "RollerSupport"):
            self.tag_raise(i)
        self.highlight(self.selected)

    def __get_optimal_scale(self):
        width = self.__truss.width
        height = self.__truss.height
        self.update()
        view_width = self.winfo_width() - 2 * self.X_OFFSET
        view_height = self.winfo_height() - 2 * self.Y_OFFSET
        x_scale = view_width / width if width else view_width
        y_scale = view_height / height if height else view_height
        return min(x_scale, y_scale)

    def create_item(self, i):
        create = getattr(self, f"create_{camel_to_snake(i['type'])}")
        create(i, self.get_color(i), self.ACTIVE_COLOR)

    def get_color(self, item):
        return self.FORCE_COLOR if item["type"] == "Force" else self.LINE_COLOR

    def highlight(self, item):
        if item:
            self.itemconfig(item.get("id"), activefill="",
                            fill=self.HIGHLIGHT_COLOR)

    def dehighlight(self, item):
        if item:
            self.itemconfig(item.get("id"), fill=self.get_color(item),
                            activefill=self.ACTIVE_COLOR)

    def create_circle(self, x, y, radius, color, activefill, tags):
        self.create_oval(x - radius, y - radius, x + radius, y + radius,
                         tags=tags, width=2, outline=color,
                         fill=self.BACKGROUND_COLOR, activefill=activefill)

    def create_pin_joint(self, pj, color, activefill):
        x, y = self.to_canvas_pos(pj["x"], pj["y"])
        self.create_circle(x, y, 4, color, activefill, ("PinJoint", pj["id"]))

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

    def create_beam(self, b, color, activecolor):
        end1 = self.to_canvas_pos(b["x1"], b["y1"])
        end2 = self.to_canvas_pos(b["x2"], b["y2"])
        self.create_line(*end1, *end2, tags=("Beam", b["id"]), width=2,
                         fill=color, activefill=activecolor)

    def create_force(self, f, color, activecolor):
        x2, y2 = self.to_canvas_pos(f["x"], f["y"])
        x1, y1 = rotate((x2, y2), (x2 + self.FORCE_LENGTH, y2), f["angle"])

        self.create_line(x1, y1, x2, y2, tags=("Force", f["id"]), width=2,
                         arrow=LAST, fill=color, activefill=activecolor)

    def create_labels(self):
        for item in self.__truss:
            if item["type"] != "PinJoint":
                self.create_label(item)

    def create_label(self, i):
        x = y = 0
        if i["type"] == "Beam":
            x, y = self.to_canvas_pos((i["x1"] + i["x2"]) / 2,
                                      (i["y1"] + i["y2"]) / 2)
        if i["type"] == "Force":
            x, y = self.to_canvas_pos(i["x"], i["y"])
            x, y = rotate((x, y), (x + self.FORCE_LENGTH / 2, y), i["angle"])
        if Truss.is_joint(i):
            x, y = self.to_canvas_pos(i["x"], i["y"])
        t = self.create_text(x, y, text=i["id"], tags="Label", font="Arial 10",
                             fill=self.LABEL_COLOR)
        b = self.create_rectangle(self.bbox(t), fill=self.BACKGROUND_COLOR,
                                  outline=self.BACKGROUND_COLOR, tags="Label")
        self.tag_lower(b, t)

    def to_canvas_pos(self, x, y):
        rx = x - self.__truss.left
        canvas_x = rx * self.__scale + self.X_OFFSET
        ry = y - self.__truss.bottom
        canvas_y = int(self.winfo_height()) - self.Y_OFFSET - ry * self.__scale
        return canvas_x, canvas_y

    def to_truss_pos(self, x, y):
        rx = (x - self.X_OFFSET) / self.__scale
        truss_x = rx + self.__truss.left
        ry = (int(self.winfo_height()) - self.Y_OFFSET - y) / self.__scale
        truss_y = ry + self.__truss.bottom
        return truss_x, truss_y


class ItemEditState():
    """This is FSM for item editing GUI."""
    def __init__(self):
        self.__item = None
        self.__state = self._process_default

    def default(self):
        self.__item = None
        self.__state = self._process_default

    def new(self, item_type):
        self.__item = dict(type=item_type)
        self.__state = self._edit_item

    def edit(self, item):
        self.__item = item
        self.__state = self._edit_item

    def process(self, message):
        return self.__state(message)

    def _process_default(self, msg):
        ret = dict(item=self.__item)
        if msg["action"] == "item click":
            self.__item = msg["item"]
            ret = dict(action="select", item=self.__item)
        elif msg["action"] == "click":
            self.__item = None
            ret = dict(action="cancel")
        elif msg["action"] == "delete":
            ret = dict(action="delete", item=self.__item)
            self.__item = None
        return ret

    def _edit_item(self, msg):
        r = getattr(self, f"_edit_{camel_to_snake(self.__item['type'])}")(msg)
        if r["action"] in ("finish editing", "specify force value"):
            self.default()
        return r

    def _edit_beam(self, msg):
        if self.__item.get("end2") is None:
            self.__item.update(dict(x2=msg["x"], y2=msg["y"]))
        if self.__item.get("end1") is None:
            return self._specify_node("end1", "x1", "y1", msg)
        if self.__item.get("end2") is None:
            return self._specify_node("end2", "x2", "y2", msg)
        return dict(action="finish editing", item=self.__item)

    def _edit_force(self, msg):
        if self.__item.get("applied_to") is None:
            ret = self._specify_node("applied_to", "x", "y", msg)
            ret["item"] = {"angle": -45, **ret["item"]}
            return ret
        if self.__item.get("angle") is None:
            ret = self._specify_angle(msg)
            ret["item"]["angle"] = 180 - ret["item"]["angle"]
            return ret
        return dict(action="specify force value", item=self.__item)

    def _edit_pin_joint(self, msg):
        if self.__item.get("x") is None or self.__item.get("y") is None:
            return self._specify_pos(msg)
        return dict(action="finish editing", item=self.__item)

    def _edit_pinned_support(self, msg):
        if self.__item.get("x") is None or self.__item.get("y") is None:
            return self._specify_pos(msg)
        return dict(action="finish editing", item=self.__item)

    def _edit_roller_support(self, msg):
        if self.__item.get("x") is None or self.__item.get("y") is None:
            ret = self._specify_pos(msg)
            ret["item"] = {"angle": 90, **ret["item"]}
            return ret
        if self.__item.get("angle") is None:
            return self._specify_angle(msg)
        return dict(action="finish editing", item=self.__item)

    def _specify_pos(self, msg):
        item = {**self.__item, **dict(x=msg["x"], y=msg["y"])}
        if msg["action"] in ("click", "item click"):
            self.__item.update(dict(x=msg["x"], y=msg["y"]))
            return self._edit_item({**msg, "action": "move"})
        return dict(action="update tmp", item=item)

    def _specify_angle(self, msg):
        angle = degrees(atan2(self.__item["y"] - msg["y"],
                              self.__item["x"] - msg["x"]))
        if msg["action"] in ("click", "item click"):
            self.__item["angle"] = angle
            return self._edit_item({**msg, "action": "move"})
        return dict(action="update tmp", item={**self.__item, "angle": angle})

    def _specify_node(self, node, x, y, msg):
        self.__item.update({x: msg["x"], y: msg["y"]})
        if msg["action"] == "item click" and Truss.is_joint(msg["item"]):
            j = msg["item"]
            self.__item.update({node: j["id"], x: j["x"], y: j["y"]})
            return self._edit_item({**msg, "action": "move"})
        return dict(action="update tmp", item=self.__item)


class PropertyEditor(Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.__variables = {}

    def show(self, properties, ok, cancel):
        new_vars = {p["name"]: StringVar(value=p["value"]) for p in properties}
        if self.__variables.keys() == new_vars.keys():
            for name, var in new_vars.items():
                self.__variables[name].set(var.get())
            self.__update_widgets(properties)
        else:
            self.clear()
            self.__variables = new_vars
            self.__create_widgets(properties, ok, cancel)
        return self.__variables

    def __create_widgets(self, properties, ok, cancel):
        o = dict(padx=5, pady=5, sticky=W+E+N+S)
        i = 0
        for p in properties:
            name = p["name"]
            Label(self, text=name).grid(column=0, row=i, **o)
            if p.get("command"):
                w = Button(self, name=camel_to_snake(name),
                           text=p["value"], command=p["command"])
            elif p.get("editable"):
                w = Entry(self, textvariable=self.__variables[name])
            else:
                w = Label(self, text=p["value"])
            w.grid(column=1, row=i, **o)
            i += 1
        Button(self, text="OK", command=ok).grid(column=0, row=i, **o)
        Button(self, text="Cancel", command=cancel).grid(column=1, row=i, **o)

    def __update_widgets(self, properties):
        for p in properties:
            if p.get("command"):
                btn = self.nametowidget(camel_to_snake(p["name"]))
                btn["text"] = p["value"] if p.get("value") is not None else ""

    def clear(self):
        self.__variables = {}
        for child in self.winfo_children():
            child.destroy()
        Frame(self).grid()  # hack to hide empty instance


class TrussPropertyEditor(PropertyEditor, Observable):
    def __init__(self, master, **kw):
        PropertyEditor.__init__(self, master, **kw)
        Observable.__init__(self)

    def show_properties(self, item):
        getattr(self, camel_to_snake(item["type"]))(item)

    def beam(self, b):
        def edit_end1():
            self.notify(dict(action="edit field", item=b, field="end1"))

        def edit_end2():
            self.notify(dict(action="edit field", item=b, field="end2"))

        def ok():
            new = dict(type="Beam",
                       id=values["Beam"].get(),
                       end1=self.nametowidget("end 1")["text"],
                       end2=self.nametowidget("end 2")["text"])
            self.finish_editing(new)

        p = [{"name": b["type"], "value": b.get("id"), "editable": False},
             {"name": "End 1", "value": b.get("end1"), "command": edit_end1},
             {"name": "End 2", "value": b.get("end2"), "command": edit_end2}]
        values = self.show(properties=p, ok=ok, cancel=self.cancel)

    def pinned_support(self, ps):
        def ok():
            try:
                new = dict(type="PinnedSupport",
                           id=values["PinnedSupport"].get(),
                           x=self.getdouble(values["X"].get()),
                           y=self.getdouble(values["Y"].get()))
                self.finish_editing(new)
            except ValueError:
                self.__show_not_a_float_warning()

        p = [{"name": ps["type"], "value": ps.get("id"), "editable": False},
             {"name": "X", "value": ps.get("x", 0), "editable": True},
             {"name": "Y", "value": ps.get("y", 0), "editable": True}]
        values = self.show(properties=p, ok=ok, cancel=self.cancel)

    def roller_support(self, rs):
        def ok():
            try:
                new = dict(type="RollerSupport",
                           id=values["RollerSupport"].get(),
                           x=self.getdouble(values["X"].get()),
                           y=self.getdouble(values["Y"].get()),
                           angle=self.getdouble(values["Angle"].get()))
                self.finish_editing(new)
            except ValueError:
                self.__show_not_a_float_warning()

        p = [{"name": rs["type"], "value": rs.get("id"), "editable": False},
             {"name": "X", "value": rs.get("x", 0), "editable": True},
             {"name": "Y", "value": rs.get("y", 0), "editable": True},
             {"name": "Angle", "value": rs.get("angle", 0), "editable": True}]
        values = self.show(properties=p, ok=ok, cancel=self.cancel)

    def pin_joint(self, pj):
        def ok():
            try:
                new = dict(type="PinJoint",
                           id=values["PinJoint"].get(),
                           x=self.getdouble(values["X"].get()),
                           y=self.getdouble(values["Y"].get()))
                self.finish_editing(new)
            except ValueError:
                self.__show_not_a_float_warning()

        p = [{"name": pj["type"], "value": pj.get("id"), "editable": False},
             {"name": "X", "value": pj.get("x", 0), "editable": True},
             {"name": "Y", "value": pj.get("y", 0), "editable": True}]
        values = self.show(properties=p, ok=ok, cancel=self.cancel)

    def force(self, f):
        def edit_application():
            self.notify(dict(action="edit field", item=f, field="applied_to"))

        def ok():
            try:
                new = dict(type="Force",
                           id=values["Force"].get(),
                           applied_to=self.nametowidget("applied to")["text"],
                           angle=self.getdouble(values["Angle"].get()),
                           value=self.getdouble(values["Value"].get()))
                self.finish_editing(new)
            except ValueError:
                self.__show_not_a_float_warning()

        p = [{"name": f["type"], "value": f.get("id"), "editable": False},
             {"name": "Applied to", "value": f.get("applied_to"),
              "command": edit_application},
             {"name": "Angle", "value": f.get("angle", 0), "editable": True},
             {"name": "Value", "value": f.get("value", 0), "editable": True}]
        values = self.show(properties=p, ok=ok, cancel=self.cancel)

    def __show_not_a_float_warning(self):
        showwarning(parent=self, title="Illegal value",
                    message="Not a floating point value.\nPlease try again")

    def show_results(self, results):
        p = [{"name": "Force", "value": "Value", "editable": False}]
        for n, v in results.items():
            p.append({"name": n, "value": f"{v:>.4f}", "editable": False})
        self.show(properties=p, ok=self.cancel, cancel=self.cancel)

    def cancel(self):
        self.notify(dict(action="cancel"))

    def finish_editing(self, item):
        def all_mandatory_values_specified():
            fields = Truss.MANDATORY_FIELDS[item["type"]]
            return all(item.get(f) != "" for f in fields if f != "id")

        if all_mandatory_values_specified():
            self.notify(dict(action="finish editing", item=item))
        else:
            self.cancel()
