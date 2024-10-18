import wx
import wx.adv
from pony.orm import *

from database import FoundationDocument, OrigSampleSet, PMTestSeries
from ui.icon import get_icon
from ui.validators import *

WizPageChangingEvent, EVT_WIZ_PAGE_CHAGING = wx.lib.newevent.NewEvent()


class DialogCreatePmSeries(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить набор испытаний", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()

        self._type = _type
        if _type == "CREATE":
            ...
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
        self.parent = None

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(top_sizer)

        label = wx.StaticText(
            self,
            label="Название",
        )
        main_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(
            self,
            label="Регистрационный номер",
        )
        main_sizer.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

        label = wx.StaticText(self, label="Документ")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_fd = wx.Choice(self, size=wx.Size(250, -1))
        self.field_fd.Append("[Не выбрано]")
        self.field_fd.SetSelection(0)
        main_sizer.Add(self.field_fd, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self._documents = []
        data = select(o for o in FoundationDocument).order_by(lambda x: desc(x.RID))
        for o in data:
            self.field_fd.Append(o.Name)
            self._documents.append(o)

        label = wx.StaticText(
            self,
            label="Место проведения",
        )
        main_sizer.Add(label, 0)
        self.field_location = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_location.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_location, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

    @db_session
    def _on_save(self, event):
        fields = {
            "Name": self.field_name.GetValue().strip(),
            "Number": self.field_number.GetValue().strip(),
            "Comment": self.field_comment.GetValue().strip(),
            "Location": self.field_location.GetValue().strip(),
        }

        if self.field_fd.GetSelection() > 0:
            fd = FoundationDocument[self._documents[self.field_fd.GetSelection() - 1].RID]
            fields["foundation_document"] = fd

        if self._type == "CREATE":
            o = PMTestSeries(**fields)
        else:
            ...

        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
