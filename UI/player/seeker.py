from tkinter import Canvas, Scale
from tkinter.font import Font

from music.player import Player


class Seeker(Canvas):
    """
    A time slider to control the player's position
    """

    FONT = ("consolas", 16)

    player: Player
    line_height: int = 10
    line_padding: int = 10
    seek_size: int = 20
    percentage: float = 0
    was_paused: bool | None = None
    was_paused_called: int = 0

    def __init__(self, master, player: Player):
        temp = Scale()
        self.fg = temp["fg"]
        self.trough = temp["troughcolor"]
        temp.destroy()
        del temp

        Canvas.__init__(self, master, bd=0, highlightthickness=0, height=Font(font=self.FONT).metrics("linespace"))

        self.player = player
        self.line_height = 10
        self.line_padding = 10
        self.seek_size = 20
        self.percentage = 0
        self.was_paused = None
        self.was_paused_called = 0

        self.start = self.create_text(0, 0, anchor="nw", text=" " + Seeker.format_seconds(0), font=self.FONT, fill=self.fg)
        self.end = self.create_text(self.winfo_width(), 0, anchor="ne", text=Seeker.format_seconds(0) + " ", font=self.FONT, fill=self.fg)

        self.line = self.create_rectangle(0, 0, 0, 0, fill=self.trough, outline=self.fg)
        self.seek = self.create_oval(0, 0, 0, 0, fill=self["bg"], outline=self.fg)

        self.bind("<Configure>", self.on_resize)
        self.bind("<ButtonPress-1>", self.line_down)
        self.bind("<ButtonRelease-1>", self.line_up)
        self.bind("<B1-Motion>", self.line_moved)
        self.tag_bind(self.seek, "<B1-Motion>", self.line_moved)

    @staticmethod
    def format_seconds(s: int) -> str:
        """
        Takes the time in seconds and returns a formatted string

        Args:
            s: int
                The number of seconds

        Returns:
            A string in the format hh:mm:ss
        """

        h = s // (60 * 60)
        m = (s // 60) % 60
        s = s % 60

        return "%02d:%02d:%02d" % (h, m, s)  # .%04d ms

    def on_resize(self, _=None):
        self.update_seekbar(True)

    def line_down(self, event):
        """Event callback for when we have pushed down the mouse button"""

        if self.was_paused is None and self.was_paused_called == 0:
            self.was_paused = self.player.is_paused()
        self.was_paused_called += 1

        self.player.pause()
        self.line_moved(event)

    def line_moved(self, event):
        """Event callback for when we have dragged the mouse button"""

        x1, y1, x2, y2 = self.coords(self.line)
        if event.x < x1:
            p = 0
        elif event.x > x2:
            p = 1
        else:
            p = (event.x - x1) / (x2 - x1)

        self.percentage = p

        self.update_text(False)
        self.update_seekbar()

    def line_up(self, event):
        """Event callback for when we have pushed up the mouse button"""

        x1, y1, x2, y2 = self.coords(self.line)
        if event.x < x1:
            p = 0
        elif event.x > x2:
            p = 1
        else:
            p = (event.x - x1) / (x2 - x1)

        self.percentage = p
        self.player.set_pos(p)

        if self.was_paused:
            self.player.stop()
        else:
            self.player.unpause()
            self.player.play()

        self.update_seekbar()

        self.was_paused_called -= 1
        if self.was_paused_called < 1:
            self.was_paused_called = 0
            self.was_paused = None

    def update_text(self, update_seek: bool = True):
        """
        Updates the text of the seek bar

        Updates the current position text and the end position text
        An optional boolean can be passed to also update the seekbar position.

        Args:
            update_seek: bool
                if True, update the seekbar position
        """

        if self.player.length() > 0:
            if update_seek:
                self.percentage = self.player.get_pos()
                self.update_seekbar()
        else:
            self.coords(
                self.seek,
                -100, 0, 0, 0
            )

        current = " " + Seeker.format_seconds(int(self.percentage * self.player.length()))
        ending = Seeker.format_seconds(int(self.player.length())) + " "

        self.itemconfig(self.start, text=current)
        self.itemconfig(self.end, text=ending)

    def update_seekbar(self, resized: bool = False):
        """
        Updates the seekbar's position

        Args:
            resized: bool
                If True, the window was resized and we will need to recalculate the size of the bar.
        """

        bounds = self.bbox(self.start)
        width_pos = bounds[2] - bounds[0]
        bounds = self.bbox(self.end)
        width_end = bounds[2] - bounds[0]

        if resized:
            self.coords(self.end, self.winfo_width(), 0)
            self.coords(
                self.line,
                width_pos + self.line_padding,
                self.winfo_height() / 2 - self.line_height / 2,
                self.winfo_width() - width_end - self.line_padding,
                self.winfo_height() / 2 + self.line_height / 2
            )

        line_width = self.winfo_width() - (width_end + width_pos) - 2 * self.line_padding

        current_pos = self.percentage * line_width
        self.coords(
            self.seek,
            current_pos + width_pos - self.seek_size / 2 + self.line_padding,
            (self.winfo_height() - self.seek_size) / 2,
            current_pos + width_pos + self.seek_size / 2 + self.line_padding,
            (self.winfo_height() + self.seek_size) / 2,
        )

    def get_pos(self) -> float:
        """Gets the current position as a float between 0.0 and 1.0"""

        return self.percentage
