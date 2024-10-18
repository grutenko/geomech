import wx

from ui.resourcelocation import resource_path


def get_icon(name, scale_to=None):
    icon = wx.Bitmap(resource_path("icons/" + name + ".ico"))
    if scale_to != None:
        image = icon.ConvertToImage()
        image = image.Scale(scale_to, scale_to, wx.IMAGE_QUALITY_HIGH)
        icon = image.ConvertToBitmap()
    return icon


def get_art(id, scale_to=None):
    icon = wx.ArtProvider.GetBitmap(id, wx.ART_MENU)
    if scale_to != None:
        image = icon.ConvertToImage()
        image = image.Scale(scale_to, scale_to, wx.IMAGE_QUALITY_HIGH)
        icon = image.ConvertToBitmap()
    return icon
