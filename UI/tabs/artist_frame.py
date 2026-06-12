from tkinter import *
from tkinter import ttk
import music.image
from music.indexer import MusicIndexer

from widgets.gridview import GridView
from widgets.listview import ListView

ADD = "\u2795"


class ArtistsFrame(LabelFrame):
    """
    A frame listing all the artists found

    Each artist is a button that can be pressed to show all the albums by the artist.
    """

    indexer: MusicIndexer
    selected_album: str | None
    selected_artist: str | None
    buttons: list[Button]
    artist_buttons: list[Button]

    artists_label: Label
    artists_search: Entry
    artists: GridView
    artists_scroll_bar: ttk.Scrollbar

    albums_search: Entry
    albums: GridView
    albums_scroll_bar: ttk.Scrollbar
    albums_back: Button
    albums_artist_name: Label
    albums_artist_play_all: Button

    songs_back: Button
    songs_album_name: Label
    songs_album_play_all: Button
    songs_album_add_all: Button
    songs_album_add: Button
    songs: ListView
    songs_scroll_bar: ttk.Scrollbar

    def __init__(self, master, indexer: MusicIndexer):
        LabelFrame.__init__(self, master, text="Artists", bd=2)
        self.indexer = indexer
        self.selected_album = None
        self.selected_artist = None
        self.buttons = []
        self.artist_buttons = []

        self.artists_search = Entry(self)
        self.artists_label = Label(self, text="Search:")
        self.artists = GridView(
            self, item_width=300, item_height=75, item_padx=20, item_pady=20
        )
        self.artists_scroll_bar = ttk.Scrollbar(self, command=self.artists.yview)
        self.artists.yscrollcommand = self.artists_scroll_bar.set
        self.artists.sort_key = lambda button: button["text"]

        self.albums_search = Entry(self)
        self.albums_back = Button(self, text="\u25C0 Back", command=self.show_artists)
        self.albums_artist_name = Label(self, width=30)
        self.albums_artist_play_all = Button(
            self, text="\u23F5 Play All",
            command=lambda: self.winfo_toplevel().event_generate("<<Artist-PlayAll>>", when="tail")
        )
        self.albums = GridView(
            self, item_width=300, item_height=350, item_padx=20, item_pady=20
        )
        self.sort_key = lambda v: self.indexer.albums[v["text"]].date
        self.albums_scroll_bar = ttk.Scrollbar(self, command=self.albums.yview)
        self.albums.yscrollcommand = self.albums_scroll_bar.set
        self.albums.sort_key = lambda button: button.data.album

        self.songs_back = Button(self, text="\u25C0 Back", command=lambda: self.show_albums(self.selected_artist))
        self.songs_album_name = Label(self, compound=LEFT)
        self.songs_album_add_all = Button(
            self, text="\u23F5 Add To Queue",
            command=lambda: self.winfo_toplevel().event_generate("<<Artist-Album-AddAll>>", when="tail")
        )
        self.songs_album_play_all = Button(
            self, text="\u23F5 Play All",
            command=lambda: self.winfo_toplevel().event_generate("<<Artist-Album-PlayAll>>", when="tail")
        )
        self.songs_album_add = Button(
            self, text=ADD,
            command=lambda: self.winfo_toplevel().event_generate("<<Artist-Album-Add>>", when="tail")
        )
        self.songs = ListView(
            self, columns=("#", "Title", "Album", "Artist", "Length"),
            auto_expand=(1, 2, 3),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[30, 150, 100, 100, 100]
        )
        self.songs_scroll_bar = ttk.Scrollbar(self, command=self.songs.yview)
        self.songs.yscrollcommand = self.songs_scroll_bar.set

        self.show_artists()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.artists_search.bind("<KeyRelease>", lambda e: self.update_list())
        self.albums_search.bind("<KeyRelease>", lambda e: self.update_album_list(self.albums_search.get().lower()))

        self.songs.bind("<<Selected>>", lambda e: self.winfo_toplevel().event_generate("<<Artist-Selected>>", when="tail", x=e.x, y=e.y))
        self.songs.bind("<<Info>>", lambda e: self.winfo_toplevel().event_generate("<<Artist-Info>>", when="tail", x=e.x, y=e.y))

        self.songs_scroll_bar.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_back.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_name.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_play_all.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_add_all.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_add.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs.bind("<<Back>>", lambda e: self.songs_back.invoke())

        self.albums_scroll_bar.bind("<Button-4>", lambda e: self.albums_back.invoke())
        self.albums_back.bind("<Button-4>", lambda e: self.albums_back.invoke())
        self.albums_artist_name.bind("<Button-4>", lambda e: self.albums_back.invoke())
        self.albums_search.bind("<Button-4>", lambda e: self.albums_back.invoke())
        self.albums_artist_play_all.bind("<Button-4>", lambda e: self.albums_back.invoke())
        self.albums.bind("<Button-4>", lambda e: self.albums_back.invoke())

    def show_artists(self):
        """Shows all artists currently indexed"""

        self.focus_force()

        self.artists_label.grid(row=0, column=0, sticky=NSEW, ipadx=10, ipady=10, pady=(0, 10))
        self.artists_search.grid(row=0, column=1, sticky=NSEW, ipadx=100, ipady=10, pady=(0, 10))
        self.artists.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.artists_scroll_bar.grid(row=1, column=2, sticky=NS)

        self.songs_back.grid_forget()
        self.songs.grid_forget()
        self.songs_scroll_bar.grid_forget()
        self.songs_album_name.grid_forget()
        self.songs_album_play_all.grid_forget()
        self.songs_album_add_all.grid_forget()
        self.songs_album_add.grid_forget()

        self.albums_search.grid_forget()
        self.albums_back.grid_forget()
        self.albums.grid_forget()
        self.albums_scroll_bar.grid_forget()
        self.albums_artist_name.grid_forget()
        self.albums_artist_play_all.grid_forget()

        self.selected_album = None
        self.selected_artist = None

    def show_albums(self, artist: str):
        """
        Shows all albums for a given artist
        If there are no albums, then nothing is shown

        Parameters:
            artist: str
                The name of the artist
        """

        self.focus_force()

        self.songs_back.grid_forget()
        self.songs.grid_forget()
        self.songs_scroll_bar.grid_forget()
        self.songs_album_name.grid_forget()
        self.songs_album_add_all.grid_forget()
        self.songs_album_play_all.grid_forget()
        self.songs_album_add.grid_forget()

        self.artists_label.grid_forget()
        self.artists_search.grid_forget()
        self.artists.grid_forget()
        self.artists_scroll_bar.grid_forget()

        self.albums_back.grid(row=0, column=0, sticky=NSEW)
        self.albums_search.grid(row=0, column=1, sticky=NSEW, padx=10)
        self.albums_artist_name.grid(row=0, column=2, sticky=NSEW, padx=10)
        self.albums_artist_play_all.grid(row=0, column=3, sticky=NSEW)
        self.albums.grid(row=1, column=0, columnspan=4, sticky=NSEW)
        self.albums_scroll_bar.grid(row=1, column=4, sticky=NS)

        self.selected_artist = artist
        self.selected_album = None

        self.albums_artist_name["text"] = artist

        self.update_album_list(None)

    def show_songs(self, album):
        """
        Shows the list of songs from an album
        If the album does not exist, no songs are shown

        Parameters:
            album: str
                The album to show, must be a valid key within `self.indexer`
        """

        self.focus_force()

        self.artists_label.grid_forget()
        self.artists_search.grid_forget()
        self.artists.grid_forget()
        self.artists_scroll_bar.grid_forget()

        self.albums_search.grid_forget()
        self.albums_back.grid_forget()
        self.albums.grid_forget()
        self.albums_scroll_bar.grid_forget()
        self.albums_artist_name.grid_forget()
        self.albums_artist_play_all.grid_forget()

        self.songs_back.grid(row=0, column=0, sticky=NSEW)
        self.songs_album_name.grid(row=0, column=1, sticky=NSEW)
        self.songs_album_play_all.grid(row=0, column=2, sticky=NSEW)
        self.songs_album_add_all.grid(row=0, column=3, sticky=NSEW)
        self.songs_album_add.grid(row=0, column=4, sticky=NSEW)
        self.songs.grid(row=1, column=0, columnspan=5, sticky=NSEW)
        self.songs_scroll_bar.grid(row=1, column=5, sticky=NS)

        self.selected_album = album

        self.songs_album_name["text"] = album

        self.songs.clear()

        self.songs.values = [list(v) for v in self.indexer.index if v.album == self.selected_album]
        self.songs.update_all()

    def update_buttons(self):
        """
        Update all buttons within the album and artist frames
        Instead of creating widgets on the fly, we keep a cache of all widgets,
        Then only display the ones we need
        """

        self.buttons.clear()
        self.artist_buttons.clear()

        for i, album in enumerate(self.indexer.albums):
            button = Button(self.albums, text=album, compound='bottom', anchor="n", width=300, height=350,
                            command=lambda a=album: self.show_songs(a), wraplength=300)
            button.data = self.indexer.albums[album]
            button.bind("<Map>", lambda e, b=button: (setattr(b, "image", music.image.get(b.data.filename, (300, 300))), b.config(image=b.image)))
            button.bind("<Unmap>", lambda e, b=button: (setattr(b, "image", None), b.config(image="")))
            button.bind("<Button-4>", lambda e: self.albums_back.invoke())
            self.buttons.append(button)

        for artist in self.indexer.artists:
            button = Button(self.artists, text=artist, anchor=CENTER, width=300, height=75,
                            command=lambda a=artist: self.show_albums(a), wraplength=300)
            self.artist_buttons.append(button)

        self.update_list()

    def update_album_list(self, search: str | None):
        """Updates the album list by clearing then adding the albums from the selected artist"""

        scroll_index = self.albums.current_row
        self.albums.clear()

        albums = set()
        for song in self.indexer.index:
            if song.artist == self.selected_artist:
                albums.add(song.album)

        for button in [b for b in self.buttons if b["text"] in albums and (search is None or search in b["text"].lower())]:
            self.albums.add(button)

        self.albums.current_row = scroll_index
        self.albums.sort(self.sort_key, reverse=True)
        self.albums.update_rows()

    def update_list(self):
        """Update the list of artists"""

        search = self.artists_search.get().lower()
        scroll_index = self.artists.current_row

        self.artists.clear()

        for button in (self.artist_buttons if (search == "") else [b for b in self.artist_buttons if search in b["text"].lower()]):
            self.artists.add(button)

        self.artists.current_row = scroll_index
        self.artists.update_rows()
        self.config(text=f"Artists({len(self.artists)})")
#
