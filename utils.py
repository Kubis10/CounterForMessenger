"""
Utility functions for the CounterForMessenger application.
"""
import tkinter as tk
from PIL import Image, ImageTk
from os import listdir

def set_icon(window):
    """
    Sets the icon of a tkinter window to the CFM icon.

    Args:
        window: A tkinter window object
    """
    im = Image.open('assets/CFM.ico')
    photo = ImageTk.PhotoImage(im)
    window.wm_iconphoto(True, photo)


def set_resolution(window, width, height):
    """
    Centers the window on the screen with the specified dimensions.

    Args:
        window: A tkinter window object
        width: The desired width of the window
        height: The desired height of the window
    """
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')


def existing_languages():
    """
    Returns a list of available language modules.

    Returns:
        List of language module names without the .py extension
    """
    return [lang.title().split('.')[0] for lang in listdir('langs') if lang != '__pycache__']


# Safeguard for the treeview automated string conversion problem
PREFIX = '<@!PREFIX>'
