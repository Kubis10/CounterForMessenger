"""
Theme manager for CounterForMessenger
Allows switching between light and dark themes
"""

class ThemeManager:
    """Manages themes for the application"""

    # Light theme colors
    LIGHT_THEME = {
        "bg_primary": "#f5f5f5",
        "bg_secondary": "#e0e0e0",
        "bg_accent": "#d0d0d0",
        "fg_primary": "#000000",
        "fg_secondary": "#333333",
        "button_bg": "#e0e0e0",
        "button_fg": "#000000",
        "treeview_bg": "#ffffff",
        "treeview_fg": "#000000",
        "selected_bg": "#0078d7",
        "selected_fg": "#ffffff",
        "hover_bg": "#e5f1fb"
    }

    # Dark theme colors - bardziej estetyczna kolorystyka
    DARK_THEME = {
        "bg_primary": "#1e1e2e",     # Ciemny niebieski zamiast szarego
        "bg_secondary": "#181825",    # Ciemniejszy niebieski dla bocznego panelu
        "bg_accent": "#313244",       # Jaśniejszy akcent dla wyróżnienia elementów
        "fg_primary": "#cdd6f4",      # Jasny niebieskoszary tekst zamiast czystej bieli
        "fg_secondary": "#a6adc8",    # Jaśniejszy tekst drugorzędny
        "button_bg": "#45475a",       # Jaśniejsze tło przycisku z odcieniem niebieskim
        "button_fg": "#cdd6f4",       # Kolor tekstu przycisków dopasowany do głównego tekstu
        "treeview_bg": "#1e1e2e",     # Tło drzewa zgodne z głównym tłem
        "treeview_fg": "#cdd6f4",     # Tekst drzewa zgodny z głównym tekstem
        "selected_bg": "#7f849c",     # Subtelniejszy niebieski dla zaznaczenia
        "selected_fg": "#ffffff",     # Biały tekst na zaznaczeniu
        "hover_bg": "#585b70"         # Jaśniejszy odcień przy najechaniu
    }

    def __init__(self):
        """Initialize theme manager with dark theme as default"""
        self.current_theme = "dark"
        self.colors = self.DARK_THEME.copy()

    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme

    def get_colors(self):
        """Get the current theme colors dictionary"""
        return self.colors

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.colors = self.LIGHT_THEME.copy()
        else:
            self.current_theme = "dark"
            self.colors = self.DARK_THEME.copy()
        return self.colors

    def apply_theme_to_styles(self, style):
        """
        Apply the current theme to ttk styles

        Args:
            style: ttk.Style object to configure
        """
        colors = self.colors

        # Resetujemy wszystkie style przed aplikowaniem nowych
        style.theme_use('default')

        # Configure main background styles
        style.configure('TFrame', background=colors["bg_primary"])
        style.configure('Nav.TFrame', background=colors["bg_secondary"])
        style.configure('Main.TFrame', background=colors["bg_primary"])

        # Configure button styles - upewniamy się, że kolor tekstu jest jawnie ustawiony
        style.configure('TButton',
                       background=colors["button_bg"],
                       foreground=colors["button_fg"])

        # Jawnie wymuszamy kolory dla wszystkich stanów przycisku
        style.map('TButton',
                 background=[('active', colors["hover_bg"]),
                             ('pressed', colors["bg_accent"]),
                             ('disabled', colors["bg_secondary"])],
                 foreground=[('active', colors["button_fg"]),
                             ('pressed', colors["button_fg"]),
                             ('disabled', colors["fg_secondary"])])

        # Specjalny styl dla przycisków menu
        style.configure('Menu.TButton',
                       background=colors["bg_secondary"],
                       foreground=colors["fg_primary"])
        style.map('Menu.TButton',
                 background=[('active', colors["hover_bg"]),
                             ('pressed', colors["bg_accent"])],
                 foreground=[('active', colors["fg_primary"]),
                             ('pressed', colors["fg_primary"])])

        # Styl dla przycisku przełączania motywu
        style.configure('ThemeToggle.TButton',
                       background=colors["bg_accent"],
                       foreground=colors["fg_primary"])
        style.map('ThemeToggle.TButton',
                 background=[('active', colors["hover_bg"])],
                 foreground=[('active', colors["fg_primary"])])

        # Custom treeview style for main display
        style.configure('Custom.Treeview',
                       background=colors["treeview_bg"],
                       foreground=colors["treeview_fg"],
                       fieldbackground=colors["treeview_bg"])
        style.map('Custom.Treeview',
                 background=[('selected', colors["selected_bg"])],
                 foreground=[('selected', colors["selected_fg"])])

        # Header style for treeview
        style.configure('Custom.Treeview.Heading',
                       background=colors["bg_accent"],
                       foreground=colors["fg_primary"])
        style.map('Custom.Treeview.Heading',
                 background=[('active', colors["hover_bg"])])

        # Labels
        style.configure('TLabel',
                       background=colors["bg_primary"],
                       foreground=colors["fg_primary"])

        # Entry style (search input, etc.)
        style.configure('TEntry',
                       background=colors["bg_accent"],
                       foreground=colors["fg_primary"],
                       fieldbackground=colors["bg_accent"])

        # Dodatkowe style dla widgetów ttk
        style.configure('TCheckbutton',
                       background=colors["bg_primary"],
                       foreground=colors["fg_primary"])
        style.configure('TRadiobutton',
                       background=colors["bg_primary"],
                       foreground=colors["fg_primary"])
