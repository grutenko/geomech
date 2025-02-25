import wx

from pony.orm import db_session, select, commit
from database import MineObject, Station, BoreHole, OrigSampleSet
from ui.validators import TextValidator, DateValidator
import ui.datetimeutil


class OrigSampleSetSelectTypeDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Выбрать тип набора образцов", size=wx.Size(250, 200))
        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Тип набора")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_type = wx.Choice(self, choices=["Керн", "Штуф", "Дисперсный материал"])
        self.field_type.SetSelection(0)
        main_sz.Add(self.field_type, 0, wx.EXPAND)

        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)

        line = wx.StaticLine(self)
        main_sz.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Выбрать")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        sz.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)
        self.SetSizer(sz)
        self.Layout()
        self.type = "CORE"

    def on_save(self, event):
        if self.field_type.GetSelection() == 0:
            self.type = "CORE"
        elif self.field_type.GetSelection() == 1:
            self.type = "STUF"
        elif self.field_type.GetSelection() == 2:
            self.type = "DISPERCE"
        self.EndModal(wx.ID_OK)


class OrigSampleSetCoreDialog(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None):
        super().__init__(parent, title="Добавить керн", size=wx.Size(300, 550))
        _type = "CREATE"
        self._type = _type
        self._target = o
        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)

        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Месторождение")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_field = wx.Choice(self)
        main_sz.Add(self.field_field, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self.fields = []
        for o in select(o for o in MineObject if o.Type == "FIELD"):
            self.fields.append(o)
            self.field_field.Append(o.Name)
        if len(self.fields) > 0:
            self.field_field.SetSelection(0)

        if _type == "CREATE":
            autofill_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Поля для автозаполнения")
            label = wx.StaticText(self, label="Числовой № скважины")
            autofill_sizer.Add(label, 0)
            self.field_orig_no = wx.TextCtrl(self, size=wx.Size(250, -1))
            self.field_orig_no.Bind(wx.EVT_KEY_UP, self.on_orig_no_updated)
            autofill_sizer.Add(self.field_orig_no, 0, wx.EXPAND)
            main_sz.Add(autofill_sizer, 0, wx.EXPAND)

        label = wx.StaticText(
            self,
            label="Регистрационный номер " + ("(автом. из Числового №)*" if _type == "CREATE" else "*"),
        )
        main_sz.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sz.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(
            self,
            label="Название " + ("(автом. из Числового №)*" if _type == "CREATE" else "*"),
        )
        main_sz.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sz.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Комментарий")
        main_sz.Add(collpane, 0, wx.GROW)

        comment_pane = collpane.GetPane()
        comment_sizer = wx.BoxSizer(wx.VERTICAL)
        comment_pane.SetSizer(comment_sizer)

        label = wx.StaticText(comment_pane, label="Комментарий")
        comment_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(comment_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE)
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        comment_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Координаты")
        main_sz.Add(collpane, 0, wx.GROW)

        coords_pane = collpane.GetPane()
        coords_sizer = wx.BoxSizer(wx.VERTICAL)
        coords_pane.SetSizer(coords_sizer)

        cs_name = MineObject[self.fields[self.field_field.GetSelection()].RID].coord_system.Name
        self.coords_label = wx.StaticText(
            coords_pane,
            label="Система координат: " + (cs_name if len(cs_name) < 24 else cs_name[:24] + "..."),
        )
        coords_sizer.Add(self.coords_label, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.open_cs_transf = wx.Button(coords_pane, label="Открыть утилиту перевода координат")
        coords_sizer.Add(self.open_cs_transf, 0, wx.EXPAND)
        self.open_cs_transf.Bind(wx.EVT_BUTTON, self.on_open_cs_transf)

        label = wx.StaticText(coords_pane, label="X (м)")
        coords_sizer.Add(label, 0)
        self.field_x = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_x.SetDigits(2)
        coords_sizer.Add(self.field_x, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Y (м)")
        coords_sizer.Add(label, 0)
        self.field_y = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_y.SetDigits(2)
        coords_sizer.Add(self.field_y, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Z (м)")
        coords_sizer.Add(label, 0)
        self.field_z = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_z.SetDigits(2)
        coords_sizer.Add(self.field_z, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Параметры")
        main_sz.Add(collpane, 0, wx.GROW)

        props_pane = collpane.GetPane()
        props_sizer = wx.BoxSizer(wx.VERTICAL)
        props_pane.SetSizer(props_sizer)

        label = wx.StaticText(props_pane, label="Азимут (град.)")
        props_sizer.Add(label, 0)
        self.field_azimuth = wx.SpinCtrl(props_pane, min=-100000000, max=10000000000)
        props_sizer.Add(self.field_azimuth, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(props_pane, label="Наклон (град.)")
        props_sizer.Add(label, 0)
        self.field_tilt = wx.SpinCtrl(props_pane, min=-100000000, max=10000000000)
        props_sizer.Add(self.field_tilt, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(props_pane, label="Диаметр (мм)")
        props_sizer.Add(label, 0)
        self.field_diameter = wx.SpinCtrl(props_pane, min=-100000000, max=10000000000)
        props_sizer.Add(self.field_diameter, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(props_pane, label="Длина (м)")
        props_sizer.Add(label, 0)
        self.field_length = wx.SpinCtrlDouble(props_pane, min=-100000000.0, max=10000000000.0)
        self.field_length.SetDigits(2)
        props_sizer.Add(self.field_length, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата закладки скважины / начала измерений*")
        main_sz.Add(label, 0)
        self.field_start_date = wx.TextCtrl(self)
        self.field_start_date.SetValidator(DateValidator())

        main_sz.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения измерений")
        main_sz.Add(label, 0)
        self.field_end_date = wx.TextCtrl(self)
        self.field_end_date.SetValidator(DateValidator(allow_empty=True))
        main_sz.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата ликвидации скважины")
        main_sz.Add(label, 0)
        self.field_destroy_date = wx.TextCtrl(self)
        self.field_destroy_date.SetValidator(DateValidator(allow_empty=True))
        main_sz.Add(self.field_destroy_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sz.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Создать")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        sz.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)
        self.SetSizer(sz)
        self.Layout()

        self.field_field.Bind(wx.EVT_CHOICE, self.on_orig_no_updated)

    def on_open_cs_transf(self, event): ...

    @db_session
    def on_orig_no_updated(self, event):
        event.Skip()
        parent = MineObject[self.fields[self.field_field.GetSelection()].RID]
        cs_name = parent.coord_system.Name
        self.coords_label.SetLabel("Система координат: " + (cs_name if len(cs_name) < 24 else cs_name[:24] + "..."))
        name = str(self.field_orig_no.GetValue()) + " на"
        number = str(self.field_orig_no.GetValue())
        while parent.Level > 0:
            name += " " + parent.Name
            number += "@" + (parent.Name if len(parent.Name) < 4 else parent.Name[:4])
            parent = parent.parent

        self.field_name.SetValue(name)
        self.field_number.SetValue(number)

    @db_session
    def on_save(self, event):
        if not self.Validate():
            return

        fields = {
            "Number": self.field_number.GetValue(),
            "Name": self.field_name.GetValue(),
            "Comment": self.field_comment.GetValue(),
            "X": self.field_x.GetValue(),
            "Y": self.field_y.GetValue(),
            "Z": self.field_z.GetValue(),
            "Azimuth": float(self.field_azimuth.GetValue()),
            "Tilt": float(self.field_tilt.GetValue()),
            "Diameter": float(self.field_diameter.GetValue() / 1000),
            "Length": self.field_length.GetValue(),
        }

        if self._type == "CREATE":
            fields["mine_object"] = MineObject[self.fields[self.field_field.GetSelection()].RID]
            fields["station"] = None

        fields["StartDate"] = ui.datetimeutil.encode_date(self.field_start_date.GetValue())

        date = self.field_end_date.GetValue()
        if len(date.strip()) > 0:
            fields["EndDate"] = ui.datetimeutil.encode_date(date)

        date = self.field_destroy_date.GetValue()
        if len(date.strip()) > 0:
            fields["DestroyDate"] = ui.datetimeutil.encode_date(date)

        core_fields = {
            "Number": "Керн:%s" % fields["Number"],
            "Name": "Керн:%s" % fields["Name"],
            "X": fields["X"],
            "Y": fields["Y"],
            "Z": fields["Z"],
            "SampleType": "CORE",
            "StartSetDate": fields["StartDate"],
            "EndSetDate": fields["EndDate"],
        }

        if self._type == "CREATE":
            o = BoreHole(**fields)
            core_fields["bore_hole"] = o
            core_fields["mine_object"] = o.mine_object
            core = OrigSampleSet(**core_fields)
        else:
            o = BoreHole[self._target.RID]
            o.set(**fields)
            core = OrigSampleSet[self._target.RID]
            o.set(**core_fields)

        commit()
        self.o = core
        self.EndModal(wx.ID_OK)


class OrigSampleSetOtherDialog(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, sample_type="STUF"):
        super().__init__(parent)
        self.o = o
        self.sample_type = sample_type
        self.type = type
        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)

        super().__init__(parent, title="Добавить керн", size=wx.Size(300, 550))
        _type = "CREATE"
        self._type = _type
        self._target = o
        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)

        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Месторождение")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_field = wx.Choice(self)
        main_sz.Add(self.field_field, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self.fields = []
        for o in select(o for o in MineObject if o.Type == "FIELD"):
            self.fields.append(o)
            self.field_field.Append(o.Name)
        if len(self.fields) > 0:
            self.field_field.SetSelection(0)

        if _type == "CREATE":
            autofill_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Поля для автозаполнения")
            label = wx.StaticText(self, label="Числовой № набора")
            autofill_sizer.Add(label, 0)
            self.field_orig_no = wx.TextCtrl(self, size=wx.Size(250, -1))
            self.field_orig_no.Bind(wx.EVT_KEY_UP, self.on_orig_no_updated)
            autofill_sizer.Add(self.field_orig_no, 0, wx.EXPAND)
            main_sz.Add(autofill_sizer, 0, wx.EXPAND)

        label = wx.StaticText(
            self,
            label="Регистрационный номер " + ("(автом. из Числового №)*" if _type == "CREATE" else "*"),
        )
        main_sz.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sz.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(
            self,
            label="Название " + ("(автом. из Числового №)*" if _type == "CREATE" else "*"),
        )
        main_sz.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sz.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Комментарий")
        main_sz.Add(collpane, 0, wx.GROW)

        comment_pane = collpane.GetPane()
        comment_sizer = wx.BoxSizer(wx.VERTICAL)
        comment_pane.SetSizer(comment_sizer)

        label = wx.StaticText(comment_pane, label="Комментарий")
        comment_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(comment_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE)
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        comment_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Координаты")
        main_sz.Add(collpane, 0, wx.GROW)

        coords_pane = collpane.GetPane()
        coords_sizer = wx.BoxSizer(wx.VERTICAL)
        coords_pane.SetSizer(coords_sizer)

        cs_name = MineObject[self.fields[self.field_field.GetSelection()].RID].coord_system.Name
        self.coords_label = wx.StaticText(
            coords_pane,
            label="Система координат: " + (cs_name if len(cs_name) < 24 else cs_name[:24] + "..."),
        )
        coords_sizer.Add(self.coords_label, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.open_cs_transf = wx.Button(coords_pane, label="Открыть утилиту перевода координат")
        coords_sizer.Add(self.open_cs_transf, 0, wx.EXPAND)
        self.open_cs_transf.Bind(wx.EVT_BUTTON, self.on_open_cs_transf)

        label = wx.StaticText(coords_pane, label="X (м)")
        coords_sizer.Add(label, 0)
        self.field_x = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_x.SetDigits(2)
        coords_sizer.Add(self.field_x, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Y (м)")
        coords_sizer.Add(label, 0)
        self.field_y = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_y.SetDigits(2)
        coords_sizer.Add(self.field_y, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Z (м)")
        coords_sizer.Add(label, 0)
        self.field_z = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_z.SetDigits(2)
        coords_sizer.Add(self.field_z, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата начала отбора*")
        main_sz.Add(label, 0)
        self.field_start_date = wx.TextCtrl(self)
        self.field_start_date.SetValidator(DateValidator())

        main_sz.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения отбора")
        main_sz.Add(label, 0)
        self.field_end_date = wx.TextCtrl(self)
        self.field_end_date.SetValidator(DateValidator(allow_empty=True))
        main_sz.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sz.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Создать")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        sz.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)
        self.SetSizer(sz)
        self.Layout()

        self.field_field.Bind(wx.EVT_CHOICE, self.on_orig_no_updated)

    def on_open_cs_transf(self, event): ...

    @db_session
    def on_orig_no_updated(self, event):
        event.Skip()
        parent = MineObject[self.fields[self.field_field.GetSelection()].RID]
        cs_name = parent.coord_system.Name
        self.coords_label.SetLabel("Система координат: " + (cs_name if len(cs_name) < 24 else cs_name[:24] + "..."))
        name = str(self.field_orig_no.GetValue()) + " на"
        number = str(self.field_orig_no.GetValue())
        while parent.Level > 0:
            name += " " + parent.Name
            number += "@" + (parent.Name if len(parent.Name) < 4 else parent.Name[:4])
            parent = parent.parent

        if self.sample_type == "STUF":
            typname = "Штуф"
        else:
            typname = "Дисперс:"
        self.field_name.SetValue(typname + ":" + name)
        self.field_number.SetValue(typname + ":" + number)

    def on_save(self, event): ...
