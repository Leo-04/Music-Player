from tkinter import *
from tkinter import ttk

from music.track import TrackData
from UI.tabs.playlist_frame import PlaylistFrame
from widgets.dialogs import showinfo, DialogWindow
from widgets.treelist import TreeList, TreeItem

CROSS = "\u274C"
UNTICKED = "\u2B1C"
TICKED = "\u2705"


class PlayListItem(TreeItem):
    """A simple TreeItem which contains a UI.tabs.playlist_frame.PlayListItem"""

    def __init__(self, tree: TreeList, playlist: "PlayListItem", name: str):
        self.playlist = playlist
        TreeItem.__init__(self, tree, text=name, anchor=W, opened_chr=TICKED, closed_chr=UNTICKED, opened=False)

    # @override
    def update_text(self):
        """Overridden method to make sure text always contains the opened / closed character"""

        try:
            Button.configure(self, text=(self.opened_chr if self.opened else self.closed_chr) + " " + self.text)
        except: pass


class AddToPlaylistWindow(DialogWindow):
    """A simple dialog to add songs to a playlist"""

    playlists_tree: TreeList
    playlists: PlaylistFrame
    tracks: list[TrackData]

    def __init__(self, master, playlists: PlaylistFrame):
        DialogWindow.__init__(self, "Add To Playlists", root=master, width=400, height=500)

        self.playlists = playlists
        self.tracks = []

        self.playlists_tree = TreeList(self)
        playlists_yscroll_bar = ttk.Scrollbar(self, command=self.playlists_tree.yview)
        self.playlists_tree.yscrollcommand = playlists_yscroll_bar.set
        playlists_xscroll_bar = ttk.Scrollbar(self, command=self.playlists_tree.xview, orient=HORIZONTAL)
        self.playlists_tree.xscrollcommand = playlists_xscroll_bar.set

        add = Button(self, text="Add", command=self.do_add)

        self.playlists_tree.grid(row=0, column=0, sticky=NSEW)
        playlists_yscroll_bar.grid(row=0, column=1, sticky=NS)
        playlists_xscroll_bar.grid(row=1, column=0, sticky=EW)
        add.grid(row=2, column=0, columnspan=2, sticky=NSEW, padx=10, pady=10)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.resizable(True, True)

    def close(self):
        """Called when we need to close the dialog"""

        self.withdraw()

    def on_select(self, event: Event):
        """Callback for listview"""

    def toggle(self):
        """Toggles the windows visibility"""

        if self.winfo_ismapped():
            self.close()
        else:
            self.show()

    def show(self):
        """Shows this dialog window"""

        self.playlists_tree.clear()
        playlists = self.playlists.list_playlists()

        queue = [(None, playlists)]
        while len(queue):
            parent, tree = queue.pop(0)
            if parent is None:
                parent = self.playlists_tree

            for name, sub_list in tree:
                if isinstance(sub_list, list):
                    item = TreeItem(self.playlists_tree, text=name, anchor=W, opened=True)
                    queue.append((item, sub_list))
                else:
                    item = PlayListItem(self.playlists_tree, sub_list, name)

                parent.add(item)

        self.geometry("400x400")
        self.position()
        self.deiconify()
        self.update()

    def do_add(self):
        """Callback for a when we click a button to add the songs to the playlists selected"""

        self.close()

        queue = self.playlists_tree.get_items().copy()
        while len(queue):
            item = queue.pop(0)
            if isinstance(item, PlayListItem):
                if item.cget("opened"):
                    self.playlists.add_to_playlist(item.playlist, self.tracks)
            else:
                queue.extend(item.get_items())

    def set_tracks(self, tracks: list[TrackData]):
        """
        Sets the tracks we want to add to the playlists

        All None values are ignored within the list
        If the list (with Nones removed) is not empty, this function calls `self.show()`

        Args:
            tracks: list[TrackData]
                The lists of tracks to be added to a playlist
        """

        self.tracks = [track for track in tracks if track is not None]

        if len(self.tracks):
            self.show()
