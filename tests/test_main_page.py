import unittest
from unittest.mock import MagicMock, patch
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
        pass
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

class TestMainPageSearch(unittest.TestCase):
    def setUp(self):
        # Setup mocks
        self.mock_tk = MagicMock()
        self.mock_tk.Frame = DummyFrame
        self.mock_tk.Scrollbar = DummyScrollbar
        self.mock_tk.NO = 'no'
        self.mock_tk.Scrollbar.set = MagicMock()

        self.mock_ttk = MagicMock()
        self.mock_ttk.Frame = DummyFrame
        self.mock_ttk.Treeview = DummyTreeview
        self.mock_ttk.Label = DummyLabel
        self.mock_ttk.Button = DummyButton
        self.mock_ttk.Entry = DummyEntry
        self.mock_ttk.Style = MagicMock

        # IMPORTANT: Link them
        self.mock_tk.ttk = self.mock_ttk

        # Create the patcher
        self.modules_patcher = patch.dict(sys.modules, {
            'tkinter': self.mock_tk,
            'tkinter.ttk': self.mock_ttk,
            'popups.statistics_popup': MagicMock(),
            'popups.multi_sort_popup': MagicMock(),
            'popups.loading_popup': MagicMock(),
            'utils': MagicMock()
        })
        self.modules_patcher.start()

        # Import module under test inside setUp to ensure it uses the mocks
        # Remove from sys.modules if it's there to force reload
        if 'gui.main_page' in sys.modules:
            del sys.modules['gui.main_page']

        import gui.main_page
        self.main_page_module = gui.main_page

        self.controller = MagicMock()
        self.controller.lang_mdl = MagicMock()
        self.controller.lang_mdl.TITLE_NAME = "Name"
        self.controller.lang_mdl.TITLE_SEARCH = "Search"
        self.controller.theme_manager = MagicMock()

        # Instantiate MainPage
        self.page = self.main_page_module.MainPage(MagicMock(), self.controller)

        # Mock the treeview attribute on the instance
        self.page.treeview = MagicMock()
        self.page.search_entry = MagicMock()

    def tearDown(self):
        self.modules_patcher.stop()

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
