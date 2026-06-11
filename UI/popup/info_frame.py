import platform
import subprocess
from tkinter import *
import music.image
from music.track import TrackData
from widgets.dialogs import showinfo, DialogWindow

ADD = "\u2795"
PLAY = "\u23F5"


class InfoWindow(DialogWindow):
    """
    A window to display details and actions for the current song being played
    """

    track: TrackData | None
    image: PhotoImage
    art: Label
    title: Label
    album: Button
    date: Label
    number: Label
    artist: Button
    length: Label
    file_loc: Button
    play: Button
    add_queue: Button
    add_playlist: Button

    def __init__(self, master):
        DialogWindow.__init__(self, "Song Info", root=master, width=850, height=410, close_on_deselect=False)
        self.track = None

        frame = LabelFrame(self, text="Album Art", width=300, height=300)
        self.image = PhotoImage(width=300, height=300)
        self.art = Label(frame, image=self.image)
        self.art.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=5, rowspan=4)

        frame = LabelFrame(self, text="Title")
        self.title = Label(frame, text="Track Title")
        self.title.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=0, column=1, sticky=NSEW, padx=10, pady=5)

        frame = LabelFrame(self, text="Track Number")
        self.number = Label(frame, text="Track #")
        self.number.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=0, column=2, sticky=NSEW, padx=10, pady=5)

        frame = LabelFrame(self, text="Album")
        self.album = Button(frame, text="Track Album",
                            command=lambda: (self.close(), master.winfo_toplevel().event_generate("<<Info-Album>>", when="tail")))
        self.album.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=1, column=1, sticky=NSEW, padx=10, pady=5)

        frame = LabelFrame(self, text="Length", width=150)
        self.length = Label(frame, text="00:00:00", width=8)
        self.length.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=1, column=2, sticky=NSEW, padx=10, pady=5)

        frame = LabelFrame(self, text="Artist")
        self.artist = Button(frame, text="Track Artist",
                             command=lambda: (self.close(), master.winfo_toplevel().event_generate("<<Info-Artist>>", when="tail")))
        self.artist.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=2, column=1, sticky=NSEW, padx=10, pady=5)

        frame = LabelFrame(self, text="Track Date")
        self.date = Label(frame, text="Date")
        self.date.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=2, column=2, sticky=NSEW, padx=10, pady=5)

        frame = LabelFrame(self, text="File Location")
        self.file_loc = Button(frame, text="C:/", command=self.open_file_loc, anchor=W)
        self.file_loc.pack(fill=BOTH, expand=1, padx=10, pady=10)
        frame.grid(row=3, column=1, columnspan=2, sticky=NSEW, padx=10, pady=5)

        self.play = Button(self, text=PLAY + " Play",
                           command=lambda: (self.close(), master.winfo_toplevel().event_generate("<<Info-Play>>", when="tail")))
        self.play.grid(row=4, column=0, sticky=NSEW, padx=10, pady=5)

        self.add_queue = Button(self, text=" Add To Queue",
                                command=lambda: (self.close(), master.winfo_toplevel().event_generate("<<Info-AddQueue>>", when="tail")))
        self.add_queue.grid(row=4, column=1, sticky=NSEW, padx=10, pady=5)

        self.add_playlist = Button(self, text=ADD,
                                   command=lambda: (self.close(), master.winfo_toplevel().event_generate("<<Info-AddPlaylist>>", when="tail")))
        self.add_playlist.grid(row=4, column=2, sticky=NSEW, padx=10, pady=5)

        # self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)

    def close(self):
        """Hides the window"""

        self.withdraw()
        self.default()

    def open_file_loc(self):
        """Opens the folder the music is located in"""

        if not self.track:
            return

        folder = str(self.track.folder)

        plat = platform.system()
        if plat == "Windows":
            cmd = ['explorer', folder.replace("/", "\\")]
        elif plat == "Linux":
            cmd = ['xdg-open', folder]
        elif plat == "Darwin":
            cmd = ['open', folder]
        else:
            showinfo("Unknown OS", "Don't know what da hell you running this on lol")
            return

        subprocess.Popen(cmd)

    def toggle(self):
        """Toggles the visibility of the window"""

        if self.winfo_viewable():
            self.withdraw()
        else:
            self.position()
            self.deiconify()
            self.update()

    def set_track(self, track: TrackData):
        """
        Sets the current details to be displayed for a given track

        Args:
            track: TrackData
                The track that the details shall be gotten from
        """

        if track is None:
            return

        if self.track is not None and self.track.filename == track.filename:
            return self.toggle()

        self.track = track

        self.image = music.image.get(str(self.track.filename), (300, 300))
        self.art["image"] = self.image

        self.title["text"] = self.track.title
        self.album["text"] = self.track.album
        self.artist["text"] = self.track.artist
        self.number["text"] = str(self.track.number)
        self.length["text"] = self.track.get_len()
        self.date["text"] = str(self.track.date)
        self.file_loc["text"] = str(self.track.filename)

        self.position()
        self.deiconify()
        self.update()
    #
