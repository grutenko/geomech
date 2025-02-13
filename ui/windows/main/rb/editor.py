import wx
import wx.propgrid
from pony.orm import db_session, select, desc
from database import RockBurst, RBTypicalCause, RBCause, RBType, RBTypicalPreventAction, RBPreventAction, RBSign, RBTypicalSign, MineObject
from ui.icon import get_icon
from ui.validators import TextValidator, DateValidator
from .prevent_actions_list import PreventActionsList
from pubsub.pub import subscribe, unsubscribe


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
        self.my_signs = []
        self.my_causes = []

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
        self._types = []
        data = select(o for o in RBType).order_by(lambda x: x.Name)
        for o in data:
            self.field_type.Append(o.Name)
            self._types.append(o)
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
            label="Номер",
        )
        left_sizer.Add(label, 0)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=256))
        left_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=5)

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

        self.page_signs = wx.CheckListBox(self.notebook)
        self.load_signs()
        self.notebook.AddPage(self.page_signs, "Признаки удароопасности")

        self.page_causes = wx.CheckListBox(self.notebook)
        self.load_causes()
        self.notebook.AddPage(self.page_causes, "Причины")

        self.page_prevent_actions = PreventActionsList(self.notebook, [])
        self.notebook.AddPage(self.page_prevent_actions, "Профилактические мероприятия")

        main_sizer.Add(self.notebook, 1, wx.EXPAND)

        top_sizer.Add(main_sizer, 1, wx.EXPAND)

        self.btn_save = wx.Button(self, label="Сохранить")
        top_sizer.Add(self.btn_save, 0, wx.ALL, border=10)

        self.SetSizer(top_sizer)
        self.Layout()

        subscribe(self.on_object_changed, "object.added")
        subscribe(self.on_object_changed, "object.deleted")
        self.Bind(wx.EVT_CLOSE, self.on_close)

    @db_session
    def load_signs(self):
        self.signs = []
        self.page_signs.Clear()
        self.my_signs = list(map(lambda x: x.rb_typical_sign, select(o for o in RBSign if o.rock_burst == self.o)))
        for sign in select(o for o in RBTypicalSign):
            self.page_signs.Append(sign.Name)
            self.page_signs.Check(self.page_signs.GetCount() - 1, sign in self.my_signs)
            self.signs.append(sign)

    @db_session
    def load_causes(self):
        self.causes = []
        self.page_causes.Clear()
        self.my_causes = list(map(lambda x: x.rb_typical_cause, select(o for o in RBCause if o.rock_burst == self.o)))
        for cause in select(o for o in RBTypicalCause):
            self.page_causes.Append(cause.Name)
            self.page_causes.Check(self.page_causes.GetCount() - 1, cause in self.my_causes)
            self.causes.append(cause)

    @db_session
    def on_object_changed(self, o):
        self.load_causes()
        self.load_signs()

    def on_close(self, event):
        unsubscribe(self.on_object_changed, "object.added")
        unsubscribe(self.on_object_changed, "object.deleted")
        event.Skip()
