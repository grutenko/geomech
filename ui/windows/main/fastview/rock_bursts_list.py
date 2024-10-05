import wx

class RockBurstsListFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self._list.AppendColumn("ID", width=50)
        self._list.AppendColumn("Название", width=250)
        self._list.AppendColumn("Дата и время события", width=250)
        main_sizer.Add(self._list, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds = None):
        self.Show()
    def end(self):
        self.Hide()