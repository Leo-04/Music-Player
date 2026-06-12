from tkinter import *
from tkinter import ttk
import music.image
from music.indexer import MusicIndexer

from widgets.gridview import GridView
from widgets.listview import ListView

ADD = "\u2795"


class AlbumsFrame(LabelFrame):
    """
    A frame listing all the albums found

    Each album is a button that can be pressed to show all the songs on the album.
    The image art for an album is loaded in when it is mapped to the screen, and unloaded when unmapped
    This saves alot on memory, but does mean it is constantly loading and unloading images when you scroll.
    """

    indexer: MusicIndexer
    selected_album: str | None
    buttons: list[Button]

    albums_search: Entry
    albums_label: Label
    albums: GridView
    albums_scroll_bar: ttk.Scrollbar

    songs_back: Button
    songs_album_name: Label
    songs_album_play_all: Button
    songs_album_add_all: Button
    songs_album_add: Button
    songs: ListView
    songs_scroll_bar: ttk.Scrollbar

    def __init__(self, master, indexer: MusicIndexer):
        LabelFrame.__init__(self, master, text="Albums", bd=2)
        self.indexer = indexer
        self.selected_album = None
        self.buttons = []

        self.albums_search = Entry(self)
        self.albums_label = Label(self, text="Search:")
        self.albums = GridView(
            self, item_width=300, item_height=350, item_padx=20, item_pady=20
        )
        self.albums_scroll_bar = ttk.Scrollbar(self, command=self.albums.yview)
        self.albums.yscrollcommand = self.albums_scroll_bar.set
        self.albums.sort_key = lambda button: button.data.album

        self.songs_back = Button(self, text="\u25C0 Back", command=self.show_albums)
        self.songs_album_name = Label(self, compound=LEFT)
        self.songs_album_play_all = Button(
            self, text="\u23F5 Play All",
            command=lambda: self.winfo_toplevel().event_generate("<<Album-PlayAll>>", when="tail")
        )
        self.songs_album_add_all = Button(
            self, text="\u23F5 Add To Queue",
            command=lambda: self.winfo_toplevel().event_generate("<<Album-AddAll>>", when="tail")
        )
        self.songs_album_add = Button(
            self, text=ADD,
            command=lambda: self.winfo_toplevel().event_generate("<<Album-Add>>", when="tail")
        )
        self.songs = ListView(
            self, columns=("#", "Title", "Album", "Artist", "Length"),
            auto_expand=(1, 2, 3),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[30, 150, 100, 100, 100]
        )
        self.songs_scroll_bar = ttk.Scrollbar(self, command=self.songs.yview)
        self.songs.yscrollcommand = self.songs_scroll_bar.set

        self.show_albums()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.albums_search.bind("<KeyRelease>", lambda e: self.update_list())

        self.songs.bind("<<Selected>>", lambda e: self.winfo_toplevel().event_generate("<<Album-Selected>>", when="tail", x=e.x, y=e.y))
        self.songs.bind("<<Info>>", lambda e: self.winfo_toplevel().event_generate("<<Album-Info>>", when="tail", x=e.x, y=e.y))

        self.songs_scroll_bar.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_back.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_name.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_play_all.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_add_all.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_album_add.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs.bind("<<Back>>", lambda e: self.songs_back.invoke())

    def show_albums(self):
        """Shows the list of albums"""

        self.songs_back.grid_forget()
        self.songs.grid_forget()
        self.songs_scroll_bar.grid_forget()
        self.songs_album_name.grid_forget()
        self.songs_album_play_all.grid_forget()
        self.songs_album_add.grid_forget()
        self.songs_album_add_all.grid_forget()

        self.albums_label.grid(row=0, column=0, sticky=NSEW, ipadx=10, ipady=10, pady=(0, 10))
        self.albums_search.grid(row=0, column=1, sticky=NSEW, ipadx=100, ipady=10, pady=(0, 10))
        self.albums.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.albums_scroll_bar.grid(row=1, column=2, sticky=NS)

        self.update_list()

        self.selected_album = None

    def show_songs(self, album: str):
        """
        Shows the list of songs from an album
        If the album does not exist, no songs are shown

        Parameters:
            album: str
                The album to show, must be a valid key within `self.indexer`
        """

        self.focus_force()

        self.selected_album = album

        self.albums_label.grid_forget()
        self.albums_search.grid_forget()

        self.songs_back.grid(row=0, column=0, sticky=NSEW)
        self.songs_album_name.grid(row=0, column=1, sticky=NSEW)
        self.songs_album_play_all.grid(row=0, column=2, sticky=NSEW)
        self.songs_album_add_all.grid(row=0, column=3, sticky=NSEW)
        self.songs_album_add.grid(row=0, column=4, sticky=NSEW)
        self.songs.grid(row=1, column=0, columnspan=5, sticky=NSEW)
        self.songs_scroll_bar.grid(row=1, column=5, sticky=NS)

        self.songs_album_name["text"] = album

        self.songs.clear()
        self.songs.values = [list(v) for v in self.indexer.index if v.album == self.selected_album]
        self.songs.update_all()

    def update_buttons(self):
        """
        Update the album buttons
        As we store each button for the albums, we need to recreate them if the index gets updated
        """

        self.buttons.clear()

        for i, album in enumerate(self.indexer.albums):
            button = Button(self.albums, text=album, compound='bottom', anchor="n", width=300, height=330,
                            command=lambda a=album: self.show_songs(a), wraplength=300)
            button.data = self.indexer.albums[album]
            button.bind("<Map>", lambda e, b=button: (setattr(b, "image", music.image.get(b.data.filename, (300, 300))), b.config(image=b.image)))
            button.bind("<Unmap>", lambda e, b=button: (setattr(b, "image", None), b.config(image="")))
            self.buttons.append(button)

        self.update_list()

    def update_list(self):
        """Updates the song list by clearing then adding the albums"""

        search = self.albums_search.get().lower()
        scroll_index = self.albums.current_row

        self.albums.clear()

        for button in (self.buttons if (search == "") else [b for b in self.buttons if search in b["text"].lower()]):
            self.albums.add(button)

        self.albums.current_row = scroll_index
        self.albums.update_rows()
        self.config(text=f"Albums({len(self.albums)})")
#
