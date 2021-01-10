#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from math import atan2, degrees
from tkinter import (Button, Canvas, Entry, Frame, Label, OptionMenu,
                     StringVar, LAST, E, N, S, W)
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

    def __init__(self, master, truss):
        super().__init__(master, bg=self.BACKGROUND_COLOR)
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


class TrussEditState():
    """This is FSM for truss editing GUI."""
    def __init__(self):
        self.__item = None
        self.__state = None
        self.set_to("default")

    def set_to(self, new_state):
        self.__item = None
        self.__state = getattr(self, f"process_{new_state}")

    def process(self, message):
        return self.__state(message)

    def process_default(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "item click":
            self.__item = m["item"]
            ret = dict(action="select", item=self.__item)
        elif m["action"] == "click":
            self.__item = None
            ret = dict(action="cancel")
        elif m["action"] == "delete":
            ret = dict(action="delete", item=self.__item)
            self.__item = None
        return ret

    def process_pj(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item = dict(x=m["x"], y=m["y"], type="PinJoint")
            ret = dict(action="update tmp", item=self.__item)
        elif m["action"] in ("click", "item click"):
            ret = dict(action="create new", item=self.__item)
        return ret

    def process_ps(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item = dict(x=m["x"], y=m["y"], type="PinnedSupport")
            ret = dict(action="update tmp", item=self.__item)
        elif m["action"] in ("click", "item click"):
            ret = dict(action="create new", item=self.__item)
        return ret

    def process_rs(self, m):
        self.__state = self.specify_rs_position
        return self.process(m)

    def specify_rs_position(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item = dict(x=m["x"], y=m["y"], angle=90,
                               type="RollerSupport")
            ret = dict(action="update tmp", item=self.__item)
        elif m["action"] in ("click", "item click"):
            self.__state = self.specify_rs_angle
        return ret

    def specify_rs_angle(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item["angle"] = degrees(atan2(self.__item["y"] - m["y"],
                                                 self.__item["x"] - m["x"]))
            ret = dict(action="update tmp", item=self.__item)
        elif m["action"] in ("click", "item click"):
            ret = dict(action="create new", item=self.__item)
        return ret

    def process_beam(self, m):
        self.__state = self.specify_beam_end1
        return self.process(m)

    def specify_beam_end1(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item = dict(x1=0, y1=0, x2=0, y2=0, type="Beam")
            ret = dict(action="update tmp", item=self.__item)
        if (m["action"] == "item click" and Truss.is_joint(m["item"])):
            j = m["item"]
            self.__item = dict(end1=j["id"], x1=j["x"], y1=j["y"], type="Beam")
            self.__state = self.specify_beam_end2
        return ret

    def specify_beam_end2(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item = {**self.__item, "x2": m["x"], "y2": m["y"]}
            ret = dict(action="update tmp", item=self.__item)
        elif (m["action"] == "item click" and Truss.is_joint(m["item"])):
            self.__item["end2"] = m["item"]["id"]
            ret = dict(action="create new", item=self.__item)
        return ret

    def process_force(self, m):
        self.__state = self.specify_force_application
        return self.process(m)

    def specify_force_application(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item = dict(x=m["x"], y=m["y"], angle=-45, type="Force")
            ret = dict(action="update tmp", item=self.__item)
        if (m["action"] == "item click" and Truss.is_joint(m["item"])):
            j = m["item"]
            self.__item = dict(applied_to=j["id"], x=j["x"], y=j["y"],
                               type="Force")
            self.__state = self.specify_force_angle
        return ret

    def specify_force_angle(self, m):
        ret = dict(item=self.__item)
        if m["action"] == "move":
            self.__item["angle"] = 180 - degrees(atan2(
                self.__item["y"] - m["y"], self.__item["x"] - m["x"]))
            ret = dict(action="update tmp", item=self.__item)
        elif m["action"] in ("click", "item click"):
            ret = dict(action="create force", item=self.__item)
        return ret


class PropertyEditor(Frame):
    def create(self, properties, ok, cancel):
        self.clear()
        options = dict(padx=5, pady=5, sticky=W+E+N+S)
        variables = {}
        i = 0
        for p in properties:
            name = p["name"]
            Label(self, text=name).grid(column=0, row=i, **options)
            variables[name] = StringVar(value=p["value"])
            if p.get("values") is None:
                if p.get("editable"):
                    w = Entry(self, textvariable=variables[name])
                else:
                    w = Label(self, text=p["value"])
            else:
                w = OptionMenu(self, variables[name], *p["values"])
            w.grid(column=1, row=i, **options)
            i += 1
        Button(self, text="OK", command=ok).grid(column=0, row=i, **options)
        Button(self, text="Cancel", command=cancel
               ).grid(column=1, row=i, **options)
        return variables

    def clear(self):
        for child in self.winfo_children():
            child.destroy()
        Frame(self).grid()  # hack to hide empty instance


class TrussPropertyEditor(PropertyEditor, Observable):
    def __init__(self, master, truss):
        PropertyEditor.__init__(self, master)
        Observable.__init__(self)
        self.__truss = truss

    def show_properties(self, item):
        getattr(self, camel_to_snake(item["type"]))(item)

    def beam(self, b):
        def ok():
            new = dict(end1=values["End 1"].get(), end2=values["End 2"].get(),
                       type="Beam", id=values["Beam"].get())
            self.replace(b, new)

        nodes = tuple(n["id"] for n in self.__truss.joints) + ("",)
        ps = [{"name": b["type"], "value": b.get("id"), "editable": False},
              {"name": "End 1", "value": b.get("end1"), "values": nodes},
              {"name": "End 2", "value": b.get("end2"), "values": nodes}]
        values = self.create(properties=ps, ok=ok, cancel=self.cancel)

    def pinned_support(self, ps):
        def ok():
            new = dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                       type="PinnedSupport", id=values["PinnedSupport"].get())
            self.replace(ps, new)

        ps = [{"name": ps["type"], "value": ps.get("id"), "editable": False},
              {"name": "X", "value": ps.get("x", 0), "editable": True},
              {"name": "Y", "value": ps.get("y", 0), "editable": True}]
        values = self.create(properties=ps, ok=ok, cancel=self.cancel)

    def roller_support(self, rs):
        def ok():
            new = dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                       id=values["RollerSupport"].get(), type="RollerSupport",
                       angle=float(values["Angle"].get()))
            self.replace(rs, new)

        ps = [{"name": rs["type"], "value": rs.get("id"), "editable": False},
              {"name": "X", "value": rs.get("x", 0), "editable": True},
              {"name": "Y", "value": rs.get("y", 0), "editable": True},
              {"name": "Angle", "value": rs.get("angle", 0), "editable": True}]
        values = self.create(properties=ps, ok=ok, cancel=self.cancel)

    def pin_joint(self, pj):
        def ok():
            new = dict(x=float(values["X"].get()), y=float(values["Y"].get()),
                       type="PinJoint", id=values["PinJoint"].get())
            self.replace(pj, new)

        ps = [{"name": pj["type"], "value": pj.get("id"), "editable": False},
              {"name": "X", "value": pj.get("x", 0), "editable": True},
              {"name": "Y", "value": pj.get("y", 0), "editable": True}]
        values = self.create(properties=ps, ok=ok, cancel=self.cancel)

    def force(self, f):
        def ok():
            new = dict(id=values["Force"].get(),
                       value=float(values["Value"].get()),
                       applied_to=values["Applied to"].get(),
                       angle=float(values["Angle"].get()), type="Force")
            self.replace(f, new)

        js = tuple(n["id"] for n in self.__truss.joints) + ("",)
        ps = [
            {"name": f["type"], "value": f.get("id"), "editable": False},
            {"name": "Applied to", "value": f.get("applied_to"), "values": js},
            {"name": "Value", "value": f.get("value", 0), "editable": True},
            {"name": "Angle", "value": f.get("angle", 0), "editable": True}]
        values = self.create(properties=ps, ok=ok, cancel=self.cancel)

    def show_results(self, results):
        ps = [{"name": "Force", "value": "Value", "editable": False}]
        for n, v in results.items():
            ps.append({"name": n, "value": f"{v:>.4f}", "editable": False})
        self.create(properties=ps, ok=self.cancel, cancel=self.cancel)

    def cancel(self):
        self.notify(dict(action="cancel"))

    def replace(self, old, new):
        self.notify(dict(action="replace", old=old, item=new))
