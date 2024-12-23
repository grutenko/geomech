import wx
from pony.orm import *

from database import FoundationDocument
from ui.icon import get_icon
from ui.validators import *
from ui.widgets.supplied_data.widget import SuppliedDataWidget
from ui.widgets.supplied_data.widget_for_new_owner import SuppliedDataWidgetForNewOwner


class CreateDocumentDialog(wx.Dialog):
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить Документ", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.SetSize(wx.Size(550, 450))

        if _type == "CREATE":
            self.parent = o
        else:
            self._target = o
            self.SetTitle("Документ: %s" % self._target.Name)
        self._type = _type

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 0, wx.EXPAND | wx.ALL, border=10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Тип документа*")
        sizer.Add(label, 0)
        self.field_type = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_type.SetValidator(TextValidator(lenMin=1, lenMax=256))
        sizer.Add(self.field_type, 0, wx.EXPAND)
        left_sizer.Add(sizer, 0, wx.EXPAND | wx.BOTTOM, border=5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Номер документа")
        sizer.Add(label, 0)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=0, lenMax=32))
        sizer.Add(self.field_number, 0, wx.EXPAND)
        left_sizer.Add(sizer, 0, wx.EXPAND)

        main_sizer.Add(left_sizer, 1, wx.EXPAND)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Комментарий")
        sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(self, size=wx.Size(250, 100), style=wx.TE_MULTILINE)
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        sizer.Add(self.field_comment, 1, wx.EXPAND)
        right_sizer.Add(sizer, 1, wx.EXPAND | wx.LEFT, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == "CREATE":
            label = "Cоздать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        top_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=5)

        main_sizer.Add(right_sizer, 1, wx.EXPAND)

        if _type == "CREATE":
            self._supplied_data = SuppliedDataWidgetForNewOwner(self, "FOUNDATION_DOC")
        else:
            self._supplied_data = SuppliedDataWidget(self)
            self._supplied_data.hide_target_name()
            self._supplied_data.start(self._target, "FOUNDATION_DOC")
        top_sizer.Add(self._supplied_data, 1, wx.EXPAND)

        self.SetSizer(top_sizer)
        self.Layout()

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        fields = {
            "Number": self.field_number.GetValue().strip(),
            "Type": self.field_type.GetValue(),
            "Comment": self.field_comment.GetValue(),
        }

        if self._type == "CREATE":
            o = FoundationDocument(**fields)
        else:
            o = FoundationDocument[self._target.RID]
            o.set(**fields)

        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
