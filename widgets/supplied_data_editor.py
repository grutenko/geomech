import wx
import database
import typing
import mixins
import form_validators
import mimetypes
import os
from datetime import datetime
from .ui.supplied_data_editor import (
    Ui_SuppliedData_Editor,
    UI_DataEditor_Dialog,
    Ui_DataPartsEditor_Dialog
)

class _DataEditor_Dialog(UI_DataEditor_Dialog, mixins.OptionalFieldsMixin):
    __e: database.SuppliedData = None
    __is_new: bool = True
    __owner: database.SuppliedDataOwner

    def __init__(self, owner: database.SuppliedDataOwner, data: database.SuppliedData = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)
        self.__owner = owner

        self.field_Name.SetValidator(form_validators.TextValidator(len_min=1))
        self.field_Comment.SetValidator(form_validators.TextValidator(len_min=1))
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.SetEscapeId(wx.ID_CANCEL)
        self.SetAffirmativeId(wx.ID_SAVE)

        self.__e = data
        if data != None:
            self.__set_fields()
            self.__is_new = False

    def __set_fields(self):
        self.field_Name.SetValue(self.__e.Name)
        if self.__e.Number != None:
            self.field_Number.SetValue(self.__e.Number)
            self.field_Number.Enable(True)
            self.field_Number_enabled.SetValue(1)
        if self.__e.Comment != None:
            self.field_Comment.SetValue(self.__e.Comment)
            self.field_Comment.Enable(True)
            self.field_Comment_enabled.SetValue(1)
        if self.__e.DataDate != None:
            self.field_DataDate.SetValue(self.__e.DataDate)
            self.field_DataDate.Enable(True)
            self.field_DataDate_enabled.SetValue(1)

    def __on_cancel_click(self, event):
        self.Close()

    def __on_save_click(self, event):
        event.Skip()
        if self.__is_new:
            self.__e = database.SuppliedData()
            self.__e.OwnID = self.__owner.RID
            self.__e.OwnType = self.__owner.own_type
            database.get_session().add(self.__e)
        self.__e.Name = self.field_Name.GetValue()
        self.__e.Number = self.field_Number.GetValue() if self.field_Number.IsEnabled() else None
        self.__e.Comment = self.field_Comment.GetValue() if self.field_Comment.IsEnabled() else None
        if self.field_DataDate.IsEnabled():
            date: wx.DateTime = self.field_DataDate.GetValue()
            self.__e.DataDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())
        else:
            self.__e.DataDate = None
        database.commit_changes(self.GetParent())
        self.Close()
        

class _DataPartsEditor_Dialog(Ui_DataPartsEditor_Dialog, mixins.OptionalFieldsMixin):
    __e: database.SuppliedDataPart = None
    __is_new: bool = True
    __data: database.SuppliedData

    def __init__(self, 
                 data: database.SuppliedData,
                 part: database.SuppliedDataPart = None,
                 *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)
        self.__e = part
        self.__data = data
        if part != None:
            self.__is_new = False
            self.__set_fields()

        self.field_Name.SetValidator(form_validators.TextValidator(len_min=1))
        self.field_Comment.SetValidator(form_validators.TextValidator(len_min=1))
        self.file_name.SetValidator(form_validators.TextValidator(len_min=1))
        self.file_mime_type.SetValidator(form_validators.TextValidator(pattern=r'\w+/[-.\w]+(?:\+[-.\w]+)?'))
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_select_file.Bind(wx.EVT_BUTTON, self.__on_select_file)
        self.SetEscapeId(wx.ID_CANCEL)
        self.SetAffirmativeId(wx.ID_SAVE)

    def __set_fields(self):
        self.field_Name.SetValue(self.__e.Name)
        if self.__e.Comment != None:
            self.field_Comment.SetValue(self.__e.Comment)
            self.field_Comment_enabled.SetValue(1)
            self.field_Comment.Enable(True)
        self.field_DataDate.SetValue(self.__e.DataDate)
        self.file_mime_type.SetValue(self.__e.DType)
        self.file_name.SetValue(self.__e.FileName)

    def __on_select_file(self, event):
        if not self.__is_new:
            msg = "Сейчас вы выбираете новый файл для этого материала. Это удалит текущий файл. Продолжить?"
            dial = wx.MessageDialog(None, msg, 'Замена файла', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dial.ShowModal() != wx.ID_YES:
                return
        with wx.FileDialog(self, "Добавить сопроводительный материал", wildcard="Все файлы (*.*)|*.*", style=wx.FD_OPEN) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.file_path.SetValue(pathname)
            mime, _ = mimetypes.guess_type(pathname)
            if mime != None:
                self.file_mime_type.SetValue(mime)
            self.file_name.SetValue(os.path.basename(pathname))

    def __on_cancel_click(self, event):
        self.Close()

    def __on_save_click(self, event):
        event.Skip()
        if self.__is_new and len(self.file_path.GetValue()) == 0:
            dlg=wx.MessageDialog(None, "Не выбран файл",
                                "Выберите файл для загрузки.", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.file_path.GetValue()) > 0:
            stat = os.stat(self.file_path.GetValue())
            if stat.st_size > 1024*1024*50:
                dlg=wx.MessageDialog(None, "Максимальный размер превышен",
                                    "Выбранный файл превышаем максимальный размер в 50МБ.", wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        if self.__is_new:
            self.__e = database.SuppliedDataPart()
            self.__e.SDID = self.__data.RID
            database.get_session().add(self.__e)
        self.__e.Name = self.field_Name.GetValue()
        self.__e.Comment = self.field_Comment.GetValue() if self.field_Comment.IsEnabled() else None
        date: wx.DateTime = self.field_DataDate.GetValue()
        self.__e.DataDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())
        self.__e.DataDate = date
        if len(self.file_path.GetValue()) > 0:
            with open(self.file_path.GetValue(), 'rb') as file:
                self.__e.DataContent = memoryview(file.read())
        self.__e.DType = self.file_mime_type.GetValue()
        self.__e.FileName = self.file_name.GetValue()
        database.commit_changes(self.GetParent())

        self.Close()

class SuppliedDataEditor(Ui_SuppliedData_Editor):
    _owner: database.SuppliedDataOwner
    _data: typing.List[database.SuppliedData] = []
    _selected_data: typing.List[database.SuppliedData] = []
    # Parts for current selected supplied data
    _parts: typing.List[database.SuppliedDataPart] = []
    _selected_parts: typing.List[database.SuppliedDataPart] = []

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__bind()

    def __bind(self):
        self.btn_add_data.Bind(wx.EVT_BUTTON, self.__on_add_data)
        self.btn_edit_data.Bind(wx.EVT_BUTTON, self.__on_edit_data)
        self.btn_delete_data.Bind(wx.EVT_BUTTON, self.__on_delete_data)
        self.btn_add_part.Bind(wx.EVT_BUTTON, self.__on_add_part)
        self.btn_edit_part.Bind(wx.EVT_BUTTON, self.__on_edit_part)
        self.btn_delete_part.Bind(wx.EVT_BUTTON, self.__on_delete_part)
        self.list_data.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__on_data_item_selected)
        self.list_data.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.__on_data_item_deselected)
        self.list_parts.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__on_part_item_selected)
        self.list_parts.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.__on_part_item_deselected)

    def set_data_owner(self, owner: database.SuppliedDataOwner):
        self._owner = owner
        self._render()

    def _render(self):
        self._data = self._owner.supplied_data
        self._selected_data = []
        self.list_data.DeleteAllItems()
        for row_index, item in enumerate(self._data):
            self.list_data.InsertItem(row_index, "")
            self.list_data.SetItem(row_index, 0, item.Name)
        self._selected_data = []
        self._parts = []
        self._selected_parts = []
        self.list_parts.DeleteAllItems()
        self.__update_controls_state()

    def __on_data_item_selected(self, event: wx.ListEvent):
        self._selected_data.append(self._data[event.GetIndex()])
        self.__load_parts()
        self.__update_controls_state()    

    def __on_data_item_deselected(self, event: wx.ListEvent):
        self._selected_data.remove(self._data[event.GetIndex()])
        if len(self._selected_data) > 0:
            self.__load_parts()
        else:
            self._parts = []
            self._selected_parts = []
            self.list_parts.DeleteAllItems()
        self.__update_controls_state()

    def __on_part_item_selected(self, event: wx.ListEvent):
        self._selected_parts.append(self._parts[event.GetIndex()])
        self.__update_controls_state()    

    def __on_part_item_deselected(self, event: wx.ListEvent):
        self._selected_parts.remove(self._parts[event.GetIndex()])
        self.__update_controls_state()

    def __load_parts(self):
        self._parts = self._selected_data[0].parts
        self._selected_parts = []
        self._render_parts()

    def _render_parts(self):
        self.list_parts.DeleteAllItems()
        for row_index, item in enumerate(self._parts):
            self.list_parts.InsertItem(row_index, "")
            self.list_parts.SetItem(row_index, 0, item.Name)
            self.list_parts.SetItem(row_index, 1, "н/а")
            self.list_parts.SetItem(row_index, 2, item.DType)
        self._selected_parts = []
        self.__update_controls_state()

    def __update_controls_state(self):
        self.btn_add_data.Enable(True)
        self.btn_edit_data.Enable(len(self._selected_data) == 1)
        self.btn_delete_data.Enable(len(self._selected_data) > 0)
        self.btn_add_part.Enable(len(self._selected_data) > 0)
        self.btn_edit_part.Enable(len(self._selected_parts) == 1)
        self.btn_delete_part.Enable(len(self._selected_parts) > 0)

    def __on_add_data(self, event):
        w = _DataEditor_Dialog(owner=self._owner, parent=self)
        w.ShowModal()
        self._render()

    def __on_edit_data(self, event):
        w = _DataEditor_Dialog(owner=self._owner, data=self._selected_data[0], parent=self)
        w.ShowModal()
        self._render()

    def __on_delete_data(self, event):
        msg = "Вы  действительно хотите удалить {0}объектов? Это действие необратимо.".format(len(self._selected_data))
        dial = wx.MessageDialog(None, msg, 'Подтвердите удаление', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            for item in self._selected_data:
                database.get_session().delete(item)
            database.commit_changes(self.GetParent())
        self._render()

    def __on_add_part(self, event):
        w = _DataPartsEditor_Dialog(data=self._selected_data[0], parent=self)
        w.ShowModal()
        self.__load_parts()

    def __on_edit_part(self, event):
        w = _DataPartsEditor_Dialog(data=self._selected_data[0], part=self._selected_parts[0], parent=self)
        w.ShowModal()
        self.__load_parts()

    def __on_delete_part(self, event):
        msg = "Вы  действительно хотите удалить {0} объектов? Это действие необратимо.".format(len(self._selected_data))
        dial = wx.MessageDialog(None, msg, 'Подтвердите удаление', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            for item in self._selected_parts:
                database.get_session().delete(item)
            database.commit_changes(self.GetParent())
        self._selected_parts = []
        self.__load_parts()