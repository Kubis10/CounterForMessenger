import unittest
from unittest.mock import MagicMock
import sys

# Define dummy classes for tkinter
class DummyFrame:
    def __init__(self, parent=None, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def grid(self, *args, **kwargs):
        pass
    def tkraise(self, *args, **kwargs):
        pass
    def config(self, *args, **kwargs):
        pass
    def configure(self, *args, **kwargs):
        pass

class DummyScrollbar:
    def __init__(self, parent=None, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def set(self, *args, **kwargs):
        pass
    def config(self, *args, **kwargs):
        pass

class DummyTreeview:
    def __init__(self, *args, **kwargs):
        self.mock = MagicMock()
    def column(self, *args, **kwargs):
        pass
    def heading(self, *args, **kwargs):
        pass
    def bind(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def selection_set(self, *args, **kwargs):
        pass
    def selection_remove(self, *args, **kwargs):
        pass
    def selection(self, *args, **kwargs):
        return []
    def get_children(self, *args, **kwargs):
        return []
    def item(self, *args, **kwargs):
        return {'values': []}
    def delete(self, *args, **kwargs):
        pass
    def set(self, *args, **kwargs):
        pass
    def move(self, *args, **kwargs):
        pass
    def yview(self, *args, **kwargs):
        pass
    def tag_configure(self, *args, **kwargs):
        pass
    def __setitem__(self, key, value):
        pass
    def __getitem__(self, key):
        return []

class DummyLabel:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def configure(self, *args, **kwargs):
        pass

class DummyButton:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def configure(self, *args, **kwargs):
        pass

class DummyEntry:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def insert(self, *args, **kwargs):
        pass
    def bind(self, *args, **kwargs):
        pass
    def get(self):
        return ""
    def delete(self, *args, **kwargs):
        pass

# Setup mocks
mock_tk = MagicMock()
mock_tk.Frame = DummyFrame
mock_tk.Scrollbar = DummyScrollbar
mock_tk.NO = 'no'
mock_tk.Scrollbar.set = MagicMock() # Needs to be callable

mock_ttk = MagicMock()
mock_ttk.Frame = DummyFrame
mock_ttk.Treeview = DummyTreeview
mock_ttk.Label = DummyLabel
mock_ttk.Button = DummyButton
mock_ttk.Entry = DummyEntry
mock_ttk.Style = MagicMock

# IMPORTANT: Link them
mock_tk.ttk = mock_ttk

sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk
sys.modules['popups.statistics_popup'] = MagicMock()
sys.modules['popups.multi_sort_popup'] = MagicMock()
sys.modules['popups.loading_popup'] = MagicMock()
sys.modules['utils'] = MagicMock()

from gui.main_page import MainPage

class TestMainPageSearch(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.controller.lang_mdl = MagicMock()
        self.controller.lang_mdl.TITLE_NAME = "Name"
        self.controller.lang_mdl.TITLE_SEARCH = "Search"
        self.controller.theme_manager = MagicMock()

        # Instantiate MainPage
        self.page = MainPage(MagicMock(), self.controller)

        # Mock the treeview attribute on the instance
        self.page.treeview = MagicMock()
        self.page.search_entry = MagicMock()

    def test_search_found(self):
        print("Running test_search_found")
        self.page.treeview.get_children.return_value = ['item1', 'item2', 'item3']

        def get_item(item_id):
            if item_id == 'item1':
                return {'values': ['Alice', 'Group', 10]}
            elif item_id == 'item2':
                return {'values': ['Bob', 'Private', 5]}
            elif item_id == 'item3':
                return {'values': ['Charlie', 'Group', 20]}
            return {}

        self.page.treeview.item.side_effect = get_item
        self.page.search_entry.get.return_value = 'Alice'

        self.page.search()

        self.page.treeview.selection_set.assert_called_with(['item1'])

    def test_search_partial(self):
        print("Running test_search_partial")
        self.page.treeview.get_children.return_value = ['item1', 'item2']

        def get_item(item_id):
            if item_id == 'item1':
                return {'values': ['Superman', 'Group', 10]}
            elif item_id == 'item2':
                return {'values': ['Batman', 'Private', 5]}
            return {}
        self.page.treeview.item.side_effect = get_item
        self.page.search_entry.get.return_value = 'man'

        self.page.search()

        self.page.treeview.selection_set.assert_called_with(['item1', 'item2'])

    def test_search_numeric(self):
        print("Running test_search_numeric")
        self.page.treeview.get_children.return_value = ['item1', 'item2']

        def get_item(item_id):
            if item_id == 'item1':
                return {'values': ['Alice', 'Group', 12345]}
            elif item_id == 'item2':
                return {'values': ['Bob', 'Private', 67890]}
            return {}
        self.page.treeview.item.side_effect = get_item
        self.page.search_entry.get.return_value = '123'

        self.page.search()

        self.page.treeview.selection_set.assert_called_with(['item1'])

    def test_search_not_found(self):
        print("Running test_search_not_found")
        self.page.treeview.get_children.return_value = ['item1']
        self.page.treeview.item.return_value = {'values': ['Alice', 'Group', 10]}
        self.page.search_entry.get.return_value = 'Bob'

        self.page.search()

        self.page.treeview.selection_set.assert_called_with([])

if __name__ == '__main__':
    unittest.main()
