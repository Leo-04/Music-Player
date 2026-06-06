from tkinter import *

from music.player import Player

from UI.player.action_buttons import ActionButtons, NO_SHUFFLE, PREV, PAUSE, NEXT, REPEAT
from UI.player.preview import Preview
from UI.player.seeker import Seeker


class PopoutPlayer(Toplevel):
    """
    A simple pop-out player with:
    - Action buttons
    - Seekbar
    - Previews for song title, album and artist
    """

    action_buttons: ActionButtons
    shuffle: Button
    prev: Button
    play: Button
    next: Button
    loop: Button

    preview: Preview
    track_name: Label
    album: Label
    artist: Label

    seeker: Seeker

    def __init__(self, master, player: Player, action_buttons: ActionButtons, preview: Preview):
        Toplevel.__init__(self, master, width=375, height=85)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title("Pop-Out-Player")
        self.bind("<Enter>", lambda e: self.attributes(alpha=1))
        self.bind("<FocusIn>", lambda e: self.attributes(alpha=1))
        self.bind("<FocusOut>", lambda e: self.attributes(alpha=0.05))
        self.attributes(topmost=1)

        try: # Need a try for Linux / Mac
            self.attributes(toolwindow=1)
        except: pass

        self.action_buttons = action_buttons
        self.preview = preview

        self.track_name = Label(self, text=self.preview.track_name.cget("text"), bd=1, relief="ridge", anchor=W)
        self.album = Label(self, text=self.preview.album.cget("text"), width=1, bd=1, relief="ridge", anchor=W)
        self.artist = Label(self, text=self.preview.artist.cget("text"), width=1, bd=1, relief="ridge", anchor=W)

        self.shuffle = Button(self, name="shuffle", text=NO_SHUFFLE, image=action_buttons.img_1x1, compound=CENTER,
                              width=51, height=51, font="consolas 30",
                              command=lambda: (action_buttons.do_shuffle(), self.update_info()))
        self.prev = Button(self, name="previous", text=PREV, image=action_buttons.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30",
                           command=lambda: (action_buttons.do_prev(), self.update_info()))
        self.play = Button(self, name="play", text=PAUSE, image=action_buttons.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30",
                           command=lambda: (action_buttons.do_play(), self.update_info()))
        self.next = Button(self, name="next", text=NEXT, image=action_buttons.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30",
                           command=lambda: (action_buttons.do_next(), self.update_info()))
        self.loop = Button(self, name="loop", text=REPEAT, image=action_buttons.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30",
                           command=lambda: (action_buttons.do_loop(), self.update_info()))

        self.seeker = Seeker(self, player)

        self.seeker.grid(row=0, column=0, columnspan=10, sticky=EW)

        self.track_name.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        self.artist.grid(row=2, column=0, sticky=NSEW)
        self.album.grid(row=2, column=1, sticky=NSEW)

        self.shuffle.grid(row=1, column=2, rowspan=2, sticky=NSEW)
        self.prev.grid(row=1, column=3, rowspan=2, sticky=NSEW)
        self.play.grid(row=1, column=4, rowspan=2, sticky=NSEW)
        self.next.grid(row=1, column=5, rowspan=2, sticky=NSEW)
        self.loop.grid(row=1, column=6, rowspan=2, sticky=NSEW)

        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.resizable(True, True)
        self.minsize(300, 85)

    def show(self):
        """Shows this window and hides the root window"""

        self.deiconify()
        self.update()
        self.master.winfo_toplevel().withdraw()

    def close(self):
        """Hides this window and shows the root window"""

        self.withdraw()
        self.master.winfo_toplevel().deiconify()
        self.master.winfo_toplevel().update()

    def update_info(self):
        """Updates the information on the pop-out viewer"""

        self.track_name.config(text=self.preview.track_name.cget("text"))
        self.album.config(text=self.preview.album.cget("text"))
        self.artist.config(text=self.preview.artist.cget("text"))
        self.shuffle.config(text=self.action_buttons.shuffle.cget("text"))
        self.prev.config(text=self.action_buttons.prev.cget("text"))
        self.play.config(text=self.action_buttons.play.cget("text"))
        self.next.config(text=self.action_buttons.next.cget("text"))
        self.loop.config(text=self.action_buttons.loop.cget("text"))
        self.seeker.update_text()
