#!/usr/bin/env python


import  wx # pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
import wx.html2  # pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
import wx.adv as adv # pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
import wx.lib.statbmp as SB # pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython

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
        
    def setLabel(self, label='tbc'):
        self.label=label
        self.SetLabel(label)
        

class BitmapButton(wx.BitmapButton):
    def __init__(self, parent, id, bitmap, pos=wx.DefaultPosition, size=wx.DefaultSize):
        pic = wx.Bitmap(bitmap, wx.BITMAP_TYPE_ANY)
        wx.BitmapButton.__init__(self, parent, id, pic, pos, size )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        #self.label=label
        self.Bind(wx.EVT_ENTER_WINDOW, self.activate)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.deactivate)
        
    def activate(self, evt=0):
        self.SetBackgroundColour(Colour(50, 90, 1000))
        self.SetForegroundColour(Colour(255, 255, 255))
        #self.SetLabelMarkup(f"<b>{self.label}</b>")
        
    def deactivate(self, evt=0):
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        #self.SetLabelMarkup(self.label)
        

class Colour(wx.Colour):
    def __init__(self, r, g, b, alpha=wx.ALPHA_OPAQUE):
        wx.Colour.__init__(self, r, g, b, alpha)
        

class SpinCtrl(wx.SpinCtrl):
    def __init__(self, parent, id, value, pos, size, style, min,  max, initial):
        wx.SpinCtrl.__init__(self, parent, id, value, pos, size, style, min, max, initial, )
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
               
class TextCtrl(wx.TextCtrl):
    def __init__(self, parent, id, value, pos, size, style, validator=''):
        if validator:
            wx.TextCtrl.__init__(self, parent, id, value, pos, size, style, validator)
        else:
            wx.TextCtrl.__init__(self, parent, id, value, pos, size, style)
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        self.ValidRoutine=self.Validate_Pass
    
    def Validate_Pass(self):
        #Null validation routine.
        return True
    def setValidRoutine(self, routine):
        #Set validation routine.  Must be Validate_Pass, Validate_Not_Empty or Validate_Float.
        self.ValidRoutine=routine
        
    def runValidRoutine(self):
        #Validate field.  Must be Validate_Pass, Validate_Not_Empty or Validate_Float.
        return self.ValidRoutine()
        
    def Validate_Not_Empty(self):
        """ Validate the contents of the given text control, must contain some text. Use setValidRoutine(Validate_Not_Empty)
        """
        text = self.GetValue()

        if len(text) == 0:
            wx.MessageBox("Must contain some text.", "Error")
            self.SetBackgroundColour("White")
            self.SetFocus()
            self.Refresh()
            return False
        else:
            self.SetBackgroundColour(Colour(50, 50, 60))
            self.Refresh()
            return True
            
    def Validate_Float ( self ):
        """ Validate the contents of the given text control. Must be valid float. Use setValidRoutine(Validate_Float)
        """ 
        Text = self.GetValue ()
        #print('here')
        if self.isfloat(Text):
            self.SetBackgroundColour (Colour(50, 50, 60))
            self.Refresh()
            return True
        else :
            wx.MessageBox("Invalid float object.", "Error")
            self.SetBackgroundColour ("White")
            self.SetFocus()
            self.Refresh()
            return False
            
    def isfloat(self, x): 
        try: 
            float(x) 
            return True 
        except: 
            return False
        
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
        #print (f'Notebook label is: "{self.GetLabel()}"')
        #print (f'Notebook value is: "{self.GetValue()}"')

    def GetValue(self):
        return self.GetLabel()

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
        

class CalendarCtrl(wx.adv.CalendarCtrl):
    def __init__(self, parent, date, style):
        wx.adv.CalendarCtrl.__init__(self, parent, wx.ID_ANY, date, pos=wx.DefaultPosition, size=wx.DefaultSize, style=style)
        self.SetDate(date)
        
        
class TimePickerCtrl(adv.TimePickerCtrl):
    def __init__(self, parent, time, pos, size, style):
        adv.TimePickerCtrl.__init__(self, parent, wx.ID_ANY, time, pos=wx.DefaultPosition, size=wx.DefaultSize, style=style)
        self.SetBackgroundColour(Colour(50, 50, 60))
    def GetSecs(self):
        time = self.GetTime()
        seconds=time[2]+60*time[1]+60*60*time[0]
        return seconds
        
    def SetSecs(self, secs):
        secsInHour=int(60*60)
        secsInMinute=int(60)
        hours = int(secs/secsInHour)
        mins = int((secs % secsInHour) / secsInMinute)
        secs = int((secs % secsInHour) % secsInMinute)
        self.SetTime(hours, mins, secs)

class StaticBitmap(SB.GenStaticBitmap):
    #st1 = SB.GenStaticBitmap(panel, -1, bmp, (20, 10))
    
    def __init__(self, parent, id=wx.ID_ANY, bitmap="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.BORDER_NONE, select=False):
        SB.GenStaticBitmap.__init__(self, parent, id, bitmap, pos, size, style );
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        self.c1 = None
        self.c2 = None

    #def OnDrawArea(self, event=0):
        #self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        #self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        #self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseOut)
        #return
        self.c1 = None
        self.c2 = None
        self.parent=parent
        
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        #self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        #self.Bind(wx.EVT_MOTION, self.OnMouseMove)

        self.startPos = None
        self.overlay = wx.Overlay()

    def setBitmap(self, bitmap="", select=False ):
        self.SetBitmap(bitmap)
        
    def OnPaint2(self, evt):
        # Just some simple stuff to paint in the window for an example
        dc = wx.PaintDC(self)
        coords = ((40,40),(200,220),(210,120),(120,300))
        dc.SetBackground(wx.Brush("sky blue"))
        dc.Clear()

        dc.SetPen(wx.Pen("red", 2))
        dc.SetBrush(wx.CYAN_BRUSH)
        dc.DrawPolygon(coords)
        dc.DrawLabel("Draw the mouse across this window to see \n"
                    "a rubber-band effect using wx.Overlay",
                    (140, 50, -1, -1))


    def OnLeftDown(self, evt):
        # Capture the mouse and save the starting posiiton for the
        # rubber-band
        #self.parent.TerminalWrite('LeftDown')
        self.CaptureMouse()
        self.startPos = evt.GetPosition()

    def OnMouseMove2(self, evt):
        if not self.HasCapture():
            return        
        self.endPos=evt.GetPosition()
        self.drawRectangle()
        
    def drawRectangle(self):
        rect = wx.Rect(self.startPos, self.endPos)
        # Draw the rubber-band rectangle using an overlay so it
        # will manage keeping the rectangle and the former window
        # contents separate.
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
            
        pen = wx.Pen("black", 1)
        brush = wx.Brush(Colour(192,192,192,50))
        if "wxMac" in wx.PlatformInfo:
            dc.SetPen(pen)
            dc.SetBrush(brush)
            dc.DrawRectangleRect(rect)
        else:
            # use a GC on Windows (and GTK?)
            # this crashed on the Mac
            ctx = wx.GraphicsContext.Create(dc)
            ctx.SetPen(pen)
            ctx.SetBrush(brush)
            ctx.DrawRectangle(*rect)

        del odc # work around a bug in the Python wrappers to make
                # sure the odc is destroyed before the dc is.

        #self.parent.parent.TerminalWrite(f'Rectangle position = {rect}')
        
    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        #self.startPos = None

        # When the mouse is released we reset the overlay and it
        # restores the former content to the window.
        #dc = wx.ClientDC(self)
        #odc = wx.DCOverlay(self.overlay, dc)
        #odc.Clear()
        #del odc
        #self.overlay.Reset()
    def GetRectCoords(self):
        try:
            self.parent.parent.TerminalWrite([[self.startPos.x, self.startPos.x],[self.endPos.y,self.endPos.y]])
        except Exception:
            return []
        return([[self.startPos.x, self.startPos.x],[self.endPos.y,self.endPos.y]])
    def ResetRectCoords(self):
        self.startPos = None
        self.endPos = None
        return
    def OnRightUp(self, evt):
        self.parent.parent.TerminalWrite([[self.startPos.x, self.startPos.x],[self.endPos.y,self.endPos.y]])
        if self.HasCapture():
            self.ReleaseMouse()
        self.startPos = None
        self.endPos = None

        # When the mouse is released we reset the overlay and it
        # restores the former content to the window.
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        del odc
        self.overlay.Reset()
        
    def OnMouseIn(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        
    def OnMouseOut(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
 
#class Notebook(wx.Notebook):
#    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
#        wx.Notebook.__init__(self, parent, id, pos, size)
#        self.SetBackgroundColour(Colour(50, 50, 60))
#        self.SetForegroundColour(Colour(128, 128, 128)) 
class Panel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.BORDER_NONE):
        wx.Panel.__init__(self, parent, id, pos, size, style );
        self.SetBackgroundColour(Colour(50, 50, 60))
        self.SetForegroundColour(Colour(128, 128, 128))
        self.c1 = None
        self.c2 = None
        self.parent=parent
        
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        #self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        #self.Bind(wx.EVT_MOTION, self.OnMouseMove)

        self.startPos = None
        self.overlay = wx.Overlay()

    def OnPaint2(self, evt):
        # Just some simple stuff to paint in the window for an example
        dc = wx.PaintDC(self)
        coords = ((40,40),(200,220),(210,120),(120,300))
        dc.SetBackground(wx.Brush("sky blue"))
        dc.Clear()

        dc.SetPen(wx.Pen("red", 2))
        dc.SetBrush(wx.CYAN_BRUSH)
        dc.DrawPolygon(coords)
        dc.DrawLabel("Draw the mouse across this window to see \n"
                    "a rubber-band effect using wx.Overlay",
                    (140, 50, -1, -1))


    def OnLeftDown(self, evt):
        # Capture the mouse and save the starting posiiton for the
        # rubber-band
        self.parent.TerminalWrite('LeftDown')
        self.CaptureMouse()
        self.startPos = evt.GetPosition()

    def OnMouseMove2(self, evt):
        if not self.HasCapture():
            return        
        rect = wx.Rect(self.startPos, evt.GetPosition())
        # Draw the rubber-band rectangle using an overlay so it
        # will manage keeping the rectangle and the former window
        # contents separate.
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
            
        pen = wx.Pen("black", 1)
        brush = wx.Brush(Colour(192,192,192,200))
        if "wxMac" in wx.PlatformInfo:
            dc.SetPen(pen)
            dc.SetBrush(brush)
            dc.DrawRectangleRect(rect)
        else:
            # use a GC on Windows (and GTK?)
            # this crashed on the Mac
            ctx = wx.GraphicsContext.Create(dc)
            ctx.SetPen(pen)
            ctx.SetBrush(brush)
            ctx.DrawRectangle(*rect)

        del odc # work around a bug in the Python wrappers to make
                # sure the odc is destroyed before the dc is.


    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        self.startPos = None

        # When the mouse is released we reset the overlay and it
        # restores the former content to the window.
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        del odc
        self.overlay.Reset()
        
    def OnMouseIn(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        
    def OnMouseOut(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        
    #def OnMouseOver(self, event):
    #    if event.Dragging() and event.LeftIsDown():
    #        self.c2 = event.GetPosition()
    #        self.Refresh()
    #
    #def OnMouseMove(self, event):
    #    if event.Dragging() and event.LeftIsDown():
    #        self.c2 = event.GetPosition()
    #        self.Refresh()
    #
    #def OnMouseDown(self, event):
    #    self.c1 = event.GetPosition()
    #
    #def OnMouseUp(self, event):
    #    self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
    #    #self.Destroy()
    #
    #def OnPaint(self, event):
    #    #global selectionOffset, selectionSize
    #    if self.c1 is None or self.c2 is None: return
    #
    #    dc = wx.PaintDC(self)
    #    dc.SetPen(wx.Pen('red', 1))
    #    dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.TRANSPARENT))
    #
    #    dc.DrawRectangle(self.c1.x, self.c1.y, self.c2.x - self.c1.x, self.c2.y - self.c1.y)
    #    #selectionOffset = str(self.c1.x) + "x" + str(self.c1.y)
    #    #selectionSize = str(abs(self.c2.x - self.c1.x)) + "x" + str(abs(self.c2.y - self.c1.y))
    def PrintPosition(self, pos):
        return str(pos.x) + "x" + str(pos.y)

