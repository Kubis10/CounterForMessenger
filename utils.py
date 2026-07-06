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


# Plain tk widget classes that don't automatically pick up ttk.Style changes
_THEMED_TK_CLASSES = ("Toplevel", "Frame", "Label", "Listbox", "Button")


def apply_theme(window, theme):
    """
    Applies the active theme's colors to plain tk widgets (Toplevel, Frame, Label,
    Listbox, Button) within a window, including all of its children.

    ttk widgets (ttk.Button, ttk.Label, ttk.Entry, etc.) are already themed globally
    through ttk.Style whenever the theme changes, but plain `tk` widgets used in some
    popups/pages are not - they must be colored manually or they always show the
    system default (light) colors regardless of the active theme.

    Args:
        window: Root tk.Toplevel or tk.Frame to theme, including all its children
        theme: Active Theme instance providing color constants (see gui.theme)
    """
    widget_class = window.winfo_class()
    try:
        if widget_class in ("Toplevel", "Frame"):
            window.configure(bg=theme.BACKGROUND)
        elif widget_class == "Label":
            window.configure(bg=theme.BACKGROUND, fg=theme.FOREGROUND)
        elif widget_class == "Listbox":
            window.configure(
                bg=theme.LISTBOX_BG, fg=theme.LISTBOX_FG,
                selectbackground=theme.LISTBOX_SELECT_BG, selectforeground=theme.LISTBOX_SELECT_FG,
                highlightthickness=0
            )
        elif widget_class == "Button":
            window.configure(
                bg=theme.BUTTON_BG, fg=theme.FOREGROUND,
                activebackground=theme.BUTTON_ACTIVE_BG, activeforeground=theme.FOREGROUND
            )
    except tk.TclError:
        # Some widgets (e.g. tkcalendar's internal frames) don't support all options
        pass

    for child in window.winfo_children():
        apply_theme(child, theme)


# Safeguard for the treeview automated string conversion problem
PREFIX = '<@!PREFIX>'
