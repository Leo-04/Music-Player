import ctypes
from tkinter import Toplevel, LEFT, RIGHT

SM_CXSIZE = 30
SM_CXBORDER = 5

try:  # >= win 8.1
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:  # win 8.0 or less
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        print("Cannot SetProcessDPIAware")

try:
    button_width = ctypes.windll.user32.GetSystemMetrics(SM_CXSIZE)
    bd_width = ctypes.windll.user32.GetSystemMetrics(SM_CXBORDER)
except:
    button_width = bd_width = 0


class TitlebarFrame(Toplevel):
    """A hack to get buttons onto the title bar"""

    side: RIGHT
    padding: int
    root: Toplevel

    def __init__(self, window, cnf=None, **kwargs):
        self.side = RIGHT
        self.padding = 0

        self.root = window.winfo_toplevel()
        Toplevel.__init__(self, self.root, self.custom_config(cnf, **kwargs))
        self.overrideredirect(True)
        self.bind("<FocusIn>", lambda e: ("break", self.root.focus())[0], add="+")
        self.root.bind("<FocusIn>", lambda e: (None, self.show())[0], add="+")
        self.root.bind("<FocusOut>", lambda e: self.hide(), add="+")
        self.root.bind("<Configure>", lambda e: self.update_pos())

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

        if "side" in cnf:
            self.side = cnf.pop("side")

        if "padding" in cnf:
            self.padding = cnf.pop("padding")

        return cnf

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "side" == key:
            return self.side

        elif "padding" == key:
            return self.padding

        else:
            return Toplevel.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Toplevel.keys(self) + ["side", "padding"]

    def show(self):
        """Shows the window"""

        self.overrideredirect(True)
        self.deiconify()

    def hide(self):
        """Hides the window"""

        self.withdraw()
        self.overrideredirect(False)

    def update_pos(self):
        """Event callback to update the windows position and size"""

        if self.root.wm_state() == "iconic":
            return

        offset_y = bd_width + self.root.winfo_y()
        bar_height = abs(self.root.winfo_y() - self.root.winfo_rooty()) - bd_width * 2

        if bar_height <= 0:
            self.hide()
            return

        width = self.winfo_width()
        values = (
            width, bar_height,
            self.root.winfo_rootx() + (
                (
                        self.root.winfo_width() - width - (4 * button_width) - self.padding
                )
                if self.side == RIGHT
                else (
                        button_width + self.padding
                )
            ), offset_y
        )

        if self.root.winfo_width() < (5 * button_width) + width:
            self.hide()
        else:
            self.geometry("%ix%i+%i+%i" % values)
            self.show()
