import wx

from wx.adv import DatePickerCtrl, DP_ALLOWNONE, DP_DEFAULT, DP_SHOWCENTURY

import datetime

from pony.orm import *
import wx.adv
from database import Station, MineObject, BoreHole
import ui.datetimeutil

from ui.validators import *
from ui.windows.switch_coord_system.frame import CsTransl

class DialogCreateBoreHole(wx.Dialog):
    @db_session
    def __init__(self, parent, o = None):
        super().__init__(parent, title="Добавить Скважину", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))

        self.parent = o

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        autofill_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Поля для автозаполнения")
        label = wx.StaticText(self, label="Числовой № скважины")
        autofill_sizer.Add(label, 0)
        self.field_orig_no = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_orig_no.Bind(wx.EVT_KEY_UP, self._on_orig_no_updated)
        autofill_sizer.Add(self.field_orig_no, 0, wx.EXPAND)
        main_sizer.Add(autofill_sizer, 0, wx.EXPAND)

        label = wx.StaticText(
            self, label="Регистрационный номер (автом. из Числового №)*"
        )
        main_sizer.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Название (автом. из Числового №)*")
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
        self.field_comment = wx.TextCtrl(
            comment_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE
        )
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        comment_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата закладки скважины / начала измерений*")
        main_sizer.Add(label, 0)
        self.field_start_date = DatePickerCtrl(self)
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения измерений")
        main_sizer.Add(label, 0)
        self.field_end_date = DatePickerCtrl(
            self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE
        )
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата ликвидации скважины")
        main_sizer.Add(label, 0)
        self.field_destroy_date = DatePickerCtrl(
            self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE
        )
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
        label = wx.StaticText(coords_pane, label="Система координат: " + (cs_name if len(cs_name) < 24 else cs_name[:24] + '...'))
        coords_sizer.Add(label, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.open_cs_transf = wx.Button(
            coords_pane, label="Открыть утилиту перевода координат"
        )
        coords_sizer.Add(self.open_cs_transf, 0, wx.EXPAND)
        self.open_cs_transf.Bind(wx.EVT_BUTTON, self._on_open_cs_transf)

        label = wx.StaticText(coords_pane, label="X")
        coords_sizer.Add(label, 0)
        self.field_x = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_x.SetDigits(2)
        coords_sizer.Add(self.field_x, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Y")
        coords_sizer.Add(label, 0)
        self.field_y = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_y.SetDigits(2)
        coords_sizer.Add(self.field_y, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Z")
        coords_sizer.Add(label, 0)
        self.field_z = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_z.SetDigits(2)
        coords_sizer.Add(self.field_z, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Параметры")
        main_sizer.Add(collpane, 0, wx.GROW)

        props_pane = collpane.GetPane()
        props_sizer = wx.BoxSizer(wx.VERTICAL)
        props_pane.SetSizer(props_sizer)

        label = wx.StaticText(props_pane, label="Азимут")
        props_sizer.Add(label, 0)
        self.field_azimuth = wx.SpinCtrlDouble(props_pane, min=-100000000.0, max=10000000000.0)
        self.field_azimuth.SetDigits(2)
        props_sizer.Add(self.field_azimuth, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(props_pane, label="Наклон")
        props_sizer.Add(label, 0)
        self.field_tilt = wx.SpinCtrlDouble(props_pane, min=-100000000.0, max=10000000000.0)
        self.field_tilt.SetDigits(2)
        props_sizer.Add(self.field_tilt, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(props_pane, label="Диаметр")
        props_sizer.Add(label, 0)
        self.field_diameter = wx.SpinCtrlDouble(props_pane, min=-100000000.0, max=10000000000.0)
        self.field_diameter.SetDigits(2)
        props_sizer.Add(self.field_diameter, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(props_pane, label="Длина")
        props_sizer.Add(label, 0)
        self.field_length = wx.SpinCtrlDouble(props_pane, min=-100000000.0, max=10000000000.0)
        self.field_length.SetDigits(2)
        props_sizer.Add(self.field_length, 0, wx.EXPAND | wx.BOTTOM, border=10)

        
        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Создать")
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

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
            name = station.Number.split('@')[0] + '/' + str(self.field_orig_no.GetValue()) + ' на'
            number = str(self.field_orig_no.GetValue()) + '@' + station.Number.split('@')[0]
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
            "Azimuth": self.field_azimuth.GetValue(),
            "Tilt": self.field_tilt.GetValue(),
            "Diameter": self.field_diameter.GetValue(),
            "Length": self.field_length.GetValue(),
        }

        if isinstance(self.parent, MineObject):
            fields['mine_object'] = MineObject[self.parent.RID]
            fields['station'] = None
        else:
            station = Station[self.parent.RID]
            fields['mine_object'] = station.mine_object
            fields['station'] = station

        fields["StartDate"] = ui.datetimeutil.encode_date(
            self.field_start_date.GetValue()
        )

        date: wx.DateTime = self.field_end_date.GetValue()
        if date.IsValid():
            fields["EndDate"] = ui.datetimeutil.encode_date(date)

        date: wx.DateTime = self.field_destroy_date.GetValue()
        if date.IsValid():
            fields["DestroyDate"] = ui.datetimeutil.encode_date(date)

        try:
            self.o = BoreHole(**fields)
        except Exception as e:
            wx.MessageBox(str(e))
        else:
            self.EndModal(wx.ID_OK)