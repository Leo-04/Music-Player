from tkinter import *

from UI.player.action_buttons import ActionButtons
from UI.player.side_buttons import SideButtons
from UI.player.preview import Preview
from UI.player.seeker import Seeker
from music.player import Player


class PlayerFrame(Frame):
    """
    Groups all the widgets used to control the music into one frame class
    """

    preview: Preview
    actions: ActionButtons
    side: SideButtons
    seeker: Seeker

    def __init__(self, master, player: Player):
        Frame.__init__(self, master, height=100)

        self.preview = Preview(self)
        self.actions = ActionButtons(self)
        self.side = SideButtons(self)
        self.seeker = Seeker(self, player)

        self.preview.propagate(False)
        self.side.propagate(False)

        self.actions.update()

        self.seeker.place(relx=0, rely=0, relwidth=1, relheight=0.25, anchor=NW)
        self.actions.place(relx=0.5, rely=0.50 + 0.125, anchor="center")
        self.actions.winfo_toplevel().update()
        width = self.actions.winfo_width() + 100
        self.preview.place(relx=0, rely=0.25, relwidth=0.5, width=-width/2, relheight=0.75, anchor=NW)
        self.side.place(relx=0.5, x=width / 2, rely=0.25, relwidth=0.5, width=-width / 2, relheight=0.75, anchor=NW)
