# _*_ coding: UTF8 _*_

import wx.lib.newevent
from enum import Enum

class ManageTypes(Enum):
    NEED_CREATE = 1
    NEED_EDIT = 2
    NEED_DELETE = 3
    NEED_FILTER = 4
    NEED_SHOW_DETAIL = 5
    NEED_CONTEXT_MENU = 6

__xEntityManageEventType__ = wx.NewEventType()

class xEntityManageEvent(wx.PyEvent):
    def __init__(self, **kw):
        wx.PyEvent.__init__(self)
        self.SetEventType(__xEntityManageEventType__)
        self._getAttrDict().update(kw)

EVT_ENTITY_MANAGE_EVENT = wx.PyEventBinder(__xEntityManageEventType__)