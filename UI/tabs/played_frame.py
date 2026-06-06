from tkinter import *
from tkinter import ttk

from UI.tabs.playlist_frame import PlaylistFrame
from widgets.listview import ListView

ADD = "\u2795"
CROSS = "\u274C"


class PlayedFrame(LabelFrame):
    """A frame to show the recently played items"""

    last_played: list[tuple[str | tuple[str, ...], str]]
    songs: ListView
    playlists: PlaylistFrame

    def __init__(self, master, last_played: list[tuple[str, str]], playlists: PlaylistFrame):
        LabelFrame.__init__(self, master, text="Recently-Played", bd=2)
        self.last_played = last_played
        self.playlists = playlists

        # Type can be: Song, Album, Artist, Playlist, File
        self.songs = ListView(
            self, columns=("#", "Name", "Type", " "),
            auto_expand=(1,),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[None, 150, 100]
        )
        songs_scroll_bar = ttk.Scrollbar(self, command=self.songs.yview)
        self.songs.yscrollcommand = songs_scroll_bar.set

        self.songs.grid(row=1, column=0, sticky=NSEW)
        songs_scroll_bar.grid(row=1, column=1, sticky=NS)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.songs.bind("<<Selected>>", self.on_select)
        self.songs.bind("<<Info>>", lambda e: self.winfo_toplevel().event_generate("<<Played-Info>>", when="tail", x=e.x, y=e.y))

        self.update_shown()

    def on_select(self, event: Event):
        if event.x == 3:
            self.last_played.pop(event.y)
            self.update_shown()
        else:
            self.winfo_toplevel().event_generate("<<Played-Selected>>", when="tail", x=event.x, y=event.y)

    def get_last_played(self) -> list[tuple[str | tuple[str, ...] | list[int], str]]:
        """Return the last played list"""

        return self.last_played

    def add(self, name: str | tuple[str, ...] | list[int], type_: str):
        self.last_played.insert(0, (name, type_))

        self.update_shown()

    def update_shown(self):
        """Update the list of shown played"""

        self.songs.clear()
        i = 1
        for name, type_ in self.last_played:
            if type_ == "Playlist":
                playlist = self.playlists.get_playlist_from_path(name)
                if playlist is None:
                    string_name = "ERROR"
                else:
                    string_name = playlist.cget("text")
            elif type_ == "Song":
                string_name = name[0]
            else:
                string_name = str(name)

            self.songs.add((str(i), string_name, type_, CROSS))
            i += 1

        self.songs.update_all()
        if i != 1:
            self.config(text=f"Recently-Played({i - 1})")
        else:
            self.config(text=f"Recently-Played")


#
