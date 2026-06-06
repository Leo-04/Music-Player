import shutil
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

from music.indexer import Indexer
from music.player import Player
from widgets.listview import ListView
from widgets.dialogs import showinfo

CROSS = "\u274C"
ADD = "\u2795"


class SettingsFrame(LabelFrame):
    """A setting frame"""

    indexer: Indexer
    player: Player
    settings: dict
    themes: ListView
    outputs: ListView  # Not used
    indexer_paths: ListView
    ffplay_button: Button

    def __init__(self, master, indexer: Indexer, player: Player, settings: dict):
        LabelFrame.__init__(self, master, text="Settings", bd=2)
        self.player = player
        self.indexer = indexer
        self.settings = settings

        self.themes = ListView(
            self, columns=("Theme",),
            auto_expand=(0,),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[100], height=150, bd=2, relief="ridge"
        )
        theme_scroll_bar = ttk.Scrollbar(self, command=self.themes.yview)
        self.themes.yscrollcommand = theme_scroll_bar.set

        # Not used
        self.outputs = ListView(
            self, columns=("Output Device",),
            auto_expand=(0,),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[100], height=150, bd=2, relief="ridge"
        )
        outputs_scroll_bar = ttk.Scrollbar(self, command=self.outputs.yview)
        self.outputs.yscrollcommand = outputs_scroll_bar.set

        self.indexer_paths = ListView(
            self, columns=("Indexer Paths", " "),
            auto_expand=(0,),
            sashwidth=0,
            sashrelief="raised", title_relief="raised", title_padx=10, title_pady=5,
            widths=[100], height=150, bd=2, relief="ridge"
        )
        indexer_paths_scroll_bar = ttk.Scrollbar(self, command=self.indexer_paths.yview)
        self.indexer_paths.yscrollcommand = indexer_paths_scroll_bar.set

        # eq_button = Button(self, text="EQ\nPreset", command=lambda: self.winfo_toplevel().event_generate("<<Settings-ShowEq>>", when="tail"))
        # indexer_button = Button(self, text="Restart\nIndexer", command=lambda: self.indexer.update_index_thread())
        self.ffplay_button = Button(self, text="FFPlay: " + str(Player.ffplay), command=self.choose_ffplay)

        self.themes.grid(row=0, column=0, sticky=NSEW)
        theme_scroll_bar.grid(row=0, column=1, sticky=NS)
        # self.outputs.grid(row=1, column=0, sticky=NSEW)
        # outputs_scroll_bar.grid(row=1, column=1, sticky=NS)
        self.indexer_paths.grid(row=2, column=0, sticky=NSEW)
        indexer_paths_scroll_bar.grid(row=2, column=1, sticky=NS)
        self.ffplay_button.grid(row=3, column=0, columnspan=3, sticky=NSEW)

        # indexer_button.grid(row=0, column=2, sticky=NSEW)
        # eq_button.grid(row=2, column=2, sticky=NSEW)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.bind("<Map>", lambda e: self.on_show())
        self.outputs.bind("<<Selected>>", self.output_select)
        self.indexer_paths.bind("<<Selected>>", self.indexer_selected)
        self.themes.bind("<<Selected>>", self.theme_select)

    def choose_ffplay(self):
        """Callback for choosing ffplay path"""

        # Check if we can find it
        if shutil.which("ffplay"):
            Player.ffplay = shutil.which("ffplay")
            self.settings["ffplay"] = None
            self.ffplay_button["text"] = "FFplay: " + Player.ffplay
            return

        file = askopenfilename(filetypes=[("Executable", ".exe"), ("All", "*")])
        if file:
            self.ffplay_button["text"] = "FFplay: " + file
            self.settings["ffplay"] = file
            Player.ffplay = file

    def theme_select(self, event: Event):
        """Callback for selecting a theme"""

        if event.y != self.themes.selected:
            self.themes.select(event.y)
            self.settings["theme"] = self.themes.values[self.themes.get_selected()][0]

            showinfo("Theme", "Restarted needed")

    def output_select(self, event: Event):
        """Callback for selecting a output"""

        outputs = self.player.get_outputs()
        self.player.set_output(outputs[event.y][1])

        self.settings["output_device"] = event.y

    def indexer_selected(self, event: Event):
        """Callback for selecting an index path"""

        if event.x == 1:
            self.indexer.paths.pop(event.y)
            self.indexer.update_index_thread()
            self.on_show()

        elif event.y >= len(self.indexer.paths):
            folder = askdirectory()
            if folder:
                self.indexer.add_path(folder)
                self.indexer.update_index_thread()

                self.on_show()

        self.settings["index_paths"] = self.indexer.paths

    def on_show(self):
        """Update values when shown"""

        self.outputs.clear()
        outputs = self.player.get_outputs()
        for output in outputs:
            self.outputs.add(output)
        self.outputs.select([o[1] for o in outputs].index(self.player.get_output()))
        self.outputs.update_all()

        self.indexer_paths.clear()
        for path in self.indexer.paths:
            self.indexer_paths.add([path, CROSS])
        self.indexer_paths.add([ADD, " "])
        self.indexer_paths.update_all()

        self.themes.clear()
        for path in self.settings["themes"]:
            self.themes.add([path])
        self.themes.select(self.settings["themes"].index(self.settings["theme"]))
        self.themes.update_all()

    def get_settings(self) -> dict:
        """Returns the new settings"""

        return {
            "index_paths": [str(s) for s in self.settings["index_paths"]],
            "theme": self.settings["theme"],
            "output_device": self.settings["output_device"],
            "ffplay": Player.ffplay
        }
#
