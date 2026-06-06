from tkinter import *

from UI.player.volume_slider import VolumeSlider

# https://en.wikipedia.org/wiki/Media_control_symbols
OUTPUT = "🎧"  # 🎘#📾#🖸#🔌#🎧
ADD = "\u2795"


class SideButtons(Frame):
    """
    Controls the side buttons that are placed to the right side of the action buttons
    """

    img_1x1: PhotoImage
    volume: VolumeSlider
    add: Button

    def __init__(self, master=None):
        Frame.__init__(self, master, bd=1, relief="ridge")

        self.img_1x1 = PhotoImage(width=1, height=1)

        self.volume = VolumeSlider(self)
        self.add = Button(self, text=ADD, image=self.img_1x1, compound=CENTER, width=51, height=51, font="consolas 30",
                          command=lambda *e: self.winfo_toplevel().event_generate("<<Action-AddCurrentSongToPlaylist>>", when="tail"))

        self.volume.grid(row=0, column=3, pady=12, padx=5, sticky=EW)
        self.add.grid(row=0, column=1, pady=12, padx=5)

        self.columnconfigure(3, weight=1)
#
