import wx

from ui.datetimeutil import decode_date

from .fastview_propgrid import FastviewPropgrid


class CoreFastview(wx.Panel):
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
        prop = self.propgrid.Append(wx.propgrid.DateProperty("Дата отбора", "StartDate"))
        prop.SetFormat("%d.%m.%Y")
        self.propgrid.SetPropertyReadOnly(prop)
        prop = self.propgrid.Append(wx.propgrid.DateProperty("Дата завершения отбора", "EndDate"))
        prop.SetFormat("%d.%m.%Y")
        self.propgrid.SetPropertyReadOnly(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds=None):
        start_date = decode_date(o.StartSetDate)
        fields = {
            "RID": o.RID,
            "Number": o.Number,
            "Name": o.Name,
            "Comment": o.Comment,
            "StartDate": wx.DateTime(start_date.day, start_date.month - 1, start_date.year),
        }
        if o.EndSetDate != None:
            date = decode_date(o.EndSetDate)
            fields["EndDate"] = wx.DateTime(date.day, date.month - 1, date.year)
        self.propgrid.SetPropertyValues(fields)
        self.Update()
        self.Show()

    def end(self):
        self.Hide()
