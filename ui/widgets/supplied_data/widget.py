import wx
import wx.dataview
import os

from pony.orm import *
import wx.dataview
from database import *

from ui.icon import get_art, get_icon
from ui.resourcelocation import resource_path
from ui.validators import *

class FolderEditor(wx.Dialog):
    def __init__(self, parent, o = None):
        super().__init__(parent)

        if o == None:
            self.SetTitle("Добавить раздел")
        else:
            self.SetTitle("Изменить раздел: %s" % o.Name)

        self.SetIcon(wx.Icon(get_icon("folder-add")))

        self.o = o

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Название *")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=128))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Номер")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=0, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Датировка материала")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_data_date = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_data_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_data_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

        line = wx.StaticLine(self)
        top_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if o == None:
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        top_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)

    def _apply_fields(self):
        ...

    def _on_save(self, event):
        if not self.Validate():
            return

class FileEditor(wx.Dialog):
    def __init__(self, parent, p = None, o = None):
        super().__init__(parent)
        self.CenterOnParent()
        self.SetTitle("Добавить файл")
        self.SetIcon(wx.Icon(get_icon("file-add")))

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

        btn_sizer = wx.StdDialogButtonSizer()
        if o != None:
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

    def _on_save(self, event):
        if not self.Validate():
            return

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)


class SuppliedDataWidget(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить раздел", get_icon("folder-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_create_folder, item)
        item = self.toolbar.AddTool(wx.ID_FILE, "Добавить файл", get_icon("file-add"))
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddTool(wx.ID_DOWN, "Скачать", get_icon("download"), kind=wx.ITEM_DROPDOWN)
        self.toolbar.EnableTool(wx.ID_FILE, False)
        self.toolbar.Realize()
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.statusbar = wx.StatusBar(self, style=0)
        main_sizer.Add(self.statusbar, 0, wx.EXPAND)

        self._deputy = wx.Panel(self)
        deputy_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(
            self._deputy,
            label="Недоступны для этого объекта",
            style=wx.ST_ELLIPSIZE_MIDDLE,
        )
        deputy_sizer.Add(label, 1, wx.CENTER | wx.ALL, border=20)
        self._deputy.SetSizer(deputy_sizer)
        main_sizer.Add(self._deputy, 1, wx.EXPAND)

        self._image_list = wx.ImageList(16, 16)
        self._icons = {}
        self.list = wx.dataview.TreeListCtrl(self, style=wx.dataview.TL_DEFAULT_STYLE | wx.BORDER_NONE | wx.dataview.TL_3STATE)
        self.list.AssignImageList(self._image_list)
        self._icon_folder = self._image_list.Add(get_icon("folder"))
        self._icon_folder_open = self._image_list.Add(get_icon("folder-open"))
        self._icon_file = self._image_list.Add(get_art(wx.ART_NORMAL_FILE, scale_to=16))
        self.list.AppendColumn("Название", 250)
        self.list.AppendColumn("Тип", 50)
        self.list.AppendColumn("Размер", 50)
        self.list.AppendColumn("Датировка", 80)
        self.list.Hide()

        self.SetSizer(main_sizer)
        self._main_sizer = main_sizer

        self.list.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self._on_selection_changed)
        self.list.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self._on_item_contenxt_menu)

        self.Layout()

    def _on_selection_changed(self, event):
        self._update_controls_state()

    def _on_create_folder(self, event):
        dlg = FolderEditor(self)
        dlg.ShowModal()

    def _on_create_file(self, event):
        dlg = FileEditor(self)
        dlg.ShowModal()

    def _on_item_contenxt_menu(self, event: wx.dataview.DataViewEvent):
        item = event.GetItem()
        menu = wx.Menu()
        if not item.IsOk():
            item = menu.Append(wx.ID_ADD, "Добавить раздел")
            item.SetBitmap(get_icon("folder-add"))
            menu.Bind(wx.EVT_MENU, self._on_create_folder, item)
        else:
            item = self.list.GetSelection()
            if isinstance(self.list.GetItemData(item), SuppliedData):
                item = menu.Append(wx.ID_EDIT, "Изменить раздел")
            else:
                item = menu.Append(wx.ID_EDIT, "Изменить файл")
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить файл")
            item.SetBitmap(get_icon("file-add"))
            menu.Bind(wx.EVT_MENU, self._on_create_file, item)
            item = menu.Append(wx.ID_DELETE, "Удалить")
            item.SetBitmap(get_icon("delete"))

        self.PopupMenu(menu, event.GetPosition())

    def _apply_icon(self, icon_name, icon):
        if icon_name not in self._icons:
            self._icons[icon_name] = self._image_list.Add(icon)
        return self._icons[icon_name]

    @db_session
    def _render(self):
        self.list.DeleteAllItems()
        for o in select(o for o in SuppliedData if o.OwnID == self.o.RID and o.OwnType == self._type):
            folder = self.list.AppendItem(
                self.list.GetRootItem(),
                o.Name,
                self._icon_folder,
                self._icon_folder_open,
                o,
            )
            self.list.SetItemText(folder, 1, "Папка")
            self.list.SetItemText(folder, 2, "---")
            for child in o.parts:
                ext = child.FileName.split(".")[-1]
                if ext == "xlsx":
                    ext = "xls"
                icon_path = resource_path("icons/%s.png" % ext)
                if os.path.exists(icon_path):
                    _icon = self._apply_icon(ext, wx.Bitmap(icon_path))
                else:
                    _icon = self._icon_file
                file = self.list.AppendItem(folder, child.Name, _icon, _icon, child)
                self.list.SetItemText(file, 1, child.FileName.split(".")[-1])
                self.list.SetItemText(file, 2, "---")

    def _update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_ADD, self.o != None)
        item = self.list.GetSelection()
        item_selected = False
        folder_selected = False
        if item.IsOk():
            item_selected = True
            folder_selected = isinstance(self.list.GetItemData(item), SuppliedData)
        self.toolbar.EnableTool(wx.ID_FILE, folder_selected)

    def start(self, o, _type):
        self.o = o
        self._type = _type
        self._main_sizer.Detach(2)
        self._deputy.Hide()
        self._main_sizer.Add(self.list, 1, wx.EXPAND)
        self.list.Show()
        self._render()
        self.statusbar.SetStatusText(o.get_tree_name())
        self.Layout()

    def end(self):
        self.o = None
        self._type = None
        self.list.DeleteAllItems()
        self._main_sizer.Detach(2)
        self.list.Hide()
        self._main_sizer.Add(self._deputy, 1, wx.CENTER)
        self._deputy.Show()
        self.statusbar.SetStatusText("")
        self.Layout()
