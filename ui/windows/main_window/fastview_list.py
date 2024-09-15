import wx

class FastviewList(wx.ListCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT)

    def start(self, table):
        ...

    def stop(self):
        ...