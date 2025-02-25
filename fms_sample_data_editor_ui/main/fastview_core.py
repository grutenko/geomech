import wx
import wx.propgrid

from ui.datetimeutil import decode_date
from pony.orm import db_session
from database import BoreHole


class FastviewOrigSampleSet(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER | wx.propgrid.PG_TOOLBAR)
        self.SetSplitterPosition(150)
        prop = self.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("№", "Number"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        self.SetPropertyReadOnly(prop)
        category = self.Append(wx.propgrid.PropertyCategory("Координаты", "Coords"))
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("X (м)", "X"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Y (м)", "Y"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Z (м)", "Z"))
        self.SetPropertyReadOnly(prop)
        category = self.Append(wx.propgrid.PropertyCategory("Параметры", "Params"))
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Азимут (град.)", "Azimuth"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Наклон (град.)", "Tilt"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Диаметр (м)", "Diameter"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Длина (м)", "Length"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.DateProperty("Дата закладки", "StartDate"))
        prop.SetFormat("%d.%m.%Y")
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.DateProperty("Дата завершения", "EndDate"))
        prop.SetFormat("%d.%m.%Y")
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.DateProperty("Дата ликвидации", "DestroyDate"))
        prop.SetFormat("%d.%m.%Y")
        self.SetPropertyReadOnly(prop)
        self.Hide()

    @db_session
    def start(self, o):
        o = BoreHole[o.bore_hole.RID]
        start_date = decode_date(o.StartDate)
        fields = {
            "RID": o.RID,
            "Number": o.Number,
            "Name": o.Name,
            "Comment": o.Comment,
            "X": o.X,
            "Y": o.Y,
            "Z": o.Z,
            "Azimuth": o.Azimuth,
            "Tilt": o.Tilt,
            "Diameter": o.Diameter,
            "Length": o.Length,
            "StartDate": wx.DateTime(start_date.day, start_date.month - 1, start_date.year),
        }
        if o.EndDate != None:
            date = decode_date(o.EndDate)
            fields["EndDate"] = wx.DateTime(date.day, date.month - 1, date.year)
        if o.DestroyDate != None:
            date = decode_date(o.DestroyDate)
            fields["DestroyDate"] = wx.DateTime(date.day, date.month - 1, date.year)
        self.SetPropertyValues(fields)
        self.Update()
        self.Show()
