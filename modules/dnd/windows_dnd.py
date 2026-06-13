from tkinter import Tk
import ctypes
from ctypes import wintypes, WINFUNCTYPE

WM_DROPFILES = 0x0233

comctl32 = ctypes.windll.comctl32
shell32 = ctypes.windll.shell32

shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
shell32.DragAcceptFiles.restype = None

shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
shell32.DragQueryFileW.restype = wintypes.UINT

shell32.DragFinish.argtypes = [wintypes.HANDLE]
shell32.DragFinish.restype = None

WNDPROC = WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM, ctypes.c_void_p, ctypes.c_void_p)

comctl32.SetWindowSubclass.argtypes = [wintypes.HWND, WNDPROC, ctypes.c_void_p, ctypes.c_void_p]
comctl32.SetWindowSubclass.restype = wintypes.BOOL

comctl32.DefSubclassProc.restype = ctypes.c_long
comctl32.RemoveWindowSubclass.argtypes = [wintypes.HWND, WNDPROC, ctypes.c_void_p]


def dnd(root: Tk, callback: callable):
    """
    Drag and drop functionality for files
    Only implement on window

    Parameters:
        root: Tk
            The window to allow drag and dropping

        callback: callable[list[str]]
            The function to call with the list of dragged files
    """

    def window_protocol(hwnd, msg, wParam, lParam, uidSubclass, dwRefData):
        if msg == WM_DROPFILES:
            hdrop = wParam
            num_files = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
            files = []

            for i in range(num_files):
                # Get file via buffer
                length = shell32.DragQueryFileW(hdrop, i, None, 0)
                buffer = ctypes.create_unicode_buffer(length + 1)
                shell32.DragQueryFileW(hdrop, i, buffer, length + 1)
                files.append(buffer.value)

            shell32.DragFinish(hdrop)

            if callback:
                callback(files)

            return 0

        else:
            # Pass onto next handler
            return ctypes.windll.comctl32.DefSubclassProc(hwnd, msg, wintypes.WPARAM(wParam), wintypes.LPARAM(lParam))

    root.deiconify()
    root.update()
    hwnd = root.winfo_id()
    if not hwnd:
        raise Exception("Cannot get root window hwnd")

    # Chain the calls
    root.dnd_window_protocol = WNDPROC(window_protocol)
    ctypes.windll.comctl32.SetWindowSubclass(hwnd, root.dnd_window_protocol, ctypes.c_void_p(1), ctypes.c_void_p(0))
    shell32.DragAcceptFiles(hwnd, True)
