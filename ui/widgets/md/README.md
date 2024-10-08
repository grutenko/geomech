# wxMarkdown

**wxMarkdown** makes adding panels of formatted text much easier!
In stead of having to open and close each context yourself with a `RichTextCtrl`,
enter what you want in Markdown and see it appear with the right styling.

## Table of contents

- [Example](#example)
- [Feature support](#feature-support)
- [To-Do](#to-do)

## Example

It's straight-forward. You initialise the Markdown panel as you would any other panel. You add Markdown content to it with `AddContent`. That's it. Embed it how you'd like.

```py
import wx
import wxmarkdown as wxm

app = wx.App()
frame = wx.Frame(None)

md = wxm.Markdown(frame)
md.AddContent("""
# A Very Simple Example
This example doesn't showcase _all supported syntax_.
It's just meant to showcase **how to use the package**.
""")

frame.Show()
app.MainLoop()
```

## Feature support

All basic Markdown syntax is supported. The package currently uses [`Markdown`](https://pypi.org/project/Markdown/) for parsing.

- Italic text
- Bold text
- Inline code
- Heading
- Unordered list
- Ordered list
- Link
- Image
- Blockquote
- ~~Horizontal rule~~

You can enable the embedding of external images by setting `allow_download_images` to `True`.

## To-Do

_Some of these features are likely not yet implemented solely because I haven't been able to figure out `wxPython`'s Rich Text modules fully. If you understand how the package works and know a solution for either of these todos, I would greatly appreciate if you'd get in contact with me._

- **Linkable images**: This could be implemented by binding a function to the click of an image. However, I cannot get this to work within the context of a `RichTextCtrl`.
- **Link hover effect**: Change appearance of a link upon hovering over it.
- **Horizontal Rule**: A horizontal divider
- Improve default theme
