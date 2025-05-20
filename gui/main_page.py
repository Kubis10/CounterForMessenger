"""
Main page module for CounterForMessenger
"""
import tkinter as tk
from tkinter import ttk
from os import listdir
from functools import cmp_to_key

from popups.statistics_popup import StatisticsPopup
from popups.multi_sort_popup import MultiSortPopup
from popups.loading_popup import LoadingPopup
from utils import PREFIX

class MainPage(tk.Frame):
    """Main panel of the application showing message statistics"""

    def __init__(self, parent, controller):
        """
        Initialize the main page

        Args:
            parent: Parent widget
            controller: Controller object for managing application state
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.module = self.controller.lang_mdl

        # Get theme colors
        self.colors = self.controller.theme_manager.get_colors()

        # Apply theme to the application
        self.style = ttk.Style()
        self.controller.theme_manager.apply_theme_to_styles(self.style)

        # Configure the background color of the root frame
        self.configure(background=self.colors["bg_primary"])

        # Main layout setup - using more modern grid layout
        self.grid_columnconfigure(0, weight=0)  # Left sidebar - fixed width
        self.grid_columnconfigure(1, weight=1)  # Content area - expandable
        self.grid_rowconfigure(0, weight=1)     # Main content - expandable

        # Create sidebar panel
        self.sidebar = ttk.Frame(self, padding=10, style='Nav.TFrame', width=200)
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.sidebar.grid_propagate(False)  # Fixed width

        # Create header and content frame
        self.content_frame = ttk.Frame(self, style='Main.TFrame')
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Header - fixed height
        self.content_frame.grid_rowconfigure(1, weight=1)  # Content - expandable

        # Header frame for title and theme toggle
        self.header_frame = ttk.Frame(self.content_frame, style='Main.TFrame', padding=10)
        self.header_frame.grid(row=0, column=0, sticky='ew')
        self.header_frame.grid_columnconfigure(0, weight=1)  # Title - expandable
        self.header_frame.grid_columnconfigure(1, weight=0)  # Theme toggle - fixed width

        # Main application title
        self.title_label = ttk.Label(
            self.header_frame,
            text=f'{self.module.TITLE_APP_NAME}',
            font=('Arial', 24),
            style='TLabel'
        )
        self.title_label.grid(row=0, column=0, sticky='w', pady=10)

        # Theme toggle button
        theme_text = "☀️ Jasny motyw" if self.controller.theme_manager.get_current_theme() == "dark" else "🌙 Ciemny motyw"
        self.theme_button = ttk.Button(
            self.header_frame,
            text=theme_text,
            style='ThemeToggle.TButton',
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=1, sticky='e', padx=10)

        # Main content area
        self.main_content = ttk.Frame(self.content_frame, style='Main.TFrame', padding=10)
        self.main_content.grid(row=1, column=0, sticky='nsew')

        # Set up the treeview with scrollbars in the main content
        self.setup_treeview()

        # Setup sidebar with actions
        self.setup_sidebar()

        # Setup info panel beneath the treeview
        self.setup_info_panel()

    def setup_treeview(self):
        """Set up the treeview component with scrollbars"""
        # Create a frame to hold the treeview and scrollbars
        treeview_frame = ttk.Frame(self.main_content, style='Main.TFrame')
        treeview_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical")
        x_scrollbar = ttk.Scrollbar(treeview_frame, orient="horizontal")

        # Create treeview with both scrollbars
        self.treeview = ttk.Treeview(
            treeview_frame,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            style='Custom.Treeview',
            height=20
        )

        # Configure scrollbars
        y_scrollbar.config(command=self.treeview.yview)
        x_scrollbar.config(command=self.treeview.xview)

        # Place components using grid
        self.treeview.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure treeview frame grid
        treeview_frame.grid_columnconfigure(0, weight=1)
        treeview_frame.grid_rowconfigure(0, weight=1)

        # Define columns
        columns = {
            'name': self.module.TITLE_NAME,
            'pep': self.module.TITLE_PARTICIPANTS,
            'type': self.module.TITLE_CHAT_TYPE,
            'msg': self.module.TITLE_NUMBER_OF_MSGS,
            'call': self.module.TITLE_CALL_DURATION,
            'photos': self.module.TITLE_NUMBER_OF_PHOTOS,
            'gifs': self.module.TITLE_NUMBER_OF_GIFS,
            'videos': self.module.TITLE_NUMBER_OF_VIDEOS,
            'files': self.module.TITLE_NUMBER_OF_FILES,
        }

        # Configure treeview
        self.treeview.column('#0', width=0, stretch=tk.NO)
        self.treeview['columns'] = tuple(columns.keys())

        # Configure column widths more appropriately
        self.treeview.column('name', width=200, minwidth=100)
        self.treeview.column('pep', width=150, minwidth=80)
        self.treeview.column('type', width=100, minwidth=80)
        self.treeview.column('msg', width=100, minwidth=80)
        self.treeview.column('call', width=100, minwidth=80)
        self.treeview.column('photos', width=80, minwidth=50)
        self.treeview.column('gifs', width=80, minwidth=50)
        self.treeview.column('videos', width=80, minwidth=50)
        self.treeview.column('files', width=80, minwidth=50)

        # Add column headings
        for keyword, text in columns.items():
            self.treeview.heading(keyword, text=text, anchor='center')

        # Bind events
        self.treeview.bind('<Button-3>', lambda event: self.deselect())
        self.treeview.bind('<Double-1>', lambda event: self.show_statistics())

        # Ordered list of columns
        self.columns = list(columns.keys())
        self.column_titles = columns

        # Ordered list of columns to sort by
        self.sort_columns = []

        # Store the biases for each column in one place
        self.column_biases = {
            "name": "stringwise",
            "pep": "numberwise",
            "type": "stringwise",
            "msg": "numberwise",
            "call": "numberwise",
            "photos": "numberwise",
            "gifs": "numberwise",
            "videos": "numberwise",
            "files": "numberwise",
        }

        # Store whether each column is reversed (for multi-sort)
        self.columns_reversed = dict()

    def setup_sidebar(self):
        """Set up the sidebar with menu options"""
        # Add app logo/title at the top of sidebar
        logo_frame = ttk.Frame(self.sidebar, style='Nav.TFrame')
        logo_frame.pack(fill='x', pady=(0, 20))

        ttk.Label(
            logo_frame,
            text="CFM",
            font=('Arial', 16, 'bold'),
            foreground=self.colors["fg_secondary"],
            background=self.colors["bg_secondary"],
        ).pack(side='top', pady=10)

        # Create main menu buttons
        menu_buttons = [
            ("home", self.module.TITLE_HOME, self.controller.ICON_HOME, None),
            ("upload", self.module.TITLE_UPLOAD_MESSAGES, self.controller.ICON_STATUS_VISIBLE, self.upload_data),
            ("search", self.module.TITLE_SEARCH, self.controller.ICON_SEARCH, self.show_search),
            ("sort", self.module.TITLE_MULTI_SORT, None, self.show_multi_sort),
            ("profile", self.module.TITLE_PROFILE, self.controller.ICON_PROFILE, self.show_profile),
            ("settings", self.module.TITLE_SETTINGS, self.controller.ICON_SETTINGS, self.show_settings),
            ("exit", self.module.TITLE_EXIT, self.controller.ICON_EXIT, self.controller.destroy)
        ]

        # Create a frame for search (initially hidden)
        self.search_frame = ttk.Frame(self.sidebar, style='Nav.TFrame')

        # Create search entry and button
        self.search_entry = ttk.Entry(self.search_frame, width=15)
        self.search_entry.pack(side='left', padx=5)

        ttk.Button(
            self.search_frame,
            text="🔍",
            style='Menu.TButton',
            width=3,
            command=self.search
        ).pack(side='right')

        # Add all menu buttons
        for i, (name, text, icon, command) in enumerate(menu_buttons):
            btn = ttk.Button(
                self.sidebar,
                text=text,
                image=icon if icon else None,
                compound='left' if icon else 'none',
                style='Menu.TButton',
                padding=10,
                command=command
            )
            # Style exit button differently
            if name == "exit":
                btn.pack(side='bottom', fill='x', pady=5)
            else:
                btn.pack(fill='x', pady=5)

                # Save reference for search button to toggle search frame
                if name == "search":
                    self.search_button = btn

    def setup_info_panel(self):
        """Set up information panel beneath the treeview"""
        info_frame = ttk.Frame(self.main_content, style='Main.TFrame', padding=5)
        info_frame.pack(side='bottom', fill='x', pady=10)

        # Status information
        status_text = f"{self.module.TITLE_TOTAL_MESSAGES}: {self.controller.total_messages} | "
        status_text += f"{self.module.TITLE_SENT_MESSAGES}: {self.controller.sent_messages}"

        self.status_label = ttk.Label(
            info_frame,
            text=status_text,
            foreground=self.colors["fg_secondary"],
            background=self.colors["bg_primary"]
        )
        self.status_label.pack(side='left')

        # Instructions
        help_text = f"• {self.module.TITLE_UPLOAD_MESSAGES} - zaimportuj dane | "
        help_text += f"• Podwójne kliknięcie - pokaż statystyki | "
        help_text += f"• Prawy przycisk - odznacz"

        help_label = ttk.Label(
            info_frame,
            text=help_text,
            foreground=self.colors["fg_secondary"],
            background=self.colors["bg_primary"]
        )
        help_label.pack(side='right')

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.controller.toggle_theme()

    def show_search(self):
        """Show or hide the search panel"""
        if self.search_frame.winfo_ismapped():
            self.search_frame.pack_forget()
        else:
            # Insert after the search button
            self.search_frame.pack(fill='x', pady=5)
            self.search_entry.focus_set()

    def show_multi_sort(self):
        """Show the multi-sort popup dialog"""
        MultiSortPopup(
            self.controller,
            self.columns[:],  # Pass a copy
            {**self.column_titles},  # Pass a copy
            self.columns_reversed,
            self.sort_columns,
            lambda: self.apply_multi_sort()
        )

    def show_profile(self):
        """Show the profile popup"""
        from popups.profile_popup import ProfilePopup
        ProfilePopup(self.controller)

    def show_settings(self):
        """Show the settings popup"""
        from popups.settings_popup import SettingsPopup
        SettingsPopup(self.controller)

    def deselect(self):
        """
        Remove current treeview selection
        Invoked on <Button-3> (right-click)
        """
        self.treeview.selection_remove(self.treeview.selection())

    def search(self):
        """
        Search for text in the treeview and highlight matching rows
        Highlight all messages whose values contain the query at least once
        """
        query = self.search_entry.get()
        selections = []
        for child in self.treeview.get_children():
            for value in self.treeview.item(child)['values']:
                if str(value).lower().find(query.lower()) != -1:
                    # Selection accepted, save it and move on
                    selections.append(child)
                    break
        self.treeview.selection_set(selections)

        # Update status label to show search results
        if query:
            self.status_label.config(
                text=f"{self.module.TITLE_SEARCH}: '{query}' - {len(selections)} wyników"
            )

    def upload_data(self):
        """
        Load data into the treeview
        Invoked by pressing the upload button
        """
        # Wipe all previous data in treeview
        self.treeview.delete(*self.treeview.get_children())
        try:
            directory = self.controller.get_directory()
            conversations = len(listdir(directory))
            LoadingPopup(self.controller, conversations, self.treeview)

            # Bind general purpose handler to column clicks
            self.treeview.heading('msg', command=lambda col='msg': self.click_column(col, False, 'numberwise'))
            self.treeview.heading('name', command=lambda col='name': self.click_column(col, False, 'stringwise'))
            self.treeview.heading('type', command=lambda col='type': self.click_column(col, False, 'stringwise'))
            self.treeview.heading('call', command=lambda col='call': self.click_column(col, False, 'numberwise'))
            self.treeview.heading('photos', command=lambda col='photos': self.click_column(col, False, 'numberwise'))
            self.treeview.heading('gifs', command=lambda col='gifs': self.click_column(col, False, 'numberwise'))
            self.treeview.heading('videos', command=lambda col='videos': self.click_column(col, False, 'numberwise'))
            self.treeview.heading('files', command=lambda col='files': self.click_column(col, False, 'numberwise'))

            # Update status label with message counts
            self.status_label.config(
                text=f"{self.module.TITLE_TOTAL_MESSAGES}: {self.controller.total_messages} | "
                     f"{self.module.TITLE_SENT_MESSAGES}: {self.controller.sent_messages}"
            )

        except FileNotFoundError:
            print('>MainPage/upload_data THROWS FileNotFoundError, NOTIFY OP IF UNEXPECTED')

    def click_column(self, col, order, bias):
        """
        Handle column click for sorting
        Clicking a column (and therefore doing a sort on it) discards multi-sort info

        Args:
            col: Column to sort by
            order: Sort order (True for descending, False for ascending)
            bias: Sort bias (stringwise or numberwise)
        """
        self.sort_columns.clear()
        self.columns_reversed.clear()
        self.sort_treeview(col, order, bias)

    def sort_treeview(self, column, order, bias):
        """
        Sort treeview by column

        Args:
            column: Column to sort by
            order: Sort order (True for descending, False for ascending)
            bias: Sort bias (stringwise or numberwise)
        """
        # Cache the get_children call
        children = self.treeview.get_children('')
        # Retrieve the column's contents
        contents = [(self.treeview.set(k, column), k) for k in children]
        # For number-wise sorting, convert to integers once, beforehand
        if bias == 'numberwise':
            # Convert strings to integers and sort
            contents = [(int(val), k) for val, k in contents]
            contents.sort(key=lambda t: t[0], reverse=order)
        else:
            # For string-wise sorting, Python's default sort is string-wise
            contents.sort(reverse=order)
        # Reinsert the items into the treeview in sorted order
        for index, (val, k) in enumerate(contents):
            self.treeview.move(k, '', index)
        # Reverse the order for the next sort
        self.treeview.heading(column, command=lambda: self.sort_treeview(column, not order, bias))

    def apply_multi_sort(self):
        """
        Sort the treeview based on multiple columns

        This function sorts the rows based on the ordering stored in `self.sort_columns`.
        To achieve this, the `compare` function tries to break ties based
        each successive column in the ordering, before giving up and declaring a tie.
        """
        def compare(a, b, ordering):
            # a and b are *rows* of data (dictionaries)
            if ordering == []:
                # We have nothing left to break ties on
                return 0

            # We will try to break the tie on this column
            column_name = ordering[0]
            bias = self.column_biases[column_name]
            reverse_multiplier = -1 if self.columns_reversed[column_name] else 1

            # Retrieve the appropriate column from each row
            a_value = a[column_name]
            b_value = b[column_name]

            if bias == "stringwise":
                if a_value < b_value: return -1 * reverse_multiplier
                elif a_value > b_value: return 1 * reverse_multiplier
            elif bias == "numberwise":
                a_value, b_value = int(a_value), int(b_value)
                if a_value < b_value: return -1 * reverse_multiplier
                elif a_value > b_value: return 1 * reverse_multiplier
            else:
                raise ValueError(f"Undefined bias '{bias}'")

            # If we made it here, then the values are equal when compared
            # on the current column value. Continue with the next column in the ordering.
            return compare(a, b, ordering[1:])

        def compare_wrapper(a, b):
            (_, a) = a
            (_, b) = b
            return compare(a, b, self.sort_columns)

        # Retrieve all of the rows of the dataset
        children = self.treeview.get_children('')
        rows = [
            (k,
                {
                    column_name: self.treeview.set(k, column_name)
                    for column_name in self.column_biases
                }
            )
            for k in children
        ]

        rows.sort(key=cmp_to_key(compare_wrapper))

        for (idx, (k, _)) in enumerate(rows):
            self.treeview.move(k, '', idx)

    def show_statistics(self):
        """
        Show statistics popup for selected conversation
        Invoked on double left click on any treeview listing
        """
        try:
            selection = self.treeview.item(self.treeview.selection()[0]).get('values', [])
            if len(selection) == 0:
                return
            # Treeview automated conversion problem, read StatisticsPopup comments
            # Removing prefix safeguard
            StatisticsPopup(self.controller, selection[10].replace(PREFIX, ''))
        except IndexError:
            # Miss-click / empty selection, nothing to show here
            return
