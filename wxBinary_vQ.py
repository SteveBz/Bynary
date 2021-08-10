#!/usr/bin/env python

import os
import time
#import  wx.lib.scrolledpanel as scrolled

import wx.html2 # pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
import pandas as pd
import ashla.data_access as da
import sys, inspect, math

import datetime
#Matplotlib
from numpy import arange, sin, pi # pip3 install numpy
import numpy as np
import matplotlib # pip3 install matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib import animation
from matplotlib.artist import Artist
import matplotlib.ticker as ticker
import csv
import pickle
from wxPyControls import *
from PyBins import *
from starSystems import *
from newtonian_values import xdata2, ydata2, ydata2_1D

import configVar

from matplotlib.ticker import (MultipleLocator, NullFormatter, ScalarFormatter, AutoMinorLocator, FormatStrFormatter)

gl_cfg=configVar.configVar("/home/image/x-Stronomy/binClient.conf")
ROWCOUNTMATRIX={
    'ADQL':0,
    'UN':0,
    'BIN2':0,
    'UN':0,
    'R0':0,
    'V0':0,
    'RVFILTER':0,
    'PXFILTER':0,
    'PMFILTER':0,
    'BIN':0
}
RELEASE='eDR3'
CATALOG='KEB5E5-1pc'
FONTSIZE=20
#Cancel command for import button
CANCEL=False 
import SQLLib
import db              # For star/observing database.
dbiStro=db.db()
database = gl_cfg.getItem('database','SETTINGS')
databaseid = gl_cfg.getItem('databaseuserid','SETTINGS')
databasepwd = gl_cfg.getItem('databasepwd','SETTINGS')
iStro=dbiStro.conFbdb(database, databaseid, databasepwd)  # chmod +777 Binaries-DB-30.fdb 
        
class MainPanel(wx.Panel):
    def __init__(self, mainFrame):
        wx.Panel.__init__(self, mainFrame)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Menu & Status bar ###########################################################
        menuBar = wx.MenuBar()
        menuBar.SetBackgroundColour(Colour(50, 50, 60))
        menuBar.SetForegroundColour(Colour(128, 128, 128))
        menuFile = wx.Menu()
        
        m_exit = menuFile.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menuFile, "&File")
        
        menuAbout = wx.Menu()
        m_about = menuAbout.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menuAbout, "&Help")
        mainFrame.SetMenuBar(menuBar)
        
        mainFrame.SetMenuBar(menuBar)
        mainFrame.statusbar = mainFrame.CreateStatusBar()
        t=time.strftime("%Y/%m/%d/ %H:%M:%S")
        mainFrame.statusbar.SetStatusText(t)
        mainFrame.statusbar.SetBackgroundColour(Colour(50, 50, 60)) #Grey
        
        self.sizer_nb=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_nb)
        self.nb=Notebook(self)
        self.sizer_nb.Add(self.nb, 1, wx.ALL|wx.EXPAND, 5)

        self.nb.printArrays=self.printArrays
        # Here we create a panel and a notebook on the panel
        self.releasePage = gaiaStarRetrieval(self.nb, self)
        self.catalogPage = gaiaBinaryRetrieval(self.nb, self)
        self.retrievalPage = dataRetrieval(self.nb, self)
        self.filterPage = dataFilter(self.nb)
        self.plottingPage = kineticDataPlotting(self.nb, self)
        self.skyPage = skyDataPlotting(self.nb, self)
        self.hrPage = HRDataPlotting(self.nb, self)
        self.TulleyFisherPage = TFDataPlotting(self.nb, self)
        self.AladinPage = AladinView(self.nb, self)
        
#        #
#        ## add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.releasePage, "Download stars and attributes")
        self.nb.AddPage(self.catalogPage, "Download binary catalogue")
        self.nb.AddPage(self.retrievalPage, "Binary catalogue")
        self.nb.AddPage(self.filterPage, "Binary filters")
        self.nb.AddPage(self.skyPage, "Sky density plot")
        self.nb.AddPage(self.hrPage, "H-R plot")
        self.nb.AddPage(self.plottingPage, "Kinematic plot")
        self.nb.AddPage(self.TulleyFisherPage, "Velocity vs Mass plot")
        self.nb.AddPage(self.AladinPage, "View Binaries in Aladin Lite")
        self.nb.SetSelection(int(gl_cfg.getItem('tab','SETTINGS'))) # get setting from config file)
        
    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnClose(self, event):
        print('Closing message')
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            dlg.Destroy()
            exit()
        else:
            dlg.Destroy()
            
    def printArrays(self):
        
        return
    
        try:
            print(f'length of "selectedStarIDs" = {len(self.nb.selectedStarIDs)}')
        except Exception:
            print(f'"selectedStarIDs" not found')
        try:
            print(f'length of "selectedStarBinaryMappings" = {len(self.nb.selectedStarBinaryMappings)}')
        except Exception:
            print(f'"selectedStarBinaryMappings" not found')
        try:
            print(f'length of "star_rows" = {len(self.nb.star_rows)}')
        except Exception:
            print(f'"star_rows" not found')
        try:
            print(f'length of "status" = {len(self.nb.status)}')
            print(f'- sum of include = {self.nb.status["include"].sum()}')
            print(f'- sum of notgroup = {self.nb.status["notgroup"].sum()}')
            print(f'- sum of radialvelocity = {self.nb.status["radialvelocity"].sum()}')
            print(f'- sum of dataLoadOut = {self.nb.status["dataLoadOut"].sum()}')
            print(f'- sum of populateOut = {self.nb.status["populateOut"].sum()}')
            print(f'- sum of hrOut = {self.nb.status["hrOut"].sum()}')
            print(f'- sum of kineticOut = {self.nb.status["kineticOut"].sum()}')
            print(f'- sum of ruweExcl = {self.nb.status["ruweExcl"].sum()}')
        except Exception:
            print(f'Not all "status" columns found')
        try:
            print(f'length of "binaryDetail" = {len(self.nb.binaryDetail)}')
        except Exception:
            print(f'"binaryDetail" not found')
        try:
            print(f'length of "X" = {len(self.nb.X)}')
        except Exception:
            print(f'"X" not found')
        try:
            print(f'length of "Y" = {len(self.nb.Y)}')
        except Exception:
            print(f'"Y" not found')
            

class gaiaStarRetrieval(wx.Panel):
    
    def dump(self, obj):
      for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'
        #
        self.sizer_main_divider=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main=wx.BoxSizer(wx.VERTICAL)
        self.sizer_main_divider.Add(self.sizer_main)
        #self.sizer_h=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_h=wx.FlexGridSizer(cols=8)
        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.sizer_v2=wx.BoxSizer(wx.VERTICAL)
        self.sizer_h2=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.sizer_h)
        self.sizer_main.Add(self.sizer_v)
        self.sizer_main.Add(self.sizer_h2)
        self.sizer_main_divider.Add(self.sizer_v2)
        
        # Select release
        static_Release = StaticText(self, id=wx.ID_ANY, label="Release (eDR3):")
        self.sizer_h.Add(static_Release, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Release select
        self.release = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        releases=self.releaseRefresh()
        #self.release.Bind(wx.EVT_CHOICE, self.catRefresh)
        self.release.SetSelection(int(gl_cfg.getItem('release','GAIASTAR')))
        self.release.SetToolTip("Select release source (currently only eDR3)")
        self.sizer_h.Add(self.release, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        global RELEASE
        RELEASE = self.release.GetValue()
        
        self.textctrl_newRelease = TextCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.sizer_h.Add(self.textctrl_newRelease, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_newRelease.SetToolTip("Enter new release name.")
        
        self.buttonRelease = Button(self, wx.ID_ANY, u"New release")
        self.buttonRelease.SetToolTip("Enter name of new release (5 chars).")
        self.buttonRelease.Bind(wx.EVT_LEFT_DOWN, self.addRelease)
        self.sizer_h.Add(self.buttonRelease, 0,wx.ALIGN_LEFT|wx.ALL , 5)

        # Select RA from (degrees)
        static_RAfrom = StaticText(self, id=wx.ID_ANY, label="RA from (Deg):")
        self.sizer_h.Add(static_RAfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_RAfrom = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rafrom','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=360,initial=int(gl_cfg.getItem('rafrom', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_RAfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_RAfrom.SetToolTip("Lower RA to download - 0 to 360")
        
        # Select RA to (degrees)
        static_RAto = StaticText(self, id=wx.ID_ANY, label="RA to (Deg):")
        self.sizer_h.Add(static_RAto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_RAto = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rato','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=360,initial=int(gl_cfg.getItem('rato', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_RAto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_RAto.SetToolTip("Upper RA to download to - out of 360")
        
        # Select Px from (mas)
        static_PXfrom = StaticText(self, id=wx.ID_ANY, label="Px from (mas):")
        self.sizer_h.Add(static_PXfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXfrom = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxfrom','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxfrom', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_PXfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXfrom.SetToolTip("Lower Parallax to download - 0 to 1000 (expectation is '3')")
        
        # Select Px to (degrees)
        static_PXto = StaticText(self, id=wx.ID_ANY, label="Px to (mas):")
        self.sizer_h.Add(static_PXto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXto = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxto','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxto', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_PXto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXto.SetToolTip("Upper Parallax to download to - out of 1000 (expectation is '1000')")
        
                #and parallax_over_error > 5
                #and phot_g_mean_flux_over_error > 50
                #and phot_rp_mean_flux_over_error > 10
                #and phot_bp_mean_flux_over_error > 10
        # Select parallax_over_error
        static_Px_err = StaticText(self, id=wx.ID_ANY, label="Px/err:")
        self.sizer_h.Add(static_Px_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Px_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('px_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('px_err', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_Px_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Px_err.SetToolTip("parallax_over_error to download - 0 to 100 (expectation is '5')")
        
        # Select phot_g_mean_flux_over_error
        static_G_err = StaticText(self, id=wx.ID_ANY, label="G/err:")
        self.sizer_h.Add(static_G_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_G_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('g_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('g_err', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_G_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_G_err.SetToolTip("phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50')")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err = StaticText(self, id=wx.ID_ANY, label="Rp/err:")
        self.sizer_h.Add(static_Rp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_Rp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err.SetToolTip("phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err = StaticText(self, id=wx.ID_ANY, label="Bp/err:")
        self.sizer_h.Add(static_Bp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_Bp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Bp_err.SetToolTip("phot_bp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        self.sizer_h.AddSpacer(1)
        self.sizer_h.AddSpacer(1)
        self.sizer_h.AddSpacer(1)
        self.sizer_h.AddSpacer(1)
        
        # Create download only data check box
        downloadOnlyStaticText = StaticText(self, id=wx.ID_ANY, label="Download only?")
        self.sizer_h.Add(downloadOnlyStaticText, 0, wx.ALL, 2)
        self.downloadOnlyCheckBox = CheckBox(self)
        self.downloadOnlyCheckBox.SetToolTip("Speed up download by only downloading and saving pandas files to disc.  Ie not saving to database.")
        self.downloadOnlyCheckBox.SetValue(gl_cfg.getBoolean('downloadonly', 'GAIASTAR'))
        self.sizer_h.Add(self.downloadOnlyCheckBox, 0, wx.ALL, 2)
        
        # Create force redownload data check box
        forceDownloadStaticText = StaticText(self, id=wx.ID_ANY, label="Force redownload?")
        self.sizer_h.Add(forceDownloadStaticText, 0, wx.ALL, 2)
        self.forceDownloadCheckBox = CheckBox(self)
        self.forceDownloadCheckBox.SetToolTip("Force re-download of files from Gaia.  This overwrites local values.")
        self.forceDownloadCheckBox.SetValue(gl_cfg.getBoolean('forceredownload', 'GAIASTAR'))
        self.sizer_h.Add(self.forceDownloadCheckBox, 0, wx.ALL, 2)
        
        # Create 'deactivate indices' check box to speed up data inserts.
        deactivateIndicesStaticText = StaticText(self, id=wx.ID_ANY, label="Deactivate indices?")
        self.sizer_h.Add(deactivateIndicesStaticText, 0, wx.ALL, 2)
        self.deactivateIndicesCheckBox = CheckBox(self)
        self.deactivateIndicesCheckBox.SetToolTip("Deactivate indices to speed up DB inserts.  Speeds up large changes.  ")
        self.deactivateIndicesCheckBox.SetValue(gl_cfg.getBoolean('deactivateindices', 'GAIASTAR'))
        self.sizer_h.Add(self.deactivateIndicesCheckBox, 0, wx.ALL, 2)
        
        self.SetSizer(self.sizer_main_divider)
                        
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(565,600), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
        self.listctrl.InsertColumn(0, u"Release", wx.LIST_FORMAT_CENTER,  width=100)
        self.listctrl.InsertColumn(1, u"RA from", wx.LIST_FORMAT_RIGHT, width=100)
        self.listctrl.InsertColumn(2, u"RA to", wx.LIST_FORMAT_RIGHT, width=100)
        self.listctrl.InsertColumn(3, u"Star count", wx.LIST_FORMAT_CENTER,  width=100)
        self.listctrl.InsertColumn(4, u"Date time", wx.LIST_FORMAT_CENTER,  width=160)
        #
        #self.restoreListCtrl()
        
        self.sizer_v.Add(self.listctrl, 0, wx.TOP | wx.BOTTOM , 10)
        
        # Import Total prompt
        
        static_Total = StaticText(self, id=wx.ID_ANY, label="Total stars:")
        self.sizer_h2.Add(static_Total, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Total
        
        self.static_Total = StaticText(self, id=wx.ID_ANY, label='n/a')
        self.sizer_h2.Add(self.static_Total, 0, wx.ALL, 5)
        
        # Loading data
        
        static_DataLoad = StaticText(self, id=wx.ID_ANY, label="Data save/load:")
        self.sizer_v2.Add(static_DataLoad, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.button1 = Button(self, wx.ID_ANY, u"Star Load")
        self.button1.SetToolTip("Import selected stars from Gaia.")
        self.button1.Bind(wx.EVT_LEFT_DOWN, self.read_GaiaStars)
        self.sizer_v2.Add(self.button1, 0,wx.ALIGN_LEFT|wx.ALL , 5)
        
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel import or status update.")
        self.sizer_v2.Add(self.button2, 0, wx.LEFT | wx.RIGHT , 5)
        
        self.deleteSelection = Button(self, id=wx.ID_ANY, label="Delete", pos=wx.DefaultPosition,size=wx.DefaultSize)
        #self.deleteSelection.Bind(wx.EVT_BUTTON, self.OnDeleteSelection)
        self.deleteSelection.SetToolTip("Delete bineries with that combination of 'release', 'catalogue', and 'healpix/RA/dec'")
        self.sizer_v2.Add(self.deleteSelection, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
    def OnCancel(self, event=0):
    
        global CANCEL
        CANCEL= True
    #    
    #    
    def releaseRefresh(self, event=0):
        
        global RELEASE
        #RELEASE = self.release.GetValue()
        TBL_RELEASE = SQLLib.sqlSelect(iStro, "TBL_RELEASE")
        #TBL_RELEASE.setWhereValueString("RELEASE_", RELEASE)
        TBL_RELEASE.setReturnCol("RELEASE_")
        TBL_RELEASE.setSortCol("RELEASE_",1) # -ve is desc, +ve is ascending
        records = TBL_RELEASE.selectRecordSet()
        self.releases=[]
        
        for release in records.itermap():
            self.releases.append(release['RELEASE_'])
        #
        self.release.Clear()
        self.release.SetItems(self.releases)
        #
        #gl_cfg.getItem('release', 'GAIASTAR') # Get setting in config file
        self.release.SetSelection(int(gl_cfg.getItem('release', 'GAIASTAR'))) # Get setting from config file
        return self.releases
    def addRelease(self, event=0):
        
        global RELEASE
        TBL_RELEASE = SQLLib.sqlInsert(iStro, "TBL_RELEASE")
        release=self.textctrl_newRelease.GetValue()
        if len(release)>0 and  len(release)<5:
            TBL_RELEASE .setAttributeString("RELEASE_", release)
            self.textctrl_newRelease.SetValue('')
        records = TBL_RELEASE.insertRecord()
        self.releaseRefresh()
        
    #    
    def read_GaiaStars(self, event):
    
        self.button1.Disable()
        self.listctrl.DeleteAllItems()
        
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('rafrom',self.spin_RAfrom.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('rato',self.spin_RAto.GetValue(), 'GAIASTAR') # save setting in config file
        
        gl_cfg.setItem('pxto',self.spin_PXto.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('pxfrom',self.spin_PXfrom.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('rp_err',self.spin_Rp_err.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('bp_err',self.spin_Bp_err.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('px_err',self.spin_Px_err.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('g_err',self.spin_G_err.GetValue(), 'GAIASTAR') # save setting in config file
        
        gl_cfg.setItem('downloadonly',self.downloadOnlyCheckBox.GetValue(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('forceredownload', bool(self.forceDownloadCheckBox.GetValue()), 'GAIASTAR') # save notebook tab setting in config file
        gl_cfg.setItem('deactivateindices',bool(self.deactivateIndicesCheckBox.GetValue()), 'GAIASTAR') # save notebook tab setting in config file
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        query=[0]
        
        selectFrom = """SELECT
            distinct gaia_source.source_id,
            gaia_source.ra,
            gaia_source.ra_error,
            gaia_source.dec,
            gaia_source.dec_error,
            gaia_source.parallax,
            gaia_source.parallax_error,
            gaia_source.phot_g_mean_mag,
            gaia_source.bp_rp,
            gaia_source.dr2_radial_velocity,
            gaia_source.dr2_radial_velocity_error,
            --gaia_source.phot_variable_flag,
            --gaia_source.teff_val,
            --gaia_source.a_g_val, 
            gaia_source.pmra,
            gaia_source.pmra_error, 
            gaia_source.pmdec,
            gaia_source.ruwe,
            gaia_source.pmdec_error
        
            FROM gaiaedr3.gaia_source
        """
        
        count=0
        step = 1
        lowerRA=self.spin_RAfrom.GetValue()
        upperRA=self.spin_RAto.GetValue()
        forceIt=self.forceDownloadCheckBox.GetValue()
        release=self.release.GetValue()
        TotalCount=0
        #forceDownload=self.forceDownloadCheckBox.GetValue()
        downloadOnly=self.downloadOnlyCheckBox.GetValue()
        
        #ALTER INDEX IDX_TBL_OBJECTS1 INACTIVE
        #ALTER INDEX IDX_TBL_OBJECTS2 INACTIVE
        #ALTER INDEX IDX_TBL_OBJECTS3 INACTIVE
        #ALTER INDEX IDX_TBL_OBJECTS4 INACTIVE
            
        if self.deactivateIndicesCheckBox.GetValue():
            #Deactivate 4 indices on TBL_OBJECTS
            TBL_OBJECTS  = SQLLib.sql(iStro, "TBL_OBJECTS ")
            #ALTER INDEX IDX_TBL_BINARIES1 to 9 INACTIVE
            for idx in range(1,5):
                bulkSQL=f"ALTER INDEX IDX_TBL_OBJECTS{idx} INACTIVE ;"
                TBL_OBJECTS .executeIAD(bulkSQL)
                print(bulkSQL)
                
        for i in range(lowerRA, upperRA, step):
            query[0] = selectFrom + f"""
            -- RA {i} to {i+step}
            WHERE gaia_source.ra >= {i} and gaia_source.ra < {i+step}
            --    source_id in (3242763706493692544, 3242763706493692288)
                and parallax >= {self.spin_PXfrom.GetValue()}
                and parallax < {self.spin_PXto.GetValue()}
                and parallax_over_error > {self.spin_Px_err.GetValue()}
                and phot_g_mean_flux_over_error > {self.spin_G_err.GetValue()}
                and phot_rp_mean_flux_over_error > {self.spin_Rp_err.GetValue()}
                and phot_bp_mean_flux_over_error > {self.spin_Bp_err.GetValue()}
            """
            
            #print( query[0] )
            print (f'i = {i}')
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            #filePrefix='iEquals0' + date_time
            print('start query', date_time)
            # output_data = gaia_cnxn.gaia_get_pairs_of_close_stars(save_to_pickle=True, dump_to_file=True, output_format='json')
            
            if not os.path.isdir(f'bindata/{release}'):
                os.mkdir (f'bindata/{release}')
            if not os.path.isdir(f'bindata/{release}/stars'):
                os.mkdir (f'bindata/{release}/stars')
                
            if (not forceIt) and os.path.isfile(f'bindata/{release}/stars/gaia_{release}_RA{i}'):
                data =pd.read_pickle(f'bindata/{release}/stars/gaia_{release}_RA{i}')
                print(f'Restore from local pickle file')
            else:
                gaia_cnxn = da.GaiaDataAccess()
                data = gaia_cnxn.gaia_query_to_pandas(query[0])
                print(f'Download from Gaia')
                data.to_pickle(f'bindata/{release}/stars/gaia_{release}_RA{i}')
                
            #gaia_cnxn = da.GaiaDataAccess()
            #data = gaia_cnxn.gaia_query_to_pandas(query[0])
            #data.set_option('display.max_colwidth', None)
            #print (downloadOnly)
            lenArray=len(data)
            self.listctrl.Append([release,i, i+step, lenArray, date_time])
            self.listctrl.EnsureVisible(i-lowerRA)
            self.Layout()
            wx.Yield()
            TotalCount=TotalCount+lenArray
            self.static_Total.SetLabel(f'{TotalCount:,}')
            if downloadOnly:
                continue
            print(f'delete old records for RA {i} to {i+1} degrees')
            TBL_OBJECTS = SQLLib.sqlDelete(iStro, "TBL_OBJECTS")
            TBL_OBJECTS.setWhereValueLTFloat('RA_', i+1)
            TBL_OBJECTS.setWhereValueGEFloat('RA_', i)
            TBL_OBJECTS.setWhereValueString('RELEASE_', release)
            TBL_OBJECTS.deleteRecordSet()
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            #filePrefix='iEquals0' + date_time
            print(f'start processing {len(data)} records at {date_time}.' )
            bulkSQL='execute block as begin'
            source_id_array=[]
            data2=data.to_dict()
            #print(data)
            print(f'Number of stars: {len(data)} in {TotalCount}')
            
            #for record in data2:  #.iterrows():
            #for record in data2:  #.iterrows():
            for index in range(len(data)):
                count=count+1
                #if record.source_id in source_id_array:
                #    continue
                #else:
                #    source_id_array.append(int(record.source_id))
                #print('record = ', record)
                TBL_GAIA_eDR3  = SQLLib.sqlInsert(iStro, "TBL_objects ")
                #print(index)
                #print(data2['source_id'][index])
                TBL_GAIA_eDR3 .setAttributeInteger("source_id", data2['source_id'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("ra_", data2['ra'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("ra_error", data2['ra_error'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("dec_", data2['dec'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("dec_error", data2['dec_error'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("parallax", data2['parallax'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("parallax_error", data2['parallax_error'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("phot_g_mean_mag", data2['phot_g_mean_mag'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("bp_rp", data2['bp_rp'][index])
                if data2['dr2_radial_velocity'][index] and not math.isnan(data2['dr2_radial_velocity'][index]):
                    TBL_GAIA_eDR3 .setAttributeFloat("radial_velocity", data2['dr2_radial_velocity'][index])
                if data2['dr2_radial_velocity_error'][index] and not math.isnan(data2['dr2_radial_velocity_error'][index]):
                    TBL_GAIA_eDR3 .setAttributeFloat("radial_velocity_error", data2['dr2_radial_velocity_error'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("pmra", data2['pmra'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("pmra_error", data2['pmra_error'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("pmdec", data2['pmdec'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("pmdec_error", data2['pmdec_error'][index])
                TBL_GAIA_eDR3 .setAttributeFloat("ruwe", data2['ruwe'][index])
                TBL_GAIA_eDR3 .setAttributeString("release_", release)
                #print (count)
                #print (count % 20)
                if index % 20:
                    bulkSQL = bulkSQL + """
                    """ + TBL_GAIA_eDR3 .getInsertSQL() + " "
                else:
                    bulkSQL = bulkSQL + """
                    """ + TBL_GAIA_eDR3 .getInsertSQL() + """
                    end"""
                    #now = datetime.datetime.utcnow() # current date and time
                    #date_time = now.strftime("%Y%m%d_%H%M%S")
                    #print("1) SQL = ", bulkSQL)
                    TBL_GAIA_eDR3 .executeIAD(bulkSQL)
                    
                    label=float(100 * index /lenArray)
                    #self.button1.SetLabel(f'{i+1}th {label:,.1f}%')
                    self.button1.SetLabel(f'{i}/{upperRA-1}-{label}%')
                    global CANCEL
                    if CANCEL:
                        CANCEL = False
                        #Release button
                        self.button1.Enable()
                        return
                    wx.Yield()
                    
                    TBL_GAIA_eDR3  = SQLLib.sqlInsert(iStro, "TBL_objects ")
                    bulkSQL='execute block as begin'
            
            if bulkSQL != 'execute block as begin':
                bulkSQL = bulkSQL + '  end'
                #print("2) SQL = ", bulkSQL)
                TBL_GAIA_eDR3 .executeIAD(bulkSQL)
                
            self.Layout()
            wx.Yield()
            
            bulkSQL=''
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            #print("RA_ = ", data2['ra'][index], index, 'update', date_time)
        
        print(2)

        if self.deactivateIndicesCheckBox.GetValue():
            #ALTER INDEX IDX_TBL_OBJECTS1 ACTIVE
            #ALTER INDEX IDX_TBL_OBJECTS2 ACTIVE
            #ALTER INDEX IDX_TBL_OBJECTS3 ACTIVE
            #ALTER INDEX IDX_TBL_OBJECTS4 ACTIVE
            #Deactivate 4 indices on TBL_OBJECTS
            TBL_OBJECTS  = SQLLib.sql(iStro, "TBL_OBJECTS ")
            #ALTER INDEX IDX_TBL_BINARIES1 to 9 INACTIVE
            for idx in range(1,5):
                bulkSQL=f"ALTER INDEX IDX_TBL_OBJECTS{idx} ACTIVE ;"
                TBL_OBJECTS .executeIAD(bulkSQL)
                print(bulkSQL)
                
        self.button1.Enable()
        print(7)
        
class gaiaBinaryRetrieval(wx.Panel):
    
    def dump(self, obj):
      for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'
        
        #Try to find existing files, if not, create blank one
        files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','star_rows','X','Y','status','export']
        for file in files:
            try:
                setattr(self.parent,file, pd.read_pickle('bindata/'+file+'.saved'))
            except Exception:
                setattr(self.parent,file, pd.DataFrame())

        try:
            file_to_read = open('bindata/starSystemList.pickle', 'rb') #File containing example object
            self.parent.starSystemList = pickle.load(file_to_read) # Load saved object
            file_to_read.close()
        except Exception:
            self.parent.starSystemList=binaryStarSystems(len(self.parent.status))
        
        self.sizer_main_divider=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main=wx.BoxSizer(wx.VERTICAL)
        self.sizer_main_divider.Add(self.sizer_main)
        self.sizer_h=wx.FlexGridSizer(cols=6)
        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.sizer_v2=wx.BoxSizer(wx.VERTICAL)
        self.sizer_h2=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.sizer_h)
        self.sizer_main.Add(self.sizer_v)
        self.sizer_main.Add(self.sizer_h2)
        self.sizer_main_divider.Add(self.sizer_v2)
        
        # Select release
        
        static_Release = StaticText(self, id=wx.ID_ANY, label="Release:")
        self.sizer_h.Add(static_Release, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Release select
        self.release = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        releases=self.releaseRefresh()
        self.release.Bind(wx.EVT_CHOICE, self.catRefresh)
        self.release.SetSelection(int(gl_cfg.getItem('release','GAIABINARY')))
        self.release.SetToolTip("Select release source")
        self.sizer_h.Add(self.release, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        global RELEASE
        RELEASE = self.release.GetValue()
        
        # Catalogue prompt
        static_Catalogue = StaticText(self, id=wx.ID_ANY, label="Catalogue:")
        self.sizer_h.Add(static_Catalogue, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.catalogue = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(110,-1), choices=[], value='')
        self.catalogue.SetToolTip("Select Catalogue")
        self.catRefresh()
        self.catalogue.SetSelection(int(gl_cfg.getItem('catalog', 'GAIABINARY')))
        self.sizer_h.Add(self.catalogue, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        global CATALOG
        CATALOG = self.catalogue.GetValue()
        
        self.textctrl_newCatalog = TextCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.sizer_h.Add(self.textctrl_newCatalog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_newCatalog.SetToolTip("Enter new catalogue name.")
        
        self.buttonCatalogue = Button(self, wx.ID_ANY, u"New catalogue")
        self.buttonCatalogue.SetToolTip("Enter name of new catalogue (10 chars).")
        self.buttonCatalogue.Bind(wx.EVT_LEFT_DOWN, self.addCatalogue)
        self.sizer_h.Add(self.buttonCatalogue, 0,wx.ALIGN_LEFT|wx.ALL , 5)
        # Load Catalogue
        
        static_Separation = StaticText(self, id=wx.ID_ANY, label="Separation (pc):")
        self.sizer_h.Add(static_Separation, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        # Values (ie row 2)
        self.textctrl_Separation = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('value', 'GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT) 
        self.sizer_h.Add(self.textctrl_Separation, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_Separation.SetToolTip("Enter separation in parsecs")
        
        # Select from Healpics
        static_HPSfrom = StaticText(self, id=wx.ID_ANY, label="HPS from:")
        self.sizer_h.Add(static_HPSfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_HPSfrom = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('hpsfrom','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=192,initial=int(gl_cfg.getItem('rafrom', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_HPSfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_HPSfrom.SetToolTip("Lower HPS to download 0 to 192")
        
        # Select 2 degrees
        static_HPSto = StaticText(self, id=wx.ID_ANY, label="HPS to:")
        self.sizer_h.Add(static_HPSto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_HPSto = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('hpsto','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=192,initial=int(gl_cfg.getItem('rato', 'GAIASTAR')))  
        self.sizer_h.Add(self.spin_HPSto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_HPSto.SetToolTip("Upper Healpix to scan to - out of 192")
        
        #******************************  Primary star **************************************
        
        # Select Px from (mas)
        static_PXfrom1 = StaticText(self, id=wx.ID_ANY, label="Px1=Px2 + n%:")
        self.sizer_h.Add(static_PXfrom1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXfrom1per = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxfrom1per','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxfrom1', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_PXfrom1per, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXfrom1per.SetToolTip("Primary lower parallax to download - 0% to 500% (calculated as a percentage of companion lower parallax.)")
        
        # Select Px to (degrees)
        static_PXto1 = StaticText(self, id=wx.ID_ANY, label="Px1 to (mas):")
        self.sizer_h.Add(static_PXto1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXto1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxto1','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxto1', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_PXto1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXto1.SetToolTip("Primary upper parallax to download to - out of 1000 (expectation is '1000')")
        
        #and parallax_over_error > 20
        #and phot_g_mean_flux_over_error > 50
        #and phot_rp_mean_flux_over_error > 20
        #and phot_bp_mean_flux_over_error > 20
        # Select parallax_over_error
        static_Px_err1 = StaticText(self, id=wx.ID_ANY, label="Px/err (1):")
        self.sizer_h.Add(static_Px_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Px_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('px_err1','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('px_err1', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_Px_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Px_err1.SetToolTip("Primary parallax_over_error to download - 0 to 100 (expectation is '20')")
        
        # Select phot_g_mean_flux_over_error
        static_G_err = StaticText(self, id=wx.ID_ANY, label="G/err (1):")
        self.sizer_h.Add(static_G_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_G_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('g_err1','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('g_err1', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_G_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_G_err1.SetToolTip("Primary phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50')")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err1 = StaticText(self, id=wx.ID_ANY, label="Rp/err (1):")
        self.sizer_h.Add(static_Rp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err1','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err1', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_Rp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err1.SetToolTip("Primary phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '20')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err1 = StaticText(self, id=wx.ID_ANY, label="Bp/err (1):")
        self.sizer_h.Add(static_Bp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err1','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err1', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_Bp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Bp_err1.SetToolTip("Primary phot_bp_mean_flux_over_error to download - 0 to 100 (expectation is '20')")
        
        #******************************  Companion star **************************************
        
        # Select Px from (mas)
        static_PXfrom2 = StaticText(self, id=wx.ID_ANY, label="Px2 from (mas):")
        self.sizer_h.Add(static_PXfrom2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXfrom2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxfrom2','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxfrom2', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_PXfrom2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXfrom2.SetToolTip("Lower companion parallax to download - 0 to 1000 (expectation is '3')")
        
        # Select Px to (degrees)
        static_PXto2 = StaticText(self, id=wx.ID_ANY, label="Px2 to (mas):")
        self.sizer_h.Add(static_PXto2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXto2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxto2','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxto2', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_PXto2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXto2.SetToolTip("Upper companion parallax to download to - out of 1000 (expectation is '1000')")
        
        #and parallax_over_error > 5
        #and phot_g_mean_flux_over_error > 50
        #and phot_rp_mean_flux_over_error > 10
        #and phot_bp_mean_flux_over_error > 10
        # Select parallax_over_error
        static_Px_err2 = StaticText(self, id=wx.ID_ANY, label="Px/err (2):")
        self.sizer_h.Add(static_Px_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Px_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('px_err2','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('px_err2', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_Px_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Px_err2.SetToolTip("Companion parallax_over_error to download - 0 to 100 (expectation is '5')")
        
        # Select phot_g_mean_flux_over_error
        static_G_err2 = StaticText(self, id=wx.ID_ANY, label="G/err (2):")
        self.sizer_h.Add(static_G_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_G_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('g_err2','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('g_err2', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_G_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_G_err2.SetToolTip("Companion phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50')")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err2 = StaticText(self, id=wx.ID_ANY, label="Rp/err (2):")
        self.sizer_h.Add(static_Rp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err2','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err2', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_Rp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err2.SetToolTip("Companion phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err2 = StaticText(self, id=wx.ID_ANY, label="Bp/err (2):")
        self.sizer_h.Add(static_Bp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err2','GAIABINARY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err2', 'GAIABINARY')))  
        self.sizer_h.Add(self.spin_Bp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Bp_err2.SetToolTip("Companion phot_bp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Create download only data check box
        downloadOnlyStaticText = StaticText(self, id=wx.ID_ANY, label="Download only?")
        self.sizer_h.Add(downloadOnlyStaticText, 0, wx.ALL, 2)
        self.downloadOnlyCheckBox = CheckBox(self)
        self.downloadOnlyCheckBox.SetToolTip("Speed up download by only downloading and saving pandas files to disc.  Ie not saving to database.")
        self.downloadOnlyCheckBox.SetValue(gl_cfg.getBoolean('downloadonly', 'GAIABINARY'))
        self.sizer_h.Add(self.downloadOnlyCheckBox, 0, wx.ALL, 2)
        
        # Create force redownload data check box
        forceDownloadStaticText = StaticText(self, id=wx.ID_ANY, label="Force redownload?")
        self.sizer_h.Add(forceDownloadStaticText, 0, wx.ALL, 2)
        self.forceDownloadCheckBox = CheckBox(self)
        self.forceDownloadCheckBox.SetToolTip("Force re-download of files from Gaia.  This overwrites local values.")
        self.forceDownloadCheckBox.SetValue(gl_cfg.getBoolean('forceredownload', 'GAIABINARY'))
        self.sizer_h.Add(self.forceDownloadCheckBox, 0, wx.ALL, 2)
        
        # Create 'deactivate indices' check box to speed up data inserts.
        deactivateIndicesStaticText = StaticText(self, id=wx.ID_ANY, label="Deactivate indices?")
        self.sizer_h.Add(deactivateIndicesStaticText, 0, wx.ALL, 2)
        self.deactivateIndicesCheckBox = CheckBox(self)
        self.deactivateIndicesCheckBox.SetToolTip("Deactivate indices to speed up DB inserts.  Speeds up large changes.  ")
        self.deactivateIndicesCheckBox.SetValue(gl_cfg.getBoolean('deactivateindices', 'GAIABINARY'))
        self.sizer_h.Add(self.deactivateIndicesCheckBox, 0, wx.ALL, 2)
                
        self.SetSizer(self.sizer_main_divider)
                        
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(765,500), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
        self.listctrl.InsertColumn(0, u"Release", wx.LIST_FORMAT_CENTER,  width=100)
        self.listctrl.InsertColumn(1, u"Catalogue", wx.LIST_FORMAT_CENTER, width=100)
        self.listctrl.InsertColumn(2, u"separation", wx.LIST_FORMAT_CENTER, width=100)
        self.listctrl.InsertColumn(3, u"Healpix from", wx.LIST_FORMAT_RIGHT, width=100)
        self.listctrl.InsertColumn(4, u"Healpix to", wx.LIST_FORMAT_RIGHT, width=100)
        self.listctrl.InsertColumn(5, u"Binary count", wx.LIST_FORMAT_RIGHT,  width=100)
        self.listctrl.InsertColumn(6, u"Date time", wx.LIST_FORMAT_CENTER,  width=160)
        #
        
        self.sizer_v.Add(self.listctrl, 0, wx.TOP | wx.BOTTOM , 10)
                
        # Import Total prompt
        
        static_Total = StaticText(self, id=wx.ID_ANY, label="Total stars:")
        self.sizer_h2.Add(static_Total, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Total
        
        self.static_Total = StaticText(self, id=wx.ID_ANY, label='n/a')
        self.sizer_h2.Add(self.static_Total, 0, wx.ALL, 5)
        
        # Loading data
        
        static_DataLoad = StaticText(self, id=wx.ID_ANY, label="Data load:")
        self.sizer_v2.Add(static_DataLoad, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.button1 = Button(self, wx.ID_ANY, u"Binary Load")
        self.button1.SetToolTip("Download selected binaries from Gaia.")
        self.button1.Bind(wx.EVT_LEFT_DOWN, self.read_GaiaBinaries)
        self.sizer_v2.Add(self.button1, 0,wx.ALIGN_LEFT|wx.ALL , 5)
                
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel import or status update.")
        self.sizer_v2.Add(self.button2, 0, wx.LEFT | wx.RIGHT , 5)
        

    def addCatalogue(self, event=0):
        
        global RELEASE
        TBL_CATALOG = SQLLib.sqlInsert(iStro, "TBL_CATALOG")
        catalog=self.textctrl_newCatalog.GetValue()
        if len(catalog)>0 and  len(catalog)<10:
            TBL_CATALOG .setAttributeString("RELEASE_", self.release.GetValue())
            TBL_CATALOG .setAttributeString("CATALOG", catalog)
            records = TBL_CATALOG.insertRecord()
            self.textctrl_newCatalog.SetValue('')
        self.catRefresh()
     
            
    #def restoreListCtrl(self, event=0, limit=1000):
    #    
    #    try:
    #        self.parent.selectedStarBinaryMappings=self.parent.selectedStarBinaryMappings.convert_dtypes()
    #    except Exception:
    #        pass
    #    
    #    for index, row  in self.parent.selectedStarBinaryMappings.iterrows():
    #        if index>limit:
    #            break
    #        try:
    #            if str(row.STATUS) == '<NA>':
    #                status=''
    #            else:
    #                status=str(row.STATUS)
    #        except Exception:
    #            status = ''
    #        try:
    #            if row.NOT_GROUPED == True:
    #                notGrouped='True'
    #            else:
    #                notGrouped='False'
    #        except Exception:
    #            notGrouped = 'Not Avail.'
    #        try:
    #            if row.HAS_RADIAL_VELOCITY == True:
    #                hasRadialVelocity='True'
    #            else:
    #                hasRadialVelocity='False'
    #        except Exception:
    #            hasRadialVelocity = 'Not Avail.'
    #        try:
    #            separation = str(float(row.SEPARATION))
    #        except Exception:
    #            separation = 'Not Avail.'
    #        try:
    #            healpix = str(int(row.HEALPIX))
    #        except Exception:
    #            healpix = 'Not Avail.'
    #        self.listctrl.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, index,separation, notGrouped, hasRadialVelocity, status, row.RELEASE_, row.CATALOG, healpix])

    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        
    def catRefresh(self, event=0):
        
        global RELEASE
        RELEASE = self.release.GetValue()
        TBL_CATALOG = SQLLib.sqlSelect(iStro, "TBL_CATALOG")
        TBL_CATALOG.setWhereValueString("RELEASE_", RELEASE)
        TBL_CATALOG.setReturnCol("CATALOG")
        TBL_CATALOG.setSortCol("CATALOG",1) # -ve is desc, +ve is ascending
        records = TBL_CATALOG.selectRecordSet()
        self.catalogues=[]
        
        for catalogue in records.itermap():
            #print(f'catalogue={catalogue}')
            self.catalogues.append(catalogue['CATALOG'])
        #
        self.catalogue.Clear()
        self.catalogue.SetItems(self.catalogues)
        self.catalogue.SetSelection(0)
        
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIABINARY') # save setting in config file
        
    def releaseRefresh(self, event=0):
        
        global RELEASE
        #RELEASE = self.release.GetValue()
        TBL_RELEASE = SQLLib.sqlSelect(iStro, "TBL_RELEASE")
        #TBL_RELEASE.setWhereValueString("RELEASE_", RELEASE)
        TBL_RELEASE.setReturnCol("RELEASE_")
        TBL_RELEASE.setSortCol("RELEASE_",1) # -ve is desc, +ve is ascending
        records = TBL_RELEASE.selectRecordSet()
        self.releases=[]
        
        for release in records.itermap():
            self.releases.append(release['RELEASE_'])
        #
        self.release.Clear()
        self.release.SetItems(self.releases)
        #
        self.release.SetSelection(int(gl_cfg.getItem('release', 'GAIABINARY'))) # Get setting from config file
        return self.releases
        
    def binaries(self, record, i, release, catalogue ):
        TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ");
        TBL_BINARIES .setAttributeIntBig("SOURCE_ID_PRIMARY", record.source_id)
    
        TBL_BINARIES .setAttributeIntBig("SOURCE_ID_SECONDARY", record.source_id2)
    
        #global release, catalogue
        TBL_BINARIES .setAttributeString("release_", release)
        TBL_BINARIES .setAttributeString("CATALOG", catalogue)
        TBL_BINARIES .setAttributeBool("NOT_GROUPED", True)
        if self.is_number(record.radial_velocity) and self.is_number(record.radial_velocity2):
            TBL_BINARIES .setAttributeBool("HAS_RADIAL_VELOCITY", True)
            TBL_BINARIES.setAttributeString("STATUS", "")
        else:
            TBL_BINARIES .setAttributeBool("HAS_RADIAL_VELOCITY", False)
            TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES .setAttributeFloat("SEPARATION", record.pairdistance)
        TBL_BINARIES .setAttributeInteger("HEALPIX", i)
        return TBL_BINARIES .getInsertSQL()
    def is_number(self, s):
        
        try:
            float(s)
            return True
        except Exception:
            return False
    def read_GaiaBinaries(self, event):

        self.button1.Disable()
        
        self.listctrl.DeleteAllItems()
        
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('value',self.textctrl_Separation.GetValue(), 'GAIABINARY') # save setting in config file        
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('hpsfrom',self.spin_HPSfrom.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('hpsto',self.spin_HPSto.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('downloadonly',self.downloadOnlyCheckBox.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('forceredownload', bool(self.forceDownloadCheckBox.GetValue()), 'GAIABINARY') # save notebook tab setting in config file
        gl_cfg.setItem('deactivateindices',bool(self.deactivateIndicesCheckBox.GetValue()), 'GAIABINARY') # save notebook tab setting in config file
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        gl_cfg.setItem('pxto1',self.spin_PXto1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('pxfrom1per',self.spin_PXfrom1per.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('rp_err1',self.spin_Rp_err1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('bp_err1',self.spin_Bp_err1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('px_err1',self.spin_Px_err1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('g_err1',self.spin_G_err1.GetValue(), 'GAIABINARY') # save setting in config file
        
        gl_cfg.setItem('pxto2',self.spin_PXto2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('pxfrom2',self.spin_PXfrom2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('rp_err2',self.spin_Rp_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('bp_err2',self.spin_Bp_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('px_err2',self.spin_Px_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('g_err2',self.spin_G_err2.GetValue(), 'GAIABINARY') # save setting in config file
                        
        query=[0]
        #
            
        Gaia50000Select="""-- Binary star selection ADQL from K el Badry paper.  Comments by S Cookson.
        -- Pair distance is angular distance. Other fields removed for separate star data download.
        -- It is expected that the star data is downloaded once - about 8 million stars - and the binaries are downloaded many times.
        -- This separation of data speeds up the binary downloads.
        SELECT g2.source_id as source_id2, t1.source_id, t1.dr2_radial_velocity as radial_velocity, g2.dr2_radial_velocity as radial_velocity2, distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)) AS pairdistance
        """
        # Comments for CICLE parameter
        #"""
        #The physical separation of a pair is theta*d, where theta is the angular separation (in radians), and d is the distance. The distance in parsecs is d = 1000/parallax,
        #where the Gaia parallaxes are in mas. Finally, the CIRCLE function wants an angular separation in degrees (not radians). So:
        #
        #theta [rad] * d [pc] < 0.24 
        #theta [deg] * d [pc] < (0.24 * pi/180)
        #theta [deg] * 1000/parallax [mas] < (0.24 * 180/pi)
        #theta [deg]/parallax [mas] < (0.24 * 180/pi)/1000
        #
        #And (0.24 * 180/pi)/1000 = 1.4e-2
        #
        #So if you wanted e.g. 1 pc, you would replace 1.4e-2 with 0.0573. '
        #"""
        #"""
        separation=float(self.textctrl_Separation.GetValue())
        pc=float(0.0573*separation)
        print(pc)
        nsigma=8
        release=self.release.GetValue()
        #release='fDR3'
        catalogue=self.catalogue.GetValue()
        HPS=[]
        HPSlower = int(self.spin_HPSfrom.GetValue())
        HPSupper = int(self.spin_HPSto.GetValue())
        HPS.extend(range(HPSlower,HPSupper))
        countMe=0
        forceIt=False # Force download
        step=1
        
        forceIt=self.forceDownloadCheckBox.GetValue() # Force download
        downloadOnly=self.downloadOnlyCheckBox.GetValue() # Download only, don't update
            
        if self.deactivateIndicesCheckBox.GetValue():
            #Deactivate 9 indices on TBL_BINARIES
            TBL_BINARIES  = SQLLib.sql(iStro, "TBL_objects ")
            #ALTER INDEX IDX_TBL_BINARIES1 to 9 INACTIVE
            for idx in range(1,10):
                bulkSQL=f"ALTER INDEX IDX_TBL_BINARIES{idx} INACTIVE ;"
                TBL_BINARIES .executeIAD(bulkSQL)
                print(bulkSQL)
                
        count=0
        Gaia50000Where=f"""
            WHERE
                    -- The '!=' symbol makes sure they are not the same star.
                    -- The '<' sign makes sure that only pair AB is included not BA.
                    -- You can use either
                    t1.source_id < g2.source_id
                AND
                    -- Where star 2 is within a defined radius of star 1 (see note)
                    1 = contains(POINT('ICRS', g2.ra, g2.dec), CIRCLE('ICRS', t1.ra, t1.dec,{pc}*t1.parallax))
                AND
                    -- And radial separation minus ...
                    abs(1/t1.parallax - 1/g2.parallax) -
                    -- 2 * pi()/180 * 'in the plane separation'/parallax
                    2*0.01745*distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec))/t1.parallax
                    < 3*sqrt(power(t1.parallax_error,2)/power(t1.parallax, 4) + power(g2.parallax_error, 2)/power(g2.parallax, 4))
            --    AND
            --        -- Relative velocity in the plane of the sky - Pythagoras. No spherical correction (pp 15-16 WM Smart).
            --	      -- Section removed because non-Newtonian movement deselected.
            --        sqrt(power((t1.pmra - g2.pmra), 2) + power((t1.pmdec - g2.pmdec), 2))
            --        -- Newtonian line (eq4 in the paper)
            --        - (7.42e-3 * power(t1.parallax, 1.5) * power(distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)), -0.5))
            --            <
            --        -- < 8 sigma (changed from 3 to 8)
            --        {nsigma}*sqrt(
            --            ((power((t1.pmra_error), 2) + power((g2.pmra_error), 2)) *  power((t1.pmra - g2.pmra), 2) +
            --            (power((t1.pmdec_error), 2) + power((g2.pmdec_error), 2)) * power((t1.pmdec - g2.pmdec), 2))
            --                /(power((t1.pmra - g2.pmra), 2) + power((t1.pmdec - g2.pmdec), 2)))
                AND
                    -- sigma < 1.5 (noise/signal < 1.5)
                    sqrt(
                        ((power((t1.pmra_error), 2) + power((g2.pmra_error), 2)) * power((t1.pmra - g2.pmra), 2) +
                        (power((t1.pmdec_error), 2) + power((g2.pmdec_error), 2)) * power((t1.pmdec - g2.pmdec), 2))
                            /(power((t1.pmra - g2.pmra), 2) + power((t1.pmdec - g2.pmdec), 2)))
                                < 1.5
        """
        for i in HPS:
            
            healpixA=2**35*4**(12-2)*i
            healpixB=2**35*4**(12-2)*(i+step) 
        
            fromHealpixClause=f"""
            -- index file: {i}
            source_id >= {healpixA} and source_id < {healpixB} and
            """
            print (i, healpixA)
            
            Gaia50000From=f"""
            FROM
            -- outer product of candidates for primary star with candidates for secondary star
            -- t1 is primary
            (select * from gaiaedr3.gaia_source
            where
                {fromHealpixClause}
                -- outside solar system and within 333 pcs
                parallax between {self.spin_PXfrom2.GetValue() * (1 + int(self.spin_PXfrom1per.GetValue())/100)} and {self.spin_PXto1.GetValue()} and
                parallax_over_error > {self.spin_Px_err1.GetValue()} and
                -- Many dim stars don't have photometric data on Gaia
                -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
                phot_g_mean_flux_over_error > {self.spin_G_err1.GetValue()} and
                phot_rp_mean_flux_over_error > {self.spin_Rp_err1.GetValue()} and
                phot_bp_mean_flux_over_error > {self.spin_Bp_err1.GetValue()})
                as t1,
            (select * from gaiaedr3.gaia_source
            where 
                {fromHealpixClause}
                bp_rp is not null and
                -- outside solar system and within 333 pcs
                parallax between {self.spin_PXfrom2.GetValue()} and {self.spin_PXto2.GetValue()} and
                parallax_over_error > {self.spin_Px_err2.GetValue()} and
                -- Many dim stars don't have photometric data on Gaia
                -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
                phot_g_mean_flux_over_error > {self.spin_Px_err2.GetValue()} and
                phot_rp_mean_flux_over_error > {self.spin_Rp_err2.GetValue()} and
                phot_bp_mean_flux_over_error > {self.spin_Bp_err2.GetValue()})
                as g2
            """
        
            query[0]=Gaia50000Select+" "+Gaia50000From+" "+Gaia50000Where
            
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            print('start query', date_time)
            if not os.path.isdir(f'bindata/{release}'):
                os.mkdir (f'bindata/{release}')
            if not os.path.isdir(f'bindata/{release}/{catalogue}'):
                os.mkdir (f'bindata/{release}/{catalogue}')
                
            if (not forceIt) and os.path.isfile(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}'):
                data =pd.read_pickle(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}')
                print('Local copy restored')
            else:
                print(query[0])
                gaia_cnxn = da.GaiaDataAccess()
                data = gaia_cnxn.gaia_query_to_pandas(query[0])
                print(data)
                data.to_pickle(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}')
            
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            
            dataLen=len(data)
            countMe=countMe+dataLen
            #print(f'Running total countMe={countMe:,}')
            self.static_Total.SetLabel(f'{countMe:,}')
            self.listctrl.Append([release,catalogue, separation, i, i+step, f'{dataLen:,}', date_time])
            self.listctrl.EnsureVisible(i-HPSlower)
            self.Layout()
            wx.Yield()
            if downloadOnly:
                continue
            
            print(f'delete old records for healix {i}')
            TBL_BINARIES = SQLLib.sqlDelete(iStro, "TBL_BINARIES");
            TBL_BINARIES.setWhereValueInt('HEALPIX', i)
            TBL_BINARIES.setWhereValueString('CATALOG', catalogue)
            TBL_BINARIES.setWhereValueString('RELEASE_', release)
            TBL_BINARIES.deleteRecordSet()
            print('start processing record', date_time)
            bulkSQL='execute block as begin'
            print(f'length of data = {len(data):,}')
            source_id_array=[]
            data=data.convert_dtypes()
            dataLen=len(data)
            for index, record in data.iterrows():
                count=count+1
                if [record.source_id,record.source_id2] in source_id_array:
                    continue
                else:
                    source_id_array.append([record.source_id,record.source_id2])
                sql=self.binaries(record,i, release, catalogue)
                if index % 20:
                    bulkSQL = bulkSQL + """
                    """ + sql + " "
                else:
                    bulkSQL = bulkSQL + """
                    """ + sql + """
                    end"""
                    TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ")
                    TBL_BINARIES .executeIAD(bulkSQL)
                    
                    #Refresh button with progress and check for 'cancel'
                    label=int(100 * index /dataLen)
                    self.button1.SetLabel(f'{i}/{HPSupper-1}-{label}%')
                    global CANCEL
                    if CANCEL:
                        CANCEL = False
                        #Release button
                        self.button1.Enable()
                        return
                    wx.Yield()
                    
                    bulkSQL='execute block as begin'
            if bulkSQL != 'execute block as begin':
                bulkSQL = bulkSQL + '  end'
                TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ")
                TBL_BINARIES .executeIAD(bulkSQL)
            bulkSQL=''
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            print('update', date_time)
            
            wx.Yield()
        #SQL="""
        #SELECT 
        #g2.source_id as source_id2,
        #t1.source_id, 
        #distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)) AS pairdistance
        #FROM (select * from gaiaedr3.gaia_source 
        #          where source_id >= 9871890383196127232 and source_id < 9907919180215091200 and 
        #parallax between 5 and 1000 and
        #parallax_over_error > 20 and
        #phot_g_mean_flux_over_error > 50 and
        #phot_rp_mean_flux_over_error > 20 and
        #phot_bp_mean_flux_over_error > 20) as t1,
        #(select * from gaiaedr3.gaia_source
        #where source_id >= 9871890383196127232 and source_id < 9907919180215091200 and
        # bp_rp is not null and
        #parallax > 3 and
        #parallax_over_error > 5 and
        #phot_g_mean_flux_over_error > 50 and
        #phot_rp_mean_flux_over_error > 10 and
        #phot_bp_mean_flux_over_error > 10) as g2
        #WHERE 1 = contains(POINT('ICRS', g2.ra, g2.dec),
        #CIRCLE('ICRS', t1.ra, t1.dec,
        #1.4e-2*t1.parallax))
        #AND t1.source_id != g2.source_id
        #AND abs(1/t1.parallax - 1/g2.parallax) -
        #2*0.01745*distance(POINT('ICRS', t1.ra,
        #t1.dec), POINT('ICRS', g2.ra, g2.dec))/
        #t1.parallax < 3*sqrt(power(t1.parallax_error,
        #2)/power(t1.parallax, 4) + power(
        #g2.parallax_error, 2)/power(g2.parallax, 4))
        #AND sqrt(power((t1.pmra - g2.pmra), 2) +
        #power((t1.pmdec - g2.pmdec), 2)) -
        #(7.42e-3 * power(t1.parallax, 1.5) *
        #power(distance(POINT('ICRS', t1.ra, t1.dec),
        #POINT('ICRS', g2.ra, g2.dec)), -0.5)) <
        #3*sqrt(((power((t1.pmra_error), 2) + power(
        #(g2.pmra_error), 2)) * power((t1.pmra -
        #g2.pmra), 2) + (power((t1.pmdec_error), 2) +
        #power((g2.pmdec_error), 2)) * power(
        #(t1.pmdec - g2.pmdec), 2))/(power(
        #(t1.pmra - g2.pmra), 2) + power(
        #(t1.pmdec - g2.pmdec), 2)))
        #AND sqrt(((power((t1.pmra_error), 2) +
        #                   power((g2.pmra_error), 2)) * power(
        #(t1.pmra - g2.pmra), 2) + (power(
        #(t1.pmdec_error), 2) + power(
        #(g2.pmdec_error), 2)) * power((t1.pmdec -
        #g2.pmdec), 2))/(power((t1.pmra - g2.pmra),
        #2) + power((t1.pmdec - g2.pmdec), 2))) < 1.5
        #"""
        self.parent.printArrays()
                
        if self.deactivateIndicesCheckBox.GetValue():
            TBL_BINARIES  = SQLLib.sql(iStro, "TBL_objects ")
            #ALTER INDEX IDX_TBL_BINARIES1 to 9 ACTIVE
            for idx in range(1,10):
                bulkSQL=f"ALTER INDEX IDX_TBL_BINARIES{idx} ACTIVE ;"
                TBL_BINARIES .executeIAD(bulkSQL)
                print(bulkSQL)
        self.button1.Enable()
        
    def resetStatus(self, event):
        
        self.reset.Disable()
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", True)
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            if i<192:
                TBL_BINARIES.setWhereValueLTInt("SOURCE_ID", healpix)
        print(TBL_BINARIES.updateRecord())
        
        self.reset.Enable()
        
    def deselectRVnull(self, event):
        
        self.rvnull.Disable()
        
        commentHP='--'
        commentRA='--'
        commentDec='--'
        
        i=int(self.spin_loadType.GetValue())
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            commentHP=''
        if self.loadType_combo.GetSelection()==1:
            commentRA=''
        if self.loadType_combo.GetSelection()==2:
            commentDec=''

        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        healpix=2**35*4**(12-2)*i
        
        sql = f"""SELECT b.RELEASE_, b.CATALOG, b.SOURCE_ID_PRIMARY, b.SOURCE_ID_SECONDARY, b.SEPARATION, b.NOT_GROUPED, b.HAS_RADIAL_VELOCITY
                FROM TBL_BINARIES b
                    inner join TBL_OBJECTS o1
                        on b.SOURCE_ID_PRIMARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_
                    inner join TBL_OBJECTS o2
                        on b.SOURCE_ID_SECONDARY=o2.SOURCE_ID and b.RELEASE_ = o2.RELEASE_
                where (o1.RADIAL_VELOCITY is Null
                or o2.RADIAL_VELOCITY is Null) and b.CATALOG = '{CATALOG}' and b.RELEASE_ = '{RELEASE}' and b.HAS_RADIAL_VELOCITY = True
        
            {commentHP} and b.SOURCE_ID_PRIMARY < {healpix}
            {commentRA} and o1.RA_ < {i}  and o2.RA_ < {i}
            {commentDec} and o1.DEC_ < {i}  and o2.DEC_ < {i} and o1.DEC_ > {-i}  and o2.DEC_ > {-i}
            
        ORDER BY SOURCE_ID_PRIMARY asc
        
                """

        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        Array=[] 
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            #self.parent.radialvelocity[index]=0
            Array.append( row.SOURCE_ID_PRIMARY)
            if not index % 200:
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "rv=0")
                TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "rv=0")
                TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                Array=[] 
                label=float(100 * index /lenArray)
                self.rvnull.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    self.rvnull.Enable()
                    return
                wx.Yield()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        
        label=int(100)
        self.rvnull.SetLabel(f'{label:,.1f}%')
        
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
        TBL_BINARIES.setWhereValueString("RELEASE_", RELEASE)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setReturnCol("count(*) as CNT")
        records = TBL_BINARIES.selectRecordSet()
        for row in records:
            ROWCOUNTMATRIX['RV0']=row[0]
            self.static_RVnull.SetLabel(f'{row[0]:,}')
        self.rvnull.Enable()
        self.Layout()
        
    def OnDeleteSelection(self, event):
        #Move Ba to another catalogue
        self.deleteSelection.Disable()
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        
        whereValue=int(self.spin_loadType.GetValue())
                
        if self.loadType_combo.GetSelection()==0:
            whereValue=2**35*4**(12-2)*whereValue  # From Gaia website
            whereAtt='SOURCE_ID_PRIMARY'
        if self.loadType_combo.GetSelection()==1:
            whereAtt='RA_'
        if self.loadType_combo.GetSelection()==2:
            whereAtt=='DEC_'
        
        TBL_BINARIES = SQLLib.sqlDelete(iStro, "TBL_BINARIES")

        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.setWhereValueLTInt(whereAtt, whereValue)
                
        print(TBL_BINARIES.deleteRecordSet())
        
        self.deleteSelection.Enable()
        
    def moveBineries(self, event):
        #Move Ba to another catalogue
        self.move.Disable()
        
        global RELEASE, CATALOG
        #RELEASE=self.release.GetValue()
        CATALOG_NEW=self.catalogue.GetValue()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("CATALOG", CATALOG_NEW)

        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        #TBL_BINARIES.setWhereAttGTAtt("SOURCE_ID_PRIMARY", "SOURCE_ID_SECONDARY")
                
        print(TBL_BINARIES.updateRecord())
        
        self.move.Enable()
        
    def deselectDuplicates(self, event):
        #Freeze button
        self.ungroup.Disable()
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "ALLSTARS2")
        TBL_BINARIES.setReturnCol("SOURCE_ID")
        TBL_BINARIES.setGroupByCol("SOURCE_ID")
        TBL_BINARIES.setHavingGTInt("COUNT(SOURCE_ID)",1) # Having count > 1 (ie duplicate SOURCE_ID)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", True)
        TBL_BINARIES.setSortCol("SOURCE_ID")

        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            if i<192:
                TBL_BINARIES.setWhereValueLTInt("SOURCE_ID", healpix)
        if self.loadType_combo.GetSelection()==1:
            TBL_BINARIES.setWhereValueLTInt("RA_", i)
        if self.loadType_combo.GetSelection()==2:
            TBL_BINARIES.setWhereValueLTInt("DEC_", i)
            TBL_BINARIES.setWhereValueLTInt(-i, "DEC_")
        
        sql = TBL_BINARIES.getSQL()
        print (sql)
        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        print(f'Ungrouping {lenArray} records started')
        Array=[] 
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            Array.append( row.SOURCE_ID)
            
            if not index % 200:
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "dupl")
                TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "dupl")
                TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                
                Array=[] 
    
                label=float(100 * index /lenArray)
                self.ungroup.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    #Release button
                    self.ungroup.Enable()
                    return
                wx.Yield()
                 
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "dupl")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "dupl")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        
        label=int(100)
        self.ungroup.SetLabel(f'{label:,.1f}%')
        
        
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
        TBL_BINARIES.setWhereValueString("RELEASE_", RELEASE)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", False)
        TBL_BINARIES.setReturnCol("count(*) as CNT")
        records = TBL_BINARIES.selectRecordSet()
        for row in records:
            #print(f'{row[0]:,}')
            ROWCOUNTMATRIX['GRP']=row[0]
            self.static_Cluster.SetLabel(f'{row[0]:,}')
        
        #Release button
        self.ungroup.Enable()
        self.Layout()
        

class dataRetrieval(wx.Panel):
    
    def dump(self, obj):
      for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'
        
        #Try to find existing files, if not, create blank one
        files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','star_rows','X','Y','status','export']
        for file in files:
            try:
                setattr(self.parent,file, pd.read_pickle('bindata/'+file+'.saved'))
            except Exception:
                setattr(self.parent,file, pd.DataFrame())

        try:
            file_to_read = open('bindata/starSystemList.pickle', 'rb') #File containing example object
            self.parent.starSystemList = pickle.load(file_to_read) # Load saved object
            file_to_read.close()
        except Exception:
            self.parent.starSystemList=binaryStarSystems(len(self.parent.status))
        
        self.sizer_main_divider=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main=wx.BoxSizer(wx.VERTICAL)
        self.sizer_main_divider.Add(self.sizer_main)
        self.sizer_h=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.sizer_v2=wx.BoxSizer(wx.VERTICAL)
        self.sizer_h2=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.sizer_h)
        self.sizer_main.Add(self.sizer_v)
        self.sizer_main.Add(self.sizer_h2)
        self.sizer_main_divider.Add(self.sizer_v2)
        
        # Select release
        
        static_Release = StaticText(self, id=wx.ID_ANY, label="Release:")
        self.sizer_h.Add(static_Release, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Release select
        self.release = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        releases=self.releaseRefresh()
        self.release.Bind(wx.EVT_CHOICE, self.catRefresh)
        self.release.SetSelection(int(gl_cfg.getItem('release','RETRIEVAL')))
        self.release.SetToolTip("Select release source")
        self.sizer_h.Add(self.release, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        global RELEASE
        RELEASE = self.release.GetValue()
        
        # Catalogue prompt
        static_Catalogue = StaticText(self, id=wx.ID_ANY, label="Catalogue:")
        self.sizer_h.Add(static_Catalogue, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.catalogue = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        self.catalogue.SetToolTip("Select Catalogue")
        self.catRefresh()
        self.catalogue.SetSelection(int(gl_cfg.getItem('catalog', 'RETRIEVAL')))
        self.sizer_h.Add(self.catalogue, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        global CATALOG
        CATALOG = self.catalogue.GetValue()
        
        # Load Catalogue
        
        # Loadtype
        
        self.loadType_combo = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['Healpix','Degrees (RA)','Degrees (Dec)', 'Parsecs'], value='')
        self.loadType_combo.SetSelection(int(gl_cfg.getItem('loadtype', 'RETRIEVAL')))
        self.loadType_combo.SetToolTip("Select load mechanism")
        self.loadType_combo.Bind(wx.EVT_CHOICE, self.loadTypeRefresh)
        self.sizer_h.Add(self.loadType_combo, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        # Values (ie row 2)
        self.spin_loadType = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=360,initial=int(gl_cfg.getItem('value', 'RETRIEVAL')))  
        self.sizer_h.Add(self.spin_loadType, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_loadType.SetToolTip("Upper Healpix to scan to - out of 192")
        self.loadTypeRefresh()
        
        # Create ungrouped data check box
        ungroupedStaticText = StaticText(self, id=wx.ID_ANY, label="Load clusters?")
        self.sizer_h.Add(ungroupedStaticText, 0, wx.ALL, 2)
        self.unGroupedCheckBox = CheckBox(self)
        self.unGroupedCheckBox.SetToolTip("Speed up load and program by not loading binaries in clusters.")
        self.unGroupedCheckBox.SetValue(gl_cfg.getBoolean('ungrouped', 'RETRIEVAL'))
        self.sizer_h.Add(self.unGroupedCheckBox, 0, wx.ALL, 2)
        
        # Create RV=0 data check box
        rvnullStaticText = StaticText(self, id=wx.ID_ANY, label="Load RV=0?")
        self.sizer_h.Add(rvnullStaticText, 0, wx.ALL, 2)
        self.rvnullCheckBox = CheckBox(self)
        self.rvnullCheckBox.SetToolTip("Speed up load and program by not loading binaries flagged with one or both stars having radial velocity = 0.")
        self.rvnullCheckBox.SetValue(gl_cfg.getBoolean('rvnull', 'RETRIEVAL'))
        self.sizer_h.Add(self.rvnullCheckBox, 0, wx.ALL, 2)
        
                
        self.SetSizer(self.sizer_main_divider)
                        
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(1140,600), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
        self.listctrl.InsertColumn(0, u"Gaia Star 1 Source ID", wx.LIST_FORMAT_RIGHT, width=200)
        self.listctrl.InsertColumn(1, u"Gaia Star 2 Source ID", wx.LIST_FORMAT_RIGHT, width=200)
        self.listctrl.InsertColumn(2, u"pairing no.", wx.LIST_FORMAT_RIGHT, width=80)
        self.listctrl.InsertColumn(3, u"separation", width=100)
        self.listctrl.InsertColumn(4, u"Not grouped?", wx.LIST_FORMAT_CENTER,  width=80)
        self.listctrl.InsertColumn(5, u"Has RV?", wx.LIST_FORMAT_CENTER,  width=80)
        self.listctrl.InsertColumn(6, u"Status", wx.LIST_FORMAT_CENTER,  width=100)
        self.listctrl.InsertColumn(7, u"Release", wx.LIST_FORMAT_CENTER,  width=100)
        self.listctrl.InsertColumn(8, u"Catalogue", wx.LIST_FORMAT_CENTER, width=100)
        self.listctrl.InsertColumn(9, u"Healpix", wx.LIST_FORMAT_RIGHT, width=100)
        #
        self.restoreListCtrl()
        
        self.sizer_v.Add(self.listctrl, 0, wx.TOP | wx.BOTTOM , 10)
        
        # Import Total prompt
        
        static_Total = StaticText(self, id=wx.ID_ANY, label="Total pairs:")
        self.sizer_h2.Add(static_Total, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Total
        
        ROWCOUNTMATRIX['ADQL']=len(self.parent.selectedStarBinaryMappings)
        self.static_Total = StaticText(self, id=wx.ID_ANY, label=f'{ROWCOUNTMATRIX["ADQL"]:,}')
        self.sizer_h2.Add(self.static_Total, 0, wx.ALL, 5)
        
        # Number in clusters prompt
        
        static_Cluster = StaticText(self, id=wx.ID_ANY, label="Number in clusters:")
        self.sizer_h2.Add(static_Cluster, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Cluster
        
        #ROWCOUNTMATRIX['GRP']=len(self.parent.selectedStarBinaryMappings)
        self.static_Cluster = StaticText(self, id=wx.ID_ANY, label=f'N/a')
        self.sizer_h2.Add(self.static_Cluster, 0, wx.ALL, 5)
        
        # Number in RVnulls prompt
        
        static_RVnull = StaticText(self, id=wx.ID_ANY, label="Number without radial velocity:")
        self.sizer_h2.Add(static_RVnull, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # RVnull
        
        #ROWCOUNTMATRIX['GRP']=len(self.parent.selectedStarBinaryMappings)
        self.static_RVnull = StaticText(self, id=wx.ID_ANY, label=f'N/a')
        self.sizer_h2.Add(self.static_RVnull, 0, wx.ALL, 5)
        
        # Loading data
        
        static_DataLoad = StaticText(self, id=wx.ID_ANY, label="Data save/load:")
        self.sizer_v2.Add(static_DataLoad, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.button1 = Button(self, wx.ID_ANY, u"DB Load")
        self.button1.SetToolTip("Import selected release/catalogue from database with or without null radial velocities or ungrouped star clusters.")
        self.button1.Bind(wx.EVT_LEFT_DOWN, self.read_csv)
        self.sizer_v2.Add(self.button1, 0,wx.ALIGN_LEFT|wx.ALL , 5)
        
        self.button2 = Button(self, wx.ID_ANY, u"Export")
        self.sizer_v2.Add(self.button2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.button2.SetToolTip("Export selected data from active TF tab to csv file")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.write_csv)
        
        #Save catalogue in a directory
        
        self.save = Button(self, id=wx.ID_ANY, label="&Save", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.save.Bind(wx.EVT_BUTTON, self.catalogSave)
        self.save.SetToolTip("Save catalogue in a directory")
        self.sizer_v2.Add(self.save, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Restore catalogue from a diretory
        
        self.restore = Button(self, id=wx.ID_ANY, label="&Restore", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.restore.Bind(wx.EVT_BUTTON, self.catalogRestore)
        self.restore.SetToolTip("Restore catalogue from a diretory")
        self.sizer_v2.Add(self.restore, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel import or status update.")
        self.sizer_v2.Add(self.button2, 0, wx.LEFT | wx.RIGHT , 5)
        
        # Status processing prompt
        
        static_Status = StaticText(self, id=wx.ID_ANY, label="Status setting:")
        self.sizer_v2.Add(static_Status, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Deselect stars with no radial velocity
        
        self.rvnull = Button(self, id=wx.ID_ANY, label="&RV = Null", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.rvnull.Bind(wx.EVT_BUTTON, self.deselectRVnull)
        self.rvnull.SetToolTip("Deselect stars with no radial velocity")
        self.sizer_v2.Add(self.rvnull, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Rename Catalogue
        
        self.move = Button(self, id=wx.ID_ANY, label="&Move", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.move.Bind(wx.EVT_BUTTON, self.moveBineries)
        self.move.SetToolTip("For bineries in one catalogue, move to a different catalogue 'KEB5E5-BA")
        self.sizer_v2.Add(self.move, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Delete bineries with that combination of 'release', 'catalogue', and 'healpix/RA/dec'
        
        self.deleteSelection = Button(self, id=wx.ID_ANY, label="Delete", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.deleteSelection.Bind(wx.EVT_BUTTON, self.OnDeleteSelection)
        self.deleteSelection.SetToolTip("Delete bineries with that combination of 'release', 'catalogue', and 'healpix/RA/dec'")
        self.sizer_v2.Add(self.deleteSelection, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Deselect grouped stars (ie stars in more than 1 binary)
        
        self.ungroup = Button(self, id=wx.ID_ANY, label="&Ungroup", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.ungroup.Bind(wx.EVT_BUTTON, self.deselectDuplicates)
        self.ungroup.SetToolTip("Deselect binaries with stars that appear in more than one pair.  Ie deselect both pairs or entire cluster.")
        self.sizer_v2.Add(self.ungroup, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Reset status
        
        self.reset = Button(self, id=wx.ID_ANY, label="&Reset", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.reset.Bind(wx.EVT_BUTTON, self.resetStatus)
        self.reset.SetToolTip("Reset status for all binaries in this catalogue")
        self.sizer_v2.Add(self.reset, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.Layout()
        self.parent.printArrays()

    def write_csv(self, event):

        now = datetime.datetime.utcnow() # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")
        fileName='exportData' + date_time + '.csv'
        exportpd=pd.DataFrame(self.parent.export)
        exportpd.to_csv(fileName)
        
        print ("Write complete")
            
    def restoreListCtrl(self, event=0, limit=1000):
        
        try:
            self.parent.selectedStarBinaryMappings=self.parent.selectedStarBinaryMappings.convert_dtypes()
        except Exception:
            pass
        
        for index, row  in self.parent.selectedStarBinaryMappings.iterrows():
            if index>limit:
                break
            try:
                if str(row.STATUS) == '<NA>':
                    status=''
                else:
                    status=str(row.STATUS)
            except Exception:
                status = ''
            try:
                if row.NOT_GROUPED == True:
                    notGrouped='True'
                else:
                    notGrouped='False'
            except Exception:
                notGrouped = 'Not Avail.'
            try:
                if row.HAS_RADIAL_VELOCITY == True:
                    hasRadialVelocity='True'
                else:
                    hasRadialVelocity='False'
            except Exception:
                hasRadialVelocity = 'Not Avail.'
            try:
                separation = str(float(row.SEPARATION))
            except Exception:
                separation = 'Not Avail.'
            try:
                healpix = str(int(row.HEALPIX))
            except Exception:
                healpix = 'Not Avail.'
            self.listctrl.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, index,separation, notGrouped, hasRadialVelocity, status, row.RELEASE_, row.CATALOG, healpix])

    def catalogSave(self, event=0):
        global CATALOG, RELEASE
        
        
        CATALOG=self.catalogue.GetValue()
        RELEASE=self.release.GetValue()
        
        if not os.path.isdir(f'bindata'):
            os.mkdir (f'bindata')
        if not os.path.isdir(f'bindata/{RELEASE}'):
            os.mkdir (f'bindata/{RELEASE}')
        if not os.path.isdir(f'bindata/{RELEASE}/{CATALOG}'):
            os.mkdir (f'bindata/{RELEASE}/{CATALOG}')
        
        #Try to save files, if not, error
        files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','star_rows','X','Y','status','export']
        for file in files:
            try:
                x = getattr(self.parent,file)
                x=pd.DataFrame(x)
                x.to_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
            except Exception:
                print('Error directory failed to save:')
                print (f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
             
        
    def catalogRestore(self, event=0):
        
        self.listctrl.DeleteAllItems()
        global CATALOG, RELEASE
        
        CATALOG=self.catalogue.GetValue()
        RELEASE=self.release.GetValue()
        #Try to restore saved files, if not, error
        files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','star_rows','X','Y','status','export']
        for file in files:
            try:
                setattr(self.parent,file, pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved'))
            except Exception:
                print('Error directory failed to restore:')
                print (f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
                
        self.restoreListCtrl()
    def loadTypeRefresh(self, event=0):

        if self.loadType_combo.GetSelection()==0:
            self.spin_loadType.SetMin(0)
            self.spin_loadType.SetMax(192)
            self.spin_loadType.SetToolTip("Upper Healpix to load to - out of 192")
        if self.loadType_combo.GetSelection()==1:
            self.spin_loadType.SetMin(0)
            self.spin_loadType.SetMax(360)
            self.spin_loadType.SetToolTip("Upper RA to load to - out of 360")
        if self.loadType_combo.GetSelection()==2:
            self.spin_loadType.SetMin(0)
            self.spin_loadType.SetMax(90)
            self.spin_loadType.SetToolTip("Dec to load to - out of 90 (Loads from -x to +x)")
        if self.loadType_combo.GetSelection()==3:
            self.spin_loadType.SetMin(3)
            self.spin_loadType.SetMax(1000)
            self.spin_loadType.SetToolTip("Px to load to - 3 - 1000")

        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('loadType',self.loadType_combo.GetSelection(), 'RETRIEVAL') # save setting in config file
    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        
    def catRefresh(self, event=0):
        
        global RELEASE
        RELEASE = self.release.GetValue()
        TBL_CATALOG = SQLLib.sqlSelect(iStro, "TBL_CATALOG")
        TBL_CATALOG.setWhereValueString("RELEASE_", RELEASE)
        TBL_CATALOG.setReturnCol("CATALOG")
        TBL_CATALOG.setSortCol("CATALOG",1) # -ve is desc, +ve is ascending
        records = TBL_CATALOG.selectRecordSet()
        self.catalogues=[]
        
        for catalogue in records.itermap():
            #print(f'catalogue={catalogue}')
            self.catalogues.append(catalogue['CATALOG'])
        #
        self.catalogue.Clear()
        self.catalogue.SetItems(self.catalogues)
        self.catalogue.SetSelection(0)
        
        gl_cfg.setItem('release',self.release.GetSelection(), 'RETRIEVAL') # save setting in config file
        
    def releaseRefresh(self, event=0):
        
        global RELEASE
        #RELEASE = self.release.GetValue()
        TBL_RELEASE = SQLLib.sqlSelect(iStro, "TBL_RELEASE")
        #TBL_RELEASE.setWhereValueString("RELEASE_", RELEASE)
        TBL_RELEASE.setReturnCol("RELEASE_")
        TBL_RELEASE.setSortCol("RELEASE_",1) # -ve is desc, +ve is ascending
        records = TBL_RELEASE.selectRecordSet()
        self.releases=[]
        
        for release in records.itermap():
            self.releases.append(release['RELEASE_'])
        #
        self.release.Clear()
        self.release.SetItems(self.releases)
        #
        #gl_cfg.getItem('release', 'RETRIEVAL') # Get setting in config file
        self.release.SetSelection(int(gl_cfg.getItem('release', 'RETRIEVAL'))) # Get setting from config file
        return self.releases
        
    def read_csv(self, event):

        self.button1.Disable()
        
        
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('loadType',self.loadType_combo.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('value',self.spin_loadType.GetValue(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
                
        global xdata2
        global ydata2_1D
        global ydata2
        global xdata2Log
        global ydata2Log

        # Initialise arrays and variables
        self.parent.status=[]  
        self.parent.binaryDetail=[] 
        self.parent.X={}
        self.parent.Y={}
        self.listctrl.DeleteAllItems()
        self.parent.export=[]
        
        if hasattr(self.parent,"selectedStarBinaryMappings"):
            self.parent.selectedStarBinaryMappings={}
        else:
            setattr(self.parent,"selectedStarBinaryMappings", {} )
        if hasattr(self.parent,"selectedStarIDs"):
            self.parent.selectedStarIDs=[] 
        else:
            setattr(self.parent,"selectedStarIDs", []  )
            
        global ROWCOUNTMATRIX
        ROWCOUNTMATRIX={
            'ADQL':0,
            'UN':0,
            'BIN2':0,
            'UN':0,
            'R0':0,
            'V0':0,
            'RVFILTER':0,
            'PXFILTER':0,
            'PMFILTER':0,
            'BIN':0
        }
        
        
        # Select query data
                        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        healpix=2**35*4**(12-2)*i  # From Gaia website
        
        commentHP='--'
        commentRA='--'
        commentDec='--'
        commentPx='--'
        commentRVnotGroup='--'
        commentGroupedandUngroupedwithRV='--'
        commentRVandRVnullUngrouped='--'
        
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i  # From Gaia website
            commentHP=''
        if self.loadType_combo.GetSelection()==1:
            commentRA=''
        if self.loadType_combo.GetSelection()==2:
            commentDec=''
        if self.loadType_combo.GetSelection()==3:
            commentPx=''
        # Load everything (very slow)
        if self.rvnullCheckBox.GetValue()==True and self.unGroupedCheckBox.GetValue()==True:
            pass
        # We want only unclustered binaries with radial velocity (default - quickest)
        if self.rvnullCheckBox.GetValue()==False and self.unGroupedCheckBox.GetValue()==False:
            commentRVnotGroup=''
        # We want all group data for binaries with radial velocity
        if self.rvnullCheckBox.GetValue()==False and self.unGroupedCheckBox.GetValue()==True:
            commentGroupedandUngroupedwithRV=''
        # We want all RV data for ungrouped binaries
        if self.rvnullCheckBox.GetValue()==True and self.unGroupedCheckBox.GetValue()==False:
            commentRVandRVnullUngrouped=''
            
        querySQL = f"""SELECT DISTINCT b.RELEASE_, b.CATALOG, b.STATUS, b.SOURCE_ID_PRIMARY, b.SOURCE_ID_SECONDARY, b.SEPARATION, b.NOT_GROUPED, b.HAS_RADIAL_VELOCITY, b.HEALPIX,
        
        o1.SOURCE_ID, o1.RA_, o1.RA_ERROR, o1.DEC_, o1.DEC_ERROR,
                        o1.PARALLAX, o1.PARALLAX_ERROR, o1.PHOT_G_MEAN_MAG, o1.BP_RP, o1.RADIAL_VELOCITY,
                        o1.RADIAL_VELOCITY_ERROR, o1.PHOT_VARIABLE_FLAG, o1.TEFF_VAL, o1.A_G_VAL,
                        o1.PMRA, o1.PMRA_ERROR, o1.PMDEC, o1.PMDEC_ERROR, o1.RELEASE_, o1.RUWE,
                        1000/o1.PARALLAX as DIST,
                        
        o2.SOURCE_ID, o2.RA_, o2.RA_ERROR, o2.DEC_, o2.DEC_ERROR,
                        o2.PARALLAX, o2.PARALLAX_ERROR, o2.PHOT_G_MEAN_MAG, o2.BP_RP, o2.RADIAL_VELOCITY,
                        o2.RADIAL_VELOCITY_ERROR, o2.PHOT_VARIABLE_FLAG, o2.TEFF_VAL, o2.A_G_VAL,
                        o2.PMRA, o2.PMRA_ERROR, o2.PMDEC, o2.PMDEC_ERROR, o2.RELEASE_, o2.RUWE,
                        1000/o2.PARALLAX as DIST
        FROM TBL_BINARIES b
            left join TBL_OBJECTS o1
                on b.SOURCE_ID_PRIMARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_
            left join TBL_OBJECTS o2
                on b.SOURCE_ID_SECONDARY=o2.SOURCE_ID and b.RELEASE_ = o2.RELEASE_
        WHERE b.CATALOG = '{CATALOG}' 
            and b.release_ = '{RELEASE}'
            {commentHP} and SOURCE_ID_PRIMARY < {healpix}
            {commentRA} and o1.RA_ < {i}  and o2.RA_ < {i}
            {commentPx} and o1.PARALLAX > {i} and o2.PARALLAX > {i}
            {commentDec} and o1.DEC_ < {i}  and o2.DEC_ < {i} and o1.DEC_ > {-i}  and o2.DEC_ > {-i}
            {commentRVnotGroup} and b.HAS_RADIAL_VELOCITY = True and b.NOT_GROUPED = True
            {commentGroupedandUngroupedwithRV} and b.HAS_RADIAL_VELOCITY = True 
            {commentRVandRVnullUngrouped} and b.NOT_GROUPED = True 
 
        --    and b.SOURCE_ID_PRIMARY < b.SOURCE_ID_SECONDARY
            
        ORDER BY SOURCE_ID_PRIMARY asc
        
        """
        
        print (querySQL)
        recordsAll = pd.read_sql(querySQL, iStro)
        i=0
        lenArray=len(recordsAll)
        print(f'lenArray={lenArray}')
        self.parent.starSystemList=binaryStarSystems(lenArray)
        
        records=recordsAll.iloc[:,range(9)]
        X=recordsAll.iloc[:,range(9,30)]
        Y=recordsAll.iloc[:,range(30,51)]
        records=records.convert_dtypes()
        #recordsAll=recordsAll.convert_dtypes()
        del recordsAll
        X=X.convert_dtypes()
        Y=Y.convert_dtypes()
        for index, row  in records.iterrows():
            i=i+1
            if not index % 100:
                label=float(100 * index /lenArray)
                self.button1.SetLabel(f'{label:,.1f}%')
                self.static_Total.SetLabel(f'{index:,} of {lenArray:,}')
                if not math.log10(index) % 1:
                    self.layout()
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    self.button1.Enable()
                    return
                wx.Yield()
            if str(row.STATUS) == '<NA>':
                status=''
            else:
                status=str(row.STATUS)
            #Only display first 1000
            if index<1000:
                try:
                    if str(row.STATUS) == '<NA>':
                        status=''
                    else:
                        status=str(row.STATUS)
                except Exception:
                    status = ''
                try:
                    if row.NOT_GROUPED == True:
                        notGrouped='True'
                        notGroupedBool=True
                    else:
                        notGrouped='False'
                        notGroupedBool=False
                except Exception:
                    notGrouped = 'Not Avail.'
                    notGroupedBool=False
                try:
                    if row.HAS_RADIAL_VELOCITY == True:
                        hasRadialVelocity='True'
                        hasRadialVelocityBool='True'
                    else:
                        hasRadialVelocity='False'
                        hasRadialVelocityBool=False
                except Exception:
                    hasRadialVelocity = 'Not Avail.'
                    hasRadialVelocityBool=False
                try:
                    separation = str(float(row.SEPARATION))
                except Exception:
                    separation = 'Not Avail.'
                try:
                    healpix = str(int(float(row.HEALPIX)))
                except Exception:
                    healpix = 'Not Avail.'
                self.listctrl.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, index, separation, notGrouped, hasRadialVelocity,status, row.RELEASE_, row.CATALOG, healpix])
            
            #  The 'notgroup' flag indicates that the stars in the system don't occur in other binaries too.
            notgroup=1
            
            #  The 'radialvelocity' flag indicates that the stars in the system each have radial velocities.
            radialvelocity=1
            
            #  The 'include' flag indicates that the binary will be part of the final plot.
            include=1
            
            try:
                if row.STATUS=='dupl':
                    notgroup=0
                    include=0
            except Exception:
                pass
            
            try:
                if row.STATUS=='rv=0':
                    radialvelocity=0
                    include=0
            except Exception:
                pass
                
            if len(self.parent.status)<=index:
                self.parent.status.append([include, notgroup,radialvelocity])
            else:
                self.parent.status[index-1]=[include, notgroup,radialvelocity]
                
            
            R=0
            V=0
            Verr=0
            try:
                #Check for primary/companion
                if X.PHOT_G_MEAN_MAG.iloc[index]<Y.PHOT_G_MEAN_MAG.iloc[index]:
                    # Add first star (primary star)
                    self.parent.starSystemList.addSystem(X.iloc[index], i)
                    #
                    # Add second star (companion star)
                    (ccdm, R, V, Verr, M, BIN) = self.parent.starSystemList.addSystem(Y.iloc[index], i)
                else:
                    # Add first star in reverse order (primary star)
                    self.parent.starSystemList.addSystem(Y.iloc[index], i)
                    #
                    # Add second star in reverse order  (companion star)
                    (ccdm, R, V, Verr, M, BIN) = self.parent.starSystemList.addSystem(X.iloc[index], i)
            except Exception:
                # Add first star (primary star)
                self.parent.starSystemList.addSystem(X.iloc[index], i)
                #
                # Add second star (companion star)
                (ccdm, R, V, Verr, M, BIN) = self.parent.starSystemList.addSystem(Y.iloc[index], i)
                include=0
            
            primaryPointer=self.parent.starSystemList.binaryList[str(index+1)].primary
            star2Pointer=self.parent.starSystemList.binaryList[str(index+1)].star2
            self.parent.selectedStarIDs.append(primaryPointer.SOURCE_ID)
            self.parent.selectedStarIDs.append(star2Pointer.SOURCE_ID)
            self.parent.selectedStarBinaryMappings[i]={
                'SOURCE_ID_PRIMARY':int(primaryPointer.SOURCE_ID),
                'SOURCE_ID_SECONDARY':int(star2Pointer.SOURCE_ID),
                'STATUS':status,
                'HAS_RADIAL_VELOCITY':hasRadialVelocityBool,
                'NOT_GROUPED':notGroupedBool,
                'SEPARATION':separation,
                'CATALOG':CATALOG,
                'RELEASE_':RELEASE,
                'HEALPIX':healpix
                
            }
            if BIN:
                ROWCOUNTMATRIX['BIN2']=ROWCOUNTMATRIX['BIN2']+1
                if not (R > 0 and not math.isnan(R)):
                    ROWCOUNTMATRIX['R0']=ROWCOUNTMATRIX['R0']+1
                elif not (float(V[0]) > 0 and not float(math.isnan(V[0]))):
                    ROWCOUNTMATRIX['V0']=ROWCOUNTMATRIX['V0']+1
                elif not (float(Verr[0]) > 0 and not float(math.isnan(Verr[0]))):
                    ROWCOUNTMATRIX['VerrGTV']=ROWCOUNTMATRIX['VerrGTV']+1
            else:
                ROWCOUNTMATRIX['UN']=ROWCOUNTMATRIX['UN']+1
        
            #try:
            if not isinstance(self.parent.selectedStarIDs, list):
                print("self.parent.selectedStarIDs is not list")
                exit()
            if not isinstance(self.parent.selectedStarIDs, list):
                print("self.parent.selectedStarIDs is not list")
                exit()
            if not isinstance(self.parent.X, dict):
                print("self.parent.X is not list")
                exit()
            if not isinstance(self.parent.Y, dict):
                print("self.parent.Y is not list")
                exit()
            if not isinstance(self.parent.binaryDetail, list):
                print("self.parent.binaryDetail_ is not list")
                exit()
            try:
                XRUWE=float(self.parent.starSystemList.binaryList[str(index+1)].primary.RUWE)
            except:
                XRUWE=0
            try:
                YRUWE=float(self.parent.starSystemList.binaryList[str(index+1)].star2.RUWE)
            except:
                YRUWE=0

            try:
                self.parent.X[index] = {
                    'ra':float(self.parent.starSystemList.binaryList[str(index+1)].primary.RA_),
                    'dec':float(self.parent.starSystemList.binaryList[str(index+1)].primary.DEC_),
                    'BminusR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.BP_RP),
                    'mag':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PHOT_G_MEAN_MAG-5*math.log10(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST/10)),
                    'PMRA':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PMRA),
                    'PMRA_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PMRA_ERROR),
                    'PMDEC':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PMDEC),
                    'PMDEC_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PMDEC_ERROR),
                    'PARALLAX':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PARALLAX),
                    'PARALLAX_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.PARALLAX_ERROR),
                    'DIST':float(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST),
                    'RUWE':XRUWE
                    }
            except Exception:
                    print (f'Skipped record {index}')
                    #row=row.transpose()
                    print('Error 1', row)
                    print(index)
                    print(X[:index+2])
                    print(Y[:index+2])
                    print(records[:int(index+2)])
                    self.button1.SetBackgroundColour(Colour(150,20,20))
                    self.button1.Enable()
                    return
            try:
                self.parent.Y[index] ={
                    'ra':float(self.parent.starSystemList.binaryList[str(index+1)].star2.RA_),
                    'dec':float(self.parent.starSystemList.binaryList[str(index+1)].star2.DEC_),
                    'BminusR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.BP_RP),
                    'mag':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PHOT_G_MEAN_MAG-5*math.log10(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST/10)),
                    'PMRA':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PMRA),
                    'PMRA_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PMRA_ERROR),
                    'PMDEC':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PMDEC),
                    'PMDEC_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PMDEC_ERROR),
                    'PARALLAX':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PARALLAX),
                    'PARALLAX_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.PARALLAX_ERROR),
                    'DIST':float(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST),
                    'RUWE':YRUWE}
            except Exception:
                    print (f'Skipped record {index}')
                    #row=row.transpose()
                    print('Error 2', row)
                    print(index)
                    print(X[:index+2])
                    print(Y[:index+2])
                    print(records[:int(index+2)])
                    self.button1.SetBackgroundColour(Colour(150,20,20))
                    self.button1.Enable()
                    return
            self.parent.binaryDetail.append ([R, V[0], Verr[0], V[1], Verr[1], M])
            
            if include:
                primaryPointer=self.parent.starSystemList.binaryList[str(index+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(index+1)].star2
                exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.SOURCE_ID),
                    'ra1':float(primaryPointer.RA_),
                    'dec1':float(primaryPointer.DEC_),
                    'mag1':primaryPointer.PHOT_G_MEAN_MAG,
                    'MAG1':self.parent.X[index]['mag'],
                    'PARALLAX1':float(primaryPointer.PARALLAX),
                    'DIST1':float(primaryPointer.DIST),
                    'RUWE1':XRUWE,
                    'SOURCE_ID_SECONDARY':str(star2Pointer.SOURCE_ID),
                    'ra2':float(star2Pointer.RA_),
                    'dec2':float(star2Pointer.DEC_),
                    'mag2':star2Pointer.PHOT_G_MEAN_MAG,
                    'MAG2':self.parent.Y[index]['mag'],
                    'PARALLAX2':float(star2Pointer.PARALLAX),
                    'DIST2':float(star2Pointer.DIST),
                    'RUWE2':YRUWE,
                    'vRA':V[0],
                    'vDEC':V[1],
                    'V2D':math.sqrt(V[0]**2+V[1]**2),
                    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                    'Log10vRA':np.log10(V[0]),
                    'Log10vDEC':np.log10(V[1]),
                    'Log10r':np.log10(R),
                    #'M':M,
                    'r':R
                }
            
                self.parent.export.append(exportRecord)
                

        self.parent.export=pd.DataFrame(self.parent.export)
        self.button1.SetLabel('Import')
        
        ROWCOUNTMATRIX['ADQL']=len(self.parent.selectedStarBinaryMappings)
        self.static_Total.SetLabel(f'{int(len(self.parent.selectedStarIDs)/2):,}')
        print('End')
        
        self.parent.selectedStarIDs=pd.DataFrame(self.parent.selectedStarIDs, columns=['source_id'])
        self.parent.selectedStarBinaryMappings=pd.DataFrame.from_dict(self.parent.selectedStarBinaryMappings, orient='index')#, columns=['i', 'SOURCE_ID_PRIMARY', 'SOURCE_ID_SECONDARY'
        self.parent.status=pd.DataFrame(self.parent.status, columns=['include', 'notgroup', 'radialvelocity'])
        self.parent.status['dataLoadOut']=self.parent.status['include']
        self.parent.status['populateOut']=self.parent.status['include']
        self.parent.status['hrOut']=self.parent.status['include']
        self.parent.status['kineticOut']=self.parent.status['include']
        self.parent.status['ruweExcl']=self.parent.status['include']
        self.parent.binaryDetail=pd.DataFrame(self.parent.binaryDetail, columns=['r','vRA','vRAerr','vDEC','vDECerr', 'M'])
        
        self.parent.X=pd.DataFrame.from_dict(self.parent.X, orient='index') #, columns=['ra','dec','BminusR', 'mag']pd.DataFrame.from_dict(data, orient='index')
        self.parent.Y=pd.DataFrame.from_dict(self.parent.Y, orient='index') #, columns=['ra','dec','BminusR', 'mag'])
        
        self.parent.star_rows=pd.DataFrame.from_dict(self.parent.starSystemList.getStar_rows(), orient='index') #, columns=column_names)
        
        # Save pandas files as pickle files for next time.
        files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','star_rows','X','Y','status','export']
        
        #Check directory exists and create if not.
        if not os.path.isdir(f'bindata'):
            os.mkdir (f'bindata')
        for file in files:
            try:
                x = getattr(self.parent,file)
                x=pd.DataFrame(x)
                x.to_pickle(f'bindata/{file}.saved')
            except Exception:
                print('Error directory failed to save:')
                print (f'bindata/{file}.saved')
                
        # Open file handle
        file_to_store = open('bindata/starSystemList.pickle', 'wb')
        #Save object to file
        pickle.dump(self.parent.starSystemList, file_to_store)  
        # Close file handle
        file_to_store.close()
 
        self.parent.printArrays()
        self.button1.Enable()
        
    def resetStatus(self, event):
        
        self.reset.Disable()
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", True)
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            if i<192:
                TBL_BINARIES.setWhereValueLTInt("SOURCE_ID", healpix)
        print(TBL_BINARIES.updateRecord())
        
        self.reset.Enable()
        
    def deselectRVnull(self, event):
        
        self.rvnull.Disable()
        
        commentHP='--'
        commentRA='--'
        commentDec='--'
        
        i=int(self.spin_loadType.GetValue())
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            commentHP=''
        if self.loadType_combo.GetSelection()==1:
            commentRA=''
        if self.loadType_combo.GetSelection()==2:
            commentDec=''

        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        healpix=2**35*4**(12-2)*i
        
        sql = f"""SELECT b.RELEASE_, b.CATALOG, b.SOURCE_ID_PRIMARY, b.SOURCE_ID_SECONDARY, b.SEPARATION, b.NOT_GROUPED, b.HAS_RADIAL_VELOCITY
                FROM TBL_BINARIES b
                    inner join TBL_OBJECTS o1
                        on b.SOURCE_ID_PRIMARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_
                    inner join TBL_OBJECTS o2
                        on b.SOURCE_ID_SECONDARY=o2.SOURCE_ID and b.RELEASE_ = o2.RELEASE_
                where (o1.RADIAL_VELOCITY is Null
                or o2.RADIAL_VELOCITY is Null) and b.CATALOG = '{CATALOG}' and b.RELEASE_ = '{RELEASE}' and b.HAS_RADIAL_VELOCITY = True
        
            {commentHP} and b.SOURCE_ID_PRIMARY < {healpix}
            {commentRA} and o1.RA_ < {i}  and o2.RA_ < {i}
            {commentDec} and o1.DEC_ < {i}  and o2.DEC_ < {i} and o1.DEC_ > {-i}  and o2.DEC_ > {-i}
            
        ORDER BY SOURCE_ID_PRIMARY asc
        
                """

        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        Array=[] 
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            #self.parent.radialvelocity[index]=0
            Array.append( row.SOURCE_ID_PRIMARY)
            if not index % 200:
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "rv=0")
                TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "rv=0")
                TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                Array=[] 
                label=float(100 * index /lenArray)
                self.rvnull.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    self.rvnull.Enable()
                    return
                wx.Yield()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        
        label=int(100)
        self.rvnull.SetLabel(f'{label:,.1f}%')
        
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
        TBL_BINARIES.setWhereValueString("RELEASE_", RELEASE)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setReturnCol("count(*) as CNT")
        records = TBL_BINARIES.selectRecordSet()
        for row in records:
            #print(f'{row[0]:,}')
            ROWCOUNTMATRIX['RV0']=row[0]
            self.static_RVnull.SetLabel(f'{row[0]:,}')
        self.rvnull.Enable()
        self.Layout()
        
    def OnDeleteSelection(self, event):
        #Move Ba to another catalogue
        self.deleteSelection.Disable()
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        
        whereValue=int(self.spin_loadType.GetValue())
                
        if self.loadType_combo.GetSelection()==0:
            whereValue=2**35*4**(12-2)*whereValue  # From Gaia website
            whereAtt='SOURCE_ID_PRIMARY'
        if self.loadType_combo.GetSelection()==1:
            whereAtt='RA_'
        if self.loadType_combo.GetSelection()==2:
            whereAtt=='DEC_'
        
        TBL_BINARIES = SQLLib.sqlDelete(iStro, "TBL_BINARIES")

        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.setWhereValueLTInt(whereAtt, whereValue)
                
        print(TBL_BINARIES.deleteRecordSet())
        
        self.deleteSelection.Enable()
        
    def moveBineries(self, event):
        #Move Ba to another catalogue
        self.move.Disable()
        
        global RELEASE, CATALOG
        #RELEASE=self.release.GetValue()
        CATALOG_NEW=self.catalogue.GetValue()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("CATALOG", CATALOG_NEW)

        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        #TBL_BINARIES.setWhereAttGTAtt("SOURCE_ID_PRIMARY", "SOURCE_ID_SECONDARY")
                
        print(TBL_BINARIES.updateRecord())
        
        self.move.Enable()
        
    def deselectDuplicates(self, event):
        #Freeze button
        self.ungroup.Disable()
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "ALLSTARS2")
        TBL_BINARIES.setReturnCol("SOURCE_ID")
        TBL_BINARIES.setGroupByCol("SOURCE_ID")
        TBL_BINARIES.setHavingGTInt("COUNT(SOURCE_ID)",1) # Having count > 1 (ie duplicate SOURCE_ID)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", True)
        TBL_BINARIES.setSortCol("SOURCE_ID")

        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            if i<192:
                TBL_BINARIES.setWhereValueLTInt("SOURCE_ID", healpix)
        if self.loadType_combo.GetSelection()==1:
            TBL_BINARIES.setWhereValueLTInt("RA_", i)
        if self.loadType_combo.GetSelection()==2:
            TBL_BINARIES.setWhereValueLTInt("DEC_", i)
            TBL_BINARIES.setWhereValueLTInt(-i, "DEC_")
        
        sql = TBL_BINARIES.getSQL()
        print (sql)
        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        print(f'Ungrouping {lenArray} records started')
        Array=[] 
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            Array.append( row.SOURCE_ID)
            
            if not index % 200:
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "dupl")
                TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "dupl")
                TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                
                Array=[] 
    
                label=float(100 * index /lenArray)
                self.ungroup.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    #Release button
                    self.ungroup.Enable()
                    return
                wx.Yield()
                 
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "dupl")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
        #TBL_BINARIES.setWhereValueInt("SOURCE_ID_PRIMARY", row.SOURCE_ID)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "dupl")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
        TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
        #TBL_BINARIES.setWhereValueInt("SOURCE_ID_SECONDARY", row.SOURCE_ID)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        
        label=int(100)
        self.ungroup.SetLabel(f'{label:,.1f}%')
        
        
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
        TBL_BINARIES.setWhereValueString("RELEASE_", RELEASE)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", False)
        TBL_BINARIES.setReturnCol("count(*) as CNT")
        records = TBL_BINARIES.selectRecordSet()
        for row in records:
            #print(f'{row[0]:,}')
            ROWCOUNTMATRIX['GRP']=row[0]
            self.static_Cluster.SetLabel(f'{row[0]:,}')
        
        #Release button
        self.ungroup.Enable()
        self.Layout()
        
class dataFilter(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=6, hgap=0, rows=3, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings (ie row 1)
                
        self.static_parallax = StaticText(self, label='Px S/N') 
        fgsizer.Add(self.static_parallax, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for PMRA and PMDEC
        self.pmsnratio = StaticText(self, label='pm S/N') 
        fgsizer.Add(self.pmsnratio, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Difference in radial veocities between the two stars.
        self.static_diff_radial_velocity = StaticText(self, label='diff in rad. vel.') 
        fgsizer.Add(self.static_diff_radial_velocity, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_ruwe = StaticText(self, label='RUWE') 
        fgsizer.Add(self.static_ruwe, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_InOut = StaticText(self, label='Inner/outer') 
        fgsizer.Add(self.static_InOut, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_distCutoff = StaticText(self, label='Dist. cutoff') 
        fgsizer.Add(self.static_distCutoff, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_parallax_SN = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxsn_gt','FILTER')))  
        fgsizer.Add(self.spin_parallax_SN, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_parallax_SN.SetToolTip("Signal to noise ratio for Parallax (ie Px/error) in either star.")
        
        # Signal to noise ratio for PMRA and PMDEC
        self.spin_pmsnratio = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pmsn_gt','FILTER')))
        fgsizer.Add(self.spin_pmsnratio, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_pmsnratio.SetToolTip("Signal to noise ratio for PMRA and PMDEC (ie PM/error) in either star.")

        #Diffence in radial velocities between primary and companion stars.
        self.spin_diff_radial_velocity = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=99,initial=int(gl_cfg.getItem('rv_lt','FILTER')))
        fgsizer.Add(self.spin_diff_radial_velocity, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_diff_radial_velocity.SetToolTip("Difference in radial velocities between primary and companion stars.")
        
        #Max RUWE.
        self.text_ruwe = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('ruwe_lt','FILTER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_ruwe, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_ruwe.SetToolTip("Maximum RUWE in either star.  Enter decimal x for RUWE < x")
        
        self.combo_InOut = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['Inner','Outer'], value='')
        self.combo_InOut.SetSelection(int(gl_cfg.getItem('io','FILTER')))
        fgsizer.Add(self.combo_InOut, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.combo_InOut.SetToolTip("Stars inside or outside the distance cutoff")
        
        #Distance cutoff.
        self.spin_distCutoff = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=333,initial=int(gl_cfg.getItem('cutoff','FILTER')))  
        fgsizer.Add(self.spin_distCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_distCutoff.SetToolTip("Distance cutoff in pc.")
        
        self.SetSizer(self.sizer_v)
                
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        #
        self.loadData = Button(self, wx.ID_ANY, u"Filter data")
        self.loadData.Bind(wx.EVT_LEFT_DOWN, self.populateListctrl)
        fgsizer.Add(self.loadData, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel filter.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Filter Reset button
        
        self.Reset_but = Button(self, id=wx.ID_ANY, label="&Reset", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.Reset_but.Bind(wx.EVT_BUTTON, self.OnReset)
        fgsizer.Add(self.Reset_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        
        # Import Total prompt
        
        dataInTotal = StaticText(self, id=wx.ID_ANY, label="Total pairs:")
        fgsizer.Add(dataInTotal, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Total
        
        populateOut=0
        try:
            populateOut=self.parent.status['populateOut'].sum()
        except Exception:
            pass
        
        self.dataInTotal = StaticText(self, id=wx.ID_ANY, label=f'{populateOut:,}')
        fgsizer.Add(self.dataInTotal, 0, wx.ALL, 5)
        
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(1920,600), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
        self.listctrl.InsertColumn(0, u"Gaia %s Source ID" % RELEASE, width=180)
        self.listctrl.InsertColumn(1, u"pairing number", width=120)
        self.listctrl.InsertColumn(2, u"ra", width=100)
        self.listctrl.InsertColumn(3, u"ra_error", width=100)
        self.listctrl.InsertColumn(4, u"dec", width=100)
        self.listctrl.InsertColumn(5, u"dec error", width=100)
        self.listctrl.InsertColumn(6, u"parallax", width=100)
        self.listctrl.InsertColumn(7, u"px err", width=100)
        self.listctrl.InsertColumn(8, u"pmra", width=100)
        self.listctrl.InsertColumn(9, u"pmra err", width=100)
        self.listctrl.InsertColumn(10, u"pmdec", width=100)
        self.listctrl.InsertColumn(11, u"pmdec err", width=100)
        self.listctrl.InsertColumn(12, u"RUWE", width=100)
        self.listctrl.InsertColumn(13, u"Rad. Vel", width=100)
        self.listctrl.InsertColumn(14, u"Exclude", width=100)
        self.listctrl.InsertColumn(15, u"Release", width=100)

        self.sizer_v.Add(self.listctrl, 0, wx.TOP | wx.BOTTOM , 10)
        self.sizer_v.Add(hsizer1, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.sizer_v.Add(hsizer2, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        self.restoreListCtrl()
        
        self.Layout()

    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        
    def OnReset(self, event=0):
        self.parent.status=pd.DataFrame(self.parent.status)
        self.parent.status['include']=self.parent.status['dataLoadOut']
        self.parent.status['populateOut']=self.parent.status['dataLoadOut']
        self.parent.status['hrOut']=self.parent.status['dataLoadOut']
        self.parent.status['kineticOut']=self.parent.status['dataLoadOut']
        
    def populateListctrl(self, event):
        # This routine populates the StarList List Control and filters for Radial velocity and signal to
        # noise ratios for proper motion and paralax.
        gl_cfg.setItem('pxsn_gt',self.spin_parallax_SN.GetValue(),'FILTER')
        gl_cfg.setItem('pmsn_gt',self.spin_pmsnratio.GetValue(),'FILTER')
        gl_cfg.setItem('rv_lt',self.spin_diff_radial_velocity.GetValue(),'FILTER')
        gl_cfg.setItem('ruwe_lt',self.text_ruwe.GetValue(),'FILTER')
        gl_cfg.setItem('io',self.combo_InOut.GetSelection(),'FILTER')
        gl_cfg.setItem('cutoff',self.spin_distCutoff.GetValue(),'FILTER')
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
       
        self.loadData.Disable() #Disable the button to avoid being pressed twice
        
        self.parent.export=[]
        self.listctrl.DeleteAllItems() # clear the control
        self.parent.star_rows=pd.read_pickle('bindata/star_rows.saved') # Pick up most recent starlist if changed.
        selectedStarBinaryMappings=self.parent.selectedStarBinaryMappings 
        star_rows=self.parent.star_rows
        self.OnReset()  # Reset starting point to end of data load.
        
        #
        #Initialise variables
        #

        lenArray=len(self.parent.selectedStarIDs)
        
        ROWCOUNTMATRIX={
            'ADQL':0,
            'UN':0,
            'BIN2':0,
            'UN':0,
            'GRP':0,
            'R0':0,
            'V0':0,
            'RVFILTER':0,
            'PXFILTER':0,
            'PMFILTER':0,
            'BIN':0
        }
        rv=0
        rv1=0
        radialvelocity=1
        ROWCOUNTMATRIX['ADQL']=lenArray /2  # Number of binaries
        sn_px_limit=float(self.spin_parallax_SN.GetValue())
        sn_pm_limit=float(self.spin_pmsnratio.GetValue())
        distCutoff_limit=float(self.spin_distCutoff.GetValue())
        outerShell=bool(self.combo_InOut.GetSelection())
        ruwe_limit=float(self.text_ruwe.GetValue())
        
        rv_diff_limit=float(self.spin_diff_radial_velocity.GetValue())
        idxBin=0   # Binary index (obviously there are 2x as many stars as binaries)
        star_rows=star_rows.convert_dtypes()
        
        concat_df = pd.concat([self.parent.status,self.parent.status]).sort_index().reset_index(drop=True)
        #Filter out currently inluded rows only
        indexStatus = concat_df.index
        condition = concat_df.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        
        for index in statusIndicesList:
        #for index, row in star_rows.iterrows():
            idxBin=int(index/2)
            row=star_rows.iloc[index]
            
            if not index % 100:
                label=float(100 * index /(lenArray))
                self.loadData.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    self.loadData.Enable()
                    return
                wx.Yield()
            # We can skip this code after n>1000
            if self.parent.status.include[idxBin]==0 and index>1000:
                continue
            try:
                if selectedStarBinaryMappings.SOURCE_ID_PRIMARY.iloc[row.PAIRING-1] == int(row.SOURCE_ID):
                    #print('Here 1')
                    #  Primary star found reset include/notgroup/exclude and RV
                    include=1
                    excludeTxt=''
                    radialvelocity=1
                    
                    try:
                        rv=float(row.RADIAL_VELOCITY)
                    except Exception:
                        rv=0
                        include=0
                        excludeTxt='rv=0'
                        radialvelocity=0
                    rv1=rv
                else:
                    #print('Here 2')
                    # ...  or secondary
                    if selectedStarBinaryMappings.SOURCE_ID_SECONDARY.iloc[row.PAIRING-1] == int(row.SOURCE_ID):
                        #print('Here 2a')
                        try:
                            rv=float(row.RADIAL_VELOCITY)
                        except Exception:
                            rv=0
                            include=0
                            excludeTxt='rv=0'
                            radialvelocity=0
                        # Must all exist
                        if rv_diff_limit and rv and rv1:
                            sn_row=abs(float(rv1-rv))
                            if sn_row>rv_diff_limit:
                                excludeTxt=f'RV diff={int(sn_row)}'
                                include=0
                    else:
                        print (f'Skipped record {index}')
                        row=row.transpose()
                        print(1, row)
                        print(index)
                        print(star_rows[:index+2])
                        print(selectedStarBinaryMappings[:int(index/2+2)])
                        self.loadData.SetBackgroundColour(Colour(150,20,20))
                        self.loadData.Enable()
                        return
                        #continue
            except Exception:
                print(2, row)
                print(f'index = {index}')
                #print(star_rows)
                print(star_rows[:index+5])
                self.loadData.SetBackgroundColour(Colour(150,20,20))
                self.loadData.Enable()
                return
                
            if math.isnan(float(rv)) or math.isnan(float(rv1)):
                include=0
                excludeTxt='rv=0'
                radialvelocity=0
            
            # Check and set radial velocity
            if not radialvelocity:
                include=0
                excludeTxt=f'rv=0'
                self.parent.status.radialvelocity[idxBin]=radialvelocity
                
            try:
                ruwe=float(row.RUWE)
            except Exception:
                ruwe=0
                
            if include:
                dist_row=abs(float(row.DIST))
                if sn_px_limit and include:
                    sn_row=abs(float(row.PARALLAX)/float(row.PARALLAX_ERROR))
                    if sn_px_limit>sn_row:
                        excludeTxt=f'SN_PX={int(sn_row)}'
                        include=0
            #Cut off inner or outer stars iside or outside limit
            #if include:
                dist_row=abs(float(row.DIST))
                if outerShell and dist_row<distCutoff_limit:
                    excludeTxt=f'Inside shell'
                    include=0
                if not outerShell and dist_row>distCutoff_limit:
                    excludeTxt=f'Outer shell'
                    include=0
                    
                if sn_pm_limit:
                    sn_row=abs(float(row.PMRA)/float(row.PMRA_ERROR))
                    if sn_pm_limit>sn_row:
                        excludeTxt=f'SN_PMRA={int(sn_row)}'
                        include=0
                    sn_row=abs(float(row.PMDEC)/float(row.PMDEC_ERROR))
                    if sn_pm_limit>sn_row and include:
                        excludeTxt=f'SN_PMDEC={int(sn_row)}'
                        include=0

                if ruwe_limit:
                    ruwe_row=abs(ruwe)
                    if ruwe_row>ruwe_limit:
                        excludeTxt=f'RUWE={round(float(ruwe_row),2)}'
                        include=0 
                        self.parent.status.ruweExcl[idxBin]=0

            if not include:
                self.parent.status.include[idxBin]=0
            odd=(index-2*idxBin)
            if odd and self.parent.status.include[idxBin]:
                primaryPointer=self.parent.starSystemList.binaryList[str(idxBin+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(idxBin+1)].star2
                exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.SOURCE_ID),
                    'ra1':float(primaryPointer.RA_),
                    'dec1':float(primaryPointer.DEC_),
                    'mag1':primaryPointer.PHOT_G_MEAN_MAG,
                    'MAG1':self.parent.X.mag[idxBin],
                    'PARALLAX1':float(primaryPointer.PARALLAX),
                    'DIST1':float(primaryPointer.DIST),
                    'RUWE1':primaryPointer.RUWE,
                    'SOURCE_ID_SECONDARY':str(star2Pointer.SOURCE_ID),
                    'ra2':float(star2Pointer.RA_),
                    'dec2':float(star2Pointer.DEC_),
                    'mag2':star2Pointer.PHOT_G_MEAN_MAG,
                    'MAG2':self.parent.Y.mag[idxBin],
                    'PARALLAX2':float(star2Pointer.PARALLAX),
                    'DIST2':float(star2Pointer.DIST),
                    'RUWE2':star2Pointer.RUWE,
                    'vRA':self.parent.binaryDetail.vRA[idxBin],
                    'vDEC':self.parent.binaryDetail.vDEC[idxBin],                    
                    'V2D':math.sqrt(self.parent.binaryDetail.vRA[idxBin]**2+self.parent.binaryDetail.vDEC[idxBin]**2),
                    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                    'Log10vRA':np.log10(abs(self.parent.binaryDetail.vRA[idxBin])),
                    'Log10vDEC':np.log10(abs(self.parent.binaryDetail.vDEC[idxBin])),
                    'Log10r':np.log10(self.parent.binaryDetail.r[idxBin]),
                    #'M':M,
                    'r':self.parent.binaryDetail.r[idxBin]
                }
            
                self.parent.export.append(exportRecord)

        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle('bindata/export.saved')   
        self.restoreListCtrl()
        self.loadData.SetLabel(f'100%')
        self.parent.status['populateOut']=self.parent.status['include']
        self.parent.status['hrOut']=self.parent.status['include']
        self.parent.status['kineticOut']=self.parent.status['include']
        self.parent.status.to_pickle('bindata/status.saved')
        populateOut=self.parent.status['populateOut'].sum()
        self.dataInTotal.SetLabel(f'{populateOut:,}')
        self.loadData.Enable()
        self.parent.printArrays()
        
    def restoreListCtrl(self, event=0, limit=1000):
        

        try:
            self.parent.star_rows=self.parent.star_rows.convert_dtypes()
        except Exception:
            pass
            
        for index, row  in self.parent.star_rows.iterrows():
            if index>limit:
                break
            try:
                rv=float(row.RADIAL_VELOCITY)
            except Exception:
                rv=0
                include=0
                excludeTxt='rv=0'
                radialvelocity=0
            try:
                ruwe=float(row.RUWE)
            except Exception:
                ruwe=0
            try:
                self.listctrl.Append([int(row.SOURCE_ID), int(row.PAIRING),float(row.RA_),float(row.RA_ERROR), float(row.DEC_) ,float(row.DEC_ERROR), float(row.PARALLAX) ,float(row.PARALLAX_ERROR), float(row.PMRA),float(row.PMRA_ERROR), float(row.PMDEC),float(row.PMDEC_ERROR),ruwe,rv, '',row.RELEASE_])
            except Exception:
                print(self.parent.star_rows)
                print('"star_rows" Error')
    
    def OnQuery(self, event=0):
                
        query=[0]
                       
        selectFrom = """SELECT
            gaia_source.source_id,
            gaia_source.ra,
            gaia_source.ra_error,
            gaia_source.dec,
            gaia_source.dec_error,
            (1000/TO_REAL(gaia_source.parallax)) as dist,
            gaia_source.parallax,
            gaia_source.parallax_error,
            gaia_source.phot_g_mean_mag,
            gaia_source.bp_rp,
            gaia_source.radial_velocity,
            gaia_source.radial_velocity_error,
            gaia_source.phot_variable_flag,
            gaia_source.teff_val,
            gaia_source.a_g_val, 
            gaia_source.pmra,
            gaia_source.PMRA_ERROR, 
            gaia_source.pmdec,
            gaia_source.PMDEC_ERROR,
            hipp.ccdm, hipp.nsys,
            hipp.n_ccdm, 
            hipp.ncomp, hipparcos2_best_neighbour.angular_distance AS angular_distance_between_hipp_gaia
        
            FROM gaiadr2.gaia_source
            LEFT JOIN gaiadr2.hipparcos2_best_neighbour ON gaia_source.source_id = hipparcos2_best_neighbour.source_id
            LEFT JOIN public.hipparcos_newreduction AS hipp2 ON hipp2.hip = hipparcos2_best_neighbour.original_ext_source_id
            LEFT JOIN public.hipparcos AS hipp ON hipp2.hip = hipp.hip
            
        """
        
        query[0] = selectFrom + f"""
        
        WHERE gaiadr2.gaia_source.source_id in ({self.parent.selectedStarIDs})
        
        """
        
        query[0] = query[0].replace("[", "")
        query[0] = query[0].replace("]", "")
        

        gaia_cnxn = da.GaiaDataAccess()
        data = gaia_cnxn.gaia_query_to_pandas(query[0])
        
        now = datetime.datetime.utcnow() # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")
        self.filePrefix=self.csvFile.GetValue()[:-3] + date_time
        gaia_cnxn.data_save_pickle(data, self.filePrefix)


class skyDataPlotting(wx.Panel):

# Plot position on sky for chosen binaries.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_v)
        fgsizer = wx.FlexGridSizer(cols=12, hgap=0, rows=2, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Create unselected data check box
        unselectedStaticText = StaticText(self, id=wx.ID_ANY, label="Show unselected")
        fgsizer.Add(unselectedStaticText, 0, wx.ALL, 2)
        self.unselectedCheckBox = CheckBox(self)
        self.unselectedCheckBox.SetToolTip("Show unselected binaries in green or grey.")
        self.unselectedCheckBox.SetValue(gl_cfg.getBoolean('unselected', 'SKYPLOT'))
        fgsizer.Add(self.unselectedCheckBox, 0, wx.ALL, 2)
        
        # Create suppress groups data check box
        suppressGroupsStaticText = StaticText(self, id=wx.ID_ANY, label="suppress groups")
        fgsizer.Add(suppressGroupsStaticText, 0, wx.ALL, 2)
        self.suppressGroupsCheckBox = CheckBox(self)
        self.suppressGroupsCheckBox.SetToolTip("suppress groups from unselected binaries.")
        self.suppressGroupsCheckBox.SetValue(gl_cfg.getBoolean('suppressgroups', 'SKYPLOT'))
        fgsizer.Add(self.suppressGroupsCheckBox, 0, wx.ALL, 2)

        # Create suppress RV=0 data check box
        suppressRVZeroStaticText = StaticText(self, id=wx.ID_ANY, label="suppress RV=0")
        fgsizer.Add(suppressRVZeroStaticText, 0, wx.ALL, 2)
        self.suppressRVZeroCheckBox = CheckBox(self)
        self.suppressRVZeroCheckBox.SetToolTip("suppress binaries without radial velocities.")
        self.suppressRVZeroCheckBox.SetValue(gl_cfg.getBoolean('suppressrvzero', 'SKYPLOT'))
        fgsizer.Add(self.suppressRVZeroCheckBox, 0, wx.ALL, 2)

        # Create 'all white' check box
        allWhiteStaticText = StaticText(self, id=wx.ID_ANY, label="Plot monochrome")
        fgsizer.Add(allWhiteStaticText, 0, wx.ALL, 2)
        self.allWhiteCheckBox = CheckBox(self)
        self.allWhiteCheckBox.SetToolTip("Show unselected binaries in white  (or black for print version).  Over-rides green setting.")
        self.allWhiteCheckBox.SetValue(gl_cfg.getBoolean('allwhite', 'SKYPLOT'))
        fgsizer.Add(self.allWhiteCheckBox, 0, wx.ALL, 2)

        # Create show large data points
        largeStaticText = StaticText(self, id=wx.ID_ANY, label="Show large data points")
        fgsizer.Add(largeStaticText, 0, wx.ALL, 2)
        self.largePointsCheckBox = CheckBox(self)
        self.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints', 'SKYPLOT'))
        self.largePointsCheckBox.SetToolTip("Shows larger data points for stars on graph.")
        fgsizer.Add(self.largePointsCheckBox, 0, wx.ALL, 2)
        
        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print Version")
        fgsizer.Add(prntVersion_StaticText, 0, wx.ALL, 2)
        self.prntVersionCheckBox = CheckBox(self)
        self.prntVersionCheckBox.SetToolTip("Produce print version of graph.")
        self.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion', 'SKYPLOT'))
        fgsizer.Add(self.prntVersionCheckBox, 0, wx.ALL, 2)

        # Draw button
        
        self.plot_but = Button(self, id=wx.ID_ANY, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        # Draw imported stars only
        
        self.starsOnly_but = Button(self, id=wx.ID_ANY, label="&Stars Only", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.starsOnly_but.Bind(wx.EVT_BUTTON, self.OnStarsOnly)
        fgsizer.Add(self.starsOnly_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Draw velocity map
        self.skyGraph = matplotlibPanel(parent=self, size=(1350, 750))
        fg2sizer.Add(self.skyGraph)
        
        self.Layout()
        

    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        
    def OnStarsOnly(self, event=0):

        # Draw sky plot
        
        querySQL = f"""SELECT 
            o1.SOURCE_ID, o1.RA_, o1.RA_ERROR, o1.DEC_, o1.PHOT_G_MEAN_MAG
        FROM TBL_Objects o1
                        
        WHERE o1.release_ = '{RELEASE}' and 
        parallax >= 3.0 and
        parallax < 1000 and
        radial_velocity is not Null
        
            
        -- ORDER BY SOURCE_ID asc
        
         """
        
        print (querySQL)
        starsAll = pd.read_sql(querySQL, iStro)
        i=0
        lenArray=len(starsAll)
        
        xdata = starsAll.RA_
        ydata = starsAll.DEC_
        mag = starsAll.PHOT_G_MEAN_MAG

        self.skyGraph.axes.set_ylabel('Declination (deg)', fontsize=FONTSIZE)
        self.skyGraph.axes.set_xlabel('Right Ascension (deg)', fontsize=FONTSIZE)
        self.skyGraph.axes.set_yscale('linear')
        self.skyGraph.axes.set_xscale('linear')
        self.skyGraph.set_limits([360,0],[-90, 90])
        self.skyGraph.axes.grid(b=None, which='minor', axis='both')
        
        # To remove the artist
        for frame in self.skyGraph.frames:
            try:
                Artist.remove(frame)
            except Exception:
                pass
        try:
            self.line.remove()
        except Exception:
            pass
        
        legend1=[] 
        legend2=[] 
        
              
        prntVersion=self.prntVersionCheckBox.GetValue()
        if prntVersion:
            c='black'
            self.skyGraph.axes.set_title("")
            self.skyGraph.axes.patch.set_facecolor('1')  # White shade
        else:
            self.skyGraph.axes.set_title(f"Stars within 333 pcs.  Gaia {RELEASE}.  {lenArray} stars with a non-zero radial velocity.", fontsize=FONTSIZE)
            self.skyGraph.axes.patch.set_facecolor('0.25')  # Grey shade
            c='white'
                
        marker = ','
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
        #Display graph
        self.line, = self.skyGraph.axes.plot(xdata, ydata, color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
    
        legend1.append(self.line)
        self.skyGraph.draw(self.line, xdata, ydata, False, [] )

        #    """
        #Attach a text label above each bar displaying its height
        #"""
        self.skyGraph.frames=[] 
        
        self.skyGraph.Layout()
        self.Layout()

    def OnPlot(self, event=0):

        self.plot_but.Disable()
        self.parent.export=[]
        
        prntVersion=self.prntVersionCheckBox.GetValue()
        gl_cfg.setItem('prntversion',prntVersion, 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('unselected',self.unselectedCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('allwhite',self.allWhiteCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('suppressgroups',self.suppressGroupsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('suppressrvzero',self.suppressRVZeroCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        #
        
        xdata1 = pd.DataFrame(self.parent.X.ra * self.parent.status['include'], columns=['ra'])
        ydata1 = pd.DataFrame(self.parent.X.dec * self.parent.status['include'], columns=['dec'])
        xdata2 = pd.DataFrame(self.parent.X.ra, columns=['ra'])
        ydata2 = pd.DataFrame(self.parent.X.dec, columns=['dec'])

        self.skyGraph.axes.set_ylabel('Declination (deg)', fontsize=FONTSIZE)
        self.skyGraph.axes.set_xlabel('Right Ascension (deg)', fontsize=FONTSIZE)
        self.skyGraph.axes.set_yscale('linear')
        self.skyGraph.axes.set_xscale('linear')
        self.skyGraph.set_limits([360,0],[-90, 90])
        
        try:
            self.line.remove()
        except Exception:
            pass
        try:
            self.line2.remove()
        except Exception:
            pass
        
        legend1=[] 
        legend2=[] 
        
        unselectedBins=0
        if self.unselectedCheckBox.GetValue():
               
            unselectedBins=len(self.parent.status['include'])-self.parent.status['include'].sum()
            if self.allWhiteCheckBox.GetValue():
                c='white'
                if prntVersion:
                    c='black'
            else:
                c='green'
                if prntVersion:
                    c='silver'
                
            if self.suppressGroupsCheckBox.GetValue():
                xdata2.ra = xdata2.ra * self.parent.status['notgroup']
                ydata2.dec = ydata2.dec * self.parent.status['notgroup']
                
            if self.suppressRVZeroCheckBox.GetValue():
                xdata2.ra = xdata2.ra * self.parent.status['radialvelocity']
                ydata2.dec = ydata2.dec * self.parent.status['radialvelocity']
                
            print(f'{xdata2.ra.sum()}')
            print(f'{ydata2.dec.sum()}')
            marker = ','
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
            try:
                self.line2, = self.skyGraph.axes.plot(xdata2.ra.to_list(), ydata2.dec.to_list(), color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
            except Exception as e:
                print (f'self.skyGraph.axes.plot Crash 1) "{e}"')
                print(xdata1)
                print(ydata1)
                self.plot_but.SetBackgroundColour(Colour(150,20,20))
                self.plot_but.Enable()
                return
            
            legend1.append(self.line2)
            legend2.append('unselected')
            self.skyGraph.draw(self.line2, xdata2, ydata2, False, [] )

        if prntVersion:
            c='black'
            self.skyGraph.axes.set_title("")
            self.skyGraph.axes.patch.set_facecolor('1')  # Grey shade
        else:
            self.skyGraph.axes.set_title(f"Binary distribution showing {self.parent.status['include'].sum():,} selected and {unselectedBins:,} unselected from {len(self.parent.status):,}", fontsize=FONTSIZE)
            self.skyGraph.axes.patch.set_facecolor('0.25')  # Grey shade
            c='white'
            
        marker = ','
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
        try:
            self.line, = self.skyGraph.axes.plot(xdata1.ra.to_list(), ydata1.dec.to_list(), color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
        except Exception as e:
            print (f'self.skyGraph.axes.plot Crash 2) "{e}"')
            print(xdata1)
            print(ydata1)
            self.plot_but.SetBackgroundColour(Colour(150,20,20))
            self.plot_but.Enable()
            return
        
        self.skyGraph.draw(self.line, xdata1, ydata1, True,[] )
        #        
            
        self.skyGraph.Layout()
        self.Layout()
        self.parent.printArrays()

        self.plot_but.Enable()
        
class HRDataPlotting(wx.Panel):

# Plot HR diagram for chosen binaries.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_v)
        fgsizer = wx.FlexGridSizer(cols=13, hgap=0, rows=4, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings
        
        self.static_colourLower = StaticText(self, label='Colour (lower)') 
        fgsizer.Add(self.static_colourLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_colourUpper = StaticText(self, label='Colour (upper)') 
        fgsizer.Add(self.static_colourUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_magLower = StaticText(self, label='Mag. lower') 
        fgsizer.Add(self.static_magLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_magUpper = StaticText(self, label='Mag. upper') 
        fgsizer.Add(self.static_magUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_magRange = StaticText(self, label='Mag. range') 
        fgsizer.Add(self.static_magRange, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #fgsizer.AddSpacer(1)
        
        # Create show raw data check box
        unselectedStaticText = StaticText(self, id=wx.ID_ANY, label="Show unselected")
        fgsizer.Add(unselectedStaticText, 0, wx.ALL, 2)
        self.unselectedCheckBox = CheckBox(self)
        self.unselectedCheckBox.SetValue(gl_cfg.getBoolean('unselected', 'HRPLOT'))
        self.unselectedCheckBox.SetToolTip("Show unselected binaries in green or grey.")
        fgsizer.Add(self.unselectedCheckBox, 0, wx.ALL, 2)

        # Create 'all white' check box
        allWhiteStaticText = StaticText(self, id=wx.ID_ANY, label="Plot monochrome")
        fgsizer.Add(allWhiteStaticText, 0, wx.ALL, 2)
        self.allWhiteCheckBox = CheckBox(self)
        self.allWhiteCheckBox.SetToolTip("Show unselected binaries in white (or black for print version). Over-rides green setting.")
        self.allWhiteCheckBox.SetValue(gl_cfg.getBoolean('allwhite', 'HRPLOT'))
        fgsizer.Add(self.allWhiteCheckBox, 0, wx.ALL, 2)
        
        
        # Create show large data points
        largeStaticText = StaticText(self, id=wx.ID_ANY, label="Show large data points")
        fgsizer.Add(largeStaticText, 0, wx.ALL, 2)
        self.largePointsCheckBox = CheckBox(self)
        self.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints', 'HRPLOT'))
        self.largePointsCheckBox.SetToolTip("Shows larger data points for stars on graph.")
        fgsizer.Add(self.largePointsCheckBox, 0, wx.ALL, 2)

        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print Version")
        fgsizer.Add(prntVersion_StaticText, 0, wx.ALL, 2)
        self.prntVersionCheckBox = CheckBox(self)
        self.prntVersionCheckBox.SetToolTip("Produce print version of graph.")
        self.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion', 'HRPLOT'))
        fgsizer.Add(self.prntVersionCheckBox, 0, wx.ALL, 2)

        # Query values
        
        #self.text_colourLower = TextCtrl(self, id=wx.ID_ANY, value="0.9", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT) 
        self.text_colourLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('col_lower', 'HRPLOT'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_colourLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_colourUpper = TextCtrl(self, id=wx.ID_ANY, value="2.3", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_colourUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('col_upper', 'HRPLOT'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_colourUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_magLower = TextCtrl(self, id=wx.ID_ANY, value="5.5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT) 
        #self.text_magLower = TextCtrl(self, id=wx.ID_ANY, value="5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_magLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mag_lower', 'HRPLOT'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_magLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_magUpper = TextCtrl(self, id=wx.ID_ANY, value="9.5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT) 
        #self.text_magUpper = TextCtrl(self, id=wx.ID_ANY, value="8.5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_magUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mag_upper', 'HRPLOT'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_magUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_magRange = TextCtrl(self, id=wx.ID_ANY, value="0.3", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_magRange = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mag_range', 'HRPLOT'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_magRange, 0, wx.ALIGN_LEFT|wx.ALL, 5)
                
        fgsizer.AddSpacer(1)
       
        # Draw button
        
        self.plot_but = Button(self, id=wx.ID_ANY, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # H-R Filter button
        
        self.Filter_but = Button(self, id=wx.ID_ANY, label="&Filter", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.Filter_but.Bind(wx.EVT_BUTTON, self.OnFilter)
        fgsizer.Add(self.Filter_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Cancel Button
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel H-R filter.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # H-R Filter Reset button
        
        self.Reset_but = Button(self, id=wx.ID_ANY, label="&Reset", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.Reset_but.Bind(wx.EVT_BUTTON, self.OnReset)
        fgsizer.Add(self.Reset_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Draw velocity map
        self.hrGraph = matplotlibPanel(parent=self, size=(950, 750))
        fg2sizer.Add(self.hrGraph)
        
        self.Layout()
        

    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        
    def OnReset(self, event=0):
        #if hasattr(self.parent, 'populateOut'):
        self.parent.status['include']=self.parent.status['populateOut']
        self.parent.status['hrOut']=self.parent.status['populateOut']
        self.parent.status['kineticOut']=self.parent.status['populateOut']
            #self.parent.status.include=self.parent.hrResetList['include']
        self.OnPlot()
        
    def OnFilter(self, event=0):
        self.Filter_but.Disable()
        
        self.parent.export=[]
        gl_cfg.setItem('col_lower',self.text_colourLower.GetValue(),'HRPLOT')
        gl_cfg.setItem('col_upper',self.text_colourUpper.GetValue(),'HRPLOT')
        gl_cfg.setItem('mag_lower',self.text_magLower.GetValue(),'HRPLOT')
        gl_cfg.setItem('mag_upper',self.text_magUpper.GetValue(),'HRPLOT')
        gl_cfg.setItem('mag_range',self.text_magRange.GetValue(),'HRPLOT')
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        gl_cfg.setItem('allwhite',self.allWhiteCheckBox.GetValue(), 'HRPLOT') # save setting in config file
        gl_cfg.setItem('unselected',self.unselectedCheckBox.GetValue(), 'HRPLOT') # save setting in config file
        gl_cfg.setItem('prntversion',self.prntVersionCheckBox.GetValue(), 'HRPLOT') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'HRPLOT') # save setting in config file
        self.OnReset()
        colourUpper=float(self.text_colourUpper.GetValue())
        magLower=float(self.text_magLower.GetValue())
        magUpper=float(self.text_magUpper.GetValue())
        colourLower=float(self.text_colourLower.GetValue())
        self.m=(magLower-magUpper)/(colourLower-colourUpper)
        self.c=magUpper - colourUpper*self.m
        self.Yerr = float(self.text_magRange.GetValue())
                
        lenArray=len(self.parent.status)
        self.parent.X=self.parent.X.convert_dtypes()
        self.parent.Y=self.parent.Y.convert_dtypes()
        #Filter out currently inluded rows only
        indexStatus = self.parent.status.index
        condition = self.parent.status.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        
        for index in statusIndicesList:
        #for index, X1 in self.parent.X.iterrows():
            X1=self.parent.X.iloc[index]
            X2=self.parent.Y.iloc[index]
            include=float(self.parent.status.include[index])
            if not include:
                continue
            if not index % 100:
                label=float(100 * index /lenArray)
                self.Filter_but.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    self.Filter_but.Enable()
                    return
                wx.Yield()
            (Yup, Ydown)=self.XreturnY(X1.BminusR)
            if float(X1.mag) < Yup or float(X1.mag) > Ydown or float(X1.BminusR) < colourLower or float(X1.BminusR) > colourUpper :
                self.parent.status.include[index]=0
                continue
            
            (Yup, Ydown)=self.XreturnY(X2.BminusR)
            if float(X2.mag) < Yup or float(X2.mag) > Ydown or float(X2.BminusR) < colourLower or float(X2.BminusR) > colourUpper :
                self.parent.status.include[index]=0
                continue
                primaryPointer=self.parent.starSystemList.binaryList[str(index+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(index+1)].star2
                exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.SOURCE_ID),
                    'ra1':float(primaryPointer.RA_),
                    'dec1':float(primaryPointer.DEC_),
                    'mag1':primaryPointer.PHOT_G_MEAN_MAG,
                    'MAG1':self.parent.X.mag[index],
                    'PARALLAX1':float(primaryPointer.PARALLAX),
                    'DIST1':float(primaryPointer.DIST),
                    'RUWE1':primaryPointer.RUWE,
                    'SOURCE_ID_SECONDARY':str(star2Pointer.SOURCE_ID),
                    'ra2':float(star2Pointer.RA_),
                    'dec2':float(star2Pointer.DEC_),
                    'mag2':star2Pointer.PHOT_G_MEAN_MAG,
                    'MAG2':self.parent.Y.mag[index],
                    'PARALLAX2':float(star2Pointer.PARALLAX),
                    'DIST2':float(star2Pointer.DIST),
                    'RUWE2':star2Pointer.RUWE,
                    'vRA':self.parent.binaryDetail.vRA[index],
                    'vDEC':self.parent.binaryDetail.vDEC[index],                     
                    'V2D':math.sqrt(self.parent.binaryDetail.vRA[index]**2+self.parent.binaryDetail.vDEC[index]**2),
                    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                    'Log10vRA':np.log10(abs(self.parent.binaryDetail.vRA[index])),
                    'Log10vDEC':np.log10(abs(self.parent.binaryDetail.vDEC[index])),
                    'Log10r':np.log10(abs(self.parent.binaryDetail.r[index])),
                    #'M':M,
                    'r':self.parent.binaryDetail.r[index]
                }
            
                self.parent.export.append(exportRecord)
        
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle('bindata/export.saved')   
        self.parent.printArrays()

        self.parent.status['hrOut']=self.parent.status['include']
        self.parent.status['kineticOut']=self.parent.status['include']
        try:
            self.parent.status.to_pickle(f'bindata/status.saved')
        except Exception:
            print('Error directory failed to save')
            print (self.parent.status)
        
        self.OnPlot()
        label=int(100)
        self.Filter_but.SetLabel(f'{label:,.1f}%')
        self.Filter_but.Enable()

    def XreturnY(self, X):
        # Return range of acceptable magnitudes.
        Y=float(self.m*float(X) + float(self.c))
        
        return [Y-self.Yerr,Y+self.Yerr]
    
    def OnPlot(self, event=0):


        self.plot_but.Disable()
        # Draw velocity map
        xdata1=pd.concat([self.parent.X.BminusR * self.parent.status['include'], self.parent.Y.BminusR * self.parent.status['include']])
        ydata1=pd.concat([self.parent.X.mag * self.parent.status['include'], self.parent.Y.mag * self.parent.status['include']])
        xdata2=pd.concat([self.parent.X.BminusR, self.parent.Y.BminusR])
        xdata2=xdata2.tolist()
        ydata2=pd.concat([self.parent.X.mag, self.parent.Y.mag])
        ydata2=ydata2.tolist()

        self.hrGraph.axes.set_ylabel('$M_G$', fontsize=FONTSIZE, rotation='horizontal')
        self.hrGraph.axes.set_xlabel('$B_P - R_P$', fontsize=FONTSIZE)
        self.hrGraph.axes.set_yscale('linear')
        self.hrGraph.axes.set_xscale('linear')
        self.hrGraph.set_limits([-.5,4],[18, -2.5])
        
        # To remove the artist
        for frame in self.hrGraph.frames:
            try:
                Artist.remove(frame)
            except Exception:
                pass
        try:
            self.line.remove()
        except Exception:
            pass
        try:
            self.line2.remove()
        except Exception:
            pass
        try:
            self.line3.remove()
        except Exception:
            pass
        
        legend1=[] 
        legend2=[] 
        
        unselectedBins=0
        prntVersion=self.prntVersionCheckBox.GetValue()
        if self.unselectedCheckBox.GetValue():
               
            if self.allWhiteCheckBox.GetValue():
                c='white'
                if prntVersion:
                    c='black'
            else:
                c='green'
                if prntVersion:
                    c='silver'
                
            marker = ','
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
            #Display graph
            try:
                self.line2, = self.hrGraph.axes.plot(xdata2, ydata2, color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
            except Exception:
                print(xdata2)
                print(ydata2)
        
            legend1.append(self.line2)
            legend2.append('unselected')
            self.hrGraph.draw(self.line2, xdata2, ydata2, False, [] )
            
        
            unselectedBins=len(self.parent.status['include'])-self.parent.status['include'].sum()
            
        if prntVersion:
            c='black'
            self.hrGraph.axes.set_title("")
            self.hrGraph.axes.patch.set_facecolor('1')  # Grey shade
        else:
            self.hrGraph.axes.set_title(f"Colour/Magnitude plot for {self.parent.status['include'].sum():,} selected and {unselectedBins:,} unselected stars", fontsize=FONTSIZE)
            self.hrGraph.axes.patch.set_facecolor('0.25')  # Grey shade
            c='white'
    
        marker = ','
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
        xdata1=xdata1.tolist()
        ydata1=ydata1.tolist()
        self.line, = self.hrGraph.axes.plot(xdata1, ydata1, color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
    
        legend1.append(self.line)
        legend2.append('Selected binaries')
        self.hrGraph.draw(self.line, xdata1, ydata1, True,[] )
                
        #    """
        #Attach a text label above each bar displaying its height
        #"""
        self.hrGraph.frames=[] 
        
        self.hrGraph.Layout()
        self.Layout()

        self.parent.printArrays()
        
        self.plot_but.Enable()


class kineticDataPlotting(wx.Panel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=14, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings
        
        self.static_bins = StaticText(self, label='# bins') 
        fgsizer.Add(self.static_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xLower = StaticText(self, label='x-lower') 
        fgsizer.Add(self.static_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xUpper = StaticText(self, label='x-upper') 
        fgsizer.Add(self.static_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yLower = StaticText(self, label='y-lower') 
        fgsizer.Add(self.static_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yUpper = StaticText(self, label='y-upper') 
        fgsizer.Add(self.static_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Outlier cutoff
        self.static_x_TopLeft = StaticText(self, label='x (Top Left)') 
        fgsizer.Add(self.static_x_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_y_TopLeft = StaticText(self, label='y (Top Left)') 
        fgsizer.Add(self.static_y_TopLeft , 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_x_BottomRight = StaticText(self, label='x (Bottom Right)') 
        fgsizer.Add(self.static_x_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_y_BottomRight = StaticText(self, label='y (Bottom Right)') 
        fgsizer.Add(self.static_y_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)     
        
        # Upper cutoff
        self.static_upperCutoff = StaticText(self, label='Upper cutoff') 
        fgsizer.Add(self.static_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # v x err reporting threshold.
        self.static_vxerrCutoff = StaticText(self, label="v/dv t'hold") 
        fgsizer.Add(self.static_vxerrCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)        
        
         # Lower bin cutoff header
        lowerBinCutoff_StaticText = StaticText(self, id=wx.ID_ANY, label="Lower Bin cutoff")
        fgsizer.Add(lowerBinCutoff_StaticText, 0, wx.ALL, 2)
       
        #Type of scale
        self.static_yLog = StaticText(self, label='y scale') 
        fgsizer.Add(self.static_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yAverage = StaticText(self, label='y Average') 
        fgsizer.Add(self.static_yAverage, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Axis limits
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','KINETIC')))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer umber of bins to divide x-scale into.")
        
        self.textctrl_xLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_lower','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xLower.SetToolTip("Lower end of x-scale.")
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_yLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_lower','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yLower.SetToolTip("Lower end of y-scale.")
        self.textctrl_yUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_upper','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yUpper.SetToolTip("Upper end of y-scale.")
        
        # Outlier values
        self.text_x_TopLeft = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_topLeft','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_x_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_y_TopLeft = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_topLeft','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_y_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_x_BottomRight = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_bottomRight','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_x_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_y_BottomRight = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_bottomRight','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_y_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Upper cutoff
        self.text_upperCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_cutoff','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperCutoff.SetToolTip("Value of y-scale above which values will be ignored.")
        
        # v x err reporting threshold
        self.text_vxerrCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('v_dv_cutoff','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.text_vxerrCutoff.SetToolTip("v/v_error reporting threshold.")
        fgsizer.Add(self.text_vxerrCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Lower bin cutoff textctrl
        self.lowerBinCutoffTextCtrl = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('lower_bin_cutoff','KINETIC'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.lowerBinCutoffTextCtrl.SetToolTip("Enter number below which occupancy not to display bins.")
        fgsizer.Add(self.lowerBinCutoffTextCtrl, 0, wx.ALL, 2)
        
        self.combo_yLog = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['log','normal'], value='')
        self.combo_yLog.SetSelection(int(gl_cfg.getItem('y_scale','KINETIC')))
        fgsizer.Add(self.combo_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.combo_yAvg = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['rms','mean'], value='')
        self.combo_yAvg.SetSelection(int(gl_cfg.getItem('y_avg','KINETIC')))
        fgsizer.Add(self.combo_yAvg, 0, wx.ALIGN_LEFT|wx.ALL, 5)
                
        # Create show bins check box
        showRABinsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bins (RA and Dec)")
        fgsizer.Add(showRABinsStaticText, 0, wx.ALL, 2)
        self.showBinsCheckBox = CheckBox(self)
        self.showBinsCheckBox.SetValue(gl_cfg.getBoolean('showbins','KINETIC'))
        self.showBinsCheckBox.SetToolTip("Display 1D RA & Dec data in separate bins.")
        fgsizer.Add(self.showBinsCheckBox, 0, wx.ALL, 2)
        
        # Create show raw data check box
        rawDataStaticText = StaticText(self, id=wx.ID_ANY, label="Show raw data")
        fgsizer.Add(rawDataStaticText, 0, wx.ALL, 2)
        self.rawDataCheckBox = CheckBox(self)
        self.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata', 'KINETIC'))
        self.rawDataCheckBox.SetToolTip("Display raw data on graph.")
        fgsizer.Add(self.rawDataCheckBox, 0, wx.ALL, 2)

        # Create show outlier line check box
        outlierStaticText = StaticText(self, id=wx.ID_ANY, label="Show outlier line")
        fgsizer.Add(outlierStaticText, 0, wx.ALL, 2)
        self.outlierLineCheckBox = CheckBox(self)
        self.outlierLineCheckBox.SetValue(gl_cfg.getBoolean('outlierline', 'KINETIC'))
        self.outlierLineCheckBox.SetToolTip("Show outlier line on graph.")
        fgsizer.Add(self.outlierLineCheckBox, 0, wx.ALL, 2)

        # Create show large data points
        largeStaticText = StaticText(self, id=wx.ID_ANY, label="Show large data points")
        fgsizer.Add(largeStaticText, 0, wx.ALL, 2)
        self.largePointsCheckBox = CheckBox(self)
        self.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints', 'KINETIC'))
        self.largePointsCheckBox.SetToolTip("Shows larger dec & ra data points for actual stars on graph.")
        fgsizer.Add(self.largePointsCheckBox, 0, wx.ALL, 2)

        # Create show labels line check box
        labelsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bin labels")
        fgsizer.Add(labelsStaticText, 0, wx.ALL, 2)
        self.showLabelsCheckBox = CheckBox(self)
        self.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels','KINETIC'))
        self.showLabelsCheckBox.SetToolTip("Show labels above bins on graph.")
        fgsizer.Add(self.showLabelsCheckBox, 0, wx.ALL, 2)

        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print Version")
        fgsizer.Add(prntVersion_StaticText, 0, wx.ALL, 2)
        self.prntVersionCheckBox = CheckBox(self)
        self.prntVersionCheckBox.SetToolTip("Produce print version of graph.")
        self.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion', 'KINETIC'))
        fgsizer.Add(self.prntVersionCheckBox, 0, wx.ALL, 2)
        

        # Draw button
        
        self.plot_but = Button(self, id=wx.ID_ANY, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Cancel Button
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel binning.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw velocity map
        self.velocityGraph = matplotlibPanel(parent=self, size=(1350, 750))
        fg2sizer.Add(self.velocityGraph)
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Metric", wx.LIST_FORMAT_RIGHT, width=280 )
        self.summaryList.SetColumnWidth(0, 280)
        self.summaryList.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, width=120 )
        self.summaryList.SetColumnWidth(1, 120)
        self.SetSizer(self.sizer_v)
        self.velocityGraph.Layout()
        self.Layout()

    def XreturnY(self, X):
        # Return lower outlier range.
        #Y=float(self.m*float(X) + float(self.c))
        Y=self.m*float(math.log10(X)) + self.c
        return 10**Y
    
    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
    
    def OnReset(self, event=0):
        #if hasattr(self.parent, 'hrinclude'):
        self.parent.status['include']=self.parent.status['hrOut']
        self.parent.status['kineticOut']=self.parent.status['include']

    def OnPlot(self, event=0):

        
        self.plot_but.Disable()
        
        self.parent.export=[]
        
        gl_cfg.setItem('no_bins',self.spin_bins.GetValue(),'KINETIC')
        gl_cfg.setItem('x_lower',self.textctrl_xLower.GetValue(),'KINETIC')
        gl_cfg.setItem('x_upper',self.textctrl_xUpper.GetValue(),'KINETIC')
        gl_cfg.setItem('y_lower',self.textctrl_yLower.GetValue(),'KINETIC')
        gl_cfg.setItem('y_upper',self.textctrl_yUpper.GetValue(),'KINETIC')
        gl_cfg.setItem('x_topLeft',self.text_x_TopLeft.GetValue(),'KINETIC')
        gl_cfg.setItem('y_topLeft',self.text_y_TopLeft.GetValue(),'KINETIC')
        gl_cfg.setItem('x_bottomRight',self.text_x_BottomRight.GetValue(),'KINETIC')
        gl_cfg.setItem('y_bottomRight',self.text_y_BottomRight.GetValue(),'KINETIC')
        gl_cfg.setItem('upper_cutoff',self.text_upperCutoff.GetValue(),'KINETIC')
        gl_cfg.setItem('v_dv_cutoff',self.text_vxerrCutoff.GetValue(),'KINETIC')
        gl_cfg.setItem('lower_bin_cutoff',self.lowerBinCutoffTextCtrl.GetValue(),'KINETIC')
        gl_cfg.setItem('y_scale',self.combo_yLog.GetSelection(),'KINETIC')
        gl_cfg.setItem('y_avg',self.combo_yAvg.GetSelection(),'KINETIC')
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        gl_cfg.setItem('prntversion',self.prntVersionCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('showbins',self.showBinsCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('rawdata',self.rawDataCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('outlierline',self.outlierLineCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('showlabels',self.showLabelsCheckBox.GetValue(), 'KINETIC') # save setting in config file
        
        self.OnReset()
        # Draw kinematic map
        #self.parent.vdvExclude=0  # Keep track of how many pairs are excluded because 'v x vErr' exceeds a threshold.
        
        # To remove the artist
        for frame in self.velocityGraph.frames:
            try:
                frame.remove()
            except Exception:
                pass
        try:
            self.linera.remove()
        except Exception:
            pass
        try:
            self.linedec.remove()
        except Exception:
            pass
        try:
            self.line2.remove()
        except Exception:
            pass
        try:
            self.line3ra.remove()
        except Exception:
            pass
        try:
            self.line3dec.remove()
        except Exception:
            pass
        try:
            self.lineOL.remove()
        except Exception:
            pass
        
        legend1=[] 
        legend2=[] 
        
        self.velocityGraph.set_limits([float(self.textctrl_xLower.GetValue()),float(self.textctrl_xUpper.GetValue())],[float(self.textctrl_yLower.GetValue()),float(self.textctrl_yUpper.GetValue())])
        
        prntVersion=self.prntVersionCheckBox.GetValue()
        
        #Set up local valriables to avoid repeated calls to wx functions and for clarity
        x_BottomRight=float(self.text_x_BottomRight.GetValue())
        x_TopLeft=float(self.text_x_TopLeft.GetValue())
        y_BottomRight=float(self.text_y_BottomRight.GetValue())
        y_TopLeft=float(self.text_y_TopLeft.GetValue())
        # Calculate parameters for outlier line.
        self.m=float(math.log10(y_BottomRight)-math.log10(y_TopLeft)/(math.log10(x_BottomRight)-math.log10(x_TopLeft))) # m = dy/dx
        self.c=float(math.log10(y_TopLeft) - math.log10(x_TopLeft)*self.m)
    
        lenArray=len(self.parent.binaryDetail)
        upperCutoff=float(self.text_upperCutoff.GetValue())
        vxerrCutoff=float(self.text_vxerrCutoff.GetValue())
            
        if self.showBinsCheckBox.GetValue():   
            
            #
            # Convert RA data into bins
            #
#######################################################################

            top=float(self.textctrl_xUpper.GetValue())      #  Get top of range
            bottom=float(self.textctrl_xLower.GetValue())   #  Get bottom of range
            diff = math.log10(top)-math.log10(bottom)   #  Work out difference in log terms.
######################################################################
            numRABins=int(self.spin_bins.GetValue())      #  Get number of RA bins.
            dataRABins=bin(numRABins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            upper=top
            factor=10**(diff/numRABins)
            lower=upper/factor
            for i in range(numRABins):
                dataRABins.newBin(lower, upper)
                upper=lower
                lower=upper/factor
                
            numDECBins=int(self.spin_bins.GetValue()-1)      #  Get number of DEC bins (It's 1 fewer than the number of RA bins).
            dataDECBins=bin(numDECBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            
            # Need to offset upper bound of top bin by sqrt of a factor. TOTAL interval is the same with 1/2 a DEC bin at the top and half a DEC bin at the bottom.
            # Ignore these and reduce number of bins by 1.
            upper=top/math.sqrt(factor)
            lower=upper/factor
            for i in range(numDECBins):
                dataDECBins.newBin(lower, upper)
                upper=lower
                lower=upper/factor

            #Filter out currently inluded rows only
            indexStatus = self.parent.status.index
            condition = self.parent.status.include == True
            statusIndices = indexStatus[condition]
            statusIndicesList = statusIndices.tolist()
            
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.include[i]) or not int(self.parent.status.include[i]):
                    continue
                #else:
                #    include=int(self.parent.status.include[i])
                #Set up local valriables to avoid repeated PD access and for clarity
                vRA=0
                vDEC=0
                excludeRA=0
                excludeDec=0
                vRA=abs(float(self.parent.binaryDetail.vRA[i]))
                vDEC=abs(float(self.parent.binaryDetail.vDEC[i]))
                r=abs(float(self.parent.binaryDetail.r[i]))
                vRAerr=abs(float(self.parent.binaryDetail.vRAerr[i]))
                vDECerr=abs(float(self.parent.binaryDetail.vDECerr[i]))
                # Go through and bin
                label=float(100.0 * i /lenArray)
                self.plot_but.SetLabel(f'{label:,.1f}%')
                global CANCEL
                if CANCEL:
                    CANCEL = False
                    self.plot_but.Enable()
                    return
                wx.Yield()
                
                # Check for outliers.  If we loose one, we should loose both.
                # If r is within band that we're checking for ouliers AND the velocity
                # is more than the calculated velocity allowed at that radius
                #
                # Check for outliers
                Y=self.XreturnY(r)
                if (vRA > Y or vDEC > Y ) and r > x_TopLeft and r < x_BottomRight:
                    self.parent.status.include[i]=0
                    
                # Check for cutoff.  If we loose one, we should loose both.
                if vRA>upperCutoff or vDEC>upperCutoff:
                    self.parent.status.include[i]=0
                    
                # Check RA limits
                if self.parent.status.include[i]:
                    #Exclude point if v/dv > vxerrCutoff
                    excludeRA = dataRABins.binAddDataPoint(x=r, y=vRA, dy=vRAerr, value=vxerrCutoff)
                    excludeDec = dataDECBins.binAddDataPoint(x=r, y=vDEC, dy=vDECerr, value=vxerrCutoff)
                    # Exclude binary if both RA & Dec excluded.
                    if excludeRA and excludeDec:
                        self.parent.status.include[i]=0
                    else:
                        primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
                        star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
                        exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.SOURCE_ID),
                            'ra1':float(primaryPointer.RA_),
                            'dec1':float(primaryPointer.DEC_),
                            'mag1':primaryPointer.PHOT_G_MEAN_MAG,
                            'MAG1':self.parent.X.mag[i],
                            'PARALLAX1':float(primaryPointer.PARALLAX),
                            'DIST1':float(primaryPointer.DIST),
                            'RUWE1':primaryPointer.RUWE,
                            'SOURCE_ID_SECONDARY':str(star2Pointer.SOURCE_ID),
                            'ra2':float(star2Pointer.RA_),
                            'dec2':float(star2Pointer.DEC_),
                            'mag2':star2Pointer.PHOT_G_MEAN_MAG,
                            'MAG2':self.parent.Y.mag[i],
                            'PARALLAX2':float(star2Pointer.PARALLAX),
                            'DIST2':float(star2Pointer.DIST),
                            'RUWE2':star2Pointer.RUWE,
                            'vRA':self.parent.binaryDetail.vRA[i],
                            'vDEC':self.parent.binaryDetail.vDEC[i],                      
                            'V2D':math.sqrt(self.parent.binaryDetail.vRA[i]**2+self.parent.binaryDetail.vDEC[i]**2),
                            'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                            'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                            'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                            'Log10vRA':np.log10(abs(self.parent.binaryDetail.vRA[i])),
                            'Log10vDEC':np.log10(abs(self.parent.binaryDetail.vDEC[i])),
                            'Log10r':np.log10(abs(self.parent.binaryDetail.r[i])),
                            #'M':M,
                            'r':self.parent.binaryDetail.r[i]
                        }

                        self.parent.export.append(exportRecord)
                        
            xdata3ra=dataRABins.getBinXArray('centre')
            ydata3ra=dataRABins.getBinYArray(self.combo_yAvg.GetValue())
            rerrbin3ra=dataRABins.getBinXVarArray()
            verrbin3ra=dataRABins.getBinYVarArray()
                        
            self.line3ra = self.velocityGraph.axes.errorbar(xdata3ra, ydata3ra, xerr=rerrbin3ra, yerr=verrbin3ra, fmt='o', ecolor='m', elinewidth=1, capsize=0, mfc='m', mec='m', ms=3) #,label='Gaia binned'
            self.line3ra[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line3ra[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
            if not prntVersion:
                legend1.append(self.line3ra)
                legend2.append('Gaia RA binned data')
            
            xScaleBy=1.15
            yScaleBy=1.05

            if self.showLabelsCheckBox.GetValue():
                #    """
                #Attach a text label above each bar displaying its height
                #"""
                self.velocityGraph.frames=[] 
                if prntVersion:
                    c='black'
                else:
                    c='white'
                for x,y,label in zip(xdata3ra, ydata3ra, dataRABins.getBinYLabelArray()):
                   self.velocityGraph.frames.append(self.velocityGraph.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))
                        
            self.velocityGraph.draw(self.line3ra, xdata3ra, ydata3ra, False, [] )
            
            ####################################################################################################dec
            
            xdata3dec=dataDECBins.getBinXArray('centre')
            ydata3dec=dataDECBins.getBinYArray(self.combo_yAvg.GetValue())
            rerrbin3dec=dataDECBins.getBinXVarArray()
            verrbin3dec=dataDECBins.getBinYVarArray()
                        
            if self.showLabelsCheckBox.GetValue():
                if prntVersion:
                    c='black'
                else:
                    c='white'
                for x,y,label in zip(xdata3dec, ydata3dec, dataDECBins.getBinYLabelArray()):
                   self.velocityGraph.frames.append(self.velocityGraph.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))
               
            self.line3dec = self.velocityGraph.axes.errorbar(xdata3dec, ydata3dec, xerr=rerrbin3dec, yerr=verrbin3dec, fmt='o', ecolor='c', elinewidth=1, capsize=0, mfc='c', mec='c', ms=3) #,label='Gaia binned'
            self.line3dec[-1][0].set_linestyle(':')
            self.line3dec[-1][1].set_linestyle(':')
            if not prntVersion:
                legend1.append(self.line3dec)
                legend2.append('Gaia DEC binned data')
            
            self.velocityGraph.draw(self.line3dec, xdata3dec, ydata3dec, False, [] )
        
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle('bindata/export.saved')   
        xdata1 = self.parent.binaryDetail.r * self.parent.status['include']
        ydata1ra = self.parent.binaryDetail.vRA * self.parent.status['include']
        ydata1dec = self.parent.binaryDetail.vDEC * self.parent.status['include']
        
        a=np.array(ydata1ra)

               
        ROWCOUNTMATRIX['BIN']=len(xdata1)
        if self.rawDataCheckBox.GetValue():
            c='white'
            if prntVersion:
                c='black'
            marker = ','
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
            self.linera, = self.velocityGraph.axes.plot(xdata1, ydata1ra, color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
            self.velocityGraph.draw(self.linera, xdata1, ydata1ra, True, [] )
            self.linedec, = self.velocityGraph.axes.plot(xdata1, ydata1dec, color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
            self.velocityGraph.draw(self.linedec, xdata1, ydata1dec, True, [] )
                    
            if not prntVersion:
                legend1.append(self.linedec)
                legend2.append('Gaia raw data')
        if self.outlierLineCheckBox.GetValue():
            xdataOL=[x_TopLeft,x_BottomRight]
            ydataOL=[y_TopLeft,y_BottomRight]
            
            self.lineOL, = self.velocityGraph.axes.plot(xdataOL, ydataOL, 'ko--', linewidth=1, markersize=1)
            self.velocityGraph.draw(self.lineOL, xdataOL, ydataOL, True, [] )
            
            if not prntVersion:
                legend1.append(self.lineOL)
                legend2.append('Outlier cutoff')
        
        ROWCOUNTMATRIX['ADQL']=len(self.parent.status['include'])
        ROWCOUNTMATRIX['GRP']=len(self.parent.status['include'])-self.parent.status['notgroup'].sum()
        NGxRV=self.parent.status['notgroup'] * self.parent.status['radialvelocity']
        ROWCOUNTMATRIX['V0']=self.parent.status['notgroup'].sum()-NGxRV.sum()
        ROWCOUNTMATRIX['R0']=ROWCOUNTMATRIX['ADQL']- ROWCOUNTMATRIX['BIN']
        ROWCOUNTMATRIX['BIN']=self.parent.status['include'].sum()
        
        if prntVersion:
            self.velocityGraph.axes.set_title("")
            self.velocityGraph.axes.patch.set_facecolor('1')  # White shade
        else:
            self.velocityGraph.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,} binary stars, Gaia {RELEASE}, velocity vs separation with Newtonian expectation", fontsize=FONTSIZE)
            self.velocityGraph.axes.patch.set_facecolor('0.25')  # Grey shade
            
        self.line2, = self.velocityGraph.axes.plot(xdata2, ydata2_1D, 'r-', lw=1)#,label='Newtonian')
        
        
        if not prntVersion:
            legend1.append(self.line2)
            legend2.append('Newtonian rms value')
            
        self.velocityGraph.axes.legend(legend1, legend2)
        if prntVersion:
            self.velocityGraph.axes.get_legend().remove()
            
        self.velocityGraph.draw(self.line2, xdata2, ydata2_1D, False, [] )
        
        self.summaryList.DeleteAllItems()
        self.summaryList.InsertItem(0, 'Gaia DB')
        self.summaryList.SetItem(0, 1, f"{ROWCOUNTMATRIX['ADQL']:,}")
        #Set bold
        item = self.summaryList.GetItem(0,0)
        #print "itemText", item.GetText()       
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.summaryList.SetItem(item)  
        
        rowCnt=1
        self.summaryList.InsertItem(rowCnt, 'In groups')
        self.summaryList.SetItem(rowCnt, 1, f"{ROWCOUNTMATRIX['GRP']:,}")
        
        rowCnt += 1
        self.summaryList.InsertItem(2, 'No radial velocity')
        self.summaryList.SetItem(2, 1, f"{ROWCOUNTMATRIX['V0']:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(3, 'Total')
        total=ROWCOUNTMATRIX['ADQL']-ROWCOUNTMATRIX['GRP']-ROWCOUNTMATRIX['V0']
        self.summaryList.SetItem(3, 1, f"{total:,}")
        #Set bold
        item = self.summaryList.GetItem(3,0)   
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.summaryList.SetItem(item)  
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Other noise')
        other=ROWCOUNTMATRIX['ADQL']-ROWCOUNTMATRIX['GRP']-ROWCOUNTMATRIX['V0']-ROWCOUNTMATRIX['BIN']
        self.summaryList.SetItem(rowCnt, 1, f'{other:,}')
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, f'Remaining selected binaries')
        self.summaryList.SetItem(rowCnt, 1, f"{ROWCOUNTMATRIX['BIN']:,}")
        #Set bold
        item = self.summaryList.GetItem(rowCnt,0)
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.summaryList.SetItem(item)
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Error and noise metrics')
        #Set bold
        item = self.summaryList.GetItem(rowCnt,0)
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.MakeBold().MakeUnderlined()
        item.SetFont(font)
        self.summaryList.SetItem(item)
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N for v/dv (RA)')
        snVoverDv=self.CalcVoverdv()
        self.summaryList.SetItem(rowCnt, 1, f"{snVoverDv[0]:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N for v/dv (DEC)')
        self.summaryList.SetItem(rowCnt, 1, f"{snVoverDv[1]:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N PMRA')
        snPMRAoverDPMRAx=self.CalcMeanXoverDx('PMRA','PMRA_ERROR')
        self.summaryList.SetItem(rowCnt, 1, f"{snPMRAoverDPMRAx:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N PMDEC')
        snPMDECoverDPMDECx=self.CalcMeanXoverDx('PMDEC','PMDEC_ERROR')
        self.summaryList.SetItem(rowCnt, 1, f"{snPMDECoverDPMDECx:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N Px')
        snPxoverDpx=self.CalcMeanXoverDx('PARALLAX','PARALLAX_ERROR')
        self.summaryList.SetItem(rowCnt, 1, f"{snPxoverDpx:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean RUWE')
        avgRuwe=self.CalcMeanXoverDx('RUWE',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgRuwe:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Distance')
        avgDIST=self.CalcMeanXoverDx('DIST',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgDIST:,}")
        
        
        if self.showBinsCheckBox.GetValue():  
            #Mean binned binary RMS 1D relative velocity  in RA
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'Mean binned RMS 1D velocity in RA')        
            ydata3rapd=pd.DataFrame(ydata3ra, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{ydata3rapd.V.mean():,.4f}")
        
            #Mean binned binary RMS 1D relative velocity  in DEC
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'Mean binned RMS 1D velocity in DEC')        
            ydata3decpd=pd.DataFrame(ydata3dec, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{ydata3decpd.V.mean():,.4f}")
        
        self.parent.status['kineticOut']=self.parent.status['include']
        try:
            self.parent.status.to_pickle(f'bindata/status.saved')
        except Exception:
            print('Error directory failed to save')
            print (self.parent.status)
        self.parent.printArrays()

        self.plot_but.Enable()
        
    def CalcVoverdv(self):
        
        vRAoverdv=self.parent.status['include']*self.parent.binaryDetail.vRA.abs()/self.parent.binaryDetail.vRAerr.abs()
        vDECoverdv=self.parent.status['include']*self.parent.binaryDetail.vDEC.abs()/self.parent.binaryDetail.vDECerr.abs()
        
        totalSelected=self.parent.status['include'].sum()
        
        return([round(vRAoverdv.sum()/totalSelected,2),round(vDECoverdv.sum()/totalSelected,2)])
        
        
    def CalcMeanXoverDx(self, col, col_error):
        if col_error:
            XoverDx=self.parent.status['include']*self.parent.X[col].abs()/self.parent.X[col_error].abs()
            XoverDx=XoverDx+self.parent.status['include']*self.parent.X[col].abs()/self.parent.X[col_error].abs()

            totalSelected=self.parent.status['include'].sum()
            totalSelected=totalSelected*2
        else:
            XoverDx=self.parent.status['include']*self.parent.X[col].abs()
            totalSelected=self.parent.status['include'].sum()
        
        return round(XoverDx.sum()/totalSelected,2)
        
class TFDataPlotting(wx.Panel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=12, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings
        
        self.static_bins = StaticText(self, label='# bins') 
        fgsizer.Add(self.static_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xLower = StaticText(self, label='x-lower') 
        fgsizer.Add(self.static_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xUpper = StaticText(self, label='x-upper') 
        fgsizer.Add(self.static_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yLower = StaticText(self, label='y-lower') 
        fgsizer.Add(self.static_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yUpper = StaticText(self, label='y-upper') 
        fgsizer.Add(self.static_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Upper R cutoff
        self.static_upperRCutoff = StaticText(self, label='Upper r-cutoff') 
        fgsizer.Add(self.static_upperRCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)        
        
        # Upper cutoff
        self.static_upperYCutoff = StaticText(self, label='Upper y-cutoff') 
        fgsizer.Add(self.static_upperYCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Lower bin cutoff header
        lowerBinCutoff_StaticText = StaticText(self, id=wx.ID_ANY, label="Lower Bin cutoff")
        fgsizer.Add(lowerBinCutoff_StaticText, 0, wx.ALL, 2)
       
        #Type of scale
        self.static_yLog = StaticText(self, label='y scale') 
        fgsizer.Add(self.static_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yAverage = StaticText(self, label='y Average') 
        fgsizer.Add(self.static_yAverage, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.static_LessGreater = StaticText(self, label='Less than/greater than') 
        fgsizer.Add(self.static_LessGreater, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_sepnCutoff = StaticText(self, label="Sep'n. cutoff") 
        fgsizer.Add(self.static_sepnCutoff, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Axis limits
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','TULLEYFISHER')))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer umber of bins to divide x-scale into.")
        
        self.textctrl_xLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_lower','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xLower.SetToolTip("Lower end of x-scale.")
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_yLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_lower','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yLower.SetToolTip("Lower end of y-scale.")
        self.textctrl_yUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_upper','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yUpper.SetToolTip("Upper end of y-scale.")
        
        # Upper R cutoff
        self.text_upperRCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_rcutoff','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperRCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperRCutoff.SetToolTip("Value of r-scale (separation) above which values will be ignored.")
        
        # Upper Y cutoff
        self.text_upperYCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_ycutoff','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperYCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperYCutoff.SetToolTip("Value of y-scale above which values will be ignored.")
        
        # Lower bin cutoff textctrl
        self.lowerBinCutoffTextCtrl = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('lower_bin_cutoff','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.lowerBinCutoffTextCtrl.SetToolTip("Enter number below which not to display bins.")
        fgsizer.Add(self.lowerBinCutoffTextCtrl, 0, wx.ALL, 2)
        
        self.combo_yLog = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['log','normal'], value='')
        self.combo_yLog.SetSelection(int(gl_cfg.getItem('y_scale','TULLEYFISHER')))
        fgsizer.Add(self.combo_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.combo_yAvg = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['rms','mean'], value='')
        self.combo_yAvg.SetSelection(int(gl_cfg.getItem('y_avg','TULLEYFISHER')))
        fgsizer.Add(self.combo_yAvg, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.combo_LtGt = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['Greater than','Less than'], value='')
        self.combo_LtGt.SetSelection(int(gl_cfg.getItem('gtlt','TULLEYFISHER')))
        fgsizer.Add(self.combo_LtGt, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.combo_LtGt.SetToolTip("Separation of bianaries is greater than or less than the (Newtonian) separation cutoff")
        
        #Distance cutoff.
        self.TextCtrl_sepnCutoff = TextCtrl(self, id=wx.ID_ANY, value=str(float(gl_cfg.getItem('cutoff','TULLEYFISHER'))), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.TextCtrl_sepnCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.TextCtrl_sepnCutoff.SetToolTip("(Newtonian) separation cutoff in pc.")
        
        # Create show raw data check box
        rawDataStaticText = StaticText(self, id=wx.ID_ANY, label="Show raw data")
        fgsizer.Add(rawDataStaticText, 0, wx.ALL, 2)
        self.rawDataCheckBox = CheckBox(self)
        self.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata', 'TULLEYFISHER'))
        self.rawDataCheckBox.SetToolTip("Display raw data on graph.")
        fgsizer.Add(self.rawDataCheckBox, 0, wx.ALL, 2)

        # Create show labels line check box
        labelsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bin labels")
        fgsizer.Add(labelsStaticText, 0, wx.ALL, 2)
        self.showLabelsCheckBox = CheckBox(self)
        self.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels', 'TULLEYFISHER'))
        self.showLabelsCheckBox.SetToolTip("Show labels above bins on graph.")
        fgsizer.Add(self.showLabelsCheckBox, 0, wx.ALL, 2)

        # Create '1D/2D' check box
        V1D_StaticText = StaticText(self, id=wx.ID_ANY, label="show 1D chart?")
        fgsizer.Add(V1D_StaticText, 0, wx.ALL, 2)
        self.V1D_CheckBox = CheckBox(self)
        self.V1D_CheckBox.SetToolTip("Produce 1D velocity version of graph. 2D is the default")
        self.V1D_CheckBox.SetValue(gl_cfg.getBoolean('v1d', 'TULLEYFISHER'))
        fgsizer.Add(self.V1D_CheckBox, 0, wx.ALL, 2)
        
        # Create show large data points
        largeStaticText = StaticText(self, id=wx.ID_ANY, label="Show large data points")
        fgsizer.Add(largeStaticText, 0, wx.ALL, 2)
        self.largePointsCheckBox = CheckBox(self)
        self.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints', 'TULLEYFISHER'))
        self.largePointsCheckBox.SetToolTip("Shows larger data points for stars on graph.")
        fgsizer.Add(self.largePointsCheckBox, 0, wx.ALL, 2)
        
        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print Version")
        fgsizer.Add(prntVersion_StaticText, 0, wx.ALL, 2)
        self.prntVersionCheckBox = CheckBox(self)
        self.prntVersionCheckBox.SetToolTip("Produce print version of graph.")
        self.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion', 'TULLEYFISHER'))
        fgsizer.Add(self.prntVersionCheckBox, 0, wx.ALL, 2)
        
        # Draw button
        
        self.plot_but = Button(self, id=wx.ID_ANY, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Cancel Button
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel binning.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw velocity map
        self.TulleyFPlot = matplotlibPanel(parent=self, size=(1350, 750))
        fg2sizer.Add(self.TulleyFPlot)
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Metric", wx.LIST_FORMAT_RIGHT, width=280 )
        self.summaryList.SetColumnWidth(0, 280)
        self.summaryList.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, width=120 )
        self.summaryList.SetColumnWidth(1, 120)
        self.SetSizer(self.sizer_v)
        self.TulleyFPlot.Layout()
        self.Layout()

    def XreturnY(self, X):
        # Return lower outlier range.
        Y=self.m*float(X) + self.c
        return Y
    
    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
    
    def OnReset(self, event=0):
        self.parent.status['include']=self.parent.status['kineticOut']

    def OnPlot(self, event=0):

        #self.parent.export=pd.DataFrame(columns=['SOURCE_ID_PRIMARY','ra1','dec1','mag1','SOURCE_ID_SECONDARY','ra2','dec2','mag2', 'vRA', 'vDEC', 'V2D', 'M', 'r'])
        self.parent.export=[]
        
        self.plot_but.Disable()
        
        gl_cfg.setItem('no_bins',self.spin_bins.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('x_lower',self.textctrl_xLower.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('x_upper',self.textctrl_xUpper.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('y_lower',self.textctrl_yLower.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('y_upper',self.textctrl_yUpper.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('upper_rcutoff',self.text_upperRCutoff.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('upper_ycutoff',self.text_upperYCutoff.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('lower_bin_cutoff',self.lowerBinCutoffTextCtrl.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('y_scale',self.combo_yLog.GetSelection(),'TULLEYFISHER')
        gl_cfg.setItem('y_avg',self.combo_yAvg.GetSelection(),'TULLEYFISHER')
        gl_cfg.setItem('gtlt',self.combo_LtGt.GetSelection(),'TULLEYFISHER')
        gl_cfg.setItem('cutoff',self.TextCtrl_sepnCutoff.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        gl_cfg.setItem('rawdata',self.rawDataCheckBox.GetValue(), 'TULLEYFISHER') # save setting in config file
        gl_cfg.setItem('prntversion',self.prntVersionCheckBox.GetValue(), 'TULLEYFISHER') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'TULLEYFISHER') # save setting in config file
        gl_cfg.setItem('v1d',self.V1D_CheckBox.GetValue(), 'TULLEYFISHER') # save setting in config file
        gl_cfg.setItem('showlabels',self.showLabelsCheckBox.GetValue(), 'TULLEYFISHER') # save setting in config file
        self.OnReset()
        
        # To remove the artist
        for frame in self.TulleyFPlot.frames:
            try:
                frame.remove()
            except Exception:
                pass
        try:
            self.line1.remove()
        except Exception:
            pass
        try:
            self.line3TF.remove()
        except Exception:
            pass

        try:
            self.lineLMS.remove()
        except Exception:
            pass
        
        legend1=[] 
        legend2=[] 
        
        self.TulleyFPlot.set_limits([float(self.textctrl_xLower.GetValue()),float(self.textctrl_xUpper.GetValue())],[float(self.textctrl_yLower.GetValue()),float(self.textctrl_yUpper.GetValue())])
        
        prntVersion=self.prntVersionCheckBox.GetValue()
            
        lenArray=len(self.parent.binaryDetail)
        upperRCutoff=float(self.text_upperRCutoff.GetValue())
        upperYCutoff=float(self.text_upperYCutoff.GetValue())
        
        #
        # Convert Velocity data into bins
        #
#######################################################################

        top=float(self.textctrl_xUpper.GetValue())      #  Get top of range
        bottom=float(self.textctrl_xLower.GetValue())   #  Get bottom of range
        diff = math.log10(top)-math.log10(bottom)   #  Work out difference in log terms.
######################################################################
        numTFBins=int(self.spin_bins.GetValue())      #  Get number of RA bins.
        dataTFBins=bin(numTFBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
        upper=top
        factor=10**(diff/numTFBins)
        lower=upper/factor
        for i in range(numTFBins):
            dataTFBins.newBin(lower, upper)
            upper=lower
            lower=upper/factor
            
        #Filter out currently inluded rows only
        indexStatus = self.parent.status.index
        condition = self.parent.status.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        
        #Loop through binary values
        for i in statusIndicesList:
            
            if math.isnan(self.parent.status.include[i]) or not int(self.parent.status.include[i]):
                continue
            else:
                include=int(self.parent.status.include[i])
            #Set up local valriables to avoid repeated PD access and for clarity
            if math.isnan(self.parent.binaryDetail.vRA[i]) :
                print(f'i={i}, vRA = {self.parent.binaryDetail.vRA[i]}')
            if math.isnan(self.parent.binaryDetail.vDEC[i]) :
                print(f'i={i}, vDEC = {self.parent.binaryDetail.vDEC[i]}')
            vRA=abs(float(self.parent.binaryDetail.vRA[i]))
            vDEC=abs(float(self.parent.binaryDetail.vDEC[i]))
            V2D=math.sqrt(vRA**2+vDEC**2)
            
            r=abs(float(self.parent.binaryDetail.r[i]))
            vRAerr=abs((float(self.parent.binaryDetail.vRAerr[i])))
            vDECerr=abs(float(self.parent.binaryDetail.vDECerr[i]))
            Verr=abs(math.sqrt((vRA*vRAerr)**2+(vDEC*vDECerr)**2))/V2D
            M=abs(float(self.parent.binaryDetail.M[i]))
            # Go through and bin
            label=float(100.0 * i /lenArray)
            self.plot_but.SetLabel(f'{label:,.1f}%')
            global CANCEL
            if CANCEL:
                CANCEL = False
                self.plot_but.Enable()
                return
            wx.Yield()
            
            primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
            star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
            exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.SOURCE_ID),
                'ra1':float(primaryPointer.RA_),
                'dec1':float(primaryPointer.DEC_),
                'mag1':primaryPointer.PHOT_G_MEAN_MAG,
                'MAG1':self.parent.X.mag[i],
                'PARALLAX1':float(primaryPointer.PARALLAX),
                'DIST1':float(primaryPointer.DIST),
                'RUWE1':primaryPointer.RUWE,
                'SOURCE_ID_SECONDARY':str(star2Pointer.SOURCE_ID),
                'ra2':float(star2Pointer.RA_),
                'dec2':float(star2Pointer.DEC_),
                'mag2':star2Pointer.PHOT_G_MEAN_MAG,
                'MAG2':self.parent.Y.mag[i],
                'PARALLAX2':float(star2Pointer.PARALLAX),
                'DIST2':float(star2Pointer.DIST),
                'RUWE2':star2Pointer.RUWE,
                'vRA':self.parent.binaryDetail.vRA[i],
                'vDEC':self.parent.binaryDetail.vDEC[i],
                'V2D':math.sqrt(self.parent.binaryDetail.vRA[i]**2+self.parent.binaryDetail.vDEC[i]**2),
                'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                'Log10vRA':np.log10(abs(self.parent.binaryDetail.vRA[i])),
                'Log10vDEC':np.log10(abs(self.parent.binaryDetail.vDEC[i])),
                'Log10r':np.log10(abs(self.parent.binaryDetail.r[i])),
                'M':M,
                'r':self.parent.binaryDetail.r[i]
            }
            #
            # Check Separation limits
            if self.combo_LtGt.GetSelection()==0:
                # Ie 'Outer' shell
                if r>float(self.TextCtrl_sepnCutoff.GetValue()) and upperYCutoff>V2D and upperRCutoff>r:
                    self.parent.export.append(exportRecord)
                    if self.V1D_CheckBox.GetValue()==True:
                        if dataTFBins.binAddDataPoint(x=M, y=vRA, dy=vRAerr, value=0) :
                            print(f'Exclude "vRAerr" x={M}, y={vRA}')
                        if dataTFBins.binAddDataPoint(x=M, y=vDEC, dy=vDECerr, value=0) :
                            print(f'Exclude "vDECerr" x={M}, y={vDEC}')
                        
                    else:
                        if dataTFBins.binAddDataPoint(x=M, y=V2D, dy=Verr, value=0) :
                            self.parent.status.include[i]=0
                            print(f'Exclude "Verr" x={M}, y={V2D}')
                else:
                    self.parent.status.include[i]=0
            else:
                # Ie 'Inner' shell
                if r<float(self.TextCtrl_sepnCutoff.GetValue()) and upperYCutoff>V2D and upperRCutoff>r:
                    self.parent.export.append(exportRecord)
                    if self.V1D_CheckBox.GetValue()==True:
                        if dataTFBins.binAddDataPoint(x=M, y=vRA, dy=vRAerr, value=0):
                            print(f'Exclude "vRAerr" x={M}, y={vRA}')
                        if dataTFBins.binAddDataPoint(x=M, y=vDEC, dy=vDECerr, value=0) :
                            print(f'Exclude "vDECerr" x={M}, y={vDEC}')
                    else:
                        if dataTFBins.binAddDataPoint(x=M, y=V2D, dy=Verr, value=0) :
                            self.parent.status.include[i]=0
                            print(f'Exclude "verr" x={M}, y={V2D}')
                else:
                    self.parent.status.include[i]=0
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle('bindata/export.saved')   
        xdata3TF=dataTFBins.getBinXArray(type='centre')
        ydata3TF=dataTFBins.getBinYArray(self.combo_yAvg.GetValue())
        rerrbin3TF=dataTFBins.getBinXVarArray()
        verrbin3TF=dataTFBins.getBinXVarArray()
    
        self.line3TF = self.TulleyFPlot.axes.errorbar(x=xdata3TF, y=ydata3TF, xerr=rerrbin3TF, yerr=verrbin3TF, fmt='o', ecolor='m', elinewidth=1, capsize=0, mfc='m', mec='m', ms=3) #,label='Gaia binned'
        self.line3TF[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
        self.line3TF[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
        
        if self.V1D_CheckBox.GetValue()==True:
            ND = '1'
        else:
            ND = '2'
        if not prntVersion:
            legend1.append(self.line3TF)
            legend2.append(f'{ND}D Velocity binned data')
        
        xScaleBy=1
        yScaleBy=1.05

        if self.showLabelsCheckBox.GetValue():
            #    """
            #Attach a text label above each bar displaying its height
            #"""
            self.TulleyFPlot.frames=[] 
            if prntVersion:
                c='black'
            else:
                c='white'
            for x,y,label in zip(xdata3TF, ydata3TF, dataTFBins.getBinYLabelArray()):
               self.TulleyFPlot.frames.append(self.TulleyFPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))
        
        self.TulleyFPlot.draw(self.line3TF, xdata3TF, ydata3TF, False, [] )
        
        self.TulleyFPlot.axes.set_xlabel('total binary mass ($M_{\odot}$)', fontsize=FONTSIZE)
                
        self.TulleyFPlot.axes.set_ylabel(f'{ND}D relative velocity in plane of sky (km/s)', fontsize=FONTSIZE)
        ####################################################################################################dec

        xdata1 = self.parent.binaryDetail.M * self.parent.status['include']
        ydata1 = self.parent.binaryDetail.vRA * self.parent.status['include']
               
        c='white'
        if prntVersion:
            c='black'

        ROWCOUNTMATRIX['ADQL']=self.parent.status['dataLoadOut'].sum()
        ROWCOUNTMATRIX['GRP']=ROWCOUNTMATRIX['ADQL']-self.parent.status['notgroup'].sum()
        NGxRV=self.parent.status['notgroup'] * self.parent.status['radialvelocity']
        ROWCOUNTMATRIX['V0']=self.parent.status['notgroup'].sum()-NGxRV.sum()
        ROWCOUNTMATRIX['R0']=ROWCOUNTMATRIX['ADQL']- ROWCOUNTMATRIX['BIN']
        ROWCOUNTMATRIX['BIN']=self.parent.status['include'].sum()
        
        if prntVersion:
            self.TulleyFPlot.axes.set_title("")
            self.TulleyFPlot.axes.patch.set_facecolor('1')  # White shade
        else:
            self.TulleyFPlot.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,} binary stars, Gaia {RELEASE}, {ND}D relative velocity vs total mass", fontsize=FONTSIZE)
            self.TulleyFPlot.axes.patch.set_facecolor('0.25')  # Grey shade
        
        self.TulleyFPlot.axes.grid(b=1, which='both', axis='both')     
        
        marker = ','
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
        #self.TulleyFPlot.axes.set_xticklabels(['1.0x','1.2x','1.4x','1.6x','1.8x','2.0x','2.2x','2.4x'])
        
        if self.rawDataCheckBox.GetValue():
            self.line1, = self.TulleyFPlot.axes.plot(xdata1, ydata1, color=c, marker=marker, linestyle='none', linewidth=0, markersize=1)
            if not prntVersion:
                legend1.append(self.line1)
                legend2.append('TF raw data')
                
            self.TulleyFPlot.draw(self.line1, xdata1, ydata1, True, [] )
                
        
        self.TulleyFPlot.Layout()
        self.Layout()

        self.summaryList.DeleteAllItems()
        self.summaryList.InsertItem(0, 'Gaia DB')
        self.summaryList.SetItem(0, 1, f"{ROWCOUNTMATRIX['ADQL']:,}")
        #Set bold
        item = self.summaryList.GetItem(0,0)
        #print "itemText", item.GetText()       
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.summaryList.SetItem(item)  
        
        rowCnt=1
        self.summaryList.InsertItem(rowCnt, 'In groups')
        self.summaryList.SetItem(rowCnt, 1, f"{ROWCOUNTMATRIX['GRP']:,}")
        
        rowCnt += 1
        self.summaryList.InsertItem(2, 'No radial velocity')
        self.summaryList.SetItem(2, 1, f"{ROWCOUNTMATRIX['V0']:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(3, 'Total')
        total=ROWCOUNTMATRIX['ADQL']-ROWCOUNTMATRIX['GRP']-ROWCOUNTMATRIX['V0']
        self.summaryList.SetItem(3, 1, f"{total:,}")
        #Set bold
        item = self.summaryList.GetItem(3,0)
        #print "itemText", item.GetText()       
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.summaryList.SetItem(item)  
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Other noise')
        other=ROWCOUNTMATRIX['ADQL']-ROWCOUNTMATRIX['GRP']-ROWCOUNTMATRIX['V0']-ROWCOUNTMATRIX['BIN']
        self.summaryList.SetItem(rowCnt, 1, f'{other:,}')
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, f'Remaining selected binaries')
        self.summaryList.SetItem(rowCnt, 1, f"{ROWCOUNTMATRIX['BIN']:,}")
        #Set bold
        item = self.summaryList.GetItem(rowCnt,0)
        #print "itemText", item.GetText()       
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.summaryList.SetItem(item)
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Error and noise metrics')
        #Set bold
        item = self.summaryList.GetItem(rowCnt,0)
        #print "itemText", item.GetText()       
        # Get its font, change it, and put it back:
        font = item.GetFont()
        font.MakeBold().MakeUnderlined()
        item.SetFont(font)
        self.summaryList.SetItem(item)
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N for v/dv (RA)')
        snVoverDv=self.CalcVoverdv()
        self.summaryList.SetItem(rowCnt, 1, f"{snVoverDv[0]:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N for v/dv (DEC)')
        self.summaryList.SetItem(rowCnt, 1, f"{snVoverDv[1]:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean RUWE')
        avgRuwe=self.CalcMeanXoverDx('RUWE',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgRuwe:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Distance')
        avgDIST=self.CalcMeanXoverDx('DIST',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgDIST:,}")
        
        #Mean stellar mass 
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean individual stellar mass')        
        xdata1=pd.DataFrame(xdata1, columns=['M'])
        avg=xdata1['M'].sum()/(self.parent.status['include'].sum()*2)
        #avg=xdata1.M.mean() # Can't do this because of all the zeros.
        self.summaryList.SetItem(rowCnt, 1, f"{avg:,.2f}")
        
        #Mean stellar mass  * 2
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean binary mass')        
        xdata1=pd.DataFrame(xdata1, columns=['M'])
        avg=xdata1['M'].sum()/(self.parent.status['include'].sum())
        #avg=xdata1.M.mean() # Can't do this because of all the zeros.
        self.summaryList.SetItem(rowCnt, 1, f"{avg:,.2f}")
        
        #Mean binned Binary Mass
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean binned binary mass')        
        data3TFpd=pd.DataFrame(np.log10(xdata3TF), columns=['M'])
        meanBinnedMass=data3TFpd.M.mean()
        self.summaryList.SetItem(rowCnt, 1, f"{10**meanBinnedMass:,.2f}")
        
        #Binned Binary Mass variance
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binned binary mass variance')        
        #xdata3TFpd=pd.DataFrame(xdata3TF, columns=['M'])
        varBinnedMass=data3TFpd.M.var()
        self.summaryList.SetItem(rowCnt, 1, f"{10**varBinnedMass:,.4f}")
        
        #Mean binned binary RMS 2D relative velocity 
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, f'Mean binned RMS {ND}D velocity')        
        data3TFpd['V']=np.log10(ydata3TF)
        meanBinnedRV=data3TFpd.V.mean()
        self.summaryList.SetItem(rowCnt, 1, f"{10**meanBinnedRV:,.4f}")
        
        # Binned RV vs M covariance
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binned RV vs M covariance') 
        covBinnedRV_M=data3TFpd.cov()
        self.summaryList.SetItem(rowCnt, 1, f"{10**covBinnedRV_M.M[1]:,.4f}")
                                 
        # Binned RV vs M covariance over M variance (ie slope)
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Slope') 
        self.slope=covBinnedRV_M.M[1]/covBinnedRV_M.M[0]
        self.summaryList.SetItem(rowCnt, 1, f"{self.slope:,.3f}")
                                 
        # Offset
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Offset') 
        self.offset=meanBinnedRV-self.slope*meanBinnedMass
        self.summaryList.SetItem(rowCnt, 1, f"{self.offset:,.3f}")

        # Coefficient of correlation (r)
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Coefficient of correlation (r)') 
        self.correlation=covBinnedRV_M.M[1]/math.sqrt(covBinnedRV_M.M[0]*covBinnedRV_M.V[1])
        self.summaryList.SetItem(rowCnt, 1, f"{self.correlation:,.3f}")
        
        # Calculate confidence interval for slope
        xLog10=np.log10(dataTFBins.getBinXArray('centre'))
        yLog10=np.log10(dataTFBins.getBinYArray(self.combo_yAvg.GetValue()))
        xLog10Sum=0
        
        n=0
        for i in range(numTFBins):
            if math.isnan(xLog10[i]):
                continue
            xLog10Sum=xLog10Sum+xLog10[i]
            n=n+1
        xMeanLog10=xLog10Sum/n
        yMinusYhatSum=0
        xMinusXbarSum=0
        for i in range(numTFBins):
            if math.isnan(xLog10[i]):
                continue
            yHat_i=self.XreturnY(xLog10[i])
            yMinusYhatSum=yMinusYhatSum+(yLog10[i]-yHat_i)**2
            xMinusXbarSum=xMinusXbarSum+(xLog10[i]-xMeanLog10)**2
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, f'Slope confidence interval (1 sigma)')
        self.summaryList.SetItem(rowCnt, 1, f"{math.sqrt((yMinusYhatSum/xMinusXbarSum)/(n-2)):,.2f}")
                
        xdataLMS=[dataTFBins.binUpperBounds[0],dataTFBins.binLowerBounds[numTFBins-1]]
        ydataLMS=[10**self.XreturnY(math.log10(dataTFBins.binUpperBounds[0])),10**self.XreturnY(math.log10(dataTFBins.binLowerBounds[numTFBins-1]))]
        
        self.lineLMS, = self.TulleyFPlot.axes.plot(xdataLMS, ydataLMS, 'yo--', linewidth=1, markersize=1)
        
        if not prntVersion:
            legend1.append(self.lineLMS)
            legend2.append('LMS line')
        
        self.TulleyFPlot.axes.legend(legend1, legend2)
        if prntVersion:
            self.TulleyFPlot.axes.get_legend().remove()
        self.TulleyFPlot.axes.xaxis.set_major_locator(ticker.AutoLocator())
        self.TulleyFPlot.axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        
        self.TulleyFPlot.draw(self.lineLMS, xdataLMS, ydataLMS, True, [] )
        
        self.TulleyFPlot.Layout()
        self.Layout()
        self.parent.printArrays()

        self.plot_but.Enable()
    
    def XreturnY(self, X):
        # Return lower outlier range.
        Y=self.slope*float(X) + self.offset
        return Y
    def CalcVoverdv(self):
        
        vRAoverdv=self.parent.status['include']*self.parent.binaryDetail.vRA.abs()/self.parent.binaryDetail.vRAerr.abs()
        vDECoverdv=self.parent.status['include']*self.parent.binaryDetail.vDEC.abs()/self.parent.binaryDetail.vDECerr.abs()
        
        totalSelected=self.parent.status['include'].sum()
        
        return([round(vRAoverdv.sum()/totalSelected,2),round(vDECoverdv.sum()/totalSelected,2)])
        
        
    def CalcMeanXoverDx(self, col, col_error):
        if col_error:
            XoverDx=self.parent.status['include']*self.parent.X[col].abs()/self.parent.X[col_error].abs()
            XoverDx=XoverDx+self.parent.status['include']*self.parent.X[col].abs()/self.parent.X[col_error].abs()

            totalSelected=self.parent.status['include'].sum()
            totalSelected=totalSelected*2
        else:
            XoverDx=self.parent.status['include']*self.parent.X[col].abs()
            totalSelected=self.parent.status['include'].sum()
        
        return round(XoverDx.sum()/totalSelected,2)
        
class AladinView(wx.Panel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=12, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=3, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Draw button
        
        self.refresh_but = Button(self, id=wx.ID_ANY, label="&Refresh", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.refresh_but.Bind(wx.EVT_BUTTON, self.restoreListCtrl)
        fgsizer.Add(self.refresh_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        # Draw button
        
        self.prim_but = Button(self, id=wx.ID_ANY, label="&Primary", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.prim_but.Bind(wx.EVT_BUTTON, self.onPrimaryStar)
        fgsizer.Add(self.prim_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        # Draw button
        
        self.sec_but = Button(self, id=wx.ID_ANY, label="&Secondary", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.sec_but.Bind(wx.EVT_BUTTON, self.onCompanionStar)
        fgsizer.Add(self.sec_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Draw button
        
        self.cat_but = Button(self, id=wx.ID_ANY, label="&Gaia eDR3 catalogue", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.cat_but.Bind(wx.EVT_BUTTON, self.onGaiaeDR3catalogue)
        fgsizer.Add(self.cat_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        sortChoices=['SOURCE_ID_PRIMARY',
                    #'M':M,
                    'r',
                    'vRA',
                    'vDEC',                    
                    'V2D',
                    'DIST',
                    'RA_MEAN',
                    'DEC_MEAN',
                    'ra1',
                    'dec1',
                    'mag1',
                    'MAG1',
                    'PARALLAX1',
                    'DIST1',
                    'RUWE1',
                    'SOURCE_ID_SECONDARY',
                    'ra2',
                    'dec2',
                    'mag2',
                    'MAG2',
                    'PARALLAX2',
                    'DIST2',
                    'RUWE2'
                    #'M':M,
                    ]
        # Sort by
        self.sort = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=sortChoices)
        self.sort.Bind(wx.EVT_CHOICE, self.onSort)
        self.sort.SetSelection(int(gl_cfg.getItem('sort','ALADIN')))
        self.sort.SetToolTip("Select column to sort on.")
        fgsizer.Add(self.sort, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        # Asc/desc
        self.ascBool = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['Descending', 'Ascending'])
        self.ascBool.Bind(wx.EVT_CHOICE, self.onSort)
        self.ascBool.SetSelection(int(gl_cfg.getItem('order','ALADIN')))
        self.ascBool.SetToolTip("Select sort order.")
        fgsizer.Add(self.ascBool, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Create summary results list box.
        self.binaryList=ListCtrl(self, size=(560, 750)) 
        fg2sizer.Add(self.binaryList, 0, wx.ALL, 2)
        self.binaryList.InsertColumn(0, "Primary", wx.LIST_FORMAT_RIGHT, width=170 )
        self.binaryList.SetColumnWidth(0, 170)
        self.binaryList.InsertColumn(1, "Companion", wx.LIST_FORMAT_RIGHT, width=170 )
        self.binaryList.SetColumnWidth(1, 170)
        self.binaryList.InsertColumn(2, "Separation", wx.LIST_FORMAT_RIGHT, width=80 )
        self.binaryList.SetColumnWidth(2, 80)
        self.binaryList.InsertColumn(3, "V2D", wx.LIST_FORMAT_RIGHT, width=60 )
        self.binaryList.SetColumnWidth(3, 60)
        self.binaryList.InsertColumn(4, "DIST", wx.LIST_FORMAT_RIGHT, width=60 )
        self.binaryList.SetColumnWidth(4, 60)
        
##########   Aladin.u-strasbg.fr #########################
        self.cosmicBrowser = wx.html2.WebView.New(self, id=wx.ID_ANY, url="", pos=wx.DefaultPosition, size=(750, 750))
        fg2sizer.Add(self.cosmicBrowser)
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(500, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Property", wx.LIST_FORMAT_RIGHT, width=80 )
        self.summaryList.SetColumnWidth(0, 80)
        self.summaryList.InsertColumn(1, "Primary", wx.LIST_FORMAT_RIGHT, width=170 )
        self.summaryList.SetColumnWidth(1, 170)
        self.summaryList.InsertColumn(2, "Companion", wx.LIST_FORMAT_RIGHT, width=170 )
        self.summaryList.SetColumnWidth(2, 170)
        self.SetSizer(self.sizer_v)
        self.Layout()
        self.onRefreshPage()
        self.restoreListCtrl()
    
    def onSort(self, event=0):
        gl_cfg.setItem('sort',int(self.sort.GetSelection()),'ALADIN')
        gl_cfg.setItem('order',int(self.ascBool.GetSelection()),'ALADIN')
        self.parent.export=pd.DataFrame(self.parent.export)
        self.parent.export=self.parent.export.sort_values(by=self.sort.GetValue(), ascending=int(self.ascBool.GetSelection()))
        self.restoreListCtrl()
    def restoreListCtrl(self, event=0, limit=1000):
        
        self.parent.export=pd.DataFrame(self.parent.export)
        try:
            self.parent.export=self.parent.export.sort_values(by=self.sort.GetValue(), ascending=int(self.ascBool.GetSelection()))
        except Exception:
            print('Sort failed')
        self.binaryList.DeleteAllItems()
        self.summaryList.DeleteAllItems()
        self.exportDisplay=pd.DataFrame(self.parent.export)
        
        try:
            self.exportDisplay=self.exportDisplay.convert_dtypes()
        except Exception:
            self.exportDisplay=pd.DataFrame()
        for index, row  in self.exportDisplay.iterrows():
            V2D = math.sqrt(row.vRA**2+row.vDEC**2)
            DIST = (row.DIST1+row.DIST2)/2
            self.binaryList.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, round(row.r,4), round(V2D,4), round(DIST,2)])
            if index > 1000:
                return
    def onGaiaeDR3catalogue(self, event=0):
    
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        binaryIdx = self.binaryList.GetNextSelected(-1)
        if hasattr(self,'exportDisplay'):
            binaryROW=self.exportDisplay.iloc[binaryIdx]
            coords=str(binaryROW.ra1) + ', ' + str(binaryROW.dec1)
        
        self.onRefreshPage(coords, coords)
        
    def onPrimaryStar(self, event=0):
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        binaryIdx = self.binaryList.GetNextSelected(-1)
        if hasattr(self,'exportDisplay'):
            binaryROW=self.exportDisplay.iloc[binaryIdx]
            coords=str(binaryROW.ra1) + ', ' + str(binaryROW.dec1)
        self.AddStats(binaryROW)
        self.onRefreshPage(coords)
        
    def onCompanionStar(self, event=0):
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file

        binaryIdx = self.binaryList.GetNextSelected(-1)
        if hasattr(self,'exportDisplay'):
            binaryROW=self.exportDisplay.iloc[binaryIdx]
            coords=str(binaryROW.ra2) + ', ' + str(binaryROW.dec2)
            
        self.AddStats(binaryROW)
        
        self.onRefreshPage(coords)
    def AddStats(self, binaryROW):
        
        self.summaryList.DeleteAllItems()
        self.summaryList.Append(['SOURCE_ID',str(binaryROW.SOURCE_ID_PRIMARY),str(binaryROW.SOURCE_ID_SECONDARY)])
        self.summaryList.Append(['RA',binaryROW.ra1,binaryROW.ra2])
        self.summaryList.Append(['DEC',binaryROW.dec1,binaryROW.dec2])
        self.summaryList.Append(['mag',binaryROW.mag1,binaryROW.mag2])
        self.summaryList.Append(['MAG',binaryROW.MAG1,binaryROW.MAG2])
        self.summaryList.Append(['PARALLAX',binaryROW.PARALLAX1,binaryROW.PARALLAX2])
        self.summaryList.Append(['DIST',binaryROW.DIST1,binaryROW.DIST2])
        self.summaryList.Append(['RUWE',binaryROW.RUWE1,binaryROW.RUWE2])
        self.summaryList.Append(['Separation',binaryROW.r,''])
        self.summaryList.Append(['vRA',binaryROW.vRA,''])
        self.summaryList.Append(['vDEC',binaryROW.vDEC,''])
        self.summaryList.Append(['V2D',binaryROW.V2D,''])
        self.summaryList.Append(['DIST',binaryROW.DIST,''])
        self.summaryList.Append(['RA_MEAN',binaryROW.RA_MEAN,''])
        self.summaryList.Append(['Log10vRA',binaryROW.Log10vRA,''])
        self.summaryList.Append(['Log10vDEC',binaryROW.Log10vDEC,''])
        self.summaryList.Append(['Log10r',binaryROW.Log10r,''])
        
    def onRefreshPage(self, coords='319.248057505893, -53.8355296313695', coords2=''):
        
        
        data = '''
<!DOCTYPE>
<html>
  <head>    
    <!-- Aladin Lite CSS style file -->
    <link rel="stylesheet" href="http://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css" />

  </head>  
  <body>   
<!-- you can skip the following line if your page already integrates the jQuery library -->
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.12.1.min.js" charset="utf-8"></script>
    
<!-- insert this snippet where you want Aladin Lite viewer to appear and after the loading of jQuery -->
    <!-- Aladin Lite container at requested dimensions -->
    <div id="aladin-lite-div" style="width:730px;height:700px;"></div>
        <input id="DSS" type="radio" name="survey" value="P/DSS2/color"><label for="DSS">DSS color<label>
        <input id="2MASS" type="radio" name="survey" value="P/2MASS/color"><label for="2MASS">2MASS<label>
        <input id="allwise" type="radio" name="survey" value="P/allWISE/color"><label for="allwise">AllWISE<label>
        <input id="GALEX" type="radio" name="survey" value="P/GALEXGR6/AIS/color"><label for="GALEX">GALEX<label>
        <input id="Fermi" type="radio" name="survey" value="P/Fermi/color"><label for="Fermi">Fermi<label>
        <input id="IRIS" type="radio" name="survey" value="P/IRIS/color"><label for="IRIS">IRIS<label>

    <!-- Aladin Lite JS code -->
    <script type="text/javascript" src="http://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.js" charset="utf-8"></script>

    <!-- Creation of Aladin Lite instance with initial parameters -->
    <script type="text/javascript">
        var aladin = A.aladin('#aladin-lite-div', {survey: "P/DSS2/color", fov:0.25, target: "%s"});
        $('input[name=survey]').change(function() {
            aladin.setImageSurvey($(this).val());
        });
        aladin.addCatalog(A.catalogFromVizieR('I/350/gaiaedr3', '%s', 0.2, {shape: 'square', sourceSize: 8, color: 'red', onClick: 'showPopup'}));
  
    </script>
  </body>
</html>
        ''' % (coords, coords2)
        
        hostname = "aladin.u-strasbg.fr" #example
        response = os.system("ping -c 1 " + hostname)
        #and then check the response...
        if response == 0:
            self.cosmicBrowser.SetPage(data,"")
            print(hostname+' available.')
        else:
            print(hostname+' not available!')

class matplotlibPanel(wx.Panel):
    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)
        self.parent=parent

        self.figure = Figure(figsize=(8,5)) # Inches!?Figure(figsize=(5,2.5))
        
        # Axes & labels
        self.axes = self.figure.add_subplot(111)
        self.frames=[] 
        self.axes.set_ylabel('1D relative velocity in plane of sky (km/s)', fontsize=FONTSIZE)
        self.axes.set_xlabel('2D separation (pc)', fontsize=FONTSIZE)
        self.axes.set_title("<n> binary pairs showing actual velocity and Newtonian expectation", fontsize=FONTSIZE)
        self.axes.patch.set_facecolor('0.25')  # Grey shade
        self.axes.grid(b=1, which='major', axis='both')
        self.axes.set_autoscale_on(True)
        self.axes.margins(1)
        self.axes.set_yscale('log', nonpositive='clip')
        self.axes.set_xscale('log', nonpositive='clip')
        
        self.figure.tight_layout(h_pad=1, w_pad=1)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        #### Hidden toolbar
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        #self.toolbar.Hide()
    
    def set_limits(self, xLimits,yLimits):
    
        self.axes.set_xlim(xLimits)
        self.axes.set_ylim(yLimits)    
    
    def draw(self, line, xdata, ydata, error, errorData):

        if hasattr(self.parent, 'combo_yLog') and self.parent.combo_yLog.GetValue()=='log':
            self.axes.set_yscale('log', nonpositive='clip')
        else:
            self.axes.set_yscale('linear')
        self.axes.relim()
        self.axes.autoscale_view(True,True,True)
        #
        
        ANGLE=0
        for tick in self.axes.xaxis.get_major_ticks():
            tick.label.set_fontsize(FONTSIZE) 
            tick.label.set_rotation(ANGLE)
        for tick in self.axes.yaxis.get_major_ticks():
            tick.label.set_fontsize(FONTSIZE) 
            tick.label.set_rotation(ANGLE)  # vertical, 'horizontal'
        for tick in self.axes.xaxis.get_minor_ticks():
            tick.label.set_fontsize(FONTSIZE) 
            tick.label.set_rotation(ANGLE)
        for tick in self.axes.yaxis.get_minor_ticks():
            tick.label.set_fontsize(FONTSIZE) 
            tick.label.set_rotation(ANGLE)  # vertical, 'horizontal'
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
    def formatPrint(self):
        self.axes.patch.set_facecolor('1')  # White
        

if __name__ == '__main__':
    app = wx.App(0)
    frame = wx.Frame(None, id=wx.ID_ANY, title="Binary Star Workbench", pos=wx.DefaultPosition, size=[1800,950])
    fa = MainPanel(frame)
    frame.Show()
    app.MainLoop()