import wx

from ui.widgets.supplied_data.widget import SuppliedDataWidget

class MainWindowSuppliedData(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._notebook = wx.Notebook(self)

        object_panel = wx.Panel(self._notebook)
        object_sizer = wx.BoxSizer(wx.VERTICAL)
        self._widget = SuppliedDataWidget(object_panel)
        object_sizer.Add(self._widget, 1, wx.EXPAND)
        object_panel.SetSizer(object_sizer)
        self._notebook.AddPage(object_panel, "Объект")

        main_sizer.Add(self._notebook, 1, wx.EXPAND)
        
        self.SetSizer(main_sizer)

        self.Layout()