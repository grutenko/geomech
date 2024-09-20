import wx
from wx.adv import DatePickerCtrl, DP_ALLOWNONE, DP_DEFAULT, DP_SHOWCENTURY
from pony.orm import *

from database import *
from ui.validators import *


class CreateDischargeSeries(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(
            parent, title="Добавить [Разгрузка] Набор замеров", size=wx.Size(400, 600)
        )
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))

        self._type = _type
        if _type == "CREATE":
            self.parent = o
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
            self.parent = OrigSampleSet[o.orig_sample_set.RID]

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

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

        label = wx.StaticText(self, label="Дата начала измерений*")
        main_sizer.Add(label, 0)
        self.field_start_date = DatePickerCtrl(self)
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения измерений")
        main_sizer.Add(label, 0)
        self.field_end_date = DatePickerCtrl(
            self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE
        )
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Документ обоснование")
        main_sizer.Add(label, 0)
        self.field_document = wx.Choice(self)
        self.field_document.Append("-- Без документа --")
        self.field_document.SetSelection(0)

        self._documents = []
        for o in select(o for o in FoundationDocument):
            self.field_document.Append(o.Name)
            self._documents.append(o)

        main_sizer.Add(self.field_document, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == "CREATE":
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        if _type == "UPDATE":
            self._set_fields()
        else:
            self._apply_fields()

    def _set_fields(self): ...

    def _apply_fields(self):
        date = self.field_start_date.GetValue()
        self.field_name.SetValue(
            (
                "%s.%s.%s"
                % (
                    str(date.GetDay()).zfill(2),
                    str(date.GetMonth() + 1).zfill(2),
                    str(date.GetYear()),
                )
            )
            + " "
            + self.parent.Name
        )

    def _on_save(self, event): ...
