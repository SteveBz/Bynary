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
from PyBins2 import *
from starSystems import *
from newtonian_values import xdata2, ydata2, ydata2_1D

from astropy_healpix import HEALPix # pip3 install astropy_healpix
import healpy as hp  #pip3 install healpy
from astropy.coordinates import Galactic, SkyCoord # pip3 install astropy
import astropy.units as u

import re
import configVar

from matplotlib.ticker import (MultipleLocator, NullFormatter, ScalarFormatter, AutoMinorLocator, FormatStrFormatter)

from astroquery.gaia import Gaia
from shutil import copyfile as cp


#Gaia.remove_jobs(["job_id_1","job_id_2",...])
#Gaia.login()
#jobs = [job for job in Gaia.list_async_jobs()]
#job_ids = [inp.jobid for inp in jobs]

gl_cfg=configVar.configVar("./binClient.conf")
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
RELEASE='DR3'
CATALOG='KEB-0.50pc'
HPS_SCALE=192
HPS_SCALE = int(gl_cfg.getItem('hps_scale','SETTINGS', 192))
FONTSIZE=20
#Cancel command for import button
CANCEL=False 
import SQLLib
import db              # For star/observing database.
dbiStro=db.db()
database = gl_cfg.getItem('database','SETTINGS')
#databaseid = gl_cfg.getItem('databaseuserid','SETTINGS')
#databasepwd = gl_cfg.getItem('databasepwd','SETTINGS')
iStro=dbiStro.conSQLite(database) 

from sqlalchemy import create_engine # pip3 install sqlalchemy
encoding='UTF8'
engine = create_engine('sqlite:///bynary_db_v2.db', echo=True, encoding=encoding)
sqlite_connection = engine.connect()
#iStro=sqlite_connection
#CREATE TABLE "TBL_RELEASE" (
#	"RELEASE_"	TEXT,
#	PRIMARY KEY("RELEASE_")
#);
#CREATE TABLE "TBL_CATALOG" (
#	"RELEASE_"	TEXT,
#	"CATALOG"	TEXT,
#	PRIMARY KEY("RELEASE_","CATALOG")
#);
class MainPanel(wx.Panel):
    def __init__(self, mainFrame):
        self.mainFrame=mainFrame
        wx.Panel.__init__(self, self.mainFrame)
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
        
        self.mainFrame.SetMenuBar(menuBar)
        self.mainFrame.statusbar = self.mainFrame.CreateStatusBar()
        
        self.sizer_nb=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_nb)
        self.nb=Notebook(self)
        self.sizer_nb.Add(self.nb, 1, wx.ALL|wx.EXPAND, 5)

        self.nb.printArrays=self.printArrays
        self.nb.StatusBarNormal=self.StatusBarNormal
        self.nb.StatusBarProcessing=self.StatusBarProcessing
        
        # Here we create a panel and a notebook on the panel
        self.releasePage = gaiaStarRetrieval(self.nb, self)
        self.catalogPage = gaiaBinaryRetrieval(self.nb, self)
        self.retrievalPage = dataRetrieval(self.nb, self)
        self.filterPage = dataFilter(self.nb, self)
        self.plottingPage = kineticDataPlotting(self.nb, self)
        self.skyPage = skyDataPlotting(self.nb, self)
        self.hrPage = HRDataPlotting(self.nb, self)
        self.GaiaMassPage = MassPlotting(self.nb, self)
        self.TulleyFisherPage = TFDataPlotting(self.nb, self)
        self.NumberDensityPage = NumberDensityPlotting(self.nb, self)
        #NumberDensityPlotting
        self.AladinPage = AladinView(self.nb, self)
        
#        #
#        ## add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.releasePage, "Download stars and attributes")
        self.nb.AddPage(self.catalogPage, "Download binary catalogue")
        self.nb.AddPage(self.retrievalPage, "Load Binary catalogue")
        self.nb.AddPage(self.filterPage, "Apply binary filters")
        self.nb.AddPage(self.skyPage, "Sky density plot")
        self.nb.AddPage(self.hrPage, "H-R plot")
        self.nb.AddPage(self.plottingPage, "Kinematic plot")
        self.nb.AddPage(self.GaiaMassPage, "Est Mass vs FLAME Mass plot")
        self.nb.AddPage(self.TulleyFisherPage, "Velocity vs Mass plot")
        self.nb.AddPage(self.NumberDensityPage, "Star Density vs Distance plot")
        self.nb.AddPage(self.AladinPage, "View Binaries in Aladin Lite")
        self.nb.SetSelection(int(gl_cfg.getItem('tab','SETTINGS', 0))) # get setting from config file)
        
    def StatusBarNormal(self, text=""):
        
        t=time.strftime("%Y/%m/%d/ %H:%M:%S")
        if text:
            self.mainFrame.statusbar.SetStatusText(f'{t} | {text}')
        else:
            self.mainFrame.statusbar.SetStatusText(t)
            
        self.mainFrame.statusbar.SetBackgroundColour(Colour(50, 50, 60)) #Grey
        
    def StatusBarProcessing(self, text=""):
        
        t=time.strftime("%Y/%m/%d/ %H:%M:%S")
        if text:
            self.mainFrame.statusbar.SetStatusText(f'{t} | {text}')
        else:
            self.mainFrame.statusbar.SetStatusText(t)
            
        self.mainFrame.statusbar.SetBackgroundColour(Colour(150, 50, 60)) #Grey
        
        wx.Yield()
        
    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnClose(self, event):
        #print('Closing message')
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
    
        #try:
        #    print(f'length of "selectedStarIDs" = {len(self.nb.selectedStarIDs)}')
        #except Exception:
        #    print(f'"selectedStarIDs" not found')
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
            print(f'- sum of massVmassOut = {self.nb.status["massVmassOut"].sum()}')
            print(f'- sum of tfOut = {self.nb.status["tfOut"].sum()}')
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
        static_Release = StaticText(self, id=wx.ID_ANY, label="Release (DR3):")
        self.sizer_h.Add(static_Release, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        
        #Release select
        self.release = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        releases=self.releaseRefresh()
        #self.release.Bind(wx.EVT_CHOICE, self.catRefresh)
        self.release.SetSelection(int(gl_cfg.getItem('release','GAIASTAR', 0)))
        self.release.SetToolTip("Select release source (currently only eDR3)")
        self.sizer_h.Add(self.release, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        global RELEASE
        RELEASE = self.release.GetValue()
        
        # Create download only data check box
        rvDR2StaticText = StaticText(self, id=wx.ID_ANY, label="Add RV from DR2?")
        self.sizer_h.Add(rvDR2StaticText, 0, wx.ALL, 2)
        self.rvDR2CheckBox = CheckBox(self)
        self.rvDR2CheckBox.SetToolTip("Add Radial Velocity from DR2.  Applicable to eDR3.")
        self.rvDR2CheckBox.SetValue(gl_cfg.getBoolean('edr3', 'GAIASTAR'))
        self.sizer_h.Add(self.rvDR2CheckBox, 0, wx.ALL, 2)
        
        self.textctrl_newRelease = TextCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.sizer_h.Add(self.textctrl_newRelease, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_newRelease.SetToolTip("Enter new release name.")
        self.textctrl_newRelease.SetMaxLength(5)
        self.textctrl_newRelease.setValidRoutine(self.textctrl_newRelease.Validate_Not_Empty)
        
        self.buttonRelease = Button(self, wx.ID_ANY, u"New release")
        self.buttonRelease.SetToolTip("Enter name of new release (5 chars).")
        self.buttonRelease.Bind(wx.EVT_LEFT_DOWN, self.addRelease)
        self.sizer_h.Add(self.buttonRelease, 0,wx.ALIGN_LEFT|wx.ALL , 5)

        self.sizer_h.AddSpacer(1)
        self.sizer_h.AddSpacer(1)
        
        # Select RA from (degrees)
        static_RAfrom = StaticText(self, id=wx.ID_ANY, label="RA from (Deg):")
        self.sizer_h.Add(static_RAfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_RAfrom = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rafrom','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=360,initial=int(gl_cfg.getItem('rafrom', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_RAfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_RAfrom.SetToolTip("Lower RA to download - 0 to 360")
        
        # Select RA to (degrees)
        static_RAto = StaticText(self, id=wx.ID_ANY, label="RA to (Deg):")
        self.sizer_h.Add(static_RAto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_RAto = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rato','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=360,initial=int(gl_cfg.getItem('rato', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_RAto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_RAto.SetToolTip("Upper RA to download to - out of 360")
        
        # Select Px from (mas)
        static_PXfrom = StaticText(self, id=wx.ID_ANY, label="Px from (mas):")
        self.sizer_h.Add(static_PXfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXfrom = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxfrom','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxfrom', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_PXfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXfrom.SetToolTip("Lower Parallax to download - 0 to 1000 (expectation is '3')")
        
        # Select Px to (degrees)
        static_PXto = StaticText(self, id=wx.ID_ANY, label="Px to (mas):")
        self.sizer_h.Add(static_PXto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXto = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxto','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxto', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_PXto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_PXto.SetToolTip("Upper Parallax to download to - out of 1000 (expectation is '1000')")
        
                #and parallax_over_error > 5
                #and phot_g_mean_flux_over_error > 50
                #and phot_rp_mean_flux_over_error > 10
                #and phot_bp_mean_flux_over_error > 10
                
        #self.sizer_h.AddSpacer(1)
        #self.sizer_h.AddSpacer(1)
        #self.sizer_h.AddSpacer(1)
        #self.sizer_h.AddSpacer(1)
        # Select parallax_over_error
        static_Px_err = StaticText(self, id=wx.ID_ANY, label="Px/err:")
        self.sizer_h.Add(static_Px_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Px_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('px_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('px_err', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_Px_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Px_err.SetToolTip("parallax_over_error to download - 0 to 100 (expectation is '5')")
        
        # Select phot_g_mean_flux_over_error
        static_G_err = StaticText(self, id=wx.ID_ANY, label="G/err:")
        self.sizer_h.Add(static_G_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_G_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('g_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('g_err', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_G_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_G_err.SetToolTip("phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50')")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err = StaticText(self, id=wx.ID_ANY, label="Rp/err:")
        self.sizer_h.Add(static_Rp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_Rp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err.SetToolTip("phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err = StaticText(self, id=wx.ID_ANY, label="Bp/err:")
        self.sizer_h.Add(static_Bp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_Bp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Bp_err.SetToolTip("phot_bp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        
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
        self.button1.Enable()
        CANCEL= True
        
        self.parent.StatusBarNormal('Completed OK')
    #    
    #    
    def releaseRefresh(self, event=0):
        
        global RELEASE
        #RELEASE = self.release.GetValue()
        TBL_RELEASE = SQLLib.sqlSelect(iStro, "TBL_RELEASE")
        #TBL_RELEASE.setWhereValueString("RELEASE_", RELEASE)
        TBL_RELEASE.setReturnCol("RELEASE_")
        TBL_RELEASE.setSortCol("RELEASE_",1) # -ve is desc, +ve is ascending
        try:
            records = TBL_RELEASE.selectRecordSet()
        except Exception:
            TBL_RELEASE.executeIAD('CREATE TABLE IF NOT EXISTS "TBL_RELEASE" (  \
                                                    "RELEASE_"	TEXT, \
                                                    PRIMARY KEY("RELEASE_")\
                                                    );'
            )
            TBL_RELEASE.executeIAD('CREATE TABLE IF NOT EXISTS "TBL_OBJECTS" ( \
                                                    "RELEASE_"	TEXT, \
                                                    "source_id"	BIGINT, \
                                                    "index"	BIGINT, \
                                                    "RA_"	FLOAT, \
                                                    "ra_error"	FLOAT, \
                                                    "DEC_"	FLOAT, \
                                                    "dec_error"	FLOAT, \
                                                    "parallax"	FLOAT, \
                                                    "parallax_error"	FLOAT, \
                                                    "phot_g_mean_mag"	FLOAT, \
                                                    "bp_rp"	FLOAT, \
                                                    "radial_velocity"	FLOAT, \
                                                    "radial_velocity_error"	FLOAT, \
                                                    "parallax_over_error"	FLOAT, \
                                                    "phot_g_mean_flux_over_error"	FLOAT, \
                                                    "phot_rp_mean_flux_over_error"	FLOAT, \
                                                    "phot_bp_mean_flux_over_error"	FLOAT, \
                                                    "pmra"	FLOAT, \
                                                    "pmra_error"	FLOAT, \
                                                    "pmdec"	FLOAT, \
                                                    "pmdec_error"	FLOAT, \
                                                    "ruwe"	FLOAT, \
                                                    "mass_flame"	FLOAT, \
                                                    "mass_flame_upper"	FLOAT, \
                                                    "mass_flame_lower"	FLOAT, \
                                                    "age_flame"	FLOAT, \
                                                    "age_flame_upper"	FLOAT, \
                                                    "age_flame_lower"	FLOAT, \
                                                    "classprob_dsc_specmod_binarystar"	FLOAT, \
                                                    PRIMARY KEY("RELEASE_","source_id") \
                                                    );'
            )
            TBL_RELEASE.executeIAD('CREATE TABLE IF NOT EXISTS "TBL_BINARIES" ( \
                                                "RELEASE_"	TEXT, \
                                                "CATALOG"	TEXT, \
                                                "SOURCE_ID_PRIMARY"	BIGINT, \
                                                "SOURCE_ID_SECONDARY"	BIGINT, \
                                                "index"	BIGINT, \
                                                "SEPARATION"	FLOAT, \
                                                "HEALPIX"	BIGINT, \
                                                "NOT_GROUPED"	BOOLEAN, \
                                                "HAS_RADIAL_VELOCITY"	BOOLEAN, \
                                                "STATUS"	TEXT, \
                                                PRIMARY KEY("RELEASE_","CATALOG","SOURCE_ID_PRIMARY","SOURCE_ID_SECONDARY") \
                                        );'
            )
            TBL_RELEASE.executeIAD('CREATE VIEW ALLSTARS2 (SOURCE_ID, CATALOG, RELEASE_, RA_, DEC_, STATUS, NOT_GROUPED, HAS_RADIAL_VELOCITY, PHOT_G_MEAN_MAG, SEPARATION, RUWE) \
                                        AS SELECT SOURCE_ID_SECONDARY, CATALOG, b.RELEASE_, o1.RA_, o1.DEC_, b.STATUS, b.NOT_GROUPED, b.HAS_RADIAL_VELOCITY, o1.PHOT_G_MEAN_MAG, SEPARATION, o1.RUWE \
                                        FROM TBL_BINARIES b \
                                            left join TBL_OBJECTS o1 \
                                            on b.SOURCE_ID_SECONDARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_ \
                                        UNION ALL \
                                        SELECT SOURCE_ID_PRIMARY, CATALOG, c.RELEASE_, o2.RA_, o2.DEC_, c.STATUS, c.NOT_GROUPED, c.HAS_RADIAL_VELOCITY, o2.PHOT_G_MEAN_MAG, SEPARATION, o2.RUWE \
                                        FROM TBL_BINARIES c \
                                            left join TBL_OBJECTS o2 \
                                            on c.SOURCE_ID_PRIMARY=o2.SOURCE_ID and c.RELEASE_ = o2.RELEASE_\
                                        ;')
            records = TBL_RELEASE.selectRecordSet()
        self.releases=[]
        
        #PHOT_G_MEAN_FLUX_OVER_ERROR	
        #PHOT_RP_MEAN_FLUX_OVER_ERROR
        #PHOT_BP_MEAN_FLUX_OVER_ERROR
        #MASS_FLAME
        #MASS_FLAME_UPPER
        #MASS_FLAME_LOWER
        #AGE_FLAME
        #AGE_FLAME_UPPER
        #AGE_FLAME_LOWER
        #CLASSPROB_DSC_SPECMOD_BINARYSTAR
        for row in records.fetchall():
            self.releases.append(str(row[0]))
        #
        self.release.Clear()
        self.release.SetItems(self.releases)
        #
        #gl_cfg.getItem('release', 'GAIASTAR') # Get setting in config file
        self.release.SetSelection(int(gl_cfg.getItem('release', 'GAIASTAR', 0))) # Get setting from config file
        return self.releases
    def addRelease(self, event=0):
        
        attributes=[self.textctrl_newRelease]
        for attribute in attributes:
            if not attribute.runValidRoutine():
                return
            
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
            
        self.parent.StatusBarProcessing('Star download commenced')
        
        global CANCEL
        CANCEL = False
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
        dr2=''
        if self.rvDR2CheckBox.GetValue():
            dr2='dr2_'
        selectFrom = f"""SELECT
            distinct gaia_source.source_id,
            gaia_source.ra,
            gaia_source.ra_error,
            gaia_source.dec,
            gaia_source.dec_error,
            gaia_source.parallax,
            gaia_source.parallax_error,
            gaia_source.phot_g_mean_mag,
            gaia_source.bp_rp,
            gaia_source.{dr2}radial_velocity,
            gaia_source.{dr2}radial_velocity_error,
            gaia_source.parallax_over_error,
            gaia_source.phot_g_mean_flux_over_error,
            gaia_source.phot_rp_mean_flux_over_error,
            gaia_source.phot_bp_mean_flux_over_error,
            astrophysical_parameters.mass_flame,
            astrophysical_parameters.mass_flame_upper,
            astrophysical_parameters.mass_flame_lower,
            astrophysical_parameters.age_flame_upper,
            astrophysical_parameters.age_flame_lower,
            astrophysical_parameters.age_flame,
            astrophysical_parameters.classprob_dsc_specmod_binarystar,
            --gaia_source.phot_variable_flag,
            --gaia_source.teff_val,
            --gaia_source.a_g_val, 
            gaia_source.pmra,
            gaia_source.pmra_error, 
            gaia_source.pmdec,
            gaia_source.ruwe,
            gaia_source.pmdec_error
        
            FROM gaiadr3.gaia_source
                left join  gaiadr3.astrophysical_parameters
                on gaia_source.source_id=astrophysical_parameters.source_id
        """
        
        count=0
        step = 1
        step = int(gl_cfg.getItem('hps_step','SETTINGS', 1))
        lowerRA=self.spin_RAfrom.GetValue()
        upperRA=self.spin_RAto.GetValue()
        forceIt=self.forceDownloadCheckBox.GetValue()
        release=self.release.GetValue()
        TotalCount=0
        #forceDownload=self.forceDownloadCheckBox.GetValue()
        downloadOnly=self.downloadOnlyCheckBox.GetValue()
        #    
        #if self.deactivateIndicesCheckBox.GetValue():
        #    #Deactivate 4 indices on TBL_OBJECTS
        #    TBL_OBJECTS  = SQLLib.sql(iStro, "TBL_OBJECTS ")
        #    #ALTER INDEX IDX_TBL_OBJECTS1 to 4 INACTIVE
        #    for idx in range(1,5):
        #        bulkSQL=f"DROP INDEX IF EXISTS IDX_TBL_OBJECTS{idx} ;"
        #        TBL_OBJECTS .executeIAD(bulkSQL)
        #        print(f'{bulkSQL} of 4')
        
        commentG='--'
        commentRp='--'
        commentBp='--'
        
        if int(self.spin_G_err.GetValue()):
            commentG=''
        if int(self.spin_Rp_err.GetValue()):
            commentRp=''
        if int(self.spin_Bp_err.GetValue()):
            commentBp=''
            
        self.parent.StatusBarProcessing(f'Delete old records for RA {lowerRA} to {upperRA} degrees')

        TBL_OBJECTS = SQLLib.sqlDelete(iStro, "TBL_OBJECTS")
        #TBL_OBJECTS.setWhereValueLTFloat('RA_', i+1)
        #TBL_OBJECTS.setWhereValueGEFloat('RA_', i)
        TBL_OBJECTS.setWhereAndList('RA_', [f'>={lowerRA}',f'<{upperRA}'])
        TBL_OBJECTS.setWhereValueString('RELEASE_', release)
        try:
            TBL_OBJECTS.deleteRecordSet()
        except Exception:
            self.parent.StatusBarProcessing(f'Delete failed')

        
        if self.deactivateIndicesCheckBox.GetValue():
            #Deactivate 4 indices on TBL_OBJECTS
            TBL_OBJECTS  = SQLLib.sql(iStro, "TBL_OBJECTS ")
            #ALTER INDEX IDX_TBL_OBJECTS1 to 4 INACTIVE
            for idx in range(1,5):
                bulkSQL=f"DROP INDEX IF EXISTS IDX_TBL_OBJECTS{idx} ;"
                TBL_OBJECTS .executeIAD(bulkSQL)
                self.parent.StatusBarProcessing(f'{bulkSQL} of 4')
                
        for i in range(lowerRA, upperRA, step):
            query[0] = selectFrom + f"""
            -- RA {i} to {i+step}
            WHERE gaia_source.ra >= {i} and gaia_source.ra < {i+step}
            --    source_id in (3242763706493692544, 3242763706493692288)
                and parallax >= {self.spin_PXfrom.GetValue()}
                and parallax < {self.spin_PXto.GetValue()}
                and parallax_over_error > {self.spin_Px_err.GetValue()}
                -- Many dim stars don't have photometric data on Gaia
                -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
                {commentG} and phot_g_mean_flux_over_error > {self.spin_G_err.GetValue()}
                {commentRp} and phot_rp_mean_flux_over_error > {self.spin_Rp_err.GetValue()} 
                {commentBp} and phot_bp_mean_flux_over_error > {self.spin_Bp_err.GetValue()}
            """
            
            #print( query[0] )
            #self.parent.StatusBarProcessing (f'i = {i}')
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            #filePrefix='iEquals0' + date_time
            self.parent.StatusBarProcessing(f'start query: ra = {i} to {i+1}')
            # output_data = gaia_cnxn.gaia_get_pairs_of_close_stars(save_to_pickle=True, dump_to_file=True, output_format='json')
            
            if not os.path.isdir(f'bindata/{release}'):
                os.mkdir (f'bindata/{release}')
            if not os.path.isdir(f'bindata/{release}/stars'):
                os.mkdir (f'bindata/{release}/stars')
                
            if (not forceIt) and os.path.isfile(f'bindata/{release}/stars/gaia_{release}_RA{i}'):
                data =pd.read_pickle(f'bindata/{release}/stars/gaia_{release}_RA{i}')
                self.parent.StatusBarProcessing(f'Restore from local pickle file')
            else:
                gaia_cnxn = da.GaiaDataAccess()
                data = gaia_cnxn.gaia_query_to_pandas(query[0])
                self.parent.StatusBarProcessing(f'Download from Gaia')
                self.parent.StatusBarProcessing(f'bindata/{release}/stars/gaia_{release}_RA{i}')
                data.to_pickle(f'bindata/{release}/stars/gaia_{release}_RA{i}', protocol=int(gl_cfg.getItem('pickle_protocol', 'SETTINGS', 4))) # save setting in config file)
                
            lenArray=len(data)
            self.listctrl.Append([release,i, i+step, f'{lenArray:,}', date_time])
            self.listctrl.EnsureVisible(i-lowerRA)
            self.Layout()
            wx.Yield()
            
            TotalCount=TotalCount+lenArray
            self.static_Total.SetLabel(f'{TotalCount:,}')
            if downloadOnly:
                self.spin_RAfrom.SetValue(i)
                gl_cfg.setItem('rafrom',i, 'GAIASTAR') # save setting in config file
                continue
            #
            ##data.to_sql()
            #print(f'delete old records for RA {i} to {i+1} degrees')
            #TBL_OBJECTS = SQLLib.sqlDelete(iStro, "TBL_OBJECTS")
            ##TBL_OBJECTS.setWhereValueLTFloat('RA_', i+1)
            ##TBL_OBJECTS.setWhereValueGEFloat('RA_', i)
            #TBL_OBJECTS.setWhereAndList('RA_', [f'>={i}',f'<{i+1}'])
            #TBL_OBJECTS.setWhereValueString('RELEASE_', release)
            #try:
            #    TBL_OBJECTS.deleteRecordSet()
            #except Exception:
            #    print('Delete Failed.')
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            #filePrefix='iEquals0' + date_time
            self.parent.StatusBarProcessing(f'start processing {len(data):,} records at {date_time}.' )
            bulkSQL='execute block as begin'
            source_id_array=[]
            data2=data.to_dict()
            self.parent.StatusBarProcessing(f'Number of stars: {len(data):,} in {TotalCount:,}')
            global sqlite_connection
            data = data.rename(columns={
                                               'ra': 'RA_',
                                               'dec': 'DEC_',
                                               'dr2_radial_velocity': 'radial_velocity',
                                               'dr2_radial_velocity_error': 'radial_velocity_error',
                                        })
            #data.reset_index(drop=True, inplace=True)
            #data = data.iloc[: , 1:]
            data.drop(['dist_pc'], axis=1, inplace=True)
            data.drop(['dist_err_pc'], axis=1, inplace=True)
            data['RELEASE_'] = release
            data.to_sql("TBL_OBJECTS", con=sqlite_connection, schema='main', index=False, if_exists='append', method=None)
            self.Layout()
            wx.Yield()
            
            label=i
            self.button1.SetLabel(f'{label}')
            self.Layout()
            if CANCEL:
                CANCEL = False
                self.button1.Enable()
                return
            wx.Yield()
            bulkSQL=''
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            self.parent.StatusBarProcessing('end query')
            # output_data = gaia_cnxn.gaia_get_pairs_o
            self.spin_RAfrom.SetValue(i)
            gl_cfg.setItem('rafrom',i, 'GAIASTAR') # save setting in config file
        
        self.spin_RAfrom.SetValue(lowerRA)
        gl_cfg.setItem('rafrom',lowerRA, 'GAIASTAR') # save setting in config file
        print(2)

        if self.deactivateIndicesCheckBox.GetValue():
        #    #ALTER INDEX IDX_TBL_OBJECTS1 ACTIVE
        #    #ALTER INDEX IDX_TBL_OBJECTS2 ACTIVE
        #    #ALTER INDEX IDX_TBL_OBJECTS3 ACTIVE
        #    #ALTER INDEX IDX_TBL_OBJECTS4 ACTIVE
        #    #Deactivate 4 indices on TBL_OBJECTS
            TBL_OBJECTS  = SQLLib.sql(iStro, "TBL_OBJECTS ")
            #    #ALTER INDEX IDX_TBL_OBJECTS1 to 4 ACTIVE
            SQL=f"CREATE INDEX IDX_TBL_OBJECTS1 ON TBL_OBJECTS (SOURCE_ID);"
            TBL_OBJECTS .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_OBJECTS2 ON TBL_OBJECTS (PARALLAX);"
            TBL_OBJECTS .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_OBJECTS3 ON TBL_OBJECTS (RA_);"
            TBL_OBJECTS .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_OBJECTS4 ON TBL_OBJECTS (DEC_);"
            TBL_OBJECTS .executeIAD(SQL)
                
        self.button1.Enable()

        self.parent.StatusBarNormal('Completed OK')
                
class gaiaBinaryRetrieval(wx.Panel):
    
    def dump(self, obj):
      for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'
        #
        ##Try to find existing files, if not, create blank one
        #files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        #if len (sys.argv)>1:
        #    arg=sys.argv[1].strip()
        #else:
        #    arg=''
        #if arg == 'new':
        #    #Force exception if 'new' passed
        #    fileSuffix='new'
        #    fileSuffix2='new'
        #else:
        #    fileSuffix='saved'
        #    fileSuffix2='pickle'
        #
        global RELEASE
        global CATALOG
        #for file in files:
        #    try:
        #        setattr(self.parent,file, pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.{fileSuffix}'))
        #    except Exception:
        #        setattr(self.parent,file, pd.DataFrame())

        # adding exception handling
        try:
            cp(f'bindata/{RELEASE}/{CATALOG}/binClient.conf', 'binClient.conf')
        except IOError as e:
            self.parent.StatusBarProcessing("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print(f"Unexpected error: {sys.exc_info()}")
            exit(1)
        
        self.parent.StatusBarProcessing("File restore done!\n")
        #print(self.parent.status)
        #try:
        #    file_to_read = open('bindata/starSystemList.'+fileSuffix2, 'rb') #File containing example object
        #    self.parent.starSystemList = pickle.load(file_to_read) # Load saved object
        #    file_to_read.close()
        #except Exception:
        #    self.parent.starSystemList=binaryStarSystems(len(self.parent.status))
        
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
        ##########################              Line 1 
        # Select release
        
        static_Release = StaticText(self, id=wx.ID_ANY, label="Release:")
        self.sizer_h.Add(static_Release, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Release select
        self.release = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        releases=self.releaseRefresh()
        self.release.Bind(wx.EVT_CHOICE, self.catRefresh)
        self.release.SetSelection(int(gl_cfg.getItem('release','GAIABINARY',0)))
        self.release.SetToolTip("Select release source")
        self.sizer_h.Add(self.release, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        RELEASE = self.release.GetValue()
        
        # Catalogue prompt
        static_Catalogue = StaticText(self, id=wx.ID_ANY, label="Catalogue:")
        self.sizer_h.Add(static_Catalogue, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.catalogue = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(110,-1), choices=[], value='')
        self.catalogue.SetToolTip("Select Catalogue")
        self.catRefresh()
        self.catalogue.SetSelection(int(gl_cfg.getItem('catalog', 'GAIABINARY',0)))
        self.sizer_h.Add(self.catalogue, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        CATALOG = self.catalogue.GetValue()
        
        self.textctrl_newCatalog = TextCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.sizer_h.Add(self.textctrl_newCatalog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_newCatalog.SetToolTip("Enter new catalogue name.")
        self.textctrl_newCatalog.SetMaxLength(10)
        self.textctrl_newCatalog.setValidRoutine(self.textctrl_newCatalog.Validate_Not_Empty)
        
        
        # Healpix scale (192, 768, 3072, 12288)
        
        self.HPScale_combo = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['192','768','3072', '12288'], value=gl_cfg.getItem('hps_scale', 'SETTINGS', 0))
        self.HPScale_combo.SetValue(int(gl_cfg.getItem('hps_scale', 'SETTINGS', 0)))
        self.HPScale_combo.SetToolTip("Select scale for Healpix '192','768', '3072' or '12,288'")
        self.HPScale_combo.Bind(wx.EVT_CHOICE, self.onHPScale_Refresh)
        self.sizer_h.Add(self.HPScale_combo, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Load Catalogue
        
        static_Separation = StaticText(self, id=wx.ID_ANY, label="Separation (pc):")
        self.sizer_h.Add(static_Separation, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        # Values (ie row 2)
        self.textctrl_Separation = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('value', 'GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT) 
        self.sizer_h.Add(self.textctrl_Separation, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_Separation.SetToolTip("Enter separation in parsecs")
        self.textctrl_Separation.setValidRoutine(self.textctrl_Separation.Validate_Float)
        
        # Select from Healpics
        static_HPSfrom = StaticText(self, id=wx.ID_ANY, label="HPS from:")
        self.sizer_h.Add(static_HPSfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_HPSfrom = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('hpsfrom','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=HPS_SCALE,initial=int(gl_cfg.getItem('rafrom', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_HPSfrom, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_HPSfrom.SetToolTip(f"Lower HPS to download 0 to {HPS_SCALE}")
        
        # Select 2 degrees
        static_HPSto = StaticText(self, id=wx.ID_ANY, label="HPS to:")
        self.sizer_h.Add(static_HPSto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_HPSto = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('hpsto','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=HPS_SCALE,initial=int(gl_cfg.getItem('rato', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_HPSto, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_HPSto.SetToolTip(f"Upper Healpix to scan to - out of {HPS_SCALE}")
        
        #******************************  Primary star **************************************
        
        # Select Px from (mas)
        static_PXfrom1 = StaticText(self, id=wx.ID_ANY, label="Px1 from (mas):")
        self.sizer_h.Add(static_PXfrom1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.textctrl_PXfrom1 = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxfrom1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, )  
        self.sizer_h.Add(self.textctrl_PXfrom1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_PXfrom1.SetToolTip("Primary lower parallax to download - 0 to 1000 (expectation is '3.3')")
        
        # Select Px to (degrees)
        static_PXto1 = StaticText(self, id=wx.ID_ANY, label="Px1 to (mas):")
        self.sizer_h.Add(static_PXto1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXto1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxto1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxto1', 'GAIABINARY',0)))  
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
        self.spin_Px_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('px_err1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('px_err1', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Px_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Px_err1.SetToolTip("Primary parallax_over_error to download - 0 to 100 (expectation is '20')")
        
        # Select phot_g_mean_flux_over_error
        static_G_err = StaticText(self, id=wx.ID_ANY, label="G/err (1):")
        self.sizer_h.Add(static_G_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_G_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('g_err1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('g_err1', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_G_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_G_err1.SetToolTip("Primary phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50')")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err1 = StaticText(self, id=wx.ID_ANY, label="Rp/err (1):")
        self.sizer_h.Add(static_Rp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err1', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Rp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err1.SetToolTip("Primary phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '20')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err1 = StaticText(self, id=wx.ID_ANY, label="Bp/err (1):")
        self.sizer_h.Add(static_Bp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err1', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Bp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Bp_err1.SetToolTip("Primary phot_bp_mean_flux_over_error to download - 0 to 100 (expectation is '20')")
        
        #******************************  Companion star **************************************
        
        # Select Px from (mas)
        static_PXfrom2 = StaticText(self, id=wx.ID_ANY, label="Px2 from (mas):")
        self.sizer_h.Add(static_PXfrom2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.textctrl_PXfrom2 = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxfrom2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, )  
        self.sizer_h.Add(self.textctrl_PXfrom2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_PXfrom2.SetToolTip("Lower companion parallax to download - 0 to 1000 (expectation is '3')")
        self.textctrl_PXfrom2.setValidRoutine(self.textctrl_PXfrom2.Validate_Float)
        
        # Select Px to (degrees)
        static_PXto2 = StaticText(self, id=wx.ID_ANY, label="Px2 to (mas):")
        self.sizer_h.Add(static_PXto2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Values (ie row 2)
        self.spin_PXto2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('pxto2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxto2', 'GAIABINARY',0)))  
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
        self.spin_Px_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('px_err2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('px_err2', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Px_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Px_err2.SetToolTip("Companion parallax_over_error to download - 0 to 100 (expectation is '5')")
        
        # Select phot_g_mean_flux_over_error
        static_G_err2 = StaticText(self, id=wx.ID_ANY, label="G/err (2):")
        self.sizer_h.Add(static_G_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_G_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('g_err2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('g_err2', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_G_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_G_err2.SetToolTip("Companion phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50')")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err2 = StaticText(self, id=wx.ID_ANY, label="Rp/err (2):")
        self.sizer_h.Add(static_Rp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err2', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Rp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err2.SetToolTip("Companion phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err2 = StaticText(self, id=wx.ID_ANY, label="Bp/err (2):")
        self.sizer_h.Add(static_Bp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err2', 'GAIABINARY',0)))  
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
        
        # Set maximum healpix file size
        static_max_data = StaticText(self, id=wx.ID_ANY, label="Max. file size:")
        self.sizer_h.Add(static_max_data, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.textCtrl_max_data = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('max_data','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.sizer_h.Add(self.textCtrl_max_data, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textCtrl_max_data.SetToolTip("Maximum healpix file size (expectation is '1E6')")
        self.textCtrl_max_data.setValidRoutine(self.textCtrl_max_data.Validate_Float)
        
        # Set minimum distance from galactic plane
        static_b_gt = StaticText(self, id=wx.ID_ANY, label="|b| > :")
        self.sizer_h.Add(static_b_gt, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_mod_b_gt = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mod_b_gt','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=90,initial=int(gl_cfg.getItem('mod_b_gt', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_mod_b_gt, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_mod_b_gt.SetToolTip("Distance from galactic plane. Mod (b) greater than entered value (expectation is '15')")
        
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
        
        static_Total = StaticText(self, id=wx.ID_ANY, label="Total pairs:")
        self.sizer_h2.Add(static_Total, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Total
        
        self.static_Total = StaticText(self, id=wx.ID_ANY, label='N/a')
        self.sizer_h2.Add(self.static_Total, 0, wx.ALL, 5)
        
        
        # Number in clusters prompt
        
        static_Cluster = StaticText(self, id=wx.ID_ANY, label="Number in clusters:")
        self.sizer_h2.Add(static_Cluster, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Cluster
        
        #ROWCOUNTMATRIX['GRP']=len(self.parent.selectedStarBinaryMappings)
        self.static_Cluster = StaticText(self, id=wx.ID_ANY, label=f'N/a')
        self.sizer_h2.Add(self.static_Cluster, 0, wx.ALL, 5)
        
        ################New catalogue name
        self.buttonCatalogue = Button(self, wx.ID_ANY, u"New catalogue")
        self.buttonCatalogue.SetToolTip("Enter name of new catalogue (1-10 chars).")
        self.buttonCatalogue.Bind(wx.EVT_LEFT_DOWN, self.addCatalogue)
        self.sizer_v2.Add(self.buttonCatalogue, 0,wx.ALIGN_LEFT|wx.ALL , 5)
        
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
        
        self.button3 = Button(self, wx.ID_ANY, u"Clear jobs")
        self.button3.Bind(wx.EVT_LEFT_DOWN, self.OnClear)
        self.button3.SetToolTip("Clerar down old Gaia jobs.")
        self.sizer_v2.Add(self.button3, 0, wx.LEFT | wx.ALL , 5)
        
        #Deselect grouped stars (ie stars in more than 1 binary)
        
        self.ungroup = Button(self, id=wx.ID_ANY, label="&Ungroup", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.ungroup.Bind(wx.EVT_BUTTON, self.deselectDuplicates)
        self.ungroup.SetToolTip("Deselect binaries with stars that appear in more than one pair.  Ie deselect both pairs or entire cluster.")
        self.sizer_v2.Add(self.ungroup, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Reset status
        
        self.reset = Button(self, id=wx.ID_ANY, label="&Reset", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.reset.Bind(wx.EVT_BUTTON, self.resetStatus)
        self.reset.SetToolTip("Reset 'degrouping' for all binaries in this catalogue")
        self.sizer_v2.Add(self.reset, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
    def resetStatus(self, event):
        
        self.reset.Disable()
        
        self.parent.StatusBarProcessing('Resetting')
        
        global RELEASE, CATALOG
        global HPS_SCALE
        HPS_SCALE=int(self.HPScale_combo.GetValue())
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "")
        TBL_BINARIES.setAttributeBool("NOT_GROUPED", True)
        #TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i*192/HPS_SCALE
            if i<HPS_SCALE:
                TBL_BINARIES.setWhereValueLTInt("source_id", healpix)
        print(TBL_BINARIES.updateRecord())
        
        self.reset.Enable()
    
        self.parent.StatusBarNormal('Completed OK')
        
    def deselectDuplicates(self, event):
        #Freeze button
        self.ungroup.Disable()
        
        global CANCEL
        CANCEL = False
        self.parent.StatusBarProcessing('Degrouping commenced')
        
        global RELEASE, CATALOG
        global HPS_SCALE
        HPS_SCALE=int(self.HPScale_combo.GetValue())
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        #i=int(self.spin_loadType.GetValue())
        i = HPS_SCALE
        #if self.deactivateIndicesCheckBox.GetValue():
        #    #Deactivate 9 indices on TBL_BINARIES
        #    TBL_BINARIES  = SQLLib.sql(iStro, "TBL_objects ")
        #    #ALTER INDEX IDX_TBL_BINARIES1 to 9 INACTIVE
        #    for idx in range(1,10):
        #        bulkSQL=f"ALTER INDEX IDX_TBL_BINARIES{idx} ACTIVE ;"
        #        TBL_BINARIES .executeIAD(bulkSQL)
        #        print(f'{bulkSQL} of 9')
        #    bulkSQL=f"ALTER INDEX IDX_TBL_BINARIES3 INACTIVE ;"
        #    TBL_BINARIES .executeIAD(bulkSQL)
        #    print(f'{bulkSQL}')
        #    bulkSQL=f"ALTER INDEX IDX_TBL_BINARIES5 INACTIVE ;"
        #    TBL_BINARIES .executeIAD(bulkSQL)
        #    print(f'{bulkSQL}')
            
            
            
            
#        CREATE VIEW ALLSTARS2 (SOURCE_ID, CATALOG, RELEASE_, RA_, DEC_, STATUS, NOT_GROUPED, HAS_RADIAL_VELOCITY, PHOT_G_MEAN_MAG, SEPARATION, RUWE)
#AS SELECT SOURCE_ID_SECONDARY, CATALOG, b.RELEASE_, o1.RA_, o1.DEC_, b.STATUS, b.NOT_GROUPED, b.HAS_RADIAL_VELOCITY, o1.PHOT_G_MEAN_MAG, SEPARATION, o1.RUWE
#FROM TBL_BINARIES b
#    left join TBL_OBJECTS o1
#    on b.SOURCE_ID_SECONDARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_
#UNION ALL
#SELECT SOURCE_ID_PRIMARY, CATALOG, c.RELEASE_, o2.RA_, o2.DEC_, c.STATUS, c.NOT_GROUPED, c.HAS_RADIAL_VELOCITY, o2.PHOT_G_MEAN_MAG, SEPARATION, o2.RUWE
#FROM TBL_BINARIES c
#    left join TBL_OBJECTS o2
#    on c.SOURCE_ID_PRIMARY=o2.SOURCE_ID and c.RELEASE_ = o2.RELEASE_;
    
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "ALLSTARS2")
        TBL_BINARIES.setReturnCol("SOURCE_ID")
        TBL_BINARIES.setGroupByCol("SOURCE_ID")
        TBL_BINARIES.setHavingGTInt("COUNT(SOURCE_ID)",1) # Having count > 1 (ie duplicate SOURCE_ID)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", True)
        TBL_BINARIES.setSortCol("SOURCE_ID")

        #if self.loadType_combo.GetSelection()==0:
        healpix=2**35*4**(12-2)*i*192/HPS_SCALE
        if i<HPS_SCALE:
            TBL_BINARIES.setWhereValueLTInt("SOURCE_ID", healpix)
        #if self.loadType_combo.GetSelection()==1:
        #    TBL_BINARIES.setWhereValueLTInt("RA_", i)
        #if self.loadType_combo.GetSelection()==2:
        #    TBL_BINARIES.setWhereValueLTInt("DEC_", i)
        #    TBL_BINARIES.setWhereValueLTInt(-i, "DEC_")
        
        sql = TBL_BINARIES.getSQL()
        print (sql)
        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        self.parent.StatusBarProcessing(f'Ungrouping {lenArray:,} records started')
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
                if CANCEL:
                    CANCEL = False
                    #Release button
                    self.ungroup.Enable()
                    self.dbload.Enable()
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
        
        #if self.deactivateIndicesCheckBox.GetValue():
        #    #Deactivate 9 indices on TBL_BINARIES
        #    TBL_BINARIES  = SQLLib.sql(iStro, "TBL_objects ")
        #    #ALTER INDEX IDX_TBL_BINARIES1 to 9 INACTIVE
        #    for idx in range(1,10):
        #        bulkSQL=f"ALTER INDEX IDX_TBL_BINARIES{idx} ACTIVE ;"
        #        TBL_BINARIES .executeIAD(bulkSQL)
        #        print(f'{bulkSQL} of 9')
                
        #Release button
        self.ungroup.Enable()
        self.Layout()
        
        self.parent.StatusBarNormal('Completed OK')
        
    def OnClear(self, event=0):
        
        self.button3.Disable()
        gaia_cnxn = da.GaiaDataAccess()
        jobs = [job for job in gaia_cnxn.list_async_jobs()]
        #job_ids = [inp.jobid for inp in jobs]
        numJobs = len(jobs)
        num=0
        for inp in jobs:
            num=num+1
            gaia_cnxn.remove_jobs([inp.jobid])
            self.parent.StatusBarProcessing(f'Job id = {inp.jobid} removed. ({num:,} of {numJobs:,})')
            wx.Yield()
            global CANCEL
            if CANCEL:
                CANCEL = False
                self.button3.Enable()
                return
        self.parent.StatusBarNormal(f'Complete OK - {numJobs} removed.')
        self.button3.Enable()
        
    def onHPScale_Refresh(self, event=0):

        global HPS_SCALE
        HPS_SCALE=int(self.HPScale_combo.GetValue())
        self.spin_HPSfrom.SetMax(HPS_SCALE)
        self.spin_HPSfrom.SetToolTip(f"Upper Healpix to scan from - '0' to {HPS_SCALE}")
        self.spin_HPSto.SetMax(HPS_SCALE)
        self.spin_HPSto.SetToolTip(f"Upper Healpix to scan to - '0' to {HPS_SCALE}")
        
        gl_cfg.setItem('hps_scale', HPS_SCALE,'SETTINGS')
        
    def addCatalogue(self, event=0):
        
        attributes=[self.textctrl_newCatalog]
        for attribute in attributes:
            if not attribute.runValidRoutine():
                return
        global RELEASE
        TBL_CATALOG = SQLLib.sqlInsert(iStro, "TBL_CATALOG")
        catalog=self.textctrl_newCatalog.GetValue()
        if len(catalog)>0 and  len(catalog)<=10:
            TBL_CATALOG .setAttributeString("RELEASE_", self.release.GetValue())
            TBL_CATALOG .setAttributeString("CATALOG", catalog)
            records = TBL_CATALOG.insertRecord()
            self.textctrl_newCatalog.SetValue('')
        self.catRefresh()
     
            
    def OnCancel(self, event=0):

        global CANCEL
        self.button1.Enable()
        CANCEL= True
        self.button3.Enable()
        self.ungroup.Enable()
        
        self.parent.StatusBarNormal('Completed OK')
        
    def catRefresh(self, event=0):
        
        global RELEASE
        RELEASE = self.release.GetValue()
        TBL_CATALOG = SQLLib.sqlSelect(iStro, "TBL_CATALOG")
        TBL_CATALOG.setWhereValueString("RELEASE_", RELEASE)
        TBL_CATALOG.setReturnCol("CATALOG")
        TBL_CATALOG.setSortCol("CATALOG",1) # -ve is desc, +ve is ascending
        try:
            records = TBL_CATALOG.selectRecordSet()
        except Exception:
            TBL_CATALOG.executeIAD('CREATE TABLE IF NOT EXISTS "TBL_CATALOG" ( \
                                                "RELEASE_"	TEXT NOT NULL, \
                                                "CATALOG"	TEXT NOT NULL, \
                                                FOREIGN KEY("RELEASE_") REFERENCES "TBL_RELEASE"("RELEASE_"), \
                                                PRIMARY KEY("RELEASE_","CATALOG") \
                                                );'
            )
            records = TBL_CATALOG.selectRecordSet()
        self.catalogues=[]
        
        for row in records.fetchall():
            #print(f'catalogue={catalogue}')
            self.catalogues.append(str(row[0]))
        #
        self.catalogue.Clear()
        self.catalogue.SetItems(self.catalogues)
        self.catalogue.SetSelection(0)
        
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIASTAR') # save setting in config file
        
    def releaseRefresh(self, event=0):
        
        global RELEASE
        #RELEASE = self.release.GetValue()
        TBL_RELEASE = SQLLib.sqlSelect(iStro, "TBL_RELEASE")
        #TBL_RELEASE.setWhereValueString("RELEASE_", RELEASE)
        TBL_RELEASE.setReturnCol("RELEASE_")
        TBL_RELEASE.setSortCol("RELEASE_",1) # -ve is desc, +ve is ascending
        records = TBL_RELEASE.selectRecordSet()
        self.releases=[]
        
        for row in records.fetchall():
            self.releases.append(str(row[0]))
        #
        self.release.Clear()
        self.release.SetItems(self.releases)
        #
        self.release.SetSelection(int(gl_cfg.getItem('release', 'GAIABINARY',0))) # Get setting from config file
        return self.releases
        
    def binaries(self, record, i, release, catalogue ):
        TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ");
        TBL_BINARIES .setAttributeIntBig("SOURCE_ID_PRIMARY", record.source_id)
    
        TBL_BINARIES .setAttributeIntBig("SOURCE_ID_SECONDARY", record.source_id2)
    
        #global release, catalogue
        TBL_BINARIES .setAttributeString("release_", release)
        TBL_BINARIES .setAttributeString("CATALOG", catalogue)
        TBL_BINARIES .setAttributeBool("NOT_GROUPED", True)
        #print(record)
        if hasattr(record, 'radial_velocity'):
            if self.is_number(record.radial_velocity) and self.is_number(record.radial_velocity2):
                TBL_BINARIES .setAttributeBool("HAS_RADIAL_VELOCITY", True)
                TBL_BINARIES.setAttributeString("STATUS", "")
            else:
                TBL_BINARIES .setAttributeBool("HAS_RADIAL_VELOCITY", False)
                TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES .setAttributeFloat("SEPARATION", record.pairdistance)
        TBL_BINARIES .setAttributeInteger("HEALPIX", i)
        return TBL_BINARIES .getInsertSQL()
    def read_GaiaBinaries(self, event):

        global CANCEL
        CANCEL = False
        self.parent.StatusBarProcessing('Downloading binary lists from Gaia')
        
        attributes=[self.textctrl_Separation, self.textctrl_PXfrom2, self.textctrl_PXfrom1, self.textCtrl_max_data]
        for attribute in attributes:
            if not attribute.runValidRoutine():
                return
            
        self.button1.Disable()
        
        self.listctrl.DeleteAllItems()
        
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('value',self.textctrl_Separation.GetValue(), 'GAIABINARY') # save setting in config file 
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('hpsfrom',self.spin_HPSfrom.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('hpsto',self.spin_HPSto.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('downloadonly',self.downloadOnlyCheckBox.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('forceredownload', bool(self.forceDownloadCheckBox.GetValue()), 'GAIABINARY') # save notebook tab setting in config file
        gl_cfg.setItem('deactivateindices',bool(self.deactivateIndicesCheckBox.GetValue()), 'GAIABINARY') # save notebook tab setting in config file
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        gl_cfg.setItem('pxto1',self.spin_PXto1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('pxfrom1',self.textctrl_PXfrom1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('rp_err1',self.spin_Rp_err1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('bp_err1',self.spin_Bp_err1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('px_err1',self.spin_Px_err1.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('g_err1',self.spin_G_err1.GetValue(), 'GAIABINARY') # save setting in config file
        
        gl_cfg.setItem('pxto2',self.spin_PXto2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('pxfrom2',self.textctrl_PXfrom2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('rp_err2',self.spin_Rp_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('bp_err2',self.spin_Bp_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('px_err2',self.spin_Px_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('g_err2',self.spin_G_err2.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('mod_b_gt',self.spin_mod_b_gt.GetValue(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('max_data',self.textCtrl_max_data.GetValue(), 'GAIABINARY') # save setting in config file
        
        gl_cfg.setItem('hps_scale', int(self.HPScale_combo.GetValue()),'SETTINGS')
        
                        
        query=[0]
        #
            
        Gaia50000Select="""-- Binary star selection ADQL from K el Badry paper.  Comments by S Cookson.
        -- Pair distance is angular distance. Other fields removed for separate star data download.
        -- It is expected that the star data is downloaded once - about 8 million stars - and the binaries are downloaded many times.
        -- This separation of data speeds up the binary downloads.
        SELECT g2.source_id as source_id2, t1.source_id, t1.radial_velocity as radial_velocity, g2.radial_velocity as radial_velocity2, distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)) AS pairdistance
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
        #print(pc)
        nsigma=8
        release=self.release.GetValue()
        #release='fDR3'
        catalogue=self.catalogue.GetValue()
        mod_b_gt=float(abs(self.spin_mod_b_gt.GetValue()))
        max_data=abs(float(self.textCtrl_max_data.GetValue()))
        countMe=0
        #forceIt=False # Force download
        
        forceIt=self.forceDownloadCheckBox.GetValue() # Force download
        downloadOnly=self.downloadOnlyCheckBox.GetValue() # Download only, don't update
            
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
        
        commentG1='--'
        commentRp1='--'
        commentBp1='--'
        commentG2='--'
        commentRp2='--'
        commentBp2='--'
        
        if int(self.spin_G_err1.GetValue()):
            commentG1=''
        if int(self.spin_Rp_err1.GetValue()):
            commentRp1=''
        if int(self.spin_Bp_err1.GetValue()):
            commentBp1=''
        if int(self.spin_G_err2.GetValue()):
            commentG2=''
        if int(self.spin_Rp_err2.GetValue()):
            commentRp2=''
        if int(self.spin_Bp_err2.GetValue()):
            commentBp2=''
        timeoutCount=0
        HPSlower = int(self.spin_HPSfrom.GetValue())
        HPSupper = int(self.spin_HPSto.GetValue())
        step=1
        HPS=range(HPSlower,HPSupper,step)
        #print (HPS)
        nside = int(math.sqrt(int(self.HPScale_combo.GetValue())/12))
        #print (nside)
        
        #print(f'delete old records for healix {HPSlower} to {HPSupper}')
        t=time.strftime("%Y/%m/%d/ %H:%M:%S")
        self.parent.StatusBarProcessing(f'Delete old records for healix {HPSlower} to {HPSupper}')
        wx.Yield()
        TBL_BINARIES = SQLLib.sqlDelete(iStro, "TBL_BINARIES");
        #TBL_BINARIES.setWhereValueLTFloat('HEALPIX', HPSupper)
        #TBL_BINARIES.setWhereValueGEFloat('HEALPIX', HPSlower)
        TBL_BINARIES.setWhereAndList('HEALPIX', [f'>={HPSlower}',f'<{HPSupper}'])
        TBL_BINARIES.setWhereValueString('CATALOG', catalogue)
        TBL_BINARIES.setWhereValueString('RELEASE_', release)
        print(TBL_BINARIES.getSQL())
        try:
            TBL_BINARIES.deleteRecordSet()
        except Exception:
            t=time.strftime("%Y/%m/%d/ %H:%M:%S")
            self.parent.StatusBarProcessing(f'Delete failed')
            wx.Yield()
            pass
        
        if self.deactivateIndicesCheckBox.GetValue():
            #Deactivate 9 indices on TBL_BINARIES
            TBL_BINARIES  = SQLLib.sql(iStro, "TBL_BINARIES ")
            #ALTER INDEX IDX_TBL_BINARIES1 to 9 INACTIVE
            for idx in range(1,12):
                bulkSQL=f"DROP INDEX IF EXISTS IDX_TBL_BINARIES{idx} ;"
                TBL_BINARIES .executeIAD(bulkSQL)
                self.parent.StatusBarProcessing(f'TBL_BINARIES{idx} of 11')
            
        for i in HPS:
            
            healpixA=int(2**35*4**(12-2)*i*192/HPS_SCALE)
            healpixB=int(2**35*4**(12-2)*(i+step)*192/HPS_SCALE)
        
            self.parent.StatusBarProcessing(f"{nside} = {i}")
            theta, phi = hp.pix2ang(nside, i)
            ra = np.degrees(pi*2.-phi)
            dec = -np.degrees(theta-pi/2.)
            
            # Convert to Galactic Coords.
            sc = SkyCoord(ra=ra*u.deg,dec=dec*u.deg)
            #gal_l=str(sc.galactic.l)
            #deg, minutes, seconds, fraction =  re.split('[dm.]', gal_l)
            #            #print (seconds)
            #gal_l=float(deg) + float(minutes)/60  + float(seconds)/3600
            #                        
            gal_b=str(sc.galactic.b)
            deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_b)
            gal_b=float(deg) + float(minutes)/60 + float(seconds)/3600
            
            if abs(gal_b) < mod_b_gt:
                self.parent.StatusBarProcessing(f"- Dropping healpix {i}; |b| = {round(gal_b, 1)}, ra = {round(ra,1)}, dec = {round(dec,1)}")
                continue
        
            self.spin_HPSfrom.SetValue(i)
            gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
            fromHealpixClause=f"""
            -- index file: {i}
            source_id >= {healpixA} and source_id < {healpixB} and
            """
            self.parent.StatusBarProcessing (f"{i} {healpixA}")
            
            Gaia50000From=f"""
            FROM
            -- outer product of candidates for primary star with candidates for secondary star
            -- t1 is primary
            (select * from gaiadr3.gaia_source
            where
                {fromHealpixClause}
                -- outside solar system and within 333 pcs
                parallax between {self.textctrl_PXfrom1.GetValue()} and {self.spin_PXto1.GetValue()}
                 and parallax_over_error > {self.spin_Px_err1.GetValue()}
                -- Many dim stars don't have photometric data on Gaia
                -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
                {commentG1} and phot_g_mean_flux_over_error > {self.spin_G_err1.GetValue()}
                {commentRp1} and phot_rp_mean_flux_over_error > {self.spin_Rp_err1.GetValue()} 
                {commentBp1} and phot_bp_mean_flux_over_error > {self.spin_Bp_err1.GetValue()}
                )
                as t1,
            (select * from gaiadr3.gaia_source
            where 
                {fromHealpixClause}
                {commentRp2} {commentBp2} bp_rp is not null and
                -- outside solar system and within 333 pcs
                parallax between {self.textctrl_PXfrom2.GetValue()} and {self.spin_PXto2.GetValue()} 
                and parallax_over_error > {self.spin_Px_err2.GetValue()} 
                -- Many dim stars don't have photometric data on Gaia
                -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
                {commentG2} and phot_g_mean_flux_over_error > {self.spin_G_err2.GetValue()} 
                {commentRp2} and phot_rp_mean_flux_over_error > {self.spin_Rp_err2.GetValue()}
                {commentBp2} and phot_bp_mean_flux_over_error > {self.spin_Bp_err2.GetValue()}
                )
                as g2
            """
        
            query[0]=Gaia50000Select+" "+Gaia50000From+" "+Gaia50000Where
            
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            self.parent.StatusBarProcessing(f'start query: healpix = {i} to {i+1}')
            if not os.path.isdir(f'bindata/{release}'):
                os.mkdir (f'bindata/{release}')
            if not os.path.isdir(f'bindata/{release}/{catalogue}'):
                os.mkdir (f'bindata/{release}/{catalogue}')
            try:
                if (not forceIt) and os.path.isfile(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}'):
                    data =pd.read_pickle(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}')
                    self.parent.StatusBarProcessing('Local copy restored')
                else:
                    #print('Temporary workouround.  Delete <continue> here -->')
                    #continue
                    print(query[0])
                    gaia_cnxn = da.GaiaDataAccess()
                    data = gaia_cnxn.gaia_query_to_pandas(query[0])
                    #self.parent.StatusBarProcessing(data)
                    data.to_pickle(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}', protocol=int(gl_cfg.getItem('pickle_protocol', 'SETTINGS', 4)))
            except Exception:
                self.parent.StatusBarProcessing (f'timeout for HPS i = {i}')
                timeoutCount=timeoutCount+1
                self.spin_HPSfrom.SetValue(i)
                gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
                continue
            
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            
            dataLen=len(data)
            countMe=countMe+dataLen
            self.static_Total.SetLabel(f'{countMe:,}')
            self.listctrl.Append([release,catalogue, separation, i, i+step, f'{dataLen:,}', date_time])
            try:
                self.listctrl.EnsureVisible(i-HPSlower-timeoutCount)
            except Exception:
                pass
            self.Layout()
            wx.Yield()
            if downloadOnly:
                self.spin_HPSfrom.SetValue(i)
                gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
                continue
            
            #If there is no 'next' file then it's ok to download one from Gaia.  If there is a 'next' file, then we don't want to overload the processor.
            forked = 0
            #if not os.path.isfile(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i+1}'):
            #    newpid = os.fork()
            #    if not newpid:
            #        #if not parent (ie it is the child) fork then
            #        print (f'Forking to update DB files for HPS {i}')
            #        forked = 1
            #    else:
            #        #if parent fork then leave it and skip to next Gaia Download.
            #        continue
            #
            #print(f'delete old records for healix {i}')
            #TBL_BINARIES = SQLLib.sqlDelete(iStro, "TBL_BINARIES");
            #TBL_BINARIES.setWhereValueInt('HEALPIX', i)
            #TBL_BINARIES.setWhereValueString('CATALOG', catalogue)
            #TBL_BINARIES.setWhereValueString('RELEASE_', release)
            #print(TBL_BINARIES.getSQL())
            #try:
            #    TBL_BINARIES.deleteRecordSet()
            #except Exception:
            #    print('delete failed')
            #    pass
            if max_data and len(data) > max_data:
                self.parent.StatusBarProcessing(f"- Dropping healpix {i}; length of data = {len(data):,}, |b| = {round(gal_b, 1)}, ra = {round(ra,1)}, dec = {round(dec,1)}")
                continue
        
            self.parent.StatusBarProcessing(f'start processing record. Healpix {i}')
            bulkSQL='execute block as begin'
            self.parent.StatusBarProcessing(f'length of data for healpix {i} = {len(data):,}')
            source_id_array=[]
            
            global sqlite_connection
            data = data.rename(columns={
                                               'source_id': 'SOURCE_ID_PRIMARY',
                                               'source_id2': 'SOURCE_ID_SECONDARY',
                                               'pairdistance': 'SEPARATION',
                                               })
            data.reset_index(drop=True, inplace=True)
            data=data.convert_dtypes()
            dataLen=len(data)
            #data.drop(['dist_pc'], axis=1, inplace=True)
            data['RELEASE_'] = release
            data['HEALPIX'] = i
            data['CATALOG'] = catalogue
            data['NOT_GROUPED'] = True
            data['HAS_RADIAL_VELOCITY'] = False
            #data.loc[((data['radial_velocity'].isnull().values.any()) or (data['radial_velocity2'].isnull().values.any())), 'HAS_RADIAL_VELOCITY'] = False
            data['STATUS'] = ''
            #data.loc[((data['radial_velocity'].isnull().values.any()) or (data['radial_velocity2'].isnull().values.any())), 'STATUS'] = 'rv=0'
            
            data.drop(['radial_velocity'], axis=1, inplace=True)
            data.drop(['radial_velocity2'], axis=1, inplace=True)
            data.to_sql("TBL_BINARIES", con=sqlite_connection, schema='main', index=False, if_exists='append')
            
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            self.parent.StatusBarProcessing(f'updated healpix {i}')
            
            #if forked:
            #    #if not parent (ie it is the child) fork then
            #    print (f'Exiting fork after forking to update DB files for HPS {i}')
            #    sys.exit()
            
            wx.Yield()
            
            label=i
            self.button1.SetLabel(f'{label}')
            self.Layout()
            if CANCEL:
                CANCEL = False
                self.button1.Enable()
                return
            wx.Yield()
            self.spin_HPSfrom.SetValue(i)
            gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
        
        self.spin_HPSfrom.SetValue(HPSlower)
        gl_cfg.setItem('hpsfrom',HPSlower, 'GAIABINARY') # save setting in config file
        self.parent.printArrays()
                
        if self.deactivateIndicesCheckBox.GetValue():
        
            TBL_BINARIES  = SQLLib.sql(iStro, "TBL_BINARIES ")
            #    #ALTER INDEX IDX_TBL_OBJECTS1 to 4 ACTIVE
            SQL=f"CREATE INDEX IDX_TBL_BINARIES1 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_PRIMARY);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES2 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_SECONDARY);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES3 ON TBL_BINARIES (RELEASE_, CATALOG, NOT_GROUPED);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES4 ON TBL_BINARIES (RELEASE_, CATALOG, HAS_RADIAL_VELOCITY);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES5 ON TBL_BINARIES (NOT_GROUPED);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES6 ON TBL_BINARIES (HAS_RADIAL_VELOCITY);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES7 ON TBL_BINARIES (RELEASE_);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES8 ON TBL_BINARIES (CATALOG);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES9 ON TBL_BINARIES (HEALPIX);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES10 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_PRIMARY, SOURCE_ID_SECONDARY, HAS_RADIAL_VELOCITY, NOT_GROUPED);"
            TBL_BINARIES .executeIAD(SQL)
            SQL=f"CREATE INDEX IDX_TBL_BINARIES11 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_PRIMARY, HAS_RADIAL_VELOCITY, NOT_GROUPED);"
            TBL_BINARIES .executeIAD(SQL)
                
        self.button1.Enable()
        
        self.parent.StatusBarNormal('Completed OK')
        
class masterProcessingPanel(wx.Panel):
    
    def __init__(self, parent, mainPanel):
        pass
    
    def dump(self, obj):
      for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
    
    def is_number(self, s):
        
        try:
            float(s)
            return True
        except Exception:
            return False
        
    def CalcVoverdv(self):
        
        vRAoverdv=self.parent.status['include']*self.parent.binaryDetail.vRA/self.parent.binaryDetail.vRAerr
        vDECoverdv=self.parent.status['include']*self.parent.binaryDetail.vDEC/self.parent.binaryDetail.vDECerr
        totalSelected=self.parent.status['include'].sum()
        
        return([round(vRAoverdv.sum()/totalSelected,2),round(vDECoverdv.sum()/totalSelected,2)])
        
    def CalcPercentPairNotNull(self, col):
        
        XY=self.parent.status['include']*self.parent.X[col]
        XY1 = pd.DataFrame({'X':self.parent.status['include']*self.parent.X[col], 'Y':self.parent.status['include']*self.parent.Y[col]})
        XYcount=XY1[(XY1['X'] > 0) & (XY1['Y'] > 0)].count()
        totalSelected=self.parent.status['include'].sum()
        
        return round(XYcount['X']/totalSelected,2)
        
    def CalcPercentEitherNotNull(self, col):
        
        XY=self.parent.status['include']*self.parent.X[col]
        XY1 = pd.DataFrame({'X':self.parent.status['include']*self.parent.X[col], 'Y':self.parent.status['include']*self.parent.Y[col]})
        XYcount=XY1[(XY1['X'] > 0)].count() + XY1[(XY1['Y'] > 0)].count()
        totalSelected=self.parent.status['include'].sum()*2
        return round(XYcount['X']/totalSelected,2)
        
    def CalcMeanXYoverDxy(self, col, col_error=False):
        if col_error:
            XYoverDxy=self.parent.status['include']*self.parent.X[col].abs()/self.parent.X[col_error].abs()
            XYoverDxy=XYoverDxy+self.parent.status['include']*self.parent.Y[col].abs()/self.parent.Y[col_error].abs()

            totalSelected=self.parent.status['include'].sum()
            totalSelected=totalSelected*2
        else:
            XYoverDxy=self.parent.status['include']*self.parent.X[col].abs()
            XYoverDxy=XYoverDxy+self.parent.status['include']*self.parent.Y[col].abs()
            totalSelected=self.parent.status['include'].sum()*2
        
        return round(XYoverDxy.sum()/totalSelected,2)
        
        
    def XreturnY(self, X,m=0,c=0):
        if not m:
            m=self.m
        if not c:
            c=self.c
        # Return lower outlier range.
        Y=m*float(X) + c
        return Y
    
    def OnCancel(self, event=0):

        global CANCEL
        self.plot_but.Enable()
        CANCEL= True
        self.parent.StatusBarNormal('Completed OK')
        
    def createExportRecord(self, primaryPointer, star2Pointer, idxBin):
        try:
            exportRecord={
                'SOURCE_ID_PRIMARY':str(primaryPointer.source_id),
                'ra1':float(primaryPointer.ra),
                'dec1':float(primaryPointer.dec),
                'mag1':primaryPointer.mag,
                'MAG1':self.parent.X.mag[idxBin],
                'PARALLAX1':float(primaryPointer.PARALLAX),
                'parallax_error1':float(primaryPointer.parallax_error),
                'DIST1':float(primaryPointer.DIST),
                'RUWE1':primaryPointer.RUWE,
                'PMRA1':float(primaryPointer.PMRA),
                'PMRA_ERROR1':float(primaryPointer.PMRA_ERROR),
                'PMDEC1':float(primaryPointer.PMDEC),
                'PMDEC_ERROR1':float(primaryPointer.PMDEC_ERROR),
                'BminusR1':float(primaryPointer.BminusR),
                'mass_calc1':primaryPointer.mass_calc,
                'mass_flame1':primaryPointer.mass_flame,
                'mass_flame_upper1':primaryPointer.mass_flame_upper,
                'mass_flame_lower1':primaryPointer.mass_flame_lower,
                'age_flame1':primaryPointer.age_flame,
                'age_flame_upper1':primaryPointer.age_flame_upper,
                'age_flame_lower1':primaryPointer.age_flame_lower,
                #'classprob_dsc_specmod_binarystar1':Xclassprob_dsc_specmod_binarystar,
                'PROB1':primaryPointer.classprob_dsc_specmod_binarystar,
                'SOURCE_ID_SECONDARY':str(star2Pointer.source_id),
                'ra2':float(star2Pointer.ra),
                'dec2':float(star2Pointer.dec),
                'mag2':star2Pointer.mag,
                'MAG2':self.parent.Y.mag[idxBin],
                'PARALLAX2':float(star2Pointer.PARALLAX),
                'parallax_error2':float(star2Pointer.parallax_error),
                'DIST2':float(star2Pointer.DIST),
                'RUWE2':star2Pointer.RUWE,
                'PMRA2':float(star2Pointer.PMRA),
                'PMRA_ERROR2':float(star2Pointer.PMRA_ERROR),
                'PMDEC2':float(star2Pointer.PMDEC),
                'PMDEC_ERROR2':float(star2Pointer.PMDEC_ERROR),
                'BminusR2':float(star2Pointer.BminusR),
                'mass_calc2':star2Pointer.mass_calc,
                'mass_flame2':star2Pointer.mass_flame,
                'mass_flame_upper2':star2Pointer.mass_flame_upper,
                'mass_flame_lower2':star2Pointer.mass_flame_lower,
                'age_flame2':star2Pointer.age_flame,
                'age_flame_upper2':star2Pointer.age_flame_upper,
                'age_flame_lower2':star2Pointer.age_flame_lower,
                'PROB2':star2Pointer.classprob_dsc_specmod_binarystar,
                'vRA':abs(self.parent.binaryDetail.vRA[idxBin]),
                'vRAerr':abs(self.parent.binaryDetail.vRAerr[idxBin]),
                'vDEC':abs(self.parent.binaryDetail.vDEC[idxBin]),
                'vDECerr':abs(self.parent.binaryDetail.vDECerr[idxBin]),                  
                'V2D':math.sqrt(self.parent.binaryDetail.vRA[idxBin]**2+self.parent.binaryDetail.vDEC[idxBin]**2),
                'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                'RA_MEAN':(float(primaryPointer.ra)+float(star2Pointer.ra))/2,
                'DEC_MEAN':(float(primaryPointer.dec)+float(star2Pointer.dec))/2,
                'Log10vRA':np.log10(self.parent.binaryDetail.vRA[idxBin]),
                'Log10vDEC':np.log10(self.parent.binaryDetail.vDEC[idxBin]),
                'Log10r':np.log10(self.parent.binaryDetail.r[idxBin]),
                #'M':M,
                'r':self.parent.binaryDetail.r[idxBin]
            }
        except Exception:
            print(i)
            print(primaryPointer)
            print(star2Pointer)
            print(self.parent.binaryDetail)
            return
        
        self.parent.export.append(exportRecord)
        return 
        
class dataRetrieval(masterProcessingPanel):
    
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'
        
        ##Try to find existing files, if not, create blank one
        #files=['selectedStarIDs','selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        #for file in files:
        #    try:
        #        setattr(self.parent,file, pd.read_pickle('bindata/'+file+'.saved'))
        #    except Exception:
        #        setattr(self.parent,file, pd.DataFrame())
        #
        #try:
        #    file_to_read = open('bindata/starSystemList.pickle', 'rb') #File containing example object
        #    self.parent.starSystemList = pickle.load(file_to_read) # Load saved object
        #    file_to_read.close()
        #except Exception:
        #    self.parent.starSystemList=binaryStarSystems(len(self.parent.status))
        
        
        #Try to find existing files, if not, create blank one
        files=['selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        if len (sys.argv)>1:
            arg=sys.argv[1].strip()
        else:
            arg=''
        if arg == 'new':
            #Force exception if 'new' passed
            fileSuffix='new'
            #fileSuffix2='new'
        else:
            fileSuffix='saved'
            #fileSuffix2='pickle'
        
        global RELEASE
        global CATALOG
        for file in files:
            try:
                setattr(self.parent,file, pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.{fileSuffix}'))
                print(f'bindata/{RELEASE}/{CATALOG}/{file}.{fileSuffix} loaded')
            except Exception:
                setattr(self.parent,file, pd.DataFrame())

        try:
            file_to_read = open(f'bindata/{RELEASE}/{CATALOG}/starSystemList.pickle', 'rb') #File containing example object
            self.parent.starSystemList = pickle.load(file_to_read) # Load saved object
            file_to_read.close()
            print(f'bindata/{RELEASE}/{CATALOG}/starSystemList.pickle loaded')
        except Exception:
            print(f'Error in reading bindata/{RELEASE}/{CATALOG}/starSystemList.pickle')
            self.parent.starSystemList=binaryStarSystems(len(self.parent.status))
        #print(self.parent.star_rows)
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
        self.release.SetSelection(int(gl_cfg.getItem('release','RETRIEVAL', 0)))
        self.release.SetToolTip("Select release source")
        self.sizer_h.Add(self.release, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        #global RELEASE
        RELEASE = self.release.GetValue()
        
        # Catalogue prompt
        static_Catalogue = StaticText(self, id=wx.ID_ANY, label="Catalogue:")
        self.sizer_h.Add(static_Catalogue, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.catalogue = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], value='')
        self.catalogue.SetToolTip("Select Catalogue")
        self.catRefresh()
        self.catalogue.SetSelection(int(gl_cfg.getItem('catalog', 'RETRIEVAL', 0)))
        self.sizer_h.Add(self.catalogue, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        #global CATALOG
        CATALOG = self.catalogue.GetValue()
        
        # Load Catalogue
        
        # Loadtype
        
        self.loadType_combo = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['Healpix','Degrees (RA)','Degrees (Dec)', 'Parsecs'], value='')
        self.loadType_combo.SetSelection(int(gl_cfg.getItem('loadtype', 'RETRIEVAL', 0)))
        self.loadType_combo.SetToolTip("Select load mechanism")
        self.loadType_combo.Bind(wx.EVT_CHOICE, self.loadTypeRefresh)
        self.sizer_h.Add(self.loadType_combo, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        # Values (ie row 2)
        self.spin_loadType = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=0,initial=0)  
        self.sizer_h.Add(self.spin_loadType, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_loadType.SetToolTip(f"Upper Healpix to scan to - out of {HPS_SCALE}")
        self.loadTypeRefresh()
        self.spin_loadType.SetValue(int(gl_cfg.getItem('value', 'RETRIEVAL', 0)))
        
        # Mass Adjustment
        massAdjustStaticText = StaticText(self, id=wx.ID_ANY, label="Mass adjustment:")
        self.sizer_h.Add(massAdjustStaticText, 0, wx.ALL, 2)
        
        #Mass Adjustment.
        self.text_massAdjust = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mass-adjust','RETRIEVAL', '0.05'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.sizer_h.Add(self.text_massAdjust, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_massAdjust.setValidRoutine(self.text_massAdjust.Validate_Float)
        self.text_massAdjust.SetToolTip("Enter mass adjustment in solar masses for masses less than 0.7 Mo. [Expection, about 0.05]")
        
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
        
        ## Create 'deactivate indices' check box to speed up data inserts.
        #deactivateIndicesStaticText = StaticText(self, id=wx.ID_ANY, label="Deactivate indices?")
        #self.sizer_h.Add(deactivateIndicesStaticText, 0, wx.ALL, 2)
        #self.deactivateIndicesCheckBox = CheckBox(self)
        #self.deactivateIndicesCheckBox.SetToolTip("Deactivate indices to speed up DB inserts.  Speeds up large changes.  ")
        #self.deactivateIndicesCheckBox.SetValue(gl_cfg.getBoolean('deactivateindices', 'RETRIEVAL'))
        #self.sizer_h.Add(self.deactivateIndicesCheckBox, 0, wx.ALL, 2)
                
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
        
        self.dbload = Button(self, wx.ID_ANY, u"DB Load")
        self.dbload.SetToolTip("Import selected release/catalogue from database with or without null radial velocities or ungrouped star clusters.")
        self.dbload.Bind(wx.EVT_LEFT_DOWN, self.read_db)
        self.sizer_v2.Add(self.dbload, 0,wx.ALIGN_LEFT|wx.ALL , 5)
        
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
        #
        ##Deselect grouped stars (ie stars in more than 1 binary)
        #
        #self.ungroup = Button(self, id=wx.ID_ANY, label="&Ungroup", pos=wx.DefaultPosition,size=wx.DefaultSize)
        #self.ungroup.Bind(wx.EVT_BUTTON, self.deselectDuplicates)
        #self.ungroup.SetToolTip("Deselect binaries with stars that appear in more than one pair.  Ie deselect both pairs or entire cluster.")
        #self.sizer_v2.Add(self.ungroup, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
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
        
        self.parent.StatusBarProcessing ("Write complete")
            
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
                if str(row.NOT_GROUPED) == 'True':
                    notGrouped='True'
                else:
                    notGrouped='False'
            except Exception:
                notGrouped = 'Not Avail.'
            try:
                if str(row.HAS_RADIAL_VELOCITY) == 'True':
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
        files=['selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        for file in files:
            try:
                x = getattr(self.parent,file)
                x=pd.DataFrame(x)
                x.to_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
            except Exception:
                print('Error directory failed to save:')
                print (f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
                
        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            self.parent.StatusBarProcessing("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error: {sys.exc_info()}")
            exit(1)
        
        self.parent.StatusBarProcessing("\nPandas file save done!\n")
             
        
    def catalogRestore(self, event=0):
        
        self.listctrl.DeleteAllItems()
        global CATALOG, RELEASE
        
        CATALOG=self.catalogue.GetValue()
        RELEASE=self.release.GetValue()
        #Try to restore saved files, if not, error
        files=['selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        for file in files:
            try:
                setattr(self.parent,file, pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved'))
            except Exception:
                self.parent.StatusBarProcessing('Error directory failed to restore:')
                self.parent.StatusBarProcessing (f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
        
        try:
            cp(f'bindata/{RELEASE}/{CATALOG}/binClient.conf', 'binClient.conf')
        except IOError as e:
            self.parent.StatusBarProcessing("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error: {sys.exc_info()}")
            exit(1)
        
        self.parent.StatusBarProcessing("\nPandas file restore done!\n")
        self.restoreListCtrl()
    def loadTypeRefresh(self, event=0):

        if self.loadType_combo.GetSelection()==0:
            self.spin_loadType.SetMin(0)
            self.spin_loadType.SetMax(HPS_SCALE)
            self.spin_loadType.SetToolTip(f"Upper Healpix to load to - out of {HPS_SCALE}")
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

        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('loadType',self.loadType_combo.GetSelection(), 'RETRIEVAL') # save setting in config file
    def OnCancel(self, event=0):

        global CANCEL
        self.ungroup.Enable()
        self.dbload.Enable()
        CANCEL= True
        self.parent.StatusBarNormal('Completed OK')
        
    def catRefresh(self, event=0):
        
        global RELEASE
        RELEASE = self.release.GetValue()
        TBL_CATALOG = SQLLib.sqlSelect(iStro, "TBL_CATALOG")
        TBL_CATALOG.setWhereValueString("RELEASE_", RELEASE)
        TBL_CATALOG.setReturnCol("CATALOG")
        TBL_CATALOG.setSortCol("CATALOG",1) # -ve is desc, +ve is ascending
        records = TBL_CATALOG.selectRecordSet()
        self.catalogues=[]
        
        #for catalogue in records.itermap():
        #    #print(f'catalogue={catalogue}')
        #    self.catalogues.append(catalogue['CATALOG'])
        
        for row in records.fetchall():
            #print(f'catalogue={str(row[0])}')
            self.catalogues.append(str(row[0]))
        #
        self.catalogue.Clear()
        self.catalogue.SetItems(self.catalogues)
        self.catalogue.SetSelection(0)
        
        gl_cfg.setItem('release',self.release.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIASTAR') # save setting in config file
        
    def releaseRefresh(self, event=0):
        
        global RELEASE
        #RELEASE = self.release.GetValue()
        TBL_RELEASE = SQLLib.sqlSelect(iStro, "TBL_RELEASE")
        #TBL_RELEASE.setWhereValueString("RELEASE_", RELEASE)
        TBL_RELEASE.setReturnCol("RELEASE_")
        TBL_RELEASE.setSortCol("RELEASE_",1) # -ve is desc, +ve is ascending
        records = TBL_RELEASE.selectRecordSet()
        self.releases=[]
        
        #for release in records.itermap():
        #    self.releases.append(release['RELEASE_'])
            
        for row in records.fetchall():
            self.releases.append(str(row[0]))
        #
        self.release.Clear()
        self.release.SetItems(self.releases)
        #
        #gl_cfg.getItem('release', 'RETRIEVAL') # Get setting in config file
        self.release.SetSelection(int(gl_cfg.getItem('release', 'RETRIEVAL', 0))) # Get setting from config file
        return self.releases
        
    def read_db(self, event):

        global CANCEL
        CANCEL = False
        self.dbload.Disable()

        self.parent.StatusBarProcessing('Loading from DB into memory')
        
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('catalog',self.catalogue.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('loadType',self.loadType_combo.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('value',self.spin_loadType.GetValue(), 'RETRIEVAL') # save setting in config file
        #gl_cfg.setItem('value_max',self.spin_loadType.GetValue(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'RETRIEVAL') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIABINARY') # save setting in config file
        gl_cfg.setItem('release',self.release.GetSelection(), 'GAIASTAR') # save setting in config file
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        gl_cfg.setItem('ungrouped',self.unGroupedCheckBox.GetValue(), 'RETRIEVAL') # save notebook tab setting in config file
        gl_cfg.setItem('rvnull',self.rvnullCheckBox.GetValue(), 'RETRIEVAL') # save notebook tab setting in config file       

        gl_cfg.setItem('mass-adjust',self.text_massAdjust.GetValue(), 'RETRIEVAL')
        #global xdata2
        #global ydata2_1D
        #global ydata2
        #global xdata2Log
        #global ydata2Log

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
        #if hasattr(self.parent,"selectedStarIDs"):
        #    self.parent.selectedStarIDs=[] 
        #else:
        #    setattr(self.parent,"selectedStarIDs", []  )
            
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
        healpix=int(2**35*4**(12-2)*i*192/HPS_SCALE)  # From Gaia website
        
        commentHP='--'
        commentRA='--'
        commentDec='--'
        commentPx='--'
        commentRVnotGroup='--'
        commentGroupedandUngroupedwithRV='--'
        commentRVandRVnullUngrouped='--'
        
        if self.loadType_combo.GetSelection()==0:
            healpix=int(2**35*4**(12-2)*i*192/HPS_SCALE)  # From Gaia website
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
                        o1.PARALLAX, o1.parallax_error, o1.phot_g_mean_mag, o1.PHOT_RP_MEAN_FLUX_OVER_ERROR, o1.PHOT_G_MEAN_FLUX_OVER_ERROR, o1.PHOT_BP_MEAN_FLUX_OVER_ERROR, o1.BP_RP, o1.RADIAL_VELOCITY,
                        o1.RADIAL_VELOCITY_ERROR,
                        o1.PMRA, o1.PMRA_ERROR, o1.PMDEC, o1.PMDEC_ERROR, o1.RELEASE_, o1.RUWE,
                        1000/o1.PARALLAX as DIST,
                        o1.MASS_FLAME,
                        o1.MASS_FLAME_UPPER,
                        o1.MASS_FLAME_LOWER,
                        o1.AGE_FLAME,
                        o1.AGE_FLAME_UPPER,
                        o1.AGE_FLAME_LOWER,
                        o1.CLASSPROB_DSC_SPECMOD_BINARYSTAR,
                        
        o2.SOURCE_ID, o2.RA_, o2.RA_ERROR, o2.DEC_, o2.DEC_ERROR,
                        o2.PARALLAX, o2.parallax_error, o2.phot_g_mean_mag, o2.PHOT_RP_MEAN_FLUX_OVER_ERROR, o2.PHOT_G_MEAN_FLUX_OVER_ERROR, o2.PHOT_BP_MEAN_FLUX_OVER_ERROR, o2.BP_RP, o2.RADIAL_VELOCITY,
                        o2.RADIAL_VELOCITY_ERROR, 
                        o2.PMRA, o2.PMRA_ERROR, o2.PMDEC, o2.PMDEC_ERROR, o2.RELEASE_, o2.RUWE,
                        1000/o2.PARALLAX as DIST,
                        o2.MASS_FLAME,
                        o2.MASS_FLAME_UPPER,
                        o2.MASS_FLAME_LOWER,
                        o2.AGE_FLAME,
                        o2.AGE_FLAME_UPPER,
                        o2.AGE_FLAME_LOWER,
                        o2.CLASSPROB_DSC_SPECMOD_BINARYSTAR
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
        
        --    {commentRVnotGroup} and  o1.RADIAL_VELOCITY > 0
        --    {commentRVnotGroup} and  o2.RADIAL_VELOCITY > 0  
        --    {commentGroupedandUngroupedwithRV} and  o1.RADIAL_VELOCITY > 0
        --    {commentGroupedandUngroupedwithRV} and  o2.RADIAL_VELOCITY > 0   
        --        and o1.SOURCE_ID is not null
        --        and o2.SOURCE_ID is not null
        --    ORDER BY SOURCE_ID_PRIMARY asc
        ;
        
        """
        
        print (querySQL)
        recordsAll = pd.read_sql(querySQL, iStro)
        i=0
        lenArray=len(recordsAll)
        self.parent.StatusBarProcessing(f'lenArray={lenArray:,}')
        self.parent.starSystemList=binaryStarSystems(lenArray, gl_cfg.getItem('mass-adjust','RETRIEVAL', '0.05'))
        
        #Mass_Correction=float()  #  0.05 correction to allow for low mass dispersion
        records=recordsAll.iloc[:,range(9)]
        records.drop(columns=['RELEASE_', 'CATALOG', 'SOURCE_ID_PRIMARY', 'SOURCE_ID_SECONDARY'])
        X=recordsAll.iloc[:,range(9,37)]
        Y=recordsAll.iloc[:,range(37,65)]
        records=records.convert_dtypes()
        del recordsAll
        X=X.convert_dtypes()
        Y=Y.convert_dtypes()
        for index, row  in records.iterrows():
            i=i+1
            if not index % 100:
                label=float(100 * index /lenArray)
                self.dbload.SetLabel(f'{label:,.1f}%')
                self.static_Total.SetLabel(f'{index:,} of {lenArray:,}')
                if index > 0 and not math.log10(index) % 1:
                    self.Layout()
                if CANCEL:
                    CANCEL = False
                    self.dbload.Enable()
                    return
                wx.Yield()
            if str(row.STATUS) == '<NA>' or str(row.STATUS) == 'None':
                status=''
            else:
                status=str(row.STATUS)
            #Only display first 1000
            
            try:
                if row.NOT_GROUPED == True:
                    notGrouped='True'
                    notGroupedBool=True
                    notgroup=1
                else:
                    notGrouped='False'
                    notGroupedBool=False
                    notgroup=0
            except Exception:
                notGrouped = 'Not Avail.'
                notGroupedBool=False
                notgroup=0
            try:
                if row.HAS_RADIAL_VELOCITY == True:
                    hasRadialVelocity='True'
                    hasRadialVelocityBool='True'
                    radialvelocity=1
                else:
                    hasRadialVelocity='False'
                    hasRadialVelocityBool=False
                    radialvelocity=0
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
            if index<1000:
                #try:
                #    if str(row.STATUS) == '<NA>':
                #        status=''
                #    else:
                #        status=str(row.STATUS)
                #except Exception:
                #    status = ''
                self.listctrl.Append([X.source_id[i-1],Y.source_id[i-1], index, separation, notGrouped, hasRadialVelocity,status, RELEASE, CATALOG, healpix])
            
            ##  The 'notgroup' flag indicates that the stars in the system don't occur in other binaries too.
            #notgroup=1
            #
            ##  The 'radialvelocity' flag indicates that the stars in the system each have radial velocities.
            #radialvelocity=1
            #
            ##  The 'include' flag indicates that the binary will be part of the final plot.
            if hasRadialVelocity=='True' and notGrouped=='True':
                include=1
            else:
                include=0
            #
            #try:
            #    if row.STATUS=='dupl':
            #        notgroup=0
            #        include=0
            #except Exception:
            #    print(f'Except: Duplication')
            #    pass
            #
            #try:
            #    if row.STATUS=='rv=0':
            #        radialvelocity=0
            #        include=0
            #except Exception:
            #    print(f'Except: rv=0')
            #    pass
                
            if len(self.parent.status)<=index:
                self.parent.status.append([include, notgroup,radialvelocity, index])
            else:
                self.parent.status[index-1]=[include, notgroup,radialvelocity, index-1]
                
            
            R=0
            V=0
            Verr=0
            if pd.isna(X.phot_g_mean_mag.iloc[index]):
                X.phot_g_mean_mag.iloc[index]=0
            if pd.isna(Y.phot_g_mean_mag.iloc[index]):
                Y.phot_g_mean_mag.iloc[index]=0
                
            try:
            #Check for primary/companion
                if X.phot_g_mean_mag.iloc[index]<Y.phot_g_mean_mag.iloc[index]:
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
                self.parent.StatusBarProcessing(f'Except: G_MEAN_MAG error')
                include=0
            primaryPointer=self.parent.starSystemList.binaryList[str(index+1)].primary
            star2Pointer=self.parent.starSystemList.binaryList[str(index+1)].star2
            #self.parent.selectedStarIDs.append(primaryPointer.source_id)
            #self.parent.selectedStarIDs.append(star2Pointer.source_id)
            self.parent.selectedStarBinaryMappings[i]={
                'SOURCE_ID_PRIMARY':int(primaryPointer.source_id),
                'SOURCE_ID_SECONDARY':int(star2Pointer.source_id),
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
            #if not isinstance(self.parent.selectedStarIDs, list):
            #    print("self.parent.selectedStarIDs is not list")
            #    exit()
            #if not isinstance(self.parent.selectedStarIDs, list):
            #    print("self.parent.selectedStarIDs is not list")
            #    exit()
            if not isinstance(self.parent.X, dict):
                print("self.parent.X is not list")
                exit()
            if not isinstance(self.parent.Y, dict):
                print("self.parent.Y is not list")
                exit()
            if not isinstance(self.parent.binaryDetail, list):
                print("self.parent.binaryDetail is not list")
                exit()
            try:
                XRUWE=float(self.parent.starSystemList.binaryList[str(index+1)].primary.ruwe)
            except:
                XRUWE=0
            try:
                YRUWE=float(self.parent.starSystemList.binaryList[str(index+1)].star2.ruwe)
            except:
                YRUWE=0
            try:
                XBminusR=float(self.parent.starSystemList.binaryList[str(index+1)].primary.bp_rp)
            except:
                XBminusR=0
            try:
                YBminusR=float(self.parent.starSystemList.binaryList[str(index+1)].star2.bp_rp)
            except:
                YBminusR=0
            try:
                XPHOT_G_MEAN_MAG=float(self.parent.starSystemList.binaryList[str(index+1)].primary.phot_g_mean_mag)
            except:
                XPHOT_G_MEAN_MAG=0
            try:
                YPHOT_G_MEAN_MAG=float(self.parent.starSystemList.binaryList[str(index+1)].star2.phot_g_mean_mag)
            except:
                YPHOT_G_MEAN_MAG=0
            try:
                Xmass_flame=float(self.parent.starSystemList.binaryList[str(index+1)].primary.mass_flame)
            except:
                Xmass_flame=0
            try:
                Ymass_flame=float(self.parent.starSystemList.binaryList[str(index+1)].star2.mass_flame)
            except:
                Ymass_flame=0
        
            try:
                Xmass_calc=float(self.parent.starSystemList.binaryList[str(index+1)].primary.mass_calc)
            except:
                Xmass_calc=0
            try:
                Ymass_calc=float(self.parent.starSystemList.binaryList[str(index+1)].star2.mass_calc)
            except:
                Ymass_calc=0
        
            try:
                Xmass_flame_upper=float(self.parent.starSystemList.binaryList[str(index+1)].primary.mass_flame_upper)
            except:
                Xmass_flame_upper=0
            try:
                Ymass_flame_upper=float(self.parent.starSystemList.binaryList[str(index+1)].star2.mass_flame_upper)
            except:
                Ymass_flame_upper=0
        
            try:
                Xmass_flame_lower=float(self.parent.starSystemList.binaryList[str(index+1)].primary.mass_flame_lower)
            except:
                Xmass_flame_lower=0
            try:
                Ymass_flame_lower=float(self.parent.starSystemList.binaryList[str(index+1)].star2.mass_flame_lower)
            except:
                Ymass_flame_lower=0
        
            try:
                Xage_flame=float(self.parent.starSystemList.binaryList[str(index+1)].primary.age_flame)
            except:
                Xage_flame=0
            try:
                Yage_flame=float(self.parent.starSystemList.binaryList[str(index+1)].star2.age_flame)
            except:
                Yage_flame=0
        
            try:
                Xage_flame_upper=float(self.parent.starSystemList.binaryList[str(index+1)].primary.age_flame_upper)
            except:
                Xage_flame_upper=0
            try:
                Yage_flame_upper=float(self.parent.starSystemList.binaryList[str(index+1)].star2.age_flame_upper)
            except:
                Yage_flame_upper=0
        
            try:
                Xage_flame_lower=float(self.parent.starSystemList.binaryList[str(index+1)].primary.age_flame_lower)
            except:
                Xage_flame_lower=0
            try:
                Yage_flame_lower=float(self.parent.starSystemList.binaryList[str(index+1)].star2.age_flame_lower)
            except:
                Yage_flame_lower=0
        
            try:
                Xclassprob_dsc_specmod_binarystar=float(self.parent.starSystemList.binaryList[str(index+1)].primary.classprob_dsc_specmod_binarystar)
            except:
                Xclassprob_dsc_specmod_binarystar=0
            try:
                Yclassprob_dsc_specmod_binarystar=float(self.parent.starSystemList.binaryList[str(index+1)].star2.classprob_dsc_specmod_binarystar)
            except:
                Yclassprob_dsc_specmod_binarystar=0
        
            try:
                self.parent.X[index] = {
                    'source_id':int(primaryPointer.source_id),
                    'ra':float(self.parent.starSystemList.binaryList[str(index+1)].primary.RA_),
                    'dec':float(self.parent.starSystemList.binaryList[str(index+1)].primary.DEC_),
                    'BminusR':XBminusR,
                    'mag':float(XPHOT_G_MEAN_MAG-5*math.log10(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST/10)),
                    'PMRA':float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmra),
                    'PMRA_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmra_error),
                    'PMDEC':float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmdec),
                    'PMDEC_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmdec_error),
                    'PARALLAX':float(self.parent.starSystemList.binaryList[str(index+1)].primary.parallax),
                    'parallax_error':float(self.parent.starSystemList.binaryList[str(index+1)].primary.parallax_error),
                    'DIST':float(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST),
                    'RUWE':XRUWE,
                    'mass_calc':Xmass_calc,
                    'mass_flame':Xmass_flame,
                    'mass_flame_upper':Xmass_flame_upper,
                    'mass_flame_lower':Xmass_flame_lower,
                    'age_flame':Xage_flame,
                    'age_flame_upper':Xage_flame_upper,
                    'age_flame_lower':Xage_flame_lower,
                    'classprob_dsc_specmod_binarystar':Xclassprob_dsc_specmod_binarystar
                    }
            except Exception:
                    self.parent.StatusBarProcessing (f'Skipped record {index}')
                    #row=row.transpose()
                    print('Error 1', row)
                    print(index)
                    print(X[:index+2])
                    print(Y[:index+2])
                    print(records[:int(index+2)])
                    print('ra'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.RA_)))
                    print('dec'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.DEC_)))
                    print('BminusR'+str(XBminusR))
                    print('mag'+str(float(XPHOT_G_MEAN_MAG-5*math.log10(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST/10))))
                    print('PMRA'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmra)))
                    print('PMRA_ERROR'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmra_error)))
                    print('PMDEC'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmdec)))
                    print('PMDEC_ERROR'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.pmdec_error)))
                    print('PARALLAX'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.parallax)))
                    print('parallax_error'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.parallax_error)))
                    print('DIST'+str(float(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST)))
                    print('RUWE'+str(YRUWE))
                    self.dbload.SetBackgroundColour(Colour(150,20,20))
                    self.dbload.Enable()
                    return
            try:
                self.parent.Y[index] ={
                    'source_id':int(star2Pointer.source_id),
                    'ra':float(self.parent.starSystemList.binaryList[str(index+1)].star2.RA_),
                    'dec':float(self.parent.starSystemList.binaryList[str(index+1)].star2.DEC_),
                    'BminusR':YBminusR,
                    'mag':float(YPHOT_G_MEAN_MAG-5*math.log10(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST/10)),
                    'PMRA':float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmra),
                    'PMRA_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmra_error),
                    'PMDEC':float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmdec),
                    'PMDEC_ERROR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmdec_error),
                    'PARALLAX':float(self.parent.starSystemList.binaryList[str(index+1)].star2.parallax),
                    'parallax_error':float(self.parent.starSystemList.binaryList[str(index+1)].star2.parallax_error),
                    'DIST':float(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST),
                    'RUWE':YRUWE,
                    'mass_flame':Ymass_flame,
                    'mass_calc':Ymass_calc,
                    'mass_flame_upper':Ymass_flame_upper,
                    'mass_flame_lower':Ymass_flame_lower,
                    'age_flame':Yage_flame,
                    'age_flame_upper':Yage_flame_upper,
                    'age_flame_lower':Yage_flame_lower,
                    'classprob_dsc_specmod_binarystar':Yclassprob_dsc_specmod_binarystar
                    }
            except Exception:
                    print (f'Skipped record {index}')
                    #row=row.transpose()
                    print('Error 2', row)
                    print(index)
                    print(X[:index+2])
                    print(Y[:index+2])
                    print(records[:int(index+2)])
                    print('ra'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.RA_)))
                    print('dec'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.DEC_)))
                    print('BminusR'+str(YBminusR))
                    print('mag'+str(YPHOT_G_MEAN_MAG-5*math.log10(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST/10)))
                    print('PMRA'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmra)))
                    print('PMRA_ERROR'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmra_error)))
                    print('PMDEC'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmdec)))
                    print('PMDEC_ERROR'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.pmdec_error)))
                    print('PARALLAX'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.parallax)))
                    print('parallax_error'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.parallax_error)))
                    print('DIST'+str(float(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST)))
                    print('RUWE'+str(YRUWE))
                    self.dbload.SetBackgroundColour(Colour(150,20,20))
                    self.dbload.Enable()
                    return
            self.parent.binaryDetail.append([abs(R), abs(V[0]), abs(Verr[0]), abs(V[1]), abs(Verr[1]), abs(M)])
            
            if include:
                #primaryPointer=self.parent.starSystemList.binaryList[str(index+1)].primary
                #star2Pointer=self.parent.starSystemList.binaryList[str(index+1)].star2
                exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.source_id),
                    'ra1':float(primaryPointer.RA_),
                    'dec1':float(primaryPointer.DEC_),
                    'mag1':primaryPointer.phot_g_mean_mag,
                    'MAG1':self.parent.X[index]['mag'],
                    'PARALLAX1':float(primaryPointer.parallax),
                    'PARALLAX_ERROR1':float(primaryPointer.parallax_error),
                    'DIST1':float(primaryPointer.DIST),
                    'RUWE1':XRUWE,
                    'PMRA1':float(primaryPointer.pmra),
                    'PMRA_ERROR1':float(primaryPointer.pmra_error),
                    'PMDEC1':float(primaryPointer.pmdec),
                    'PMDEC_ERROR1':float(primaryPointer.pmdec_error),
                    'BminusR1':float(XBminusR),
                    'mass_calc1':Xmass_calc,
                    'mass_flame1':Xmass_flame,
                    'mass_flame_upper1':Xmass_flame_upper,
                    'mass_flame_lower1':Xmass_flame_lower,
                    'age_flame1':Xage_flame,
                    'age_flame_upper1':Xage_flame_upper,
                    'age_flame_lower1':Xage_flame_lower,
                    'classprob_dsc_specmod_binarystar1':Xclassprob_dsc_specmod_binarystar,
                    'SOURCE_ID_SECONDARY':str(star2Pointer.source_id),
                    'ra2':float(star2Pointer.RA_),
                    'dec2':float(star2Pointer.DEC_),
                    'mag2':star2Pointer.phot_g_mean_mag,
                    'MAG2':self.parent.Y[index]['mag'],
                    'PARALLAX2':float(star2Pointer.parallax),
                    'parallax_error2':float(star2Pointer.parallax_error),
                    'DIST2':float(star2Pointer.DIST),
                    'RUWE2':YRUWE,
                    'PMRA2':float(star2Pointer.pmra),
                    'PMRA_ERROR2':float(star2Pointer.pmra_error),
                    'PMDEC2':float(star2Pointer.pmdec),
                    'PMDEC_ERROR2':float(star2Pointer.pmdec_error),
                    'BminusR2':float(YBminusR),
                    'mass_calc2':Ymass_calc,
                    'mass_flame2':Ymass_flame,
                    'mass_flame_upper2':Ymass_flame_upper,
                    'mass_flame_lower2':Ymass_flame_lower,
                    'age_flame2':Yage_flame,
                    'age_flame_upper2':Yage_flame_upper,
                    'age_flame_lower2':Yage_flame_lower,
                    'classprob_dsc_specmod_binarystar2':Yclassprob_dsc_specmod_binarystar,
                    'vRA':abs(V[0]),
                    'vRAerr':abs(Verr[0]),
                    'vDEC':abs(V[1]),
                    'vDECerr':abs(Verr[1]),
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
        #        
        #print(f'X = {self.parent.X}')

        self.parent.export=pd.DataFrame(self.parent.export)
        self.dbload.SetLabel('Import')
        
        ROWCOUNTMATRIX['ADQL']=len(self.parent.selectedStarBinaryMappings)
        self.static_Total.SetLabel(f'{int(len(self.parent.star_rows)/2):,}')
        self.parent.StatusBarProcessing('End')
        
        #self.parent.selectedStarIDs=pd.DataFrame(self.parent.selectedStarIDs, columns=['source_id'])
        self.parent.selectedStarBinaryMappings=pd.DataFrame.from_dict(self.parent.selectedStarBinaryMappings, orient='index')#, columns=['i', 'SOURCE_ID_PRIMARY', 'SOURCE_ID_SECONDARY'
        self.parent.status=pd.DataFrame(self.parent.status, columns=['include', 'notgroup', 'radialvelocity', 'pairnumber'])
        self.parent.status['dataLoadOut']=self.parent.status['include']
        self.parent.status['populateOut']=self.parent.status['include']
        self.parent.status['hrOut']=self.parent.status['include']
        self.parent.status['kineticOut']=self.parent.status['include']
        self.parent.status['massVmassOut']=self.parent.status['include']
        self.parent.status['tfOut']=self.parent.status['include']
        self.parent.binaryDetail=pd.DataFrame(self.parent.binaryDetail, columns=['r','vRA','vRAerr','vDEC','vDECerr', 'M'])
        self.parent.X=pd.DataFrame.from_dict(self.parent.X, orient='index') #, columns=['ra','dec','BminusR', 'mag']pd.DataFrame.from_dict(data, orient='index')
        self.parent.Y=pd.DataFrame.from_dict(self.parent.Y, orient='index') #, columns=['ra','dec','BminusR', 'mag'])
        self.parent.star_rows=pd.DataFrame.from_dict(self.parent.starSystemList.getStar_rows(), orient='index') #, columns=column_names)
        
        print(self.parent.X)
        
        # Save pandas files as pickle files for next time.
        files=['selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        
        #Check directory exists and create if not.
        if not os.path.isdir(f'bindata'):
            os.mkdir (f'bindata')
        for file in files:
            try:
                x = getattr(self.parent,file)
                x=pd.DataFrame(x)
                x.to_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
            except Exception:
                print('Error directory failed to save:')
                print (f'bindata/{RELEASE}/{CATALOG}/{file}.saved')
        
        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)

        self.parent.StatusBarProcessing("\nPandas file save done!\n")
        
        # Open file handle
        file_to_store = open(f'bindata/{RELEASE}/{CATALOG}/starSystemList.pickle', 'wb')
        #Save object to file
        pickle.dump(self.parent.starSystemList, file_to_store)  
        # Close file handle
        file_to_store.close()
 
        self.parent.printArrays()
        self.dbload.Enable()
        
        self.parent.StatusBarNormal('Completed OK')
        
    def resetStatus(self, event):
        
        self.reset.Disable()
        
        self.parent.StatusBarProcessing('Resetting')
        
        global RELEASE, CATALOG
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        i=int(self.spin_loadType.GetValue())
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "")
        #TBL_BINARIES.setAttributeBool("NOT_GROUPED", True)
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i*192/HPS_SCALE
            if i<HPS_SCALE:
                TBL_BINARIES.setWhereValueLTInt("source_id", healpix)
        print(TBL_BINARIES.updateRecord())
        
        self.reset.Enable()
    
        self.parent.StatusBarNormal('Completed OK')
        
    def deselectRVnull(self, event):
        
        global CANCEL
        CANCEL = False

        self.parent.StatusBarProcessing('Deselecting binaries with no RV')
        
        self.rvnull.Disable()
        
        wx.Yield()
        commentHP='--'
        commentRA='--'
        commentDec='--'
        commentPx='--'
        
        i=int(self.spin_loadType.GetValue())
        if self.loadType_combo.GetSelection()==0:
            healpix=2**35*4**(12-2)*i
            commentHP=''
        if self.loadType_combo.GetSelection()==1:
            commentRA=''
        if self.loadType_combo.GetSelection()==2:
            commentDec=''
        if self.loadType_combo.GetSelection()==3:
            commentPx=''

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
                    where (o1.RADIAL_VELOCITY != 0
                    and o2.RADIAL_VELOCITY != 0) and b.CATALOG = '{CATALOG}' and b.RELEASE_ = '{RELEASE}'
            
                    {commentHP} and b.SOURCE_ID_PRIMARY < {healpix}
                    {commentRA} and o1.RA_ < {i}  and o2.RA_ < {i}
                    {commentDec} and o1.DEC_ < {i}  and o2.DEC_ < {i} and o1.DEC_ > {-i}  and o2.DEC_ > {-i}
                    {commentPx} and o1.PARALLAX > {i} and o2.PARALLAX > {i}
                """
 #and b.HAS_RADIAL_VELOCITY = False
        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        Array=[]
        self.parent.StatusBarProcessing(f'length = {lenArray:,}')
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            #self.parent.radialvelocity[index]=0
            Array.append( row.SOURCE_ID_PRIMARY)
            if not index % 200:
                #print (index)
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "")
                TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
                TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "")
                TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
                TBL_BINARIES.setWhereInList("SOURCE_ID_SECONDARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                Array=[] 
                label=float(100 * index /lenArray)
                self.rvnull.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    self.rvnull.Enable()
                    return
                wx.Yield()
        
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
        TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("release_", RELEASE)
        TBL_BINARIES.updateRecord()
        TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
        TBL_BINARIES.setAttributeBool("HAS_RADIAL_VELOCITY", True)
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
        self.parent.StatusBarProcessing(records)

        self.parent.StatusBarNormal('Completed OK')
        
    #def deselectRVnull_old(self, event):
    #    
    #    self.rvnull.Disable()
    #    
    #    commentHP='--'
    #    commentRA='--'
    #    commentDec='--'
    #    commentPx='--'
    #    
    #    i=int(self.spin_loadType.GetValue())
    #    if self.loadType_combo.GetSelection()==0:
    #        healpix=2**35*4**(12-2)*i*192/HPS_SCALE  # From Gaia website
    #        commentHP=''
    #    if self.loadType_combo.GetSelection()==1:
    #        commentRA=''
    #    if self.loadType_combo.GetSelection()==2:
    #        commentDec=''
    #    if self.loadType_combo.GetSelection()==3:
    #        commentPx=''
    #
    #    
    #    global RELEASE, CATALOG
    #    RELEASE=self.release.GetValue()
    #    CATALOG=self.catalogue.GetValue()
    #    i=int(self.spin_loadType.GetValue())
    #    healpix=2**35*4**(12-2)*i*192/HPS_SCALE
    #    
    #    sql = f"""
    #    UPDATE b
    #    set b.STATUS = 'rv=0', b.HAS_RADIAL_VELOCITY = 0
    #
    #    FROM TBL_BINARIES b
    #        inner join TBL_OBJECTS o1
    #            on b.SOURCE_ID_PRIMARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_
    #        inner join TBL_OBJECTS o2
    #            on b.SOURCE_ID_SECONDARY=o2.SOURCE_ID and b.RELEASE_ = o2.RELEASE_
    #    where (o1.RADIAL_VELOCITY is Null
    #    or o2.RADIAL_VELOCITY is Null)
    #    and b.CATALOG = '{CATALOG}'
    #    and b.RELEASE_ = '{RELEASE}'
    #    and b.HAS_RADIAL_VELOCITY = 1
    #
    #    {commentHP} and b.SOURCE_ID_PRIMARY < {healpix}
    #    {commentRA} and o1.RA_ < {i}  and o2.RA_ < {i}
    #    {commentDec} and o1.DEC_ < {i}  and o2.DEC_ < {i} and o1.DEC_ > {-i}  and o2.DEC_ > {-i}
    #    {commentPx} and o1.PARALLAX > {i} and o2.PARALLAX > {i}
    #                
    #    and o2.SOURCE_ID is not null
    #    """
    #    print(sql)
    #    TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
    #    TBL_BINARIES.setAttributeString("STATUS", "rv=0")
    #    TBL_BINARIES.updateRecord(sql)
    #    
    #    label=int(100)
    #    self.rvnull.SetLabel(f'{label:,.1f}%')
    #    
    #    TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES")
    #    TBL_BINARIES.setWhereValueString("RELEASE_", RELEASE)
    #    TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
    #    TBL_BINARIES.setWhereValueBool("HAS_RADIAL_VELOCITY", False)
    #    TBL_BINARIES.setReturnCol("count(*) as CNT")
    #    records = TBL_BINARIES.selectRecordSet()
    #    for row in records:
    #        #print(f'{row[0]:,}')
    #        ROWCOUNTMATRIX['RV0']=row[0]
    #        self.static_RVnull.SetLabel(f'{row[0]:,}')
    #    self.rvnull.Enable()
    #    self.Layout()
    #    
    def OnDeleteSelection(self, event):
        #Move Ba to another catalogue
        self.deleteSelection.Disable()
        
        self.parent.StatusBarProcessing('Deleting catalogue')
        
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
        
        self.parent.StatusBarNormal('Completed OK')
        
    def moveBineries(self, event):
        #Move Ba to another catalogue
        self.move.Disable()
        
        self.parent.StatusBarProcessing('Moving binary catalogue commenced')
        
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
        
        self.parent.StatusBarNormal('Completed OK')
        
class dataFilter(masterProcessingPanel):
    
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=13, hgap=0, rows=3, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings (ie row 1)
                
        # Signal to noise ratio for Px
        self.static_parallax = StaticText(self, label='Px S/N') 
        fgsizer.Add(self.static_parallax, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for Red Magnitude
        self.static_red_mag = StaticText(self, label='Rp S/N') 
        fgsizer.Add(self.static_red_mag, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for Green Magnitude
        self.static_green_mag = StaticText(self, label='G S/N') 
        fgsizer.Add(self.static_green_mag, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for Blue Magnitude
        self.static_blue_mag = StaticText(self, label='Bp S/N') 
        fgsizer.Add(self.static_blue_mag, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Signal to noise ratio for PMRA and PMDEC
        self.pmsnratio = StaticText(self, label='pm S/N') 
        fgsizer.Add(self.pmsnratio, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Difference in radial veocities between the two stars.
        self.static_diff_radial_velocity = StaticText(self, label='diff in rad. vel.') 
        fgsizer.Add(self.static_diff_radial_velocity, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_ruwe = StaticText(self, label='RUWE') 
        fgsizer.Add(self.static_ruwe, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_text_binProbability = StaticText(self, label='Bin Prob') 
        fgsizer.Add(self.static_text_binProbability, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_InDist = StaticText(self, label='Inner dist') 
        fgsizer.Add(self.static_InDist, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_OutDist = StaticText(self, label='Outer Limit') 
        fgsizer.Add(self.static_OutDist, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_minSepn = StaticText(self, label='Min Sepn') 
        fgsizer.Add(self.static_minSepn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_ageDiffMax = StaticText(self, label='Max Age Diff') 
        fgsizer.Add(self.static_ageDiffMax, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Activate age comparison (both stars must have and 'age')
        forceAgeCompStaticText = StaticText(self, id=wx.ID_ANY, label="Age Comparison?")
        fgsizer.Add(forceAgeCompStaticText, 0, wx.ALL, 2)
        
        # Values (ie row 2)
        # Signal to noise ratio for Px
        self.spin_parallax_SN = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pxsn_gt','FILTER', 0)))
        fgsizer.Add(self.spin_parallax_SN, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_parallax_SN.SetToolTip("Signal to noise ratio for Parallax (ie Px/error) in either star.")
        
        # Signal to noise ratio for Red Magnitude
        self.spin_red_mag_SN = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('rpsn_gt','FILTER', 0)))
        fgsizer.Add(self.spin_red_mag_SN, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_red_mag_SN.SetToolTip("Signal to noise ratio for Red Magnitude (ie Rp/error) in either star.")
        
        # Signal to noise ratio for Green Magnitude
        self.spin_green_mag_SN = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('g_sn_gt','FILTER', 0)))
        fgsizer.Add(self.spin_green_mag_SN, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_green_mag_SN.SetToolTip("Signal to noise ratio for Green Magnitude (ie G/error) in either star.")
        
        # Signal to noise ratio for Blue Magnitude
        self.spin_blue_mag_SN = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('bpsn_gt','FILTER', 0)))
        fgsizer.Add(self.spin_blue_mag_SN, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_blue_mag_SN.SetToolTip("Signal to noise ratio for Blue Magnitude (ie Bp/error) in either star.")
        
        # Signal to noise ratio for PMRA and PMDEC
        self.spin_pmsnratio = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=1000,initial=int(gl_cfg.getItem('pmsn_gt','FILTER',0)))
        fgsizer.Add(self.spin_pmsnratio, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_pmsnratio.SetToolTip("Signal to noise ratio for PMRA and PMDEC (ie PM/error) in either star.")

        #Diffence in radial velocities between primary and companion stars.
        self.spin_diff_radial_velocity = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=99,initial=int(gl_cfg.getItem('rv_lt','FILTER',0)))
        fgsizer.Add(self.spin_diff_radial_velocity, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_diff_radial_velocity.SetToolTip("Difference in radial velocities between primary and companion stars.")
        
        #Max RUWE.
        self.text_ruwe = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('ruwe_lt','FILTER', 1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_ruwe, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_ruwe.setValidRoutine(self.text_ruwe.Validate_Float)
        self.text_ruwe.SetToolTip("Maximum RUWE in either star.  Enter decimal x for RUWE < x")
        
        #Binary probability.
        self.text_binProbability = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bin_probability_lt','FILTER', 0.1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_binProbability, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_binProbability.setValidRoutine(self.text_binProbability.Validate_Float)
        self.text_binProbability.SetToolTip("Maximum probability in either star.  Enter decimal x for probability < x")
        
        #self.combo_InOut = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['Inner','Outer'], value='')
        #self.combo_InOut.SetSelection(int(gl_cfg.getItem('io','FILTER',0)))
        #fgsizer.Add(self.combo_InOut, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.combo_InOut.SetToolTip("Stars inside or outside the distance cutoff")
        
        #Inner Distance cutoff.
        self.spin_distInnerCutoff = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=333,initial=int(gl_cfg.getItem('cutoff-inner','FILTER', 1))) 
        self.spin_distInnerCutoff.SetToolTip("Inner limit of distance for stars to be included.")
        fgsizer.Add(self.spin_distInnerCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        #Outer Distance cutoff.
        self.spin_distCutoff = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=333,initial=int(gl_cfg.getItem('cutoff-outer','FILTER',100))) 
        self.spin_distCutoff.SetToolTip("Outer limit of distance for stars to be included.")
        fgsizer.Add(self.spin_distCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        #Min Sepn cutoff.
        self.text_Min_Sepn = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('min-sepn','FILTER', '0'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_Min_Sepn, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_Min_Sepn.setValidRoutine(self.text_Min_Sepn.Validate_Float)
        self.text_Min_Sepn.SetToolTip("Minimum separation of binary pair.  Enter decimal parsecs")
        
        #Max Age diff cutoff.
        self.text_ageDiffMax = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('age-diff-max','FILTER', '15'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_ageDiffMax, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_ageDiffMax.setValidRoutine(self.text_ageDiffMax.Validate_Float)
        self.text_ageDiffMax.SetToolTip("Maximum difference binary ages.  Enter decimal age in giga-annum (Ga).  The default is 15 Ga to allow all pairs through.")
        
        # Activate age comparison (both stars must have an 'age')
        self.activateAgeCompCheckBox = CheckBox(self)
        self.activateAgeCompCheckBox.SetToolTip("Activate age comparison (both stars must have an 'age').")
        self.activateAgeCompCheckBox.SetValue(gl_cfg.getBoolean('activate-age-comp', 'FILTER'))
        fgsizer.Add(self.activateAgeCompCheckBox, 0, wx.ALL, 2)
        
        self.SetSizer(self.sizer_v)
                
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        #
        self.loadData = Button(self, wx.ID_ANY, u"Filter data")
        self.loadData.Bind(wx.EVT_LEFT_DOWN, self.applyFilter)
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
        self.listctrl.InsertColumn(1, u"pair #", width=60)
        self.listctrl.InsertColumn(2, u"ra", width=70)
        #self.listctrl.InsertColumn(3, u"ra_error", width=100)
        self.listctrl.InsertColumn(3, u"dec", width=70)
        #self.listctrl.InsertColumn(5, u"dec error", width=100)
        self.listctrl.InsertColumn(4, u"parallax", width=70)
        self.listctrl.InsertColumn(5, u"px err", width=70)
        self.listctrl.InsertColumn(6, u"pmra", width=70)
        self.listctrl.InsertColumn(7, u"pmra err", width=70)
        self.listctrl.InsertColumn(8, u"pmdec", width=70)
        self.listctrl.InsertColumn(9, u"pmdec err", width=70)
        self.listctrl.InsertColumn(10, u"RUWE", width=70)
        self.listctrl.InsertColumn(11, u"Rad. Vel", width=70)
        #self.listctrl.InsertColumn(12, u"Exclude", width=100)
        self.listctrl.InsertColumn(12, u"Release", width=70)
        self.listctrl.InsertColumn(13, u"RV?", width=50)
        self.listctrl.InsertColumn(14, u"UnGrp?", width=70)
        self.listctrl.InsertColumn(15, u"Incl?", width=50)
        self.listctrl.InsertColumn(16, u"g mag", width=70)
        self.listctrl.InsertColumn(17, u"mass", width=70)
        self.listctrl.InsertColumn(18, u"age", width=70)
        self.listctrl.InsertColumn(19, u"bin prob", width=60)
        self.listctrl.InsertColumn(20, u"Exclusion reason", width=200)

        self.sizer_v.Add(self.listctrl, 0, wx.TOP | wx.BOTTOM , 10)
        self.sizer_v.Add(hsizer1, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.sizer_v.Add(hsizer2, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        self.restoreListCtrl()
        
        self.Layout()

    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        self.loadData.Enable()
        self.parent.StatusBarNormal('Completed OK')
        
    def OnReset(self, event=0):
        self.parent.status=pd.DataFrame(self.parent.status)
        self.parent.status['include']=self.parent.status['dataLoadOut']
        self.parent.status['populateOut']=self.parent.status['dataLoadOut']
        self.parent.status['hrOut']=self.parent.status['dataLoadOut']
        self.parent.status['kineticOut']=self.parent.status['dataLoadOut']
        self.parent.status['massVmassOut']=self.parent.status['dataLoadOut']
        self.parent.status['tfOut']=self.parent.status['dataLoadOut']
        
    def applyFilter(self, event):
        
        global CANCEL
        CANCEL = False
        self.parent.StatusBarProcessing('Filter processing commenced')
        
        wx.Yield()
        attributes=[self.text_ruwe, self.text_binProbability, self.text_Min_Sepn, self.text_ageDiffMax]
        for attribute in attributes:
            attribute.setValidRoutine(attribute.Validate_Float)
            if not attribute.runValidRoutine():
                return

        # This routine populates the StarList List Control and filters for Radial velocity and signal to
        # noise ratios for proper motion and paralax.
        gl_cfg.setItem('pxsn_gt',self.spin_parallax_SN.GetValue(),'FILTER')
        gl_cfg.setItem('rpsn_gt',self.spin_red_mag_SN.GetValue(),'FILTER')
        gl_cfg.setItem('g_sn_gt',self.spin_green_mag_SN.GetValue(),'FILTER')
        gl_cfg.setItem('bpsn_gt',self.spin_blue_mag_SN.GetValue(),'FILTER')
        gl_cfg.setItem('pmsn_gt',self.spin_pmsnratio.GetValue(),'FILTER')
        gl_cfg.setItem('rv_lt',self.spin_diff_radial_velocity.GetValue(),'FILTER')
        gl_cfg.setItem('ruwe_lt',self.text_ruwe.GetValue(),'FILTER')
        gl_cfg.setItem('bin_probability_lt',self.text_binProbability.GetValue(),'FILTER')
        #gl_cfg.setItem('io',self.combo_InOut.GetSelection(),'FILTER')
        gl_cfg.setItem('cutoff-outer',self.spin_distCutoff.GetValue(),'FILTER')
        gl_cfg.setItem('cutoff-inner',self.spin_distInnerCutoff.GetValue(),'FILTER')
        gl_cfg.setItem('min-sepn',self.text_Min_Sepn.GetValue(),'FILTER')
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        gl_cfg.setItem('age-diff-max',self.text_ageDiffMax.GetValue(),'FILTER')
        gl_cfg.setItem('activate-age-comp',self.activateAgeCompCheckBox.GetValue(),'FILTER')
        
        self.loadData.Disable() #Disable the button to avoid being pressed twice
        
        #print(self.parent.status)
        self.parent.export=[]
        self.listctrl.DeleteAllItems() # clear the control
        self.parent.star_rows=pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/star_rows.saved') # Pick up most recent starlist if changed.
        selectedStarBinaryMappings=self.parent.selectedStarBinaryMappings 
        star_rows=self.parent.star_rows
        self.OnReset()  # Reset starting point to end of data load.
        #
        #Initialise variables
        #

        lenArray=len(self.parent.star_rows)
        
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
        age_flame=0
        age_flame1=0
        radialvelocity=1
        ROWCOUNTMATRIX['ADQL']=lenArray /2  # Number of binaries
        sn_px_limit=float(self.spin_parallax_SN.GetValue())
        sn_rp_limit=float(self.spin_red_mag_SN.GetValue())
        sn_g_limit=float(self.spin_green_mag_SN.GetValue())
        sn_bp_limit=float(self.spin_blue_mag_SN.GetValue())
        sn_pm_limit=float(self.spin_pmsnratio.GetValue())
        distCutoff_limit=float(self.spin_distCutoff.GetValue())
        minSepn_limit=float(self.text_Min_Sepn.GetValue())
        ageDiffMax_limit=float(self.text_ageDiffMax.GetValue())
        activate_ageDiffMax=float(self.activateAgeCompCheckBox.GetValue())
        distInnerCutoff_limit=float(self.spin_distInnerCutoff.GetValue())
        #outerShell=bool(self.combo_InOut.GetSelection())
        ruwe_limit=float(self.text_ruwe.GetValue())
        binProbability_limit=float(self.text_binProbability.GetValue())
        
        rv_diff_limit=float(self.spin_diff_radial_velocity.GetValue())
        idxBin=0   # Binary index (obviously there are 2x as many stars as binaries)
        star_rows=star_rows.convert_dtypes()
        
        #print(star_rows)
        #print(self.parent.status)
        concat_df = pd.concat([self.parent.status,self.parent.status]).sort_values(by=['pairnumber']).reset_index(drop=True)
        #Select currently included rows only
        #print(concat_df)
        indexStatus = concat_df.index
        condition = concat_df.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        excludeArr=[]
        for idxStar in statusIndicesList:
        #for idxStar, row in star_rows.iterrows():
            idxBin=int(idxStar/2)
            row=star_rows.iloc[idxStar]
            
            if not idxStar % 100:
                label=float(100 * idxStar /(lenArray))
                self.loadData.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    self.loadData.Enable()
                    return
                wx.Yield()
            ## We can skip this code after n>1000
            #if self.parent.status.include[idxBin]==0 and idxStar>1000:
            #    continue
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
                        self.parent.StatusBarProcessing(excludeTxt)
                        radialvelocity=0
                    rv1=rv
                    if activate_ageDiffMax:
                        if row.age_flame:
                            age_flame=float(row.age_flame)
                        else:
                            age_flame=0
                            include=0
                            excludeTxt='age_flame=0'
                            self.parent.StatusBarProcessing(excludeTxt)
                        age_flame1=age_flame
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
                            self.parent.StatusBarProcessing(excludeTxt)
                            radialvelocity=0
                        # Must all exist
                        if rv_diff_limit and rv and rv1:
                            sn_row=abs(float(rv1-rv))
                            if sn_row>rv_diff_limit:
                                excludeTxt=f'RV diff={int(sn_row)}'
                                self.parent.StatusBarProcessing(excludeTxt)
                                include=0
                            
                        if activate_ageDiffMax:
                            if row.age_flame:
                                age_flame=float(row.age_flame)
                            else:
                                age_flame=0
                                include=0
                                excludeTxt='age_flame=0'
                                self.parent.StatusBarProcessing(excludeTxt)
                            age_flame1=age_flame
                        
                        # Must all exist
                        if  activate_ageDiffMax and ageDiffMax_limit and age_flame and age_flame1:
                            ageDiff=abs(float(age_flame1-age_flame))
                            if ageDiff>ageDiffMax_limit:
                                excludeTxt=f'ageDiff > {float(ageDiff)}'
                                self.parent.StatusBarProcessing(excludeTxt)
                                include=0
                    else:
                        self.parent.StatusBarProcessing (f'Skipped record {idxStar}')
                        row=row.transpose()
                        print(1, row)
                        print(idxStar)
                        print(star_rows[:idxStar+2])
                        print(selectedStarBinaryMappings[:int(idxStar/2+2)])
                        self.loadData.SetBackgroundColour(Colour(150,20,20))
                        self.loadData.Enable()
                        return
                        #continue
            except Exception:
                print(2, row)
                self.parent.StatusBarProcessing(f'idxStar = {idxStar}')
                #print(star_rows)
                print(star_rows[:idxStar+5])
                self.loadData.SetBackgroundColour(Colour(150,20,20))
                self.loadData.Enable()
                return
                
            if math.isnan(float(rv)) or math.isnan(float(rv1)):
                include=0
                excludeTxt='rv=<na>'
                self.parent.StatusBarProcessing(excludeTxt)
                radialvelocity=0
            #print(row.PHOT_RP_MEAN_FLUX_OVER_ERROR)
            if pd.isna(row.PHOT_G_MEAN_FLUX_OVER_ERROR):
                include=0
                excludeTxt='PHOT_G...=<na>'
                self.parent.StatusBarProcessing(excludeTxt)
                radialvelocity=0
                
            if pd.isna(row.PHOT_RP_MEAN_FLUX_OVER_ERROR):
                include=0
                excludeTxt='PHOT_RP...=<na>'
                self.parent.StatusBarProcessing(excludeTxt)
                radialvelocity=0
                
            if pd.isna(row.PHOT_BP_MEAN_FLUX_OVER_ERROR):
                include=0
                excludeTxt='PHOT_BP...=<na>'
                self.parent.StatusBarProcessing(excludeTxt)
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
                
            try:
                binProb=float(row.classprob_dsc_specmod_binarystar)
            except Exception:
                binProb=0
                
            if include:
                #Parallax S/N filter
                if include and sn_px_limit:
                    sn_row=abs(float(row.PARALLAX)/float(row.PARALLAX_ERROR))
                    if sn_px_limit>sn_row:
                        excludeTxt=f'SN_PX={int(sn_row)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0
                        
                #and phot_g_mean_flux_over_error > 50
                #and phot_rp_mean_flux_over_error > 10
                #and phot_bp_mean_flux_over_error > 10
                #Green Flux S/N filter
                if include and sn_g_limit:
                    sn_row=abs(float(row.PHOT_G_MEAN_FLUX_OVER_ERROR))
                    if sn_g_limit>sn_row:
                        excludeTxt=f'SN_G={int(sn_row)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0
                #Red Flux S/N filter
                if include and sn_rp_limit:
                    sn_row=abs(float(row.PHOT_RP_MEAN_FLUX_OVER_ERROR))
                    if sn_rp_limit>sn_row:
                        excludeTxt=f'SN_Rp={int(sn_row)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0
                #Blue Flux S/N filter
                if include and sn_bp_limit:
                    sn_row=abs(float(row.PHOT_BP_MEAN_FLUX_OVER_ERROR))
                    if sn_bp_limit>sn_row:
                        excludeTxt=f'SN_Bp={int(sn_row)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0
                #Cut off stars outside outer limits
                dist_row=abs(float(row.DIST))
                if include and dist_row>distCutoff_limit:
                    excludeTxt=f'Exceeds outer cutoff'
                    self.parent.StatusBarProcessing(excludeTxt)
                    include=0
                #Cut off inside  inner limits
                if  include and dist_row<distInnerCutoff_limit:
                    excludeTxt=f'Less than inner cutoff'
                    self.parent.StatusBarProcessing(excludeTxt)
                    include=0
                #print(row)
                #Exclude separations less than minimum separation
                if  include and self.parent.binaryDetail.r[idxBin]<minSepn_limit:
                    excludeTxt=f'Less than minimum Separation'
                    self.parent.StatusBarProcessing(excludeTxt)
                    include=0
                    
                if include and sn_pm_limit:
                    sn_row=abs(float(row.PMRA)/float(row.PMRA_ERROR))
                    if sn_pm_limit>sn_row:
                        excludeTxt=f'SN_PMRA={int(sn_row)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0
                    sn_row=abs(float(row.PMDEC)/float(row.PMDEC_ERROR))
                    if  include and sn_pm_limit>sn_row:
                        excludeTxt=f'SN_PMDEC={int(sn_row)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0

                if include and ruwe_limit:
                    ruwe_row=abs(ruwe)
                    #Exclude ruwe above limit or 0 (ie not available)
                    if ruwe_row>ruwe_limit or ruwe_row==0:
                        excludeTxt=f'RUWE={round(float(ruwe_row),2)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0 
                        #self.parent.status.ruweExcl[idxBin]=0

                if include and binProbability_limit:
                    binProb_row=abs(binProb)
                    #Exclude binProb_row above limit or 0 (ie not available)
                    if binProb_row>binProbability_limit or binProb_row==0:
                        excludeTxt=f'Excluded because probability {round(float(binProb_row),2)} > limit = {round(float(binProbability_limit),2)}'
                        self.parent.StatusBarProcessing(excludeTxt)
                        include=0
                    #else:
                    #    print(f'Probability {round(float(binProb_row),2)} !> limit = {round(float(binProbability_limit),2)}')

            if not include:
                self.parent.status.include[idxBin]=0
            odd=(idxStar-2*idxBin)
            if odd and self.parent.status.include[idxBin]:
                primaryPointer=self.parent.X.iloc[idxBin]
                star2Pointer=self.parent.Y.iloc[idxBin]
                #print(primaryPointer)
                exportRecord=self.createExportRecord(primaryPointer, star2Pointer, idxBin)
            excludeArr.append(excludeTxt)

        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle(f'bindata/{RELEASE}/{CATALOG}/export.saved')
        self.restoreListCtrl(txtArr=excludeArr)
        self.loadData.SetLabel(f'100%')
        self.parent.status['populateOut']=self.parent.status['include']
        self.parent.status['hrOut']=self.parent.status['include']
        self.parent.status['kineticOut']=self.parent.status['include']
        self.parent.status['massVmassOut']=self.parent.status['include']
        self.parent.status['tfOut']=self.parent.status['include']
        # Save pandas status file as pickle files for next time.
        self.parent.status.to_pickle(f'bindata/{RELEASE}/{CATALOG}/status.saved')

        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)

        populateOut=self.parent.status['populateOut'].sum()
        self.dataInTotal.SetLabel(f'{populateOut:,}')
        self.loadData.Enable()
        self.parent.printArrays()
        
        self.parent.StatusBarNormal('Completed OK')
        
    def restoreListCtrl(self, event=0, limit=1000, txtArr=[]):
        
        try:
            self.parent.star_rows=self.parent.star_rows.convert_dtypes()
        except Exception:
            pass
        #print(self.parent.star_rows)
        for idxStar, row  in self.parent.star_rows.iterrows():
            #print(row)
            if idxStar>=limit:
                break
            try:
                rv=float(row.RADIAL_VELOCITY)
            except Exception:
                rv=0
                self.parent.status.include[int(idxStar/2)]=0
                self.parent.status.radialvelocity[int(idxStar/2)]=0
            if not rv:
                self.parent.status.include[int(idxStar/2)]=0
                self.parent.status.radialvelocity[int(idxStar/2)]=0                
            try:
                ruwe=float(row.RUWE)
            except Exception:
                ruwe=0             
            try:
                age=float(row.age_flame)
            except Exception:
                age=0             
            try:
                mass=float(row.mass_flame)
            except Exception:
                mass=0        
            try:
                binarystar=float(row.classprob_dsc_specmod_binarystar)
            except Exception:
                binarystar=0
            if idxStar+1>len(txtArr):
                txt=''
            else:
                txt=txtArr[idxStar]
            try:
                self.listctrl.Append(
                    [int(row.SOURCE_ID),
                     int(row.PAIRING),
                     round(float(row.RA_),4),
                     #float(row.RA_ERROR),
                     round(float(row.DEC_),4) ,
                     #float(row.DEC_ERROR),
                     round(float(row.PARALLAX),4),
                     round(float(row.PARALLAX_ERROR),4),
                     round(float(row.PMRA),4),
                     round(float(row.PMRA_ERROR),4),
                     round(float(row.PMDEC),4),
                     round(float(row.PMDEC_ERROR),4),
                     round(ruwe, 4),
                     round(rv,4),
                     row.RELEASE_,
                     self.parent.status.radialvelocity[int(idxStar/2)],
                     self.parent.status.notgroup[int(idxStar/2)],
                     self.parent.status.include[int(idxStar/2)],
                     round(float(row.PHOT_G_MEAN_MAG),4),
                     round(float(mass),4),
                     round(float(age),4),
                     round(float(binarystar),4),
                     txt
                     ]
                )
                     
        #"phot_g_mean_flux_over_error"	FLOAT, \
        #"phot_rp_mean_flux_over_error"	FLOAT, \
        #"phot_bp_mean_flux_over_error"	FLOAT, \
        #"mass_flame"	FLOAT, \
        #"mass_flame_upper"	FLOAT, \
        #"mass_flame_lower"	FLOAT, \
        #"age_flame"	FLOAT, \
        #"age_flame_upper"	FLOAT, \
        #"age_flame_lower"	FLOAT, \
        #"classprob_dsc_specmod_binarystar"	FLOAT, \
            except Exception:
                print(self.parent.status)
                print(row)
                self.parent.StatusBarProcessing('"star_rows" Error')
                #exit(1)

class skyDataPlotting(masterProcessingPanel):

# Plot position on sky for chosen binaries.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_v)
        fgsizer = wx.FlexGridSizer(cols=14, hgap=0, rows=2, vgap=0)           # On left hand side
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

        # Create Galactic coords check box
        showGalacticCoordsStaticText = StaticText(self, id=wx.ID_ANY, label="Galactic coords")
        fgsizer.Add(showGalacticCoordsStaticText, 0, wx.ALL, 2)
        self.showGalacticCoordsCheckBox = CheckBox(self)
        self.showGalacticCoordsCheckBox.SetToolTip("Show Galactic coords instad of RA & Dec.")
        self.showGalacticCoordsCheckBox.SetValue(gl_cfg.getBoolean('galacticCoords', 'SKYPLOT'))
        fgsizer.Add(self.showGalacticCoordsCheckBox, 0, wx.ALL, 2)

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

        ## Draw imported stars only
        #
        #self.starsOnly_but = Button(self, id=wx.ID_ANY, label="&Stars Only", pos=wx.DefaultPosition,size=wx.DefaultSize)
        #self.starsOnly_but.Bind(wx.EVT_BUTTON, self.OnStarsOnly)
        #fgsizer.Add(self.starsOnly_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Draw velocity map
        
        try:
            self.skyGraph = matplotlibPanel(parent=self, size=(1350, 750))
            fg2sizer.Add(self.skyGraph)
        except Exception:
            pass
        
        self.Layout()
        

    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        self.plot_but.Enable()
        #self.starsOnly_but.Enable()
        self.parent.StatusBarNormal('Completed OK')
                
    def OnPlot(self, event=0):

        global CANCEL
        CANCEL = False
        self.plot_but.Disable()
        self.parent.export=[]
        
        self.parent.StatusBarProcessing('Sky plotting commenced')
        
        prntVersion=self.prntVersionCheckBox.GetValue()
        gl_cfg.setItem('prntversion',prntVersion, 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('unselected',self.unselectedCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('allwhite',self.allWhiteCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('suppressgroups',self.suppressGroupsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('suppressrvzero',self.suppressRVZeroCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('galacticCoords',self.showGalacticCoordsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        #
        #print(self.parent.X.ra)
        
        xdata1 = pd.DataFrame(self.parent.X.ra * self.parent.status['include'], columns=['ra'])
        ydata1 = pd.DataFrame(self.parent.X.dec * self.parent.status['include'], columns=['dec'])
        xdata2 = pd.DataFrame(self.parent.X.ra, columns=['ra'])
        ydata2 = pd.DataFrame(self.parent.X.dec, columns=['dec'])
        if self.showGalacticCoordsCheckBox.GetValue():
            self.skyGraph.axes.set_ylabel("Galactic 'l' (deg)", fontsize=FONTSIZE)
            self.skyGraph.axes.set_xlabel("Galactic 'b' (deg)", fontsize=FONTSIZE)
        else:
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
            
            if self.showGalacticCoordsCheckBox.GetValue():
                l=[]
                b=[]
                for i in range(len(xdata2.ra)):
                    # Convert to Galactic Coords.
                    sc = SkyCoord(ra=xdata2.ra[i]*u.deg,dec=ydata2.dec[i]*u.deg)
                    gal_l=str(sc.galactic.l)
                    try:
                        deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_l)
                    except:
                        self.parent.StatusBarProcessing(f'Missing decimal point in gal_l={gal_l}')
                        deg, minutes, seconds, fraction  =  re.split('[dms]', gal_l)
                    gal_l=float(deg) + float(minutes)/60  + float(seconds)/3600
                    l.append(gal_l)
                    
                    gal_b=str(sc.galactic.b)
                    try:
                        deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_b)
                    except:
                        self.parent.StatusBarProcessing(f'Missing decimal point in gal_b={gal_b}')
                        deg, minutes, seconds, fraction  =  re.split('[dms]', gal_b)
                    gal_b=float(deg) + float(minutes)/60 + float(seconds)/3600
                    b.append(gal_b)
                xdata2.ra=l
                ydata2.dec=b
            
            marker = ','
            markersize=1
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
                markersize=1.5
            try:
                self.line2, = self.skyGraph.axes.plot(xdata2.ra.to_list(), ydata2.dec.to_list(), color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
            except Exception as e:
                self.parent.StatusBarProcessing (f'self.skyGraph.axes.plot Crash 1) "{e}"')
                print(xdata2)
                print(ydata2)
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
        markersize=1
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
            markersize=1.5
            
        if self.showGalacticCoordsCheckBox.GetValue():
            l=[]
            b=[]
            for i in range(len(xdata1.ra)):
                # Convert to Galactic Coords.
                sc = SkyCoord(ra=xdata1.ra[i]*u.deg,dec=ydata1.dec[i]*u.deg)
                gal_l=str(sc.galactic.l)
                try:
                    deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_l)
                except:
                    self.parent.StatusBarProcessing(f'Missing decimal point in gal_l={gal_l}')
                    deg, minutes, seconds, fraction  =  re.split('[dms]', gal_l)
                gal_l=float(deg) + float(minutes)/60  + float(seconds)/3600
                l.append(gal_l)
                
                gal_b=str(sc.galactic.b)
                try:
                    deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_b)
                except:
                    self.parent.StatusBarProcessing(f'Missing decimal point in gal_b={gal_b}')
                    deg, minutes, seconds, fraction  =  re.split('[dms]', gal_b)
                gal_b=float(deg) + float(minutes)/60 + float(seconds)/3600
                b.append(gal_b)
            xdata1.ra=l
            ydata1.dec=b
        try:
            self.line, = self.skyGraph.axes.plot(xdata1.ra.to_list(), ydata1.dec.to_list(), color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
        except Exception as e:
            self.parent.StatusBarProcessing (f'self.skyGraph.axes.plot Crash 2) "{e}"')
            print(xdata1)
            print(ydata1)
            self.plot_but.SetBackgroundColour(Colour(150,20,20))
            self.plot_but.Enable()
            return
        
        self.skyGraph.draw(self.line, xdata1, ydata1, True,[] )
        #        
        try:   
            self.skyGraph.Layout()
        except Exception:
            pass
        self.Layout()
        self.parent.printArrays()

        self.plot_but.Enable()
        
        self.parent.StatusBarNormal('Completed OK')
        
class HRDataPlotting(masterProcessingPanel):

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
        self.text_colourLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('col_lower', 'HRPLOT', .7), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_colourLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_colourUpper = TextCtrl(self, id=wx.ID_ANY, value="2.3", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_colourUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('col_upper', 'HRPLOT', 2), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_colourUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_magLower = TextCtrl(self, id=wx.ID_ANY, value="5.5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT) 
        #self.text_magLower = TextCtrl(self, id=wx.ID_ANY, value="5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_magLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mag_lower', 'HRPLOT', 4.7), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_magLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_magUpper = TextCtrl(self, id=wx.ID_ANY, value="9.5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT) 
        #self.text_magUpper = TextCtrl(self, id=wx.ID_ANY, value="8.5", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_magUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mag_upper', 'HRPLOT', 8.7), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_magUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.text_magRange = TextCtrl(self, id=wx.ID_ANY, value="0.3", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        self.text_magRange = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('mag_range', 'HRPLOT', 0.4), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
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
        try:
            self.hrGraph = matplotlibPanel(parent=self, size=(950, 750))
            fg2sizer.Add(self.hrGraph)
        except Exception:
            pass
        
        self.Layout()
        
    def OnCancel(self, event=0):

        global CANCEL
        CANCEL= True
        self.Filter_but.Enable()
        self.parent.StatusBarNormal(f'Completed OK')
        
    def OnReset(self, event=0):
        #if hasattr(self.parent, 'populateOut'):
        self.parent.status['include']=self.parent.status['populateOut']
        self.parent.status['hrOut']=self.parent.status['populateOut']
        self.parent.status['kineticOut']=self.parent.status['populateOut']
            #self.parent.status.include=self.parent.hrResetList['include']
        self.OnPlot()
        
    def OnFilter(self, event=0):
        
        self.parent.StatusBarProcessing('H-R plotting commenced')
        
        attributes=[self.text_colourLower, self.text_colourUpper, self.text_magLower, self.text_magUpper,
                    self.text_magRange]
        for attribute in attributes:
            attribute.setValidRoutine(attribute.Validate_Float)
            if not attribute.runValidRoutine():
                return
            
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

                #primaryPointer=self.parent.X1
                #star2Pointer=self.parent.X2
                self.createExportRecord(X1, X2, index)
                #exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.SOURCE_ID),
                #    'ra1':float(primaryPointer.RA_),
                #    'dec1':float(primaryPointer.DEC_),
                #    'mag1':primaryPointer.phot_g_mean_mag,
                #    'MAG1':self.parent.X.mag[index],
                #    'PARALLAX1':float(primaryPointer.PARALLAX),
                #    'parallax_error1':float(primaryPointer.parallax_error),
                #    'DIST1':float(primaryPointer.DIST),
                #    'RUWE1':primaryPointer.RUWE,
                #    'RUWE1':primaryPointer.ruwe,
                #    'PMRA1':float(primaryPointer.pmra),
                #    'PMRA_ERROR1':float(primaryPointer.pmra_error),
                #    'PMDEC1':float(primaryPointer.pmdec),
                #    'PMDEC_ERROR1':float(primaryPointer.pmdec_error),
                #    'BminusR1':float(primaryPointer.bp_rp),
                #    'mass_flame1':primaryPointer.mass_flame,
                #    'mass_flame_upper1':primaryPointer.mass_flame_upper,
                #    'mass_flame_lower1':primaryPointer.mass_flame_lower,
                #    'age_flame1':primaryPointer.age_flame,
                #    'age_flame_upper1':primaryPointer.age_flame_upper,
                #    'age_flame_lower1':primaryPointer.age_flame_lower,
                #    'PROB1':primaryPointer.classprob_dsc_specmod_binarystar,
                #    'SOURCE_ID_SECONDARY':str(star2Pointer.SOURCE_ID),
                #    'ra2':float(star2Pointer.RA_),
                #    'dec2':float(star2Pointer.DEC_),
                #    'mag2':star2Pointer.phot_g_mean_mag,
                #    'MAG2':self.parent.Y.mag[index],
                #    'PARALLAX2':float(star2Pointer.PARALLAX),
                #    'parallax_error2':float(star2Pointer.parallax_error),
                #    'DIST2':float(star2Pointer.DIST),
                #    'RUWE2':star2Pointer.ruwe,
                #    'PMRA2':float(star2Pointer.pmra),
                #    'PMRA_ERROR2':float(star2Pointer.pmra_error),
                #    'PMDEC2':float(star2Pointer.pmdec),
                #    'PMDEC_ERROR2':float(star2Pointer.pmdec_error),
                #    'BminusR2':float(star2Pointer.bp_rp),
                #    'mass_flame2':star2Pointer.mass_flame,
                #    'mass_flame_upper2':star2Pointer.mass_flame_upper,
                #    'mass_flame_lower2':star2Pointer.mass_flame_lower,
                #    'age_flame2':star2Pointer.age_flame,
                #    'age_flame_upper2':star2Pointer.age_flame_upper,
                #    'age_flame_lower2':star2Pointer.age_flame_lower,
                #    'PROB2':star2Pointer.classprob_dsc_specmod_binarystar,
                #    'vRA':abs(self.parent.binaryDetail.vRA[index]),
                #    'vRAerr':abs(self.parent.binaryDetail.vRAerr[index]),
                #    'vDEC':abs(self.parent.binaryDetail.vDEC[index]), 
                #    'vDECerr':abs(self.parent.binaryDetail.vDECerr[index]),                      
                #    'V2D':math.sqrt(self.parent.binaryDetail.vRA[index]**2+self.parent.binaryDetail.vDEC[index]**2),
                #    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                #    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                #    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                #    'Log10vRA':np.log10(self.parent.binaryDetail.vRA[index]),
                #    'Log10vDEC':np.log10(self.parent.binaryDetail.vDEC[index]),
                #    'Log10r':np.log10(self.parent.binaryDetail.r[index]),
                #    #'M':M,
                #    'r':self.parent.binaryDetail.r[index]
                #}
                #
                #self.parent.export.append(exportRecord)
        
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle(f'bindata/{RELEASE}/{CATALOG}/export.saved')   
        self.parent.printArrays()

        self.parent.status['hrOut']=self.parent.status['include']
        self.parent.status['kineticOut']=self.parent.status['include']
        
        # Save pandas status file as pickle files for next time.
        try:
            self.parent.status.to_pickle(f'bindata/{RELEASE}/{CATALOG}/status.saved')
        except Exception:
            self.parent.StatusBarProcessing('Error directory failed to save')
            print (self.parent.status)

        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
        self.OnPlot()
        label=int(100)
        self.Filter_but.SetLabel(f'{label:,.1f}%')
        self.Filter_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
    def XreturnY(self, X):
        # Return range of acceptable magnitudes.
        Y=float(self.m*float(X) + float(self.c))
        
        return [Y-self.Yerr,Y+self.Yerr]
    
    def OnPlot(self, event=0):

        global CANCEL
        CANCEL = False
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
            markersize=1
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
                markersize=1.5
            #Display graph
            try:
                self.line2, = self.hrGraph.axes.plot(xdata2, ydata2, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
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
            #c=xdata1
    
        # visualizing the mapping from values to colors
        #cbar=self.hrGraph.colorbar()
        ##legend
        #cbar.set_label(r'Redshift in $kms^{-1}$', rotation=270, labelpad=20, y=0.50)
        # Saves plot
        
        marker = ','
        markersize=1
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
            markersize=1.5
        xdata1=xdata1.tolist()
        ydata1=ydata1.tolist()
        self.line, = self.hrGraph.axes.plot(xdata1, ydata1, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
    
        legend1.append(self.line)
        legend2.append('Selected binaries')
        self.hrGraph.draw(self.line, xdata1, ydata1, True,[] )
                
        #    """
        #Attach a text label above each bar displaying its height
        #"""
        self.hrGraph.frames=[] 
        try:
            self.hrGraph.Layout()
        except Exception:
            pass
        self.Layout()

        self.parent.printArrays()
        
        self.plot_but.Enable()

        self.parent.StatusBarNormal(f'Completed OK')
        
class kineticDataPlotting(masterProcessingPanel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
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
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','KINETIC', 5)))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer umber of bins to divide x-scale into.")
        
        self.textctrl_xLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_lower','KINETIC', .0001), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xLower.SetToolTip("Lower end of x-scale.")
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','KINETIC', .1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_yLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_lower','KINETIC', .1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yLower.SetToolTip("Lower end of y-scale.")
        self.textctrl_yUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_upper','KINETIC', 5), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yUpper.SetToolTip("Upper end of y-scale.")
        
        # Outlier values
        self.text_x_TopLeft = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_topLeft','KINETIC', .004), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT) 
        self.text_x_TopLeft.SetToolTip("Top left x of outlier line.") 
        fgsizer.Add(self.text_x_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_y_TopLeft = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_topLeft','KINETIC', 4), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.text_y_TopLeft.SetToolTip("Top left y of outlier line.") 
        fgsizer.Add(self.text_y_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_x_BottomRight = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_bottomRight','KINETIC', .1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.text_x_BottomRight.SetToolTip("Bottom right x of outlier line.") 
        fgsizer.Add(self.text_x_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_y_BottomRight = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_bottomRight','KINETIC', 1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.text_y_BottomRight.SetToolTip("Bottom right y of outlier line.") 
        fgsizer.Add(self.text_y_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Upper cutoff
        self.text_upperCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_cutoff','KINETIC', 4), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperCutoff.SetToolTip("Value of y-scale above which values will be ignored.")
        
        # v x err reporting threshold
        self.text_vxerrCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('v_dv_cutoff','KINETIC', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        self.text_vxerrCutoff.SetToolTip("v/v_error reporting threshold.")
        fgsizer.Add(self.text_vxerrCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Lower bin cutoff textctrl
        self.lowerBinCutoffTextCtrl = SpinCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=99,initial=int(gl_cfg.getItem('lower_bin_cutoff','KINETIC', 5)))   
        self.lowerBinCutoffTextCtrl.SetToolTip("Enter number below which occupancy not to display bins.")
        fgsizer.Add(self.lowerBinCutoffTextCtrl, 0, wx.ALL, 2)
        
        self.combo_yLog = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['log','normal'], value='')
        self.combo_yLog.SetSelection(int(gl_cfg.getItem('y_scale','KINETIC', 0)))
        fgsizer.Add(self.combo_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.combo_yAvg = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['rms','mean'], value='')
        self.combo_yAvg.SetSelection(int(gl_cfg.getItem('y_avg','KINETIC', 0)))
        fgsizer.Add(self.combo_yAvg, 0, wx.ALIGN_LEFT|wx.ALL, 5)
                
        # Create show bins check box
        showRABinsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bins (RA and Dec)")
        fgsizer.Add(showRABinsStaticText, 0, wx.ALL, 2)
        self.showBinsCheckBox = CheckBox(self)
        self.showBinsCheckBox.SetValue(gl_cfg.getBoolean('showbins','KINETIC'))
        self.showBinsCheckBox.SetToolTip("Display 1D RA & Dec data in bins.")
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
        try:
            self.velocityGraph = matplotlibPanel(parent=self, size=(1350, 750))
            fg2sizer.Add(self.velocityGraph)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Metric", wx.LIST_FORMAT_RIGHT, width=280 )
        self.summaryList.SetColumnWidth(0, 280)
        self.summaryList.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, width=120 )
        self.summaryList.SetColumnWidth(1, 120)
        self.SetSizer(self.sizer_v)
        try:
            self.velocityGraph.Layout()
        except Exception:
            pass
        self.Layout()

    def XreturnY(self, X):
        # Return lower outlier range.
        #Y=float(self.m*float(X) + float(self.c))
        Y=self.m*float(math.log10(X)) + self.c
        return 10**Y
    
    def OnReset(self, event=0):
        #if hasattr(self.parent, 'hrinclude'):
        self.parent.status['include']=self.parent.status['hrOut']
        self.parent.status['kineticOut']=self.parent.status['include']

    def OnPlot(self, event=0):
        
        global CANCEL
        CANCEL = False
        self.parent.StatusBarProcessing('Kinetic plotting commenced')
        
        attributes=[self.textctrl_xLower, self.textctrl_xUpper, self.textctrl_yLower, self.textctrl_yUpper,
                    self.text_x_TopLeft, self.text_y_TopLeft, self.text_x_BottomRight, self.text_y_BottomRight,
                    self.text_upperCutoff, self.text_vxerrCutoff]
        for attribute in attributes:
            attribute.setValidRoutine(attribute.Validate_Float)
            if not attribute.runValidRoutine():
                return
        
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
            dataRABins=binOrganiser(numRABins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            upper=top
            factor=10**(diff/numRABins)
            lower=upper/factor
            for i in range(numRABins):
                dataRABins.newBin(lower, upper)
                upper=lower
                lower=upper/factor
                
            numDECBins=int(self.spin_bins.GetValue()-1)      #  Get number of DEC bins (It's 1 fewer than the number of RA bins).
            dataDECBins=binOrganiser(numDECBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            
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
                vRA=float(self.parent.binaryDetail.vRA[i])
                vDEC=float(self.parent.binaryDetail.vDEC[i])
                r=float(self.parent.binaryDetail.r[i])
                vRAerr=float(self.parent.binaryDetail.vRAerr[i])
                vDECerr=float(self.parent.binaryDetail.vDECerr[i])
                # Go through and bin
                label=float(100.0 * i /lenArray)
                self.plot_but.SetLabel(f'{label:,.1f}%')
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
                        #primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
                        #star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
                        #primaryPointer=self.parent.X[str(i+1)]
                        #star2Pointer=self.parent.Y[str(i+1)]
                        #primaryPointer=pd.DataFrame(primaryPointer)
                        #star2Pointer=pd.DataFrame(primaryPointer)
                        primaryPointer=self.parent.X.iloc[i]
                        star2Pointer=self.parent.Y.iloc[i]
                        self.createExportRecord(primaryPointer, star2Pointer, i)
                        #exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.source_id),
                        #    'ra1':float(primaryPointer.RA_),
                        #    'dec1':float(primaryPointer.DEC_),
                        #    'mag1':primaryPointer.phot_g_mean_mag,
                        #    'MAG1':self.parent.X.mag[i],
                        #    'PARALLAX1':float(primaryPointer.parallax),
                        #    'parallax_error1':float(primaryPointer.parallax_error),
                        #    'DIST1':float(primaryPointer.DIST),
                        #    'RUWE1':primaryPointer.ruwe,
                        #    'RUWE1':primaryPointer.ruwe,
                        #    'PMRA1':float(primaryPointer.pmra),
                        #    'PMRA_ERROR1':float(primaryPointer.pmra_error),
                        #    'PMDEC1':float(primaryPointer.pmdec),
                        #    'PMDEC_ERROR1':float(primaryPointer.pmdec_error),
                        #    'BminusR1':float(primaryPointer.bp_rp),
                        #    'mass_flame1':primaryPointer.mass_flame,
                        #    'mass_flame_upper1':primaryPointer.mass_flame_upper,
                        #    'mass_flame_lower1':primaryPointer.mass_flame_lower,
                        #    'age_flame1':primaryPointer.age_flame,
                        #    'age_flame_upper1':primaryPointer.age_flame_upper,
                        #    'age_flame_lower1':primaryPointer.age_flame_lower,
                        #    'PROB1':primaryPointer.classprob_dsc_specmod_binarystar,
                        #    'SOURCE_ID_SECONDARY':str(star2Pointer.source_id),
                        #    'ra2':float(star2Pointer.RA_),
                        #    'dec2':float(star2Pointer.DEC_),
                        #    'mag2':star2Pointer.phot_g_mean_mag,
                        #    'MAG2':self.parent.Y.mag[i],
                        #    'PARALLAX2':float(star2Pointer.parallax),
                        #    'parallax_error2':float(star2Pointer.parallax_error),
                        #    'DIST2':float(star2Pointer.DIST),
                        #    'RUWE2':star2Pointer.ruwe,
                        #    'PMRA2':float(star2Pointer.pmra),
                        #    'PMRA_ERROR2':float(star2Pointer.pmra_error),
                        #    'PMDEC2':float(star2Pointer.pmdec),
                        #    'PMDEC_ERROR2':float(star2Pointer.pmdec_error),
                        #    'BminusR2':float(star2Pointer.bp_rp),
                        #    'mass_flame2':star2Pointer.mass_flame,
                        #    'mass_flame_upper2':star2Pointer.mass_flame_upper,
                        #    'mass_flame_lower2':star2Pointer.mass_flame_lower,
                        #    'age_flame2':star2Pointer.age_flame,
                        #    'age_flame_upper2':star2Pointer.age_flame_upper,
                        #    'age_flame_lower2':star2Pointer.age_flame_lower,
                        #    'PROB2':star2Pointer.classprob_dsc_specmod_binarystar,
                        #    'vRA':abs(self.parent.binaryDetail.vRA[i]),
                        #    'vRAerr':abs(self.parent.binaryDetail.vRAerr[i]),
                        #    'vDEC':abs(self.parent.binaryDetail.vDEC[i]), 
                        #    'vDECerr':abs(self.parent.binaryDetail.vDECerr[i]),                         
                        #    'V2D':math.sqrt(self.parent.binaryDetail.vRA[i]**2+self.parent.binaryDetail.vDEC[i]**2),
                        #    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
                        #    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
                        #    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
                        #    'Log10vRA':np.log10(self.parent.binaryDetail.vRA[i]),
                        #    'Log10vDEC':np.log10(self.parent.binaryDetail.vDEC[i]),
                        #    'Log10r':np.log10(self.parent.binaryDetail.r[i]),
                        #    #'M':M,
                        #    'r':self.parent.binaryDetail.r[i]
                        #}
                        #
                        #self.parent.export.append(exportRecord)
                        
            xdata3ra=dataRABins.getBinXArray('centre')
            ydata3ra=dataRABins.getBinYArray(self.combo_yAvg.GetValue())
            rerrbin3ra=dataRABins.getBinXVarArray()
            verrbin3ra=dataRABins.getBinYVarArray()
                        
            self.line3ra = self.velocityGraph.axes.errorbar(xdata3ra, ydata3ra, xerr=rerrbin3ra, yerr=verrbin3ra, fmt='o', ecolor='r', elinewidth=2, capsize=0, mfc='r', mec='r', ms=3) #,label='Gaia binned'
            self.line3ra[-1][0].set_linestyle('-.') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line3ra[-1][1].set_linestyle('-.') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
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
               
            self.line3dec = self.velocityGraph.axes.errorbar(xdata3dec, ydata3dec, xerr=rerrbin3dec, yerr=verrbin3dec, fmt='o', ecolor='g', elinewidth=2, capsize=0, mfc='g', mec='g', ms=3) #,label='Gaia binned'
            self.line3dec[-1][0].set_linestyle('--')
            self.line3dec[-1][1].set_linestyle('--')
            if not prntVersion:
                legend1.append(self.line3dec)
                legend2.append('Gaia DEC binned data')
            
            self.velocityGraph.draw(self.line3dec, xdata3dec, ydata3dec, False, [] )
        
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle(f'bindata/{RELEASE}/{CATALOG}/export.saved')   
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
            markersize=1
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
                markersize=1.5
            self.linera, = self.velocityGraph.axes.plot(xdata1, ydata1ra, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
            self.velocityGraph.draw(self.linera, xdata1, ydata1ra, True, [] )
            self.linedec, = self.velocityGraph.axes.plot(xdata1, ydata1dec, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
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
            
        self.line2, = self.velocityGraph.axes.plot(xdata2, ydata2_1D, 'b-', lw=2)#,label='Newtonian')
        
        
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
        snPMRAoverDPMRAx=self.CalcMeanXYoverDxy('PMRA','PMRA_ERROR')
        self.summaryList.SetItem(rowCnt, 1, f"{snPMRAoverDPMRAx:,}")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N PMDEC')
        snPMDECoverDPMDECx=self.CalcMeanXYoverDxy('PMDEC','PMDEC_ERROR')
        self.summaryList.SetItem(rowCnt, 1, f"{snPMDECoverDPMDECx:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean S/N Px')
        snPxoverDpx=self.CalcMeanXYoverDxy('PARALLAX','parallax_error')
        self.summaryList.SetItem(rowCnt, 1, f"{snPxoverDpx:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean RUWE')
        avgRuwe=self.CalcMeanXYoverDxy('RUWE',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgRuwe:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Distance')
        avgDIST=self.CalcMeanXYoverDxy('DIST',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgDIST:,}")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Binary Probability for single stars')
        avgProb=self.CalcMeanXYoverDxy('classprob_dsc_specmod_binarystar',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgProb:,}")
                      
        rowCnt += 1 #Next row 
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Masses')
        avgMass=self.CalcPercentPairNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        rowCnt += 1 #Next row 
        self.summaryList.InsertItem(rowCnt, 'Fraction of stars with FLAME Masses')
        avgMass=self.CalcPercentEitherNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Ages')
        avgAge=self.CalcPercentPairNotNull('age_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgAge*100:,} %")
        
        ##print(self.parent.binaryDetail)
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
        # Save pandas status file as pickle files for next time.
        try:
            self.parent.status.to_pickle(f'bindata/{RELEASE}/{CATALOG}/status.saved')
        except Exception:
            self.parent.StatusBarProcessing('Error directory failed to save')
            print (self.parent.status)

        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
        self.parent.printArrays()

        self.plot_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
class TFDataPlotting(masterProcessingPanel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=13, hgap=0, rows=10, vgap=0)           # On left hand side
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
        
        # Upper bin Split header
        UpperBinSplit_StaticText = StaticText(self, id=wx.ID_ANY, label="Upper Bin Split")
        fgsizer.Add(UpperBinSplit_StaticText, 0, wx.ALL, 2)
       
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
        self.spin_bins.SetToolTip("Integer number of bins to divide x-scale into.")
        
        self.textctrl_xLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_lower','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xLower.SetToolTip("Lower end of x-scale.")
        self.textctrl_xLower.setValidRoutine(self.textctrl_xLower.Validate_Float)
        
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_xUpper.setValidRoutine(self.textctrl_xUpper.Validate_Float)
        
        self.textctrl_yLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_lower','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yLower.SetToolTip("Lower end of y-scale.")
        self.textctrl_yLower.setValidRoutine(self.textctrl_yLower.Validate_Float)
        
        self.textctrl_yUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_upper','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yUpper.SetToolTip("Upper end of y-scale.")
        self.textctrl_yUpper.setValidRoutine(self.textctrl_yUpper.Validate_Float)
        
        # Upper R cutoff
        self.text_upperRCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_rcutoff','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperRCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperRCutoff.SetToolTip("Value of r-scale (separation) above which values will be ignored.")
        self.text_upperRCutoff.setValidRoutine(self.text_upperRCutoff.Validate_Float)
        
        # Upper Y cutoff
        self.text_upperYCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_ycutoff','TULLEYFISHER'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperYCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperYCutoff.SetToolTip("Value of y-scale above which values will be ignored.")
        self.text_upperYCutoff.setValidRoutine(self.text_upperYCutoff.Validate_Float)
        
        # Lower bin cutoff textctrl
        self.lowerBinCutoffTextCtrl = SpinCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('lower_bin_cutoff','TULLEYFISHER')))  
        self.lowerBinCutoffTextCtrl.SetToolTip("Enter number below which not to display bins.")

        fgsizer.Add(self.lowerBinCutoffTextCtrl, 0, wx.ALL, 2)
        
        # Upper bin split spinctrl
        self.upperBinSplitSpinCtrl = SpinCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=999,initial=int(gl_cfg.getItem('upper_bin_split','TULLEYFISHER')))  
        self.upperBinSplitSpinCtrl.SetToolTip("Enter number above which to split each bin in two.")
        fgsizer.Add(self.upperBinSplitSpinCtrl, 0, wx.ALL, 2)
        
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
        self.TextCtrl_sepnCutoff.setValidRoutine(self.TextCtrl_sepnCutoff.Validate_Float)
        
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
        
        self.plot_but = Button(self, id=wx.ID_OK, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Cancel Button
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel binning.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw velocity map
        try:
            self.TulleyFPlot = matplotlibPanel(parent=self, size=(1350, 750))
            fg2sizer.Add(self.TulleyFPlot)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Metric", wx.LIST_FORMAT_RIGHT, width=280 )
        self.summaryList.SetColumnWidth(0, 280)
        self.summaryList.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, width=120 )
        self.summaryList.SetColumnWidth(1, 120)
        self.SetSizer(self.sizer_v)
        try:
            self.TulleyFPlot.Layout()
        except Exception:
            pass
        self.Layout()

    def OnReset(self, event=0):
        self.parent.status['include']=self.parent.status['kineticOut']

    def OnPlot(self, event=0):

        self.parent.StatusBarProcessing('Tulley Fisher plotting commenced')
        
        global CANCEL
        CANCEL = False
        wx.Yield()
        #self.parent.export=pd.DataFrame(columns=['SOURCE_ID_PRIMARY','ra1','dec1','mag1','SOURCE_ID_SECONDARY','ra2','dec2','mag2', 'vRA', 'vDEC', 'V2D', 'M', 'r'])
        self.parent.export=[]
        attributes=[self.textctrl_xLower, self.textctrl_xUpper, self.textctrl_yLower, self.textctrl_yUpper, self.text_upperRCutoff, self.text_upperYCutoff, self.TextCtrl_sepnCutoff]
        for attribute in attributes:
            if not attribute.runValidRoutine():
                return
        self.plot_but.Disable()
        
        gl_cfg.setItem('no_bins',self.spin_bins.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('x_lower',self.textctrl_xLower.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('x_upper',self.textctrl_xUpper.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('y_lower',self.textctrl_yLower.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('y_upper',self.textctrl_yUpper.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('upper_rcutoff',self.text_upperRCutoff.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('upper_ycutoff',self.text_upperYCutoff.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('lower_bin_cutoff',self.lowerBinCutoffTextCtrl.GetValue(),'TULLEYFISHER')
        gl_cfg.setItem('upper_bin_split',self.lowerBinCutoffTextCtrl.GetValue(),'TULLEYFISHER')
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
        dataTFBins=binOrganiser(numTFBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
        upper=top
        factor=10**(diff/numTFBins)
        lower=upper/factor
        for i in range(numTFBins):
            #if int(self.upperBinSplitSpinCtrl.GetValue())):
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
            #else:
            #    include=int(self.parent.status.include[i])
            #Set up local variables to avoid repeated PD access and for clarity
            if math.isnan(self.parent.binaryDetail.vRA[i]) :
                self.parent.StatusBarProcessing(f'i={i}, vRA = {self.parent.binaryDetail.vRA[i]}')
            if math.isnan(self.parent.binaryDetail.vDEC[i]) :
                self.parent.StatusBarProcessing(f'i={i}, vDEC = {self.parent.binaryDetail.vDEC[i]}')
            vRA=float(self.parent.binaryDetail.vRA[i])
            vDEC=float(self.parent.binaryDetail.vDEC[i])
            V2D=math.sqrt(vRA**2+vDEC**2)
            
            r=float(self.parent.binaryDetail.r[i])
            vRAerr=float(self.parent.binaryDetail.vRAerr[i])
            vDECerr=float(self.parent.binaryDetail.vDECerr[i])
            Verr=math.sqrt((vRA*vRAerr)**2+(vDEC*vDECerr)**2)/V2D
            M=float(self.parent.binaryDetail.M[i])
            # Go through and bin
            label=float(100.0 * i /lenArray)
            self.plot_but.SetLabel(f'{label:,.1f}%')
            if CANCEL:
                CANCEL = False
                self.plot_but.Enable()
                return
            wx.Yield()
            
            #primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
            #star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
            #primaryPointer=self.parent.X[str(i+1)]
            #star2Pointer=self.parent.Y[str(i+1)]
            #primaryPointer=pd.DataFrame(primaryPointer)
            #star2Pointer=pd.DataFrame(primaryPointer)
            primaryPointer=self.parent.X.iloc[i]
            star2Pointer=self.parent.Y.iloc[i]
            #exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.source_id),
            #    'ra1':float(primaryPointer.RA_),
            #    'dec1':float(primaryPointer.DEC_),
            #    'mag1':primaryPointer.phot_g_mean_mag,
            #    'MAG1':self.parent.X.mag[i],
            #    'PARALLAX1':float(primaryPointer.parallax),
            #    'parallax_error1':float(primaryPointer.parallax_error),
            #    'DIST1':float(primaryPointer.DIST),
            #    'RUWE1':primaryPointer.ruwe,
            #    'RUWE1':primaryPointer.ruwe,
            #    'PMRA1':float(primaryPointer.pmra),
            #    'PMRA_ERROR1':float(primaryPointer.pmra_error),
            #    'PMDEC1':float(primaryPointer.pmdec),
            #    'PMDEC_ERROR1':float(primaryPointer.pmdec_error),
            #    'BminusR1':float(primaryPointer.bp_rp),
            #    'mass_flame1':primaryPointer.mass_flame,
            #    'mass_flame_upper1':primaryPointer.mass_flame_upper,
            #    'mass_flame_lower1':primaryPointer.mass_flame_lower,
            #    'age_flame1':primaryPointer.age_flame,
            #    'age_flame_upper1':primaryPointer.age_flame_upper,
            #    'age_flame_lower1':primaryPointer.age_flame_lower,
            #    'PROB1':primaryPointer.classprob_dsc_specmod_binarystar,
            #    'SOURCE_ID_SECONDARY':str(star2Pointer.source_id),
            #    'ra2':float(star2Pointer.RA_),
            #    'dec2':float(star2Pointer.DEC_),
            #    'mag2':star2Pointer.phot_g_mean_mag,
            #    'MAG2':self.parent.Y.mag[i],
            #    'PARALLAX2':float(star2Pointer.parallax),
            #    'parallax_error2':float(star2Pointer.parallax_error),
            #    'DIST2':float(star2Pointer.DIST),
            #    'RUWE2':star2Pointer.ruwe,
            #    'PMRA2':float(star2Pointer.pmra),
            #    'PMRA_ERROR2':float(star2Pointer.pmra_error),
            #    'PMDEC2':float(star2Pointer.pmdec),
            #    'PMDEC_ERROR2':float(star2Pointer.pmdec_error),
            #    'BminusR2':float(star2Pointer.bp_rp),
            #    'mass_flame2':star2Pointer.mass_flame,
            #    'mass_flame_upper2':star2Pointer.mass_flame_upper,
            #    'mass_flame_lower2':star2Pointer.mass_flame_lower,
            #    'age_flame2':star2Pointer.age_flame,
            #    'age_flame_upper2':star2Pointer.age_flame_upper,
            #    'age_flame_lower2':star2Pointer.age_flame_lower,
            #    'PROB2':star2Pointer.classprob_dsc_specmod_binarystar,
            #    'vRA':self.parent.binaryDetail.vRA[i],
            #    'vRAerr':abs(self.parent.binaryDetail.vRAerr[i]),
            #    'vDEC':self.parent.binaryDetail.vDEC[i],
            #    'vDECerr':abs(self.parent.binaryDetail.vDECerr[i]),   
            #    'V2D':math.sqrt(self.parent.binaryDetail.vRA[i]**2+self.parent.binaryDetail.vDEC[i]**2),
            #    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
            #    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
            #    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
            #    'Log10vRA':np.log10(self.parent.binaryDetail.vRA[i]),
            #    'Log10vDEC':np.log10(self.parent.binaryDetail.vDEC[i]),
            #    'Log10r':np.log10(abs(self.parent.binaryDetail.r[i])),
            #    #'rerr'(abs(self.parent.binaryDetail.r[i]),
            #    'M':M,
            #    'r':self.parent.binaryDetail.r[i]
            #}
            #
            # Check Separation limits
            if self.combo_LtGt.GetSelection()==0:
                # Ie 'Outer' shell
                if r>float(self.TextCtrl_sepnCutoff.GetValue()) and upperYCutoff>V2D and upperRCutoff>r:
                    #self.parent.export.append(exportRecord)
                    self.createExportRecord(primaryPointer, star2Pointer, i)
                    if self.V1D_CheckBox.GetValue()==True:
                        if dataTFBins.binAddDataPoint(x=M, y=vRA, dy=vRAerr, value=0) :
                            self.parent.StatusBarProcessing(f'Exclude "vRAerr (a)" x={M}, y={vRA}')
                        if dataTFBins.binAddDataPoint(x=M, y=vDEC, dy=vDECerr, value=0) :
                            self.parent.StatusBarProcessing(f'Exclude "vDECerr (a)" x={M}, y={vDEC}')
                        
                    else:
                        if dataTFBins.binAddDataPoint(x=M, y=V2D, dy=Verr, value=0) :
                            self.parent.status.include[i]=0
                            self.parent.StatusBarProcessing(f'Exclude "Verr" x={M}, y={V2D}')
                else:
                    self.parent.status.include[i]=0
            else:
                # Ie 'Inner' shell
                if r<float(self.TextCtrl_sepnCutoff.GetValue()) and upperYCutoff>V2D and upperRCutoff>r:
                    #self.parent.export.append(exportRecord)
                    self.createExportRecord(primaryPointer, star2Pointer, i)
                    if self.V1D_CheckBox.GetValue()==True:
                        if dataTFBins.binAddDataPoint(x=M, y=vRA, dy=vRAerr, value=0):
                            self.parent.StatusBarProcessing(f'Exclude "vRAerr (b)" x={M}, y={vRA}')
                        if dataTFBins.binAddDataPoint(x=M, y=vDEC, dy=vDECerr, value=0) :
                            self.parent.StatusBarProcessing(f'Exclude "vDECerr (b)" x={M}, y={vDEC}')
                    else:
                        if dataTFBins.binAddDataPoint(x=M, y=V2D, dy=Verr, value=0) :
                            self.parent.status.include[i]=0
                            self.parent.StatusBarProcessing(f'Exclude "verr" x={M}, y={V2D}')
                else:
                    self.parent.status.include[i]=0
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle(f'bindata/{RELEASE}/{CATALOG}/export.saved')   
        xdata3TF=dataTFBins.getBinXArray(type='centre')
        ydata3TF=dataTFBins.getBinYArray(self.combo_yAvg.GetValue())
        rerrbin3TF=dataTFBins.getBinXVarArray()
        verrbin3TF=dataTFBins.getBinYVarArray(type='meanerror')
        print(verrbin3TF)
    
        self.line3TF = self.TulleyFPlot.axes.errorbar(x=xdata3TF, y=ydata3TF, xerr=rerrbin3TF, yerr=verrbin3TF, fmt='o', ecolor='r', elinewidth=2, capsize=0, mfc='r', mec='r', ms=3) #,label='Gaia binned'
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
        ####################################################################################################
        self.parent.binaryDetail['include']=self.parent.status['include']
        M=self.parent.binaryDetail.loc[(self.parent.binaryDetail['include'] > 0)]
        if self.V1D_CheckBox.GetValue()==True:
            xdata1 = M.M
            xdata1 = xdata1.append(M.M)
            ydata1 = M.vRA
            ydata1 = ydata1.append(M.vDEC)
        else:
            xdata1=M.M
            ydata1 = (M.vRA**2+ M.vDEC**2).apply(np.sqrt)
        self.parent.binaryDetail.drop(columns=['include'])
        
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
        
        self.TulleyFPlot.axes.grid(visible=1, which='both', axis='both')     
        
        marker = ','
        markersize=1
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
            markersize=1.5
        #self.TulleyFPlot.axes.set_xticklabels(['1.0x','1.2x','1.4x','1.6x','1.8x','2.0x','2.2x','2.4x'])
        
        if self.rawDataCheckBox.GetValue():
            self.line1, = self.TulleyFPlot.axes.plot(xdata1, ydata1, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
            if not prntVersion:
                legend1.append(self.line1)
                legend2.append('TF raw data')
                
            self.TulleyFPlot.draw(self.line1, xdata1, ydata1, True, [] )
                
        try:
            self.TulleyFPlot.Layout()
        except Exception:
            pass
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
        avgRuwe=self.CalcMeanXYoverDxy('RUWE',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgRuwe:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Distance')
        avgDIST=self.CalcMeanXYoverDxy('DIST',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgDIST:,}")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Binary Probability for single stars')
        avgProb=self.CalcMeanXYoverDxy('classprob_dsc_specmod_binarystar',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgProb:,}")
              
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Masses')
        avgMass=self.CalcPercentPairNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        
        rowCnt += 1 #Next row 
        self.summaryList.InsertItem(rowCnt, 'Fraction of FLAME Masses')
        avgMass=self.CalcPercentEitherNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Ages')
        avgAge=self.CalcPercentPairNotNull('age_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgAge*100:,} %")
        
        #Mean stellar mass 
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean individual stellar mass')        
        xdata1=pd.DataFrame(xdata1, columns=['M'])
        avg=xdata1['M'].sum()/(2*len(xdata1['M']))
        #avg=xdata1.M.mean() # Can't do this because of all the zeros.
        self.summaryList.SetItem(rowCnt, 1, f"{avg:,.2f}")
        
        #Mean stellar mass  * 2
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean binary mass')        
        xdata1=pd.DataFrame(xdata1, columns=['M'])
        avg=xdata1['M'].sum()/len(xdata1['M'])
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
            yHat_i=self.XreturnY(xLog10[i], self.slope, self.offset)
            yMinusYhatSum=yMinusYhatSum+(yLog10[i]-yHat_i)**2
            xMinusXbarSum=xMinusXbarSum+(xLog10[i]-xMeanLog10)**2
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, f'Slope confidence interval (1 sigma)')
        self.summaryList.SetItem(rowCnt, 1, f"{math.sqrt((yMinusYhatSum/xMinusXbarSum)/(n-2)):,.2f}")
                
        xdataLMS=[dataTFBins.binUpperBounds[0],dataTFBins.binLowerBounds[numTFBins-1]]
        ydataLMS=[10**self.XreturnY(math.log10(dataTFBins.binUpperBounds[0]), self.slope, self.offset),10**self.XreturnY(math.log10(dataTFBins.binLowerBounds[numTFBins-1]), self.slope,self.offset )]
        
        self.lineLMS, = self.TulleyFPlot.axes.plot(xdataLMS, ydataLMS, 'bo-', linewidth=2, markersize=1)
        
        if not prntVersion:
            legend1.append(self.lineLMS)
            legend2.append('LMS line')
        
        self.TulleyFPlot.axes.legend(legend1, legend2)
        if prntVersion:
            self.TulleyFPlot.axes.get_legend().remove()
        self.TulleyFPlot.axes.xaxis.set_major_locator(ticker.AutoLocator())
        self.TulleyFPlot.axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        
        self.TulleyFPlot.draw(self.lineLMS, xdataLMS, ydataLMS, True, [] )
        try:
            self.TulleyFPlot.Layout()
        except Exception:
            pass
        self.Layout()
        
        # Save pandas status file as pickle files for next time.
        try:
            self.parent.status.to_pickle(f'bindata/{RELEASE}/{CATALOG}/status.saved')
        except Exception:
            self.parent.StatusBarProcessing('Error directory failed to save')
            print (self.parent.status)

        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
        self.parent.printArrays()

        self.plot_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
class MassPlotting(masterProcessingPanel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=4, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings
        
        self.static_bins = StaticText(self, label='# bins') 
        fgsizer.Add(self.static_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xLower = StaticText(self, label='mass-lower') 
        fgsizer.Add(self.static_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xUpper = StaticText(self, label='mass-upper') 
        fgsizer.Add(self.static_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
     
        
        # Lower bin cutoff header
        lowerBinCutoff_StaticText = StaticText(self, id=wx.ID_ANY, label="Lower Bin cutoff")
        fgsizer.Add(lowerBinCutoff_StaticText, 0, wx.ALL, 2)
        
        # Axis limits
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','GAIAMASS', '5')))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer number of bins to divide x-scale into.")
        
        self.textctrl_xLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_lower','GAIAMASS', '1'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xLower.SetToolTip("Lower end of mass-scale.")
        self.textctrl_xLower.setValidRoutine(self.textctrl_xLower.Validate_Float)
        
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','GAIAMASS', '2'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of mass-scale.")
        self.textctrl_xUpper.setValidRoutine(self.textctrl_xUpper.Validate_Float)
        
        
        # Lower bin cutoff textctrl
        self.lowerBinCutoffTextCtrl = SpinCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('lower_bin_cutoff','GAIAMASS', '5')))  
        self.lowerBinCutoffTextCtrl.SetToolTip("Enter number below which not to display bins.")

        fgsizer.Add(self.lowerBinCutoffTextCtrl, 0, wx.ALL, 2)
        
        # Create show raw data check box
        rawDataStaticText = StaticText(self, id=wx.ID_ANY, label="Show raw data")
        fgsizer.Add(rawDataStaticText, 0, wx.ALL, 2)
        self.rawDataCheckBox = CheckBox(self)
        self.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata', 'GAIAMASS'))
        self.rawDataCheckBox.SetToolTip("Display raw data on graph.")
        fgsizer.Add(self.rawDataCheckBox, 0, wx.ALL, 2)

        # Create show labels line check box
        labelsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bins")
        fgsizer.Add(labelsStaticText, 0, wx.ALL, 2)
        self.showBinsCheckBox = CheckBox(self)
        self.showBinsCheckBox.SetValue(gl_cfg.getBoolean('showbinss', 'GAIAMASS'))
        self.showBinsCheckBox.SetToolTip("Show bins with labels on graph.")
        fgsizer.Add(self.showBinsCheckBox, 0, wx.ALL, 2)
        
        # Create show large data points
        largeStaticText = StaticText(self, id=wx.ID_ANY, label="Show large data points")
        fgsizer.Add(largeStaticText, 0, wx.ALL, 2)
        self.largePointsCheckBox = CheckBox(self)
        self.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints', 'GAIAMASS'))
        self.largePointsCheckBox.SetToolTip("Shows larger data points for stars on graph.")
        fgsizer.Add(self.largePointsCheckBox, 0, wx.ALL, 2)
        
        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print Version")
        fgsizer.Add(prntVersion_StaticText, 0, wx.ALL, 2)
        self.prntVersionCheckBox = CheckBox(self)
        self.prntVersionCheckBox.SetToolTip("Produce print version of graph.")
        self.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion', 'GAIAMASS'))
        fgsizer.Add(self.prntVersionCheckBox, 0, wx.ALL, 2)
        
        # Draw button
        
        self.plot_but = Button(self, id=wx.ID_OK, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Cancel Button
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel binning.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw velocity map
        try:
            self.MassPlot = matplotlibPanel(parent=self, size=(750, 750))
            self.MassPlot.axes.set_yscale('linear', nonpositive='clip')
            self.MassPlot.axes.set_xscale('linear', nonpositive='clip')
            fg2sizer.Add(self.MassPlot)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Metric", wx.LIST_FORMAT_RIGHT, width=280 )
        self.summaryList.SetColumnWidth(0, 280)
        self.summaryList.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, width=120 )
        self.summaryList.SetColumnWidth(1, 120)
        self.SetSizer(self.sizer_v)
        try:
            self.MassPlot.Layout()
        except Exception:
            pass
        self.Layout()

    def OnReset(self, event=0):
        self.parent.status['include']=self.parent.status['kineticOut']

    def OnPlot(self, event=0):

        self.parent.StatusBarProcessing('Gaia mass vs calculated mass plotting commenced')
        
        global CANCEL
        CANCEL = False
        wx.Yield()
        #self.parent.export=pd.DataFrame(columns=['SOURCE_ID_PRIMARY','ra1','dec1','mag1','SOURCE_ID_SECONDARY','ra2','dec2','mag2', 'vRA', 'vDEC', 'V2D', 'M', 'r'])
        self.parent.export=[]
        attributes=[self.textctrl_xLower, self.textctrl_xUpper]
        for attribute in attributes:
            if not attribute.runValidRoutine():
                return
        self.plot_but.Disable()
        
        gl_cfg.setItem('no_bins',self.spin_bins.GetValue(),'GAIAMASS')
        gl_cfg.setItem('x_lower',self.textctrl_xLower.GetValue(),'GAIAMASS')
        gl_cfg.setItem('x_upper',self.textctrl_xUpper.GetValue(),'GAIAMASS')

        gl_cfg.setItem('lower_bin_cutoff',self.lowerBinCutoffTextCtrl.GetValue(),'GAIAMASS')

        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        gl_cfg.setItem('rawdata',self.rawDataCheckBox.GetValue(), 'GAIAMASS') # save setting in config file
        gl_cfg.setItem('prntversion',self.prntVersionCheckBox.GetValue(), 'GAIAMASS') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'GAIAMASS') # save setting in config file
        gl_cfg.setItem('showbins',self.showBinsCheckBox.GetValue(), 'GAIAMASS') # save setting in config file
        self.OnReset()
        
        # To remove the artist
        for frame in self.MassPlot.frames:
            try:
                frame.remove()
            except Exception:
                pass
        try:
            self.line1.remove()
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
        
        self.MassPlot.set_limits([float(self.textctrl_xLower.GetValue()),float(self.textctrl_xUpper.GetValue())],[float(self.textctrl_xLower.GetValue()),float(self.textctrl_xUpper.GetValue())])
        
        prntVersion=self.prntVersionCheckBox.GetValue()
            
        lenArray=len(self.parent.binaryDetail)
        xdata1=[]
        ydata1=[]
        xdata2=[]
        ydata2=[]
        
        #
        # Convert Velocity data into bins
        #
#######################################################################

        top=float(self.textctrl_xUpper.GetValue())      #  Get top of range
        bottom=float(self.textctrl_xLower.GetValue())   #  Get bottom of range
        diff = top-bottom                               #  Work out difference 
######################################################################
        numBins=int(self.spin_bins.GetValue())      #  Get number of RA bins.
        dataBins=binOrganiser(numBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
        upper=top
        inc=diff/numBins
        lower=upper-inc
        for i in range(numBins):
            #if int(self.upperBinSplitSpinCtrl.GetValue())):
            dataBins.newBin(lower, upper)
            upper=lower
            lower=upper-inc
            
        #Filter out currently inluded rows only
        indexStatus = self.parent.status.index
        condition = self.parent.status.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        
        #Loop through binary values
        for i in statusIndicesList:
            
            if math.isnan(self.parent.status.include[i]) or not int(self.parent.status.include[i]):
                continue
            #else:
            #    include=int(self.parent.status.include[i])
            #Set up local variables to avoid repeated PD access and for clarity
            #if math.isnan(self.parent.binaryDetail.vRA[i]) :
            #    self.parent.StatusBarProcessing(f'i={i}, vRA = {self.parent.binaryDetail.vRA[i]}')
            #if math.isnan(self.parent.binaryDetail.vDEC[i]) :
            #    self.parent.StatusBarProcessing(f'i={i}, vDEC = {self.parent.binaryDetail.vDEC[i]}')
            #vRA=float(self.parent.binaryDetail.vRA[i])
            #vDEC=float(self.parent.binaryDetail.vDEC[i])
            #V2D=math.sqrt(vRA**2+vDEC**2)
            
            #r=float(self.parent.binaryDetail.r[i])
            #vRAerr=float(self.parent.binaryDetail.vRAerr[i])
            #vDECerr=float(self.parent.binaryDetail.vDECerr[i])
            #Verr=math.sqrt((vRA*vRAerr)**2+(vDEC*vDECerr)**2)/V2D
            #M=float(self.parent.binaryDetail.M[i])
            # Go through and bin
            label=float(100.0 * i /lenArray)
            self.plot_but.SetLabel(f'{label:,.1f}%')
            if CANCEL:
                CANCEL = False
                self.plot_but.Enable()
                return
            wx.Yield()
            

            primaryPointer=self.parent.X.iloc[i]
            star2Pointer=self.parent.Y.iloc[i]
            #primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
            #star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
            #primaryPointer=self.parent.X[str(i+1)]
            #star2Pointer=self.parent.Y[str(i+1)]
            #print(primaryPointer)
            #primaryPointer=pd.DataFrame(primaryPointer)
            #star2Pointer=pd.DataFrame(primaryPointer)
            ydata1.append(primaryPointer.mass_flame)
            ydata2.append(star2Pointer.mass_flame)
            xdata1.append(primaryPointer.mass_calc)
            xdata2.append(star2Pointer.mass_calc)
            #exportRecord={'SOURCE_ID_PRIMARY':str(primaryPointer.source_id),
            #    'ra1':float(primaryPointer.RA_),
            #    'dec1':float(primaryPointer.DEC_),
            #    'mag1':primaryPointer.phot_g_mean_mag,
            #    'MAG1':self.parent.X.mag[i],
            #    'PARALLAX1':float(primaryPointer.parallax),
            #    'parallax_error1':float(primaryPointer.parallax_error),
            #    'DIST1':float(primaryPointer.DIST),
            #    'RUWE1':primaryPointer.ruwe,
            #    'RUWE1':primaryPointer.ruwe,
            #    'PMRA1':float(primaryPointer.pmra),
            #    'PMRA_ERROR1':float(primaryPointer.pmra_error),
            #    'PMDEC1':float(primaryPointer.pmdec),
            #    'PMDEC_ERROR1':float(primaryPointer.pmdec_error),
            #    'BminusR1':float(primaryPointer.bp_rp),
            #    'mass_flame1':primaryPointer.mass_flame,
            #    'mass_flame_upper1':primaryPointer.mass_flame_upper,
            #    'mass_flame_lower1':primaryPointer.mass_flame_lower,
            #    'mass_calc1':primaryPointer.mass_calc,          
            #    'age_flame1':primaryPointer.age_flame,
            #    'age_flame_upper1':primaryPointer.age_flame_upper,
            #    'age_flame_lower1':primaryPointer.age_flame_lower,
            #    'PROB1':primaryPointer.classprob_dsc_specmod_binarystar,
            #    'SOURCE_ID_SECONDARY':str(star2Pointer.source_id),
            #    'ra2':float(star2Pointer.RA_),
            #    'dec2':float(star2Pointer.DEC_),
            #    'mag2':star2Pointer.phot_g_mean_mag,
            #    'MAG2':self.parent.Y.mag[i],
            #    'PARALLAX2':float(star2Pointer.parallax),
            #    'parallax_error2':float(star2Pointer.parallax_error),
            #    'DIST2':float(star2Pointer.DIST),
            #    'RUWE2':star2Pointer.ruwe,
            #    'PMRA2':float(star2Pointer.pmra),
            #    'PMRA_ERROR2':float(star2Pointer.pmra_error),
            #    'PMDEC2':float(star2Pointer.pmdec),
            #    'PMDEC_ERROR2':float(star2Pointer.pmdec_error),
            #    'BminusR2':float(star2Pointer.bp_rp),
            #    'mass_flame2':star2Pointer.mass_flame,
            #    'mass_flame_upper2':star2Pointer.mass_flame_upper,
            #    'mass_flame_lower2':star2Pointer.mass_flame_lower,
            #    'mass_calc2':star2Pointer.mass_calc,               
            #    'age_flame2':star2Pointer.age_flame,
            #    'age_flame_upper2':star2Pointer.age_flame_upper,
            #    'age_flame_lower2':star2Pointer.age_flame_lower,
            #    'PROB2':star2Pointer.classprob_dsc_specmod_binarystar,
            #    'vRA':self.parent.binaryDetail.vRA[i],
            #    'vRAerr':abs(self.parent.binaryDetail.vRAerr[i]),
            #    'vDEC':self.parent.binaryDetail.vDEC[i],
            #    'vDECerr':abs(self.parent.binaryDetail.vDECerr[i]),   
            #    'V2D':math.sqrt(self.parent.binaryDetail.vRA[i]**2+self.parent.binaryDetail.vDEC[i]**2),
            #    'DIST':(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2,
            #    'RA_MEAN':(float(primaryPointer.RA_)+float(star2Pointer.RA_))/2,
            #    'DEC_MEAN':(float(primaryPointer.DEC_)+float(star2Pointer.DEC_))/2,
            #    'Log10vRA':np.log10(self.parent.binaryDetail.vRA[i]),
            #    'Log10vDEC':np.log10(self.parent.binaryDetail.vDEC[i]),
            #    'Log10r':np.log10(abs(self.parent.binaryDetail.r[i])),
            #    #'rerr'(abs(self.parent.binaryDetail.r[i]),
            #    #'M':M,
            #    'r':self.parent.binaryDetail.r[i]
            #}
            #
            # Ie 'Outer' shell
            if float(primaryPointer.mass_flame) or float(star2Pointer.mass_flame):
                #self.parent.export.append(exportRecord)
                exportRecord=self.createExportRecord(primaryPointer, star2Pointer, i)
                if dataBins.binAddDataPoint(x=primaryPointer.mass_calc, y=primaryPointer.mass_flame, dy=(primaryPointer.age_flame_upper-primaryPointer.age_flame_lower)/2.0, value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "Calculated mass (a)" x={primaryPointer.mass_calc}, y={primaryPointer.mass_flame}')

            if float(star2Pointer.mass_flame):
                #self.parent.export.append(exportRecord)
                exportRecord=self.createExportRecord(primaryPointer, star2Pointer, i)
                if dataBins.binAddDataPoint(x=star2Pointer.mass_calc, y=star2Pointer.mass_flame, dy=(star2Pointer.age_flame_upper-star2Pointer.age_flame_lower)/2.0, value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "Calculated mass (b)" x={star2Pointer.mass_calc}, y={star2Pointer.mass_flame}')
        #print(self.parent.export)
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle(f'bindata/{RELEASE}/{CATALOG}/export.saved')   
        xdata3=dataBins.getBinXArray(type='mean')
        ydata3=dataBins.getBinYArray(type='mean')
        mCalcerrbin3=dataBins.getBinXVarArray()
        mGaiaerrbin3=dataBins.getBinYVarArray(type='var')
        #print(mGaiaerrbin3)
    
        if self.showBinsCheckBox.GetValue():
            self.line3 = self.MassPlot.axes.errorbar(x=xdata3, y=ydata3, xerr=mCalcerrbin3, yerr=mGaiaerrbin3, fmt='o', ecolor='r', elinewidth=2, capsize=0, mfc='r', mec='r', ms=3) #,label='Gaia binned'
            self.line3[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line3[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
            if not prntVersion:
                legend1.append(self.line3)
                legend2.append(f'Mass binned data')
            
            xScaleBy=1
            yScaleBy=1.05

            #    """
            #Attach a text label above each bar displaying its height
            #"""
            self.MassPlot.frames=[] 
            if prntVersion:
                c='black'
            else:
                c='white'
            for x,y,label in zip(xdata3, ydata3, dataBins.getBinYLabelArray()):
               self.MassPlot.frames.append(self.MassPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))
        
            self.MassPlot.draw(self.line3, xdata3, ydata3, False, [] )
        self.MassPlot.axes.set_xlabel('Calculated stellar mass ($M_{\odot}$)', fontsize=FONTSIZE)
        self.MassPlot.axes.set_ylabel('FLAME mass from Gaia ($M_{\odot}$)', fontsize=FONTSIZE)
        ####################################################################################################
        self.parent.binaryDetail['include']=self.parent.status['include']
        M=self.parent.binaryDetail.loc[(self.parent.binaryDetail['include'] > 0)]
        
        self.parent.starSystemList.binaryList[str(i+1)].primary
        
        #print(self.parent.starSystemList.binaryList)
        
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
            self.MassPlot.axes.set_title("")
            self.MassPlot.axes.patch.set_facecolor('1')  # White shade
        else:
            self.MassPlot.axes.set_title(f"Gaia {RELEASE}, FLAME mass vs calculated mass", fontsize=FONTSIZE)
            self.MassPlot.axes.patch.set_facecolor('0.25')  # Grey shade
        
        self.MassPlot.axes.grid(visible=1, which='both', axis='both')     
        
        marker = ','
        markersize=1
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
            markersize=1.5
        #self.MassPlot.axes.set_xticklabels(['1.0x','1.2x','1.4x','1.6x','1.8x','2.0x','2.2x','2.4x'])
        
        if self.rawDataCheckBox.GetValue():
            self.line1, = self.MassPlot.axes.plot(xdata1, ydata1, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
            if not prntVersion:
                legend1.append(self.line1)
                legend2.append('Primary raw data')
                
            self.MassPlot.draw(self.line1, xdata1, ydata1, True, [] )
                
            self.line2, = self.MassPlot.axes.plot(xdata2, ydata2, color='silver', marker=marker, linestyle='none', linewidth=0, markersize=markersize)
            if not prntVersion:
                legend1.append(self.line2)
                legend2.append('Secondary raw data')
                
            self.MassPlot.draw(self.line2, xdata2, ydata2, True, [] )
                
        try:
            self.MassPlot.Layout()
        except Exception:
            pass
        
        dataRange=[bottom, top]
        #print(dataRange)
        self.line4, = self.MassPlot.axes.plot(dataRange, dataRange, color='g', marker='o', linestyle='--', linewidth=1, markersize=markersize)
        if not prntVersion:
            legend1.append(self.line4)
            legend2.append('y = x')
            
        self.MassPlot.axes.legend(legend1, legend2)
        self.MassPlot.draw(self.line4, dataRange, dataRange, True, [] )

                
        #try:
        self.MassPlot.Layout()
        #except Exception:
        #    pass
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
        avgRuwe=self.CalcMeanXYoverDxy('RUWE',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgRuwe:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Distance')
        avgDIST=self.CalcMeanXYoverDxy('DIST',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgDIST:,}")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Binary Probability for single stars')
        avgProb=self.CalcMeanXYoverDxy('classprob_dsc_specmod_binarystar',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgProb:,}")
              
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Masses')
        avgMass=self.CalcPercentPairNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        
        rowCnt += 1 #Next row 
        self.summaryList.InsertItem(rowCnt, 'Fraction of FLAME Masses')
        avgMass=self.CalcPercentEitherNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Ages')
        avgAge=self.CalcPercentPairNotNull('age_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgAge*100:,} %")
        
        #
        self.MassPlot.axes.legend(legend1, legend2)
        if prntVersion:
            self.MassPlot.axes.get_legend().remove()

        try:
            self.MassPlot.Layout()
        except Exception:
            pass
        self.Layout()
        
        # Save pandas status file as pickle files for next time.
        try:
            self.parent.status.to_pickle(f'bindata/{RELEASE}/{CATALOG}/status.saved')
        except Exception:
            self.parent.StatusBarProcessing('Error directory failed to save')
            print (self.parent.status)

        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
        self.parent.printArrays()

        self.plot_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
    #def XreturnY(self, X):
    #    # Return lower outlier range.
    #    Y=self.slope*float(X) + self.offset
    #    return Y
class NumberDensityPlotting(masterProcessingPanel):

#Plot Density of stars by distance from Sol.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel= mainPanel
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=4, hgap=0, rows=6, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(fg2sizer)
        
        # Headings
        
        self.static_bins = StaticText(self, label='# bins') 
        fgsizer.Add(self.static_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.static_xLower = StaticText(self, label='x-lower') 
        #fgsizer.Add(self.static_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xUpper = StaticText(self, label='x-upper') 
        fgsizer.Add(self.static_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.static_yLower = StaticText(self, label='y-lower') 
        #fgsizer.Add(self.static_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yUpper = StaticText(self, label='y-upper') 
        fgsizer.Add(self.static_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #
        
        fgsizer.AddSpacer(1)
        # Axis limits
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','NUMBERDENSITY')))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer number of bins to divide x-scale into.")
        
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','NUMBERDENSITY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_xUpper.setValidRoutine(self.textctrl_xUpper.Validate_Float)
        #
        self.textctrl_yUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_upper','NUMBERDENSITY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yUpper.SetToolTip("Upper end of y-scale.")
        self.textctrl_yUpper.setValidRoutine(self.textctrl_yUpper.Validate_Float)
        #
        fgsizer.AddSpacer(1)
        
        # Create show 'Series 1' data check box
        Series1StaticText = StaticText(self, id=wx.ID_ANY, label="Initial Data Load Series")
        fgsizer.Add(Series1StaticText, 0, wx.ALL, 2)
        self.Series1CheckBox = CheckBox(self)
        self.Series1CheckBox.SetValue(gl_cfg.getBoolean('rawdata1', 'NUMBERDENSITY'))
        self.Series1CheckBox.SetToolTip("Display series 1 on graph.")
        fgsizer.Add(self.Series1CheckBox, 0, wx.ALL, 2)

        # Create show 'Series 2' data check box
        Series2StaticText = StaticText(self, id=wx.ID_ANY, label="Filtered Series")
        fgsizer.Add(Series2StaticText, 0, wx.ALL, 2)
        self.Series2CheckBox = CheckBox(self)
        self.Series2CheckBox.SetValue(gl_cfg.getBoolean('rawdata2', 'NUMBERDENSITY'))
        self.Series2CheckBox.SetToolTip("Display data initially loaded series on graph.")
        fgsizer.Add(self.Series2CheckBox, 0, wx.ALL, 2)

        # Create show 'Series 3' data check box
        Series3StaticText = StaticText(self, id=wx.ID_ANY, label="HR filtered Series")
        fgsizer.Add(Series3StaticText, 0, wx.ALL, 2)
        self.Series3CheckBox = CheckBox(self)
        self.Series3CheckBox.SetValue(gl_cfg.getBoolean('rawdata3', 'NUMBERDENSITY'))
        self.Series3CheckBox.SetToolTip("Display HR filtered series on graph.")
        fgsizer.Add(self.Series3CheckBox, 0, wx.ALL, 2)

        # Create show 'Series 4' data check box
        Series4StaticText = StaticText(self, id=wx.ID_ANY, label="Kinetic Filtered")
        fgsizer.Add(Series4StaticText, 0, wx.ALL, 2)
        self.Series4CheckBox = CheckBox(self)
        self.Series4CheckBox.SetValue(gl_cfg.getBoolean('rawdata4', 'NUMBERDENSITY'))
        self.Series4CheckBox.SetToolTip("Display kinetic filtered series on graph.")
        fgsizer.Add(self.Series4CheckBox, 0, wx.ALL, 2)

        # Create show labels line check box
        labelsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bin labels")
        fgsizer.Add(labelsStaticText, 0, wx.ALL, 2)
        self.showLabelsCheckBox = CheckBox(self)
        self.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels', 'NUMBERDENSITY'))
        self.showLabelsCheckBox.SetToolTip("Show labels above bins on graph.")
        fgsizer.Add(self.showLabelsCheckBox, 0, wx.ALL, 2)
        
        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print Version")
        fgsizer.Add(prntVersion_StaticText, 0, wx.ALL, 2)
        self.prntVersionCheckBox = CheckBox(self)
        self.prntVersionCheckBox.SetToolTip("Produce print version of graph.")
        self.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion', 'NUMBERDENSITY'))
        fgsizer.Add(self.prntVersionCheckBox, 0, wx.ALL, 2)
        
        # Draw button
        
        self.plot_but = Button(self, id=wx.ID_OK, label="&Plot", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.plot_but.Bind(wx.EVT_BUTTON, self.OnPlot)
        fgsizer.Add(self.plot_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Cancel Button
        self.button2 = Button(self, wx.ID_ANY, u"Cancel")
        self.button2.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.button2.SetToolTip("Cancel binning.")
        fgsizer.Add(self.button2, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw velocity map
        try:
            self.NumberDensityPlot = matplotlibPanel(parent=self, size=(1350, 750))
            fg2sizer.Add(self.NumberDensityPlot)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
        self.summaryList.InsertColumn(0, "Metric", wx.LIST_FORMAT_RIGHT, width=280 )
        self.summaryList.SetColumnWidth(0, 280)
        self.summaryList.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, width=120 )
        self.summaryList.SetColumnWidth(1, 120)
        self.SetSizer(self.sizer_v)
        try:
            self.NumberDensityPlot.Layout()
        except Exception:
            pass
        self.Layout()

        
    def OnReset(self, event=0):
        self.parent.status['include']=self.parent.status['kineticOut']

    def OnPlot(self, event=0):
       
        global CANCEL
        CANCEL = False
        self.parent.StatusBarProcessing('Number Density Plotting commenced')
        
        wx.Yield()
        #self.parent.export=[]
        attributes=[self.textctrl_xUpper, self.textctrl_yUpper]
        for attribute in attributes:
            if not attribute.runValidRoutine():
                return
        self.plot_but.Disable()
        
        gl_cfg.setItem('no_bins',self.spin_bins.GetValue(),'NUMBERDENSITY')
        gl_cfg.setItem('x_upper',self.textctrl_xUpper.GetValue(),'NUMBERDENSITY')
        gl_cfg.setItem('y_upper',self.textctrl_yUpper.GetValue(),'NUMBERDENSITY')

        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        gl_cfg.setItem('prntversion',self.prntVersionCheckBox.GetValue(), 'NUMBERDENSITY') # save setting in config file
        gl_cfg.setItem('showlabels',self.showLabelsCheckBox.GetValue(), 'NUMBERDENSITY') # save setting in config file
        gl_cfg.setItem('rawdata1', self.Series1CheckBox.GetValue(), 'NUMBERDENSITY')
        gl_cfg.setItem('rawdata2', self.Series2CheckBox.GetValue(), 'NUMBERDENSITY')
        gl_cfg.setItem('rawdata3', self.Series3CheckBox.GetValue(), 'NUMBERDENSITY')
        gl_cfg.setItem('rawdata4', self.Series4CheckBox.GetValue(), 'NUMBERDENSITY')
        self.OnReset()
        
        # To remove the artist
        for frame in self.NumberDensityPlot.frames:
            try:
                frame.remove()
            except Exception:
                pass
        try:
            self.line1.remove()
        except Exception:
            pass
        try:
            self.line1ND.remove()
        except Exception:
            pass

        try:
            self.line2ND.remove()
        except Exception:
            pass

        try:
            self.line3ND.remove()
        except Exception:
            pass

        try:
            self.line4ND.remove()
        except Exception:
            pass
        
        legend1=[] 
        legend2=[] 
        
        self.NumberDensityPlot.set_limits([0,float(self.textctrl_xUpper.GetValue())],[0,float(self.textctrl_yUpper.GetValue())])
        
        prntVersion=self.prntVersionCheckBox.GetValue()
            
        lenArray=len(self.parent.binaryDetail)

        
        #
        # Convert Velocity data into bins
        #
#######################################################################

        top=float(self.textctrl_xUpper.GetValue())      #  Get top of range
        bottom=0.0   #  Get bottom of range
        diff = top-bottom                               #  Work out difference in linnear not log terms.
######################################################################
        numNDBins=int(self.spin_bins.GetValue())      #  Get number of bins.
        dataNDBins1=binOrganiser(numNDBins, 1)
        upper=top
        factor=float(diff/numNDBins)
        lower=upper-factor
        for i in range(numNDBins):
            dataNDBins1.newBin(lower, upper)
            upper=lower
            lower=upper-factor
            
        dataNDBins2=binOrganiser(numNDBins, 1)
        upper=top
        factor=float(diff/numNDBins)
        lower=upper-factor
        for i in range(numNDBins):
            dataNDBins2.newBin(lower, upper)
            upper=lower
            lower=upper-factor
            
        dataNDBins3=binOrganiser(numNDBins, 1)
        upper=top
        factor=float(diff/numNDBins)
        lower=upper-factor
        for i in range(numNDBins):
            dataNDBins3.newBin(lower, upper)
            upper=lower
            lower=upper-factor
            
        dataNDBins4=binOrganiser(numNDBins, 1)
        upper=top
        factor=float(diff/numNDBins)
        lower=upper-factor
        for i in range(numNDBins):
            dataNDBins4.newBin(lower, upper)
            upper=lower
            lower=upper-factor
        # Initial data (Red, 1)
        if self.Series1CheckBox.GetValue():
            #Select Intial Data Loaded
            indexStatus = self.parent.status.index
            condition = self.parent.status.dataLoadOut == True
            statusIndices = indexStatus[condition]
            statusIndicesList = statusIndices.tolist()
            
            #Loop through binary values
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.dataLoadOut[i]) or not int(self.parent.status.dataLoadOut[i]):
                    continue
    
                primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2

                #primaryPointer=self.parent.X[str(i+1)]
                #star2Pointer=self.parent.Y[str(i+1)]
                #Set up local variables to avoid repeated PD access and for clarity
                DIST=(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2
    
                # Go through and bin
                label=float(100.0 * i /lenArray)
                self.plot_but.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    self.plot_but.Enable()
                    return
                wx.Yield()
                if dataNDBins1.binAddDataPoint(x=DIST, y=1, dy=.00011, value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "vRAerr (c)" x={DIST}, y=1')
    
            xdata1ND=dataNDBins1.getBinXArray(type='centre')
            ydata1ND=dataNDBins1.getBinYLabelArray()
            rerrbin1ND=dataNDBins1.getBinXVarArray()
            verrbin1ND=dataNDBins1.getBinYVarArray(type='meanerror')
        
            self.line1ND = self.NumberDensityPlot.axes.errorbar(x=xdata1ND, y=ydata1ND, xerr=rerrbin1ND, yerr=verrbin1ND, fmt='o', ecolor='r', elinewidth=2, capsize=0, mfc='r', mec='r', ms=3) #,label='Gaia binned'
            self.line1ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line1ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
            # Second tab data (Yellow, 2)
            
        if self.Series2CheckBox.GetValue():
            #Select Intial Data Loaded minus S/N filters, velocity filters and Distance filter
            indexStatus = self.parent.status.index
            condition = self.parent.status.populateOut == True
            statusIndices = indexStatus[condition]
            statusIndicesList = statusIndices.tolist()
            
            #Loop through binary values
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.populateOut[i]) or not int(self.parent.status.populateOut[i]):
                    continue
    
                primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
                #Set up local variables to avoid repeated PD access and for clarity
                DIST=(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2
    
                # Go through and bin
                label=float(100.0 * i /lenArray)
                self.plot_but.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    self.plot_but.Enable()
                    return
                wx.Yield()
                if dataNDBins2.binAddDataPoint(x=DIST, y=1, dy=.00011, value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "vRAerr (d)" x={DIST}, y=1')
    
            xdata2ND=dataNDBins2.getBinXArray(type='centre')
            ydata2ND=dataNDBins2.getBinYLabelArray()
            rerrbin2ND=dataNDBins2.getBinXVarArray()
            verrbin2ND=dataNDBins2.getBinYVarArray(type='meanerror')
        
            self.line2ND = self.NumberDensityPlot.axes.errorbar(x=xdata2ND, y=ydata2ND, xerr=rerrbin2ND, yerr=verrbin2ND, fmt='o', ecolor='y', elinewidth=2, capsize=0, mfc='y', mec='y', ms=3) #,label='Gaia binned'
            self.line2ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line2ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
        if self.Series3CheckBox.GetValue():
            #Select H-R filtered rows only
            indexStatus = self.parent.status.index
            condition = self.parent.status.hrOut == True
            statusIndices = indexStatus[condition]
            statusIndicesList = statusIndices.tolist()
            
            #Loop through binary values
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.hrOut[i]) or not int(self.parent.status.hrOut[i]):
                    continue
    
                primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
                #Set up local variables to avoid repeated PD access and for clarity
                DIST=(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2
    
                # Go through and bin
                label=float(100.0 * i /lenArray)
                self.plot_but.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    self.plot_but.Enable()
                    return
                wx.Yield()
                if dataNDBins3.binAddDataPoint(x=DIST, y=1, dy=.00011, value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "vRAerr (e)" x={DIST}, y=1')
    
            xdata3ND=dataNDBins3.getBinXArray(type='centre')
            ydata3ND=dataNDBins3.getBinYLabelArray()
            rerrbin3ND=dataNDBins3.getBinXVarArray()
            verrbin3ND=dataNDBins3.getBinYVarArray(type='meanerror')
        
            self.line3ND = self.NumberDensityPlot.axes.errorbar(x=xdata3ND, y=ydata3ND, xerr=rerrbin3ND, yerr=verrbin3ND, fmt='o', ecolor='g', elinewidth=2, capsize=0, mfc='g', mec='g', ms=3) #,label='Gaia binned'
            self.line3ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line3ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
        if self.Series4CheckBox.GetValue():
            #Select Kinetic filtered rows only
            indexStatus = self.parent.status.index
            condition = self.parent.status.kineticOut == True
            statusIndices = indexStatus[condition]
            statusIndicesList = statusIndices.tolist()
            
            #Loop through binary values
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.kineticOut[i]) or not int(self.parent.status.kineticOut[i]):
                    continue
    
                primaryPointer=self.parent.starSystemList.binaryList[str(i+1)].primary
                star2Pointer=self.parent.starSystemList.binaryList[str(i+1)].star2
                #primaryPointer=self.parent.X[str(i+1)]
                #star2Pointer=self.parent.Y[str(i+1)]
                #Set up local variables to avoid repeated PD access and for clarity
                DIST=(float(primaryPointer.DIST)+float(star2Pointer.DIST))/2
    
                # Go through and bin
                label=float(100.0 * i /lenArray)
                self.plot_but.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    self.plot_but.Enable()
                    return
                wx.Yield()
                if dataNDBins4.binAddDataPoint(x=DIST, y=1, dy=.00011, value=0) :
                    self.parent.StatusBarProcessing(f'Exclude 1 pair "vRAerr (f)" Distance={DIST}')
    
            xdata4ND=dataNDBins4.getBinXArray(type='centre')
            ydata4ND=dataNDBins4.getBinYLabelArray()
            rerrbin4ND=dataNDBins4.getBinXVarArray()
            verrbin4ND=dataNDBins4.getBinYVarArray(type='meanerror')
        
            self.line4ND = self.NumberDensityPlot.axes.errorbar(x=xdata4ND, y=ydata4ND, xerr=rerrbin4ND, yerr=verrbin4ND, fmt='o', ecolor='b', elinewidth=2, capsize=0, mfc='b', mec='b', ms=3) #,label='Gaia binned'
            self.line4ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line4ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
        
        #if not prntVersion:
        #    legend1=[self.line1ND, self.line2ND, self.line3ND, self.line4ND]
        #    legend2=[f'Total Unfiltered.', f'S/N & Distance Filtered.', f'HR Filtered.', f'Kinetic Filtered']

        
        xScaleBy=1
        yScaleBy=1.05

        if self.showLabelsCheckBox.GetValue():
            #    """
            #Attach a text label above each bar displaying its height
            #"""
            self.NumberDensityPlot.frames=[] 
            if prntVersion:
                c='black'
            else:
                c='white'
            if self.Series1CheckBox.GetValue():
                legend1.append(self.line1ND)
                legend2.append(f'Total Unfiltered.')

                for x,y,label in zip(xdata1ND, ydata1ND, dataNDBins1.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))

            if self.Series2CheckBox.GetValue():
                legend1.append(self.line2ND)
                legend2.append(f'S/N & Distance Filtered.')
                for x,y,label in zip(xdata2ND, ydata2ND, dataNDBins2.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))

            if self.Series3CheckBox.GetValue():
                legend1.append(self.line3ND)
                legend2.append(f'HR Filtered.')
                for x,y,label in zip(xdata3ND, ydata3ND, dataNDBins3.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))

            if self.Series4CheckBox.GetValue():
                legend1.append(self.line4ND)
                legend2.append(f'Kinetic Filtered.')
                for x,y,label in zip(xdata4ND, ydata4ND, dataNDBins4.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*.8, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE))

        self.NumberDensityPlot.axes.set_xlabel('Distance from Sol (pc)', fontsize=FONTSIZE)

        self.NumberDensityPlot.axes.set_ylabel(f'Star count', fontsize=FONTSIZE)

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
            self.NumberDensityPlot.axes.set_title("")
            self.NumberDensityPlot.axes.patch.set_facecolor('1')  # White shade
        else:
            self.NumberDensityPlot.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,} binary stars, Gaia {RELEASE}, star density by distance.", fontsize=FONTSIZE)
            self.NumberDensityPlot.axes.patch.set_facecolor('0.25')  # Grey shade
        
        self.NumberDensityPlot.axes.grid(visible=1, which='both', axis='both')     
        
        
        if not prntVersion:
            self.NumberDensityPlot.axes.legend(legend1, legend2)
        if prntVersion:
            self.NumberDensityPlot.axes.get_legend().remove()
        self.NumberDensityPlot.axes.xaxis.set_major_locator(ticker.AutoLocator())
        self.NumberDensityPlot.axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        
        self.NumberDensityPlot.drawLinear()
        try:
            self.NumberDensityPlot.Layout()
        except Exception:
            pass
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
        avgRuwe=self.CalcMeanXYoverDxy('RUWE',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgRuwe:,}")
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Distance')
        avgDIST=self.CalcMeanXYoverDxy('DIST',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgDIST:,}")

        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Mean Binary Probability for single stars')
        avgProb=self.CalcMeanXYoverDxy('classprob_dsc_specmod_binarystar',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgProb:,}")
              
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Masses')
        avgMass=self.CalcPercentPairNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        
        rowCnt += 1 #Next row 
        self.summaryList.InsertItem(rowCnt, 'Fraction of FLAME Masses')
        avgMass=self.CalcPercentEitherNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")
        
        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Ages')
        avgAge=self.CalcPercentPairNotNull('age_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgAge*100:,} %")
        try:
            self.NumberDensityPlot.Layout()
        except Exception:
            pass
        self.Layout()
        self.parent.printArrays()
        
        # Save pandas status file as pickle files for next time.
        try:
            self.parent.status.to_pickle(f'bindata/{RELEASE}/{CATALOG}/status.saved')
        except Exception:
            self.parent.StatusBarProcessing('Error directory failed to save')
            print (self.parent.status)

        # adding exception handling
        try:
            cp('binClient.conf', f'bindata/{RELEASE}/{CATALOG}/binClient.conf')
        except IOError as e:
            print("Unable to copy file. %s" % e)
            #exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
             
        self.parent.StatusBarNormal('Completed OK')
        self.plot_but.Enable()
        
    
    #def XreturnY(self, X):
    #    # Return lower outlier range.
    #    Y=self.slope*float(X) + self.offset
    #    return Y
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
        
        self.sec_but = Button(self, id=wx.ID_ANY, label="&Mark", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.sec_but.Bind(wx.EVT_BUTTON, self.onCompanionStar)
        fgsizer.Add(self.sec_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Draw button
        
        self.cat_but = Button(self, id=wx.ID_ANY, label="&Gaia DR3 catalogue", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.cat_but.Bind(wx.EVT_BUTTON, self.onGaiaCatalogue)
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
        self.summaryList.SetColumnWidth(0, 130)
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
            self.parent.StatusBarProcessing('Sort failed')
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
    def onGaiaCatalogue(self, event=0):
    
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        binaryIdx = self.binaryList.GetNextSelected(-1)
        if hasattr(self,'exportDisplay'):
            binaryROW=self.exportDisplay.iloc[binaryIdx]
            coords=str(binaryROW.ra1) + ', ' + str(binaryROW.dec1)
        
        self.onRefreshPage(coords, '' , True)
        
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
            coords=str(binaryROW.ra1) + ', ' + str(binaryROW.dec1)
            coords2=str(binaryROW.ra2) + ', ' + str(binaryROW.dec2)
            
        self.AddStats(binaryROW)
        
        self.onRefreshPage(coords, coords2)
    def AddStats(self, binaryROW):
        print(binaryROW)
        self.summaryList.DeleteAllItems()
        self.summaryList.Append(['SOURCE_ID',str(binaryROW.SOURCE_ID_PRIMARY),str(binaryROW.SOURCE_ID_SECONDARY)])
        self.summaryList.Append(['RA',self.returnRounded(binaryROW.ra1,4),self.returnRounded(binaryROW.ra2,4)])
        self.summaryList.Append(['DEC',self.returnRounded(binaryROW.dec1,4),self.returnRounded(binaryROW.dec2,4)])
        self.summaryList.Append(['mag',self.returnRounded(binaryROW.mag1,4),self.returnRounded(binaryROW.mag2,4)])
        self.summaryList.Append(['MAG',self.returnRounded(binaryROW.MAG1,4),self.returnRounded(binaryROW.MAG2,4)])
        self.summaryList.Append(['PARALLAX',self.returnRounded(binaryROW.PARALLAX1,4),self.returnRounded(binaryROW.PARALLAX2,4)])
        self.summaryList.Append(['PARALLAX err',self.returnRounded(binaryROW.parallax_error1,4),self.returnRounded(binaryROW.parallax_error2,4)])
        self.summaryList.Append(['PMRA',self.returnRounded(binaryROW.PMRA1,4),self.returnRounded(binaryROW.PMRA2,4)])
        self.summaryList.Append(['PMRA_ERROR',self.returnRounded(binaryROW.PMRA_ERROR1,4),self.returnRounded(binaryROW.PMRA_ERROR2,4)])
        self.summaryList.Append(['PMDEC',self.returnRounded(binaryROW.PMDEC1,4),self.returnRounded(binaryROW.PMDEC2,4)])
        self.summaryList.Append(['PMDEC_ERROR',self.returnRounded(binaryROW.PMDEC_ERROR1,4),self.returnRounded(binaryROW.PMDEC_ERROR2,4)])
        self.summaryList.Append(['BminusR',self.returnRounded(binaryROW.BminusR1,4),self.returnRounded(binaryROW.BminusR2,4)])
        self.summaryList.Append(['DIST',self.returnRounded(binaryROW.DIST1,4),self.returnRounded(binaryROW.DIST2,4)])
        self.summaryList.Append(['RUWE',self.returnRounded(binaryROW.RUWE1,4),self.returnRounded(binaryROW.RUWE2,4)])
        self.summaryList.Append(['mass_flame',self.returnRounded(binaryROW.mass_flame1,4),self.returnRounded(binaryROW.mass_flame2,4)])
        self.summaryList.Append(['mass_flame_upper',self.returnRounded(binaryROW.mass_flame_upper1,4),self.returnRounded(binaryROW.mass_flame_upper2,4)])
        self.summaryList.Append(['mass_flame_lower',self.returnRounded(binaryROW.mass_flame_lower1,4),self.returnRounded(binaryROW.mass_flame_lower2,4)])
        self.summaryList.Append(['age_flame',self.returnRounded(binaryROW.age_flame1,4),self.returnRounded(binaryROW.age_flame2,4)])
        self.summaryList.Append(['age_flame_upper',self.returnRounded(binaryROW.age_flame_upper1,4),self.returnRounded(binaryROW.age_flame_upper2,4)])
        self.summaryList.Append(['age_flame_lower',self.returnRounded(binaryROW.age_flame_lower1,4),self.returnRounded(binaryROW.age_flame_lower2,4)])
        self.summaryList.Append(['Bin Prob',self.returnRounded(binaryROW.PROB1,4),self.returnRounded(binaryROW.PROB2,4)])
        self.summaryList.Append(['Separation',self.returnRounded(binaryROW.r,4),''])
        self.summaryList.Append(['vRA',self.returnRounded(binaryROW.vRA,4),''])
        self.summaryList.Append(['vDEC',self.returnRounded(binaryROW.vDEC,4),''])
        self.summaryList.Append(['V2D',self.returnRounded(binaryROW.V2D,4),''])
        self.summaryList.Append(['DIST',self.returnRounded(binaryROW.DIST,4),''])
        self.summaryList.Append(['RA_MEAN',self.returnRounded(binaryROW.RA_MEAN,4),''])
        self.summaryList.Append(['Log10vRA',self.returnRounded(binaryROW.Log10vRA,4),''])
        self.summaryList.Append(['Log10vDEC',self.returnRounded(binaryROW.Log10vDEC,4),''])
        self.summaryList.Append(['Log10r',self.returnRounded(binaryROW.Log10r,4),''])
    
    def returnRounded(self, inStr, digits=4):
        out=inStr
        try:
            out = round(inStr, digits)
        except Exception:
            pass
        return out
    
    def onRefreshPage(self, coords='319.248057505893, -53.8355296313695', coords2='', gaiaMarker=0):
        # Options:
        #    coords=main star
        #    coords2=secondary star
        #    gaiaMarker=YorN
        newJava=''
        if gaiaMarker:
            newJava='''
        aladin.addCatalog(A.catalogFromVizieR('I/355/gaiadr3', '%s', 0.2, {shape: 'square', sourceSize: 8, color: 'red', onClick: 'showPopup'}));
            ''' % coords
            
        if len(coords2):
            newJava='''
        var marker1 = A.marker(%s, {popupTitle: 'Main', popupDesc: 'Object type: Main Star in pair'});
        var marker2 = A.marker(%s, {popupTitle: 'Second', popupDesc: 'Object type: Companion Star in pair'});
        var markerLayer = A.catalog({color: '#800080', sourceSize: 18});
        aladin.addCatalog(markerLayer);
        markerLayer.addSources([marker1, marker2]);
            ''' % (coords, coords2)

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
        <input id="DSS" type="radio" name="survey" value="P/DSS2/color" checked><label for="DSS">DSS color<label>
        <!-- <input id="DSS-blue" type="radio" name="survey" value="P/DSS2/blue"><label for="DSS-blue">DSS blue<label> -->
        <input id="2MASS" type="radio" name="survey" value="P/2MASS/color"><label for="2MASS">2MASS<label>
        <input id="allwise" type="radio" name="survey" value="P/allWISE/color"><label for="allwise">AllWISE<label>
        <input id="GALEX" type="radio" name="survey" value="P/GALEXGR6/AIS/color"><label for="GALEX">GALEX<label>
        <!-- <input id="glimpse" type="radio" name="survey" value="P/GLIMPSE360"><label for="glimpse">GLIMPSE 360<label> -->
        <!-- <input id="Fermi" type="radio" name="survey" value="P/Fermi/color"><label for="Fermi">Fermi<label> -->
        <!-- <input id="IRIS" type="radio" name="survey" value="P/IRIS/color"><label for="IRIS">IRIS<label> -->

    <!-- Aladin Lite JS code -->
    <script type="text/javascript" src="http://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.js" charset="utf-8"></script>

    <!-- Creation of Aladin Lite instance with initial parameters -->
    <script type="text/javascript">
        var aladin = A.aladin('#aladin-lite-div', {survey: "P/DSS2/color", fov:0.25, target: "%s"});
        $('input[name=survey]').change(function() {
            aladin.setImageSurvey($(this).val());
        });
        %s
  
    </script>
  </body>
</html>
        ''' % (coords, newJava)
        
        print (data)
        hostname = "aladin.u-strasbg.fr" #example
        response = os.system("ping -c 1 " + hostname)
        #and then check the response...
        if response == 0:
            self.cosmicBrowser.SetPage(data,"")
            self.parent.StatusBarProcessing(hostname+' available.')
        else:
            self.parent.StatusBarProcessing(hostname+' not available!')

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
        self.axes.grid(visible=1, which='major', axis='both')
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
        
    def drawLinear(self):

        #if hasattr(self.parent, 'combo_yLog') and self.parent.combo_yLog.GetValue()=='log':
        #    self.axes.set_yscale('log', nonpositive='clip')
        #else:
        self.axes.set_xscale('linear')
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