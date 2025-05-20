"""
CounterForMessenger - aplikacja do analizy wiadomości z Messengera
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

# Importy lokalnych modułów
from utils import set_icon, set_resolution, existing_languages, ThemeManager
from gui.config_page import ConfigurationPage
from gui.main_page import MainPage

class MasterWindow(tk.Tk):
    """Główne okno aplikacji CounterForMessenger"""

    def __init__(self, *args, **kwargs):
        """
        Inicjalizacja aplikacji

        Args:
            *args: Argumenty przekazywane do klasy bazowej
            **kwargs: Argumenty nazwane przekazywane do klasy bazowej
        """
        tk.Tk.__init__(self, *args, **kwargs)

        # Inicjalizacja menadżera motywów
        self.theme_manager = ThemeManager()

        # Ładowanie ikon odpowiednich dla aktualnego motywu
        self._load_icons()

        # Dane użytkownika
        self.directory = ''
        self.username = ''
        self.language = 'English'
        self.from_date_entry = ''
        self.to_date_entry = ''
        self.lang_mdl = importlib.import_module('langs.English')
        self.sent_messages = 0
        self.total_messages = 0
        self.total_chars = 0

        # Ładowanie danych użytkownika
        self.load_data()

        # Konfiguracja okna
        self.title('Counter for Messenger')
        set_icon(self)

        # Ustawienia kontenera ramek
        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Deklaracja dostępnych ramek i ich wymiarów
        self.frames = {
            "ConfigurationPage": [800, 600, None],
            "MainPage": [1375, 700, None]
        }

        # Inicjalizacja i ładowanie ramek do kontenera
        self.refresh_frames()

        # Wyświetlenie odpowiedniej strony startowej
        self.show_frame(
            "MainPage" if exists('config.txt') else "ConfigurationPage"
        )

    def _load_icons(self):
        """Ładuje ikony odpowiednie dla aktualnego motywu"""
        # Określ katalog ikon w zależności od motywu
        if self.theme_manager.get_current_theme() == "dark":
            icon_prefix = "light_"  # Jasne ikony dla ciemnego motywu
        else:
            icon_prefix = ""  # Domyślne (ciemne) ikony dla jasnego motywu

        # Ładuj ikony z odpowiedniego katalogu
        try:
            self.ICON_HOME = tk.PhotoImage(file=f'assets/{icon_prefix}home.png')
            self.ICON_SETTINGS = tk.PhotoImage(file=f'assets/{icon_prefix}settings.png')
            self.ICON_EXIT = tk.PhotoImage(file=f'assets/{icon_prefix}exit.png')
            self.ICON_STATUS_VISIBLE = tk.PhotoImage(file=f'assets/{icon_prefix}visible.png')
            self.ICON_SEARCH = tk.PhotoImage(file=f'assets/{icon_prefix}search.png')
            self.ICON_PROFILE = tk.PhotoImage(file=f'assets/{icon_prefix}person.png')
        except tk.TclError:
            # Jeśli nie ma ikon dla ciemnego motywu, użyj domyślnych
            print(f"Nie znaleziono ikon dla {icon_prefix}. Używam domyślnych.")
            self.ICON_HOME = tk.PhotoImage(file='assets/home.png')
            self.ICON_SETTINGS = tk.PhotoImage(file='assets/settings.png')
            self.ICON_EXIT = tk.PhotoImage(file='assets/exit.png')
            self.ICON_STATUS_VISIBLE = tk.PhotoImage(file='assets/visible.png')
            self.ICON_SEARCH = tk.PhotoImage(file='assets/search.png')
            self.ICON_PROFILE = tk.PhotoImage(file='assets/person.png')

    def show_frame(self, page_name):
        """
        Wyświetla wybraną ramkę

        Args:
            page_name: Nazwa strony do wyświetlenia
        """
        width, height, frame = self.frames.get(page_name)
        set_resolution(self, width, height)
        # Pokazanie nowej ramki
        frame.tkraise()

    def get_username(self):
        """
        Pobiera nazwę użytkownika

        Returns:
            Nazwa użytkownika lub komunikat o braku nazwy
        """
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.username == '' or self.username.isspace() else self.username

    def get_directory(self):
        """
        Pobiera ścieżkę do katalogu z danymi

        Returns:
            Ścieżka do katalogu lub komunikat o braku wyboru
        """
        return self.lang_mdl.TITLE_NO_SELECTION if self.directory == '/' or self.directory.isspace() else self.directory

    def get_from_date_entry(self):
        """
        Pobiera datę początkową

        Returns:
            Data początkowa lub komunikat o braku daty
        """
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.from_date_entry == '' else self.from_date_entry

    def get_to_date_entry(self):
        """
        Pobiera datę końcową

        Returns:
            Data końcowa lub komunikat o braku daty
        """
        return self.lang_mdl.TITLE_NOT_APPLICABLE if self.to_date_entry == '' else self.to_date_entry

    def get_language(self):
        """
        Pobiera aktualny język

        Returns:
            Nazwa aktualnie wybranego języka
        """
        # Sprawdzenie czy zmienna językowa zawiera prawidłowe przypisanie
        if self.language not in existing_languages():
            # Domyślny język to angielski
            self.language = 'English'
            self.lang_mdl = importlib.import_module('langs.English')
        return self.language

    def refresh_frames(self):
        """Inicjalizuje i układa wszystkie ramki aplikacji"""
        # Inicjalizacja i ułożenie wszystkich ramek na sobie
        # Przełączanie między ramkami pozwoli na nawigację w aplikacji
        # bez zamykania jej
        for page_class in (ConfigurationPage, MainPage):
            page_name = page_class.__name__
            width, height, old_frame = self.frames[page_name]
            new_frame = page_class(parent=self.container, controller=self)
            self.frames[page_name] = [width, height, new_frame]
            new_frame.grid(row=0, column=0, sticky='nsew')

    def update_data(self, username, directory, language, from_date_entry, to_date_entry):
        """
        Aktualizuje dane użytkownika

        Args:
            username: Nazwa użytkownika
            directory: Ścieżka do katalogu z danymi
            language: Wybrany język
            from_date_entry: Data początkowa
            to_date_entry: Data końcowa
        """
        temp = self.language
        self.username = username
        self.directory = directory
        self.language = language
        self.from_date_entry = from_date_entry
        self.to_date_entry = to_date_entry
        self.lang_mdl = importlib.import_module(f'langs.{language}')

        # Zapisanie danych użytkownika w pliku config.txt
        with open('config.txt', 'w', encoding='utf-8') as f:
            f.write(f'{username}\n{directory}\n{language}\n{from_date_entry}\n{to_date_entry}')

        # Odświeżenie interfejsu tylko jeśli zmienił się język
        if temp != language:
            self.refresh_frames()

    def load_data(self):
        """Wczytuje dane użytkownika z pliku config.txt"""
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
                print(f"Błąd wczytywania konfiguracji: {e}")

    def extract_data(self, conversation):
        """
        Wydobywa dane z plików JSON dla danej konwersacji

        Args:
            conversation: Folder konwersacji do przetworzenia

        Returns:
            Tuple zawierający różne statystyki konwersacji
        """
        participants = {}
        chat_title, chat_type = '', self.lang_mdl.TITLE_GROUP_CHAT
        call_duration = total_messages = total_chars = sent_messages = start_date = 0
        total_photos = total_gifs = total_videos = total_files = 0

        # Przetwarzanie dat
        self._normalize_dates()

        # Przetwarzanie plików JSON w folderze konwersacji
        for file in glob.glob(f'{self.directory}{conversation}/*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Zbieranie uczestników czatu
                    for participant in data.get('participants', []):
                        name = participant['name']
                        participants[name] = participants.get(name, 0)

                    # Aktualizacja liczników
                    for message in data.get('messages', []):
                        message_date = datetime.fromtimestamp(int(message["timestamp_ms"]) / 1000).date()

                        # Filtrowanie wiadomości w wybranym okresie
                        if self.from_date_entry <= message_date <= self.to_date_entry:
                            total_messages += 1

                            # Zliczanie znaków
                            try:
                                total_chars += len(message.get('content', ''))
                            except (KeyError, TypeError):
                                pass

                            # Zliczanie wiadomości nadawcy
                            sender = message['sender_name']
                            if sender == self.get_username():
                                sent_messages += 1

                            # Śledzenie wiadomości uczestników
                            participants[sender] = participants.get(sender, 0) + 1

                            # Zapisywanie czasu połączeń
                            call_duration += message.get('call_duration', 0)

                            # Zapisz datę utworzenia konwersacji
                            current_timestamp = message['timestamp_ms']
                            if start_date == 0 or current_timestamp < start_date:
                                start_date = current_timestamp

                            # Zliczanie multimediów
                            if 'photos' in message:
                                total_photos += len(message['photos'])
                            if 'gifs' in message:
                                total_gifs += len(message['gifs'])
                            if 'videos' in message:
                                total_videos += len(message['videos'])
                            if 'files' in message:
                                total_files += len(message['files'])

                    # Pobierz nazwę i typ czatu
                    chat_title = data.get('title', '')

                    # Sprawdź czy to czat prywatny
                    try:
                        # Jeśli nie ma elementu 'joinable_mode', to czat jest prywatny
                        _ = data['joinable_mode']
                    except KeyError:
                        chat_type = self.lang_mdl.TITLE_PRIVATE_CHAT
            except Exception as e:
                print(f"Błąd przetwarzania pliku {file}: {e}")

        return (
            chat_title, participants, chat_type, total_messages, total_chars,
            call_duration, sent_messages, start_date, total_photos, total_gifs,
            total_videos, total_files
        )

    def _normalize_dates(self):
        """Normalizuje format dat wejściowych i wyjściowych"""
        # Konwersja krotek na wartość pojedynczą
        if isinstance(self.from_date_entry, tuple) and len(self.from_date_entry) == 1:
            self.from_date_entry = self.from_date_entry[0]
        if isinstance(self.to_date_entry, tuple) and len(self.to_date_entry) == 1:
            self.to_date_entry = self.to_date_entry[0]

        # Konwersja stringów na obiekty dat
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

    def toggle_theme(self):
        """Przełącza między jasnym i ciemnym motywem"""
        self.theme_manager.toggle_theme()
        # Odśwież ramki, aby zastosować nowy motyw
        self.refresh_frames()


if __name__ == "__main__":
    app = MasterWindow()
    app.mainloop()
