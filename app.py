# https://www.vertex42.com/ExcelTips/unicode-symbols.html
import json
import os
import sys
import threading
from tkinter import *
from tkinter.filedialog import askopenfilenames

from widgets.notebook import Notebook
from widgets.dialogs import showinfo, askyesno
from widgets.spinner import Spinner
from widgets.style import Style
from widgets.systray import SystemTray
from widgets.tk_menu import TkMenu
from widgets.tooltips import ToolTips
from widgets.wincnf import WindowCnf

from UI.popup.popout_player import PopoutPlayer
from UI.popup.eq import EqWindow
from UI.popup.add_playlist_frame import AddToPlaylistWindow
from UI.popup.info_frame import InfoWindow

from UI.tabs.played_frame import PlayedFrame
from UI.tabs.album_frame import AlbumsFrame
from UI.tabs.artist_frame import ArtistsFrame
from UI.tabs.playlist_frame import PlaylistFrame
from UI.tabs.settings_frame import SettingsFrame
from UI.tabs.songs_frame import SongsFrame
from UI.tabs.queue_frame import QueueFrame

from UI.player.player_frame import PlayerFrame

from music.indexer import MusicIndexer
from music.player import Player as Player
from music.track import get_track_data_from_filename, TrackData

from modules import mediakeys
from modules.dnd import dnd

from resources import *


def dir_path(local_path: str) -> str:
    """
    Finds the path of the current executable file or script

    Parameters:
        local_path: str | PathLike
            The local path to a file or folder

    Returns:
        The full absolute path to the file / folder
    """

    # Check if this script exists
    if os.path.exists(__file__):
        exe = __file__

    # If not, then we have probably been compiled and is located in sys.executable
    else:
        exe = sys.executable

    # Get the path
    return os.path.join(os.path.dirname(exe), local_path)


class App(Tk):
    """
    Main application instance
    """

    # Threading
    media_key_thread: threading.Thread | None

    # Music
    indexer: MusicIndexer
    player: Player

    # UI
    style: Style
    systray: SystemTray
    tips: ToolTips

    indexer_button: Button
    spinner: Spinner

    tabs: Notebook
    player_frame: PlayerFrame

    queue: QueueFrame
    songs: SongsFrame
    albums: AlbumsFrame
    artists: ArtistsFrame
    playlists: PlaylistFrame
    played: PlayedFrame
    settings: SettingsFrame

    info_window: InfoWindow
    add_window: AddToPlaylistWindow
    eq_window: EqWindow
    popout: PopoutPlayer

    def __init__(self, argv: list[str]):
        """
        Creates an application instance

        Parameters:
            argv: list[str]
                The command line arguments
        """

        # Config window
        Tk.__init__(self)

        # Cannot hide as dialogs require window to be shown
        # self.withdraw()  # Hide until we are done loading
        # Instead show splash screen while loading
        # Its black so not to flash bang people
        Label(
            self, name="splashScreen", text="Loading...", font=(None, 50), bg="black", fg="light grey"
        ).place(x=0, y=0, relwidth=1, relheight=1)

        self.minsize(1000, 525)
        self.geometry("1000x525")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.title("Music Player")
        self.cnf = WindowCnf(self)
        image = PhotoImage(data=ICON)
        self.iconphoto(True, image)
        self.style = Style(self)
        self.systray = SystemTray(image, self.title(), self.show, self.show_menu)
        self.media_key_thread = None

        # Load data
        self.check_paths_exist()
        playlists = self.load_playlists()
        settings = self.load_settings()
        self.load_theme_from_settings(settings)
        if settings["ffplay"] is not None:
            Player.ffplay = settings["ffplay"]

        if Player.ffplay is None or not os.path.exists(Player.ffplay):
            if os.path.exists(dir_path("ffmpeg/bin/")):
                Player.ffplay = dir_path("ffmpeg/bin/ffplay")
            else:
                showinfo("Cannot find FFPlay", "Cannot find FFPlay,\nplease update the FFPlay path in settings")
                Player.ffplay = None

        # Create indexer and music player
        self.indexer = MusicIndexer(
            settings["index_paths"],
            on_done=lambda: self.event_generate("<<Indexer-Done>>", when="tail"),
            on_error=lambda err: showinfo("Error", "Indexer error: " + str(err)),
            on_start=lambda: self.event_generate("<<Indexer-Start>>", when="tail")
        )
        self.player = Player(
            on_end=lambda: self.event_generate("<<Action-Next>>", when="tail"),
            on_time=lambda p: self.on_time_update(),
            on_error=lambda error: showinfo("Cannot play", f"Cannot play music\nCheck in settings\nif FFPlay's path is correct\nError: \n{error}")
        )

        # Create UI
        menu = TkMenu(
            self,
            dict(text="Add Files To Queue", hotkey="<Control-Key-o>", command=self.add_files),
            dict(text="EQ Presets", hotkey="<Control-e>", command=lambda: self.player.set_eq(*self.eq_window.get())),
            dict(text="Restart Indexer", hotkey="<Control-i>", command=self.indexer.update_index_thread, side=RIGHT, name="indexer_button"),
            dict(text="About", hotkey="<Control-h>", command=lambda: showinfo("About", ABOUT, height=420, width=400), side=RIGHT),
        )
        self.indexer_button = menu.nametowidget("indexer_button")

        self.tabs = Notebook(self, side=LEFT, panel_size=200, padx=10)
        self.player_frame = PlayerFrame(self, self.player)
        self.tips = ToolTips(self, highlightthickness=1)

        menu.grid(row=0, column=0, sticky=NSEW)
        self.tabs.grid(row=1, column=0, sticky=NSEW)
        self.player_frame.grid(row=2, column=0, sticky=EW)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.queue = QueueFrame(self.tabs)
        self.songs = SongsFrame(self.tabs, self.indexer)
        self.albums = AlbumsFrame(self.tabs, self.indexer)
        self.artists = ArtistsFrame(self.tabs, self.indexer)
        self.playlists = PlaylistFrame(self.tabs, playlists)
        self.played = PlayedFrame(self.tabs, settings["last_played"], self.playlists)
        self.settings = SettingsFrame(self.tabs, self.indexer, self.player, settings)
        self.popout = PopoutPlayer(self, self.player, self.player_frame.actions, self.player_frame.preview)
        self.popout.withdraw()

        self.tabs.add(text="\u2630 Queue", pady=0, frame=self.queue, bd=3)
        self.tabs.add(text="▶ Played", pady=0, frame=self.played, bd=3)
        self.tabs.add(text="\u266B Songs", pady=0, frame=self.songs, bd=3)
        self.tabs.add(text="💽 Albums", pady=0, frame=self.albums, bd=3)
        self.tabs.add(text="👤 Artists", pady=0, frame=self.artists, bd=3)
        self.tabs.add(text="🖿 Playlists", pady=0, frame=self.playlists, bd=3)
        self.tabs.add(text="⚙️ Settings", pady=0, frame=self.settings, side=BOTTOM, bd=3)
        self.tabs.select(1)

        self.spinner = Spinner(self, font=("consolas", 20), bd=1, relief="ridge")
        self.info_window = InfoWindow(self)
        self.add_window = AddToPlaylistWindow(self, self.playlists)
        self.eq_window = EqWindow(self, self.player)

        self.tips.add_widgets({self.spinner: "Indexing files"})

        # was a bit long... so moved to its own function
        self.bind_all_events()

        # Need to call these after we set up the bindings as they call events
        self.eq_window.set_sliders(settings["eq_values"])
        self.player.set_eq(*settings["eq_values"])
        self.player_frame.side.volume.set(settings["volume"])
        self.playlists.load(playlists)
        self.indexer.update_index_thread()

        # Parse command line arguments
        self.play_tracks_from_argv(argv, 0)

        dnd(self, self.play_tracks_from_argv)

    def play_tracks_from_argv(self, argv: list[str], index: int | None = None):
        """Play tracks from the command line"""

        argv_files = self.load_tracks_from_list(argv)
        for track in argv_files:
            self.played.add(str(track.filename), "File")

        self.play_tracks(index, argv_files)

        self.show()
        self.focus_set()
        self.focus_force()

    def load_tracks_from_list(self, files: list[str]) -> list[TrackData]:
        """
        Load a set of tracks from a list of files
        If a file cannot be loaded, a error message is shown

        Parameters:
            files: list[str | PathLike]
                The list of files to attempt to load
        """

        tracks = []

        for i, file in enumerate(files):
            data = get_track_data_from_filename(file)
            if data is None:
                showinfo("Error", "Cannot open music file: " + file, root=self)
            else:
                tracks.append(data)

        return tracks

    def add_files(self):
        """
        Callback to add files
        Will ask the user for more than one file to select and playback
        """

        files = askopenfilenames(filetypes=[("Music files", " ".join(MusicIndexer.EXTS)), ("Any", "*")])
        if not files:
            return

        tracks = self.load_tracks_from_list(list(files))
        for track in tracks:
            self.played.add(str(track.filename), "File")

        self.play_tracks(None, tracks)

    def get_tracks_in_album(self, album: str) -> list[TrackData]:
        """Gets all the tracks in the given album"""

        return [
            track
            for track in self.indexer.index
            if track.album == album
        ]

    def play_tracks(self, start_index: int | None, tracks: list[TrackData]):
        """
        Adds a list of tracks to the queue

        Parameters:
            start_index: int | None
                The index to start playing from
                if it is None, it won't clear the current tracks on the queue

            tracks: list[TrackData]
                A list of tracks
        """

        if len(tracks):
            if start_index is not None:
                self.queue.clear()
                if start_index < 0:
                    start_index = 0
                elif start_index >= len(tracks):
                    start_index = len(tracks) - 1

            self.queue.add_tracks(tracks)

            if start_index is not None:
                self.queue.select(start_index)
                self.tabs.select(0)

    def play_album(self, start_index: None | int, album: str):
        """Plays all songs on an album"""

        self.played.add(album, "Album")

        self.play_tracks(start_index, self.get_tracks_in_album(album))

    def play_artist(self, start_index: None | int, artist: str):
        """Plays all songs by an artist"""

        self.played.add(artist, "Artist")

        self.play_tracks(start_index, [
            track
            for track in self.indexer.index
            if track.artist == artist
        ])

    def play_track(self, play: bool, track: TrackData):
        """Plays a singular track"""

        self.played.add((track.title, track.album, track.artist, str(track.filename)), "Song")

        self.play_tracks(0 if play else None, [track])

    def get_playlist_tracks(self, start_index: None | int, playlist_path: list[int]) -> tuple[int | None, list[TrackData] | None]:
        """
        Gets all the tracks for a given playlist

        Parameters:
            start_index: None | int
                The start index or None
                This is decremented any time an item cannot be found and is after this index

            playlist_path: list[int]
                The path to the playlist

        Returns:
            The new starting index
            and The list of tracks loaded
        """

        tracks = []

        i = 0
        playlist = self.playlists.get_playlist_from_path(playlist_path)
        if playlist is None:
            showinfo("Error", "Playlist does not exitst, was it deleted?")
            return None, None

        for track_data in playlist.list:
            track = get_track_data_from_filename(track_data["filename"], i)
            if track is None:
                possible_tracks: list[TrackData] = [
                    track
                    for track in self.indexer.index
                    if track.title == track_data["title"]
                    if track.album == track_data["album"]
                    if track.artist == track_data["artist"]
                ]

                if len(possible_tracks) == 0:
                    showinfo(
                        "Track cannot be found",
                        f"Error: The track\n'{track_data['title']}' from album '{track_data['album']}' by '{track_data['artist']}'\n"
                        "Cannot be found, please update the indexer settings or re-add the song to the playlist"
                    )
                    if start_index is not None and start_index > i:
                        start_index -= 1

                    continue
                elif len(possible_tracks) > 1:
                    showinfo(
                        "Too many tracks can be found",
                        f"Error: The track\n'{track_data['title']}' from album '{track_data['album']}' by '{track_data['artist']}'\n"
                        "Can be found multiple times, please replace it with the correct one\nDefaulting to first found track"
                    )
                    possible_tracks = [possible_tracks[0]]

                if len(possible_tracks) == 1:
                    if (askyesno(
                            "Track found",
                            f"Warning: The track\n'{track_data['title']}' from album '{track_data['album']}' by '{track_data['artist']}'\n"
                            "Was found via the indexer, the original file may have been moved\n"
                            "\n"
                            "Would you like to replace it with the new one?",
                            default=False
                    )):
                        self.playlists.update_song_path(playlist, i, str(possible_tracks[0].filename))
                    track = possible_tracks[0]

            tracks.append(track)

            i += 1

        return start_index, tracks

    def play_playlist(self, start_index: None | int, playlist: list[int]):
        """Plays all songs on a playlist"""

        start_index, tracks = self.get_playlist_tracks(start_index, playlist)
        if tracks is None:
            tracks = []
        else:
            self.played.add(playlist, "Playlist")

        self.play_tracks(start_index, tracks)

    def on_time_update(self):
        """
        Callback for when each second is passed
        Used to update visuals relating to time / seekbar
        """

        track = self.queue.get_track()
        self.player_frame.preview.set_album("ALBUM" if track is None else track.album)
        self.player_frame.preview.set_artist("ARTIST" if track is None else track.artist)
        self.player_frame.preview.set_track_name("TRACK NAME" if track is None else track.title)
        self.player_frame.preview.set_image(None if track is None else track.filename)
        self.player_frame.seeker.update_text()
        self.popout.update_info()

    def on_indexer_start(self):
        """
        Callback for when the indexer has started
        """

        if self.indexer_button["state"] == "normal":
            self.indexer_button.config(state="disabled"),
            self.spinner.place(relx=1, rely=0, anchor=NE)

    def on_indexer_done(self):
        """
        Callback for when the indexer has finished parsing files
        """

        self.songs.update_list()
        self.albums.update_buttons()
        self.artists.update_buttons()
        self.spinner.place_forget()

        self.indexer_button.config(state="normal"),
        focused_widget = self.focus_get()
        if focused_widget is None:
            focused_widget = self

        focused_widget.focus_force()

    def show_menu(self):
        """Event callback for systray right click"""
        menu = Menu(self, tearoff=0, bd=0, relief="flat")

        if self.winfo_ismapped():
            menu.add_command(label="Hide", command=self.withdraw, underline=0)
        else:
            menu.add_command(label="Show", command=self.show, underline=0)
        if self.popout.state() == "withdrawn":
            menu.add_command(label="Pop-Out", command=self.popout.show)
        else:
            menu.add_command(label="Pop-In", command=self.popout.close)
        menu.add_separator()

        # Removed because of having global key hooks
        '''
        if self.player.is_paused():
            menu.add_command(label="Play", command=lambda: self.event_generate("<<Action-Play>>"), underline=0)
        else:
            menu.add_command(label="Pause", command=lambda: self.event_generate("<<Action-Pause>>"), underline=0)
        
        menu.add_separator()
        menu.add_command(label="Next", command=lambda: self.event_generate("<<Action-Next>>"), underline=0)
        menu.add_command(label="Prev", command=lambda: self.event_generate("<<Action-Prev>>"), underline=0)
        menu.add_separator()
        '''

        menu.add_command(label="Close", command=self.close)

        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def show(self):
        """Shows the window"""

        self.deiconify()
        self.update()

    def close(self):
        """Close the window and save values"""

        # Hide to make it look like we closed faster
        self.media_key_thread = None
        self.withdraw()
        self.popout.withdraw()
        del self.systray

        try:
            json.dump({
                "volume": self.player_frame.side.volume.get(),
                "eq_values": self.eq_window.get_sliders(),
                "last_played": self.played.get_last_played(),
                **self.settings.get_settings()
            }, open(dir_path("data/settings.json"), "w"))
        except Exception as err:
            self.show()
            showinfo("Error", "Could not save settings\nError: " + str(err))

        playlists = self.playlists.get_playlists()
        try:
            json.dump(playlists, open(dir_path("data/playlists.json"), "w"))
        except Exception as err:
            self.show()
            showinfo("Error", "Could not save playlists\nError: " + str(err))

        self.player.stop()
        self.player.destroy()
        self.destroy()

    def check_paths_exist(self):
        """
        Check if the application's data paths exist
        Creates data and themes folders if they do not exist
        Creates the 3 basic themes if they do not exist

        If any error occurs, then an information window is shown
        """

        if not os.path.exists(dir_path("data/")):
            try:
                os.mkdir(dir_path("data/"))
                os.mkdir(dir_path("data/themes"))
            except Exception as err:
                showinfo("Error", "Cannot create data folder\nError: " + str(err), root=self)

        # Check for each default theme
        try:
            if not os.path.exists(dir_path("data/themes/system")):
                with open(dir_path("data/themes/system"), "w") as fp:
                    fp.write(SYSTEM_THEME)

            if not os.path.exists(dir_path("data/themes/light")):
                with open(dir_path("data/themes/light"), "w") as fp:
                    fp.write(LIGHT_THEME)

            if not os.path.exists(dir_path("data/themes/dark")):
                with open(dir_path("data/themes/dark"), "w") as fp:
                    fp.write(DARK_THEME)

        except Exception as err:
            showinfo("Error", "Cannot create themes folder\nError: " + str(err), root=self)

    def load_settings(self) -> dict:
        """
        Attempts to load the settings for the data path
        If any error occurs, then an information window is shown

        Returns:
            The settings
        """

        # Load settings
        try:
            settings = json.load(open(dir_path("data/settings.json")))

            # Error if format is wrong
            if (
                    type(settings["theme"]) != str
                    or type(settings["output_device"]) != str
                    or type(settings["volume"]) != int
                    or (type(settings["index_paths"]) != list
                        and any([type(val) != str for val in settings["index_paths"]]))
                    or (type(settings["last_played"]) != list
                        and any([type(val) != str for val in settings["last_played"]]))
                    or (type(settings["eq_values"]) != list
                        and any([type(settings["eq_values"][i]) != int for i in range(10)]))
                    or (type(settings["ffplay"]) != str
                        and settings["ffplay"] is not None)
            ):
                raise TypeError()
        except Exception as err:
            settings = {
                "theme": "dark",
                "index_paths": ["C:\\users\\" + os.getlogin() + "\\music" if os.name == "nt" else "~/music"],
                "output_device": "",
                "volume": 100,
                "eq_values": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "last_played": [],
                "ffplay": None,
            }

            self.load_theme_from_settings(settings)
            showinfo("Error", "Could not load settings\nError: " + str(err), root=self)

        return settings

    def load_playlists(self) -> list[tuple[str, list[dict | tuple[...]]]]:
        # Load Playlists
        try:
            playlists = json.load(open(dir_path("data/playlists.json")))

            # Error if format is wrong
            if (
                    not isinstance(playlists, list)
                    and any([
                not isinstance(key, str)
                and not isinstance(stuff, list)
                for key, stuff in playlists
            ])
            ):
                raise TypeError()
        except Exception as err:
            showinfo("Error", "Could not load playlists\nError: " + str(err), root=self)
            playlists = {}

        return playlists

    def load_theme_from_settings(self, settings: dict):
        """
        Load the currently selected theme from settings,
        Default to dark mode if any error occurs

        Parameters:
            settings: dict
                The applications settings loaded from a json file
        """

        # Load style
        settings["themes"] = []
        try:
            settings["themes"] = os.listdir(dir_path("data/themes/"))
            path = dir_path("data/themes/" + settings["theme"])
            self.style.load(open(path).read(), path)
        except Exception as err:
            self.style.load(DARK_THEME, "DarkTheme")
            showinfo("Error", f"Could not load theme {'`'}{settings['theme']}{'`'}\nError: \n{err}")

        # Configure window styles
        try:
            if self.style.get("WindowTitle", "foreground"):
                self.cnf.fg = self.style.get("WindowTitle", "foreground")
            if self.style.get("*WindowTitle", "background"):
                self.cnf.bg = self.style.get("*WindowTitle", "background")
            if self.style.get("WindowTitle", "highlightColor"):
                self.cnf.bd = self.style.get("WindowTitle", "highlightColor")

            self.cnf.corner = WindowCnf.SQUARE
        except Exception as err:
            # These can go wrong in so many more ways, just ignore the error
            print("ERROR:", err)

    def bind_all_events(self):
        """
        Binds all events for application control
        """

        # ====================== Hotkeys ======================

        def play_pause():
            if self.player.is_paused():
                self.event_generate("<<Action-Play>>", when="tail")
            else:
                self.event_generate("<<Action-Pause>>", when="tail")

        def scrub_left():
            self.player.set_pos(self.player.get_pos() - (5 / self.player.length()))

        def scrub_right():
            self.player.set_pos(self.player.get_pos() + (5 / self.player.length()))

        def increase_volume():
            self.player_frame.side.volume.set(self.player_frame.side.volume.get() + 1)

        def decrease_volume():
            self.player_frame.side.volume.set(self.player_frame.side.volume.get() - 1)

        def if_text_widget_is_not_focused(callback, *args, **kwargs) -> callable:
            """Returns an event function that will on call `callback` if a text like widget is not focused"""

            def func(_):
                if (
                    not (issubclass(type(self.focus_get()), (Text, Entry, Scale)))
                    and (type(self.focus_get()) not in (Text, Entry, Scale))
                ):
                    callback(*args, **kwargs)

            return func


        self.bind("<Key-space>", if_text_widget_is_not_focused(play_pause))
        self.bind("<Key-Left>", if_text_widget_is_not_focused(scrub_left))
        self.bind("<Key-Right>", if_text_widget_is_not_focused(scrub_right))
        self.bind("<Key-Up>", if_text_widget_is_not_focused(increase_volume))
        self.bind("<Key-Down>", if_text_widget_is_not_focused(decrease_volume))

        self.bind("<Key-l>", if_text_widget_is_not_focused(self.player_frame.actions.do_loop))
        self.bind("<Key-h>", if_text_widget_is_not_focused(self.player_frame.actions.do_shuffle))
        self.bind("<Key-greater>", if_text_widget_is_not_focused(self.event_generate, "<<Action-Next>>", when="tail"))
        self.bind("<Key-period>", if_text_widget_is_not_focused(self.event_generate, "<<Action-Next>>", when="tail"))
        self.bind("<Key-less>", if_text_widget_is_not_focused(self.event_generate, "<<Action-Prev>>", when="tail"))
        self.bind("<Key-comma>", if_text_widget_is_not_focused(self.event_generate, "<<Action-Prev>>", when="tail"))
        self.bind("<Key-plus>", if_text_widget_is_not_focused(self.event_generate, "<<Action-AddCurrentSongToPlaylist>>", when="tail"))
        self.bind("<Key-equal>", if_text_widget_is_not_focused(self.event_generate, "<<Action-AddCurrentSongToPlaylist>>", when="tail"))
        self.bind("<Key-q>", if_text_widget_is_not_focused(self.tabs.select, 0))
        self.bind("<Key-r>", if_text_widget_is_not_focused(self.tabs.select, 1))
        self.bind("<Key-s>", if_text_widget_is_not_focused(self.tabs.select, 2))
        self.bind("<Key-b>", if_text_widget_is_not_focused(self.tabs.select, 3))
        self.bind("<Key-a>", if_text_widget_is_not_focused(self.tabs.select, 4))
        self.bind("<Key-p>", if_text_widget_is_not_focused(self.tabs.select, 5))
        self.bind("<Key-i>", if_text_widget_is_not_focused(self.tabs.select, 6))
        self.bind("<Key-t>", if_text_widget_is_not_focused(self.event_generate, "<<Action-Info>>", when="tail"))


        # ====================== Actions ======================

        def previous_song(_: Event):
            if self.queue.get_track() is None:
                return

            if (
                    self.queue.get_track().length * self.player.get_pos() <= 5
                    and self.queue.get_track()
            ):
                self.queue.move(-1, not self.player.is_paused())
            else:
                self.player.set_pos(0)

        def next_song(_: Event):
            if self.queue.get_track() is None:
                return

            self.queue.move(1, not self.player.is_paused())

        def pause(_: Event):
            if self.queue.get_track() is None:
                return

            self.player.pause()
            self.player_frame.actions.set_play(False)

        def play(_: Event):
            if self.queue.get_track() is None:
                return

            self.player.play()
            self.player_frame.actions.set_play(True)

        def show_info():
            if self.queue.get_track() is not None:
                self.info_window.set_track(self.queue.get_track())
            else:
                self.tabs.select(2)

        def show_album(_: Event):
            if self.queue.get_track() is not None:
                self.albums.show_songs(self.queue.get_track().album)

            self.tabs.select(3)

        def show_artist(_: Event):
            if self.queue.get_track() is not None:
                self.artists.show_albums(self.queue.get_track().artist)

            self.tabs.select(4)

        self.bind("<<Action-Shuffle>>", lambda e: (self.queue.shuffle(True)))
        self.bind("<<Action-NoShuffle>>", lambda e: (self.queue.shuffle(False)))
        self.bind("<<Action-Prev>>", previous_song)
        self.bind("<<Action-Next>>", next_song)
        self.bind("<<Action-Pause>>", pause)
        self.bind("<<Action-Play>>", play)
        self.bind("<<Action-Repeat>>", lambda e: (self.queue.loop(QueueFrame.LoopType.LOOP_QUEUE)))
        self.bind("<<Action-Repeat1>>", lambda e: (self.queue.loop(QueueFrame.LoopType.LOOP_1_SONG)))
        self.bind("<<Action-NoRepeat>>", lambda e: (self.queue.loop(QueueFrame.LoopType.STOP_AT_END)))
        self.bind("<<Action-AddCurrentSongToPlaylist>>", lambda e: (self.add_window.set_tracks([self.queue.get_track()])))
        self.bind("<<Action-Info>>", lambda e: show_info())
        self.bind("<<Action-Album>>", show_album)
        self.bind("<<Action-Artist>>", show_artist)
        self.bind("<<Action-Mute>>", lambda e: (self.player.set_volume(0)))
        self.bind("<<Action-SetVolume>>", lambda e: (self.player.set_volume(e.x)))

        if sys.platform.startswith('linux') or os.name == "nt":
            self.bind("<<MediaKey-PlayPause>>", lambda e: self.player_frame.actions.do_play())
            self.bind("<<MediaKey-Stop>>", lambda e: self.event_generate("<<Action-Pause>>"))
            self.bind("<<MediaKey-Next>>", lambda e: self.event_generate("<<Action-Next>>"))
            self.bind("<<MediaKey-Previous>>", lambda e: self.event_generate("<<Action-Prev>>"))

            self.media_key_thread = threading.Thread(
                target=mediakeys.media_key_thread,
                args=(self, lambda: self.media_key_thread),
                daemon=True
            )
            self.media_key_thread.start()
        else:
            # Default to window bindings
            self.bind("<XF86AudioPlay>", lambda e: self.player_frame.actions.do_play())
            self.bind("<XF86AudioStop>", lambda e: self.event_generate("<<Action-Pause>>"))
            self.bind("<XF86AudioNext>", lambda e: self.event_generate("<<Action-Next>>"))
            self.bind("<XF86AudioPrev>", lambda e: self.event_generate("<<Action-Prev>>"))
            # Don't need because the OS will mute itself:
            # self.bind("<XF86AudioMute>", lambda e: self.event_generate("<<Action-Mute>>"))

        # ====================== Info ======================

        def info_show_album(_: Event):
            self.albums.show_songs(self.info_window.track.album)
            self.tabs.select(3)

        def info_show_artist(_: Event):
            self.artists.show_albums(self.info_window.track.artist)
            self.tabs.select(4)

        self.bind("<<Info-Album>>", info_show_album)
        self.bind("<<Info-Artist>>", info_show_artist)
        self.bind("<<Info-Play>>", lambda e: (self.play_track(True, self.info_window.track)))
        self.bind("<<Info-AddQueue>>", lambda e: (self.play_track(False, self.info_window.track)))
        self.bind("<<Info-AddPlaylist>>", lambda e: (self.add_window.set_tracks([self.info_window.track])))

        # ====================== Albums ======================

        def album_song_selected(event: Event):
            if event.x == 2:
                self.albums.show_songs(self.albums.selected_album)
                self.tabs.select(3)
            elif event.x == 3:
                tracks = self.get_tracks_in_album(self.albums.selected_album)
                self.artists.show_albums(tracks[event.y].artist)
                self.tabs.select(4)
            else:
                self.play_album(event.y, self.albums.selected_album)

        self.bind("<<Album-PlayAll>>", lambda e: (self.play_album(0, self.albums.selected_album)))
        self.bind("<<Album-AddAll>>", lambda e: (self.play_album(None, self.albums.selected_album)))
        self.bind("<<Album-Add>>", lambda e: (self.add_window.set_tracks(self.get_tracks_in_album(self.albums.selected_album))))
        self.bind("<<Album-Selected>>", album_song_selected)
        self.bind("<<Album-Info>>", lambda e: (self.info_window.set_track(self.get_tracks_in_album(self.albums.selected_album)[e.y])))

        # ====================== Artist ======================

        def album_song_selected(event: Event):
            if event.x == 2:
                self.albums.show_songs(self.artists.selected_album)
                self.tabs.select(3)
            elif event.x == 3:
                tracks = self.get_tracks_in_album(self.artists.selected_album)
                self.artists.show_albums(tracks[event.y].artist)
                self.tabs.select(4)
            else:
                self.play_album(event.y, self.artists.selected_album)

        self.bind("<<Artist-PlayAll>>", lambda e: (self.play_artist(0, self.artists.selected_artist)))
        self.bind("<<Artist-Album-PlayAll>>", lambda e: (self.play_album(0, self.artists.selected_album)))
        self.bind("<<Artist-Album-AddAll>>", lambda e: (self.play_album(None, self.artists.selected_album)))
        self.bind("<<Artist-Album-Add>>", lambda e: (self.add_window.set_tracks(self.get_tracks_in_album(self.artists.selected_album))))
        self.bind("<<Artist-Selected>>", album_song_selected)
        self.bind("<<Artist-Info>>", lambda e: (self.info_window.set_track(self.get_tracks_in_album(self.artists.selected_album)[e.y])))

        # ====================== Playlist ======================

        self.bind("<<Playlist-PlayAll>>", lambda e: (self.play_playlist(0, self.playlists.selected_playlist.path())))
        self.bind("<<Playlist-AddAll>>", lambda e: (self.play_playlist(None, self.playlists.selected_playlist.path())))

        def get_playlist_track(index: None | int) -> None | TrackData:
            index, tracks = self.get_playlist_tracks(index, self.playlists.selected_playlist.path())
            if tracks is None or index is None:
                return None

            return tracks[index]

        def playlist_song_selected(event: Event):
            if event.x == 2:
                self.albums.show_songs(get_playlist_track(event.y).album)
                self.tabs.select(3)
            elif event.x == 3:
                self.artists.show_albums(get_playlist_track(event.y).artist)
                self.tabs.select(4)
            else:
                self.play_playlist(event.y, self.playlists.selected_playlist.path())

        self.bind("<<Playlist-Selected>>", playlist_song_selected)
        self.bind("<<Playlist-Info>>", lambda e: (self.info_window.set_track(get_playlist_track(e.y))))

        # ====================== Queue ======================

        def load_the_queue(_: Event):
            if self.queue.get_track() is None:
                self.player.pause()
            else:
                self.player.load(str(self.queue.get_track().filename), self.queue.get_track().length)
                self.player_frame.actions.set_play(self.queue.get_track() is not None)

        def load_the_queue_but_dont_play(_: Event):
            self.player.stop()
            if self.queue.get_track() is not None:
                self.player.load(str(self.queue.get_track().filename), self.queue.get_track().length, play=False)

            self.player.set_pos(0)
            self.player.pause()
            self.player_frame.actions.set_play(False)
            self.on_time_update()

        def queue_album_selected(event: Event):
            self.albums.show_songs(self.queue.get_tracks()[event.y].album)
            self.tabs.select(3)

        def queue_artist_selected(event: Event):
            self.artists.show_albums(self.queue.get_tracks()[event.y].artist)
            self.tabs.select(4)

        self.bind("<<Queue-Info>>", lambda e: (self.info_window.set_track(self.queue.get_tracks()[e.y])))
        self.bind("<<Queue-Load>>", load_the_queue)
        self.bind("<<Queue-LoadNoPlay>>", load_the_queue_but_dont_play)
        self.bind("<<Queue-Album>>", queue_album_selected)
        self.bind("<<Queue-Artist>>", queue_artist_selected)

        # ====================== Songs ======================

        def songs_selected(event: Event):
            if event.x == 2:
                self.albums.show_songs(self.songs.get_songs()[event.y].album)
                self.tabs.select(3)
            elif event.x == 3:
                self.artists.show_albums(self.songs.get_songs()[event.y].artist)
                self.tabs.select(4)
            else:
                self.play_track(True, self.songs.get_songs()[event.y])

        self.bind("<<Songs-Selected>>", songs_selected)
        self.bind("<<Songs-Info>>", lambda e: (self.info_window.set_track(self.songs.get_songs()[e.y])))

        # ====================== Settings ======================
        # self.bind("<<Settings-ShowEq>>", lambda e: (
        #     self.player.set_eq(*self.eq_window.get())
        # ))

        # ====================== Played ======================

        def played_selected(event: Event):
            data, type_ = self.played.get_last_played()[event.y]

            if type_ == "Album":
                self.play_album(0, data)

            elif type_ == "Artist":
                self.play_artist(0, data)

            elif type_ == "Playlist":
                self.play_playlist(0, data)

            elif type_ == "Song":
                filename = data[-1]
                self.play_track(True, self.load_tracks_from_list([filename])[0])

            elif type_ == "File":
                self.play_tracks(0, self.load_tracks_from_list([data]))
                self.played.add(data, type_)

            else:
                print("Invalid type:", type_)

        def played_info(event: Event):
            data, type_ = self.played.get_last_played()[event.y]

            if type_ == "Album":
                self.albums.show_songs(data)
                self.tabs.select(3)

            elif type_ == "Artist":
                self.artists.show_albums(data)
                self.tabs.select(4)

            elif type_ == "Playlist":
                self.playlists.show_playlist(self.playlists.get_playlist_from_path(data))
                self.tabs.select(5)

            elif type_ == "Song":
                self.info_window.set_track(self.load_tracks_from_list([data[-1]])[0])

            elif type_ == "File":
                self.info_window.set_track(self.load_tracks_from_list([data])[0])

            else:
                print("Invalid type:", type_)

        self.bind("<<Played-Selected>>", played_selected)
        self.bind("<<Played-Info>>", played_info)

        # ====================== Indexer ======================

        self.bind("<<Indexer-Start>>", lambda e: self.on_indexer_start())
        self.bind("<<Indexer-Done>>", lambda e: self.on_indexer_done())
