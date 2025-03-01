import wx
import wx.propgrid
from ui.datetimeutil import decode_date


class FastviewOrigOther(wx.propgrid.PropertyGrid):
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
        prop = self.Append(wx.propgrid.DateProperty("Дата отбора", "StartDate"))
        prop.SetFormat("%d.%m.%Y")
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.DateProperty("Дата завершения отбора", "EndDate"))
        prop.SetFormat("%d.%m.%Y")
        self.SetPropertyReadOnly(prop)
        self.Hide()

    def start(self, o):
        fields = {
            "RID": o.RID,
            "Number": o.Number,
            "Name": o.Name,
            "Comment": o.Comment if o.Comment is not None else "",
            "StartDate": decode_date(o.StartSetDate),
            "EndDate": decode_date(o.EndSetDate) if o.EndSetDate is not None else None,
        }
        self.SetPropertyValues(fields)
        self.Show()
