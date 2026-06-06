from tkinter import *

import music.image


class Preview(Frame):
    """
    Contains a preview image and music title, artist and album buttons
    """

    track_name: Button
    artist: Button
    album: Button
    image: PhotoImage
    image_widget: Label

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.track_name = Button(self, text="TRACK NAME", bd=1, relief="ridge", anchor=W,
                                 command=lambda: self.winfo_toplevel().event_generate("<<Action-Info>>", when="tail"))
        self.artist = Button(self, text="ARTIST", width=1, bd=1, relief="ridge", anchor=W,
                             command=lambda: self.winfo_toplevel().event_generate("<<Action-Artist>>", when="tail"))
        self.album = Button(self, text="ALBUM", width=1, bd=1, relief="ridge", anchor=W,
                            command=lambda: self.winfo_toplevel().event_generate("<<Action-Album>>", when="tail"))

        self.image_file = None
        self.image = PhotoImage(width=75, height=75)
        self.image_widget = Label(self, image=self.image, bd=1, relief="ridge")

        self.image_widget.grid(row=0, column=0, rowspan=2, sticky=NSEW)
        self.track_name.grid(row=0, column=1, columnspan=2, sticky=NSEW)
        self.artist.grid(row=1, column=1, sticky=NSEW)
        self.album.grid(row=1, column=2, sticky=NSEW)

        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def set_image(self, music_file: str):
        """
        Sets the preview image from a music file

        Args:
            music_file: PathLike
                A path to the music file to get the image from
        """

        if self.image_file != music_file:
            self.image_file = music_file
            self.image = music.image.get(self.image_file, (75, 75))
            self.image_widget["image"] = self.image

    def set_track_name(self, name: str):
        self.track_name["text"] = name

    def set_artist(self, artist: str):
        self.artist["text"] = artist

    def set_album(self, album: str):
        self.album["text"] = album
#
