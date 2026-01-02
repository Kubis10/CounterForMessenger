import importlib
import tkinter as tk
from tkinter import ttk

from gui import icons


class Theme:
    """
    Theme interface that different theme implementations inherit.
    """
    name : str
    def apply(self, style: ttk.Style):
        raise NotImplementedError

class DefaultTheme(Theme):
    name = "default"
    def apply(self, style: ttk.Style):
        style.theme_use("clam")

        # Global background / foreground defaults
        # light gray background
        # black text
        # white for entries
        style.configure(".",background="#f0f0f0", foreground="#000000", fieldbackground="#ffffff")

        # Navigation panel and main panel styles
        style.configure("Nav.TFrame", background="#e0e0e0")  # slightly darker gray
        style.configure("Main.TFrame", background="#f0f0f0")

        # Treeview selected colors
        style.map("Custom.Treeview", background=[("selected", "#3399ff")], foreground=[("selected", "#ffffff")])

        # Treeview headings
        style.configure("Treeview.Heading", background="#d0d0d0", foreground="#000000", relief="flat")
        style.map("Treeview.Heading", background=[("active", "#c0c0c0")])

        # Buttons
        style.configure("TButton", background="#e0e0e0", foreground="#000000", padding=(14, 10), relief="flat", borderwidth=0)
        style.map("TButton",
                  background=[("active", "#d0d0d0"),
                              ("pressed", "#3399ff")
                  ],
                  foreground=[("disabled", "#888888")
                  ]
        )

        # Entry widgets
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000", insertcolor="#000000")

        # Custom labels (like your title labels)
        style.configure("Custom.TLabel", foreground='#232323', font=('Arial', 15))


class DarkTheme(Theme):
    name = "dark"
    def apply(self, style: ttk.Style):
        style.theme_use("clam")

        style.configure(".", background="#0d1117", foreground="#c9d1d9", fieldbackground="#161b22")

        style.configure("Nav.TFrame", background="#161b22")
        style.configure("Main.TFrame", background="#0d1117")
        style.configure("Top_Bar.TFrame", background="#00002a")

        style.map("Custom.Treeview", background=[("selected", "#1f6feb")], foreground=[("selected", "#ffffff")])

        style.configure("Treeview.Heading", background="#161b22", foreground="#c9d1d9", relief="flat")

        style.map("Treeview.Heading", background=[("active", "#30363d")])

        style.configure("TButton", background="#161b22", foreground="#c9d1d9", padding=(14, 10),  relief="flat", borderwidth=0)

        style.configure("Custom.TLabel", foreground='#ffffff', font=('Arial', 15))

        style.map("TButton",
            background=[
                ("active", "#30363d"),
                ("pressed", "#1f6feb")
            ],
            foreground=[
                ("disabled", "#8b949e")
            ]
        )
        style.configure("TEntry", fieldbackground="#161b22", foreground="#c9d1d9", insertcolor="#c9d1d9")


class ThemeManager:
    """
    Stores information of the application gui (images, style, current theme, available themes)
    and manages their state based of the preferred theme
    """

    def __init__(self):
        self.style = ttk.Style()
        self.themes: dict[str, Theme] = {}
        self._images = {}
        self.current_theme: str | None = None

    def register(self, theme: Theme):
        self.themes[theme.name] = theme

    def _load_images(self):
        self._images.clear()
        for key, path in icons.ICON_PATHS[self.current_theme].items():
            self._images[key] = tk.PhotoImage(file=path)

    def apply(self, name:str):
        if name not in self.themes:
            raise ValueError(f"Theme '{name}' is not registered")
        self.themes[name].apply(self.style)
        self.current_theme = name
        self._load_images()

    def get_icon(self, name: str) -> tk.PhotoImage:
        return self._images[name]
