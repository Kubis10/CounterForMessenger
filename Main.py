"""
CounterForMessenger - application for analyzing Messenger messages
"""
import json
import tkinter as tk
import glob
import importlib
from time import time
from datetime import timedelta, datetime, date
from os.path import exists
from os import listdir
from PIL import ImageTk

# Local module imports
from utils import set_icon, set_resolution, existing_languages
from gui.config_page import ConfigurationPage
from gui.main_page import MainPage

class MasterWindow(tk.Tk):
    """Main window of the CounterForMessenger application"""

    def __init__(self, *args, **kwargs):
        """
        Application initialization

        Args:
            *args: Arguments passed to the base class
            **kwargs: Named arguments passed to the base class
        """
        tk.Tk.__init__(self, *args, **kwargs)

        # Loading icons
        self.ICON_HOME = tk.PhotoImage(file='assets/home.png')
        self.ICON_SETTINGS = tk.PhotoImage(file='assets/settings.png')
        self.ICON_EXIT = tk.PhotoImage(file='assets/exit.png')
        self.ICON_STATUS_VISIBLE = tk.PhotoImage(file='assets/visible.png')
        self.ICON_SEARCH = tk.PhotoImage(file='assets/search.png')
        self.ICON_PROFILE = tk.PhotoImage(file='assets/person.png')

        # User data
        self.directory = ''
        self.username = ''
        self.language = 'English'
        self.from_date_entry = ''
        self.to_date_entry = ''
        self.lang_mdl = importlib.import_module('langs.English')
        self.sent_messages = 0
        self.total_messages = 0
        self.total_chars = 0

        # Loading user data
        self.load_data()

        # Window configuration
        self.title('Counter for Messenger')
        set_icon(self)

        # Frame container settings
        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Declaration of available frames and their dimensions
        self.frames = {
            "ConfigurationPage": [800, 600, None],
            "MainPage": [1375, 700, None]
        }

        # Initialization and loading of frames into the container
        self.refresh_frames()

        # Displaying the appropriate start page
        self.show_frame(
            "MainPage" if exists('config.txt') else "ConfigurationPage"
        )

    def show_frame(self, page_name):
        """
        Displays the selected frame

        Args:
            page_name: Name of the page to display
        """
        width, height, frame = self.frames.get(page_name)
        set_resolution(self, width, height)
        # Show the new frame
        frame.tkraise()

    def get_username(self):
        """
        Gets the username

        Returns:
            Username or a message indicating no name
        """
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.username == '' or self.username.isspace() else self.username

    def get_directory(self):
        """
        Gets the path to the data directory

        Returns:
            Path to the directory or a message indicating no selection
        """
        return self.lang_mdl.TITLE_NO_SELECTION if self.directory == '/' or self.directory.isspace() else self.directory

    def get_from_date_entry(self):
        """
        Gets the start date

        Returns:
            Start date or a message indicating no date
        """
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.from_date_entry == '' else self.from_date_entry

    def get_to_date_entry(self):
        """
        Gets the end date

        Returns:
            End date or a message indicating no date
        """
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.to_date_entry == '' else self.to_date_entry

    def get_language(self):
        """
        Gets the current language

        Returns:
            Name of the currently selected language
        """
        # Check if the language variable contains a valid assignment
        if self.language not in existing_languages():
            # Default language is English
            self.language = 'English'
            self.lang_mdl = importlib.import_module('langs.English')
        return self.language

    def refresh_frames(self):
        """Initializes and arranges all application frames"""
        # Initialize and arrange all frames on top of each other
        # Switching between frames will allow navigation in the application
        # without closing it
        for page_class in (ConfigurationPage, MainPage):
            page_name = page_class.__name__
            width, height, old_frame = self.frames[page_name]
            new_frame = page_class(parent=self.container, controller=self)
            self.frames[page_name] = [width, height, new_frame]
            new_frame.grid(row=0, column=0, sticky='nsew')

    def update_data(self, username, directory, language, from_date_entry, to_date_entry):
        """
        Updates user data

        Args:
            username: Username
            directory: Path to the data directory
            language: Selected language
            from_date_entry: Start date
            to_date_entry: End date
        """
        temp = self.language
        self.username = username
        self.directory = directory
        self.language = language
        self.from_date_entry = from_date_entry
        self.to_date_entry = to_date_entry
        self.lang_mdl = importlib.import_module(f'langs.{language}')

        # Save user data in config.txt
        with open('config.txt', 'w', encoding='utf-8') as f:
            f.write(f'{username}\n{directory}\n{language}\n{from_date_entry}\n{to_date_entry}')

        # Refresh the interface only if the language has changed
        if temp != language:
            self.refresh_frames()

    def load_data(self):
        """Loads user data from config.txt"""
        if exists('config.txt'):
            try:
                with open('config.txt', 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                    if len(lines) >= 5:
                        self.username = lines[0]
                        self.directory = lines[1]
                        self.language = lines[2]
                        self.from_date_entry = lines[3]
                        self.to_date_entry = lines[4]
                self.lang_mdl = importlib.import_module(f'langs.{self.language}')
            except Exception as e:
                print(f"Error loading configuration: {e}")

    def extract_data(self, conversation):
        """
        Extracts data from JSON files for a given conversation

        Args:
            conversation: Conversation folder to process

        Returns:
            Tuple containing various conversation statistics
        """
        participants = {}
        chat_title, chat_type = '', self.lang_mdl.TITLE_GROUP_CHAT
        call_duration = total_messages = total_chars = sent_messages = start_date = 0
        total_photos = total_gifs = total_videos = total_files = 0

        # Processing dates
        self._normalize_dates()

        # Processing JSON files in the conversation folder
        for file in glob.glob(f'{self.directory}{conversation}/*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Collecting chat participants
                    for participant in data.get('participants', []):
                        name = participant['name']
                        participants[name] = participants.get(name, 0)

                    # Updating counters
                    for message in data.get('messages', []):
                        message_date = datetime.fromtimestamp(int(message["timestamp_ms"]) / 1000).date()

                        # Filtering messages within the selected period
                        if self.from_date_entry <= message_date <= self.to_date_entry:
                            total_messages += 1

                            # Counting characters
                            try:
                                total_chars += len(message.get('content', ''))
                            except (KeyError, TypeError):
                                pass

                            # Counting sender's messages
                            sender = message['sender_name']
                            if sender == self.get_username():
                                sent_messages += 1

                            # Tracking participant messages
                            participants[sender] = participants.get(sender, 0) + 1

                            # Recording call duration
                            call_duration += message.get('call_duration', 0)

                            # Save conversation creation date
                            current_timestamp = message['timestamp_ms']
                            if start_date == 0 or current_timestamp < start_date:
                                start_date = current_timestamp

                            # Counting multimedia
                            if 'photos' in message:
                                total_photos += len(message['photos'])
                            if 'gifs' in message:
                                total_gifs += len(message['gifs'])
                            if 'videos' in message:
                                total_videos += len(message['videos'])
                            if 'files' in message:
                                total_files += len(message['files'])

                    # Get chat name and type
                    chat_title = data.get('title', '')

                    # Check if it's a private chat
                    try:
                        # If there is no 'joinable_mode' element, the chat is private
                        _ = data['joinable_mode']
                    except KeyError:
                        chat_type = self.lang_mdl.TITLE_PRIVATE_CHAT
            except Exception as e:
                print(f"Error processing file {file}: {e}")

        return (
            chat_title, participants, chat_type, total_messages, total_chars,
            call_duration, sent_messages, start_date, total_photos, total_gifs,
            total_videos, total_files
        )

    def _normalize_dates(self):
        """Normalizes the format of input and output dates"""
        # Convert tuples to a single value
        if isinstance(self.from_date_entry, tuple) and len(self.from_date_entry) == 1:
            self.from_date_entry = self.from_date_entry[0]
        if isinstance(self.to_date_entry, tuple) and len(self.to_date_entry) == 1:
            self.to_date_entry = self.to_date_entry[0]

        # Convert strings to date objects
        if not isinstance(self.from_date_entry, date):
            try:
                self.from_date_entry = datetime.strptime(str(self.from_date_entry), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                self.from_date_entry = datetime(2000, 1, 1).date()

        if not isinstance(self.to_date_entry, date):
            try:
                self.to_date_entry = datetime.strptime(str(self.to_date_entry), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                self.to_date_entry = datetime.now().date()


if __name__ == "__main__":
    app = MasterWindow()
    app.mainloop()

