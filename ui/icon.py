import wx

def get_icon(name, scale_to = None):
    icon = wx.Bitmap("icons/" + name + ".ico")
    if scale_to != None:
        image = icon.ConvertToImage()
        image = image.Scale(scale_to, scale_to, wx.IMAGE_QUALITY_HIGH)
        icon = image.ConvertToBitmap()
    return icon

def get_art(id, scale_to = None):
    return wx.ArtProvider.GetBitmap(id, wx.ART_MENU, size=(wx.Size(scale_to, scale_to) if scale_to != None else wx.DefaultSize))