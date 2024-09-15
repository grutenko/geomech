import wx
import wx.propgrid

from ..fastview_propgrid import FastviewPropgrid

class BoreHoleFastview(wx.Panel):
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
        category = self.propgrid.Append(wx.propgrid.PropertyCategory("Координаты", "Coords"))
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("X", "X"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Y", "Y"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Z", "Z"))
        self.propgrid.DisableProperty(prop)
        category = self.propgrid.Append(wx.propgrid.PropertyCategory("Параметры", "Params"))
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Азимут", "Azimuth"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Наклон", "Tilt"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Диаметр", "Diameter"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Длина", "Length"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.DateProperty("Дата закладки", "StartDate"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.DateProperty("Дата завершения", "EndDate"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.DateProperty("Дата ликвидации", "DestroyDate"))
        self.propgrid.DisableProperty(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)

        self.Layout()
        self.Hide()

    def start(self, o, bounds = None):
        self.Show()
    def end(self):
        self.Hide()