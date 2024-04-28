import json
import tkinter as tk
import glob
import importlib
from time import time
from datetime import timedelta, datetime, date
from tkinter import ttk, filedialog
from os.path import exists
from os import listdir
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import platform
import ast 

# safeguard for the treeview automated string conversion problem
PREFIX = '<@!PREFIX>'

def setIcon(object):
    """
    This function sets the icon of a tkinter window (passed in as `object`) to 
    the CFM icon.
    """
    im = Image.open('assets/CFM.ico')
    photo = ImageTk.PhotoImage(im)
    object.wm_iconphoto(True, photo)


# change to desired resolution
def set_resolution(window, width, height):
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')


def existing_languages():
    # expected output  of lang.title() ---> '<Name>.py'
    # keep only the '<Name>'
    return [lang.title().split('.')[0] for lang in listdir('langs') if lang != '__pycache__']


class ConfigurationPage(tk.Frame):
    # build configuration panel
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.module = self.controller.lang_mdl

        # set up frame title
        tk.Label(
            self, text=self.module.TITLE_INITIAL_CONFIG, font=('Ariel', 24)
        ).pack(side='top', pady=10)

        # ask for directory and show selected path
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_INBOX}:'
        ).pack(side='top', pady=5)
        self.directory_label = tk.Label(self, text=self.module.TITLE_NO_SELECTION)
        self.directory_label.pack(side='top', pady=5)

        # show 'Open File Explorer' button
        ttk.Button(
            self, text=f'{self.module.TITLE_OPEN_FE}...', padding=5, command=self.open_file_explorer
        ).pack(side='top', pady=5)

        # Create 'from' date entry using tkcalendar in settings popup
        tk.Label(self, text=f'{self.module.TITLE_FROM}:').pack(side='top', pady=5)
        self.from_date_entry = DateEntry(self, date_pattern='yyyy-mm-dd', width=12, allow_none=True, year=2000, month=1,
                                         day=1)
        self.from_date_entry.pack(side='top', pady=10)

        # Create 'to' date entry using tkcalendar in settings popup
        tk.Label(self, text=f'{self.module.TITLE_TO}:').pack(side='top', pady=5)
        self.to_date_entry = DateEntry(self, date_pattern='yyyy-mm-dd', width=12, allow_none=True)
        self.to_date_entry.pack(side='top', pady=10)

        # ask for Facebook name
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_USERNAME}:',
        ).pack(side='top', pady=15)
        self.username_label = ttk.Entry(self, width=25)
        self.username_label.pack(side='top', pady=5)

        # set up language listbox
        self.language_label = tk.StringVar(self, value='English')
        ttk.OptionMenu(
            self, self.language_label, 'English', *existing_languages()
        ).pack(side='top', pady=10)

        # load save button
        ttk.Button(
            self, text=self.module.TITLE_SAVE, padding=7, command=self.setup
        ).pack(side='top', pady=40)

    # invoked by pressing the save button
    def setup(self):
        # communicate provided data with the master window
        self.controller.update_data(
            self.username_label.get(),
            self.directory_label.cget('text'),
            self.language_label.get(),
            self.from_date_entry.get_date(),
            self.to_date_entry.get_date()
        )
        # go to main page
        self.controller.show_frame(MainPage.__name__)

    # invoked by pressing the 'Open file explorer...' button
    def open_file_explorer(self):
        # open FE, extract given path and update label text message
        path = f'{tk.filedialog.askdirectory()}/'
        self.directory_label.config(
            text=(self.module.TITLE_NO_SELECTION if path == '' or path.isspace() or path == '/' else path)
        )


class MainPage(tk.Frame):
    # build main panel
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.configure(background='#232323')
        self.module = self.controller.lang_mdl

        # frame style setup
        self.style = ttk.Style()
        self.style.configure('Nav.TFrame', background='#131313')
        self.style.configure('Main.TFrame', background='#232323')
        self.style.configure('Custom.Treeview', background='#232323', foreground='#ffffff')
        self.nav = ttk.Frame(self, padding=20, style='Nav.TFrame')
        self.main = ttk.Frame(self, style='Main.TFrame')

        # build treeview for message data projection
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
        for keyword, text in columns.items():
            self.treeview.heading(keyword, text=text, anchor='center')
        self.treeview.bind('<Button-3>', lambda event: self.deselect())
        self.treeview.bind('<Double-1>', lambda event: self.show_statistics())

        # *Ordered* list of columns (so we can display them in a fixed order)
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

        # filter columns
        self.filter_columns = {
            'name': '',
            'pep': set(),
            'msg': -1,
            'call': -1,
            'photos': -1,
            'gifs': -1,
            'videos': -1,
            'files': -1
        }
        
        # show frame title
        ttk.Label(
            self.main, text=f'{self.module.TITLE_NUMBER_OF_MSGS}: ', foreground='#ffffff', background='#232323',
            font=('Arial', 15)
        ).pack(side='top', pady=10)

        # show home button
        ttk.Button(
            self.nav, image=self.controller.ICON_HOME, text=self.module.TITLE_HOME, compound='left', padding=5
        ).pack(side='top', pady=10)

        # show upload button
        ttk.Button(
            self.nav, image=self.controller.ICON_STATUS_VISIBLE, text=self.module.TITLE_UPLOAD_MESSAGES,
            compound='left', padding=5, command=self.upload_data
        ).pack(side='top', pady=10)

        # show search button
        self.search_entry = ttk.Entry(self.nav, width=15)
        self.search_entry.pack(side='top', pady=10)
        ttk.Button(
            self.nav, image=self.controller.ICON_SEARCH, text=self.module.TITLE_SEARCH, compound='left',
            command=self.search
        ).pack(side='top', pady=10)

        # show filter button
        ttk.Button(
            self.nav, text=self.module.TITLE_FILTER, padding=5, command=lambda: FilterPopup(self.controller, self.columns, self.column_titles, self.filter_columns, lambda : self.filter_treeview())
        ).pack(side='top', pady=10)

        # clear selection button 
        ttk.Button(
            self.nav,
            text="Clear Filters",
            padding=5,
            command=self.deselect
        ).pack(side='top', pady=10)

        # show exit button
        ttk.Button(
            self.nav, image=self.controller.ICON_EXIT, text=self.module.TITLE_EXIT, compound='left', padding=5,
            command=self.controller.destroy
        ).pack(side='bottom')

        # show settings button
        ttk.Button(
            self.nav, image=self.controller.ICON_SETTINGS, text=self.module.TITLE_SETTINGS, compound='left',
            padding=5, command=lambda: SettingsPopup(self.controller)
        ).pack(side='bottom', pady=15)

        # show profile button
        ttk.Button(
            self.nav, image=self.controller.ICON_PROFILE, text=self.module.TITLE_PROFILE, compound='left',
            padding=5, command=lambda: ProfilePopup(self.controller)
        ).pack(side='bottom')

        scrollbar.pack(side='right', fill='y')
        self.treeview.pack(side='left', fill='both', expand=1)
        scrollbar.config(command=self.treeview.yview)
        self.nav.pack(side='left', fill='y')
        self.main.pack(side='right', fill='both', expand=True)

    # invoked on <button 3>
    def deselect(self):
        # remove current treeview selection
        self.treeview.selection_remove(self.treeview.selection())

    def search(self):
        # highlight all messages whose values contain the query at least once
        query = self.search_entry.get()
        selections = []
        for child in self.treeview.get_children():
            for value in self.treeview.item(child)['values']:
                if str(value).find(query) != -1:
                    # selection accepted, save it and move on
                    selections.append(child)
                    break
        self.treeview.selection_set(selections)

    # invoked by pressing the upload button
    def upload_data(self):
        # wipe all previous data in treeview
        self.treeview.delete(*self.treeview.get_children())
        try:
            conversations = len(listdir(self.controller.get_directory()))
            LoadingPopup(self.controller, conversations, self.treeview)

            # enable column sorting on treeview
            self.treeview.heading('msg', command=lambda col='msg': self.sort_treeview(col, False, 'numberwise'))
            self.treeview.heading('name', command=lambda col='name': self.sort_treeview(col, False, 'stringwise'))
            self.treeview.heading('type', command=lambda col='type': self.sort_treeview(col, False, 'stringwise'))
            self.treeview.heading('call', command=lambda col='call': self.sort_treeview(col, False, 'numberwise'))
            self.treeview.heading('photos', command=lambda col='photos': self.sort_treeview(col, False, 'numberwise'))
        except FileNotFoundError:
            print('>MainPage/upload_data THROWS FileNotFoundError, NOTIFY OP IF UNEXPECTED')

    # invoked by pressing the column headers
    def sort_treeview(self, column, order, bias):
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

    def filter_treeview(self):
        """
        This function filters out rows based on criterias selected by the user.
        Example: Show messages with more than 10 photos, but less than 50.
        """
        # Retrieve all the rows in the treeview
        children = self.treeview.get_children('')

        column_headers = self.treeview['columns']

        filtered = []

        for child in children:
            row_content = self.treeview.item(child)['values']
            row_dict = {column_header: value for column_header, value in zip(column_headers, row_content)}

            keepRow = True
            # Check if user wants to filter by name
            if self.filter_columns['name'] != '' and row_dict['name'] != self.filter_columns['name']:
                keepRow = False

            # Check if user wants to filter by participants
            if self.filter_columns['pep'] != {''} and not self.filter_columns['pep'].issubset(ast.literal_eval(row_dict['pep'])):
                keepRow = False

            for column_name in ['msg', 'call', 'photos', 'gifs', 'videos', 'files']:
                # Check if user wants to filter by messages
                if self.filter_columns[column_name] != (-1, -1):
                    min, max = self.filter_columns[column_name]
                    if (min != -1 and row_dict[column_name] < min) or (max != -1 and row_dict[column_name] > max):
                        keepRow = False
            if (keepRow): 
                filtered.append(child)
        # 
        # Set the selection to the filtered list
        self.treeview.selection_set(filtered)

    # invoked on double left click on any treeview listing
    def show_statistics(self):
        try:
            selection = self.treeview.item(self.treeview.selection()[0]).get('values', [])
            if len(selection) == 0:
                return
            # treeview automated conversion problem, read StatisticsPopup comments
            # removing prefix safeguard
            StatisticsPopup(self.controller, selection[10].replace(PREFIX, ''))
        except IndexError:
            # miss-click / empty selection, nothing to show here
            return


class MasterWindow(tk.Tk):
    # NOTE: lang_mdl throws unresolved reference warnings here because its master
    # class doesn't recognise the TITLE_ constants.
    # it works perfectly well, thus the 'noinspection' suppression tags
    # if a better way to handle these warnings is found, remove them
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # load icons
        self.ICON_HOME = tk.PhotoImage(file='assets/home.png')
        self.ICON_SETTINGS = tk.PhotoImage(file='assets/settings.png')
        self.ICON_EXIT = tk.PhotoImage(file='assets/exit.png')
        self.ICON_STATUS_VISIBLE = tk.PhotoImage(file='assets/visible.png')
        self.ICON_SEARCH = tk.PhotoImage(file='assets/search.png')
        self.ICON_PROFILE = tk.PhotoImage(file='assets/person.png')

        # global user data
        self.directory = ''
        self.username = ''
        self.language = 'English'
        self.from_date_entry = ''
        self.to_date_entry = ''
        self.lang_mdl = importlib.import_module('langs.English')
        self.sent_messages = 0
        self.total_messages = 0
        self.total_chars = 0

        # load user
        self.load_data()

        # global window customization
        self.title('Counter for Messenger')
        self.iconbitmap('assets/CFM.ico')

        # frame container setup
        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # declare all possible app frames along with their desired dimensions (width, height)
        self.frames = {
            ConfigurationPage.__name__: [800, 600, None],
            MainPage.__name__: [1375, 700, None]
        }
        # initialize and load frames to container
        self.refresh_frames()

        # remember user that already went through configuration
        self.show_frame(
            MainPage.__name__ if exists('config.txt') else
            ConfigurationPage.__name__
        )

    # raise the next frame to-be-shown
    def show_frame(self, page_name):
        width, height, frame = self.frames.get(page_name)
        set_resolution(self, width, height)
        # invoke the new frame
        frame.tkraise()

    def get_username(self):
        # noinspection PyUnresolvedReferences
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.username == '' or self.username.isspace() else self.username

    def get_directory(self):
        # noinspection PyUnresolvedReferences
        return self.lang_mdl.TITLE_NO_SELECTION if self.directory == '/' or self.directory.isspace() else self.directory

    def get_from_date_entry(self):
        # noinspection PyUnresolvedReferences
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.from_date_entry == '' else self.from_date_entry

    def get_to_date_entry(self):
        # noinspection PyUnresolvedReferences
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.to_date_entry == '' else self.to_date_entry

    def get_language(self):
        # check if current language variable holds valid assignment
        if self.language not in existing_languages():
            # default to english if something went wrong
            self.language = 'English'
            self.lang_mdl = importlib.import_module('langs.English')
        return self.language

    def refresh_frames(self):
        # initialize and stack all the frames on top of each other
        # shuffling between them will allow traversal through the app
        # without it "committing suicide" each time
        for page in (ConfigurationPage, MainPage):
            page_name = page.__name__
            width, height, old_frame = self.frames[page_name]
            new_frame = page(parent=self.container, controller=self)
            self.frames[page_name] = [width, height, new_frame]
            new_frame.grid(row=0, column=0, sticky='nsew')

    # update internal trackers to user made changes
    def update_data(self, username, directory, language, from_date_entry, to_date_entry):
        temp = self.language
        self.username = username
        self.directory = directory
        self.language = language
        self.from_date_entry = from_date_entry,
        self.to_date_entry = to_date_entry,
        self.lang_mdl = importlib.import_module(f'langs.{language}')
        # also save user provided data to 'config.txt'
        with open('config.txt', 'w', encoding='utf-8') as f:
            f.write(f'{username}\n{directory}\n{language}\n{from_date_entry}\n{to_date_entry}')
        # refresh only to apply a new language
        if temp != language:
            self.refresh_frames()

    def load_data(self):
        if exists('config.txt'):
            with open('config.txt', 'r', encoding='utf-8') as f:
                self.username, self.directory, self.language, self.from_date_entry, self.to_date_entry = f.read().splitlines()
            self.lang_mdl = importlib.import_module(f'langs.{self.language}')

    # extract relevant data from given .json files
    def extract_data(self, conversation):
        participants = {}
        # noinspection PyUnresolvedReferences
        chat_title, chat_type = '', self.lang_mdl.TITLE_GROUP_CHAT
        call_duration, total_messages, total_chars, sent_messages, start_date, total_photos, total_gifs, total_videos, total_files = 0, 0, 0, 0, 0, 0, 0, 0, 0

        if isinstance(self.from_date_entry, tuple):
            self.from_date_entry = self.from_date_entry[0]
        if isinstance(self.to_date_entry, tuple):
            self.to_date_entry = self.to_date_entry[0]
        if not isinstance(self.from_date_entry, date) and not isinstance(self.to_date_entry, date):
            self.from_date_entry = datetime.strptime(self.from_date_entry, "%Y-%m-%d").date() if not isinstance(
                self.from_date_entry, date) else self.from_date_entry
            self.to_date_entry = datetime.strptime(self.to_date_entry, "%Y-%m-%d").date() if not isinstance(
                self.to_date_entry, date) else self.to_date_entry

        for file in glob.glob(f'{self.directory}{conversation}/*.json'):
            with open(file, 'r') as f:
                data = json.load(f)
                # collect all chat participants
                for participant in data.get('participants', []):
                    name = participant['name'].encode('iso-8859-1').decode('utf-8')
                    participants[name] = participants.get(name, 0)
                # update all relevant counters
                # filter messages that are in the chosen time window
                for message in data.get('messages', []):
                    if self.from_date_entry <= datetime.fromtimestamp(
                            int(message["timestamp_ms"]) / 1000).date() <= self.to_date_entry:
                        total_messages += 1
                        try:
                            total_chars += len(message['content'])
                        except KeyError:
                            pass
                        sender = message['sender_name'].encode('iso-8859-1').decode('utf-8')
                        if sender == self.get_username():
                            sent_messages += 1
                        # keep track of each participant's message total
                        participants[sender] = participants.get(sender, 0) + 1
                        # save call durations, if any
                        call_duration += message.get('call_duration', 0)
                        # fetch conversation creation date
                        start_date = message['timestamp_ms']  # BUG: doesn't work properly if there are 10 or more JSONs
                        if 'photos' in message:
                            total_photos += len(message['photos'])
                        if 'gifs' in message:
                            total_gifs += len(message['gifs'])
                        if 'videos' in message:
                            total_videos += len(message['videos'])
                        if 'files' in message:
                            total_files += len(message['files'])

                # fetch chat name and type
                chat_title = data.get('title', '').encode('iso-8859-1').decode('utf-8')
                try:
                    # trick: attempt to read 'joinable mode' element
                    # if non-existent, it means that the chat is a private one
                    _ = data['joinable_mode']
                except KeyError:
                    # noinspection PyUnresolvedReferences
                    chat_type = self.lang_mdl.TITLE_PRIVATE_CHAT

        return chat_title, participants, chat_type, total_messages, total_chars, call_duration, sent_messages, start_date, total_photos, total_gifs, total_videos, total_files


class ProfilePopup(tk.Toplevel):
    def __init__(self, controller):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 600, 400)

        # profile window customization
        self.title(self.module.TITLE_PROFILE)
        self.iconbitmap('assets/CFM.ico')
        self.focus_set()
        self.grab_set()

        # show 'My data' header
        ttk.Label(
            self, text=f'{self.module.TITLE_MY_DATA}:', font=('Ariel', 24)
        ).pack(side='top', pady=20)

        # display given username
        ttk.Label(
            self, text=f'{self.module.TITLE_NAME}: {self.controller.get_username()}'
        ).pack(side='top', pady=10)

        # display total number of conversations
        try:
            conversations = len(listdir(self.controller.get_directory()))
        except FileNotFoundError:
            conversations = 0
            print('>ProfilePage/#CONVERSATIONS CALCULATION THROWS FileNotFoundError, NOTIFY OP IF UNEXPECTED')
        ttk.Label(
            self, text=f'{self.module.TITLE_NUMBER_OF_CHATS}: {conversations}'
        ).pack(side='top', pady=10)

        # display total number of sent messages
        ttk.Label(
            self, text=f'{self.module.TITLE_SENT_MESSAGES}: {self.controller.sent_messages}'
        ).pack(side='top', pady=10)

        # display complete message total
        ttk.Label(
            self, text=f'{self.module.TITLE_TOTAL_MESSAGES}: {self.controller.total_messages}'
        ).pack(side='top', pady=10)

        # display total number of characters
        ttk.Label(
            self, text=f'{self.module.TITLE_TOTAL_CHARS}: {self.controller.total_chars}'
        ).pack(side='top', pady=10)

        # load exit button
        ttk.Button(
            self, text=self.module.TITLE_CLOSE_POPUP, padding=7, command=self.destroy
        ).pack(side='top', pady=40)


class SettingsPopup(tk.Toplevel):
    def __init__(self, controller):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 800, 600)

        # settings window customization
        self.title(self.module.TITLE_SETTINGS)
        self.iconbitmap('assets/CFM.ico')
        self.focus_set()
        self.grab_set()

        # ask for directory and show selected path
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_INBOX}:'
        ).pack(side='top', pady=16)
        self.directory_label = tk.Label(self, text=self.controller.get_directory())
        self.directory_label.pack(side='top', pady=15)

        # show 'Open File Explorer' button
        ttk.Button(
            self, text=f'{self.module.TITLE_OPEN_FE}...', padding=5, command=self.open_file_explorer
        ).pack(side='top', pady=5)

        # ask for Facebook name
        tk.Label(
            self, text=f'{self.module.TITLE_GIVE_USERNAME}:'
        ).pack(side='top', pady=15)
        self.username_label = ttk.Entry(self, width=25)
        self.username_label.insert(0, self.controller.get_username())
        self.username_label.pack(side='top', pady=5)

        # Create 'from' date entry using tkcalendar in settings popup
        date_entry = self.controller.get_from_date_entry()
        if not date_entry:
            # Handle the case where the entry is empty
            load_from_date = None
        elif isinstance(date_entry, tuple) and len(date_entry) == 1 and isinstance(date_entry[0], date):
            # If it's a tuple containing a datetime.date object, use it directly
            load_from_date = date_entry[0]
        elif isinstance(date_entry, date):
            # If it's a datetime.date object, use it directly
            load_from_date = date_entry
        else:
            # If it's already a string, parse it as a datetime object
            load_from_date = datetime.strptime(str(date_entry), "%Y-%m-%d").date()

        tk.Label(self, text=f'{self.module.TITLE_FROM}:').pack(side='top', pady=10)
        self.from_date_entry = DateEntry(self, date_pattern='yyyy-mm-dd', width=12, allow_none=True,
                                         year=load_from_date.year, month=load_from_date.month, day=load_from_date.day)
        self.from_date_entry.pack(side='top', pady=5)

        # Create 'to' date entry using tkcalendar in settings popup
        date_entry = self.controller.get_to_date_entry()
        if not date_entry:
            # Handle the case where the entry is empty
            load_to_date = None
        elif isinstance(date_entry, tuple) and len(date_entry) == 1 and isinstance(date_entry[0], date):
            # If it's a tuple containing a datetime.date object, use it directly
            load_to_date = date_entry[0]
        elif isinstance(date_entry, date):
            # If it's a datetime.date object, use it directly
            load_to_date = date_entry
        else:
            # If it's already a string, parse it as a datetime object
            load_to_date = datetime.strptime(str(date_entry), "%Y-%m-%d").date()

        tk.Label(self, text=f'{self.module.TITLE_TO}:').pack(side='top', pady=10)
        self.to_date_entry = DateEntry(self, date_pattern='yyyy-mm-dd', width=12, allow_none=True,
                                       year=load_to_date.year, month=load_to_date.month, day=load_to_date.day)
        self.to_date_entry.pack(side='top', pady=5)

        # set up language listbox
        self.language_label = tk.StringVar(self, value=self.controller.get_language())
        ttk.OptionMenu(
            self, self.language_label, self.controller.get_language(), *existing_languages()
        ).pack(side='top', pady=10)

        # load save button
        ttk.Button(
            self, text=self.module.TITLE_SAVE, padding=7, command=self.setup
        ).pack(side='top', pady=40)

    # invoked by pressing the save button
    def setup(self):
        # communicate provided data with the master window
        self.controller.update_data(
            self.username_label.get(),
            self.directory_label.cget('text'),
            self.language_label.get(),
            self.from_date_entry.get_date(),
            self.to_date_entry.get_date()
        )
        # exit popup
        self.destroy()

    # invoked by pressing the 'Open file explorer...' button
    def open_file_explorer(self):
        # open FE, extract given path and update label text message
        path = f'{tk.filedialog.askdirectory()}/'
        self.directory_label.config(
            text=(self.module.TITLE_NO_SELECTION if path == '' or path.isspace() or path == '/' else path)
        )


class LoadingPopup(tk.Toplevel):
    def __init__(self, controller, chat_total, treeview):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 300, 100)

        # loading window customization
        self.title(f'{self.module.TITLE_LOADING}...')
        self.iconbitmap('assets/CFM.ico')
        self.resizable(False, False)
        self.focus_set()
        self.grab_set()

        # load progress bar
        self.progress_bar = ttk.Progressbar(
            self, orient='horizontal', maximum=chat_total, length=200, mode='determinate'
        )
        self.progress_bar.pack(side='top')

        # load progress counter label
        self.progress_label = ttk.Label(
            self, text=f'{self.module.TITLE_LOADING_CHAT} 0/{chat_total}'
        )
        self.progress_label.pack(side='top')
        # load all conversations to treeview for display
        self.directory = self.controller.get_directory()
        if self.directory != '' and not self.directory.isspace() and self.directory != self.module.TITLE_NO_SELECTION:
            self.controller.sent_messages = 0
            self.controller.total_messages = 0
            self.controller.total_chars = 0
            for conversation in listdir(self.directory):
                try:
                    title, people, room, all_msgs, all_chars, calltime, sent_msgs, _, total_photos, total_gifs, total_videos, total_files = self.controller.extract_data(
                        conversation)
                    if len(people) == 0:
                        # if this occurs, the given path is of correct directory format but contains no useful info
                        # (meaning it's not the expected inbox folder)
                        # skip the entire process, nothing to show
                        break
                    # TREEVIEW AUTOMATED CONVERSION PROBLEM:
                    # the ttk treeview will convert able strings to integers.
                    # e.g. chats named '1337' will be attached to a folder named '1337_17623521673' yet be saved
                    # internally as '133717623521673'. This is not explicitly preventable.
                    # easiest solution is to force the name to be a string by temporarily adding some garbage to it.
                    treeview.insert(
                        parent='', index='end', values=(
                            title, set(people.keys()), room, all_msgs, calltime, total_photos, total_gifs, total_videos,
                            total_files, all_chars,
                            f'{PREFIX}{conversation}'
                        ))
                    # update global message counters
                    self.controller.sent_messages += sent_msgs
                    self.controller.total_messages += all_msgs
                    self.controller.total_chars += all_chars
                    # update progress bar
                    self.progress_bar['value'] += 1
                    self.progress_bar.update()

                    # update progress label
                    progress_value = self.progress_bar['value']
                    self.progress_label['text'] = f'{self.module.TITLE_LOADING_CHAT} {int(progress_value)}/{chat_total}'
                    self.progress_label.update()
                except Exception as e:
                    print("Error in loading: " + str(e))
                    continue

        # return to app
        self.destroy()


class StatisticsPopup(tk.Toplevel):
    def __init__(self, controller, selection):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 800, 1000) # enlarge to contain first five messages

        # statistics window customization
        self.title(self.module.TITLE_STATISTICS)
        self.iconbitmap('assets/CFM.ico')
        self.focus_set()
        self.grab_set()

        title, people, room, all_msgs, all_chars, calltime, sent_msgs, start_date, total_photos, total_gifs, total_videos, total_files, first_five_messages = self.controller.extract_data(
            selection)
        # resize the window to fit all data if the conversation is a group chat
        if room == self.module.TITLE_GROUP_CHAT:
            set_resolution(self, 800, 1200) # enlarge to contain first five messages
        # display popup title
        ttk.Label(self, text=f'{self.module.TITLE_MSG_STATS}:').pack(side='top', pady=16)
        # show conversation title and type
        ttk.Label(self, text=f'{self.module.TITLE_NAME}: {title}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_CONVERSATION_TYPE}: {room}').pack(side='top', pady=5)

        # load participants list box
        ttk.Label(
            self, text=f'{self.module.TITLE_PEOPLE}({len(people)}) {self.module.TITLE_AND_MESSAGES}: '
        ).pack(side='top', pady=5)
        if room == self.module.TITLE_GROUP_CHAT:
            # larger amount of participants, load bigger box and include a scrollbar
            height = 15
            ttk.Scrollbar(self).pack(side='right', fill='both')
        else:
            # fixed 2 people per private chat, load small box
            height = 2
        listbox = tk.Listbox(self, width=30, height=height)
        listbox.pack(side='top', pady=5)
        # paste participants inside listbox
        for participant, messages in people.items():
            listbox.insert('end', f'{participant} - {messages}')

        # show total number of messages and total calltime in conversation
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_MSGS}: {all_msgs}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_TOTAL_CHARS}: {all_chars}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_PHOTOS}: {total_photos}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_GIFS}: {total_gifs}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_VIDEOS}: {total_videos}').pack(side='top', pady=5)
        ttk.Label(self, text=f'{self.module.TITLE_NUMBER_OF_FILES}: {total_files}').pack(side='top', pady=5)
        ttk.Label(
            self, text=f'{self.module.TITLE_CALL_DURATION}: {timedelta(seconds=calltime)}'
        ).pack(side='top', pady=5)
        # show first message date
        ttk.Label(
            self, text=f'{self.module.TITLE_START_DATE}: {datetime.fromtimestamp(start_date / 1000)}'
        ).pack(side='top', pady=5)

        # show average messages per time period
        sec_since_start = int(time() - start_date / 1000)
        ttk.Label(
            self, text=f'{self.module.TITLE_AVERAGE_MESSAGES}: '
        ).pack(side='top', pady=5)

        listbox = tk.Listbox(self, width=30, height=4)
        listbox.pack(side='top', pady=5)
        listbox.insert('end', f'{self.module.TITLE_PER_DAY} - {all_msgs / (sec_since_start / 86400):.2f}')
        listbox.insert('end', f'{self.module.TITLE_PER_WEEK} - {all_msgs / (sec_since_start / (7 * 86400)):.2f}')
        listbox.insert('end', f'{self.module.TITLE_PER_MONTH} - {all_msgs / (sec_since_start / (30 * 86400)):.2f}')
        listbox.insert('end', f'{self.module.TITLE_PER_YEAR} - {all_msgs / (sec_since_start / (365 * 86400)):.2f}')

        # box to contain first five messages:
        ttk.Label(
            self, text="First 5 Messages:"
        ).pack(side='top', pady=5)

        messages_frame = ttk.Frame(self)  # Frame to hold Listbox and Scrollbar for messages
        messages_frame.pack(side='top', fill='both', expand=True)

        messages_scrollbar = ttk.Scrollbar(messages_frame)
        messages_scrollbar.pack(side='right', fill='y')

        messages_listbox = tk.Listbox(messages_frame, width=50, height=1, yscrollcommand=messages_scrollbar.set)
        messages_listbox.pack(side='left', fill='both', expand=True)
        messages_scrollbar.config(command=messages_listbox.yview)

        for sender_name, content in first_five_messages:
            messages_listbox.insert('end', f"{sender_name}: {content}")

        # add close button to close statistics popup
        ttk.Button(self, text="Close", command=self.destroy).pack(side='bottom', pady=10)

class FilterPopup(tk.Toplevel):
    """
    This class implements the filter popup
    """
    def __init__(self, controller, columns, column_titles, filter_columns, apply_callback):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 800, 600)

        self.columns = columns
        print(self.columns)
        self.column_titles = column_titles        

        self.title(self.module.TITLE_FILTER)
        self.focus_set()
        self.grab_set()

        self.filter_entries = {}  # Dictionary to store filter entry widgets
        self.filter_columns = filter_columns

        self.apply_callback = apply_callback

        # Create filter GUI elements
        ttk.Label(self, text="Filter by:", foreground='#000000', background='#ffffff', font=('Arial', 15)).pack(side='top', pady=10)


        self.canvas = tk.Canvas(self, borderwidth=0)
        # place a frame on the canvas, this frame will hold the child widgets           
        self.viewPort = tk.Frame(self.canvas)
        # place a scrollbar on self                     
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) 
        # attach scrollbar action to scroll of canvas
        self.canvas.configure(yscrollcommand=self.vsb.set)                          
        
        # pack scrollbar to right of self
        self.vsb.pack(side="right", fill="y")
        # pack canvas to left of self and expand to fil                                       
        self.canvas.pack(side="left", fill="both", expand=True)
        # add view port frame to canvas                     
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            
                                  tags="self.viewPort")
        
        # bind an event whenever the size of the viewPort frame changes.
        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        # bind an event whenever the size of the canvas frame changes.                       
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       
        # bind wheel events when the cursor enters the control  
        self.viewPort.bind('<Enter>', self.onEnter)
        # unbind wheel events when the cursorl leaves the control                                 
        self.viewPort.bind('<Leave>', self.onLeave)                                 

        # perform an initial stretch on render, otherwise the scroll region 
        # has a tiny border until the first resize
        self.onFrameConfigure(None)                                                 
        for column in columns:
            label_width = len(self.column_titles[column]) + 2
            if column in ['name', 'pep', 'type']:
                label = ttk.Label(self.viewPort, text=self.column_titles[column], foreground='#000000', background='#ffffff', anchor="center", width = label_width)
                label.pack(side='top', pady=5)  # Fill the label horizontally
                entry = ttk.Entry(self.viewPort, width=30)
                entry.pack(side='top', pady=5)  # Fill the entry horizontally
                self.filter_entries[column] = entry
            else:  # For numerical fields
    
                label = ttk.Label(self.viewPort, text=f"{self.column_titles[column]}:", foreground='#000000', background='#ffffff', anchor="center", width = label_width)
                label.pack(side='top', pady=5)  # Fill the label horizontally
                
                label_frame = ttk.Frame(self.viewPort)
                label_frame.pack(side='top', pady=5)  # Fill and expand the label frame horizontally
                container_frame = ttk.Frame(label_frame)
                container_frame.pack()

                min_label = ttk.Label(container_frame, text="Min:")
                min_label.grid(row=0, column=0, padx=(0, 5))

                min_entry = ttk.Entry(container_frame, width=5)
                min_entry.grid(row=0, column=1, padx=(0, 5))

                max_label = ttk.Label(container_frame, text="Max:")
                max_label.grid(row=0, column=2, padx=(0, 5))

                max_entry = ttk.Entry(container_frame, width=5)
                max_entry.grid(row=0, column=3, padx=(0, 5))

                container_frame.grid_columnconfigure(0, weight=1)
                self.filter_entries[column] = (min_entry,max_entry)
        
        apply_button = ttk.Button(self.viewPort, text="Apply Filters", command=self.apply_filters)
        apply_button.pack(fill=tk.X, pady=10)  # Fill the button horizontally

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            

    def onMouseWheel(self, event):                                                  
        # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       
        # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       
        # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")


    def apply_filters(self):
        for column, entry in self.filter_entries.items():
            if column in ['name', 'type']:
                self.filter_columns[column] = entry.get()
            elif column == 'pep': 
                participant_names = [participant.strip() for participant in entry.get().split(',')]
                self.filter_columns[column] = set(participant_names)
            else:  # For numerical fields
                min_val = entry[0].get()
                max_val = entry[1].get()
                self.filter_columns[column] = (int(min_val) if min_val else -1, int(max_val) if max_val else -1)
        self.apply_callback()
        self.destroy()
        

 
if __name__ == '__main__':
    MasterWindow().mainloop()
