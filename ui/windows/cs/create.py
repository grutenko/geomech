import wx
import re

from pony.orm import *

from database import CoordSystem
from ui.validators import *
from ui.windows.cs.matrix import CreateTransfMatrixWindow
from ui.icon import get_icon


class _Mat3_Validator(wx.Validator): ...


class _Vec3_Validator(wx.Validator): ...


class CreateCoordSystemDialog(wx.Dialog):
    def __init__(self, parent, o=None, type="CREATE"):
        super().__init__(parent, title="Добавить Систему координат")
        self.SetIcon(wx.Icon(get_icon("logo@16")))

        if type == "CREATE":
            self.parent = o
        else:
            self._target = o
            self.SetTitle("Система координат: %s" % self._target.Name)
        self._type = type

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Название")
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

        label = wx.StaticText(self, label="Минимальные координаты")
        main_sizer.Add(label, 0, wx.EXPAND)

        _sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.field_vec_min = wx.TextCtrl(self, size=wx.Size(250, -1), value="0.0; 0.0; 0.0")
        self.field_vec_min.SetValidator(_Vec3_Validator())
        _sizer.Add(self.field_vec_min, 1, wx.EXPAND)
        q = wx.StaticText(self, label="[?]")
        tooltip = wx.ToolTip("Три числа - координаты X, Y, Z, разделенные точкой с запятой.")
        q.SetToolTip(tooltip)
        _sizer.Add(q, 0, wx.CENTER | wx.LEFT, border=5)
        main_sizer.Add(_sizer, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Максимальные координаты")
        main_sizer.Add(label, 0)
        _sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.field_vec_max = wx.TextCtrl(self, size=wx.Size(250, -1), value="0.0; 0.0; 0.0")
        self.field_vec_max.SetValidator(_Vec3_Validator())
        _sizer.Add(self.field_vec_max, 1, wx.EXPAND)
        q = wx.StaticText(self, label="[?]")
        tooltip = wx.ToolTip("Три числа - координаты X, Y, Z, разделенные точкой с запятой.")
        q.SetToolTip(tooltip)
        _sizer.Add(q, 0, wx.CENTER | wx.LEFT, border=5)
        main_sizer.Add(_sizer, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.btn_open_mat_util = wx.Button(self, label="Открыть утилиту нахождения матрицы")
        self.btn_open_mat_util.Bind(wx.EVT_BUTTON, self._on_open_mat_util)
        main_sizer.Add(self.btn_open_mat_util, 0, wx.EXPAND)

        label = wx.StaticText(self, label="Положение начала в родительской системе")
        main_sizer.Add(label, 0)
        _sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.field_base = wx.TextCtrl(self, size=wx.Size(250, -1), value="0.0; 0.0; 0.0")
        self.field_base.SetValidator(_Vec3_Validator())
        _sizer.Add(self.field_base, 1, wx.EXPAND)
        q = wx.StaticText(self, label="[?]")
        tooltip = wx.ToolTip("Три числа - координаты X, Y, Z, разделенные точкой с запятой.")
        q.SetToolTip(tooltip)
        _sizer.Add(q, 0, wx.CENTER | wx.LEFT, border=5)
        main_sizer.Add(_sizer, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Матрица перевода в родительскую систему")
        main_sizer.Add(label, 0)
        _sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.field_mat = wx.TextCtrl(
            self,
            size=wx.Size(250, 60),
            style=wx.TE_MULTILINE,
            value="1.0; 0.0; 0.0\n0.0; 1.0; 0.0\n0.0; 0.0; 1.0",
        )
        self.field_mat.SetValidator(_Mat3_Validator())
        _sizer.Add(self.field_mat, 1, wx.EXPAND)
        q = wx.StaticText(self, label="[?]")
        tooltip = wx.ToolTip("Матрица 3x3 числа в строке разделенные точкой с запятой")
        q.SetToolTip(tooltip)
        _sizer.Add(q, 0, wx.CENTER | wx.LEFT, border=5)
        main_sizer.Add(_sizer, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if type == "CREATE":
            label = "Cоздать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)
        self.Layout()
        self.Fit()

        if type == "UPDATE":
            self._set_fields()

    def _on_open_mat_util(self, event):
        w = CreateTransfMatrixWindow(self)
        w.Show()

    def _set_fields(self):
        o = self._target
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment if o.Comment != None else "")
        self.field_base.SetValue("%f; %f; %f" % (o.X_0, o.Y_0, o.Z_0))
        self.field_vec_min.SetValue("%f; %f; %f" % (o.X_Min, o.Y_Min, o.Z_Min))
        self.field_vec_max.SetValue("%f; %f; %f" % (o.X_Max, o.Y_Max, o.Z_Max))
        self.field_mat.SetValue("%f; %f; %f\n%f; %f; %f\n%f; %f; %f" % (o.X_X, o.X_Y, o.X_Z, o.Y_X, o.Y_Y, o.Y_Z, o.Z_X, o.Z_Y, o.Z_Z))

    def _set_coords(self, fields):
        _min = re.split(r"\s*;\s*", self.field_vec_min.GetValue())
        fields["X_Min"] = float(_min[0])
        fields["Y_Min"] = float(_min[1])
        fields["Z_Min"] = float(_min[2])
        _max = re.split(r"\s*;\s*", self.field_vec_max.GetValue())
        fields["X_Max"] = float(_max[0])
        fields["Y_Max"] = float(_max[1])
        fields["Z_Max"] = float(_max[2])
        _zero = re.split(r"\s*;\s*", self.field_base.GetValue())
        fields["X_0"] = float(_zero[0])
        fields["Y_0"] = float(_zero[1])
        fields["Z_0"] = float(_zero[2])
        _mat = re.split(r"\s*\n\s*", self.field_mat.GetValue())
        _mat0 = re.split(r"\s*;\s*", _mat[0])
        fields["X_X"] = float(_mat0[0])
        fields["X_Y"] = float(_mat0[1])
        fields["X_Z"] = float(_mat0[2])
        _mat1 = re.split(r"\s*;\s*", _mat[1])
        fields["Y_X"] = float(_mat1[0])
        fields["Y_Y"] = float(_mat1[1])
        fields["Y_Z"] = float(_mat1[2])
        _mat2 = re.split(r"\s*;\s*", _mat[2])
        fields["Z_X"] = float(_mat2[0])
        fields["Z_Y"] = float(_mat2[1])
        fields["Z_Z"] = float(_mat2[2])
        return fields

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        if self._type == "CREATE":
            fields = {
                "parent": CoordSystem[self.parent.RID],
                "Level": self.parent.Level + 1,
                "HCode": str(self.parent.RID).zfill(8) + "." + str(self.parent.RID).zfill(19),
                "Name": self.field_name.GetValue(),
                "Comment": self.field_comment.GetValue(),
            }
            fields = self._set_coords(fields)

            try:
                self.o = CoordSystem(**fields)
            except Exception as e:
                wx.MessageBox(str(e))
            else:
                self.EndModal(wx.ID_OK)
        else:
            fields = {
                "Name": self.field_name.GetValue(),
                "Comment": self.field_comment.GetValue(),
            }
            fields = self._set_coords(fields)
            try:
                self.o = CoordSystem[self._target.RID]
                self.o.set(**fields)
            except Exception as e:
                wx.MessageBox(str(e))
            else:
                self.EndModal(wx.ID_OK)
