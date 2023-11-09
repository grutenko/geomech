import wx
from pubsub import pub
from Ui_MainWindow import Ui_MainWindow
from DischargeMeasurement_Editor import DischargeMeasurement_Editor
from Ui_DischargeSeries_Editor import Ui_DischargeSeries_Editor
import database
from database import (
    DischargeMeasurement,
    DischargeSeries,
    session
)

def _insert_row(list: wx.ListCtrl, index: int, item: DischargeMeasurement):
    list.InsertItem(index, item.RID)

    def _set(col, value, units=None):
        if value != None:
            text = str(value) + (" " + units if units != None else "")
        else:
            text = "<NULL>"
        list.SetItem(index, col, text)

    _set(0, item.RID)
    _set(1, item.DSID)
    _set(2, item.SNumber)
    _set(3, item.DschNumber)
    _set(4, item.CoreNumber)
    _set(5, item.Diameter, 'мм')
    _set(6, item.Length, 'мм')
    _set(7, item.Weight, 'г')
    _set(8, item.CartNumber)
    _set(9, item.PartNumber)
    _set(10, item.R1, 'Ом')
    _set(11, item.R2, 'Ом')
    _set(12, item.R3, 'Ом')
    _set(13, item.R4, 'Ом')
    _set(14, item.RComp, 'Ом')
    _set(15, item.Sensitivity)
    _set(16, item.TP1_1, 'мс')
    _set(17, item.TP1_2, 'мс')
    _set(18, item.TP2_1, 'мс')
    _set(19, item.TP2_2, 'мс')
    _set(20, item.TR_1, 'мс')
    _set(21, item.TR_2, 'мс')
    _set(22, item.TS_1, 'мс')
    _set(23, item.TS_2, 'мс')
    _set(24, item.PuassonStatic)
    _set(25, item.YungStatic)
    _set(26, item.CoreDepth)
    _set(27, item.E1)
    _set(28, item.E2)
    _set(29, item.E3)
    _set(30, item.E4)
    _set(31, item.Rotate)
    _set(32, item.RockType)

class MainWindow(Ui_MainWindow):
    index = 0
    query = None

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        
        self.query = database.session.query(DischargeMeasurement)
        self._SetData()
        self._SetFilterData()
        self.list_ctrl_1.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        self.btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefresh)
        self.btn_find.Bind(wx.EVT_BUTTON, self.OnQuery)

        self.popup_menu = wx.Menu()
        self.popup_menu.Append(wx.ID_ABOUT, 'Детальная информация')
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(wx.ID_EDIT, "Редактировать")
        self.popup_menu.Append(wx.ID_DELETE, "Удалить")

        self.list_popup_menu = wx.Menu()
        self.list_popup_menu.Append(wx.ID_ADD, 'Создать')
        self.list_popup_menu.Append(wx.ID_REFRESH, 'Обновить')

        self.Bind(wx.EVT_MENU, self.OnContextMenuClick)

        pub.subscribe(self._Refresh, 'main.need_refresh')

    def OnCreateDischargeMeasure(self, event):  # wxGlade: Ui_MainWindow.<event_handler>
        editor = DischargeMeasurement_Editor(self)
        editor.Show()

    def OnCreateDischargeSeries(self, event):  # wxGlade: Ui_MainWindow.<event_handler>
        editor = Ui_DischargeSeries_Editor(self)
        editor.Show()

    def _SetFilterData(self):
        series = database.session.query(DischargeSeries).all()
        for itemData in series:
            self.choice_1.Append(itemData.Name, itemData.RID)

    def _SetData(self):
        self.list_ctrl_1.Disable()
        items = self.query.all()
        for itemData in items:
            _insert_row(self.list_ctrl_1, self.index, itemData)
            self.index += 1
        self.list_ctrl_1.Enable()

    def OnRefresh(self, event):
        self._Refresh()

    def OnQuery(self, event):
        id = self.choice_1.GetClientData(self.choice_1.GetSelection())
        if id != None:
            self.query = (
                database.session.query(DischargeMeasurement)
                    .where(DischargeMeasurement.DSID == id)
            )
        else:
            self.query = database.session.query(DischargeMeasurement)

        self._Refresh()

    def OnContextMenu(self, event):
        item, _flags = self.list_ctrl_1.HitTest(event.GetPosition())
        if item == -1:
            self.list_ctrl_1.PopupMenu(self.list_popup_menu)
        else:
            self.list_ctrl_1.Select(item)
            self.list_ctrl_1.PopupMenu(self.popup_menu)

    def OnContextMenuClick(self, event):
        rid = None
        selected = self.list_ctrl_1.GetFirstSelected()
        if selected != -1:
            rid = self.list_ctrl_1.GetItem(selected, 0).GetText()
        if event.GetId() == wx.ID_ADD:
            self._OpenEditor(None)
        elif event.GetId() == wx.ID_REFRESH:
            self._Refresh()
        if event.GetId() == wx.ID_ABOUT:
            self._OpenInspector(rid)
        elif event.GetId() == wx.ID_EDIT:
            self._OpenEditor(rid)
        elif event.GetId() == wx.ID_DELETE:
            self._Delete(rid)

    def _OpenInspector(self, rowId):
        pass

    def _OpenEditor(self, rowId = None):
        if rowId != None:
            entity = database.session.query(DischargeMeasurement).get(rowId)
            if entity == None:
                dlg = wx.MessageDialog(self, "Ошибка!", 
                                    "Не удалось найти замер."
                                    + " Возможно он уже кем-то удален из Базы данных."
                                    + " Попробуйте обновить страницу и проверить наличие.")
                dlg.ShowModal()
                dlg.Destroy()
            self.editor = DischargeMeasurement_Editor(self)
            self.editor.SetEntity(entity)
            self.editor.Show()
        else:
            self.editor = DischargeMeasurement_Editor(self)
            self.editor.Show()

    def _Delete(self, rowId):
        item = database.session.query(DischargeMeasurement).get(rowId)
        if item == None:
            return
        
        dlg = wx.MessageDialog(self, 
            "Вы действительно хотите удалить замер №" + str(item.SNumber) + ". Это действие необратимо",
            "Подтвердите удаление",
            wx.OK | wx.CANCEL)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            database.session.delete(item)
            database.session.commit()
            self._Refresh()
        dlg.Destroy()

    def _Refresh(self):
        self.index = 0
        self.list_ctrl_1.DeleteAllItems()
        self._SetData()
            