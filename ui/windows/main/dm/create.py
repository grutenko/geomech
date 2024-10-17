import wx
import wx.adv

from pony.orm import *
from database import OrigSampleSet, FoundationDocument, DischargeSeries

from ui.icon import get_icon
from ui.validators import *
from ui.datetimeutil import decode_date, encode_date

WizPageChangingEvent, EVT_WIZ_PAGE_CHAGING = wx.lib.newevent.NewEvent()


class DialogCreateDischargeSeries(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить набор замеров", size=wx.Size(400, 600))
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

        label = wx.StaticText(self, label="Керн")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_core = wx.Choice(self, size=wx.Size(250, -1))
        main_sizer.Add(self.field_core, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self.field_core.Bind(wx.EVT_CHOICE, self._on_core_changed)
        if self._type != "CREATE":
            self.field_core.Disable()

        self._cores = []
        if _type == "CREATE":
            cores = select(o for o in OrigSampleSet if len(o.discharge_series) == 0).order_by(lambda x: desc(x.RID))
            for o in cores:
                self._cores.append(o)
                self.field_core.Append(o.Name)
            if len(cores) > 0:
                self.field_core.SetSelection(0)
        else:
            core = OrigSampleSet[self._target.orig_sample_set.RID]
            self._cores.append(core)
            self.field_core.Append(core.Name)
            self.field_core.SetSelection(0)

        self.SetSizer(top_sizer)

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

        label = wx.StaticText(self, label="Дата начала измерений*")
        main_sizer.Add(label, 0)
        self.field_start_date = wx.TextCtrl(self)
        self.field_start_date.SetValidator(DateValidator())
        self.field_start_date.Bind(wx.EVT_KEY_UP, self._on_measure_date_updated)

        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения")
        main_sizer.Add(label, 0)
        self.field_end_date = wx.TextCtrl(self)
        self.field_end_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

        label = wx.StaticText(
            self,
            label="Название " + ("(автом.)*" if _type == "CREATE" else "*"),
        )
        main_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

    @db_session
    def _set_auto_fields(self):
        o = self._cores[self.field_core.GetSelection()]
        date = self.field_start_date.GetValue()
        self.field_name.SetValue(date + " " + o.Name)

    def _on_measure_date_updated(self, event):
        self._set_auto_fields()

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        core = self._cores[self.field_core.GetSelection()]
        core = OrigSampleSet[core.RID]
        mine_object = core.mine_object

        fields = {
            "mine_object": mine_object,
            "orig_sample_set": core,
            "Name": self.field_name.GetValue(),
            "Comment": self.field_comment.GetValue(),
            "StartMeasure": encode_date(self.field_start_date.GetValue()),
        }

        if self.field_end_date.GetValue():
            fields["EndMeasure"] = encode_date(self.field_end_date.GetValue())

        if self.field_fd.GetSelection() > 0:
            fd = self._documents[self.field_fd.GetSelection() - 1]
            fd = FoundationDocument[fd.RID]
            fields["foundation_document"] = fd

        self.o = DischargeSeries(**fields)
        commit()
        self.EndModal(wx.ID_OK)

    def _on_core_changed(self, event):
        self._set_auto_fields()

    @db_session
    def _set_fields(self):
        o = self._target
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment)

        for index, core in enumerate(self._cores):
            if o.orig_sample_set.RID == core.RID:
                self.field_core.SetSelection(index)

        if o.foundation_document != None:
            for index, fd in enumerate(self._documents):
                if o.document.RID == fd.RID:
                    self.field_fd.SetSelection(index)

        date = decode_date(o.StartMeasure)
        self.field_start_date.SetValue("%s.%s.%s" % (str(date.day).zfill(2), str(date.month).zfill(2), str(date.year).zfill(4)))

        if o.EndMeasure != None:
            date = decode_date(o.EndMeasure)
            self.field_end_date.SetValue("%s.%s.%s" % (str(date.day).zfill(2), str(date.month).zfill(2), str(date.year).zfill(4)))
