import wx

from ui.widgets.tree import *
from .create_test_series_dialog import CreateTestSeriesDialog

class TestSeriesTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.bind_all()

    def open_create_series_dialog(self):
        dlg = CreateTestSeriesDialog(self)
        dlg.ShowModal()

    def open_edit_series_dialog(self):
        node = self.get_current_node()
        if node != None:
            dlg = CreateTestSeriesDialog(self, node.o, type="UPDATE")
            dlg.ShowModal()