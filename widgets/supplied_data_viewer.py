from collections.abc import Callable, Iterable, Mapping
from typing import Any
import wx
import wx.dataview
import database
import resources
import typing
import os
import threading
from pathvalidate import sanitize_filename
from .ui.supplied_data_viewer import Ui_SuppliedData_Viewer

EVT_RESULT_ID = wx.NewId() 
def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)
class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class SuppliedData_Viewer(Ui_SuppliedData_Viewer):
    _owner: database.SuppliedDataOwner

    __folder_icon: int
    __file_icon: int

    __mapping: typing.Dict[int, typing.Tuple[database.SuppliedData, typing.Dict[int, database.SuppliedDataPart]]] = {}

    __download_progress: wx.ProgressDialog = None
    __download_worker: threading.Thread

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        images = wx.ImageList(16, 16)
        self.__folder_icon = images.Add(wx.Bitmap(wx.Image(resources.resource_path('icons/folder.png'))))
        self.__file_icon = images.Add(wx.Bitmap(wx.Image(resources.resource_path('icons/text-x-generic.png'))))
        self.tree.AssignImageList(images) 
        self.tree.AppendColumn('Название', 350)
        self.tree.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.__on_checked)
        self.button_select_all.Bind(wx.EVT_BUTTON, self.__on_select_all)
        self.button_download.Bind(wx.EVT_BUTTON, self.__on_download)
        EVT_RESULT(self.GetParent(), self.__on_download_progress)

    def set_data_owner(self, owner: database.SuppliedDataOwner):
        self._owner = owner
        self.__render()

    class DownloadThread(threading.Thread):
        __notify_window: wx.Object
        __path: str
        __content: typing.List[typing.Tuple[database.SuppliedData, typing.List[database.SuppliedDataPart]]]
        __want_abort: int = 0
            
        def __init__(self, notify_window, path, content):
            threading.Thread.__init__(self)
            self.__notify_window = notify_window
            self.__path = path
            self.__content = content
            self.start()

        def run(self):
            try:
                self.__do_download()
            except Exception as e:
                wx.PostEvent(self.__notify_window, ResultEvent({'status': 'exception', 'exc': e}))

        def __do_download(self):
            i = 0
            total = 0
            for data, parts in self.__content:
                for part in parts:
                    total += 1
            wx.PostEvent(self.__notify_window, ResultEvent({'status': 'inited', 'total': total}))
            for data, parts in self.__content:
                path = os.path.join(self.__path, sanitize_filename(data.Name))
                if not os.path.exists(path):
                    os.makedirs(path)
                for part in parts:
                    if self.__want_abort:
                        wx.PostEvent(self.__notify_window, ResultEvent({'status': 'aborted'}))
                        return
                    filepath = os.path.join(path, sanitize_filename(part.FileName))
                    i += 1
                    with open(filepath, 'wb') as file:
                        file.write(part.DataContent)
                    wx.PostEvent(self.__notify_window, ResultEvent({
                        'status': 'in_progress',
                        'path': filepath,
                        'progress': i,
                        'total': total
                    }))
            wx.PostEvent(self.__notify_window, ResultEvent({'status': 'completed'}))

        def abort(self):
            self.__want_abort = 1

    def __on_download(self, event):
        message = "Директория скачивания"
        with wx.DirDialog(self, message, style=wx.DD_NEW_DIR_BUTTON) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dlg.GetPath()
            content = []
            for item, (data, parts) in self.__mapping.items():
                if self.tree.GetCheckedState(item) == 0:
                    continue
                content.append((data, []))
                for sub_item, part in parts.items():
                    if self.tree.GetCheckedState(sub_item) == 0:
                        continue
                    content[-1][1].append(part)
            self.__download_worker = self.DownloadThread(self.GetParent(), pathname, content)
            self.__download_progress = wx.ProgressDialog("Cохранение сопутствующи материалов.", "Идет сохранение сопутсвующих материалов.", parent=self.GetParent(), style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE)

    def __on_download_progress(self, event):
        if self.__download_progress == None:
            return
        data = event.data
        total = 0
        if data['status'] == 'inited':
            total = data['total']
        elif data['status'] == 'in_progress':
            self.__download_progress.SetRange(data['total'])
            self.__download_progress.Update(data['progress'], (data['path'][:75] + '..') if len(data['path']) > 75 else data['path'])
        else:
            if total > 0:
                self.__download_progress.Update(total)
            self.__download_progress.Destroy()
            self.__download_progress = None
            self.__download_worker = None
            if data['status'] == 'exception':
                raise data['exc']
        

    def __on_select_all(self, event):
        for item in list(self.__mapping.keys()):
            self.tree.CheckItem(item)
            for part in list(self.__mapping[item][1].keys()):
                self.tree.CheckItem(part)
        self.__update_controls_state()
    
    def __update_controls_state(self):
        can_download = False
        for item in list(self.__mapping.keys()):
            if self.tree.GetCheckedState(item) != 0:
                can_download = True
                break;
        self.button_download.Enable(can_download)

    def __on_checked(self, event: wx.dataview.TreeListEvent):
        is_checked = self.tree.GetCheckedState(event.GetItem())
        if self.tree.GetItemParent(event.GetItem()) == self.tree.GetRootItem():
            for part in list(self.__mapping[event.GetItem()][1].keys()):
                self.tree.CheckItem(part, is_checked)
        else:
            parent = self.tree.GetItemParent(event.GetItem())
            all_checked = True
            partially_checked = False
            for part in list(self.__mapping[parent][1].keys()):
                all_checked = all_checked and self.tree.GetCheckedState(part) == 1
                partially_checked = partially_checked or self.tree.GetCheckedState(part) == 1
            if all_checked:
                self.tree.CheckItem(parent)
            elif partially_checked:
                self.tree.CheckItem(parent, wx.CHK_UNDETERMINED)
            else:
                self.tree.CheckItem(parent, wx.CHK_UNCHECKED)
        self.__update_controls_state()

    def __render(self):
        self.tree.DeleteAllItems()
        self.__mapping = {}
        for data in self._owner.supplied_data:
            item = self.tree.AppendItem(self.tree.GetRootItem(), data.Name, self.__folder_icon, self.__folder_icon)
            self.__mapping[item] = (data, {})
            for part in data.parts:
                part_item = self.tree.AppendItem(item, part.Name, self.__file_icon, self.__file_icon)
                self.__mapping[item][1][part_item] = part