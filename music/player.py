import atexit
import os
import subprocess
from threading import Thread
import shutil

os.environ["PYTHONUNBUFFERED"] = "1"
os.environ['PYTHONIOENCODING'] = 'UTF-8'


class Player:
    """
    This is a basic class to handle playing audio using ffplay on the command line
    """

    ffplay: str = shutil.which("ffplay")

    on_end: callable
    on_time: callable
    on_error: callable

    def __init__(self, on_end: callable = lambda: None, on_time: callable = lambda t: None, on_error: callable = lambda err: print(err)):
        """
        Args:
            on_end: callable
                A callable to be called when the current track reaches the end

            on_time: callable
                A callable to be called each second the current track is being played
        """

        self.on_end = on_end
        self.on_time = on_time
        self.on_error = on_error
        self.buffer = ""
        self.hwnd = None
        self.volume = 100
        self.pos = 0
        self.file_path = None
        self.start_pos = 0
        self.paused = False
        self.len = 1
        self.thread = None
        self.eq = ""
        self.set_eq()

        atexit.register(self.destroy)

    def handle_buffer(self, buffer: str):
        """
        Handles ffplay output buffer

        Args:
            buffer: str
                the new line read from ffplay
        """

        try:
            pos = float(buffer)
            if str(pos) == 'nan':
                return
        except ValueError:
            return

        if self.pos != pos:
            self.pos = pos
            self.on_time(pos / self.len)

        self.pos = pos

    def read_thread(self):
        """
        A thread that reads the ffplay buffer

        This function is called in a thread and runs until `self.thread` is None or it reaches the end of the song
        If it reaches the end of the song, `self.on_end` is called
        """

        while self.hwnd is not None and self.hwnd.poll() is None and self.thread is not None:
            if self.hwnd is None:
                break

            try:
                char = self.hwnd.stderr.read(1)
            except Exception as err:
                self.on_error(err)
                break

            if char == "\n":
                line = self.buffer.strip().split(" ", 1)[0]
                self.buffer = ""
                if self.thread:
                    self.handle_buffer(line)
            else:
                self.buffer += char

        if self.thread is not None:
            self.on_end()

    def load(self, filename: str | None, length: int, play: bool = True):
        """
        Loads a file to play

        Loads a file to play from a filename, if the filename is None, it stops the music
        An optional parameter play may be used to control weather to start playing the music

        Args:
            filename: str | None
                A string to a path to play or None to stop playing

            length: int
                The length of the music

            play: bool
                Controls whether to start playing the music
        """

        self.stop()
        self.file_path = str(filename)
        self.start_pos = 0
        self.pos = 0
        self.len = length
        self.on_time(0)
        if play:
            self.play()

    def run(self):
        """
        Runs ffplay with the desired arguments

        This calls `self.stop` then plays a new song with ffplay
        This also starts `self.read_thread` in a new thread
        """

        if not self.paused and self.file_path is not None:
            if self.ffplay is None:
                self.on_error(Exception("FFPlay is not installed"))
                return

            self.stop()
            self.paused = False
            cmd = [
                self.ffplay, self.file_path,
                "-hide_banner", "-nodisp", "-autoexit",
                "-ss", str(self.start_pos),
                "-volume", str(self.volume),
                "-af", self.eq
            ]
            try:
                self.hwnd = subprocess.Popen(
                    cmd,
                    stderr=subprocess.PIPE,
                    env=os.environ,
                    universal_newlines=True,  # shell=True,
                    creationflags=0 if os.name != 'nt' else subprocess.CREATE_NO_WINDOW,
                    encoding="utf-8"
                )
            except Exception as err:
                self.on_error(err)
                return

            while self.hwnd.poll() is not None:
                pass

            self.thread = Thread(target=self.read_thread)
            self.thread.start()

    def play(self):
        """Plays the music"""

        self.paused = False
        self.run()

    def pause(self):
        """Pauses the music"""

        if not self.is_paused():
            self.stop()
            self.start_pos = self.pos
            self.paused = True

    def unpause(self):
        """Unpauses the music"""

        if self.is_paused():
            self.run()

    def is_paused(self) -> bool:
        """
        Check if the music is paused

        Returns:
            False if the music is playing
            True if the music is not playing
        """

        return self.paused

    def stop(self):
        """Stops the music"""

        if self.hwnd is not None:
            self.thread = None
            self.hwnd.terminate()
            self.handle_buffer(self.hwnd.communicate()[1])
            self.hwnd = None

        self.paused = None

    def set_pos(self, p: float):
        """
        Sets the current position of the music being played

        Args:
            p: float
                The percentage of playback
        """

        self.start_pos = p * self.len
        self.run()

    def set_volume(self, volume: int):
        """
        Sets the volume of the currently playing music

        Sets the volume of the currently playing music via VLC volume metrics.
        This is different from the system volume metrics,
        Use the equation 'system_volume=21.248*(vlc_volume ** 0.3352)' to approximately set the system volume

        Args:
            volume: int [0 -> 100]
                The volume from 0 to set the music
        """

        self.volume = volume
        self.start_pos = self.pos
        self.run()

    def get_pos(self) -> float:
        """Gets the playback time"""

        return self.pos / self.len

    def length(self) -> float:
        """Gets the playback time"""

        return self.len

    def destroy(self):
        """Stops the music and frees all related data"""

        self.stop()

    def set_eq(self, hz60=0, hz170=0, hz310=0, hz600=0, hz1k=0, hz3k=0, hz6k=0, hz12k=0, hz14k=0, hz16k=0):
        """Sets the equalizer amps"""

        self.eq = ",".join([
            "equalizer=f=%i:g=%i" % (hz, db)
            for hz, db in {
                60: hz60,
                170: hz170,
                310: hz310,
                600: hz600,
                1000: hz1k,
                3000: hz3k,
                6000: hz6k,
                12000: hz12k,
                14000: hz14k,
                16000: hz16k
            }.items()
        ])
        self.start_pos = self.pos
        if not self.is_paused():
            self.play()

    # So I switch from VLC to ffplay and I wish I knew how to implement these, but I don't think I can with ffplay
    # I'm leaving these here as I'm hoping in the future I can put the values in, and it will just work
    # For now though, they return dummy values for the UI as, although I haven't displayed it, there is UI to switch devices

    #
    # https://stackoverflow.com/questions/73413047/different-audio-output-devices-for-simultaneous-processes-python-ffplay

    # custom_env = os.environ.copy()
    #
    # Force SDL to use the Windows WASAPI driver
    # custom_env["SDL_AUDIODRIVER"] = "wasapi"
    # custom_env["SDL_AUDIO_DEVICE_NAME"] = "Headphones (High Definition Audio Device)"
    # env=custom_env
    # ffplay -hide_banner -devices
    # Linux: pulse, alsa, pipewire, jack,
    # Linux LEGACY: oss, sndio, esd, arts
    # Window: wasapi, directsound, winmm
    # Mac(lol): coreaudio
    # ffplay -hide_banner -f pulse -device "NAME"

    # still cant lol

    def get_outputs(self) -> list[tuple[str, str]]:
        """
        Get all available output devices

        Get a list of all available output devices and their names
        The first value in the tuple is the device description
        The second value in the tuple is the device ID, use this value with `self.set_output(...)`

        Returns:
            A list of devices
        """

        return [("", "")]

    def set_output(self, output: str):
        """Sets the output device"""

        pass

    def get_output(self) -> str:
        """Gets the current output device"""

        return ""
