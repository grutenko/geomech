import wx
from .fastview_propgrid import FastviewPropgrid

class PmSampleSetFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.propgrid = FastviewPropgrid(self)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds = None):
        self.Update()
        self.Show()
        
    def end(self):
        self.Hide()