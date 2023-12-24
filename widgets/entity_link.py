# _*_ coding: UTF8 _*_

import wx
import typing
import database
import inspect_windows
import list_windows
import resources

_T = typing.TypeVar('_T', bound=database.Base)

class EntityLink(wx.Button, typing.Generic[_T]):
    _entity: _T
    _name_field: str = "Name"
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 1, ""))
        self.SetOwnForegroundColour(wx.Colour(0, 102, 204))
        self.SetBitmap(wx.Bitmap(resources.resource_path("icons/external-link.png")))

        self.Bind(wx.EVT_BUTTON, self.__on_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self.__on_context_menu)

    def __on_context_menu(self, event):
        menu = wx.Menu()
        item = menu.Append(wx.MenuItem(menu, wx.NewId(), "Показать в списке"))
        self.Bind(wx.EVT_MENU, self.__on_show_in_list_click)
        self.PopupMenu(menu, event.GetPosition())

    def __on_show_in_list_click(self, event):
        list_windows.cmd_show(self._entity.__class__, with_selection=[self._entity])

    def __on_click(self, event):
        inspect_windows.cmd_show(self._entity)

    def set_entity(self, e: _T, name_field: str = 'Name'):
        if not issubclass(type(e), database.Base):
            raise Exception("{0} is not a database entity.".format(e.__class__.__name__))
        if not hasattr(e, name_field):
            raise Exception("{0} not contained in {1}".format(name_field, e.__class__.__name__))
        self._entity = e
        self._name_field = name_field
        self._name = getattr(self._entity, self._name_field)
        self.SetLabel(self._name if len(self._name) <= 20 else self._name[:20] + '...')
