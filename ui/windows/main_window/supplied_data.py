import wx

from ui.widgets.supplied_data.widget import SuppliedDataWidget
from database import *

class MainWindowSuppliedData(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._widget = SuppliedDataWidget(self)
        main_sizer.Add(self._widget, 1, wx.EXPAND)
        
        self.SetSizer(main_sizer)

        self.Layout()

    def start(self, o, _type):
        self._widget.start(o, _type)

    def end(self):
        self._widget.end()