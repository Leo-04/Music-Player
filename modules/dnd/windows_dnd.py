from tkinter import Tk
import ctypes
from ctypes import wintypes, WINFUNCTYPE

WM_DROPFILES = 0x0233
WM_DESTROY = 0x0002
WM_SIZE = 0x0005
SIZE_MINIMIZED = 1
GWL_WNDPROC = -4
WS_EX_ACCEPTFILES = 0x00000010

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
kernel32 = ctypes.windll.kernel32

user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND

user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
user32.SetWindowLongPtrW.restype = ctypes.c_void_p

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_long

shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
shell32.DragAcceptFiles.restype = None

shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
shell32.DragQueryFileW.restype = wintypes.UINT

shell32.DragFinish.argtypes = [wintypes.HANDLE]
shell32.DragFinish.restype = None

user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None

WNDPROC = WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


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

    def window_protocol(hwnd, msg, wParam, lParam):
        if msg == WM_DROPFILES:
            hdrop = wParam
            num_files = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
            files = []

            for i in range(num_files):
                # Get the length of the file path
                length = shell32.DragQueryFileW(hdrop, i, None, 0)
                # Create buffer for file path
                buffer = ctypes.create_unicode_buffer(length + 1)
                # Get the file path
                shell32.DragQueryFileW(hdrop, i, buffer, length + 1)
                files.append(buffer.value)

            shell32.DragFinish(hdrop)

            if callback:
                callback(files)

            return 0

        return user32.DefWindowProcW(hwnd, msg, wParam, lParam)

    root.deiconify()
    root.update()
    hwnd = root.winfo_id()
    if not hwnd:
        raise Exception("Cannot get root window hwnd")

    root.dnd_window_protocol = WNDPROC(window_protocol)
    user32.SetWindowLongPtrW(hwnd, GWL_WNDPROC, ctypes.cast(root.dnd_window_protocol, ctypes.c_void_p))
    shell32.DragAcceptFiles(hwnd, True)
