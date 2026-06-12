import re
from tkinter import *
from tkinter import ttk

from music.indexer import Indexer
from music.track import TrackData

from widgets.listview import ListView


class SongsFrame(LabelFrame):
    """A frame to handle all songs"""

    search: Entry
    filter_value: StringVar
    songs: ListView
    indexer: Indexer

    def __init__(self, master, indexer: Indexer):
        LabelFrame.__init__(self, master, text="Songs", bd=2)
        self.indexer = indexer

        self.search = Entry(self)

        self.filter_value = StringVar()
        options = ("All", "Title", "Album", "Artist", "Regex")
        dropdown_filter = OptionMenu(self, self.filter_value, *options, command=lambda *e: self.update_list())
        dropdown_filter.config(width=len(max(options, key=len)))
        self.filter_value.set("All")

        self.songs = ListView(
            self, columns=("#", "Title", "Album", "Artist", "Length"),
            auto_expand=(1, 2, 3),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[30, 150, 100, 100, 100]
        )
        scroll_bar = ttk.Scrollbar(self, command=self.songs.yview)
        self.songs.yscrollcommand = scroll_bar.set

        Label(self, text="Search:").grid(row=0, column=0, sticky=NSEW, ipadx=10, ipady=10, pady=(0, 10))
        self.search.grid(row=0, column=1, sticky=NSEW, ipadx=100, ipady=10, pady=(0, 10))
        dropdown_filter.grid(row=0, column=2, columnspan=2, sticky=NSEW, pady=(0, 10))
        self.songs.grid(row=1, column=0, columnspan=3, sticky=NSEW)
        scroll_bar.grid(row=1, column=3, sticky="NSE")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.search.bind("<KeyRelease>", lambda e: self.update_list())

        self.songs.bind("<<Selected>>", lambda e: self.winfo_toplevel().event_generate("<<Songs-Selected>>", when="tail", x=e.x, y=e.y))
        self.songs.bind("<<Info>>", lambda e: self.winfo_toplevel().event_generate("<<Songs-Info>>", when="tail", x=e.x, y=e.y))

    def get_songs(self) -> list[TrackData]:
        """Return a list of all tracks"""

        return [
            v[-1]  # last element is track data
            for v in self.songs.values
        ]

    def update_list(self):
        """Updates the list of songs"""

        self.songs.clear()

        search = self.search.get().lower()
        if search == "":
            self.songs.values = [list(v) + [v] for v in self.indexer.index]

        elif self.filter_value.get() == "All":
            self.songs.values = [
                list(v) + [v]
                for v in self.indexer.index
                if search in v.title.lower()
                or search in v.artist.lower()
                or search in v.album.lower()
            ]

        elif self.filter_value.get() == "Title":
            self.songs.values = [list(v) + [v] for v in self.indexer.index if search in v.title.lower()]

        elif self.filter_value.get() == "Album":
            self.songs.values = [list(v) + [v] for v in self.indexer.index if search in v.album.lower()]

        elif self.filter_value.get() == "Artist":
            self.songs.values = [list(v) + [v] for v in self.indexer.index if search in v.artist.lower()]

        elif self.filter_value.get() == "Regex":
            try:
                self.songs.values = [
                    list(v) + [v]
                    for v in self.indexer.index
                    if re.findall(search, v.title)
                    or re.findall(search, v.album)
                    or re.findall(search, v.artist)
                ]
            except re.error:
                pass

        self.songs.update_all()
        self.config(text=f"Songs({len(self.songs)})")
