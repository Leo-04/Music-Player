import os
from math import log10
from threading import Thread

import vlc

os.add_dll_directory(os.getcwd())
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')


# This is the old player and is now decrepit


class Player:
    """
    This is a basic class to handle playing audio
    """

    instance: vlc.Instance
    media_player: vlc.MediaPlayer
    equalizer: vlc.AudioEqualizer
    on_end: callable
    on_time: callable

    def __init__(self, on_end: callable = lambda: None, on_time: callable = lambda t: None):
        """
        Args:
            on_end: callable
                A callable to be called when the current track reaches the end

            on_time: callable
                A callable to be called each second the current track si being played
        """

        self.instance = vlc.Instance(["--audio-resampler=speex --no-audio-time-stretch"]) # "--no-playlist-autostart"
        self.media_player = self.instance.media_player_new()
        self.equalizer = vlc.AudioEqualizer()

        for event, func in [
            (vlc.EventType.MediaPlayerEndReached, lambda e: self.on_end()),
            (vlc.EventType.MediaPlayerPositionChanged, lambda e: self.on_time(e.u.new_position)),
        ]:
            self.media_player.event_manager().event_attach(event, func)

        self.on_end = on_end
        self.on_time = on_time

    def load(self, filename: str | None, play: bool = True):
        """
        Loads a file to play

        Loads a file to play from a filename, if the filename is None, it stops the music
        An optional parameter play may be used to control weather to start playing the music

        Args:
            filename: str | None
                A string to a path to play or None to stop playing

            play: bool
                Controls whether to start playing the music
        """

        if filename is None:
            self.stop()
        else:
            print("LOAD:", filename, play)
            self.media_player.stop()
            print("Loaded")
            media = self.instance.media_new(str(filename))

            print("Loaded")
            print(self.media_player.get_media())
            print("Loaded")
            self.media_player.set_media(None)
            print("Loaded")
            self.media_player.set_media(media)
            print("Loaded")
            if play:
                self.play()
            print("Loaded")

    def play(self):
        """Plays the music"""

        self.media_player.play()

    def pause(self):
        """Pauses the music"""

        if not self.is_paused():
            self.media_player.pause()

    def unpause(self):
        """Unpauses the music"""

        if self.is_paused():
            self.media_player.pause()

    def is_paused(self) -> bool:
        """
        Check if the music is paused

        Returns:
            False if the music is playing
            True if the music is not playing
        """

        return not self.media_player.is_playing()

    def stop(self):
        """Stops the music, this also calls `self.on_end()`"""

        self.media_player.stop()
        self.on_end()

    def set_pos(self, p: float):
        """
        Sets the current position of the music being played as a percentage from 0.0 to 1.0

        Args:
            p: float[0.0 -> 1.0]
                The percentage of the run time to set playback to
        """

        paused = self.is_paused()
        if not paused:
            self.media_player.pause()
        self.media_player.set_position(p)

        if paused:
            self.pause()
        else:
            self.media_player.play()

    def length(self) -> float:
        """Gets the playback length of the music in seconds"""

        return self.media_player.get_length() / 1000

    __len__ = length

    def set_volume(self, volume: int):
        """
        Sets the volume of the currently playing music

        Sets the volume of the currently playing music via VLC volume metrics.
        This is different from the system volume metrics,
        Use the equation 'system_volume=21.248*(vlc_volume ** 0.3352)' to approximately set the system volume

        Args:
            volume: int [0 -> ...]
                The volume from 0 to set the music
        """

        # Here is some data that I found to get the equation
        """
        vol = {100: 100, 99: 99, 98: 99, 97: 98, 96: 98, 95: 98, 94: 97, 93: 97, 92: 97, 91: 96, 90: 96, 89: 96, 88: 95, 87: 95, 86: 95, 85: 94, 84: 94, 83: 93,
         82: 93, 81: 93, 80: 92, 79: 92, 78: 92, 77: 91, 76: 91, 75: 90, 74: 90, 73: 90, 72: 89, 71: 89, 70: 88, 69: 88, 68: 87, 67: 87, 66: 87,
         65: 86, 64: 86, 63: 85, 62: 85, 61: 84, 60: 84, 59: 83, 58: 83, 57: 82, 56: 82, 55: 81, 54: 81, 53: 80, 52: 80, 51: 79, 50: 79, 49: 78,
         48: 78, 47: 77, 46: 77, 45: 76, 44: 76, 43: 75, 42: 74, 41: 74, 40: 73, 39: 73, 38: 72, 37: 71, 36: 71, 35: 70, 34: 69, 33: 69, 32: 68,
         31: 67, 30: 66, 29: 66, 28: 65, 27: 64, 26: 63, 25: 62, 24: 62, 23: 61, 22: 60, 21: 59, 20: 58, 19: 57, 18: 56, 17: 55, 16: 54, 15: 53,
         14: 51, 13: 50, 12: 49, 11: 47, 10: 46, 9: 44, 8: 43, 7: 41, 6: 39, 5: 36, 4: 34, 3: 31, 2: 27, 1: 21, 0: 0}
        # y=21.248x^{0.3352}

        if 0 <= volume <= 100:
            volume = 21.248*(volume ** 0.3352)
            volume = int(volume) + 1
        """

        self.media_player.audio_set_volume(volume)

        # https://forum.videolan.org/viewtopic.php?t=153834

    def get_pos(self) -> float:
        """Gets the playback run time percentage"""

        return self.media_player.get_position()

    def destroy(self):
        """Stops the music and frees all VLC related data"""

        self.media_player.stop()
        self.equalizer.release()
        self.media_player.release()
        self.instance.release()

    def get_outputs(self) -> list[tuple[str, str]]:
        """
        Get all available output devices

        Get a list of all available output devices and their names
        The first value in the tuple is the device description
        The second value in the tuple is the device ID, use this value with `self.set_output(...)`

        Returns:
            A list of devices
        """

        outputs = []
        mods = self.media_player.audio_output_device_enum()
        if mods:
            mod = mods
            while mod:
                mod = mod.contents
                outputs.append((mod.description.decode("utf-8"), mod.device.decode("utf-8")))
                mod = mod.next

        return outputs

    def set_output(self, output: str):
        """Sets the output device"""

        self.media_player.audio_output_device_set(None, output)

    def get_output(self) -> str:
        """Gets the current output device"""

        output = self.media_player.audio_output_device_get()
        if output is None:
            return ""
        return output

    def set_eq(self, hz60=0, hz170=0, hz310=0, hz600=0, hz1k=0, hz3k=0, hz6k=0, hz12k=0, hz14k=0, hz16k=0):
        """Sets the equalizer amps"""

        self.equalizer.set_preamp(0)
        self.equalizer.set_amp_at_index(hz60, 0)  # 60 Hz
        self.equalizer.set_amp_at_index(hz170, 1)  # 170 Hz
        self.equalizer.set_amp_at_index(hz310, 2)  # 310 Hz
        self.equalizer.set_amp_at_index(hz600, 3)  # 600 Hz
        self.equalizer.set_amp_at_index(hz1k, 4)  # 1 kHz
        self.equalizer.set_amp_at_index(hz3k, 5)  # 3 kHz
        self.equalizer.set_amp_at_index(hz6k, 6)  # 6 kHz
        self.equalizer.set_amp_at_index(hz12k, 7)  # 12 kHz
        self.equalizer.set_amp_at_index(hz14k, 8)  # 14 kHz
        self.equalizer.set_amp_at_index(hz16k, 9)  # 16 kHz
        self.media_player.set_equalizer(self.equalizer)


class ThreadedPlayer(Player):
    """Same as Player class but each function is Threaded"""

    def load(*args, **kwargs):
        Thread(target=Player.load, args=args, kwargs=kwargs).start()

    def play(*args, **kwargs):
        Thread(target=Player.play, args=args, kwargs=kwargs).start()

    def pause(*args, **kwargs):
        Thread(target=Player.pause, args=args, kwargs=kwargs).start()

    def unpause(*args, **kwargs):
        Thread(target=Player.unpause, args=args, kwargs=kwargs).start()

    def stop(*args, **kwargs):
        Thread(target=Player.stop, args=args, kwargs=kwargs).start()

    def set_pos(*args, **kwargs):
        Thread(target=Player.set_pos, args=args, kwargs=kwargs).start()

    def set_volume(*args, **kwargs):
        Thread(target=Player.set_volume, args=args, kwargs=kwargs).start()

    def set_output(*args, **kwargs):
        Thread(target=Player.set_output, args=args, kwargs=kwargs).start()

    def set_eq(*args, **kwargs):
        Thread(target=Player.set_eq, args=args, kwargs=kwargs).start()

    load.__doc__ = Player.load.__doc__
    play.__doc__ = Player.play.__doc__
    pause.__doc__ = Player.pause.__doc__
    unpause.__doc__ = Player.unpause.__doc__
    stop.__doc__ = Player.stop.__doc__
    set_pos.__doc__ = Player.set_pos.__doc__
    set_volume.__doc__ = Player.set_volume.__doc__
    set_output.__doc__ = Player.set_output.__doc__
    set_eq.__doc__ = Player.set_eq.__doc__
