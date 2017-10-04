#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import wx
import time
from git_status import check_status

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

REPOSITORY_PATH = config.get('main', 'repository_path')
REPEAT_EVERY = config.getfloat('main', 'repeat_every')


class Icon(wx.TaskBarIcon):
    """notifier's taskbar icon"""

    def __init__(self, menu):

        wx.TaskBarIcon.__init__(self)

        # menu options
        self.menu = menu

        # event handlers
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.click)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.click)
        self.Bind(wx.EVT_MENU, self.select)

        # icon state
        self.states = {
            "on": wx.Icon("dat/reader_new.png", wx.BITMAP_TYPE_PNG),
            "off": wx.Icon("dat/reader_empty.png", wx.BITMAP_TYPE_PNG)
        }
        self.setStatus("off")

    def click(self, event):
        """shows the menu"""

        menu = wx.Menu()
        for id, item in enumerate(self.menu):
            menu.Append(id, item[0])
        self.PopupMenu(menu)

    def select(self, event):
        """handles menu item selection"""

        self.menu[event.GetId()][1]()

    def setStatus(self, which):
        """sets the icon status"""

        self.SetIcon(self.states[which])
    
    def run_method(method):
        return locals()['%s' % method]()

    def close(self):
        """destroys the icon"""

        self.Destroy()


class Popup(wx.Frame):
    """notifier's popup window"""

    def __init__(self):

        wx.Frame.__init__(self, None, -1, style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR)
        self.padding = 12  # padding between edge, icon and text
        self.popped = 3  # the time popup was opened
        self.delay = 10  # time to leave the popup opened
        self.width = 400

        # platform specific hacks
        self.lineHeight = wx.MemoryDC().GetTextExtent(" ")[1]
        if wx.Platform == "__WXGTK__":
            # use the popup window widget on gtk as the
            # frame widget can't animate outside the screen
            self.popup = wx.PopupWindow(self, -1)
        elif wx.Platform == "__WXMSW__":
            # decrement line height on windows as the text calc below is off otherwise
            self.popup = self
            self.lineHeight -= 3
        elif wx.Platform == "__WXMAC__":
            # untested
            self.popup = self

        # main timer routine
        self.logo = wx.Bitmap("dat/reader_large.png")
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.main, self.timer)
        self.timer.Start(500)

    def adopt_size(self, text):
        lines = len(text.split("\n"))
        self.popup.SetSize((self.width, (self.lineHeight * (lines + 1)) + (self.padding * 2)))
        self.panel = wx.Panel(self.popup, -1, size=self.popup.GetSize())
        # popup's click handler
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.click)

        # popup's logo
        wx.StaticBitmap(self.panel, -1, pos=(self.padding, self.padding)).SetBitmap(self.logo)

    def main(self, event):

        if self.focused():
            # maintain opened state if focused
            self.popped = time.time()
        elif self.opened() and self.popped + self.delay < time.time():
            # hide the popup once delay is reached
            self.hide()

    def click(self, event):
        """handles popup click"""

        self.popped = 0
        self.hide()

    def show(self, text):
        """shows the popup"""

        self.adopt_size(text)
        # create new text
        if hasattr(self, "text"):
            self.text.Destroy()
        popupSize = self.popup.GetSize()
        logoSize = self.logo.GetSize()
        self.text = wx.StaticText(self.panel, -1)
        self.text.SetLabel(text)
        self.text.Bind(wx.EVT_LEFT_DOWN, self.click)
        self.text.Move((logoSize.width + (self.padding * 2), self.padding))
        self.text.SetSize((
            popupSize.width - logoSize.width - (self.padding * 3),
            popupSize.height - (self.padding * 2)
        ))

        # animate the popup
        screen = wx.GetClientDisplayRect()
        self.popup.Show()
        for i in range(1, popupSize.height + 1):
            self.popup.Move((screen.width - popupSize.width, screen.height - i))
            self.popup.Update()
            self.popup.Refresh()
        self.popped = time.time()

    def hide(self):
        """hides the popup"""

        self.popup.Hide()
        self.popped = 0

    def focused(self):
        """returns true if popup has mouse focus"""

        mouse = wx.GetMousePosition()
        popup = self.popup.GetScreenRect()
        return (
            self.popped and
            mouse.x in range(popup.x, popup.x + popup.width)
            and mouse.y in range(popup.y, popup.y + popup.height)
        )

    def opened(self):
        """returns true if popup is open"""

        return self.popped != 0


class Notifier(wx.App):
    """main notifier app"""

    def __init__(self):

        wx.App.__init__(self, redirect=0)

        # menu handlers
        menu = [
            ("Show again", self.open_popup),
            ("Exit", self.exit),
        ]

        # main objects
        self.icon = Icon(menu)
        self.popup = Popup()
        # main timer routine
        timer = wx.Timer(self, -1)
        self.open_popup()
        self.Bind(wx.EVT_TIMER, self.main, timer)
        timer.Start(REPEAT_EVERY * 60000)
        self.MainLoop()

    def main(self, event):
        self.open_popup()

    def open_popup(self):
        wrap_text = lambda text, wrap_char: "%s\n%s\n\n" % (text, wrap_char * len(text))
        status = "off"
        message_str = ''
        for git_repo_path in REPOSITORY_PATH.split(','):
            result = check_status(git_repo_path)
            if result:
                message_str += wrap_text(git_repo_path, '=')
                for module, message in result.items():
                    message_str += "%s\n" % module
                    for k, v in message.items():
                        message_str += "\t%s\t%s\n\n" % (k, v)
                    status = "on"
        if message_str:
            self.popup.show(message_str)
        self.icon.setStatus(status)

    def exit(self):
        # close objects and end
        self.icon.close()
        self.Exit()

notifier = Notifier()
