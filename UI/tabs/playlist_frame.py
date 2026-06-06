from tkinter import *
from tkinter import ttk

from music.track import TrackData, get_track_data_from_filename
from widgets.listview import ListView
from widgets.dialogs import askokcancel, askstring, showinfo
from widgets.treelist import TreeList, TreeItem

CROSS = "\u274C"
ADD = "\u2795"
GRIP = "\u283F"


class PlayListItem(TreeItem):
    """
    A simple TreeItem that is a playlist or a playlist folder

    This depends on if there are any items in `self.list`
    """

    list: list

    def __init__(self, tree: TreeList, name: str):
        self.list = []
        TreeItem.__init__(self, tree, text=name, pady=10, draggable=True, anchor=W, opened=True)

    # @override
    def on_click(self):
        """Overridden callback"""

        if not self.is_playlist():
            TreeItem.on_click(self)
        elif self.command:
            self.command()

    # @override
    def update_text(self):
        """Overridden so that playlists display only their name"""

        if self.is_folder():
            return TreeItem.update_text(self)

        Button.configure(self, text=self.text)

    def is_folder(self):
        """Returns true if this item *CAN* be a folder"""

        return len(self.list) == 0

    def is_playlist(self):
        """Returns true if this item *CAN* be a playlist"""

        return len(self.list) or not len(self.items)

    def path(self) -> list[int]:
        """Gets the playlist's path"""

        current = self
        path = []
        while current.parent is not None:
            path.append(current.parent.items.index(current))
            current = current.parent

        path.append(self.master.items.index(current))

        return path

class PlaylistFrame(LabelFrame):
    """
    A frame to control the playlists
    Allows adding and selecting playlists
    The sub-menu allows:
     - editing of songs positions
     - playing form any position
     - removing songs from playlist
     - deleting the playlist
    """

    playlists_tree: TreeList
    playlists_xscroll_bar: ttk.Scrollbar
    playlists_yscroll_bar: ttk.Scrollbar

    songs_back: Button
    name: Entry
    playlists_delete: Button
    songs: ListView
    songs_scroll_bar: ttk.Scrollbar
    songs_play_all: Button
    songs_add_all: Button
    selected_playlist: PlayListItem | None

    def __init__(self, master=None, playlists: list[tuple[str, list[dict | tuple[...]]]] = None):
        LabelFrame.__init__(self, master, text="Playlists", bd=2)
        if playlists is None:
            playlists = []

        self.selected_playlist = None

        self.playlists_tree = TreeList(self)
        self.playlists_yscroll_bar = ttk.Scrollbar(self, command=self.playlists_tree.yview)
        self.playlists_tree.yscrollcommand = self.playlists_yscroll_bar.set
        self.playlists_xscroll_bar = ttk.Scrollbar(self, command=self.playlists_tree.xview, orient=HORIZONTAL)
        self.playlists_tree.xscrollcommand = self.playlists_xscroll_bar.set

        self.songs_back = Button(self, text="\u25C0 Back", command=self.show_playlists)
        self.name = Entry(self)
        self.songs_play_all = Button(
            self, text="\u23F5 Play All",
            command=lambda: self.winfo_toplevel().event_generate("<<Playlist-PlayAll>>", when="tail")
        )
        self.songs_add_all = Button(
            self, text="\u23F5 Add To Queue",
            command=lambda: self.winfo_toplevel().event_generate("<<Playlist-AddAll>>", when="tail")
        )
        self.playlists_delete = Button(self, text="Delete Playlist", command=self.delete)
        self.songs = ListView(
            self, columns=(" ", "Title", "Album", "Artist", "Length", " "),
            auto_expand=(1, 2, 3),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[None, 100, 50, 50],
            show_drag=[0]
        )
        self.songs_scroll_bar = ttk.Scrollbar(self, command=self.songs.yview)
        self.songs.yscrollcommand = self.songs_scroll_bar.set

        self.playlists_tree.bind("<<Drag>>", self.on_drag)

        self.name.bind("<Return>", lambda e: self.save_name())
        self.name.bind("<Unmap>", lambda e: self.save_name())

        self.songs.bind("<<Selected>>", self.on_song_select)
        self.songs.bind("<<Drag>>", self.on_song_drag)
        self.songs.bind("<<Info>>", lambda e: self.winfo_toplevel().event_generate("<<Playlist-Info>>", when="tail", x=e.x, y=e.y))

        self.songs_scroll_bar.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_back.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.name.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_play_all.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs_add_all.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.playlists_delete.bind("<Button-4>", lambda e: self.songs_back.invoke())
        self.songs.bind("<<Back>>", lambda e: self.songs_back.invoke())

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.load(playlists)
        self.show_playlists()

    def load(self, playlists: list[tuple[str, list[dict | tuple[...]]]]):
        """
        Load playlists

        Parameters:
            playlists: dict[str, list[str]]
                The playlists to load
        """

        self.playlists_tree.clear()

        queue: list[tuple[None | PlayListItem, str, list]]
        queue = [(None, name, list_) for name, list_ in playlists]

        while len(queue):
            parent, name, items = queue.pop(0)
            tree = PlayListItem(self.playlists_tree, name)
            tree.config(command=lambda *_, t=tree: self.show_playlist(t))
            tree.bind("<Button-3>", lambda *_, t=tree: self.rename(t))

            if len(items) and isinstance(items[0], dict):
                tree.list = items
            else:
                for name2, list2 in items:
                    queue.append((tree, name2, list2))

            if parent is None:
                self.playlists_tree.add(tree)
            else:
                parent.add(tree)

        item = TreeItem(self.playlists_tree, text=ADD, pady=10, command=self.new_playlist, relief="flat")
        item.config(activebackground=item.cget("background"))
        self.playlists_tree.add(item)

    def delete(self):
        """
        Delete the currently selected playlist
        If not playlist is selected, nothing will happen
        This will prompt the user before deleting
        """

        if self.selected_playlist is None:
            return

        if askokcancel("Delete?", "Are you sure you want to delete this playlist?", default=False):
            if self.selected_playlist.parent is None:
                self.playlists_tree.remove(self.selected_playlist)
            else:
                self.selected_playlist.parent.remove(self.selected_playlist)

            self.selected_playlist = None
            self.show_playlists()

    def save_name(self):
        """
        Saves the entered name of the playlist
        If the name is the same, nothing will happen
        If the name is the same as another playlist,
         a number is recursively added
        """

        if self.selected_playlist is not None:
            self.selected_playlist.config(text=self.name.get())

    def rename(self, item: PlayListItem):
        name = askstring("Rename folder/playlist", "Rename " + repr(item.cget("text")) + ":", root=self)
        if name:
            item.config(text=name)

    def show_playlists(self):
        """Show the playlists"""

        self.save_name()

        self.songs_back.grid_forget()
        self.songs.grid_forget()
        self.songs_scroll_bar.grid_forget()
        self.playlists_delete.grid_forget()
        self.name.grid_forget()
        self.songs_play_all.grid_forget()
        self.songs_add_all.grid_forget()
        self.name.grid_forget()

        self.playlists_tree.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.playlists_yscroll_bar.grid(row=1, column=2, sticky=NS)
        self.playlists_xscroll_bar.grid(row=2, column=1, sticky=EW)

        self.selected_playlist = None

    def show_playlist(self, playlist: PlayListItem):
        """
        Show the given playlist

        Parameters:
            playlist: PlayListItem
                The playlist item to show tracks for
        """

        if playlist is None or not playlist.is_playlist():
            return

        self.songs_back.grid(row=0, column=0)
        self.name.grid(row=0, column=1, sticky=NSEW)
        self.songs_play_all.grid(row=0, column=2, sticky=NSEW)
        self.songs_add_all.grid(row=0, column=3, sticky=NSEW)
        self.playlists_delete.grid(row=0, column=4, sticky=NSEW)
        self.songs.grid(row=1, column=0, columnspan=5, sticky=NSEW)
        self.songs_scroll_bar.grid(row=1, column=5, sticky=NS)

        self.playlists_tree.grid_forget()
        self.playlists_yscroll_bar.grid_forget()
        self.playlists_xscroll_bar.grid_forget()

        self.name.delete(0, "end")
        self.name.insert(0, playlist.cget("text"))

        self.songs.clear()

        for i, track_data in enumerate(playlist.list):
            track = get_track_data_from_filename(track_data["filename"], i)
            if track is not None:
                self.songs.add([GRIP, track.title, track.album, track.artist, track.get_len(), CROSS, track.filename])
            else:
                self.songs.add([
                    GRIP, track_data["title"], track_data["album"], track_data["artist"], "--:--:--", CROSS, track_data["filename"]
                ])

        self.selected_playlist = playlist

    def on_drag(self, event: Event):
        """Callback for tree drag and drop event"""

        to: PlayListItem
        dragged: PlayListItem
        dragged, to = TreeList.get_dragged_widgets(event)

        if to is None:
            # make sure last item is the "+" to create new playlist
            add_item = self.playlists_tree.pop(-1)
            dragged.config(parent=to)
            self.playlists_tree.add(add_item)
        elif to.is_folder():
            dragged.config(parent=to)
        else:
            playlist = self.new_playlist("Combine these playlists into new folder\nName of folder:")
            if playlist is None:
                return
            # make sure last item is the "+" to create new playlist
            add_item = self.playlists_tree.pop(-1)
            playlist.config(parent=to.parent)
            dragged.config(parent=playlist)
            to.config(parent=playlist)
            self.playlists_tree.add(add_item)

    def on_song_drag(self, event: Event):
        """Event callback for when a song in a playlist is dragged"""

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

    def on_song_select(self, event: Event):
        """Event callback for when a song in a playlist is selected"""

        index = event.y
        column = event.x

        if column == 5:
            self.songs.values.pop(index)

            self.selected_playlist.list.pop(index)

            if self.songs.selected == index:
                if index >= len(self.songs):
                    index -= 1
        else:
            self.winfo_toplevel().event_generate("<<Playlist-Selected>>", when="tail", x=column, y=index)

        self.songs.update_all()

    def add_to_playlist(self, playlist: PlayListItem, tracks: list[TrackData | dict]):
        """
        Adds a list of files to a playlist
        If the playlist name does not exist,
         the playlist will be created

        Parameters:
            playlist: PlayListItem
                The playlist to add to
            tracks: list[TrackData]
                A list of tracks to add
        """

        if not playlist.is_playlist():
            showinfo("Error", "Cannot add songs to a folder", root=self)
            raise Exception("Cannot add songs to a folder")

        for track in tracks:
            if isinstance(track, TrackData):
                track = {
                    "title": track.title,
                    "album": track.album,
                    "artist": track.artist,
                    "filename": str(track.filename),
                }

            playlist.list.append(track)

    def new_playlist(self, prompt="New playlist name:"):
        """Create a new playlist with a prompt"""

        name = askstring("Create New playlist", prompt)
        if name:
            # make sure last item is the "+" to create new playlist
            add_item = self.playlists_tree.pop(-1)
            value = PlayListItem(self.playlists_tree, name)
            value.config(command=lambda: self.show_playlist(value))
            value.bind("<Button-3>", lambda e: self.rename(value))
            self.playlists_tree.add(value)
            self.playlists_tree.add(add_item)

            return value

    def get_playlists(self) -> list[list[str, ...]]:
        """Returns the playlists as serialised data"""

        playlists = []
        queue = [(item, playlists) for item in self.playlists_tree.get_items()[:-1]]
        for item, list_ in queue:
            if item.is_folder():
                new_list = []
                list_.append([item.cget("text"), new_list])
                for next_item in item.get_items():
                    queue.append((next_item, new_list))
            else:
                list_.append([item.cget("text"), item.list])

        return playlists

    def get_playlist_from_path(self, playlist_path: list[int]) -> PlayListItem | None:
        """Gets a playlist from a given index path"""

        playlist_path = playlist_path.copy()
        playlist = self.playlists_tree.get_items()[:-1]
        while len(playlist_path) > 1:
            try:
                playlist = playlist[playlist_path.pop()].get_items()
            except IndexError:
                return None
        try:
            return playlist[playlist_path[-1]]
        except IndexError:
            return None

    def list_playlists(self) -> list[tuple[str, list[PlayListItem | tuple[...]]]]:
        """Lists all the playlists w/ their items"""

        playlist_tree = []

        queue = [(playlist_tree, item) for item in self.playlists_tree.get_items()[:-1]]
        while queue:
            item: PlayListItem
            tree, item = queue.pop(0)
            if item.is_playlist():
                tree.append([item.cget("text"), item])
            else:
                items = []
                tree.append([item.cget("text"), items])
                for next_item in item.get_items():
                    queue.append((items, next_item))

        return playlist_tree

    def update_song_path(self, playlist: PlayListItem, index: int, filename: str):
        """Updates a songs filepath in case of errors"""

        if not playlist.is_playlist():
            showinfo("Error", "Cannot update filename as playlist is a folder", root=self)
            raise Exception("Cannot update filename as playlist is a folder")

        playlist.list[index]["filename"] = str(filename)
