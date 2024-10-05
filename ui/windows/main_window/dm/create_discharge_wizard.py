import wx
import wx.adv

from pony.orm import *
from database import OrigSampleSet

from ui.icon import get_icon


class Page0(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        super().__init__(parent)

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Дата начала измерений")
        main_sizer.Add(label, 0, wx.EXPAND | wx.BOTTOM, border=5)
        self.field_start_measure = wx.adv.DatePickerCtrl(self)
        main_sizer.Add(self.field_start_measure, 0, wx.EXPAND | wx.BOTTOM, border=20)

        self.checkbox_measure_ended = wx.CheckBox(self, label="Измерения завершены")
        self.checkbox_measure_ended.Bind(wx.EVT_CHECKBOX, self._on_check)
        main_sizer.Add(self.checkbox_measure_ended, 0, wx.EXPAND | wx.BOTTOM, border=5)

        label = wx.StaticText(self, label="Дата завершения измерений")
        main_sizer.Add(label, 0, wx.EXPAND | wx.BOTTOM, border=5)
        self.field_end_measure = wx.adv.DatePickerCtrl(self)
        main_sizer.Add(self.field_end_measure, 0, wx.EXPAND | wx.BOTTOM, border=5)
        self.field_end_measure.Disable()

        top_sizer.Add(main_sizer, 1, wx.EXPAND)
        self.SetSizer(top_sizer)

    def _on_check(self, event):
        self.field_end_measure.Enable(self.checkbox_measure_ended.IsChecked())


class Page1(wx.adv.WizardPageSimple):
    @db_session
    def __init__(self, parent: wx.adv.Wizard):
        super().__init__(parent)

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Выбрать набор образцов")
        top_sizer.Add(label, 0, wx.EXPAND | wx.BOTTOM, border=5)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = main_sizer
        top_sizer.Add(main_sizer, 1, wx.EXPAND)

        self._select_panel = wx.Panel(self)
        select_sizer = wx.BoxSizer(wx.VERTICAL)
        self._field_orig_sample_set = wx.Choice(self._select_panel)
        orig_sample_sets = select(o for o in OrigSampleSet if len(o.discharge_series) == 0)
        label = wx.StaticText(self._select_panel, label="Нет свободных наборов образцов.")
        label.SetForegroundColour(wx.Colour(255,44,44))
        label.Hide()
        if len(orig_sample_sets) == 0:
            label.Show()
        select_sizer.Add(label, 0, wx.EXPAND)
        for o in select(o for o in OrigSampleSet if len(o.discharge_series) == 0):
            self._field_orig_sample_set.Append(o.Name, o.RID)
        if len(orig_sample_sets) > 0:
            self._field_orig_sample_set.SetSelection(0)
        select_sizer.Add(self._field_orig_sample_set, 0, wx.EXPAND)
        self._select_panel.SetSizer(select_sizer)

        main_sizer.Add(self._select_panel, 0, wx.EXPAND | wx.BOTTOM, border=20)
        self.SetSizer(top_sizer)


class Page2(wx.adv.WizardPageSimple):
    def __init__(self, parent):
        super().__init__(parent)


@db_session
def run():
    wizard = wx.adv.Wizard(None, -1, "[Разгрузка] Мастер создания набора замеров")
    wizard.SetPageSize(wx.Size(350, 300))
    wizard.SetIcon(wx.Icon(get_icon("magic-wand")))
    wizard.CenterOnParent()
    page1 = Page0(wizard)
    page2 = Page1(wizard)
    page3 = Page2(wizard)

    wx.adv.WizardPageSimple.Chain(page1, page2)
    wx.adv.WizardPageSimple.Chain(page2, page3)
    wizard.Layout()

    wizard.RunWizard(page1)

    wizard.Destroy()
