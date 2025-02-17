import wx
import wx.propgrid


class RockBurstDialogPropeties(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.propgrid = wx.propgrid.PropertyGrid(self, style=wx.propgrid.PG_DEFAULT_STYLE | wx.propgrid.PG_SPLITTER_AUTO_CENTER)
        pg = self.propgrid
        pg.Append(wx.propgrid.FloatProperty("Глубина поверхност. (м)", "BurstDepth"))
        pg.Append(wx.propgrid.LongStringProperty("Описание места", "Place"))
        sect = pg.Append(wx.propgrid.PropertyCategory("Координаты"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Разрез (от)", "LayerFrom"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Разрез (до)", "LayerTo"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Магистраль (от)", "MagistralFrom"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Магистраль (до)", "MagistralTo"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Высотная отметка (от)", "HeightFrom"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Высотная отметка (до)", "HeightTo"))
        sect = pg.Append(wx.propgrid.PropertyCategory("Последствия"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Объем вываленой породы", "OccrVolume"))
        pg.AppendIn(sect, wx.propgrid.FloatProperty("Масса вываленой породы", "OccrWeight"))
        p = wx.propgrid.BoolProperty("Звуковой эффект", "OccrSound")
        p.SetAttribute(wx.propgrid.PG_BOOL_USE_CHECKBOX, True)
        pg.AppendIn(sect, p)
        pg.AppendIn(sect, wx.propgrid.LongStringProperty("Дополнительные сведения", "OccrComment"))
        sz.Add(self.propgrid, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
