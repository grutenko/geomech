import wx

from pony.orm import *
from database import MineObject, CoordSystem

from ui.validators import *
from ui.windows.switch_coord_system.frame import CsTransl
from ui.ctrl.coord_system_ctrl import CoordSystemCtrl

class DialogCreateMineObject(wx.Dialog):
    @db_session
    def __init__(self, parent, o = None, _type = 'CREATE'):
        super().__init__(parent, title="Добавить горный объект")
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))
        self._type = _type
        if _type == 'CREATE':
            self.parent = o
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
            self.parent = MineObject[o.parent.RID] if o.parent != None else None

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border = 10)

        label = wx.StaticText(self, label="Система координат")
        main_sizer.Add(label, 0)
        self.field_coord_system = CoordSystemCtrl(self)
        main_sizer.Add(self.field_coord_system, 0, wx.EXPAND | wx.BOTTOM, border=10)

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
        self.field_comment = wx.TextCtrl(
            comment_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE
        )
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        comment_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Ограничения координат")
        main_sizer.Add(collpane, 0, wx.GROW)

        colpane_pane = collpane.GetPane()
        colpane_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.open_cs_transf = wx.Button(colpane_pane, label="Открыть утилиту перевода координат")
        colpane_sizer.Add(self.open_cs_transf, 0, wx.BOTTOM, border=10)
        self.open_cs_transf.Bind(wx.EVT_BUTTON, self._on_open_cs_transf)

        table_sizer = wx.FlexGridSizer(4, 4, 5, 5)
        colpane_sizer.Add(table_sizer, 1, wx.EXPAND)
        colpane_pane.SetSizer(colpane_sizer)

        label = wx.StaticText(colpane_pane, label="")
        table_sizer.Add(label, 0)
        label = wx.StaticText(colpane_pane, label="X (м)")
        table_sizer.Add(label, 0)
        label = wx.StaticText(colpane_pane, label="Y (м)")
        table_sizer.Add(label, 0)
        label = wx.StaticText(colpane_pane, label="Z (м)")
        table_sizer.Add(label, 0)

        label = wx.StaticText(colpane_pane, label="Мин.")
        table_sizer.Add(label, 0)

        self.field_x_min = wx.SpinCtrlDouble(colpane_pane, min=-100000000.0, max=10000000000.0)
        self.field_x_min.SetDigits(2)
        table_sizer.Add(self.field_x_min, 0)
        self.field_y_min = wx.SpinCtrlDouble(colpane_pane, min=-100000000.0, max=10000000000.0)
        self.field_y_min.SetDigits(2)
        table_sizer.Add(self.field_y_min, 0)
        self.field_z_min = wx.SpinCtrlDouble(colpane_pane, min=-100000000.0, max=10000000000.0)
        self.field_z_min.SetDigits(2)
        table_sizer.Add(self.field_z_min, 0)

        label = wx.StaticText(colpane_pane, label="Макс.")
        table_sizer.Add(label, 0)

        self.field_x_max = wx.SpinCtrlDouble(colpane_pane, min=-100000000.0, max=10000000000.0)
        self.field_x_max.SetDigits(2)
        table_sizer.Add(self.field_x_max, 0)
        self.field_y_max = wx.SpinCtrlDouble(colpane_pane, min=-100000000.0, max=10000000000.0)
        self.field_y_max.SetDigits(2)
        table_sizer.Add(self.field_y_max, 0)
        self.field_z_max = wx.SpinCtrlDouble(colpane_pane, min=-100000000.0, max=10000000000.0)
        self.field_z_max.SetDigits(2)
        table_sizer.Add(self.field_z_max, 0)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == 'CREATE':
            label = 'Создать'
        else:
            label = 'Изменить'
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        if _type == 'UPDATE':
            self._set_fields()

    @db_session
    def _set_fields(self):
        o = self._target
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment)
        self.field_coord_system.SetValue(CoordSystem[o.coord_system.RID])
        self.field_x_min.SetValue(o.X_Min)
        self.field_y_min.SetValue(o.Y_Min)
        self.field_z_min.SetValue(o.Z_Min)
        self.field_x_max.SetValue(o.X_Max)
        self.field_y_max.SetValue(o.Y_Max)
        self.field_z_max.SetValue(o.Z_Max)

    def _on_open_cs_transf(self, event):
        dlg = CsTransl(self)
        dlg.Show()
        dlg.CenterOnParent()

    @db_session
    def _create_object(self, fields):
        fields['coord_system'] = select(o for o in CoordSystem if o.RID == fields['coord_system'].RID).first()
        if 'parent' in fields:
            fields['parent'] = select(o for o in MineObject if o.RID == fields['parent'].RID).first()
        self.o = MineObject(**fields)

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return
        
        fields = {}

        if self._target == 'CREATE':
            if self.parent != None:
                m = {
                    "REGION": "Регион",
                    "ROCKS": "Горный массив",
                    "FIELD": "Месторождение",
                    "HORIZON": "Горизонт",
                    "EXCAVATION": "Выработка",
                }
                child_mine_object_type = list(m.keys()).__getitem__(
                    list(m.keys()).index(self.parent.Type) + 1
                )
                fields['parent'] = self.parent
                fields['Type'] = child_mine_object_type
                fields['Level'] = self.parent.Level + 1
                fields['HCode'] = str(self.parent.RID).zfill(8) + '.' + str(self.parent.RID).zfill(19)
            else:
                fields['Type'] = 'REGION'
                fields['Level'] = 0
                fields['HCode'] = ('0' * 12) + '.' + ('0' * 19)
        fields['Name'] = self.field_name.GetValue()
        fields['Comment'] = self.field_comment.GetValue()
        fields['coord_system'] = CoordSystem[self.field_coord_system.GetValue().RID]
        fields['X_Min'] = self.field_x_min.GetValue()
        fields['Y_Min'] = self.field_y_min.GetValue()
        fields['Z_Min'] = self.field_z_min.GetValue()
        fields['X_Max'] = self.field_x_max.GetValue()
        fields['Y_Max'] = self.field_y_max.GetValue()
        fields['Z_Max'] = self.field_z_max.GetValue()

        try:
            if self._type == 'CREATE':
                self._create_object(fields)
            else:
                self.o = MineObject[self._target.RID]
                self.o.set(**fields)
        except Exception as e:
            wx.MessageBox(str(e))
        else:
            self.EndModal(wx.ID_OK)