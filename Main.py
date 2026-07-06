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
from collections import defaultdict
from PIL import ImageTk

from gui.theme import ThemeManager, DefaultTheme, DarkTheme
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

        # User data
        self.directory = ''
        self.username = ''
        self.language = 'English'
        self.from_date_entry = ''
        self.to_date_entry = ''
        self.theme = ""
        self.lang_mdl = importlib.import_module('langs.English')
        self.sent_messages = 0
        self.total_messages = 0
        self.total_chars = 0
        self.total_conversations = 0

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

        # Initialization of the ThemeManager and registration of Themes
        self.theme_manager = ThemeManager()
        self.theme_manager.register(DefaultTheme())
        self.theme_manager.register(DarkTheme())
        self.change_theme("default")

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

    def update_data(self, username, directory, language, from_date_entry, to_date_entry, theme):
        """
        Updates user data

        Args:
            username: Username
            directory: Path to the data directory
            language: Selected language
            from_date_entry: Start date
            to_date_entry: End date
            theme: App's theme
        """
        temp = self.language
        self.username = username
        self.directory = directory
        self.language = language
        self.from_date_entry = from_date_entry
        self.to_date_entry = to_date_entry
        self.theme = theme
        self.lang_mdl = importlib.import_module(f'langs.{language}')

        # Save user data in config.txt
        with open('config.txt', 'w', encoding='utf-8') as f:
            f.write(f'{username}\n{directory}\n{language}\n{from_date_entry}\n{to_date_entry}\n{theme}')

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
                        self.theme = lines[5] if len(lines) >= 6 else self.theme
                self.lang_mdl = importlib.import_module(f'langs.{self.language}')
            except Exception as e:
                print(f"Error loading configuration: {e}")

    @staticmethod
    def _get_participant_name(participant):
        """
        Extracts a participant's name, supporting both the legacy schema
        (dict with a 'name' key) and the newer schema (plain string)

        Args:
            participant: Participant entry as provided by Facebook's export

        Returns:
            Participant's name as a string
        """
        return participant['name'] if isinstance(participant, dict) else participant

    @staticmethod
    def _get_sender(message):
        """Extracts the sender's name, supporting old (sender_name) and new (senderName) schemas"""
        return message.get('sender_name') or message.get('senderName', '')

    @staticmethod
    def _get_message_text(message):
        """Extracts the message body, supporting old (content) and new (text) schemas"""
        content = message.get('content')
        return content if content is not None else message.get('text', '')

    @staticmethod
    def _get_timestamp(message):
        """Extracts the message timestamp, supporting old (timestamp_ms) and new (timestamp) schemas"""
        timestamp = message.get('timestamp_ms')
        if timestamp is None:
            timestamp = message.get('timestamp', 0)
        return int(timestamp)

    @staticmethod
    def _get_chat_title(data):
        """Extracts the chat title, supporting old (title) and new (threadName) schemas"""
        return data.get('title') or data.get('threadName', '')

    @staticmethod
    def _count_media(message):
        """
        Counts multimedia attachments for a message, supporting both schemas.

        The legacy (pre-2024) schema exposes separate 'photos'/'gifs'/'videos'/'files'
        arrays per message. The newer schema (including E2EE exports) instead exposes
        a single unified 'media' array with no type information (Meta doesn't expose
        the original media type for encrypted/undownloadable attachments), so those
        are counted under 'photos' as a best-effort approximation rather than being
        silently dropped and always showing 0.

        Args:
            message: Message dict to inspect

        Returns:
            Tuple of (photos, gifs, videos, files) counts for this message
        """
        photos = len(message['photos']) if 'photos' in message else 0
        gifs = len(message['gifs']) if 'gifs' in message else 0
        videos = len(message['videos']) if 'videos' in message else 0
        files = len(message['files']) if 'files' in message else 0

        if 'media' in message:
            photos += len(message['media'])

        return photos, gifs, videos, files

    def extract_data(self, conversation):
        """
        Extracts data from JSON files for a given conversation

        Args:
            conversation: Conversation folder to process

        Returns:
            Tuple containing various conversation statistics
        """
        participants = defaultdict(int)
        participant_chars = defaultdict(int)
        chat_title, chat_type = '', self.lang_mdl.TITLE_GROUP_CHAT
        call_duration = total_messages = total_chars = sent_messages = start_date = 0
        total_photos = total_gifs = total_videos = total_files = 0

        # Processing dates
        self._normalize_dates()

        # Optimization: Pre-calculate timestamps for range comparison
        start_ts = datetime.combine(self.from_date_entry, datetime.min.time()).timestamp() * 1000
        # End timestamp: We want to include the entire end date.
        # So we go to the next day at 00:00:00 and use strictly less than.
        end_ts = datetime.combine(self.to_date_entry + timedelta(days=1), datetime.min.time()).timestamp() * 1000

        cached_username = self.get_username()

        # Processing JSON files in the conversation folder
        path_to_browse = f'{self.directory}{conversation}'

        for file in glob.glob(f'{path_to_browse}/*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Collecting chat participants
                    for participant in data.get('participants', []):
                        name = self._get_participant_name(participant)
                        participants[name] = participants.get(name, 0)

                    # Updating counters
                    for message in data.get('messages', []):
                        # Filter messages by timestamp
                        timestamp = self._get_timestamp(message)

                        # Filtering messages within the selected period
                        if start_ts <= timestamp < end_ts:
                            total_messages += 1

                            # Counting characters
                            sender = self._get_sender(message)
                            try:
                                msg_chars = len(self._get_message_text(message))
                                total_chars += msg_chars
                                participant_chars[sender] += msg_chars
                            except (KeyError, TypeError):
                                pass

                            # Counting sender's messages
                            if sender == cached_username:
                                sent_messages += 1

                            # Tracking participant messages
                            participants[sender] += 1

                            # Recording call duration
                            call_duration += message.get('call_duration', 0)

                            # Save conversation creation date
                            current_timestamp = timestamp
                            if start_date == 0 or current_timestamp < start_date:
                                start_date = current_timestamp

                            # Counting multimedia
                            msg_photos, msg_gifs, msg_videos, msg_files = self._count_media(message)
                            total_photos += msg_photos
                            total_gifs += msg_gifs
                            total_videos += msg_videos
                            total_files += msg_files

                    # Get chat name and type
                    chat_title = self._get_chat_title(data)

                    # Check if it's a private chat
                    # Legacy schema exposes 'joinable_mode' only for group chats;
                    # newer schema omits it entirely, so fall back to participant count
                    if 'joinable_mode' in data:
                        chat_type = self.lang_mdl.TITLE_GROUP_CHAT
                    elif len(data.get('participants', [])) <= 2:
                        chat_type = self.lang_mdl.TITLE_PRIVATE_CHAT
                    else:
                        chat_type = self.lang_mdl.TITLE_GROUP_CHAT
            except Exception as e:
                print(f"Error processing file {file}: {e}")

        return (
            chat_title, participants, chat_type, total_messages, total_chars,
            call_duration, sent_messages, start_date, total_photos, total_gifs,
            total_videos, total_files, participant_chars
        )

    def extract_e2e_data(self):
        """
        Extracts data from JSON files in the e2e folder, producing one entry per
        person rather than a single aggregated entry, so each E2EE contact is
        listed the same way as a regular conversation

        Returns:
            List of tuples, each in the same format as extract_data() returns
        """
        # Processing dates
        self._normalize_dates()

        # Optimization: Pre-calculate timestamps for range comparison
        start_ts = datetime.combine(self.from_date_entry, datetime.min.time()).timestamp() * 1000
        end_ts = datetime.combine(self.to_date_entry + timedelta(days=1), datetime.min.time()).timestamp() * 1000

        cached_username = self.get_username()
        path_to_browse = f'{self.directory}e2e'

        # Store conversation data separately for each person/file
        e2e_conversations = {}

        for file in glob.glob(f'{path_to_browse}/*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Get thread name without number
                    thread_name = self._get_chat_title(data)
                    person_name = thread_name.split('_')[0] if '_' in thread_name else thread_name

                    # Initialize conversation data for this person if not exists
                    if person_name not in e2e_conversations:
                        e2e_conversations[person_name] = {
                            'participants': defaultdict(int),
                            'participant_chars': defaultdict(int),
                            'chat_title': person_name,
                            'chat_type': self.lang_mdl.TITLE_PRIVATE_CHAT,
                            'call_duration': 0,
                            'total_messages': 0,
                            'total_chars': 0,
                            'sent_messages': 0,
                            'total_photos': 0,
                            'total_gifs': 0,
                            'total_videos': 0,
                            'total_files': 0,
                            'start_date': 0
                        }

                    conv = e2e_conversations[person_name]

                    # Add participants
                    for participant in data.get('participants', []):
                        name = self._get_participant_name(participant)
                        conv['participants'][name] = conv['participants'].get(name, 0)

                    # Process messages for this person
                    for message in data.get('messages', []):
                        # Filter messages by timestamp
                        timestamp = self._get_timestamp(message)
                        if start_ts <= timestamp < end_ts:
                            conv['total_messages'] += 1

                            sender = self._get_sender(message)
                            try:
                                msg_chars = len(self._get_message_text(message))
                                conv['total_chars'] += msg_chars
                                conv['participant_chars'][sender] += msg_chars
                            except (KeyError, TypeError):
                                pass

                            if sender == cached_username:
                                conv['sent_messages'] += 1

                            # Tracking participant messages
                            conv['participants'][sender] += 1

                            # Counting multimedia
                            msg_photos, msg_gifs, msg_videos, msg_files = self._count_media(message)
                            conv['total_photos'] += msg_photos
                            conv['total_gifs'] += msg_gifs
                            conv['total_videos'] += msg_videos
                            conv['total_files'] += msg_files

                            if conv['start_date'] == 0 or timestamp < conv['start_date']:
                                conv['start_date'] = timestamp
            except Exception as e:
                print(f"Error processing file {file}: {e}")

        return [
            (
                conv['chat_title'], conv['participants'], conv['chat_type'], conv['total_messages'],
                conv['total_chars'], conv['call_duration'], conv['sent_messages'], conv['start_date'],
                conv['total_photos'], conv['total_gifs'], conv['total_videos'], conv['total_files'],
                conv['participant_chars']
            )
            for conv in e2e_conversations.values()
        ]

    def extract_conversation(self, selection):
        """
        Resolves a treeview selection identifier to its conversation statistics.

        Normal conversations are stored as the folder name (e.g. 'johnalice_123').
        E2E contacts are stored as 'e2e#<index>' since the e2e folder is expanded
        into one row per person rather than a single folder-wide row.

        Args:
            selection: Conversation identifier, as stored in the treeview row

        Returns:
            Tuple containing various conversation statistics
        """
        if selection.startswith('e2e#'):
            index = int(selection.split('#', 1)[1])
            return self.extract_e2e_data()[index]
        return self.extract_data(selection)

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

    def change_theme(self, name: str):
        self.theme_manager.apply(name)

    def get_theme_name(self):
        return self.theme_manager.current_theme

    def get_theme(self):
        return self.theme_manager.themes[self.get_theme_name()]


if __name__ == "__main__":
    app = MasterWindow()
    app.mainloop()
