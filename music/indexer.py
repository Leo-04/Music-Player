import traceback
from pathlib import Path
from threading import Thread
import bisect

from music.track import get_track_data_from_filename, TrackData


class Indexer:
    """
    Indexes files based on file extension

    Looks in a set of folders (and their sub folders) for any file with a matching ext.
    It inserts the values into a list using a sort key.
    Callback functions are used to indicate when certain processes are preformed.
    """

    exts: list[str] | set[str] | tuple[str, ...]
    paths: list[Path]
    index: list
    on_start: callable
    on_add: callable
    on_done: callable
    on_error: callable
    sort_key: callable

    def __init__(
        self,
        exts: list[str] | set[str] | tuple[str, ...],
        paths: list[Path | str] | None = None,
        on_start: callable = lambda: None,
        on_add: callable = lambda d = None: None,
        on_done: callable = lambda: None,
        on_error: callable = lambda e: print(traceback.format_exc()),
        sort_key: callable = lambda v: v
    ):
        """
        Args:
            exts: list[str]
                A iterable object of file extensions

            paths: iterable[PathLike] | None
                A iterable object of file paths

            paths: iterable[PathLike] | None
                A iterable object of file paths

            on_start: callable
                A callable object that gets called whenever the indexer starts

            on_add: callable
                A callable object that gets called whenever the indexer adds a new entry, the new value is passed as an argument

            on_error: callable
                A callable object that gets called whenever a exception occurs whilst indexing, the error is passed as an argument
        """

        self.exts = exts

        if paths is None:
            self.paths = list()
        else:
            self.paths = [Path(p) for p in paths]

        self.index = []

        self.on_start = on_start
        self.on_add = on_add
        self.on_done = on_done
        self.on_error = on_error
        self.sort_key = sort_key

    def get_normalized_paths(self) -> list[Path]:
        """
        Returns paths that need to be indexed

        This function copies all the index paths and removes duplicate paths so we don't check the same directory more than once
        It also removes a folder if it's a sub folder of another folder, as we will check it anyway.

        Returns:
            A list of non-duplicate paths
        """

        paths = list(self.paths)
        paths.sort(key=lambda p: len(p.absolute().as_posix()))

        i = len(paths) - 1
        while i > 0:
            for path in paths[0:i]:
                if path in paths[i].parents:
                    paths.pop(i)
                    break
            i -= 1

        return paths

    def add_path(self, p: Path | str):
        """
        Adds a path to the indexer

        Args:
            p: PathLike
                A path to a folder
        """

        path = Path(p)

        if path not in self.paths:
            self.paths.append(path)

    def add_data(self, file_path: Path, index: int):
        """
        Adds data to the indexer

        Gets data by calling `self.get_data(...)` and adds this data to a sorted list

        Args:
            file_path: Path
                A path to the file to be added

            index: int
                The index position it appeared when listing the file
        """

        data = self.get_data(file_path, index)

        if data is None:
            return

        if self.on_add(data) is None:
            bisect.insort(self.index, data, key=self.sort_key)

    def update_index_thread(self):
        """
        Calls `self.update_index()` in an thread
        """

        Thread(target=self.update_index).start()

    def update_index(self) -> int:
        """
        Updates the index

        Goes through each folder and adds the found files
        """

        try:
            self.on_start()
        except Exception as err:
            print("Cannot callback on_start:", err)

        self.index.clear()

        paths = set(self.get_normalized_paths())

        while len(paths):
            path = next(iter(paths))

            index = 1
            try:
                for file_path in path.iterdir():
                    if file_path.suffix.lower() in self.exts:
                        self.add_data(file_path, index)
                        index += 1
                    elif file_path.is_dir():
                        paths.add(file_path)

            except Exception as err:
                try:
                    self.on_error(err)
                except Exception as err:
                    print("Cannot callback on_error:", err)

            paths.remove(path)

        try:
            self.on_done()
        except Exception as err:
            print("Cannot callback on_done:", err)

        return len(self.index)

    def get_data(self, file_path: Path, index: int) -> any:
        """
        Gets the data associated with the file

        You can override this function to change what data is loaded from a file.
        By default, it just indexes the folder the file is located, the position of the file in the folder, and the file path.

        Args:
            file_path: Path
                A string or path like object to the file

            index: int
                The index position it appeared when listing the file

        Returns:
            The data associated with the file
        """

        return file_path.parent.absolute(), index, file_path

    def sort(self, sort_key: callable):
        """
        Sets the sort key

        Sets the sort key AND sorts the current indexed data with that key

        Args:
            sort_key: callable
                A callable that is passed as a sort key
        """

        self.sort_key = sort_key
        self.index.sort(key=self.sort_key)


class MusicIndexer(Indexer):
    """
    Indexes music files

    Looks in a set of folders (and their sub folders) for any file with a matching music ext.
    It inserts the values into a list using a sort key.
    Callback functions are used to indicate when certain processes are preformed.
    """

    artists: set
    albums: dict[str, TrackData]

    EXTS = {
        ".3gp", ".aa", ".aac", ".aax", ".act", ".aiff", ".alac", ".amr", ".ape", ".au", ".awb", ".dss", ".dvf",
        ".flac", ".gsm", ".iklax", ".ivs", ".m4a", ".m4b", ".m4p", ".mmf", ".movpkg", ".mp3", ".mpc", ".msv",
        ".nmf", ".ogg, .oga, .mogg", ".opus", ".ra, .rm", ".raw", ".rf64", ".sln", ".tta", ".voc", ".vox", ".wav",
        ".wma", ".wv", ".webm", ".8svx", ".cda"
    }

    def __init__(
            self,
            paths: list[Path | str] | None = None,
            on_start: callable = lambda: None,
            on_add: callable = lambda d = None: None,
            on_done: callable = lambda: None,
            on_error: callable = lambda e: print(traceback.format_exc())):
        """
        Args:
            paths: iterable[PathLike] | None
                A iterable object of file paths

            paths: iterable[PathLike] | None
                A iterable object of file paths

            on_start: callable
                A callable object that gets called whenever the indexer starts

            on_add: callable
                A callable object that gets called whenever the indexer adds a new entry, the new value is passed as an argument

            on_error: callable
                A callable object that gets called whenever a exception occurs whilst indexing, the error is passed as an argument
        """

        Indexer.__init__(self, MusicIndexer.EXTS, paths, on_start, on_add, on_done, on_error, lambda track: (track.album, track.number, track.artist))

        self.artists = set()
        self.albums = {}

    def get_data(self, file_path, index) -> TrackData:
        """
        Gets the data associated with the file

        Gets track data on a music file

        Args:
            file_path: Path
                A string or path like object to the file

            index: int
                The index position it appeared when listing the file

        Returns:
            Tack data for a file
        """

        track = get_track_data_from_filename(file_path, index)

        self.artists.add(track.artist)
        if track.album not in self.albums or track.number < self.albums[track.album].number:
            self.albums[track.album] = track

        return track
#
