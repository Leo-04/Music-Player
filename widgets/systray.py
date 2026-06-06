from tkinter import PhotoImage, TkVersion

assert TkVersion >= 9, "Needs TK version 9.0 at least for systray command"


class SystemTray:
    """A simple wrapper for Tk 9.0 systray commands"""

    tk: "TkappType"
    image: PhotoImage
    text: str

    @property
    def left_command(self) -> str:
        return "SystemTrayLeftClick" + str(id(self))

    @property
    def right_command(self) -> str:
        return "SystemTrayRightClick" + str(id(self))

    def __init__(
            self,
            image: PhotoImage,
            text: str = "",
            left_click: callable = lambda: None,
            right_click: callable = lambda: None
    ):
        self.tk = image.tk

        self.tk.createcommand(self.left_command, left_click)
        self.tk.createcommand(self.right_command, right_click)

        self.tk.call(
            "tk", "systray", "create",
            "-image", image,
            "-text", text,
            "-button1", self.left_command,
            "-button3", self.right_command,
        )

    def __del__(self):
        try:
            self.tk.deletecommand(self.left_command)
        except:
            pass

        try:
            self.tk.deletecommand(self.right_command)
        except:
            pass

        self.tk.call("tk", "systray", "destroy")

    def configure(self, cnf: dict[str, any] | None = None, **kwargs) -> any:
        """Configure this widget"""

        cnf = (cnf or {}) | kwargs

        cmd = ["tk", "systray", "configure"]

        if "tk" in cnf:
            self.tk = cnf["tk"].pop()
            if hasattr(self.tk, "tk"):
                self.tk = self.tk.tk

        if "text" in cnf:
            cmd.extend(["-text", cnf["text"]])

        if "image" in cnf:
            cmd.extend(["-image", str(cnf["image"])])

        if "left_click" in cnf:
            try:
                self.tk.deletecommand(self.left_command)
            except:
                pass

            self.tk.createcommand(self.left_command, cnf["left_click"])
            cmd.extend(["-button1", self.left_command])

        if "right_click" in cnf:
            try:
                self.tk.deletecommand(self.right_command)
            except:
                pass

            self.tk.createcommand(self.right_command, cnf["right_click"])
            cmd.extend(["-button3", self.right_command])

        return self.tk.call(*cmd)

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "image" == key:
            return self.tk.call("tk", "systray", "configure", "-image")

        elif "text" == key:
            return self.tk.call("tk", "systray", "configure", "-text")

        elif "left_click" == key:
            return self.tk.call("tk", "systray", "configure", "-button1")

        elif "right_click" == key:
            return self.tk.call("tk", "systray", "configure", "-button3")

        elif "tk" == key:
            return self.tk

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return ["tk", "image", "text", "left_click", "right_click"]
