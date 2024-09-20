import wx

from pony.orm import *

from ui.datetimeutil import decode_date
from ..fastview_propgrid import FastviewPropgrid


class DischargeSeriesFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)
        self.propgrid = FastviewPropgrid(self)
        self.propgrid.SetSplitterPosition(150)
        prop = self.propgrid.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(
            wx.propgrid.LongStringProperty("Комментарий", "Comment")
        )
        prop = self.propgrid.Append(
            wx.propgrid.DateProperty("Дата начала", "StartMeasure")
        )
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(
            wx.propgrid.DateProperty("Дата окончания", "EndMeasure")
        )
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(
            wx.propgrid.StringProperty("Документ", "foundation_document")
        )
        self.propgrid.SetPropertyReadOnly(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    @db_session
    def start(self, o, bounds=None):
        start_date = decode_date(o.StartMeasure)
        fields = {
            "RID": o.RID,
            "Name": o.Name,
            "Comment": o.Comment,
            "StartMeasure": wx.DateTime(
                start_date.day, start_date.month - 1, start_date.year
            ),
            "foundation_document": (
                o.foundation_document.Name
                if o.foundation_document != None
                else "-- Без документа --"
            ),
        }
        if o.EndMeasure != None:
            date = decode_date(o.EndMeasure)
            fields["EndMeasure"] = wx.DateTime(date.day, date.month - 1, date.year)
        self.propgrid.SetPropertyValues(fields)
        self.Show()

    def end(self):
        self.Hide()
