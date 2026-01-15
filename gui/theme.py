import tkinter as tk
from tkinter import ttk

from gui import icons


class Theme:
    """
    Theme interface that different theme implementations inherit.
    """
    name: str
    def apply(self, style: ttk.Style):
        raise NotImplementedError

class DefaultTheme(Theme):
    name = "default"
    TREEVIEW_EVEN_ROW = "#ffffff"
    TREEVIEW_ODD_ROW = "#c4c4c4"

    def apply(self, style: ttk.Style):
        style.theme_use("clam")

        # Global background / foreground defaults
        # light gray background
        # black text
        # white for entries
        style.configure(".", background="#f0f0f0", foreground="#000000", fieldbackground="#ffffff")

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
    TREEVIEW_EVEN_ROW = "#0d1117"
    TREEVIEW_ODD_ROW = "#161b22"

    def apply(self, style: ttk.Style):
        style.theme_use("clam")

        style.configure(".", background="#0d1117", foreground="#c9d1d9", fieldbackground="#161b22")

        style.configure("Nav.TFrame", background="#161b22")
        style.configure("Main.TFrame", background="#0d1117")
        style.configure("Top_Bar.TFrame", background="#00002a")

        style.map("Custom.Treeview", background=[("selected", "#1f6feb")], foreground=[("selected", "#ffffff")])

        style.configure("Treeview.Heading", background="#161b22", foreground="#c9d1d9", relief="flat")

        style.map("Treeview.Heading", background=[("active", "#30363d")])

        style.configure("TButton", background="#161b22", foreground="#c9d1d9", padding=(14, 10), relief="flat", borderwidth=0)

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
    and manages their state based on the preferred theme
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
        theme = self.current_theme

        if theme is None or theme not in icons.ICON_PATHS:
            raise ValueError(f"No icon paths configured for theme '{theme}'")

        for key, path in icons.ICON_PATHS[self.current_theme].items():
            try:
                self._images[key] = tk.PhotoImage(file=path)
            except tk.TclError as e:
                raise RuntimeError(f"Failed to load icon '{key}' from path '{path}': {e}") from e

    def apply(self, name: str):
        if name not in self.themes:
            raise ValueError(f"Theme '{name}' is not registered")
        self.themes[name].apply(self.style)
        self.current_theme = name
        self._load_images()

    def get_icon(self, name: str) -> tk.PhotoImage:
        """
        Retrieve an icon by name.
        If the icon is not available (e.g. theme not applied yet or invalid name),
        return a small placeholder image instead of raising KeyError.
        """
        try:
            return self._images[name]
        except KeyError:
            # Lazily create and cache a placeholder image to avoid repeated allocations.
            placeholder_key = "_placeholder"
            placeholder = self._images.get(placeholder_key)
            if placeholder is None:
                placeholder = tk.PhotoImage(width=1, height=1)
                self._images[placeholder_key] = placeholder
            return placeholder
