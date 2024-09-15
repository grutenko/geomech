import wx

def get_icon(name, scale_to = None):
    icon = wx.Bitmap("icons/" + name + ".ico")
    if scale_to != None:
        image = icon.ConvertToImage()
        image = image.Scale(scale_to, scale_to, wx.IMAGE_QUALITY_HIGH)
        icon = image.ConvertToBitmap()
    return icon