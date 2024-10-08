import wx
import wx.richtext as rt

import webbrowser

import urllib
from urllib.error import HTTPError, URLError

from io import BytesIO
from pathlib import Path


class ExtendedRichText(rt.RichTextCtrl):
    """
    `RichTextCtrl` with some extra quality-of-life methods and functionality.
    """

    def __init__(self, parent,
        files_directory: str = "",
        allow_download_images: bool = False,
        *args, **kwargs
    ) -> None:

        super().__init__(parent, style=wx.TE_RICH2, *args, **kwargs)
        
        self.indentations = [0]
        self.ordered_list_indices = []
        
        self.files_directory = Path(files_directory)
        self.allow_download_images = allow_download_images

        self.Bind(wx.EVT_TEXT_URL, self.on_url)

    
    def on_url(self, event: rt.RichTextEvent) -> None:
        """Open link in web browser."""
        webbrowser.open(event.GetString())


    def GetIndentation(self) -> int:
        """
        Get current indentation.
        """
        return int(sum(self.indentations))

    def GetStyle(self) -> rt.RichTextAttr:
        """
        Get current style.
        """
        style = rt.RichTextAttr()
        super().GetStyle(self.GetInsertionPoint(), style)
        return style

    def EnsureNewline(self) -> None:
        """
        Ensure buffer ends in newline.
        """
        if self.GetValue()[-1:] != '\n':
            self.Newline()


    def BeginIndentation(self, indentation: int) -> None:
        """
        Begins an indentation.
        """
        self.indentations.append(indentation)
        self.BeginLeftIndent(self.GetIndentation())

    def EndIndentation(self) -> None:
        """
        Ends an indentation.
        """
        self.EndLeftIndent()
        self.indentations.pop()


    def BeginParagraph(self) -> None:
        """
        Begins paragraph.
        """

    def EndParagraph(self) -> None:
        """
        Ends paragraph.
        """
        self.Newline()


    def BeginBlockquote(self) -> None:
        """
        Begins blockquote.
        """
        self.BeginIndentation(self.GetCharWidth() * 2)
        self.BeginTextColour('#FF8000')

    def EndBlockquote(self) -> None:
        """
        Ends blockquote.
        """
        self.EndTextColour()
        self.EndIndentation()


    def BeginCode(self) -> None:
        """
        Begins code.
        """
        font_info = self.GetStyle().GetFont()
        font_info.SetFamily(wx.FONTFAMILY_TELETYPE)
        font = wx.Font(font_info)
        self.BeginFont(font)

    def EndCode(self) -> None:
        """
        Ends code.
        """
        self.EndFont()


    def BeginHeading1(self) -> None:
        """
        Begins heading 1.
        """
        self.BeginFontSize(int(self.Font.GetPointSize() * 2.0))

    def EndHeading1(self) -> None:
        """
        Ends heading 1.
        """
        self.EndFontSize()
        self.Newline()

    def BeginHeading2(self) -> None:
        """
        Begins heading 2.
        """
        self.BeginFontSize(int(self.Font.GetPointSize() * 1.5))

    def EndHeading2(self) -> None:
        """
        Ends heading 2.
        """
        self.EndFontSize()
        self.Newline()

    def BeginHeading3(self) -> None:
        """
        Begins heading 3.
        """
        self.BeginFontSize(int(self.Font.GetPointSize() * 1.3))

    def EndHeading3(self) -> None:
        """
        Ends heading 3.
        """
        self.EndFontSize()
        self.Newline()

    def BeginHeading4(self) -> None:
        """
        Begins heading 4.
        """
        self.BeginFontSize(int(self.Font.GetPointSize() * 1.0))

    def EndHeading4(self) -> None:
        """
        Ends heading 4.
        """
        self.EndFontSize()
        self.Newline()

    def BeginHeading5(self) -> None:
        """
        Begins heading 5.
        """
        self.BeginFontSize(int(self.Font.GetPointSize() * 0.8))

    def EndHeading5(self) -> None:
        """
        Ends heading 5.
        """
        self.EndFontSize()
        self.Newline()

    def BeginHeading6(self) -> None:
        """
        Begins heading 6.
        """
        self.BeginFontSize(int(self.Font.GetPointSize() * 0.7))

    def EndHeading6(self) -> None:
        """
        Ends heading 6.
        """
        self.EndFontSize()
        self.Newline()


    def BeginLink(self, url: str) -> None:
        """
        Begins link.
        """
        self.BeginURL(url)
        self.BeginUnderline()
        self.BeginTextColour('#8800FF')
    
    def EndLink(self) -> None:
        """
        Ends link.
        """
        self.EndTextColour()
        self.EndUnderline()
        self.EndURL()


    def BeginUnorderedList(self) -> None:
        """
        Begins unordered list.
        """
        self.EnsureNewline()

    def EndUnorderedList(self) -> None:
        """
        Ends unordered list.
        """
        self.EnsureNewline()

    def BeginUnorderedListItem(self) -> None:
        """
        Begins unordered list item.
        """
        self.EnsureNewline()
        indent = self.GetIndentation()
        subindent = int(self.GetCharWidth() * 1.5)
        self.BeginStandardBullet('circle', indent, subindent)

    def EndUnorderedListItem(self) -> None:
        """
        Ends unordered list item.
        """
        self.EnsureNewline()
        self.EndStandardBullet()


    def BeginOrderedList(self) -> None:
        """
        Begins ordered list.
        """
        self.ordered_list_indices.append(0)
        self.EnsureNewline()


    def EndOrderedList(self) -> None:
        """
        Ends ordered list.
        """
        self.EnsureNewline()
        self.ordered_list_indices.pop()

    def BeginOrderedListItem(self) -> None:
        """
        Begins ordered list item.
        """

        self.EnsureNewline()

        # Increment counter and get current index
        self.ordered_list_indices[-1] += 1
        index = self.ordered_list_indices[-1]

        # Calculate the subindent from the width of the prefix
        digits = len(str(index))
        # TODO: Make this consistent.
        # This formula seems to align the text properly,
        # but it isn't rooted in anything mathematically sound.
        subindent = int(self.GetCharWidth() * 0.65 * (digits + 2))

        self.BeginNumberedBullet(index, self.GetIndentation(), subindent)

    def EndOrderedListItem(self) -> None:
        """
        Ends ordered list item.
        """
        self.EnsureNewline()
        self.EndStandardBullet()

    def WriteImage(self,
        source: str, alt_text: str = "",
        width: int = None, height: int = None
        ) -> wx.Image:
        """
        Write an image.
        """
        
        try:
            # Download image
            if source.startswith('http://') or source.startswith('https://'):

                if not self.allow_download_images:
                    raise PermissionError('Downloading images is disabled.')
                    
                request = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
                stream = BytesIO(urllib.request.urlopen(request).read())
                image = wx.Image(stream, wx.BITMAP_TYPE_ANY)
                
            # Use local image
            else:
                path = Path(source)
                if not path.exists() \
                or not path.is_file():
                    raise FileNotFoundError(source)

                image = wx.Image(self.image_directory / path)

        except (FileNotFoundError, HTTPError, URLError, PermissionError):
            # If anything goes wrong
            # with finding and rendering the image,
            # render the alt text in stead.
            
            if alt_text:
                self.BeginTextColour('grey')
                self.BeginItalic()
                self.WriteText(alt_text)
                self.EndItalic()
                self.EndTextColour()

        else:
            # Scale image
            if width and height:
                # Resize to new width and height
                image.Rescale(int(width), int(height))

            elif width and height is None:
                # Maintain aspect ratio
                ratio = int(width) / image.GetWidth()
                height = image.GetHeight() * ratio
                # Resize to new width and matching height
                image.Rescale(int(width), int(height))

            elif width is None and height:
                # Maintain aspect ratio
                ratio = int(height) / image.GetHeight()
                width = image.GetWidth() * ratio
                # Resize to new height and matching width
                image.Rescale(int(width), int(height))

            # Render image
            super().WriteImage(image)