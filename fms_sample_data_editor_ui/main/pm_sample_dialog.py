import wx

from ui.icon import get_icon
from ui.validators import TextValidator
from pony.orm import db_session, select, commit, desc
from database import OrigSampleSet, PMSample, PMSampleSet
from ui.validators import DateValidator, ChoiceValidator
from ui.custom_datetime import date
from ui.datetimeutil import encode_date


class PmSampleDialog(wx.Dialog):
    @db_session
    def __init__(self, parent, pm_sample_set=None, o=None):
        super().__init__(parent, title="Добавить образец", size=wx.Size(300, 550))
        self.SetIcon(wx.Icon(get_icon("logo")))
        self.CenterOnScreen()
        self.pm_sample_set = pm_sample_set

        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Номер *")
        main_sz.Add(label, 0)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=256))
        max_pm_sample_number = select(o for o in PMSample if o.pm_sample_set == pm_sample_set).order_by(lambda x: desc(x.Number)).first()
        number = "1"
        if max_pm_sample_number is not None:
            try:
                number = str(int(max_pm_sample_number.Number) + 1)
            except:
                ...
        self.field_number.SetValue(number)
        main_sz.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата отбора")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_set_date = wx.TextCtrl(self)
        self.field_set_date.SetValidator(DateValidator())
        self.field_set_date.SetValue(date.today().__str__())
        main_sz.Add(self.field_set_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Набор образцов *")
        main_sz.Add(label, 0, wx.EXPAND)
        self.orig_sample_sets = []
        self.field_orig_sample_set = wx.Choice(self)
        self.field_orig_sample_set.SetValidator(ChoiceValidator())
        self.field_orig_sample_set.Bind(wx.EVT_CHOICE, self.on_orig_sample_set_updated)
        for o in select(o for o in OrigSampleSet if o.mine_object == pm_sample_set.mine_object):
            if o.bore_hole is None or o.bore_hole.station is None:
                self.orig_sample_sets.append(o)
                self.field_orig_sample_set.Append(o.Name)
        if len(self.orig_sample_sets) > 0:
            self.field_orig_sample_set.SetSelection(0)
        main_sz.Add(self.field_orig_sample_set, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.core_sz = wx.StaticBoxSizer(wx.VERTICAL, self, label="Параметры керна")
        local_sz = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Начальная позиция керна")
        local_sz.Add(label, 0, wx.EXPAND)
        self.field_start_position = wx.SpinCtrlDouble(self, min=0, max=10000)
        self.field_start_position.SetDigits(2)
        local_sz.Add(self.field_start_position, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Конечная позиция керна")
        local_sz.Add(label, 0, wx.EXPAND)
        self.field_end_position = wx.SpinCtrlDouble(self, min=0, max=10000)
        self.field_end_position.SetDigits(2)
        local_sz.Add(self.field_end_position, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="№ ящика")
        local_sz.Add(label, 0, wx.EXPAND)
        self.field_box_number = wx.TextCtrl(self)
        self.field_box_number.SetValidator(TextValidator(lenMin=0, lenMax=32))
        local_sz.Add(self.field_box_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.core_sz.Add(local_sz, 1, wx.EXPAND | wx.ALL, border=10)
        main_sz.Add(self.core_sz, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.other_sz = wx.StaticBoxSizer(wx.VERTICAL, self, label="Параметры образца")
        local_sz = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Глубина отбора")
        local_sz.Add(label, 0, wx.EXPAND)
        self.field_sample_depth = wx.SpinCtrlDouble(self, min=0, max=10000)
        self.field_sample_depth.SetDigits(2)
        local_sz.Add(self.field_sample_depth, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self.other_sz.Add(local_sz, 1, wx.EXPAND | wx.ALL, border=10)
        main_sz.Add(self.other_sz, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.core_sz.Hide(0)
        self.other_sz.Hide(0)

        label = wx.StaticText(self, label="Дата завершения испытаний")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_end_set_date = wx.TextCtrl(self)
        self.field_end_set_date.SetValidator(DateValidator(allow_empty=True))
        main_sz.Add(self.field_end_set_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)

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
        self.on_orig_sample_set_updated()

    def on_orig_sample_set_updated(self, event=None):
        if len(self.orig_sample_sets) > 0:
            if self.orig_sample_sets[self.field_orig_sample_set.GetSelection()].SampleType == "CORE":
                self.use_core()
            else:
                self.use_other()

    def use_core(self):
        self.other_sz.Hide(0)
        self.core_sz.Show(0)
        self.Layout()

    def use_other(self):
        self.other_sz.Show(0)
        self.core_sz.Hide(0)
        self.Layout()

    @db_session
    def on_save(self, event):
        if not self.Validate():
            return

        orig_sample_set = self.orig_sample_sets[self.field_orig_sample_set.GetSelection()]
        fields = {}
        fields["Number"] = self.field_number.GetValue()
        fields["SetDate"] = encode_date(self.field_set_date.GetValue())
        fields["orig_sample_set"] = OrigSampleSet[orig_sample_set.RID]
        fields["pm_sample_set"] = PMSampleSet[self.pm_sample_set.RID]
        if orig_sample_set.SampleType == "CORE":
            fields["StartPosition"] = self.field_start_position.GetValue()
            fields["EndPosition"] = self.field_end_position.GetValue()
            fields["BoxNumber"] = self.field_box_number.GetValue()
        else:
            fields["StartPosition"] = self.field_sample_depth.GetValue()
        date = self.field_end_set_date.GetValue()
        if len(date.strip()) > 0:
            fields["EndTestDate"] = encode_date(date)

        o = PMSample(**fields)
        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
