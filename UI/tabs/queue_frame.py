import enum
import random
from tkinter import *
from tkinter import ttk

from music.track import TrackData
from widgets.listview import ListView

CROSS = "\u274C"
GRIP = "\u283F"


class QueueFrame(LabelFrame):
    """
    A frame to handle the music queue
    """

    class LoopType(enum.IntEnum):
        """Enum to control loop type"""

        STOP_AT_END = 0
        LOOP_1_SONG = 1
        LOOP_QUEUE = 2

    songs: ListView
    tracks: list[TrackData]
    loop_type: LoopType

    def __init__(self, master=None):
        LabelFrame.__init__(self, master, text="Queue", bd=2)

        self.songs = ListView(
            self, columns=(" ", "Title", "Album", "Artist", "Length", " "),
            auto_expand=(1, 2, 3),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[None, 100, 50, 50], show_drag=[0]
        )
        scroll_bar = ttk.Scrollbar(self, command=self.songs.yview)
        self.songs.yscrollcommand = scroll_bar.set

        self.songs.grid(row=0, column=0, sticky=NSEW)
        scroll_bar.grid(row=0, column=1, sticky=NS)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.songs.bind("<<Selected>>", self.on_select)
        self.songs.bind("<<Drag>>", self.on_drag)
        self.songs.bind("<<Info>>", lambda e: self.winfo_toplevel().event_generate("<<Queue-Info>>", when="tail", x=e.x, y=e.y))

        self.tracks = []
        self.loop_type = QueueFrame.LoopType.LOOP_QUEUE

    def on_drag(self, event: Event):
        """Callback for drag event"""

        column = event.x
        if column != 0:
            return

        from_ = event.y
        to = event.serial

        self.songs.values.insert(to, self.songs.values.pop(from_))

        if self.songs.selected == from_:
            self.songs.un_select()
            self.songs.select(to)

        self.songs.update_all()

    def on_select(self, event: Event):
        """Callback for selected event"""

        index = event.y
        column = event.x

        if column == 2:
            self.winfo_toplevel().event_generate("<<Queue-Album>>", when="tail")
        elif column == 3:
            self.winfo_toplevel().event_generate("<<Queue-Artist>>", when="tail")
        elif column == 5:
            self.songs.values.pop(index)

            if self.songs.selected == index:
                self.songs.un_select()

                if index >= len(self.songs):
                    index -= 1

                if len(self.songs):
                    self.songs.select(index)
                else:
                    self.winfo_toplevel().event_generate("<<Queue-Load>>", when="tail")
            self.config(text=f"Queue({0 if self.songs.get_selected() is None else self.songs.get_selected() + 1}/{len(self.songs)})")
        else:
            self.select(index)
            self.config(text=f"Queue({0 if self.songs.get_selected() is None else self.songs.get_selected() + 1}/{len(self.songs)})")

        self.songs.update_all()

    def loop(self, loop_type: LoopType):
        """Set the loop type"""

        self.loop_type = loop_type

    def clear(self):
        """Clears the queue"""

        self.songs.clear()
        self.tracks.clear()

        self.songs.update_all()

        self.config(text="Queue")

    def select(self, index: int):
        """Select a song by its index in the queue"""

        self.songs.select(index)
        self.songs.show(index)
        self.winfo_toplevel().event_generate("<<Queue-Load>>", when="tail")

        self.config(text=f"Queue({0 if self.songs.get_selected() is None else self.songs.get_selected() + 1}/{len(self.songs)})")

    def add_tracks(self, tracks: list[TrackData]):
        """Adds a list of tracks to the queue"""

        self.songs.clear()
        self.tracks.extend(tracks)

        for song in self.tracks:
            if song is None:
                self.songs.add([GRIP, "ERROR", "ERROR", "ERROR", "--:--:--", CROSS, song])
            else:
                self.songs.add([GRIP, song.title, song.album, song.artist, song.get_len(), CROSS, song])

        self.songs.update_all()

        self.config(text=f"Queue({0 if self.songs.get_selected() is None else self.songs.get_selected() + 1}/{len(self.songs)})")

    def move(self, delta: int = 1, play: bool = True):
        """
        Move the queue's currently selected song by an offset delta
        The actual position is dictated by `self.loop_type`
        For each `self.loop_type`:
         - `LOOP_1_SONG` will not move at all
         - `STOP_AT_END` will stop playback if delta exceeds the queue (will reset to beginning of queue)
         - `LOOP_QUEUE` will wrap delta around to the beginning if delta exceeds the queue

        Parameters:
            delta: int
                The amount to move the selected song by

            play: bool
                Weather to start playing the song that is moved too
        """

        if not len(self.songs):
            return

        if self.loop_type == QueueFrame.LoopType.LOOP_1_SONG:
            delta = 0
        next_pos = self.songs.selected + delta

        if next_pos >= len(self.songs):
            if self.loop_type == QueueFrame.LoopType.STOP_AT_END:
                play = False
                next_pos = 0
            else:
                next_pos = next_pos % len(self.songs)

        self.songs.select(next_pos)
        self.songs.show(next_pos)

        if play:
            self.winfo_toplevel().event_generate("<<Queue-Load>>", when="tail")
        else:
            self.winfo_toplevel().event_generate("<<Queue-LoadNoPlay>>", when="tail")

        self.config(text=f"Queue({0 if self.songs.get_selected() is None else self.songs.get_selected() + 1}/{len(self.songs)})")

    def get_track(self) -> TrackData:
        """Gets the currently selected song"""

        values = self.songs.get(self.songs.selected)
        if values is not None:
            return values[-1]  # last element is track data

    def shuffle(self, do_shuffle: bool):
        """Shuffles or un-shuffles the queue"""

        track = self.get_track()
        if track is None:
            return

        playing_track = track.filename

        self.songs.clear()

        if do_shuffle:
            tracks = random.sample(self.tracks, len(self.tracks))
        else:
            tracks = self.tracks

        for song in tracks:
            self.songs.add([GRIP, song.title, song.album, song.artist, song.get_len(), CROSS, song])

        self.songs.select([track.filename for track in tracks].index(playing_track))

        self.songs.update_all()
