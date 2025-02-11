import wx
import wx.propgrid
from pony.orm import *
import wx.propgrid

from database import *
from ui.icon import get_icon
from ui.validators import *


class RockBurstEditor(wx.Frame):
    @db_session
    def __init__(self, parent, o=None):
        super().__init__(
            parent,
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
        )
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.SetSize(wx.Size(900, 400))
        self.CenterOnScreen()
        self.o = o
        if o == None:
            self.SetTitle("Добавить горный удар")
        else:
            self.SetTitle("Горный удар: " + o.Name)

        top_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Месторождение", size=wx.Size(250, -1))
        left_sizer.Add(label, 0, wx.EXPAND)
        self.field_field = wx.Choice(self)
        data = select(o for o in MineObject if o.Type == "FIELD").order_by(lambda x: desc(x.RID))
        self._fields = []
        for o in data:
            self._fields.append(o)
            self.field_field.Append(o.Name)
        if len(self._fields) > 0:
            self.field_field.SetSelection(0)
        left_sizer.Add(self.field_field, 0, wx.EXPAND | wx.BOTTOM, border=5)

        label = wx.StaticText(self, label="Тип события", size=wx.Size(250, -1))
        left_sizer.Add(label, 0, wx.EXPAND)
        self.field_type = wx.Choice(self)
        left_sizer.Add(self.field_type, 0, wx.EXPAND | wx.BOTTOM, border=5)

        self.field_dynamic = wx.CheckBox(self, label="Динамическое событие?")
        left_sizer.Add(self.field_dynamic, 0, wx.EXPAND | wx.BOTTOM, border=5)

        label = wx.StaticText(
            self,
            label="Дата и время события",
        )
        left_sizer.Add(label, 0, wx.EXPAND)
        self.field_burst_date = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_burst_date.SetValidator(DateValidator())
        left_sizer.Add(self.field_burst_date, 0, wx.EXPAND | wx.BOTTOM, border=5)

        label = wx.StaticText(
            self,
            label="Название",
        )
        left_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        left_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=5)

        label = wx.StaticText(self, label="Комментарий")
        left_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(self, size=wx.Size(250, 100), style=wx.TE_MULTILINE)
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        left_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=5)

        main_sizer.Add(left_sizer, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)

        self.notebook = wx.Notebook(self)

        self.page_main = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_main_propgrid = wx.propgrid.PropertyGrid(self.page_main, style=wx.propgrid.PG_DEFAULT_STYLE | wx.propgrid.PG_SPLITTER_AUTO_CENTER)
        pg = self.page_main_propgrid
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
        sizer.Add(self.page_main_propgrid, 1, wx.EXPAND)
        self.page_main.SetSizer(sizer)
        self.notebook.AddPage(self.page_main, "Карточка ГУ")

        main_sizer.Add(self.notebook, 1, wx.EXPAND)

        top_sizer.Add(main_sizer, 1, wx.EXPAND)

        self.btn_save = wx.Button(self, label="Сохранить")
        top_sizer.Add(self.btn_save, 0, wx.ALL, border=10)

        self.SetSizer(top_sizer)
        self.Layout()
