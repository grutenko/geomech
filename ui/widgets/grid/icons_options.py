import wx
from dataclasses import dataclass

@dataclass
class IconsOptions:
    save: wx.Bitmap = wx.NullBitmap
    copy: wx.Bitmap = wx.NullBitmap
    cut: wx.Bitmap = wx.NullBitmap
    insert: wx.Bitmap = wx.NullBitmap
    cancel: wx.Bitmap = wx.NullBitmap
    back: wx.Bitmap = wx.NullBitmap
    add_row: wx.Bitmap = wx.NullBitmap
    delete_row: wx.Bitmap = wx.NullBitmap
    up: wx.Bitmap = wx.NullBitmap
    down: wx.Bitmap = wx.NullBitmap
    up: wx.Bitmap = wx.NullBitmap
    write_text: wx.Bitmap = wx.NullBitmap
    save: wx.Bitmap = wx.NullBitmap
    add_row: wx.Bitmap = wx.NullBitmap