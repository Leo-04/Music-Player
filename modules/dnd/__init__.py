import sys

if sys.platform == 'win32':
    from .windows_dnd import dnd
else:
    from tkinter import Tk


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
