import wx
import wx.dataview
from pony.orm import *
import database

class SuppliedDataWidget(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.dataview.TreeListCtrl(self, style=wx.dataview.TL_DEFAULT_STYLE | wx.BORDER_NONE)
        self.list.AppendColumn("Название", 250)
        self.list.AppendColumn("Тип", 50)
        self.list.AppendColumn("Размер", 150)
        main_sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.Layout()