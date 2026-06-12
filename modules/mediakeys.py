import os
import time
from tkinter import Tk
import ctypes

# Windows constants
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
WM_HOTKEY = 0x0312
PM_REMOVE = 0x0001

# Linux constants
KEY_PLAY = 172
KEY_PAUSE = 173
KEY_NEXT = 171
KEY_PREVIOUS = 170
KEY_STOP = 174
AnyModifier = 0
GrabModeAsync = 1
KeyPress = 2


def media_keys_thread_windows(root: Tk, is_alive: callable):
    """
    A thread to handle windows media hotkeys

    Parameters:
        root: Tk
            The root window to send events too

        is_alive: callable
            A function, while it returns true, the thread shall exist
    """

    from ctypes import wintypes

    if not ctypes.windll.user32.RegisterHotKey(None, VK_MEDIA_PLAY_PAUSE, 0, VK_MEDIA_PLAY_PAUSE):
        raise Exception("Failed to register PLAY/PAUSE")
    if not ctypes.windll.user32.RegisterHotKey(None, VK_MEDIA_NEXT_TRACK, 0, VK_MEDIA_NEXT_TRACK):
        raise Exception("Failed to register NEXT")
    if not ctypes.windll.user32.RegisterHotKey(None, VK_MEDIA_PREV_TRACK, 0, VK_MEDIA_PREV_TRACK):
        raise Exception("Failed to register PREVIOUS")
    if not ctypes.windll.user32.RegisterHotKey(None, VK_MEDIA_STOP, 0, VK_MEDIA_STOP):
        raise Exception("Failed to register STOP")

    msg = wintypes.MSG()

    while is_alive():
        if ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
            if msg.message == WM_HOTKEY:
                if msg.wParam == VK_MEDIA_PLAY_PAUSE:
                    root.after(0, lambda: root.event_generate("<<MediaKey-PlayPause>>"))
                elif msg.wParam == VK_MEDIA_STOP:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Stop>>"))
                elif msg.wParam == VK_MEDIA_PREV_TRACK:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Previous>>"))
                elif msg.wParam == VK_MEDIA_NEXT_TRACK:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Next>>"))

            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
        else:
            time.sleep(0.1)

    ctypes.windll.user32.UnregisterHotKey(None, VK_MEDIA_PLAY_PAUSE)
    ctypes.windll.user32.UnregisterHotKey(None, VK_MEDIA_NEXT_TRACK)
    ctypes.windll.user32.UnregisterHotKey(None, VK_MEDIA_PREV_TRACK)
    ctypes.windll.user32.UnregisterHotKey(None, VK_MEDIA_STOP)


# this is semi-untested as I don't have a spare linux machine to hand
# Tested in a VM so the code runs, just not the stuff within the if statement within the loop
# As far as I'm aware from the docs I've read it should work, fingers crossed :)
def media_keys_thread_linux(root: Tk, is_alive: callable):
    """
    A thread to handle linux media hotkeys

    Parameters:
        root: Tk
            The root window to send events too

        is_alive: callable
            A function, while it returns true, the thread shall exist
    """

    x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
    display = x11.XOpenDisplay(None)

    if not display:
        raise Exception("Could not open X11 display")

    root = x11.XDefaultRootWindow(display)

    if x11.XGrabKey(display, KEY_PLAY, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register PLAY")

    if x11.XGrabKey(display, KEY_PAUSE, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register PAUSE")

    if x11.XGrabKey(display, KEY_NEXT, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register NEXT")

    if x11.XGrabKey(display, KEY_PREVIOUS, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register PREVIOUS")

    if x11.XGrabKey(display, KEY_STOP, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register STOP")

    x11.XSync(display, False)

    # Funny hack
    XEvent = ctypes.c_char * 256
    event = XEvent()

    while is_alive():
        if x11.XPending(display) > 0:
            x11.XNextEvent(display, ctypes.byref(event))

            event_type = ord(event[0])

            if event_type == KeyPress:
                keycode = ord(event[1])
                if keycode == KEY_PLAY or keycode == KEY_PAUSE:
                    root.after(0, lambda: root.event_generate("<<MediaKey-PlayPause>>"))
                elif keycode == KEY_STOP:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Stop>>"))
                elif keycode == KEY_PREVIOUS:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Previous>>"))
                elif keycode == KEY_NEXT:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Next>>"))

        time.sleep(0.01)

    x11.XUngrabKey(display, KEY_PLAY, AnyModifier, root)
    x11.XUngrabKey(display, KEY_PAUSE, AnyModifier, root)
    x11.XUngrabKey(display, KEY_NEXT, AnyModifier, root)
    x11.XUngrabKey(display, KEY_PREVIOUS, AnyModifier, root)
    x11.XUngrabKey(display, KEY_STOP, AnyModifier, root)
    x11.XCloseDisplay(display)


def media_key_thread(*args):
    """
    A thread to handle media hotkeys

    Parameters:
        root: Tk
            The root window to send events too

        is_alive: callable
            A function, while it returns true, the thread shall exist
    """

    if os.name == "nt":
        media_keys_thread_windows(*args)
    else:
        media_keys_thread_linux(*args)
