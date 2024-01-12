import wx
import database
import typing
import mixins
from .ui.supplied_data_editor import (
    Ui_SuppliedData_Editor,
    UI_DataEditor_Dialog,
    Ui_DataPartsEditor_Dialog
)

class _DataEditor_Dialog(UI_DataEditor_Dialog, mixins.OptionalFieldsMixin):
    pass

class _DataPartsEditor_Dialog(Ui_DataPartsEditor_Dialog, mixins.OptionalFieldsMixin):
    pass

class SuppliedDataEditor(Ui_SuppliedData_Editor):
    _data: typing.List[database.SuppliedData] = []
    _selected_data: typing.List[database.SuppliedData] = []
    # Parts for current selected supplied data
    _parts: typing.List[database.SuppliedDataPart] = []
    _selected_parts: typing.List[database.SuppliedDataPart] = []

    _deleted_entities: typing.List[database.Base] = set()

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
        parts = filter(lambda item: item not in self._deleted_entities, self._parts)
        for row_index, item in enumerate(parts):
            self.list_parts.InsertItem(row_index, "")
            self.list_parts.SetItem(row_index, 0, item.Name)
            self.list_parts.SetItem(row_index, 1, "н/а")
            self.list_parts.SetItem(row_index, 2, item.DType)

    def __update_controls_state(self):
        self.btn_add_data.Enable(True)
        self.btn_edit_data.Enable(len(self._selected_data) == 1)
        self.btn_delete_data.Enable(len(self._selected_data) > 0)
        self.btn_add_part.Enable(len(self._selected_data) > 0)
        self.btn_edit_part.Enable(len(self._selected_parts) == 1)
        self.btn_delete_part.Enable(len(self._selected_parts) > 0)

    def set_data(self, data: typing.List[database.SuppliedData]):
        self._data = data
        self._selected_data = []
        self._render_data()

    def _render_data(self):
        self.list_data.DeleteAllItems()
        data = filter(lambda item: item not in self._deleted_entities, self._data)
        for row_index, item in enumerate(data):
            self.list_data.InsertItem(row_index, "")
            self.list_data.SetItem(row_index, 0, item.Name)

    def __on_add_data(self, event):
        w = _DataEditor_Dialog(parent=self)
        w.ShowModal()

    def __on_edit_data(self, event):
        w = _DataEditor_Dialog(parent=self)
        w.ShowModal()

    def __on_delete_data(self, event):
        self._deleted_entities.update(self._selected_data)
        self._selected_data = []
        self._render_data()

    def __on_add_part(self, event):
        w = _DataPartsEditor_Dialog(parent=self)
        w.ShowModal()

    def __on_edit_part(self, event):
        w = _DataPartsEditor_Dialog(parent=self)
        w.ShowModal()

    def __on_delete_part(self, event):
        self._deleted_entities.update(self._selected_parts)
        self._selected_parts = []
        self._render_parts()