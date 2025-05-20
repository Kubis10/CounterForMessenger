"""
Multi-sort popup dialog for CounterForMessenger
"""
import tkinter as tk
from utils import set_icon, set_resolution

class MultiSortPopup(tk.Toplevel):
    """Multi-sort popup window for configuring column sorting order"""

    def __init__(self, controller, columns, column_titles, columns_reversed, sort_columns, apply_callback):
        """
        Initialize multi-sort popup

        Args:
            controller: Controller object for managing application state
            columns: List of available column names
            column_titles: Dictionary mapping column names to display titles
            columns_reversed: Dictionary tracking reversed status for columns
            sort_columns: List of columns in current sort order
            apply_callback: Callback function to apply the sorting
        """
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl

        # This popup is bigger to make room for all the additional buttons
        set_resolution(self, 800, 600)

        self.columns = columns
        self.column_titles = column_titles

        # Bind sort info so we can mutate it later - it's important we don't break these aliases
        self.sort_columns = sort_columns
        self.columns_reversed = columns_reversed

        # We can call this function to apply the sort
        self.apply_callback = apply_callback

        # Temporary ordering - we will keep this in sync with a listbox
        # We initialize the ordering with the ordering from the MainPage, if one exists
        self.temp_ordering = self.sort_columns[:]
        self.temp_reversed = {**self.columns_reversed}

        # Window customization
        self.title(self.module.TITLE_CONFIGURE_MULTI_SORT)
        set_icon(self)
        self.focus_set()
        self.grab_set()

        # Show header
        tk.Label(
            self, text=self.module.TITLE_MULTI_SORT, font=('Ariel', 24)
        ).pack(side='top', pady=20)

        # Create the UI components
        self._create_listbox_frame()
        self._create_action_buttons()

    def _create_listbox_frame(self):
        """Create the frame containing listboxes for available columns and sort order"""
        listbox_frame = tk.Frame(self)
        listbox_frame.pack(fill=tk.X, padx=50)

        # Have columns fill width
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(1, weight=1)

        # Listbox of "available" columns
        tk.Label(
            listbox_frame,
            text=self.module.TITLE_AVAILABLE_COLUMNS
        ).grid(row=0, column=0)
        self.available_listbox = tk.Listbox(listbox_frame)
        self.available_listbox.grid(row=1, column=0, sticky='nesw')

        # Fill the listbox with all the columns
        for column_name in self.columns:
            column_title = self.column_titles[column_name]
            self.available_listbox.insert(tk.END, column_title)

        # Listbox to configure sort_order (empty to begin with)
        tk.Label(
            listbox_frame,
            text=self.module.TITLE_SORT_ORDER
        ).grid(row=0, column=1)
        self.sort_order_listbox = tk.Listbox(listbox_frame)
        self.sort_order_listbox.grid(row=1, column=1, columnspan=1, sticky='nesw')

        # Fill the listbox with restored columns
        for column_name in self.temp_ordering:
            text = self.get_entry_text(column_name)
            self.sort_order_listbox.insert(tk.END, text)

        # "Add" and "Remove" buttons
        tk.Button(
            listbox_frame,
            text=self.module.TITLE_ADD,
            command=lambda: self.add_clicked()
        ).grid(row=2, column=0)

        tk.Button(
            listbox_frame,
            text=self.module.TITLE_REMOVE,
            command=lambda: self.remove_clicked()
        ).grid(row=3, column=0)

        # "Move up" and "Move down" buttons
        tk.Button(
            listbox_frame,
            text=self.module.TITLE_MOVE_UP,
            command=lambda: self.move_up_clicked()
        ).grid(row=2, column=1)

        tk.Button(
            listbox_frame,
            text=self.module.TITLE_MOVE_DOWN,
            command=lambda: self.move_down_clicked()
        ).grid(row=3, column=1)

        # "Reverse" button
        tk.Button(
            listbox_frame,
            text=self.module.TITLE_REVERSE,
            command=lambda: self.reverse_clicked()
        ).grid(row=4, column=0)

        # "Clear" button
        tk.Button(
            listbox_frame,
            text=self.module.TITLE_CLEAR,
            command=lambda: self.clear()
        ).grid(row=4, column=1)

    def _create_action_buttons(self):
        """Create the Apply and Cancel buttons"""
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=50, pady=20)

        # Apply button
        tk.Button(
            button_frame,
            text=self.module.TITLE_APPLY,
            command=lambda: self.apply()
        ).pack(side=tk.RIGHT, padx=10)

        # Cancel button
        tk.Button(
            button_frame,
            text=self.module.TITLE_CANCEL,
            command=lambda: self.destroy()
        ).pack(side=tk.RIGHT, padx=10)

    def get_entry_text(self, column_name):
        """
        Get display text for sort order entry

        Args:
            column_name: Column name to get display text for

        Returns:
            Display text for the column, including sorting direction
        """
        column_title = self.column_titles[column_name]
        direction = "↓" if self.temp_reversed.get(column_name, False) else "↑"
        return f"{column_title} {direction}"

    def get_column_name_from_index(self, index):
        """
        Get column name from index in the columns list

        Args:
            index: Index in the columns list

        Returns:
            Column name at the given index
        """
        return self.columns[index]

    def clear(self):
        """Clear all sort columns"""
        self.temp_ordering.clear()
        self.temp_reversed.clear()
        self.sort_order_listbox.delete(0, tk.END)

    def add_clicked(self):
        """Add selected column from available list to sort order"""
        try:
            # Get the selected index in available columns
            idx = self.available_listbox.curselection()[0]

            # Get the corresponding column name
            column_name = self.get_column_name_from_index(idx)

            # Add to sort order if not already there
            if column_name not in self.temp_ordering:
                self.temp_ordering.append(column_name)
                self.sort_order_listbox.insert(tk.END, self.get_entry_text(column_name))
        except (IndexError, KeyError):
            # No selection or other error
            pass

    def remove_clicked(self):
        """Remove selected column from sort order"""
        try:
            # Get the selected index in sort order
            idx = self.sort_order_listbox.curselection()[0]

            # Remove from temp ordering and UI
            column_name = self.temp_ordering.pop(idx)
            if column_name in self.temp_reversed:
                del self.temp_reversed[column_name]
            self.sort_order_listbox.delete(idx)
        except (IndexError, KeyError):
            # No selection or other error
            pass

    def move_up_clicked(self):
        """Move selected column up in sort order"""
        try:
            # Get the selected index
            idx = self.sort_order_listbox.curselection()[0]

            # Can't move up if at the top
            if idx <= 0:
                return

            # Swap in temp ordering
            self.temp_ordering[idx-1], self.temp_ordering[idx] = self.temp_ordering[idx], self.temp_ordering[idx-1]

            # Update UI
            self._refresh_sort_order_listbox()
            self.sort_order_listbox.select_set(idx-1)
        except (IndexError, KeyError):
            # No selection or other error
            pass

    def move_down_clicked(self):
        """Move selected column down in sort order"""
        try:
            # Get the selected index
            idx = self.sort_order_listbox.curselection()[0]

            # Can't move down if at the bottom
            if idx >= len(self.temp_ordering) - 1:
                return

            # Swap in temp ordering
            self.temp_ordering[idx], self.temp_ordering[idx+1] = self.temp_ordering[idx+1], self.temp_ordering[idx]

            # Update UI
            self._refresh_sort_order_listbox()
            self.sort_order_listbox.select_set(idx+1)
        except (IndexError, KeyError):
            # No selection or other error
            pass

    def reverse_clicked(self):
        """Toggle sort direction for selected column"""
        try:
            # Get the selected index
            idx = self.sort_order_listbox.curselection()[0]
            column_name = self.temp_ordering[idx]

            # Toggle reversed status
            self.temp_reversed[column_name] = not self.temp_reversed.get(column_name, False)

            # Update UI
            self._refresh_sort_order_listbox()
            self.sort_order_listbox.select_set(idx)
        except (IndexError, KeyError):
            # No selection or other error
            pass

    def _refresh_sort_order_listbox(self):
        """Refresh the sort order listbox to reflect current temp ordering"""
        self.sort_order_listbox.delete(0, tk.END)
        for column_name in self.temp_ordering:
            self.sort_order_listbox.insert(tk.END, self.get_entry_text(column_name))

    def apply(self):
        """Apply the configured sort order and close popup"""
        # Transfer temp state to real state (using clear then extend to preserve reference)
        self.sort_columns.clear()
        self.sort_columns.extend(self.temp_ordering)

        # Update reversed status
        self.columns_reversed.clear()
        self.columns_reversed.update(self.temp_reversed)

        # Apply the sort
        self.apply_callback()

        # Close popup
        self.destroy()
