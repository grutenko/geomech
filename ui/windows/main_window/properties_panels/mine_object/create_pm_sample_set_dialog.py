import wx
from wx.adv import DatePickerCtrl, DP_DEFAULT, DP_SHOWCENTURY, DP_ALLOWNONE

from pony.orm import *

from database import PMTestSeries
from ui.icon import get_icon
from ui.validators import *


class CreatePmSampleSetDialog(wx.Dialog):
    @db_session
    def __init__(self, parent, o):
        super().__init__(parent, title="Добавить Пробу", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon(get_icon("logo@16")))

        self.parent = o

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        autofill_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Поля для автозаполнения")
        label = wx.StaticText(self, label="Номер или наименование пробы")
        autofill_sizer.Add(label, 0)
        self.field_orig_no = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_orig_no.Bind(wx.EVT_KEY_UP, self._on_orig_no_updated)
        autofill_sizer.Add(self.field_orig_no, 0, wx.EXPAND)
        main_sizer.Add(autofill_sizer, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Набор испытаний*")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_test_series = wx.Choice(self)
        self._test_series = []
        for o in select(o for o in PMTestSeries):
            self._test_series.append(o)
            self.field_test_series.Append('[' + o.foundation_document.Name + ']' + o.Name)
        main_sizer.Add(self.field_test_series, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Регистрационный номер*")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Название*")
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

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Описание трещин")
        main_sizer.Add(collpane, 0, wx.GROW | wx.BOTTOM, border=10)

        crack_pane = collpane.GetPane()
        crack_sizer = wx.BoxSizer(wx.VERTICAL)
        crack_pane.SetSizer(crack_sizer)

        label = wx.StaticText(crack_pane, label="Описание трещин")
        crack_sizer.Add(label, 0)
        self.field_crack = wx.TextCtrl(
            crack_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE
        )
        self.field_crack.SetValidator(TextValidator(lenMin=0, lenMax=512))
        crack_sizer.Add(self.field_crack, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата отбора пробы*")
        main_sizer.Add(label, 0)
        self.field_start_date = DatePickerCtrl(
            self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE
        )
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата испытания пробы")
        main_sizer.Add(label, 0)
        self.field_end_date = DatePickerCtrl(
            self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE
        )
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

    def _on_orig_no_updated(self, event): ...

    def _on_save(self, event): ...
