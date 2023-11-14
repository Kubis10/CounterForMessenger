import json
import tkinter as tk
import glob
import importlib
from collections import defaultdict
from datetime import timedelta, datetime
from shlex import join
from tkinter import ttk, filedialog
from os import listdir
from os.path import isfile, join, exists

# safeguard for the treeview automated string conversion problem
PREFIX = '<@!PREFIX>'


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
            self.language_label.get()
        )
        # go to main page
        self.controller.show_frame(MainPage.__name__)

    # invoked by pressing the 'Open file explorer...' button
    def open_file_explorer(self):
        # Open File Explorer and extract the given path
        selected_directory = tk.filedialog.askdirectory()
        if selected_directory:
            # Ensure the path ends with a slash
            path = f"{selected_directory}/" if not selected_directory.endswith("/") else selected_directory
            self.directory_label.config(text=path)
            # Update the directory in the controller
            self.controller.directory = path
            # Attempt to find the user name based on the new directory
            self.controller.update_username_from_conversations(path)
            user_name = self.controller.username
            if user_name:
                self.username_label.delete(0, tk.END)
                self.username_label.insert(0, user_name)
        else:
            # Handle the case where no directory is selected
            self.directory_label.config(text=self.module.TITLE_NO_SELECTION)


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
        }
        self.treeview.column('#0', width=0, stretch=tk.NO)
        self.treeview['columns'] = tuple(columns.keys())
        for keyword, text in columns.items():
            self.treeview.heading(keyword, text=text, anchor='center')
        self.treeview.bind('<Button-3>', lambda event: self.deselect())
        self.treeview.bind('<Double-1>', lambda event: self.show_statistics())

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


    # invoked on double left click on any treeview listing
    def show_statistics(self):
        try:
            selection = self.treeview.item(self.treeview.selection()[0]).get('values', [])
            if len(selection) == 0:
                return
            # treeview automated conversion problem, read StatisticsPopup comments
            # removing prefix safeguard
            StatisticsPopup(self.controller, selection[7].replace(PREFIX, ''))
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
            ConfigurationPage.__name__: [700, 450, None],
            MainPage.__name__: [1375, 700, None]
        }
        # initialize and load frames to container
        self.refresh_frames()

        # remember user that already went through configuration
        self.show_frame(
            MainPage.__name__ if exists('config.txt') else
            ConfigurationPage.__name__
        )

    def find_user_in_conversations(self, conversation):
        # Find all conversation files
        participant_counts = defaultdict(int)
        two_person_chats = []
        # List conversations
        for conversation in glob.glob(f'{self.directory}/*'):
            # Extract participants
            participants = set()
            for file in glob.glob(f'{conversation}/*.json'):
                with open(file, 'r') as f:
                    data = json.load(f)
                    for participant in data.get('participants', []):
                        name = participant['name'].encode('iso-8859-1').decode('utf-8')
                        if name != '':
                            participants.add(name)

            # Check if the chat has exactly two participants
            if len(participants) == 2:
                two_person_chats.append(participants)

        # Find a common participant
        for participants in two_person_chats:
            for participant in participants:
                participant_counts[participant] += 1
                if participant_counts[participant] > 1:
                    return participant  # Found a common participant

        return None  # No common participant found

    def update_username_from_conversations(self, directory):
        user_name = self.find_user_in_conversations(directory)
        if user_name:
            self.username = user_name
            # Update UI or other elements as needed
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
    def update_data(self, username, directory, language):
        temp = self.language
        self.username = username
        self.directory = directory
        self.language = language
        self.lang_mdl = importlib.import_module(f'langs.{language}')
        # also save user provided data to 'config.txt'
        with open('config.txt', 'w') as f:
            f.write(f'{username}\n{directory}\n{language}')
        # refresh only to apply a new language
        if temp != language:
            self.refresh_frames()

    def load_data(self):
        if exists('config.txt'):
            with open('config.txt', 'r') as f:
                self.username, self.directory, self.language = f.read().splitlines()
            self.lang_mdl = importlib.import_module(f'langs.{self.language}')

    # extract relevant data from given .json files
    def extract_data(self, conversation):
        participants = {}
        # noinspection PyUnresolvedReferences
        chat_title, chat_type = '', self.lang_mdl.TITLE_GROUP_CHAT
        call_duration, total_messages, total_chars, sent_messages, start_date, total_photos = 0, 0, 0, 0, 0, 0

        for file in glob.glob(f'{self.directory}{conversation}/*.json'):
            with open(file, 'r') as f:
                data = json.load(f)
                # collect all chat participants
                for participant in data.get('participants', []):
                    name = participant['name'].encode('iso-8859-1').decode('utf-8')
                    participants[name] = participants.get(name, 0)
                # update all relevant counters
                for message in data.get('messages', []):
                    total_messages += 1
                    total_chars += len(message)
                    sender = message['sender_name'].encode('iso-8859-1').decode('utf-8')
                    if sender == self.get_username():
                        sent_messages += 1
                    # keep track of each participant's message total
                    participants[sender] = participants.get(sender, 0) + 1
                    # save call durations, if any
                    call_duration += message.get('call_duration', 0)
                    # fetch conversation creation date
                    start_date = message['timestamp_ms']
                    if 'photos' in message:
                        total_photos += len(message['photos'])
                # fetch chat name and type
                chat_title = data.get('title', '').encode('iso-8859-1').decode('utf-8')
                try:
                    # trick: attempt to read 'joinable mode' element
                    # if non-existent, it means that the chat is a private one
                    _ = data['joinable_mode']
                except KeyError:
                    # noinspection PyUnresolvedReferences
                    chat_type = self.lang_mdl.TITLE_PRIVATE_CHAT

        return chat_title, participants, chat_type, total_messages, total_chars, call_duration, sent_messages, start_date, total_photos


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
            self.language_label.get()
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
        if path not in ['/', '']:
            self.controller.update_username_from_conversations(path)
            user_name = self.controller.username
            if user_name:
                self.username_label.delete(0, tk.END)
                self.username_label.insert(0, user_name)


class LoadingPopup(tk.Toplevel):
    def __init__(self, controller, chat_total, treeview):
        tk.Toplevel.__init__(self)
        self.controller = controller
        self.module = self.controller.lang_mdl
        set_resolution(self, 300, 100)

        # loading window customization
        self.title(f'{self.module.TITLE_LOADING}...')
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
                    title, people, room, all_msgs, all_chars, calltime, sent_msgs, _, total_photos = self.controller.extract_data(conversation)
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
                            title, set(people.keys()), room, all_msgs, calltime, total_photos, all_chars,
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
        set_resolution(self, 800, 600)

        # statistics window customization
        self.title(self.module.TITLE_STATISTICS)
        self.iconbitmap('assets/CFM.ico')
        self.focus_set()
        self.grab_set()

        title, people, room, all_msgs, all_chars, calltime, sent_msgs, start_date, total_photos = self.controller.extract_data(selection)
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
        ttk.Label(
            self, text=f'{self.module.TITLE_CALL_DURATION}: {timedelta(seconds=calltime)}'
        ).pack(side='top', pady=5)
        # show first message date
        ttk.Label(
            self, text=f'{self.module.TITLE_START_DATE}: {datetime.fromtimestamp(start_date / 1000)}'
        ).pack(side='top', pady=5)


if __name__ == '__main__':
    MasterWindow().mainloop()
