"""
Configuration page module for CounterForMessenger
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from utils import existing_languages

class ConfigurationPage(tk.Frame):
    """Configuration panel for initial setup"""

    def __init__(self, parent, controller):
        """
        Initialize the configuration page

        Args:
            parent: Parent widget
            controller: Controller object for managing application state
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.module = self.controller.lang_mdl

        # Set up frame title
        tk.Label(
            self, text=self.module.TITLE_INITIAL_CONFIG, font=('Ariel', 24)
        ).pack(side='top', pady=10)

        # Ask for directory and show selected path
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_INBOX}:'
        ).pack(side='top', pady=5)
        self.directory_label = tk.Label(self, text=self.module.TITLE_NO_SELECTION)
        self.directory_label.pack(side='top', pady=5)

        # Show 'Open File Explorer' button
        ttk.Button(
            self, text=f'{self.module.TITLE_OPEN_FE}...', padding=5, command=self.open_file_explorer
        ).pack(side='top', pady=5)

        # Create 'from' date entry using tkcalendar
        tk.Label(self, text=f'{self.module.TITLE_FROM}:').pack(side='top', pady=5)
        self.from_date_entry = DateEntry(self, date_pattern='yyyy-mm-dd', width=12, allow_none=True, year=2000, month=1,
                                       day=1)
        self.from_date_entry.pack(side='top', pady=10)

        # Create 'to' date entry using tkcalendar
        tk.Label(self, text=f'{self.module.TITLE_TO}:').pack(side='top', pady=5)
        self.to_date_entry = DateEntry(self, date_pattern='yyyy-mm-dd', width=12, allow_none=True)
        self.to_date_entry.pack(side='top', pady=10)

        # Ask for Facebook name
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_USERNAME}:',
        ).pack(side='top', pady=15)
        self.username_label = ttk.Entry(self, width=25)
        self.username_label.pack(side='top', pady=5)

        # Set up language dropdown
        self.language_label = tk.StringVar(self, value='English')
        ttk.OptionMenu(
            self, self.language_label, 'English', *existing_languages()
        ).pack(side='top', pady=10)

        # Load save button
        ttk.Button(
            self, text=self.module.TITLE_SAVE, padding=7, command=self.setup
        ).pack(side='top', pady=40)

    def setup(self):
        """
        Save configuration and navigate to main page
        Invoked by pressing the save button
        """
        directory = self.directory_label.cget('text')
        if not directory or directory == self.module.TITLE_NO_SELECTION:
            messagebox.showwarning(
                "Missing Information",
                "Please select the folder containing your Facebook data."
            )
            return

        # Communicate provided data with the master window
        self.controller.update_data(
            self.username_label.get(),
            directory,
            self.language_label.get(),
            self.from_date_entry.get_date(),
            self.to_date_entry.get_date()
        )
        # Go to main page
        self.controller.show_frame("MainPage")

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
