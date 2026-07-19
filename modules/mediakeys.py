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
KEY_PLAY = 0x1008FF14
KEY_PAUSE = 0x1008FF13
KEY_NEXT = 0x1008FF17
KEY_PREVIOUS = 0x1008FF16
KEY_STOP = 0x1008FF15
AnyModifier = 0x80000000
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
    
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p

    x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    x11.XDefaultRootWindow.restype = ctypes.c_ulong

    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.restype = ctypes.c_int

    x11.XPending.argtypes = [ctypes.c_void_p]
    x11.XPending.restype = ctypes.c_int

    x11.XGrabKey.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_ulong,
                             ctypes.c_int, ctypes.c_int, ctypes.c_int]
    x11.XGrabKey.restype = ctypes.c_int

    x11.XUngrabKey.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_ulong]
    x11.XUngrabKey.restype = ctypes.c_int

    x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
    x11.XSync.restype = ctypes.c_int

    x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XKeysymToKeycode.restype = ctypes.c_ubyte


    display = x11.XOpenDisplay(None)
    
    if not display:
        raise Exception("Could not open X11 display")

    root = x11.XDefaultRootWindow(display)

    play_code = x11.XKeysymToKeycode(display, KEY_PLAY)
    if x11.XGrabKey(display, play_code, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register PLAY")

    pause_code = x11.XKeysymToKeycode(display, KEY_PAUSE)
    if x11.XGrabKey(display, pause_code, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register PAUSE")

    next_code = x11.XKeysymToKeycode(display, KEY_NEXT)
    if x11.XGrabKey(display, next_code, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register NEXT")

    prev_code = x11.XKeysymToKeycode(display, KEY_PREVIOUS)
    if x11.XGrabKey(display, prev_code, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
        x11.XCloseDisplay(display)
        raise Exception("Failed to register PREVIOUS")

    stop_code = x11.XKeysymToKeycode(display, KEY_STOP)
    if x11.XGrabKey(display, stop_code, AnyModifier, root, True, GrabModeAsync, GrabModeAsync):
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
                if keycode == play_code or keycode == pause_code:
                    root.after(0, lambda: root.event_generate("<<MediaKey-PlayPause>>"))
                elif keycode == stop_code:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Stop>>"))
                elif keycode == prev_code:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Previous>>"))
                elif keycode == next_code:
                    root.after(0, lambda: root.event_generate("<<MediaKey-Next>>"))

        time.sleep(0.01)

    x11.XUngrabKey(display, play_code, AnyModifier, root)
    x11.XUngrabKey(display, pause_code, AnyModifier, root)
    x11.XUngrabKey(display, next_code, AnyModifier, root)
    x11.XUngrabKey(display, prev_code, AnyModifier, root)
    x11.XUngrabKey(display, stop_code, AnyModifier, root)
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
