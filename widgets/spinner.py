from tkinter import *

UNICODE_STEPS = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"
ASCII_STEPS = "|/-\\"


class Spinner(Label):
    """A simple spinner widget"""

    wait: int
    steps: str | list | tuple
    stage: int

    def __init__(self, master=None, cnf=None, **kwargs):
        self.wait = 50
        self.steps = UNICODE_STEPS
        self.stage = 0

        cnf = self.custom_config(cnf, **kwargs)

        Label.__init__(self, master, cnf, name="spinner")

        self.bind("<Map>", lambda e: self.update_text())

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

        if "steps" in cnf:
            self.steps = cnf.pop("steps")

        if "wait" in cnf:
            self.wait = cnf.pop("wait")

        if "stage" in cnf:
            self.stage = cnf.pop("stage")

        return cnf

    def configure(self, cnf: dict[str, any] | None = None, **kwargs) -> any:
        """Configure this widget"""

        Label.configure(self, self.custom_config(cnf, **kwargs))

    config = configure

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "steps" == key:
            return self.steps

        elif "wait" == key:
            return self.wait

        elif "stage" == key:
            return self.stage

        else:
            return Label.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Label.keys(self) + ["steps", "wait", "stage"]

    def update_text(self):
        if self.winfo_ismapped():
            self["text"] = self.steps[self.stage]

            self.stage = (self.stage + 1) % len(self.steps)

            self.after(self.wait, self.update_text)
#
