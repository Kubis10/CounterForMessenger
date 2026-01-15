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

        # Frame style setup
        self.controller.change_theme("default")
        self.nav = ttk.Frame(self, padding=20, style='Nav.TFrame')
        self.main = ttk.Frame(self, style='Main.TFrame')
        self.top_bar = ttk.Frame(self.main, style="Main.TFrame")
        self.top_bar.pack(side="top", fill="x", padx=10, pady=(10, 5))

        # Build treeview for message data projection
        scrollbar = tk.Scrollbar(self.main)
        self.treeview = ttk.Treeview(self.main, height=20, yscrollcommand=scrollbar.set, style='Custom.Treeview')
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
        self.treeview.column('#0', width=0, stretch=tk.NO)
        self.treeview['columns'] = tuple(columns.keys())
        self.treeview.column('name', width=220, anchor='w')
        self.treeview.column('pep', width=90, anchor='center')
        self.treeview.column('type', width=100, anchor='center')
        self.treeview.column('msg', width=120, anchor='e')
        self.treeview.column('call', width=140, anchor='e')
        self.treeview.column('photos', width=100, anchor='e')
        self.treeview.column('gifs', width=90, anchor='e')
        self.treeview.column('videos', width=90, anchor='e')
        self.treeview.column('files', width=90, anchor='e')
        for keyword, text in columns.items():
            self.treeview.heading(keyword, text=text, anchor='center')
        self.treeview.bind('<Button-3>', lambda event: self.deselect())
        self.treeview.bind('<Double-1>', lambda event: self.show_statistics())

        # Ordered list of columns (so we can display them in a fixed order)
        self.columns = [
            'name',
            'pep',
            'type',
            'msg',
            'call',
            'photos',
            'gifs',
            'videos',
            'files'
        ]
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

        # Show frame title
        self.title = ttk.Label(
            self.top_bar, text=f'{self.module.TITLE_NUMBER_OF_MSGS} ', style="Custom.TLabel",
        )
        self.title.pack(side='top', pady=10)

        # Show home button
        self.home_button = ttk.Button(
            self.nav, image=self.controller.theme_manager.get_icon("home"), text=self.module.TITLE_HOME, compound='left', style="TButton"
        )
        self.home_button.pack(side='top', pady=10)

        # Show upload button
        self.upload_button = ttk.Button(
            self.nav, image=self.controller.theme_manager.get_icon("upload"), text=self.module.TITLE_UPLOAD_MESSAGES,
            compound='left', style="TButton", command=self.upload_data
        )
        self.upload_button.pack(side='top', pady=10)

        # Show search button
        self.search_entry = ttk.Entry(self.top_bar, width=25)
        self.search_entry.pack(side="right", padx=(5, 0))

        # Optional placeholder
        self.search_entry.insert(0, self.module.TITLE_SEARCH)
        self.search_entry.bind(
            "<FocusIn>",
            lambda e: self.search_entry.delete(0, "end") if self.search_entry.get() ==
            self.module.TITLE_SEARCH else None
        )

        # Search button with icon
        self.search_button = ttk.Button(
            self.top_bar,
            image=self.controller.theme_manager.get_icon("search"),
            command=self.search
        )
        self.search_button.pack(side="right", pady=0)

        # Multi-sort button opens the sort-editor UI
        ttk.Button(
            self.nav, text=self.module.TITLE_MULTI_SORT, style="TButton",
            command = lambda :
            MultiSortPopup(
                self.controller,
                self.columns[:],                   # Pass a copy
                {**self.column_titles},            # Pass a copy
                self.columns_reversed,
                self.sort_columns,
                lambda : self.apply_multi_sort()
            )
        ).pack(side='top', pady=10)

        # Show exit button
        self.exit_button = ttk.Button(
            self.nav, image=self.controller.theme_manager.get_icon("exit"), text=self.module.TITLE_EXIT, compound='left', style="TButton",
            command=self.controller.destroy
        )
        self.exit_button.pack(side='bottom')

        # Show settings button
        self.settings_button = ttk.Button(
            self.nav, image=self.controller.theme_manager.get_icon("settings"), text=self.module.TITLE_SETTINGS, compound='left', style="TButton", command=lambda: self._show_settings_popup()
        )
        self.settings_button.pack(side='bottom', pady=15)

        # Show profile button
        self.profile_button = ttk.Button(
            self.nav, image=self.controller.theme_manager.get_icon("profile"), text=self.module.TITLE_PROFILE, compound='left',
            padding=7, command=lambda: self._show_profile_popup()
        )
        self.profile_button.pack(side='bottom')

        scrollbar.pack(side='right', fill='y')
        self.treeview.pack(side='left', fill='both', expand=1)
        scrollbar.config(command=self.treeview.yview)
        self.nav.pack(side='left', fill='y')
        self.main.pack(side='right', fill='both', expand=True)

    def _show_settings_popup(self):
        """Show the settings popup"""
        from popups.settings_popup import SettingsPopup
        SettingsPopup(self.controller, self)

    def _show_profile_popup(self):
        """Show the profile popup"""
        from popups.profile_popup import ProfilePopup
        ProfilePopup(self.controller)

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
                if str(value).find(query) != -1:
                    # Selection accepted, save it and move on
                    selections.append(child)
                    break
        self.treeview.selection_set(selections)

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

            self.set_treeview_theme()

        except FileNotFoundError:
            print('>MainPage/upload_data THROWS FileNotFoundError, NOTIFY OP IF UNEXPECTED')

    def set_icons(self):
        """
        Setting up the icons of the page based on the theme via theme manager
        """
        manager = self.controller.theme_manager
        self.home_button.configure(image=manager.get_icon("home"))
        self.search_button.configure(image=manager.get_icon("search"))
        self.upload_button.configure(image=manager.get_icon("upload"))
        self.exit_button.configure(image=manager.get_icon("exit"))
        self.settings_button.configure(image=manager.get_icon("settings"))
        self.profile_button.configure(image=manager.get_icon("profile"))

    def set_treeview_theme(self):
        """
        Sets up the background of each item for a specific theme

        NOTE: this happens here because the theme class doesn't know how
        we want to display the children of the treeview
        """
        theme = self.controller.get_theme()
        for i, item in enumerate(self.treeview.get_children()):
            tag = "even" if i % 2 == 0 else "odd"
            self.treeview.item(item, tags=(tag,))
        self.treeview.tag_configure("even", background=theme.TREEVIEW_EVEN_ROW)
        self.treeview.tag_configure("odd", background=theme.TREEVIEW_ODD_ROW)

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

        rows.sort(key = cmp_to_key(compare_wrapper))

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
