import wx

class PmSampleSetsListFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._list = wx.ListCtrl(self, style=wx.LC_REPORT)
        main_sizer.Add(self._list, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds = None):
        self.Show()
    def end(self):
        self.Hide()