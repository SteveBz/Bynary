#!/usr/bin/env python


import  wx
import wx.html2
class ListCtrl(wx.ListCtrl):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[] , value='', style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style) #|wx.LC_NO_HEADER
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))

    #def InsertColumn(self, col=0, value='', width=100):
    #    self.InsertColumn(col, value, wx.LIST_FORMAT_LEFT, wx.LIST_AUTOSIZE_USEHEADER )
    #    self.SetColumnWidth(col, width)
        
class Choice(wx.Choice):
    def __init__(self, parent, id, pos, size, choices=[] , value=''):
        
        wx.Choice.__init__(self, parent, id, pos, size, choices)
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        itemCount=0
        for item in choices:
            if item == value:
                self.SetSelection(itemCount)
            itemCount=itemCount+1
            
    def GetValue(self):
        return self.GetString(self.GetSelection())

    def SetValue(self, value):
        itemCount=0
        for item in self.GetStrings():
            if item == value:
                self.SetSelection(itemCount)
            itemCount=itemCount+1

class Button(wx.Button):
    def __init__(self, parent, id, label, pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.Button.__init__(self, parent, id, label, pos, size )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        self.label=label
        self.Bind(wx.EVT_ENTER_WINDOW, self.activate)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.deactivate)
        
    def activate(self, evt=0):
        self.SetBackgroundColour(Colour(50, 90, 1000))
        self.SetForegroundColour(Colour(255, 255, 255))
        self.SetLabelMarkup(f"<b>{self.label}</b>")
        
    def deactivate(self, evt=0):
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        self.SetLabelMarkup(self.label)
        

class Colour(wx.Colour):
    def __init__(self, r, g, b):
        wx.Colour.__init__(self, r, g, b)
        

class SpinCtrl(wx.SpinCtrl):
    def __init__(self, parent, id, value, pos, size, style, min,  max, initial):
        wx.SpinCtrl.__init__(self, parent, id, value, pos, size, style, min, max, initial, )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
               
class TextCtrl(wx.TextCtrl):
    def __init__(self, parent, id, value, pos, size, style):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style)
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
       
class RadioBox(wx.RadioBox):
    def __init__(self, parent, id, label, pos, size, choices, majorDimension, style):
        wx.RadioBox.__init__(self, parent, id, label, pos, size, choices=choices, majorDimension=majorDimension, style=style )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))

    def GetValue(self):
        return self.GetString(self.GetSelection())

class CheckBox(wx.CheckBox):
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.CheckBox.__init__(self, parent, id, label, pos, size )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))


class StaticText(wx.StaticText):
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=''):
        wx.StaticText.__init__(self, parent, id, label, pos, size )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))


class Notebook(wx.Notebook):
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=''):
        wx.Notebook.__init__(self, parent)
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))


class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title="About <<project>>",
        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, id=wx.ID_ANY, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()
        
        