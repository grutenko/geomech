import wx
import wx.lib.newevent

ID_TEST_SERIES = wx.ID_HIGHEST + 1
ID_ADD_PM_SAMPLE_SET = ID_TEST_SERIES + 1
ID_ADD_PM_SAMPLE = ID_TEST_SERIES + 2
ID_ADD_ORIG_SAMPLE_SET = ID_TEST_SERIES + 3

WidgetStateChangedEvent, EVT_WIDGET_STATE_CHANGED = wx.lib.newevent.NewEvent()
