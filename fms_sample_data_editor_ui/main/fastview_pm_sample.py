import wx
import wx.propgrid
from pony.orm import db_session
from ui.datetimeutil import decode_date
from database import OrigSampleSet


class FastviewPmSample(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER | wx.propgrid.PG_TOOLBAR)
        prop = self.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("№", "Number"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Набор образцов", "@orig_sample_set"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.DateProperty("Дата отбора", "SetDate"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Начальная позиция (м)", "StartPosition"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Конечная позиция (м)", "EndPosition"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("№ ящика", "BoxNumber"))
        self.SetPropertyReadOnly(prop)
        self.Hide()

    @db_session
    def start(self, o):
        fields = {
            "RID": o.RID,
            "Number": o.Number,
            "@orig_sample_set": OrigSampleSet[o.orig_sample_set.RID].Name,
            "SetDate": decode_date(o.SetDate),
            "StartPosition": o.StartPosition.__str__(),
            "EndPosition": o.EndPosition.__str__() if o.EndPosition is not None else 0,
            "BoxNumber": o.BoxNumber if o.BoxNumber is not None else 0,
        }
        self.SetPropertyValues(fields)
        self.Show()
