"""
Popup dialogs for the CounterForMessenger application.
"""

import tkinter as tk
from tkinter import ttk
from utils import set_icon, set_resolution

class ProfilePopup(tk.Toplevel):
    """Profile popup window showing user statistics"""

    def __init__(self, controller):
        """
        Initialize profile popup

        Args:
            controller: Controller object for managing application state
        """
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 600, 400)

        # Profile window customization
        self.title(self.module.TITLE_PROFILE)
        set_icon(self)
        self.focus_set()
        self.grab_set()

        # Show 'My data' header
        ttk.Label(
            self, text=f'{self.module.TITLE_MY_DATA}:', font=('Ariel', 24)
        ).pack(side='top', pady=20)

        # Display given username
        ttk.Label(
            self, text=f'{self.module.TITLE_NAME}: {self.controller.get_username()}'
        ).pack(side='top', pady=10)

        # Display total number of conversations
        try:
            from os import listdir
            conversations = len(listdir(self.controller.get_directory()))
        except FileNotFoundError:
            conversations = 0
            print('>ProfilePage/#CONVERSATIONS CALCULATION THROWS FileNotFoundError, NOTIFY OP IF UNEXPECTED')

        ttk.Label(
            self, text=f'{self.module.TITLE_NUMBER_OF_CHATS}: {conversations}'
        ).pack(side='top', pady=10)

        # Display total number of sent messages
        ttk.Label(
            self, text=f'{self.module.TITLE_SENT_MESSAGES}: {self.controller.sent_messages}'
        ).pack(side='top', pady=10)

        # Display complete message total
        ttk.Label(
            self, text=f'{self.module.TITLE_TOTAL_MESSAGES}: {self.controller.total_messages}'
        ).pack(side='top', pady=10)

        # Display total number of characters
        ttk.Label(
            self, text=f'{self.module.TITLE_TOTAL_CHARS}: {self.controller.total_chars}'
        ).pack(side='top', pady=10)

        # Load exit button
        ttk.Button(
            self, text=self.module.TITLE_CLOSE_POPUP, padding=7, command=self.destroy
        ).pack(side='top', pady=40)
