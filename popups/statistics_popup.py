"""
Statistics popup dialog for CounterForMessenger
"""
import tkinter as tk
from tkinter import ttk
from utils import set_icon, set_resolution
from datetime import timedelta, datetime
from time import time

class StatisticsPopup(tk.Toplevel):
    """Statistics popup window showing conversation details"""

    def __init__(self, controller, selection):
        """
        Initialize statistics popup

        Args:
            controller: Controller object for managing application state
            selection: Conversation ID to display statistics for
        """
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 800, 600)

        # Extract data for the selected conversation
        title, people, room, all_msgs, all_chars, calltime, sent_msgs, start_date, total_photos, total_gifs, total_videos, total_files = self.controller.extract_data(
            selection)

        # Resize the window to fit all data if the conversation is a group chat
        if room == self.module.TITLE_GROUP_CHAT:
            set_resolution(self, 800, 650)

        # Statistics window customization
        self.title(self.module.TITLE_STATISTICS)
        set_icon(self)
        self.focus_set()
        self.grab_set()

        # Display popup title
        ttk.Label(self, text=f'{self.module.TITLE_MSG_STATS}:').pack(side='top', pady=16)

        # Show conversation title and type
        ttk.Label(self, text=f'{self.module.TITLE_NAME}: {title}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_CONVERSATION_TYPE}: {room}').pack(side='top', pady=5)

        # Load participants list box
        ttk.Label(
            self, text=f'{self.module.TITLE_PEOPLE}({len(people)}) {self.module.TITLE_AND_MESSAGES}: '
        ).pack(side='top', pady=5)
        if room == self.module.TITLE_GROUP_CHAT:
            # Larger amount of participants, load bigger box and include a scrollbar
            height = 15
            ttk.Scrollbar(self).pack(side='right', fill='both')
        else:
            # Fixed 2 people per private chat, load small box
            height = 2
        listbox = tk.Listbox(self, width=30, height=height)
        listbox.pack(side='top', pady=5)

        # Paste participants inside listbox
        for participant, messages in people.items():
            listbox.insert('end', f'{participant} - {messages}')

        # Show message statistics
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_MSGS}: {all_msgs}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_TOTAL_CHARS}: {all_chars}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_PHOTOS}: {total_photos}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_GIFS}: {total_gifs}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_VIDEOS}: {total_videos}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_FILES}: {total_files}').pack(side='top', pady=5)

        # Show call duration
        ttk.Label(
            self, text=f'{self.module.TITLE_CALL_DURATION}: {timedelta(seconds=calltime)}'
        ).pack(side='top', pady=5)

        # Show first message date
        ttk.Label(
            self, text=f'{self.module.TITLE_START_DATE}: {datetime.fromtimestamp(start_date / 1000)}'
        ).pack(side='top', pady=5)

        # Show average messages per time period
        self._display_message_averages(all_msgs, start_date)

    def _display_message_averages(self, all_msgs, start_date):
        """
        Display average message counts for different time periods

        Args:
            all_msgs: Total number of messages
            start_date: Start timestamp (in milliseconds)
        """
        # Calculate seconds since start
        sec_since_start = int(time() - start_date / 1000)

        ttk.Label(
            self, text=f'{self.module.TITLE_AVERAGE_MESSAGES}: '
        ).pack(side='top', pady=5)

        # Create listbox for averages
        listbox = tk.Listbox(self, width=30, height=4)
        listbox.pack(side='top', pady=5)

        # Calculate and display averages
        day_avg = all_msgs / (sec_since_start / 86400) if sec_since_start > 0 else 0
        week_avg = all_msgs / (sec_since_start / (7 * 86400)) if sec_since_start > 0 else 0
        month_avg = all_msgs / (sec_since_start / (30 * 86400)) if sec_since_start > 0 else 0
        year_avg = all_msgs / (sec_since_start / (365 * 86400)) if sec_since_start > 0 else 0

        listbox.insert('end', f'{self.module.TITLE_PER_DAY} - {day_avg:.2f}')
        listbox.insert('end', f'{self.module.TITLE_PER_WEEK} - {week_avg:.2f}')
        listbox.insert('end', f'{self.module.TITLE_PER_MONTH} - {month_avg:.2f}')
        listbox.insert('end', f'{self.module.TITLE_PER_YEAR} - {year_avg:.2f}')
