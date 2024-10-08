import wx
import wx.richtext as rt
import markdown
import bs4
import webbrowser

from itertools import zip_longest
from .extended_rtc import ExtendedRichText


def make_linebreaks_explicit(tag: bs4.Tag) -> None:
    """
    Make all linebreaks explicit as `<br>`.
    """

    contents = []
    for child in tag.contents:
        if not isinstance(child, bs4.NavigableString):
            make_linebreaks_explicit(child)
            contents.append(child)
            continue
        
        # Split all lines and convert them to `NavigableString`
        lines = child.string.strip('\n').split('\n')
        lines = [bs4.NavigableString(line) for line in lines]
        
        # Create a list of `<br>` tags to be used in-between lines
        brs = [bs4.Tag(name='br', can_be_empty_element=True, parent=tag)
                                 for _ in range(len(lines) - 1)]

        # Zip them all together
        zipped = zip_longest(lines, brs, fillvalue=None)
        items = [item for pair in zipped for item in pair if item is not None]

        # Remove empty strings
        items = [x for x in items if not isinstance(x, bs4.NavigableString) or x.string]
        
        # Add to contents
        contents.extend(items)

    tag.contents = contents


class Markdown(wx.Panel):
    """
    `Markdown` is a panel that renders Markdown using Rich Text.
    """

    def __init__(self, parent,
        files_directory: str = "",
        allow_download_images: bool = False,
        *args, **kwargs
    ) -> None:

        super().__init__(parent, *args, **kwargs)

        self.opened_lists = [None]

        self.rtc = ExtendedRichText(self,
            files_directory=files_directory,
            allow_download_images=allow_download_images)
        self.rtc.SetEditable(False)  # Make it read-only

        # self.rtc.Disable()
        # TODO: Figure out how to hide cursor without disabling
        # the ability to click links and interact with objects.
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.rtc, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)

        self.rtc.Bind(wx.EVT_TEXT_URL, self.handle_url)

    def handle_url(self, event: rt.RichTextEvent) -> None:
        """Open link in webbrowser."""
        webbrowser.open(event.GetString())
        
    def AddContent(self, text: str) -> None:
        """
        Add Markdown content.
        """

        # Parse Markdown into HTML
        html = markdown.markdown(text)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        make_linebreaks_explicit(soup)

        # Make sure content starts on an empty line
        if self.rtc.GetValue():
            self.rtc.Newline()

        # Set scale for spacing and such
        scale = self.rtc.GetCharHeight() // 3.5
        self.rtc.SetDimensionScale(scale)
        self.rtc.SetMargins(0, 0)

        # Generate Rich Text from HTML
        self._generate_richtext(soup)

        # Strip extraneous newlines
        value = self.rtc.GetValue()
        length = len(value) - len(value.rstrip('\n'))
        pos = self.rtc.GetInsertionPoint()
        self.rtc.Remove(pos - length, pos)

    def _generate_richtext(self, tag: bs4.Tag | str) -> None:
        """
        Generate Rich Text from HTML.
        
        Recursively iterate over HTML tree and perform
        Rich Text operations based on the discovered tags.
        """

        if isinstance(tag, str):
            self.rtc.WriteText(tag)
        else:
            # Line break
            if tag.name == 'br':
                self.rtc.LineBreak()
                return
            # Image
            if tag.name == 'img' and tag.has_attr('src'):
                self.rtc.WriteImage(
                    tag['src'], tag.get('alt', ""),
                    width=tag.get('width'),
                    height=tag.get('height'))
                return
            
            
            # [OPEN TAG CONTEXT]

            # Bold text
            if tag.name == 'strong':
                self.rtc.BeginBold()
            # Italic text
            elif tag.name == 'em':
                self.rtc.BeginItalic()
            # Paragraph
            elif tag.name == 'p':
                self.rtc.BeginParagraph()
            # Blockquote
            elif tag.name == 'blockquote':
                self.rtc.BeginBlockquote()
            # Code
            elif tag.name == 'code':
                self.rtc.BeginCode()
            # Heading 1
            elif tag.name == 'h1':
                self.rtc.BeginHeading1()
            # Heading 2
            elif tag.name == 'h2':
                self.rtc.BeginHeading2()
            # Heading 3
            elif tag.name == 'h3':
                self.rtc.BeginHeading3()
            # Heading 4
            elif tag.name == 'h4':
                self.rtc.BeginHeading4()
            # Heading 5
            elif tag.name == 'h5':
                self.rtc.BeginHeading5()
            # Heading 6
            elif tag.name == 'h6':
                self.rtc.BeginHeading6()
            # Link
            elif tag.name == 'a' and tag.has_attr('href'):
                self.rtc.BeginLink(tag['href'])
            # Unordered list
            elif tag.name == 'ul':
                self.opened_lists.append(tag.name)
                self.rtc.BeginUnorderedList()
            # Ordered list
            elif tag.name == 'ol':
                self.opened_lists.append(tag.name)
                self.rtc.BeginOrderedList()
            # List item
            elif tag.name == 'li':
                if self.opened_lists[-1] == 'ul':
                    self.rtc.BeginUnorderedListItem()
                elif self.opened_lists[-1] == 'ol':
                    self.rtc.BeginOrderedListItem()


            # [RECUR INTO CHILDREN]
            for child in tag.contents:
                self._generate_richtext(child)


            # [CLOSE TAG CONTEXT]

            # Bold text
            if tag.name == 'strong':
                self.rtc.EndBold()
            # Italic text
            elif tag.name == 'em':
                self.rtc.EndItalic()
            # Paragraph
            elif tag.name == 'p':
                self.rtc.EndParagraph()
            # Blockquote
            elif tag.name == 'blockquote':
                self.rtc.EndBlockquote()
            # Code
            elif tag.name == 'code':
                self.rtc.EndCode()
            # Heading 1
            elif tag.name == 'h1':
                self.rtc.EndHeading1()
            # Heading 2
            elif tag.name == 'h2':
                self.rtc.EndHeading2()
            # Heading 3
            elif tag.name == 'h3':
                self.rtc.EndHeading3()
            # Heading 4
            elif tag.name == 'h4':
                self.rtc.EndHeading4()
            # Heading 5
            elif tag.name == 'h5':
                self.rtc.EndHeading5()
            # Heading 6
            elif tag.name == 'h6':
                self.rtc.EndHeading6()
            # Link
            elif tag.name == 'a' and tag.has_attr('href'):
                self.rtc.EndLink()
            # Unordered list
            elif tag.name == 'ul':
                self.rtc.EndUnorderedList()
                self.opened_lists.pop()
            # Ordered list
            elif tag.name == 'ol':
                self.rtc.EndOrderedList()
                self.opened_lists.pop()
            # List item
            elif tag.name == 'li':
                if self.opened_lists[-1] == 'ul':
                    self.rtc.EndUnorderedListItem()
                elif self.opened_lists[-1] == 'ol':
                    self.rtc.EndOrderedListItem()


    def BeginBackgroundColour(self, colour: wx.Colour) -> None:
        """
        Begins background colour.
        """
        highlight_attr = rt.RichTextAttr()
        highlight_attr.SetBackgroundColour(colour)
        self.rtc.BeginStyle(highlight_attr)

    def EndBackgroundColour(self) -> None:
        """
        Ends background colour.
        """
        self.rtc.EndStyle()