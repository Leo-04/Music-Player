import ctypes
from tkinter import *
from tkinter.font import Font

CLOSED = chr(9205)
OPENED = chr(9207)


class TreeItem(Button):
    """A simple item for the TreeList"""

    parent: "TreeItem" = None
    items: list["TreeItem"] = None
    show: bool = True
    opened: bool = False
    text: str = ""
    opened_chr: chr = OPENED
    closed_chr: chr = CLOSED
    command: callable = None
    draggable: bool = False

    master: "TreeList"

    def __init__(self, tree: "TreeList", cnf: dict[str, ...] | None = None, **kwargs):
        if self.items is None:
            self.items = []

        cnf = self.custom_config((cnf or {}) | kwargs)
        Button.__init__(self, tree, cnf, command=self.on_click)

        self.bind("<MouseWheel>", lambda event: tree.event_generate(
            "<MouseWheel>",
            state=event.state,
            delta=event.delta,
            x=event.x,
            y=event.y
        ))
        self.bind("<Enter>", lambda e: self.config(state="active"))
        self.bind("<Leave>", lambda e: self.config(state="normal"))
        self.bind("<B1-Motion>", lambda e: tree.event_generate("<<DragWidget>>", x=self.winfo_x() + e.x, y=self.winfo_y() + e.y))
        self.bind("<ButtonRelease-1>", lambda e: tree.event_generate("<<DragEnd>>", x=self.winfo_x() + e.x, y=self.winfo_y() + e.y))

        self.update_text()

    def on_click(self):
        """Callback for when this item is clicked"""

        self.opened = not self.opened
        self.update_text()
        self.master.update_items()

        if self.command:
            self.command()

    def update_text(self):
        """Updates the text of this widget"""

        try:
            Button.configure(self, text=(
                ((self.opened_chr if self.opened else self.closed_chr) + " ")
                if len(self.items) else ""
             ) + self.text)
        except:
            pass

    def custom_config(self, cnf: dict[str, ...]) -> dict[str, ...]:
        if "items" in cnf:
            self.items = list(cnf.pop("items"))

        if "text" in cnf:
            self.text = str(cnf.pop("text"))
            self.update_text()

        if "command" in cnf:
            self.command = cnf.pop("command")

        if "show" in cnf:
            self.show = cnf.pop("show")

        if "opened" in cnf:
            self.opened = cnf.pop("opened")

        if "opened_chr" in cnf:
            self.opened_chr = cnf.pop("opened_chr")

        if "closed_chr" in cnf:
            self.closed_chr = cnf.pop("closed_chr")

        if "parent" in cnf:
            if self.parent is None:
                self.master.remove(self)
            else:
                self.parent.remove(self)

            self.parent = cnf.pop("parent")

            if self.parent is None:
                self.master.add(self)
            else:
                self.parent.add(self)

            self.master.update_items()

        if "draggable" in cnf:
            self.draggable = cnf.pop("draggable")

        return cnf

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "items" == key:
            return self.items

        elif "text" == key:
            return self.text

        elif "command" == key:
            return self.command

        elif "show" == key:
            return self.show

        elif "opened" == key:
            return self.opened

        elif "opened_chr" == key:
            return self.opened_chr

        elif "closed_chr" == key:
            return self.closed_chr

        elif "parent" == key:
            return self.parent

        elif "draggable" == key:
            return self.draggable

        else:
            return Button.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Button.keys(self) + ["items", "show", "opened", "opened_chr", "closed_chr", "parent", "draggable"]

    def configure(self, cnf: dict[str, any] | None = None, **kwargs) -> any:
        """Configure this widget"""

        return Button.configure(self, self.custom_config((cnf or {}) | kwargs))

    config = configure

    def add(self, item: "TreeItem"):
        """Adds a sub-item to this widget, making itself its parent"""

        item.parent = self
        self.items.append(item)
        self.update_text()
        self.master.update_items()

    def pop(self, index: int):
        """Removes a sub-item by index"""

        self.items.pop(index)
        self.update_text()
        self.master.update_items()

    def remove(self, widget: "TreeItem"):
        """Removes a sub-item by value"""

        self.items.remove(widget)
        self.update_text()
        self.master.update_items()

    def get_height(self) -> int:
        """Gets the wanted height for this item"""

        return self.cget("bd")*2 + self.cget("pady")*2 + Font(font=self.cget("font")).metrics("linespace")

    def get_items(self) -> list["TreeItem"]:
        """Returns all shown items"""

        return [
            item
            for item in self.items
            if item.show
        ]

    def __len__(self):
        """Gets the length of sub-times will always be >= 1 as includes itself in the length"""

        return sum(((len(item) + 1) if item.opened else 1) for item in self.get_items())


class TreeList(Frame):
    """A list itme that can contain items sorted in a tree like structure"""

    indent_size: int | None = None
    items: list[TreeItem] = None

    yscrollcommand: callable = lambda *args: None
    xscrollcommand: callable = lambda *args: None
    viewable: int = 0
    index: int = 0
    max_indent: int = 0
    indent: int = 0
    dragged: TreeItem | None = None
    drag_window: Toplevel
    drag_window_item: Button

    def __init__(self, master: Misc | None = None, cnf: dict | None = None, **kwargs):
        Frame.__init__(self, master, (cnf or {}) | kwargs)

        if self.items is None:
            self.items = []

        self.drag_window = Toplevel(self)
        self.drag_window.withdraw()
        self.drag_window.overrideredirect(True)
        self.drag_window_item = Button(self.drag_window)
        self.drag_window_item.pack(fill=BOTH, expand=1)

        self.bind("<Configure>", lambda e: self.update_items())
        self.bind("<MouseWheel>", self.on_scroll)
        self.bind("<<DragWidget>>", self.on_drag)
        self.bind("<<DragEnd>>", self.on_end_drag)

    def on_end_drag(self, event: Event):
        """Callback for when an item has been dropped"""

        if self.dragged is None:
            return

        self.drag_window.withdraw()

        new_widget = self.winfo_containing(self.winfo_rootx() + event.x, self.winfo_rooty() + event.y)
        if new_widget != self and (
            new_widget is None
            or new_widget == self.dragged
            or not isinstance(new_widget, TreeItem)
            or not new_widget.draggable
        ):
            self.dragged = None
            return

        if new_widget == self:
            new_widget = None

        # Pointer fuckery
        x = id(self.dragged)
        y = id(new_widget)
        xx = x & 0x7F_FF_FF_FF
        rx = (x & (0x7F_FF_FF_FF << 31)) >> 31
        yy = y & 0x7F_FF_FF_FF
        ry = (y & (0x7F_FF_FF_FF << 31)) >> 31
        # If your wondering why 31 bits and not 32
        # it's because TCL does not have unsigned ints
        # Because pointers don't use most the high half of the bits,
        # it's fine to just lose 2 bits
        # Once the "data" filed of events works,
        # then we can replace it with that

        self.event_generate("<<Drag>>", x=xx, rootx=rx, y=yy, rooty=ry)
        self.dragged = None

    @staticmethod
    def get_dragged_widgets(event: Event) -> tuple[TreeItem, TreeItem | None]:
        """This is needed to unpack the evil pointers stored as integers"""

        xx = event.x
        rx = event.x_root

        yy = event.y
        ry = event.y_root

        x = xx | (rx << 31)
        y = yy | (ry << 31)

        # Even more pointer fuckery
        dragged = ctypes.cast(x, ctypes.py_object).value
        new_widget = ctypes.cast(y, ctypes.py_object).value

        return dragged, new_widget

    def on_drag(self, event: Event):
        """Callback for when an item has been dragged"""

        if self.dragged is None:
            widget = self.winfo_containing(self.winfo_rootx() + event.x, self.winfo_rooty() + event.y)
            if widget is None or not isinstance(widget, TreeItem):
                return

            if widget.draggable:
                self.dragged = widget

                for key in self.dragged.keys():
                    if key in self.drag_window_item.keys():
                        self.drag_window_item.configure({key: widget.cget(key)})

                self.drag_window.deiconify()
                self.drag_window.update()

        if self.dragged is not None:
            self.drag_window.geometry("{w}x{h}+{x}+{y}".format(
                x=event.x_root + 1,
                y=event.y_root + 1,
                w=self.dragged.winfo_width(),
                h=self.dragged.winfo_height(),
            ))

    def update_scrollbars(self):
        """Update the scrollbars"""

        if len(self.items) == 0:
            from_p = 0
            to_p = 1
        else:
            max_index = sum(((len(item) + 1) if item.opened else 1) for item in self.items)

            from_p = self.index / max_index
            to_p = (self.index + self.viewable) / max_index

        self.yscrollcommand(from_p, to_p)

        if len(self.items) == 0 or self.max_indent == 0:
            from_p = 0
            to_p = 1
        else:
            from_p = self.indent / (self.max_indent + (self.winfo_width() / self.indent_size))
            to_p = (self.indent + (self.winfo_width() / self.indent_size)) / (self.max_indent + (self.winfo_width() / self.indent_size))

        self.xscrollcommand(from_p, to_p)

    def on_scroll(self, event: Event):
        """Scroll event callback"""

        return (self.xview if (event.state & 1) else self.yview)(
            "scroll",
            -1 if event.delta > 0
            else
            1 if event.delta < 0
            else 0,
            "units"
        )

    def yview(self, cmd: str, value: int, *_):
        """Event callback for scrolling"""

        max_index = sum(len(item) + 1 if item.opened else 1 for item in self.items) + 1

        if cmd == "moveto":
            value = min(max(float(value), 0), 1)
            self.index = int(value * max_index)

        elif cmd == "scroll":
            value = int(float(value))
            self.index += value

        else:
            print(cmd, value, _)
            return

        self.index = max(min(self.index, max_index - self.viewable - 1), 0)

        self.update_items()

    def xview(self, cmd: str, value: int, *_):
        """Event callback for scrolling"""

        max_value = (self.max_indent + (self.winfo_width() / self.indent_size))

        if cmd == "moveto":
            value = min(max(float(value), 0), 1)
            self.indent = int(max_value * value)

        elif cmd == "scroll":
            value = int(float(value))
            self.indent += value

        else:
            print(cmd, value, _)
            return

        self.indent = max(min(self.indent, self.max_indent), 0)

        self.update_items()

    def update_items(self):
        """Update all the items shown in the TreeList"""

        for item in self.place_slaves():
            item.place_forget()

        start_index = 0
        height = 0
        items = [(0, item) for item in self.items]
        self.viewable = 0
        self.max_indent = 0
        while len(items) and height < self.winfo_height():
            indent, item = items.pop(0)
            if item.show and item.opened:
                for itm in item.get_items()[::-1]:
                    items.insert(0, (indent + 1, itm))

            if start_index >= self.index:
                if self.indent_size is None:
                    self.indent_size = item.get_height()

                self.viewable += 1
                item.place(
                    x=(indent - self.indent) * self.indent_size,
                    y=height,
                    w=(self.indent - indent) * self.indent_size,
                    h=item.get_height(),
                    relw=1,
                )

                height += item.get_height()

            start_index += 1
            self.max_indent = max(self.max_indent, indent)

        if height > self.winfo_height():
            self.viewable -= 1

        self.update_scrollbars()

    def add(self, item: TreeItem):
        """Adds an item to the TreeList, making the parent be the TreeList"""

        item.parent = None
        self.items.append(item)
        self.update_items()

    def remove(self, item: TreeItem):
        """Removes an item from the TreeList by value"""

        self.items.remove(item)
        self.update_items()

    def pop(self, index: int) -> TreeItem:
        """Removes an item from the TreeList by index"""

        item = self.items.pop(index)
        self.update_items()

        return item

    def clear(self):
        """Remove all items from the TreeList"""

        for widget in self.winfo_children():
            if widget != self.drag_window:
                widget.destroy()

        self.items.clear()
        self.update_items()

    def get_items(self) -> list[TreeItem]:
        """Returns all items"""

        return self.items


def main():
    """Demo of TreeList used to make it"""

    def on_drag(event: Event):
        dragged, to = tree.get_dragged_widgets(event)
        dragged.config(parent=to)

    root = Tk()
    tree = TreeList(root)
    tree.bind("<<Drag>>", on_drag)
    for i in range(10):
        item = TreeItem(
            tree,
            text="Hello " + str(i),
            font=(None, 20),
            anchor=W,
            activebackground="light grey",
            draggable=True
        )
        for j in range(10):
            item2 = TreeItem(
                tree,
                text="World " + str(i) + "," + str(j),
                font=(None, 20),
                anchor=W,
                activebackground="light grey",
                draggable=True
            )
            for k in range(10):
                item3 = TreeItem(
                    tree,
                    text="! " + str(i) + "," + str(j) + "," + str(k),
                    font=(None, 20),
                    anchor=W,
                    activebackground="light grey",
                    draggable=True,
                    command=lambda: print("hello")
                )
                item2.add(item3)
            item.add(item2)

        tree.items.append(item)
    tree.update_items()

    yscroll_bar = Scrollbar(root, command=tree.yview)
    tree.yscrollcommand = yscroll_bar.set
    yscroll_bar.pack(side=RIGHT, fill=Y)

    xscroll_bar = Scrollbar(root, command=tree.xview, orient=HORIZONTAL)
    tree.xscrollcommand = xscroll_bar.set
    xscroll_bar.pack(side=BOTTOM, fill=X)

    tree.pack(side=LEFT, fill=BOTH, expand=1)

    mainloop()


if __name__ == '__main__':
    main()
