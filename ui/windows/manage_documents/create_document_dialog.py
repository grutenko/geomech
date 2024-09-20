import wx

from pony.orm import *

from database import FoundationDocument
from ui.validators import *

class CreateDocumentDialog(wx.Dialog):
    def __init__(self, parent, o=None, type="CREATE"):
        super().__init__(parent, title="Добавить Документ")
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))

        if type == "CREATE":
            self.parent = o
        else:
            self._target = o
            self.SetTitle("Документ: %s" % self._target.Name)
        self._type = type

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Название*")
        main_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Тип документа*")
        main_sizer.Add(label, 0)
        self.field_type = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_type.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_type, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

        label = wx.StaticText(self, label="Номер документа")
        main_sizer.Add(label, 0)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=0, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if type == 'CREATE':
            label = 'Cоздать'
        else:
            label = 'Изменить'
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)
        self.Layout()
        self.Fit()

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return
        
        fields = {
            "Name": self.field_name.GetValue(),
            "Type": self.field_type.GetValue(),
            "Comment": self.field_comment.GetValue(),
            "Number": self.field_number.GetValue()
        }

        if self._type == 'CREATE':
            try:
                self.o = FoundationDocument(**fields)
            except Exception as e:
                wx.MessageBox(str(e))
            else:
                self.EndModal(wx.ID_OK)
        else:
            try:
                self.o = FoundationDocument[self._target.RID]
                self.o.set(**fields)
            except Exception as e:
                wx.MessageBox(str(e))
            else:
                self.EndModal(wx.ID_OK)