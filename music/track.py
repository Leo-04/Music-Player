from datetime import datetime
from pathlib import Path
import re
from mutagen import File


class TrackData:
    """
    Basic data for a track
    """

    number: int
    title: str
    album: str
    artist: str
    folder: Path
    filename: Path
    length: int
    date: str

    def __init__(self, track_number: int, title: str, album: str, artist: str, folder: Path, filename: Path, length: int, date: str):
        self.number = track_number
        self.title = title
        self.album = album
        self.artist = artist
        self.folder = folder
        self.filename = filename
        self.length = length
        self.date = date

    def get_len(self) -> str:
        """Gets the length as a formatted string"""

        h = int(self.length) // (60 * 60)
        m = (int(self.length) // 60) % 60
        s = int(self.length) % 60

        return "%02d:%02d:%02d" % (h, m, s)

    def __repr__(self):
        return "[%i]'%s' %s {%s} %s" % (self.number, self.title, self.artist, self.album, self.get_len())

    def __iter__(self):
        return iter([self.number, self.title, self.album, self.artist, self.get_len(), self.filename, self.folder])


def get_track_data_from_filename(file_path: Path | str, index: int = 1) -> TrackData | None:
    """
    Tries to get track data from a file_path

    Tries to get track data from a file
    If we are able to open the tags, but none are present, we use the folder data & `index` as default values

    Args:
        file_path: Pathlike
            The path to the file

        index: int
            the position the file is listed in

    Returns:
        The track data from the file OR None

    """

    file_path = Path(file_path)

    track_number = index
    title = file_path.stem
    album = file_path.parent.name
    artist = "\u2047\uFF1F Unknown Artist \uFF1F\u2047"
    folder = file_path.parent.absolute()
    file_path = file_path.absolute()
    date = ""  # str(datetime.now().year)

    try:
        file = File(file_path, easy=True)
    except Exception as err:
        print("get_track_data_from_filename", file_path, err)
        return None

    if file is None:
        return None

    for tag in ["artist", "albumartist", "author", "Albumartist", "Artist", "AlbumArtist", "Author"]:
        if tag in file:
            artist = ",".join(str(s) for s in file[tag]).title()
            break

    for tag in ["album", "Album"]:
        if tag in file:
            album = ",".join(str(s) for s in file[tag]).title()
            break

    for tag in ["title", "Title"]:
        if tag in file:
            title = ",".join(str(s) for s in file[tag]).title()
            break

    for tag in ["date", "Date", "year", "Year"]:
        if tag in file:
            date = file[tag][0]
            break

    for tag in ["tracknumber", "track", "number", "Tracknumber", "TrackNumber", "Track", "Number", "trck"]:
        if tag in file:
            number = re.search(r'\d+', file[tag][0])
            if number:
                track_number = int(number.group())
                break

    length = file.info.length

    return TrackData(track_number, title, album, artist, folder, file_path, length, date)
