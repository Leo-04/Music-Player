import math
from tkinter import *
import bisect


class GridView(Frame):
    values: list
    columns: int
    rows: int
    max_rows: int
    current_row: int
    sort_key: callable
    yscrollcommand: callable
    pad: float

    item_width: int
    item_height: int
    item_padx: int
    item_pady: int

    def __init__(self, master=None, cnf=None, **kwargs):
        self.item_width = 0
        self.item_height = 0
        self.item_padx = 0
        self.item_pady = 0

        Frame.__init__(self, master, self.custom_config(cnf, **kwargs), class_="GridView")
        self.values = list()
        self.columns = 0
        self.rows = 0
        self.max_rows = 0
        self.current_row = 0
        self.sort_key = lambda v: v.winfo_id()
        self.yscrollcommand = lambda *args: None
        self.pad = 0

        self.bind("<Configure>", lambda e: self.on_resize())
        self.bind("<Map>", lambda e: self.on_resize())
        self.bind("<MouseWheel>", self.on_scroll)

    def __len__(self):
        return len(self.values)

    def on_scroll(self, event: Event):
        """Scroll event callback"""

        return self.yview(
            "scroll",
            -1 if event.delta > 0
            else
            1 if event.delta < 0
            else 0,
            "units"
        )

    def custom_config(self, cnf: dict[str, any] | None, **kwargs) -> dict[str, any]:
        """
        Configure custom options

        Parameters:
            cnf: dict | None
            kwargs: dict
                The configurations

        Returns:
            The configurations to pass to tkinter
        """

        if cnf is None:
            cnf = {}
        cnf.update(kwargs)

        if "item_width" in cnf:
            self.item_width = cnf.pop("item_width")

        if "item_height" in cnf:
            self.item_height = cnf.pop("item_height")

        if "item_padx" in cnf:
            self.item_padx = cnf.pop("item_padx")

        if "item_pady" in cnf:
            self.item_pady = cnf.pop("item_pady")

        return cnf

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "item_width" == key:
            return self.item_width

        elif "item_height" == key:
            return self.item_height

        elif "item_padx" == key:
            return self.item_padx

        elif "item_pady" == key:
            return self.item_pady

        else:
            return Frame.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Frame.keys(self) + ["item_width", "item_height", "item_padx", "item_pady"]

    def configure(self, cnf: dict[str, any] | None = None, **kwargs) -> any:
        """Configure this widget"""

        Frame.configure(self, self.custom_config(cnf, **kwargs))

    config = configure

    def add(self, widget: Widget):
        """Add a widget"""

        bisect.insort(self.values, widget, key=self.sort_key)
        widget.bind("<MouseWheel>", self.on_scroll)

        self.update_rows()

    def clear(self):
        """Clears all widgets"""

        self.values.clear()
        self.current_row = 0

        self.update_rows()

    def sort(self, key: callable = None, reverse: bool = False):
        """
        Sorts the widgets
        If key is given, use that to sort widgets going forwards

        Parameters:
            key: callable[any] -> int | None
                The key given to sort the widgets

            reverse: bool
                Weather to reverse the items
        """

        if key is not None:
            self.sort_key = key

        self.values.sort(key=self.sort_key, reverse=reverse)

    def on_resize(self):
        """Callback for resized event"""

        if self.winfo_ismapped() and self.winfo_viewable():
            self.update_rows()
            self.yview("scroll", 0, "units")

    def update_rows(self):
        """
        Recalculates the available row and columns that can be shown
        Updated the viewable region after
        """

        width = self.winfo_width()
        height = self.winfo_height()

        item_full_width = self.item_width + self.item_padx * 2
        item_full_height = self.item_height + self.item_pady * 2
        self.columns = width // item_full_width
        self.rows = (height // item_full_height) + bool(height % item_full_height)
        self.pad = (width % item_full_width) / 2

        if self.columns == 0:
            self.max_rows = 0
        else:
            self.max_rows = math.ceil(len(self.values) / self.columns)

        self.update_display()
        self.update_scrollbar()

    def update_scrollbar(self):
        """Updates the scrollbar"""

        if self.max_rows == 0:
            from_p = 0
            to_p = 1
        else:
            from_p = self.current_row / (self.max_rows + 1)
            to_p = min(self.current_row + self.rows, self.max_rows) / self.max_rows

        self.yscrollcommand(from_p, to_p)

    def yview(self, cmd: str, value: int, *other):
        """
        Callback for scrolling

        Args:
            cmd: str
                The command
            value: int
                The value
            other: *
                Ignored
        """

        self.update_rows()

        if cmd == "moveto":
            value = min(max(float(value), 0), 1)
            self.current_row = int(value * (self.max_rows - 1))

        elif cmd == "scroll":
            value = int(float(value))
            self.current_row = max(min(self.current_row + value, self.max_rows - 1), 0)
        else:
            print(cmd, value, other)
            return

        self.update_rows()

    def update_display(self):
        """Update what widgets are currently being displayed"""

        row = 0
        column = 0

        new_items = set()

        for item in self.values[self.current_row * self.columns:]:
            new_items.add(item)
            item.place(
                x=self.pad + self.item_padx + column * (self.item_width + self.item_padx * 2),
                y=self.item_pady + row * (self.item_height + self.item_pady * 2),
                w=self.item_width,
                h=self.item_height,
            )
            column += 1
            if column >= self.columns:
                row += 1
                column = 0

            if row >= self.rows:
                break

        for item in self.place_slaves():
            if item not in new_items:
                item.place_forget()
#
