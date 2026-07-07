"""
Statistics popup dialog for CounterForMessenger
"""
import tkinter as tk
from tkinter import ttk
from utils import set_icon, set_resolution, apply_theme
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

        # Cap the window height to what actually fits the screen. Group chats
        # can have many participants, making the content taller than a fixed
        # 800x650 window could show; the content is placed in a scrollable
        # canvas below so anything that doesn't fit is reachable by scrolling
        # instead of being cut off or pushed past the bottom of the screen.
        width = 800
        height = min(650, self.winfo_screenheight() - 100)
        set_resolution(self, width, height)

        # Extract data for the selected conversation
        title, people, room, all_msgs, all_chars, calltime, sent_msgs, start_date, total_photos, total_gifs, total_videos, total_files, participant_chars = self.controller.extract_conversation(
            selection)

        # Statistics window customization
        self.title(self.module.TITLE_STATISTICS)
        set_icon(self)
        self.focus_set()
        self.grab_set()

        # Scrollable container: all content is placed inside `content`, which
        # sits in a canvas that scrolls vertically once content overflows the
        # window, so long group-chat statistics never render off-screen.
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        content = ttk.Frame(canvas)

        content.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas_window = canvas.create_window((0, 0), window=content, anchor='nw')
        canvas.bind('<Configure>', lambda event: canvas.itemconfigure(canvas_window, width=event.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Allow mouse wheel scrolling anywhere over the popup; unbind on close so
        # it doesn't keep intercepting scroll events for other windows afterwards
        canvas.bind_all('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units'))
        self.bind('<Destroy>', lambda event: canvas.unbind_all('<MouseWheel>') if event.widget is self else None)

        self._content = content

        # Display popup title
        ttk.Label(content, text=f'{self.module.TITLE_MSG_STATS}:').pack(side='top', pady=16)

        # Show conversation title and type
        ttk.Label(content, text=f'{self.module.TITLE_NAME}: {title}').pack(side='top', pady=5)
        ttk.Label(content, text=f'{self.module.TITLE_CONVERSATION_TYPE}: {room}').pack(side='top', pady=5)

        # Load participants list box
        ttk.Label(
            content, text=f'{self.module.TITLE_PEOPLE}({len(people)}) {self.module.TITLE_AND_MESSAGES}: '
        ).pack(side='top', pady=5)
        # Cap the listbox height so very large group chats don't force an
        # excessively tall widget; the outer canvas scrollbar handles overflow
        height = min(max(len(people), 2), 10)
        listbox = tk.Listbox(content, width=30, height=height)
        listbox.pack(side='top', pady=5)

        # Paste participants inside listbox
        for participant, messages in people.items():
            listbox.insert('end', f'{participant} - {messages}')

        # Show message statistics
        ttk.Label(content, text=f'{self.module.TITLE_NUMBER_OF_MSGS}: {all_msgs}').pack(side='top', pady=5)
        ttk.Label(content, text=f'{self.module.TITLE_TOTAL_CHARS}: {all_chars}').pack(side='top', pady=5)

        # Show characters per person table
        self._display_chars_per_person(participant_chars)

        ttk.Label(content, text=f'{self.module.TITLE_NUMBER_OF_PHOTOS}: {total_photos}').pack(side='top', pady=5)
        ttk.Label(content, text=f'{self.module.TITLE_NUMBER_OF_GIFS}: {total_gifs}').pack(side='top', pady=5)
        ttk.Label(content, text=f'{self.module.TITLE_NUMBER_OF_VIDEOS}: {total_videos}').pack(side='top', pady=5)
        ttk.Label(content, text=f'{self.module.TITLE_NUMBER_OF_FILES}: {total_files}').pack(side='top', pady=5)

        # Show call duration
        ttk.Label(
            content, text=f'{self.module.TITLE_CALL_DURATION}: {timedelta(seconds=calltime)}'
        ).pack(side='top', pady=5)

        # Show first message date
        ttk.Label(
            content, text=f'{self.module.TITLE_START_DATE}: {datetime.fromtimestamp(start_date / 1000)}'
        ).pack(side='top', pady=5)

        # Show average messages per time period
        self._display_message_averages(all_msgs, start_date)

        # Apply the active theme's colors to this window's plain tk widgets
        apply_theme(self, self.controller.get_theme())

    def _display_chars_per_person(self, participant_chars):
        """
        Display a listbox with the total character count sent by each
        participant, sorted from most to least characters (mirrors the
        style of the participants/messages listbox above).

        Args:
            participant_chars: Mapping of participant name -> character count
        """
        ttk.Label(self._content, text=f'{self.module.TITLE_CHARS_PER_PERSON}: ').pack(side='top', pady=5)

        listbox = tk.Listbox(self._content, width=30, height=min(max(len(participant_chars), 1), 6))
        listbox.pack(side='top', pady=5)

        for participant, chars in sorted(participant_chars.items(), key=lambda item: item[1], reverse=True):
            listbox.insert('end', f'{participant} - {chars}')

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
            self._content, text=f'{self.module.TITLE_AVERAGE_MESSAGES}: '
        ).pack(side='top', pady=5)

        # Create listbox for averages
        listbox = tk.Listbox(self._content, width=30, height=4)
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
