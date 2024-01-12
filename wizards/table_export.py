# _*_ coding: UTF8 _*_

import wx
import typing
import column
import database
import re
import xlsxwriter
import csv
from form_validators import TextValidator
from .ui.export_wizard import UI_ExportWizard

def _export_csv(entities, cols, filename, gauge):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(list(map(lambda col: col.label if col.label != None else col.name, cols)))
        gauge.SetRange(len(entities))
        gauge.SetValue(0)
        for i, e in enumerate(entities):
            gauge.SetValue(i)
            writer.writerow(list(map(lambda col: getattr(e, col.name) if col.modifier == None else col.modifier(e, getattr(e, col.name)), cols)))

def _export_xls(entities, cols, filename, gauge: wx.Gauge):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    for i, col in enumerate(cols):
        worksheet.write(0, i, col.label if col.label != None else col.name)
    gauge.SetRange(len(entities))
    gauge.SetValue(0)
    for i, e in enumerate(entities, 1):
        for j, col in enumerate(cols):
            value = getattr(e, col.name) if col.modifier == None else col.modifier(e, getattr(e, col.name))
            worksheet.write(i, j, value)
        gauge.SetValue(i)
    workbook.close()

class TableExport(UI_ExportWizard):
    _available_cols: typing.List[column.Column]
    _cols: typing.List[column.Column] = []
    _entities: typing.List[database.Base]

    def __init__(self, 
                 available_cols: typing.List[column.Column],
                 cols: typing.List[column.Column],
                 entities: typing.List[database.Base], *args, **kwds):
        super().__init__(*args, **kwds)

        self._available_cols = available_cols
        self._cols = cols

        self.columns.InsertItems(list(map(lambda x: x.label, self._available_cols)), 0)
        indexes = []
        for col in self._cols:
            for i, available in enumerate(self._available_cols):
                if available.name == col.name:
                    indexes.append(i)
        self.columns.SetCheckedItems(indexes)
        self._entities = entities

        self.field_file_name.SetValidator(TextValidator(len_min=1, message="Заполните путь сохранения файла."))
        self.__bind()
        self.__render_list()

    def __bind(self):
        self.btn_SelectFile.Bind(wx.EVT_BUTTON, self.__on_click_select_file)
        self.columns.Bind(wx.EVT_CHECKLISTBOX, self.__on_columns_changed)
        self.btn_export.Bind(wx.EVT_BUTTON, self.__on_click_export)
        self.field_export_type.Bind(wx.EVT_CHOICE, self.__on_update_export_type)
        self.btn_select_all_cols.Bind(wx.EVT_BUTTON, self.__on_select_all_cols_click)

    def __on_select_all_cols_click(self, event):
        self.columns.SetCheckedItems(range(0, len(self._available_cols)))
        self._cols = self._available_cols
        self.__render_list()

    def __on_columns_changed(self, event):
        self._cols = list(map(lambda index: self._available_cols[index], self.columns.GetCheckedItems()))
        self.__render_list()

    def __render_list(self):
        self.table.DeleteAllItems()
        self.table.DeleteAllColumns()

        for col in self._cols:
            colIndx = self.table.AppendColumn(
                col.label if not col.label is None else col.name,
                wx.LIST_FORMAT_LEFT, col.size)
        if len(self._cols) == 0:
            return
        
        def _set_col(e, row_index, col_index, col, value):
            value = col.modifier(e, value) if not col.modifier is None else str(value)
            self.table.SetItem(row_index, col_index, value)

        for row_index, e in enumerate(self._entities):
            self.table.InsertItem(row_index, "")
            for col_index, col in enumerate(self._cols):
                _set_col(e, row_index, col_index, col, e.__dict__[col.name])

    def __on_update_export_type(self, event):
        if len(self.field_file_name.GetValue()) == 0:
            return
        if self.field_export_type.GetSelection() == 0:
            self.field_file_name.SetValue(re.sub(r"\.[^\.]+$", '.csv', self.field_file_name.GetValue()))
        elif self.field_export_type.GetSelection() == 1:
            self.field_file_name.SetValue(re.sub(r"\.[^\.]+$", '.xlsx', self.field_file_name.GetValue()))

    def __on_click_select_file(self, event):
        if self.field_export_type.GetSelection() == 0:
            message = "Сохранить CSV файл"
            wildcard = "CSV файлы (*.csv)|*.csv"
        elif self.field_export_type.GetSelection() == 1:
            message = "Сохранить как таблицу Microsoft Excell"
            wildcard = "Microsoft Excell XLS файлы (*.xlsx)|*.xlsx"
        with wx.FileDialog(self, message, wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.field_file_name.SetValue(pathname)

    def _in_progress_state(self, in_progress):
        self.field_export_type.Enable(not in_progress)
        self.field_file_name.Enable(not in_progress)
        self.btn_SelectFile.Enable(not in_progress)
        self.btn_export.Enable(not in_progress)
        self.table.Enable(not in_progress)
        self.columns.Enable(not in_progress)
    
    def __on_click_export(self, event):
        if not self.Validate():
            return
        
        self._in_progress_state(True)
        if self.field_export_type.GetSelection() == 0:
            _export_csv(self._entities, self._cols, self.field_file_name.GetValue(), self.export_progress)
        elif self.field_export_type.GetSelection() == 1:
            _export_xls(self._entities, self._cols, self.field_file_name.GetValue(), self.export_progress)
        self._in_progress_state(False)
        self.export_progress.SetValue(0)

        wx.MessageBox("Экспорт завершен", "Экспорт завершен")
        

