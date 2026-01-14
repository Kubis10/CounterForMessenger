"""
Settings popup dialog for CounterForMessenger
"""
import tkinter as tk
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
from datetime import date, datetime
from utils import set_icon, set_resolution, existing_languages

class SettingsPopup(tk.Toplevel):
    """Settings popup window for adjusting application configuration"""

    def __init__(self, controller, parent):
        """
        Initialize settings popup

        Args:
            controller: Controller object for managing application state
        """
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.parent = parent
        self.module = self.controller.lang_mdl
        set_resolution(self, 800, 600)

        # Settings window customization
        self.title(self.module.TITLE_SETTINGS)
        set_icon(self)
        self.focus_set()
        self.grab_set()

        # Ask for directory and show selected path
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_INBOX}:'
        ).pack(side='top', pady=16)
        self.directory_label = tk.Label(self, text=self.controller.get_directory())
        self.directory_label.pack(side='top', pady=15)

        # Show 'Open File Explorer' button
        ttk.Button(
            self, text=f'{self.module.TITLE_OPEN_FE}...', padding=5, command=self.open_file_explorer
        ).pack(side='top', pady=5)

        # Ask for Facebook name
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_USERNAME}:',
        ).pack(side='top', pady=15)
        self.username_label = ttk.Entry(self, width=25, style="TEntry")
        self.username_label.insert(0, self.controller.get_username())
        self.username_label.pack(side='top', pady=5)

        # Create date entries
        self._create_date_entries()

        # Set up language listbox
        self.language_label = tk.StringVar(self, value=self.controller.get_language())
        ttk.OptionMenu(
            self, self.language_label, self.controller.get_language(), *existing_languages()
        ).pack(side='top', pady=10)

        # Create setting up for theme change
        tk.Label(self, text=f'{self.module.TITLE_THEME}').pack(side='top', pady=1)
        self.theme_var = tk.StringVar(
            value=controller.theme_manager.current_theme
        )

        # Safely determine initial theme value, falling back if no theme is currently set
        themes = controller.theme_manager.themes
        current_theme = controller.theme_manager.current_theme
        if current_theme is None:
            # Use the first available theme if any exist, otherwise default to empty string
            current_theme = next(iter(themes), "") if themes else ""
        self.theme_var = tk.StringVar(value=current_theme)

        ttk.Combobox(
            self,
            textvariable=self.theme_var,
            values=list(controller.theme_manager.themes.keys()),
            state="readonly"
        ).pack(side='top', pady=10)

        # Load save button
        ttk.Button(
            self, text=self.module.TITLE_SAVE, padding=7, command=self.setup
        ).pack(side='top', pady=40)


    def _create_date_entries(self):
        """Create the from and to date entries with proper initial values"""
        # Handle 'from' date
        date_entry = self.controller.get_from_date_entry()
        load_from_date = self._parse_date(date_entry)

        tk.Label(self, text=f'{self.module.TITLE_FROM}:').pack(side='top', pady=10)
        self.from_date_entry = DateEntry(
            self,
            date_pattern='yyyy-mm-dd',
            width=12,
            allow_none=True,
            year=load_from_date.year if load_from_date else 2000,
            month=load_from_date.month if load_from_date else 1,
            day=load_from_date.day if load_from_date else 1
        )
        self.from_date_entry.pack(side='top', pady=5)

        # Handle 'to' date
        date_entry = self.controller.get_to_date_entry()
        load_to_date = self._parse_date(date_entry)

        tk.Label(self, text=f'{self.module.TITLE_TO}:').pack(side='top', pady=10)
        self.to_date_entry = DateEntry(
            self,
            date_pattern='yyyy-mm-dd',
            width=12,
            allow_none=True,
            year=load_to_date.year if load_to_date else datetime.now().year,
            month=load_to_date.month if load_to_date else datetime.now().month,
            day=load_to_date.day if load_to_date else datetime.now().day
        )
        self.to_date_entry.pack(side='top', pady=5)

    def _parse_date(self, date_entry):
        """
        Parse various date formats into a datetime.date object

        Args:
            date_entry: A date entry which could be a tuple, date object or string

        Returns:
            datetime.date object or None if parsing fails
        """
        if not date_entry:
            return None

        if isinstance(date_entry, tuple) and len(date_entry) == 1:
            if isinstance(date_entry[0], date):
                return date_entry[0]

        if isinstance(date_entry, date):
            return date_entry

        try:
            # If it's a string, parse it
            return datetime.strptime(str(date_entry), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            # Default to today if parsing fails
            return datetime.now().date()

    def setup(self):
        """
        Save settings and close popup
        Invoked by pressing the save button
        """
        # Communicate provided data with the master window
        self.controller.update_data(
            self.username_label.get(),
            self.directory_label.cget('text'),
            self.language_label.get(),
            self.from_date_entry.get_date(),
            self.to_date_entry.get_date(),
            self.theme_var.get(),
        )
        self.controller.change_theme(self.theme_var.get())
        self.parent.set_treeview_theme()
        self.parent.set_icons()
        # Exit popup
        self.destroy()

    def open_file_explorer(self):
        """
        Open file explorer to select directory
        Invoked by pressing the 'Open file explorer...' button
        """
        # Open file explorer, extract given path and update label text message
        path = f'{tk.filedialog.askdirectory()}/'
        self.directory_label.config(
            text=(self.module.TITLE_NO_SELECTION if path == '' or path.isspace() or path == '/' else path)
        )
