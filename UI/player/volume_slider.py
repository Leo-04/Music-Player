from tkinter import *
from tkinter.font import Font

VOL_EXT = "📢"
VOL_MAX = "🔊"
VOL_MID = "🔉"
VOL_MIN = "🔈"
VOL_OFF = "🔇"


class VolumeSlider(Scale):
    """
    A simple Scale widget for changing volume

    If you click the text of the widget, it will mute the volume
    """

    def __init__(self, master):
        Scale.__init__(self, master, orient=HORIZONTAL, from_=0, to=100, length=10, command=self.on_slide, label="Default Output",
                       font=("consolas", 22, "bold"), showvalue=False, takefocus=True, highlightthickness=0, bd=1, relief="ridge")
        self.set(100)

        self.bind("<Button-1>", self.click)
        self.bind("<Up>", lambda e: ("break", self.set(self.get() + 1))[0])
        self.bind("<Down>", lambda e: ("break", self.set(self.get() - 1))[0])

    def click(self, event):
        """
        This event will be fired when the widget is clicked

        Check whether we have clicked the slider or the text
        If we have clicked the text, mute the audio and stop the event

        Args:
            event: Tkinter event
        """

        text_height = Font(font=self["font"]).metrics("linespace") + 1 + 2 * int(self["bd"])
        if event.y < text_height:
            self.do_mute()
            return "break"

    def do_mute(self):
        """Toggles the mute state, fires an "Action-SetVolume" or "Action-Mute" event depending on current state"""

        if self["label"][0] == VOL_OFF:
            self.on_slide()
        else:
            self.winfo_toplevel().event_generate("<<Action-Mute>>", when="tail")
            self["label"] = VOL_OFF + " " + str(self.get())

    def on_slide(self, *_):
        """
        Tkinter event callback when the slider is moved

        Updates the text of the slider as well as fires a "Action-SetVolume" event
        """

        vol = int(self.get())

        self.winfo_toplevel().event_generate("<<Action-SetVolume>>", when="tail", x=vol)

        if vol < 25:
            self["label"] = VOL_MIN + " " + str(self.get())
        elif vol < 50:
            self["label"] = VOL_MID + " " + str(self.get())
        elif vol < 101:
            self["label"] = VOL_MAX + " " + str(self.get())
        else:
            self["label"] = VOL_EXT + " " + str(self.get())
