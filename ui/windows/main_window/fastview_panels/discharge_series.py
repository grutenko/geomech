import wx
from ..fastview_propgrid import FastviewPropgrid

class DischargeSeriesFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)
        self.propgrid = FastviewPropgrid(self)
        self.propgrid.SetSplitterPosition(150)
        prop = self.propgrid.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("№", "Number"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        prop = self.propgrid.Append(wx.propgrid.DateProperty("Дата проведения", "MeasureDate"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Документ", "foundation_document"))
        self.propgrid.DisableProperty(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()
        
    def start(self, o, bounds = None):
        self.Show()
    def end(self):
        self.Hide()