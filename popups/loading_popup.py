"""
Loading popup dialog for CounterForMessenger
"""
import tkinter as tk
from tkinter import ttk
from utils import set_icon, set_resolution, PREFIX, apply_theme

class LoadingPopup(tk.Toplevel):
    """Loading popup window showing progress of loading conversations"""

    def __init__(self, controller, chat_total, treeview):
        """
        Initialize loading popup

        Args:
            controller: Controller object for managing application state
            chat_total: Total number of conversations to load
            treeview: Treeview widget to populate with conversation data
        """
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 300, 100)

        # Loading window customization
        self.title(f'{self.module.TITLE_LOADING}...')
        set_icon(self)
        self.resizable(False, False)
        self.focus_set()
        self.grab_set()

        # Load progress bar
        self.progress_bar = ttk.Progressbar(
            self, orient='horizontal', maximum=chat_total, length=200, mode='determinate'
        )
        self.progress_bar.pack(side='top')

        # Load progress counter label
        self.progress_label = ttk.Label(
            self, text=f'{self.module.TITLE_LOADING_CHAT} 0/{chat_total}'
        )
        self.progress_label.pack(side='top')

        # Apply the active theme's colors to this window's plain tk widgets
        apply_theme(self, self.controller.get_theme())

        # Load all conversations to treeview for display
        self.load_conversations(treeview, chat_total)

    def load_conversations(self, treeview, chat_total):
        """
        Load conversations from the directory into the treeview

        Args:
            treeview: Treeview widget to populate with conversation data
            chat_total: Total number of conversations to load
        """
        self.directory = self.controller.get_directory()
        if (self.directory != '' and not self.directory.isspace() and
                self.directory != self.module.TITLE_NO_SELECTION):

            # Reset message counters
            self.controller.sent_messages = 0
            self.controller.total_messages = 0
            self.controller.total_chars = 0
            self.controller.total_conversations = 0

            # Extract all conversations up front (e2e contacts already merged with
            # their matching regular-folder conversation where applicable), so the
            # progress bar total can reflect the real number of rows to insert
            all_conversations = self.controller.extract_all_conversations()
            chat_total = len(all_conversations)
            self.progress_bar['maximum'] = chat_total
            self.progress_label['text'] = f'{self.module.TITLE_LOADING_CHAT} 0/{chat_total}'

            for row_index, (title, people, room, all_msgs, all_chars, calltime, sent_msgs, _, total_photos, total_gifs, total_videos, total_files, _) in enumerate(all_conversations):
                try:
                    # TREEVIEW AUTOMATED CONVERSION PROBLEM:
                    # The ttk treeview will convert able strings to integers.
                    # E.g. chats named '1337' will be attached to a folder named '1337_17623521673' yet be saved
                    # internally as '133717623521673'. This is not explicitly preventable.
                    # Easiest solution is to force the name to be a string by temporarily adding some garbage to it.
                    treeview.insert(
                        parent='', index='end', values=(
                            title, set(people.keys()), room, all_msgs, calltime, total_photos, total_gifs, total_videos,
                            total_files, all_chars,
                            f'{PREFIX}all#{row_index}'
                        ))

                    # Update global message counters
                    self.controller.sent_messages += sent_msgs
                    self.controller.total_messages += all_msgs
                    self.controller.total_chars += all_chars
                    self.controller.total_conversations += 1

                    # Update progress bar
                    self.progress_bar['value'] += 1
                    self.progress_bar.update()

                    # Update progress label
                    progress_value = self.progress_bar['value']
                    self.progress_label['text'] = f'{self.module.TITLE_LOADING_CHAT} {int(progress_value)}/{chat_total}'
                    self.progress_label.update()

                except Exception as e:
                    print(f"Error loading conversation: {str(e)}")
                    continue

        # Close popup when done
        self.destroy()
