import wx
from ui.widgets.tree.widget import Tree, TreeNode

from pony.orm import *
from database import PMTestSeries

class PmSeriesDetail(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self._tree = Tree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Hide()

    def get_item_name(self):
        if self.o != None:
            return self.o.get_tree_name()
        return ""
    
    def _render(self):
        ...

    @db_session
    def start(self, rid):
        self.o = PMTestSeries[rid]
        self.rid = self.o.RID
        self._render()
        self.Show()

    def end(self):
        self.o = None
        self.rid = None
        self.Hide()