from tkinter import *

# https://en.wikipedia.org/wiki/Media_control_symbols
PLAY = "\u23F5"
PAUSE = "\u23F8"
STOP = "\u23F9"
PREV = "\u23EA"
NEXT = "\u23E9"
SHUFFLE = "🔀"
NO_SHUFFLE = "\u2B86"
REPEAT = "🔁"
REPEAT1 = "🔂"
NO_REPEAT = "\u2B72"
REPLAY = "🔄"


class ActionButtons(Frame):
    """
    These are the basic media control buttons, I call these "action buttons"
    """

    img_1x1: PhotoImage
    shuffle: Button
    prev: Button
    play: Button
    next: Button
    loop: Button

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.img_1x1 = PhotoImage(width=1, height=1)

        self.shuffle = Button(self, name="shuffle", text=NO_SHUFFLE, image=self.img_1x1, compound=CENTER,
                              width=51, height=51, font="consolas 30", command=self.do_shuffle)
        self.prev = Button(self, name="previous", text=PREV, image=self.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30", command=self.do_prev)
        self.play = Button(self, name="play", text=PAUSE, image=self.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30", command=self.do_play)
        self.next = Button(self, name="next", text=NEXT, image=self.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30", command=self.do_next)
        self.loop = Button(self, name="loop", text=REPEAT, image=self.img_1x1, compound=CENTER,
                           width=51, height=51, font="consolas 30", command=self.do_loop)

        self.shuffle.grid(row=0, column=1, pady=12, padx=5)
        self.prev.grid(row=0, column=2, pady=12, padx=5)
        self.play.grid(row=0, column=3, pady=12, padx=5)
        self.next.grid(row=0, column=4, pady=12, padx=5)
        self.loop.grid(row=0, column=5, pady=12, padx=5)

    def set_play(self, mode: bool):
        """
        Controls the play button's text

        Args:
            mode: bool
                True for play
                False for pause
        """

        if mode:
            self.play["text"] = PAUSE
        else:
            self.play["text"] = PLAY

    def do_shuffle(self):
        """
        Event callback function for shuffle

        This is called when the shuffle button is pressed, this updates the text and fires an event
        """

        if self.shuffle["text"] == SHUFFLE:
            self.shuffle["text"] = NO_SHUFFLE
            self.winfo_toplevel().event_generate("<<Action-NoShuffle>>", when="tail")
        else:
            self.shuffle["text"] = SHUFFLE
            self.winfo_toplevel().event_generate("<<Action-Shuffle>>", when="tail")

    def do_prev(self):
        """
        Event callback function for prev

        This is called when the prev button is pressed, this fires an event
        """

        self.winfo_toplevel().event_generate("<<Action-Prev>>", when="tail")

    def do_play(self):
        """
        Event callback function for play

        This is called when the play button is pressed, this updates the text and fires an event
        """

        if self.play["text"] == PAUSE:
            self.play["text"] = PLAY
            self.winfo_toplevel().event_generate("<<Action-Pause>>", when="tail")
        else:
            self.play["text"] = PAUSE
            self.winfo_toplevel().event_generate("<<Action-Play>>", when="tail")

    def do_next(self):
        """
        Event callback function for next

        This is called when the next button is pressed, this fires an event
        """

        self.winfo_toplevel().event_generate("<<Action-Next>>", when="tail")

    def do_loop(self):
        """
        Event callback function for loop

        This is called when the loop button is pressed, this updates the text and fires an event
        """

        if self.loop["text"] == REPEAT:
            self.loop["text"] = REPEAT1
            self.winfo_toplevel().event_generate("<<Action-Repeat1>>", when="tail")
        elif self.loop["text"] == REPEAT1:
            self.loop["text"] = NO_REPEAT
            self.winfo_toplevel().event_generate("<<Action-NoRepeat>>", when="tail")
        else:
            self.loop["text"] = REPEAT
            self.winfo_toplevel().event_generate("<<Action-Repeat>>", when="tail")
#
