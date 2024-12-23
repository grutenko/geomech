import wx
from pony.orm import *

from database import *

from .fastview_propgrid import FastviewPropgrid


class PmSampleSetFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.propgrid = FastviewPropgrid(self)
        self.propgrid.SetSplitterPosition(150)
        prop = self.propgrid.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Номер", "Number"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Место проведения испытаний", "Location"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Документ", "foundation_document"))
        self.propgrid.SetPropertyReadOnly(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    @db_session
    def start(self, o, bounds=None):
        self.Update()
        self.Show()

    def end(self):
        self.Hide()
