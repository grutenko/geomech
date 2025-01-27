import datetime

import wx
import wx.adv
from pony.orm import *
from wx.adv import DP_ALLOWNONE, DP_DEFAULT, DP_SHOWCENTURY, DatePickerCtrl

import ui.datetimeutil
from database import BoreHole, MineObject, Station
from ui.icon import get_icon
from ui.validators import *
from ui.windows.cs.transl import CsTransl


class DialogCreateBoreHole(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить Скважину", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self._type = _type
        if _type == "CREATE":
            self.parent = o
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
            self.parent = MineObject[o.mine_object.RID] if o.station == None else Station[o.station.RID]

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        if _type == "CREATE":
            autofill_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Поля для автозаполнения")
            label = wx.StaticText(self, label="Числовой № скважины")
            autofill_sizer.Add(label, 0)
            self.field_orig_no = wx.TextCtrl(self, size=wx.Size(250, -1))
            self.field_orig_no.Bind(wx.EVT_KEY_UP, self._on_orig_no_updated)
            autofill_sizer.Add(self.field_orig_no, 0, wx.EXPAND)
            main_sizer.Add(autofill_sizer, 0, wx.EXPAND)

        label = wx.StaticText(
            self,
            label="Регистрационный номер " + ("(автом. из Числового №)*" if _type == "CREATE" else "*"),
        )
        main_sizer.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(
            self,
            label="Название " + ("(автом. из Числового №)*" if _type == "CREATE" else "*"),
        )
        main_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Комментарий")
        main_sizer.Add(collpane, 0, wx.GROW)

        comment_pane = collpane.GetPane()
        comment_sizer = wx.BoxSizer(wx.VERTICAL)
        comment_pane.SetSizer(comment_sizer)

        label = wx.StaticText(comment_pane, label="Комментарий")
        comment_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(comment_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE)
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        comment_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата закладки скважины / начала измерений*")
        main_sizer.Add(label, 0)
        self.field_start_date = wx.TextCtrl(self)
        self.field_start_date.SetValidator(DateValidator())

        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения измерений")
        main_sizer.Add(label, 0)
        self.field_end_date = wx.TextCtrl(self)
        self.field_end_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата ликвидации скважины")
        main_sizer.Add(label, 0)
        self.field_destroy_date = wx.TextCtrl(self)
        self.field_destroy_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_destroy_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Координаты")
        main_sizer.Add(collpane, 0, wx.GROW)

        coords_pane = collpane.GetPane()
        coords_sizer = wx.BoxSizer(wx.VERTICAL)
        coords_pane.SetSizer(coords_sizer)

        if isinstance(self.parent, Station):
            station = Station[self.parent.RID]
            cs_name = station.mine_object.coord_system.Name
        else:
            cs_name = MineObject[self.parent.RID].coord_system.Name
        label = wx.StaticText(
            coords_pane,
            label="Система координат: " + (cs_name if len(cs_name) < 24 else cs_name[:24] + "..."),
        )
        coords_sizer.Add(label, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.open_cs_transf = wx.Button(coords_pane, label="Открыть утилиту перевода координат")
        coords_sizer.Add(self.open_cs_transf, 0, wx.EXPAND)
        self.open_cs_transf.Bind(wx.EVT_BUTTON, self._on_open_cs_transf)

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
        main_sizer.Add(collpane, 0, wx.GROW)

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

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == "CREATE":
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        if _type == "UPDATE":
            self._set_fields()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def _set_fields(self):
        o = self._target
        self.field_number.SetValue(o.Number)
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment if o.Comment != None else "")
        self.field_x.SetValue(o.X)
        self.field_y.SetValue(o.Y)
        self.field_z.SetValue(o.Z)
        self.field_start_date.SetValue(ui.datetimeutil.decode_date(o.StartDate).__str__())
        if o.EndDate != None:
            self.field_end_date.SetValue(ui.datetimeutil.decode_date(o.EndDate).__str__())
        if o.DestroyDate != None:
            self.field_destroy_date.SetValue(ui.datetimeutil.decode_date(o.DestroyDate).__str__())
        self.field_azimuth.SetValue(int(o.Azimuth))
        self.field_tilt.SetValue(int(o.Tilt))
        self.field_diameter.SetValue(int(o.Diameter * 1000))
        self.field_length.SetValue(o.Length)

    def _on_open_cs_transf(self, event):
        dlg = CsTransl(self)
        dlg.Show()
        dlg.CenterOnParent()

    @db_session
    def _on_orig_no_updated(self, event):
        event.Skip()
        if isinstance(self.parent, MineObject):
            parent = MineObject[self.parent.RID]
            name = str(self.field_orig_no.GetValue()) + " на"
            number = str(self.field_orig_no.GetValue())
        else:
            station = Station[self.parent.RID]
            parent = station.mine_object
            name = station.Number.split("@")[0] + "/" + str(self.field_orig_no.GetValue()) + " на"
            number = str(self.field_orig_no.GetValue()) + "@" + station.Number.split("@")[0]
        while parent.Level > 0:
            name += " " + parent.Name
            number += "@" + (parent.Name if len(parent.Name) < 4 else parent.Name[:4])
            parent = parent.parent

        self.field_name.SetValue(name)
        self.field_number.SetValue(number)

    @db_session
    def _create_object(self, fields):
        self.o = BoreHole(**fields)

    @db_session
    def _on_save(self, event):
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
            if isinstance(self.parent, MineObject):
                fields["mine_object"] = MineObject[self.parent.RID]
                fields["station"] = None
            else:
                station = Station[self.parent.RID]
                fields["mine_object"] = station.mine_object
                fields["station"] = station

        fields["StartDate"] = ui.datetimeutil.encode_date(self.field_start_date.GetValue())

        date = self.field_end_date.GetValue()
        if len(date.strip()) > 0:
            fields["EndDate"] = ui.datetimeutil.encode_date(date)

        date = self.field_destroy_date.GetValue()
        if len(date.strip()) > 0:
            fields["DestroyDate"] = ui.datetimeutil.encode_date(date)

        if self._type == "CREATE":
            o = BoreHole(**fields)
        else:
            o = BoreHole[self._target.RID]
            o.set(**fields)

        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
