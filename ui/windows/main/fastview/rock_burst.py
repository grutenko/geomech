import wx

from ui.datetimeutil import decode_date

from .fastview_propgrid import FastviewPropgrid


class RockBurstFastview(wx.Panel):
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
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.DateProperty("Дата события", "BurstDate"))
        self.propgrid.SetPropertyReadOnly(prop)
        category = self.propgrid.Append(wx.propgrid.PropertyCategory("Координаты", "Coords"))
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("X (м)", "X"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Y (м)", "Y"))
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Z (м)", "Z"))
        self.propgrid.SetPropertyReadOnly(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds=None):
        burst_date = decode_date(o.BurstDate)
        fields = {
            "RID": o.RID,
            "Number": o.Number,
            "Name": o.Name,
            "Comment": o.Comment,
            "X": o.X,
            "Y": o.Y,
            "Z": o.Z,
            "BurstDate": wx.DateTime(burst_date.day, burst_date.month - 1, burst_date.year),
        }
        self.propgrid.SetPropertyValues(fields)
        self.Update()
        self.Show()

    def end(self):
        self.Hide()
