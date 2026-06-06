from tkinter import *
from music.player import Player
from widgets.dialogs import DialogWindow

ADD = "\u2795"
PLAY = "\u23F5"


class EqWindow(DialogWindow):
    """
    An equaliser dialog window
    """

    player: Player
    preset: StringVar
    hz60: Scale
    hz170: Scale
    hz310: Scale
    hz600: Scale
    hz1k: Scale
    hz3k: Scale
    hz6k: Scale
    hz12k: Scale
    hz14k: Scale
    hz16k: Scale

    def __init__(self, master, player: Player):
        DialogWindow.__init__(self, "EQ", root=master, width=550, height=650)
        self.player = player

        self.hz60 = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0, bigincrement=10, tickinterval=1)
        self.hz170 = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz310 = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz600 = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz1k = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz3k = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz6k = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz12k = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz14k = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)
        self.hz16k = Scale(self, from_=20, to=-20, resolution=0.1, highlightthickness=0)

        self.img1x1 = PhotoImage(width=1, height=1)

        self.presets = {
            "Flat": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Classical": [0, 0, 0, 0, 0, 0, -7.2, -7.2, -7.2, -9.6],
            "Club": [0, 0, 8.0, 5.6, 5.6, 5.6, 3.2, 0, 0, 0],
            "Dance": [9.6, 7.2, 2.4, 0, 0, -5.6, -7.2, -7.2, 0, 0],
            "Full Bass": [-8.0, 9.6, 9.6, 5.6, 1.6, -4, -8, -10.3, -11.2, -11.2],
            "Full Bass & Treble": [7.2, 5.6, 0, -7.2, -1.8, 1.6, 8, 11.2, 12, 12],
            "Full Treble": [-9.6, -9.6, -9.6, -1, 2.4, 11.2, 16, 16, 16, 16.7],
            "Headphones": [4.8, 11.2, 5.6, -3.2, -2.4, 1.6, 4.8, 9.6, 12.8, 14.4],
            "Large Hall": [10.3, 10.3, 5.6, 5.6, 0, -4.8, -4.8, -4.8, 0, 0],
            "Live": [-1.8, 0, 1, 5.6, 5.6, 5.6, 1, 2.4, 2.4, 2.4],
            "Party": [7.2, 7.2, 0, 0, 0, 0, 0, 0, 7.2, 7.2],
            "Pop": [-1.6, 1.8, 7.2, 8, 5.6, 0, -2.4, -2.4, -1.6, -1.6],
            "Reggae": [0, 0, 0, -5.6, 0, 6.4, 6.4, 0, 0, 0],
            "Rock": [8, 4.8, -5.6, -8, -3.2, 1, 8.8, 11.2, 11.2, 11.2],
            "Ska": [-2.4, -1.8, -1, 0, 1, 5.6, 8.8, 9.6, 11.2, 9.6],
            "Soft": [1.8, 1.6, 0, -2.4, 0, 4, 8, 9.6, 11.2, 12],
            "Soft Rock": [1, 1, 2.4, 0, -4, -5.6, -3.2, 0, 2.4, 8.8],
            "Techno": [8, 5.6, 0, -5.6, -4.8, 0, 8, 9.6, 9.6, 8.8]
        }
        self.preset = StringVar()
        options = list(self.presets)
        dropdown = OptionMenu(self, self.preset, *options, command=self.choose_preset)
        dropdown.config(width=len(max(options, key=len)))
        self.preset.set("Preset")

        Label(self, text="DB   60Hz", width=1, anchor="e").grid(row=1, column=0, sticky=NSEW)
        Label(self, text="170Hz", width=1, anchor="e").grid(row=1, column=1, sticky=NSEW)
        Label(self, text="310Hz", width=1, anchor="e").grid(row=1, column=2, sticky=NSEW)
        Label(self, text="600Hz", width=1, anchor="e").grid(row=1, column=3, sticky=NSEW)
        Label(self, text="1kHz", width=1, anchor="e").grid(row=1, column=4, sticky=NSEW)
        Label(self, text="3kHz", width=1, anchor="e").grid(row=1, column=5, sticky=NSEW)
        Label(self, text="6kHz", width=1, anchor="e").grid(row=1, column=6, sticky=NSEW)
        Label(self, text="12kHz", width=1, anchor="e").grid(row=1, column=7, sticky=NSEW)
        Label(self, text="14kHz", width=1, anchor="e").grid(row=1, column=8, sticky=NSEW)
        Label(self, text="16kHz", width=1, anchor="e").grid(row=1, column=9, sticky=NSEW)

        self.hz60.grid(row=2, column=0, sticky=NSEW)
        self.hz170.grid(row=2, column=1, sticky=NSEW)
        self.hz310.grid(row=2, column=2, sticky=NSEW)
        self.hz600.grid(row=2, column=3, sticky=NSEW)
        self.hz1k.grid(row=2, column=4, sticky=NSEW)
        self.hz3k.grid(row=2, column=5, sticky=NSEW)
        self.hz6k.grid(row=2, column=6, sticky=NSEW)
        self.hz12k.grid(row=2, column=7, sticky=NSEW)
        self.hz14k.grid(row=2, column=8, sticky=NSEW)
        self.hz16k.grid(row=2, column=9, sticky=NSEW)

        dropdown.grid(row=3, column=0, columnspan=4, sticky=NSEW, padx=10, pady=10)
        Button(self, text="Save", command=self.done).grid(row=3, column=4, columnspan=3, sticky=NSEW, padx=10, pady=10)
        Button(self, text="Cancel", command=self.default).grid(row=3, column=7, columnspan=3, sticky=NSEW, padx=10, pady=10)

        for i in range(0, 10):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(2, weight=1)

    def set_sliders(self, eq_values: tuple[float, float, float, float, float, float, float, float, float, float]):
        """
        Set the EQ values

        There are 9 values each a floating point number ranging from -20.0 to 20.0 DB
        the 9 values mpa to these 9 frequency bands: 60hz, 170hz, 310hz, 600hz, 1khz, 3khz, 6khz, 12khz, 14khz, 16khz

        Args:
            eq_values: list[float]
                the EQ values
        """

        self.hz60.set(eq_values[0])
        self.hz170.set(eq_values[1])
        self.hz310.set(eq_values[2])
        self.hz600.set(eq_values[3])
        self.hz1k.set(eq_values[4])
        self.hz3k.set(eq_values[5])
        self.hz6k.set(eq_values[6])
        self.hz12k.set(eq_values[7])
        self.hz14k.set(eq_values[8])
        self.hz16k.set(eq_values[9])

    def choose_preset(self, value: str):
        """Sets a preset"""

        self.preset.set("Preset")
        self.set_sliders(self.presets[value])

    def get_sliders(self) -> tuple[float, float, float, float, float, float, float, float, float, float]:
        """Get the sliders values"""

        return (
            self.hz60.get(),
            self.hz170.get(),
            self.hz310.get(),
            self.hz600.get(),
            self.hz1k.get(),
            self.hz3k.get(),
            self.hz6k.get(),
            self.hz12k.get(),
            self.hz14k.get(),
            self.hz16k.get(),
        )

    def done(self):
        """Button callback, sets the dialog values, this causes the window to close"""

        self.set(self.get_sliders())

    def get(self, force_focus: bool = True, no_move: bool = True) -> tuple[float, float, float, float, float, float, float, float, float, float]:
        """Override from DialogWindow"""

        old_values = self.get_sliders()
        values = DialogWindow.get(self, force_focus, no_move)
        if values is None:
            self.set_sliders(old_values)
            return old_values
        return values
