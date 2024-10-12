import wx
import wx.propgrid

from ui.datetimeutil import decode_date
from .fastview_propgrid import FastviewPropgrid


class BoreHoleFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.propgrid = FastviewPropgrid(self)
        self.propgrid.SetSplitterPosition(150)
        prop = self.propgrid.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("№", "Number"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        category = self.propgrid.Append(wx.propgrid.PropertyCategory("Координаты", "Coords"))
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("X (м)", "X"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Y (м)", "Y"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Z (м)", "Z"))
        self.propgrid.SetPropertyReadOnly(prop)
        category = self.propgrid.Append(wx.propgrid.PropertyCategory("Параметры", "Params"))
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Азимут (град.)", "Azimuth"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Наклон (град.)", "Tilt"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Диаметр (м)", "Diameter"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Длина (м)", "Length"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.DateProperty("Дата закладки", "StartDate"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.DateProperty("Дата завершения", "EndDate"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.DateProperty("Дата ликвидации", "DestroyDate"))
        self.propgrid.SetPropertyReadOnly(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds=None):
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
        self.propgrid.SetPropertyValues(fields)
        self.Show()

    def end(self):
        self.Hide()
