#!/usr/bin/env python
import traceback
import os
import time
#import  wx.lib.scrolledpanel as scrolled

#import wx.html2 # pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
import wx.html2 as webview

# WebView Backends
backends = [
    (webview.WebViewBackendEdge, 'WebViewBackendEdge'),
    (webview.WebViewBackendIE, 'WebViewBackendIE'),
    (webview.WebViewBackendWebKit, 'WebViewBackendWebKit'),
    (webview.WebViewBackendDefault, 'WebViewBackendDefault'),
]
import pandas as pd # pip3 install pandas pip install dask[dataframe]

import ashla.data_access as da #pip install astroquery
import ashla.data_access.binary_data 
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
from matplotlib.colors import ListedColormap, BoundaryNorm
import csv
import pickle
from wxPyControls import *
from PyBins4 import *
from starSystems_v5 import *
from newtonian_values import xdata2, ydata2, ydata2_1D

from astropy_healpix import HEALPix # pip3 install astropy_healpix
import healpy as hp  #pip3 install healpy
from astropy.coordinates import Galactic, SkyCoord # pip3 install astropy
import astropy.units as u

import re
import configVar

from matplotlib.ticker import (MultipleLocator, NullFormatter, ScalarFormatter, AutoMinorLocator, FormatStrFormatter)

from astroquery.gaia import Gaia # pip3 install astroquery
from shutil import copyfile as cp

import argparse

from scipy.special import erf, erfinv
from scipy.stats import chi2
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

FONTSIZE = int(gl_cfg.getItem('fontsize','SETTINGS', 20))
FONTSIZE2 = int(gl_cfg.getItem('fontsize2','SETTINGS', 14))
#Cancel command for import button
CANCEL=False 
import SQLLib
import db_v3                    # For bianary database.
dbiStro=db_v3.db()
database = gl_cfg.getItem('database','SETTINGS')
print(database)
iStro=dbiStro.conSQLite(database) 

from sqlalchemy import create_engine # pip3 install sqlalchemy
encoding='UTF8'
engine = create_engine('sqlite:///bynary_db_v2.db', echo=True) # , encoding=encoding)
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


## Reads user parameters
#def parser():
parser = argparse.ArgumentParser(
    prog = 'wxBinary',
    description = 'Application to download Binaries from Gaia and process.'
)

# Parsing options (observer)
parser.add_argument('-i', help = 'Ignore saved data', action = 'store_true', dest = 'ignore_saved')

args = parser.parse_args()

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
        self.nb.releasePage = gaiaStarRetrieval(self.nb, self)
        self.nb.catalogPage = gaiaBinaryRetrieval(self.nb, self)
        self.nb.retrievalPage = dataRetrieval(self.nb, self)
        self.nb.filterPage = dataFilter(self.nb, self)
        self.nb.plottingPage = kineticDataPlotting(self.nb, self)
        self.nb.skyPage = skyDataPlotting(self.nb, self)
        self.nb.hrPage = HRDataPlotting(self.nb, self)
        self.nb.GaiaMassPage = MassPlotting(self.nb, self)
        self.nb.TulleyFisherPage = TFDataPlotting(self.nb, self)
        self.nb.NumberDensityPage = NumberDensityPlotting(self.nb, self)
        #NumberDensityPlotting
        try:
            self.nb.AladinPage = AladinView(self.nb, self)
        except Exception as e:
            print("Error. %s" % e)

#
#       add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.nb.releasePage, "Download stars and attributes")
        self.nb.AddPage(self.nb.catalogPage, "Download binary catalogue")
        self.nb.AddPage(self.nb.retrievalPage, "Load Binary catalogue")
        self.nb.AddPage(self.nb.filterPage, "Apply binary filters")
        self.nb.AddPage(self.nb.skyPage, "Sky density plot")
        self.nb.AddPage(self.nb.hrPage, "H-R plot")
        self.nb.AddPage(self.nb.plottingPage, "Kinematic plot")
        self.nb.AddPage(self.nb.GaiaMassPage, "Est Mass vs FLAME Mass plot")
        self.nb.AddPage(self.nb.TulleyFisherPage, "Velocity vs Mass plot")
        self.nb.AddPage(self.nb.NumberDensityPage, "Star Density vs Distance plot")

        try:
            self.nb.AddPage(self.nb.AladinPage, "View Binaries in Aladin Lite")
        except Exception as e:
            print("Error. %s" % e)

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
            #print(f'{t} | {text}')
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
        static_Rp_err = StaticText(self, id=wx.ID_ANY, label="RP/err:")
        self.sizer_h.Add(static_Rp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err','GAIASTAR'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err', 'GAIASTAR',0)))  
        self.sizer_h.Add(self.spin_Rp_err, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err.SetToolTip("phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err = StaticText(self, id=wx.ID_ANY, label="BP/err:")
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
        screen = Display()
        diff = int(1080 - screen.screen_height)
        ctrl_height = 700-diff
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(565,ctrl_height), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
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
        
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel import or status update.")
        self.sizer_v2.Add(self.cancel, 0, wx.LEFT | wx.RIGHT , 5)
        
        self.deleteSelection = Button(self, id=wx.ID_ANY, label="Delete", pos=wx.DefaultPosition,size=wx.DefaultSize)
        #self.deleteSelection.Bind(wx.EVT_BUTTON, self.OnDeleteSelection)
        self.deleteSelection.SetToolTip("Delete binaries with that combination of 'release', 'catalogue', and 'healpix/RA/dec'")
        self.sizer_v2.Add(self.deleteSelection, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
    def OnCancel(self, event=0):
    
        global CANCEL
        self.button1.Enable()
        CANCEL= True
        
        self.parent.StatusBarNormal('Completed OK')
    #
    def index_not_exists(self, index_name, table_name, column_name):
        check_index_sql = f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}';"
        cursor = iStro.cursor()
        cursor.execute(check_index_sql)
        result = cursor.fetchone()
    
        if result:
            # Index exists, return False
            return False
        else:
            # Index does not exist, return True
            return True
            
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
            create_table_sql = '''
                CREATE TABLE IF NOT EXISTS "TBL_OBJECTS" (
                    "RELEASE_" TEXT,
                    "source_id" BIGINT,
                    "index" BIGINT,
                    "RA_" FLOAT,
                    "ra_error" FLOAT,
                    "DEC_" FLOAT,
                    "dec_error" FLOAT,
                    "parallax" FLOAT,
                    "parallax_error" FLOAT,
                    "phot_g_mean_mag" FLOAT,
                    "bp_rp" FLOAT,
                    "radial_velocity" FLOAT,
                    "radial_velocity_error" FLOAT,
                    "parallax_over_error" FLOAT,
                    "phot_g_mean_flux_over_error" FLOAT,
                    "phot_rp_mean_flux_over_error" FLOAT,
                    "phot_bp_mean_flux_over_error" FLOAT,
                    "pmra" FLOAT,
                    "pmra_error" FLOAT,
                    "pmdec" FLOAT,
                    "pmdec_error" FLOAT,
                    "ruwe" FLOAT,
                    "mass_flame" FLOAT,
                    "mass_flame_upper" FLOAT,
                    "mass_flame_lower" FLOAT,
                    "age_flame" FLOAT,
                    "age_flame_upper" FLOAT,
                    "age_flame_lower" FLOAT,
                    "classprob_dsc_specmod_binarystar" FLOAT,
                    "ra_dec_corr" REAL,
                    "ra_parallax_corr" REAL,
                    "ra_pmra_corr" REAL,
                    "ra_pmdec_corr" REAL,
                    "dec_parallax_corr" REAL,
                    "dec_pmra_corr" REAL,
                    "dec_pmdec_corr" REAL,
                    "parallax_pmra_corr" REAL,
                    "parallax_pmdec_corr" REAL,
                    "pmra_pmdec_corr" REAL,
                    "phot_bp_mean_flux" REAL,
                    "phot_rp_mean_flux" REAL,
                    "phot_bp_mean_flux_error" REAL,
                    "phot_rp_mean_flux_error" REAL,
                    PRIMARY KEY("RELEASE_", "source_id")
                );
                '''
            TBL_RELEASE.executeIAD(create_table_sql);

            TBL_OBJECTS  = SQLLib.sql(iStro, "TBL_OBJECTS ")
            #    #ALTER INDEX IDX_TBL_OBJECTS1 to 4 ACTIVE
            if self.index_not_exists('IDX_TBL_OBJECTS1', 'TBL_OBJECTS', 'SOURCE_ID'):
                SQL=f"CREATE INDEX IDX_TBL_OBJECTS1 ON TBL_OBJECTS (SOURCE_ID);"
                TBL_OBJECTS .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_OBJECTS2', 'TBL_OBJECTS', 'PARALLAX'):
                SQL=f"CREATE INDEX IDX_TBL_OBJECTS2 ON TBL_OBJECTS (PARALLAX);"
                TBL_OBJECTS .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_OBJECTS3', 'TBL_OBJECTS', 'RA_'):
                SQL=f"CREATE INDEX IDX_TBL_OBJECTS3 ON TBL_OBJECTS (RA_);"
                TBL_OBJECTS .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_OBJECTS4', 'TBL_OBJECTS', 'DEC_'):
                SQL=f"CREATE INDEX IDX_TBL_OBJECTS4 ON TBL_OBJECTS (DEC_);"
                TBL_OBJECTS .executeIAD(SQL)
                
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
            
            TBL_BINARIES  = SQLLib.sql(iStro, "TBL_BINARIES ")
            if self.index_not_exists('IDX_TBL_BINARIES1', 'TBL_BINARIES', 'RELEASE_, CATALOG, SOURCE_ID_PRIMARY'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES1 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_PRIMARY);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES2', 'TBL_BINARIES', 'RELEASE_, CATALOG, SOURCE_ID_SECONDARY'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES2 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_SECONDARY);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES3', 'TBL_BINARIES', 'RELEASE_, CATALOG, NOT_GROUPED'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES3 ON TBL_BINARIES (RELEASE_, CATALOG, NOT_GROUPED);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES4', 'TBL_BINARIES', 'RELEASE_, CATALOG, HAS_RADIAL_VELOCITY'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES4 ON TBL_BINARIES (RELEASE_, CATALOG, HAS_RADIAL_VELOCITY);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES5', 'TBL_BINARIES', 'NOT_GROUPED'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES5 ON TBL_BINARIES (NOT_GROUPED);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES6', 'TBL_BINARIES', 'HAS_RADIAL_VELOCITY'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES6 ON TBL_BINARIES (HAS_RADIAL_VELOCITY);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES7', 'TBL_BINARIES', 'RELEASE_'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES7 ON TBL_BINARIES (RELEASE_);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES8', 'TBL_BINARIES', 'CATALOG'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES8 ON TBL_BINARIES (CATALOG);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES9', 'TBL_BINARIES', 'HEALPIX'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES9 ON TBL_BINARIES (HEALPIX);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES10', 'TBL_BINARIES', 'RELEASE_, CATALOG, SOURCE_ID_PRIMARY, SOURCE_ID_SECONDARY, HAS_RADIAL_VELOCITY, NOT_GROUPED'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES10 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_PRIMARY, SOURCE_ID_SECONDARY, HAS_RADIAL_VELOCITY, NOT_GROUPED);"
                TBL_BINARIES .executeIAD(SQL)
            if self.index_not_exists('IDX_TBL_BINARIES11', 'TBL_BINARIES', 'RELEASE_, CATALOG, SOURCE_ID_PRIMARY, HAS_RADIAL_VELOCITY, NOT_GROUPED'):
                SQL=f"CREATE INDEX IDX_TBL_BINARIES11 ON TBL_BINARIES (RELEASE_, CATALOG, SOURCE_ID_PRIMARY, HAS_RADIAL_VELOCITY, NOT_GROUPED);"
                TBL_BINARIES .executeIAD(SQL)
                
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
            gaia_source.pmdec_error,
            
            gaia_source.parallax_pmra_corr,
            gaia_source.parallax_pmdec_corr,
            gaia_source.ra_parallax_corr,
            gaia_source.dec_parallax_corr,
            gaia_source.ra_pmra_corr,
            gaia_source.ra_pmdec_corr,
            gaia_source.dec_pmra_corr,
            gaia_source.dec_pmdec_corr,
            gaia_source.pmra_pmdec_corr,
            
            gaia_source.phot_bp_mean_flux,
            gaia_source.phot_rp_mean_flux,
            gaia_source.phot_bp_mean_flux_error,
            gaia_source.phot_rp_mean_flux_error
        
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
            
        if not downloadOnly:
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
            -- RA {i} to {i+step} ({(i-lowerRA)/(upperRA-lowerRA)}%)
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
            
            print( query[0] )
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
            print(f'Delete for RA {i} to {i+1} degrees')
            TBL_OBJECTS = SQLLib.sqlDelete(iStro, "TBL_OBJECTS")
            ##TBL_OBJECTS.setWhereValueLTFloat('RA_', i+1)
            ##TBL_OBJECTS.setWhereValueGEFloat('RA_', i)
            TBL_OBJECTS.setWhereAndList('RA_', [f'>={i}',f'<{i+1}'])
            TBL_OBJECTS.setWhereValueString('RELEASE_', release)
            try:
                TBL_OBJECTS.deleteRecordSet()
            except Exception:
                print('Delete Failed.')
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            #filePrefix='iEquals0' + date_time
            self.parent.StatusBarProcessing(f'start processing {len(data):,} records at {date_time}.' )
            bulkSQL='execute block as begin'
            source_id_array=[]
            data2=data.to_dict()
            self.parent.StatusBarProcessing(f'Number of stars: {len(data):,} in {TotalCount:,}')
            #global sqlite_connection
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
            data.to_sql("TBL_OBJECTS", con=iStro, schema='main', index=False, if_exists='append', method=None)
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
        #print(2)

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
        
        static_Separation = StaticText(self, id=wx.ID_ANY, label="Separation [pc]:")
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
        self.spin_G_err1.SetToolTip("Primary phot_g_mean_flux_over_error to download - 0 to 100 (expectation is '50' - KEB)")
        
        # Select phot_rp_mean_flux_over_error
        static_Rp_err1 = StaticText(self, id=wx.ID_ANY, label="RP/err (1):")
        self.sizer_h.Add(static_Rp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err1', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Rp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err1.SetToolTip("Primary phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '20' - KEB), but should be '0' to allow for nulls")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err1 = StaticText(self, id=wx.ID_ANY, label="BP/err (1):")
        self.sizer_h.Add(static_Bp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Bp_err1 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bp_err1','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('bp_err1', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Bp_err1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Bp_err1.SetToolTip("Primary phot_bp_mean_flux_over_error to download - 0 to 100 (expectation is '20'- KEB), but should be '0' to allow for nulls")
        
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
        static_Rp_err2 = StaticText(self, id=wx.ID_ANY, label="RP/err (2):")
        self.sizer_h.Add(static_Rp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Value
        self.spin_Rp_err2 = SpinCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('rp_err2','GAIABINARY', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=100,initial=int(gl_cfg.getItem('rp_err2', 'GAIABINARY',0)))  
        self.sizer_h.Add(self.spin_Rp_err2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_Rp_err2.SetToolTip("Companion phot_rp_mean_flux_over_error to download - 0 to 100 (expectation is '10')")
        
        # Select phot_bp_mean_flux_over_error
        static_Bp_err2 = StaticText(self, id=wx.ID_ANY, label="BP/err (2):")
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
        screen = Display()
        diff = int(1080 - screen.screen_height)
        ctrl_height = 550-diff
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(765,ctrl_height), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
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
                
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel import or status update.")
        self.sizer_v2.Add(self.cancel, 0, wx.LEFT | wx.RIGHT , 5)
        
        self.button3 = Button(self, wx.ID_ANY, u"Clear jobs")
        self.button3.Bind(wx.EVT_LEFT_DOWN, self.OnClear)
        self.button3.SetToolTip("Clear down old Gaia jobs.")
        self.sizer_v2.Add(self.button3, 0, wx.LEFT | wx.ALL , 5)
        
        self.button4 = Button(self, wx.ID_ANY, u"Download jobs")
        self.button4.Bind(wx.EVT_LEFT_DOWN, self.OnDownload)
        self.button4.SetToolTip("Download old Gaia jobs (again). ATTENTION; THIS WILL DOWNLOAD ALL OLD JOBS INTO CURRENT CATALOGUE.")
        self.sizer_v2.Add(self.button4, 0, wx.LEFT | wx.ALL , 5)
        
        #Deselect grouped stars (ie stars in more than 1 binary)
        
        self.ungroup = Button(self, id=wx.ID_ANY, label="&Ungroup", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.ungroup.Bind(wx.EVT_BUTTON, self.deselectDuplicates)
        self.ungroup.SetToolTip("Deselect binaries with stars that appear in more than one pair.  Ie deselect both pairs or entire cluster.")
        self.sizer_v2.Add(self.ungroup, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Export grouped stars (ie stars in more than 1 binary)
        
        self.filterWBs = Button(self, id=wx.ID_ANY, label="&Filter WBs", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.filterWBs.Bind(wx.EVT_BUTTON, self.createFilter)
        self.filterWBs.SetToolTip("Load filters for WBs. Only export those that match one or both.")
        self.sizer_v2.Add(self.filterWBs, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.exportGroups = Button(self, id=wx.ID_ANY, label="&Export groups", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.exportGroups.Bind(wx.EVT_BUTTON, self.exportGrouped)
        self.exportGroups.SetToolTip("Create export list for grouped binaries, ie where one or both stars appear in another WB.  Any loaded filter is applied.")
        self.sizer_v2.Add(self.exportGroups, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Reset status
        
        self.reset = Button(self, id=wx.ID_ANY, label="&Reset", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.reset.Bind(wx.EVT_BUTTON, self.resetStatus)
        self.reset.SetToolTip("Reset 'degrouping' for all binaries in this catalogue")
        self.sizer_v2.Add(self.reset, 0, wx.ALIGN_LEFT|wx.ALL, 5)

    def createFilter(self, event):
        # Ask the user what csv file to open
        # Show the dialog and get the user's choice
        self.primaries=[]
        self.secondaries=[]
        
        with wx.FileDialog(self, "Open .csv file",  defaultDir=gl_cfg.getItem("filter-path"), wildcard="CSV files |*.CSV;*.csv;",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST|wx.FD_PREVIEW) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
    
            # Proceed loading the file chosen by the user
            # Get the selected file path
            file_path = fileDialog.GetPath()
            gl_cfg.setItem("filter-path",fileDialog.GetDirectory())
            # Open and read the file
            with open(file_path, 'r') as file:
                lines = csv.reader(file)
                # Process the lines as needed
                for line in lines:
                    print(line[0],line[1])
                    self.primaries.append(line[0])
                    self.secondaries.append(line[1])
        print (self.primaries)
        print(self.secondaries)
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
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", 1)
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
        print ("SQL 1", sql)
        # SELECT SOURCE_ID FROM ALLSTARS2  WHERE CATALOG = '050PxSn010' and release_ = 'DR3' and NOT_GROUPED = True GROUP BY SOURCE_ID HAVING COUNT(SOURCE_ID) > 1 ORDER BY SOURCE_ID asc
        #sql ="SELECT * FROM ALLSTARS2 WHERE CATALOG = '050PxSn010' and release_ = 'DR3'  and NOT_GROUPED = True  GROUP BY SOURCE_ID  HAVING COUNT(SOURCE_ID) > 1 ORDER BY SOURCE_ID asc"
        #print ("SQL 2", sql)
        # try:
        records = pd.read_sql(sql, iStro)
        # print("Connection = ",iStro)
        print(records)
        # exit()
        # except Exception as e:
        #     print("Error. %s" % e)

        lenArray=len(records)

        print (lenArray)
        self.parent.StatusBarProcessing(f'Ungrouping {lenArray:,} records started')
        Array=[] 
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            Array.append( row.SOURCE_ID)
            
            if not index % 200:
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "group")
                TBL_BINARIES.setAttributeBool("NOT_GROUPED", False)
                TBL_BINARIES.setWhereInList("SOURCE_ID_PRIMARY", Array)
                TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
                TBL_BINARIES.setWhereValueString("release_", RELEASE)
                TBL_BINARIES.updateRecord()
                
                TBL_BINARIES = SQLLib.sqlUpdate(iStro, "TBL_BINARIES")
                TBL_BINARIES.setAttributeString("STATUS", "group")
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
        
        
    def exportGrouped(self, event):
        #Freeze button
        self.exportGroups.Disable()
        
        global RELEASE, CATALOG
        global HPS_SCALE
        global CANCEL
        CANCEL = False
        self.parent.StatusBarProcessing('Group export commenced')
        
        
        self.parent.export=[]
        HPS_SCALE=int(self.HPScale_combo.GetValue())
        RELEASE=self.release.GetValue()
        CATALOG=self.catalogue.GetValue()
        #i=int(self.spin_loadType.GetValue())
        i = HPS_SCALE
            
            
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
#    o1.PHOT_RP_MEAN_FLUX_OVER_ERROR, o1.PHOT_G_MEAN_FLUX_OVER_ERROR, o1.PHOT_BP_MEAN_FLUX_OVER_ERROR, o1.BP_RP,
    
        TBL_BINARIES = SQLLib.sqlSelect(iStro, "TBL_BINARIES b left join TBL_OBJECTS o1 on b.SOURCE_ID_PRIMARY=o1.SOURCE_ID and b.RELEASE_ = o1.RELEASE_ left join TBL_OBJECTS o2 on b.SOURCE_ID_SECONDARY=o2.SOURCE_ID and b.RELEASE_ = o2.RELEASE_")
        TBL_BINARIES.setReturnCol("b.SOURCE_ID_PRIMARY")
        TBL_BINARIES.setReturnCol("o1.RA_ as ra1")
        TBL_BINARIES.setReturnCol("o1.DEC_ as dec1")
        TBL_BINARIES.setReturnCol("o1.parallax as px1")
        TBL_BINARIES.setReturnCol("o1.PHOT_RP_MEAN_FLUX_OVER_ERROR as rp_e1")
        TBL_BINARIES.setReturnCol("o1.BP_RP as bp_rp_1")
        
        TBL_BINARIES.setReturnCol("1000/o1.parallax as DIST1")
        TBL_BINARIES.setReturnCol("o1.parallax_error as px_err1")
        TBL_BINARIES.setReturnCol("o1.parallax_over_error as px_o_err1")
        TBL_BINARIES.setReturnCol("1/o1.parallax_over_error as px_unc1")
        TBL_BINARIES.setReturnCol("b.SOURCE_ID_SECONDARY")
        TBL_BINARIES.setReturnCol("o2.RA_ as ra2")
        TBL_BINARIES.setReturnCol("o2.DEC_ as dec2")
        TBL_BINARIES.setReturnCol("o2.parallax as px2")
        TBL_BINARIES.setReturnCol("o2.parallax as px2")
        TBL_BINARIES.setReturnCol("o2.PHOT_RP_MEAN_FLUX_OVER_ERROR as rp_e2")
        TBL_BINARIES.setReturnCol("o2.BP_RP as bp_rp_2")
        
        TBL_BINARIES.setReturnCol("1000/o2.parallax as DIST2")
        TBL_BINARIES.setReturnCol("o2.parallax_error as px_err2")
        TBL_BINARIES.setReturnCol("o2.parallax_over_error as px_o_err2")
        TBL_BINARIES.setReturnCol("1/o2.parallax_over_error as px_unc2")
        TBL_BINARIES.setReturnCol("b.SEPARATION")
        TBL_BINARIES.setReturnCol("b.HEALPIX")

        TBL_BINARIES.setWhereValueString("CATALOG", CATALOG)
        TBL_BINARIES.setWhereValueString("b.release_", RELEASE)
        TBL_BINARIES.setWhereValueBool("NOT_GROUPED", False)
        TBL_BINARIES.setSortCol("SOURCE_ID_PRIMARY")

        healpix=2**35*4**(12-2)*i*192/HPS_SCALE
        if i<HPS_SCALE:
            TBL_BINARIES.setWhereValueLTInt("SOURCE_ID_PRIMARY", healpix)

        
        sql = TBL_BINARIES.getSQL()
        print (sql)
        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        print (lenArray)
        self.parent.StatusBarProcessing(f'Exporting groups {lenArray:,} records started')
        #Array=[] 
        records=records.convert_dtypes()
        for index, row  in records.iterrows():
            
            #self.createExportRecord(self.parent.X[index], self.parent.Y[index], index)
            #try:
            prim = str(int(row.SOURCE_ID_PRIMARY))
            sec = str(int(row.SOURCE_ID_SECONDARY))
            print(prim)
            print(sec)
            if (prim in self.primaries) or  (prim in self.secondaries) or (sec in self.primaries) or  (sec in self.secondaries) or not len(self.primaries):
                exportRecord={
                    'release': RELEASE,
                    'catalogue': CATALOG,
                    'SOURCE_ID_PRIMARY':row.SOURCE_ID_PRIMARY,
                    'ra1':row.ra1,
                    'dec1':row.dec1,
                    'DIST1':row.DIST1,
                    'px1':row.px1,
                    'px_err1':row.px_err1,
                    'px_o_err1':row.px_o_err1,
                    'px_unc1':row.px_unc1,
                    'SOURCE_ID_SECONDARY':row.SOURCE_ID_SECONDARY,
                    'ra2':row.ra2,
                    'dec2':row.dec2,
                    'DIST2':row.DIST2,
                    'px2':row.px2,
                    'px_err2':row.px_err2,
                    'px_o_err2':row.px_o_err2,
                    'px_unc2':row.px_unc2,
                    'r':row.SEPARATION,
                    'HEALPIX':row.HEALPIX
                }
            
                self.parent.export.append(exportRecord)
            #except Exception:
            #    pass
                
            if not index % 200:
                
                #Array=[] 
    
                label=float(100 * index /lenArray)
                self.exportGroups.SetLabel(f'{label:,.1f}%')
                if CANCEL:
                    CANCEL = False
                    #Release button
                    self.exportGroups.Enable()
                    self.dbload.Enable()
                    return
                wx.Yield()
                 
        
        label=int(100)
        self.exportGroups.SetLabel(f'{label:,.1f}%')
        
        
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
        
        self.parent.export=pd.DataFrame(self.parent.export)
                
        #Release button
        self.exportGroups.Enable()
        self.Layout()
        
        self.parent.StatusBarNormal('Completed OK')
        
    def OnClear(self, event=0):
        
        self.button3.Disable()
        gaia_cnxn = da.GaiaDataAccess()
        jobs = [job for job in gaia_cnxn.list_async_jobs()]
        numJobs = len(jobs)
        num=0
        for inp in jobs:
            num=num+1
            try:
                gaia_cnxn.remove_jobs([inp.jobid])
            except Exception as ErrorMessage:
                print("Error", type(ErrorMessage).__name__, "-", ErrorMessage)
                continue 
            self.parent.StatusBarProcessing(f'Job id = {inp.jobid} removed. ({num:,} of {numJobs:,})')
            wx.Yield()
            global CANCEL
            if CANCEL:
                CANCEL = False
                self.button3.Enable()
                return
        self.parent.StatusBarNormal(f'Complete OK - {numJobs} removed.')
        self.button3.Enable()
        
    def OnDownload(self, event=0):
        
        HPS_SCALE=192
        HPS_SCALE = int(gl_cfg.getItem('hps_scale','SETTINGS', 192))
        self.button3.Disable()
        gaia_cnxn = da.GaiaDataAccess()
        jobs = [job for job in gaia_cnxn.list_async_jobs()]
        #job_ids = [inp.jobid for inp in jobs]
        numJobs = len(jobs)
        num=0
        
        release=self.release.GetValue()
        catalogue=self.catalogue.GetValue()
        forceIt=self.forceDownloadCheckBox.GetValue()
        for inp in jobs:
            num=num+1
            try:    
                results = inp.get_results()
                Hpx=float(results['source_id'][0])
                i=int(Hpx*HPS_SCALE/(2**35*4**(12-2)*192))
                print ("Job", inp.jobid, f"{num} of {numJobs}", "i=",i)
                gaia_data = results.to_pandas()
                data=da.BinaryStarDataFrame(gaia_data)
                if forceIt or not os.path.isfile(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}'):
                    print ("downloading file")
                    data.to_pickle(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}', protocol=int(gl_cfg.getItem('pickle_protocol', 'SETTINGS', 4)))
                else:
                    print ("file already exists") 
            except Exception as ErrorMessage:
                print("Error", type(ErrorMessage).__name__, "-", ErrorMessage)
            self.parent.StatusBarProcessing(f'Job id = {inp.jobid} downloaded. ({num:,} of {numJobs:,})')
            wx.Yield()
            global CANCEL
            if CANCEL:
                CANCEL = False
                self.button3.Enable()
                return
        self.parent.StatusBarNormal(f'Complete OK - {numJobs} downloaded.')
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
                    -- This is Eqation (2) in El Badry
                    -- And radial separation minus ...
                    abs(1/t1.parallax - 1/g2.parallax) -
                    -- 2 * pi()/180 * 'in the plane separation'/parallax
                    2*0.01745*distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec))/t1.parallax
                    -- 3 * 'error along the line of sight'/parallax
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
        
        if not downloadOnly:
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
                self.parent.StatusBarProcessing(f'Deleting TBL_BINARIES{idx} (of 11)')
            
        gaia_cnxn = da.GaiaDataAccess()
        for i in HPS:
            
            label=i
            self.button1.SetLabel(f'{label}')
            self.Layout()
            if CANCEL:
                CANCEL = False
                self.button1.Enable()
                return
            wx.Yield()
            
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
            -- index file: {i} / {HPS_SCALE}
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
                -- outside solar system and within {int(1000/float(self.textctrl_PXfrom1.GetValue()))} pcs
                parallax between {self.textctrl_PXfrom1.GetValue()} and {self.spin_PXto1.GetValue()}
                 and parallax_over_error > {self.spin_Px_err1.GetValue()}
                -- Many dim stars don't have photometric data on Gaia. Rp & Bp over err fields can be set to '0' and g should be set low, eg 5
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
                -- outside solar system and within  {int(1000/float(self.textctrl_PXfrom2.GetValue()))}  pcs
                parallax between {self.textctrl_PXfrom2.GetValue()} and {self.spin_PXto2.GetValue()} 
                and parallax_over_error > {self.spin_Px_err2.GetValue()} 
                -- Many dim stars don't have photometric data on Gaia Rp & Bp should be '0' and g should be low, eg 5
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
                    #print(query[0])
                    data = gaia_cnxn.gaia_query_to_pandas(query[0])
                    #self.parent.StatusBarProcessing(data)
                    data.to_pickle(f'bindata/{release}/{catalogue}/gaia_{release}_HP{i}', protocol=int(gl_cfg.getItem('pickle_protocol', 'SETTINGS', 4)))
            except Exception as ErrorMessage:
                print("Error", type(ErrorMessage).__name__, "-", ErrorMessage, f'HPS i = {i}')
                self.parent.StatusBarProcessing (f'timeout for HPS i = {i}')
                timeoutCount=timeoutCount+1
                self.spin_HPSfrom.SetValue(i)
                #gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
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
                #gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
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
            
            #global sqlite_connection
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
            data.to_sql("TBL_BINARIES", con=iStro, schema='main', index=False, if_exists='append')
            
            now = datetime.datetime.utcnow() # current date and time
            date_time = now.strftime("%Y%m%d_%H%M%S")
            self.parent.StatusBarProcessing(f'updated healpix {i}')
            
            #if forked:
            #    #if not parent (ie it is the child) fork then
            #    print (f'Exiting fork after forking to update DB files for HPS {i}')
            #    sys.exit()
            #
            #label=i
            #self.button1.SetLabel(f'{label}')
            #self.Layout()
            #if CANCEL:
            #    CANCEL = False
            #    self.button1.Enable()
            #    return
            #wx.Yield()
            self.spin_HPSfrom.SetValue(i)
            #gl_cfg.setItem('hpsfrom',i, 'GAIABINARY') # save setting in config file
        
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
    
    def get_value_or_default(self, obj, attr, default=0.0):
        try:
            return float(getattr(obj, attr))
        except (AttributeError, ValueError, TypeError):
            return default
    
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
        
    def CalcMedianXYoverDxy(self, col, col_error=False):
        if col_error:
            XYoverDxy1 = pd.DataFrame()
            XYoverDxy2 = pd.DataFrame()
            XYoverDxy1['Dxy_overXY']=self.parent.status['include']*self.parent.X[col_error].abs()/self.parent.X[col].abs()
            XYoverDxy2['Dxy_overXY']=self.parent.status['include']*self.parent.Y[col_error].abs()/self.parent.Y[col].abs()
            # Concatenate the DataFrames along rows (axis=0)
            XYoverDxy = pd.concat([XYoverDxy1, XYoverDxy2], axis=0)
            ## Create a new DataFrame to store the ratio
            #parallax_ratio_df = pd.DataFrame()
            #parallax_ratio_df['Dxy_overXY'] = XYoverDxy[col_error] / XYoverDxy[col]
            # Exclude zero values
            non_zero_Dxy_overXY_df = XYoverDxy[XYoverDxy['Dxy_overXY'] != 0]
            return non_zero_Dxy_overXY_df['Dxy_overXY'].median()
        #
        #    
        #
        #    totalSelected=self.parent.status['include'].sum()
        #    totalSelected=totalSelected*2
        #else:
        #    XYoverDxy=self.parent.status['include']*self.parent.X[col].abs()
        #    XYoverDxy=XYoverDxy+self.parent.status['include']*self.parent.Y[col].abs()
        #    totalSelected=self.parent.status['include'].sum()*2
        #
        #return round(XYoverDxy.sum()/totalSelected,2)
        
    #def CalcMeanV(self):
    #
    #    XplusY=self.parent.status['include']*self.parent.binaryDetail.vRA.abs()
    #    XplusY=XplusY++self.parent.status['include']*self.parent.binaryDetail.vDEC.abs()   
    #    totalSelected=self.parent.status['include'].sum()*2
    #    return round(XplusY.sum()/totalSelected,2)
        
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

    def get_float(self, data, key, default=0):
        try:
            return float(data[key])
        except (KeyError, ValueError):
            #print(data)
            #if data[key] != None:
            #    print(data[key])
            return default
    
    def get_int(self, data, key, default=0):
        #x="'"+key+"'"
        #print(data)
        #print(data[key])
        try:
            return int(data[key])
        except (KeyError, ValueError):
            return default
    
    #def get_str(data, key, default=''):
    #    try:
    #        return str(data["'"+key+"'"])
    #    except (KeyError, ValueError):
    #        return default
    
    def create_export_record_entry(self, data, suffix=''):
        entry = {}
        #print(type(data))
        #print(data)
        entry['SOURCE_ID' + suffix] = self.get_int(data, 'source_id')
        entry['ra' + suffix] = self.get_float(data, 'ra')
        entry['dec' + suffix] = self.get_float(data, 'dec')
        entry['mag' + suffix] = self.get_float(data, 'mag')
        entry['MAG' + suffix] = self.get_float(data, 'mag')
        entry['PARALLAX' + suffix] = self.get_float(data, 'PARALLAX')
        entry['parallax_error' + suffix] = self.get_float(data, 'parallax_error')
        entry['parallax_over_error' + suffix] = self.get_float(data, 'PARALLAX')/self.get_float(data, 'parallax_error')
        entry['DIST' + suffix] = self.get_float(data, 'DIST')
        entry['RUWE' + suffix] = self.get_float(data, 'RUWE')
        entry['PMRA' + suffix] = self.get_float(data, 'PMRA')
        entry['PMRA_ERROR' + suffix] = self.get_float(data, 'PMRA_ERROR')
        entry['PMDEC' + suffix] = self.get_float(data, 'PMDEC')
        entry['PMDEC_ERROR' + suffix] = self.get_float(data, 'PMDEC_ERROR')
        entry['BminusR' + suffix] = self.get_float(data, 'BminusR')
        entry['mass_calc' + suffix] = self.get_float(data, 'mass_calc')
        entry['mass_flame' + suffix] = self.get_float(data, 'mass_flame')
        entry['mass_flame_upper' + suffix] = self.get_float(data, 'mass_flame_upper')
        entry['mass_flame_lower' + suffix] = self.get_float(data, 'mass_flame_lower')
        entry['age_flame' + suffix] = self.get_float(data, 'age_flame')
        entry['age_flame_upper' + suffix] = self.get_float(data, 'age_flame_upper')
        entry['age_flame_lower'] = self.get_float(data, 'age_flame_lower')
        entry['PROB' + suffix] = self.get_float(data, 'classprob_dsc_specmod_binarystar')
    
        entry['parallax_pmra_corr' + suffix] = self.get_float(data, 'parallax_pmra_corr')
        entry['parallax_pmdec_corr' + suffix] = self.get_float(data, 'parallax_pmdec_corr')
        entry['ra_parallax_corr' + suffix] = self.get_float(data, 'ra_parallax_corr')
        entry['dec_parallax_corr' + suffix] = self.get_float(data, 'dec_parallax_corr')
        entry['ra_pmra_corr' + suffix] = self.get_float(data, 'ra_pmra_corr')
        entry['ra_pmdec_corr' + suffix] = self.get_float(data, 'ra_pmdec_corr')
        entry['dec_pmra_corr' + suffix] = self.get_float(data, 'dec_pmra_corr')
        entry['dec_pmdec_corr' + suffix] = self.get_float(data, 'dec_pmdec_corr')
        entry['pmra_pmdec_corr' + suffix] = self.get_float(data, 'pmra_pmdec_corr')
        
        entry['phot_bp_mean_flux' + suffix] = self.get_float(data, 'phot_bp_mean_flux')
        entry['phot_rp_mean_flux' + suffix] = self.get_float(data, 'phot_rp_mean_flux')
        entry['phot_bp_mean_flux_error' + suffix] = self.get_float(data, 'phot_bp_mean_flux_error')
        entry['phot_rp_mean_flux_error' + suffix] = self.get_float(data, 'phot_rp_mean_flux_error')
        #print(data)
        #print(entry)
        return entry

    def createExportRecord(self, primaryPointer, star2Pointer, idxBin):
        global RELEASE, CATALOG
        #try:
        primary_data = self.create_export_record_entry(primaryPointer, suffix='1')
        star2_data = self.create_export_record_entry(star2Pointer, suffix='2')
        #print(star2_data)
        exportRecord = {
            'release': RELEASE,
            'catalogue': CATALOG,
            
            **primary_data,
            **star2_data,
        }
        exportRecord['DIST'] = (self.get_float(primaryPointer, 'DIST') + self.get_float(star2Pointer, 'DIST')) / 2
        exportRecord['RA_MEAN'] = (self.get_float(primaryPointer, 'ra') + self.get_float(star2Pointer, 'ra')) / 2
        exportRecord['DEC_MEAN'] = (self.get_float(primaryPointer, 'dec') + self.get_float(star2Pointer, 'dec')) / 2
        exportRecord['PX_Over_Err'] = ((self.get_float(primaryPointer, 'PARALLAX')/self.get_float(star2Pointer, 'parallax_error')) + (self.get_float(star2Pointer, 'PARALLAX')/self.get_float(star2Pointer, 'parallax_error')))/2
        #
        #except Exception as e:
        #    print(f"Error creating export record: {e}")
        #    exportRecord = {
        #        'release': RELEASE,
        #        'catalogue': CATALOG
        #    }
        
        #try:
        #    exportRecord={
        #        'release': RELEASE,
        #        'catalogue': CATALOG,
        #        'SOURCE_ID_PRIMARY':int(primaryPointer['source_id']),
        #        'ra1':float(primaryPointer['ra']),
        #        'dec1':float(primaryPointer['dec']),
        #        'mag1':primaryPointer['mag'],
        #        'MAG1':primaryPointer['mag'],
        #        'PARALLAX1':float(primaryPointer['PARALLAX']),
        #        'parallax_error1':float(primaryPointer['parallax_error']),
        #        'DIST1':float(primaryPointer['DIST']),
        #        'RUWE1':primaryPointer['RUWE'],
        #        'PMRA1':float(primaryPointer['PMRA']),
        #        'PMRA_ERROR1':float(primaryPointer['PMRA_ERROR']),
        #        'PMDEC1':float(primaryPointer['PMDEC']),
        #        'PMDEC_ERROR1':float(primaryPointer['PMDEC_ERROR']),
        #        'BminusR1':float(primaryPointer['BminusR']),
        #        'mass_calc1':primaryPointer['mass_calc'],
        #        'mass_flame1':primaryPointer['mass_flame'],
        #        'mass_flame_upper1':primaryPointer['mass_flame_upper'],
        #        'mass_flame_lower1':primaryPointer['mass_flame_lower'],
        #        'age_flame1':primaryPointer['age_flame'],
        #        'age_flame_upper1':primaryPointer['age_flame_upper'],
        #        'age_flame_lower1':primaryPointer['age_flame_lower'],
        #        #'classprob_dsc_specmod_binarystar1':Xclassprob_dsc_specmod_binarystar,
        #        'PROB1':primaryPointer['classprob_dsc_specmod_binarystar'],
        #        'SOURCE_ID_SECONDARY':int(star2Pointer['source_id']),
        #        'ra2':float(star2Pointer['ra']),
        #        'dec2':float(star2Pointer['dec']),
        #        'mag2':star2Pointer['mag'],
        #        'MAG2':star2Pointer['mag'],
        #        'PARALLAX2':float(star2Pointer['PARALLAX']),
        #        'parallax_error2':float(star2Pointer['parallax_error']),
        #        'DIST2':float(star2Pointer['DIST']),
        #        'RUWE2':star2Pointer['RUWE'],
        #        'PMRA2':float(star2Pointer['PMRA']),
        #        'PMRA_ERROR2':float(star2Pointer['PMRA_ERROR']),
        #        'PMDEC2':float(star2Pointer['PMDEC']),
        #        'PMDEC_ERROR2':float(star2Pointer['PMDEC_ERROR']),
        #        'BminusR2':float(star2Pointer['BminusR']),
        #        'mass_calc2':star2Pointer['mass_calc'],
        #        'mass_flame2':star2Pointer['mass_flame'],
        #        'mass_flame_upper2':star2Pointer['mass_flame_upper'],
        #        'mass_flame_lower2':star2Pointer['mass_flame_lower'],
        #        'age_flame2':star2Pointer['age_flame'],
        #        'age_flame_upper2':star2Pointer['age_flame_upper'],
        #        'age_flame_lower2':star2Pointer['age_flame_lower'],
        #        'PROB2':star2Pointer['classprob_dsc_specmod_binarystar'],
        #        'DIST':(float(primaryPointer['DIST'])+float(star2Pointer['DIST']))/2,
        #        'RA_MEAN':(float(primaryPointer['ra'])+float(star2Pointer['ra']))/2,
        #        'DEC_MEAN':(float(primaryPointer['dec'])+float(star2Pointer['dec']))/2
        #    }
        #except Exception as e:
        #    traceback.print_exc()
        #    print(idxBin)
        #    print(primaryPointer)
        #    print(star2Pointer)
        #print(self.parent.binaryDetail)
        #    exit()
        try:
            exportRecord['vRA']=abs(self.parent.binaryDetail.vRA[idxBin])
            exportRecord['vRAerr']=abs(self.parent.binaryDetail.vRAerr[idxBin])
            exportRecord['vDEC']=abs(self.parent.binaryDetail.vDEC[idxBin])
            exportRecord['vDECerr']=abs(self.parent.binaryDetail.vDECerr[idxBin]),                 
            exportRecord['v2D']=math.sqrt(self.parent.binaryDetail.vRA[idxBin]**2+self.parent.binaryDetail.vDEC[idxBin]**2)
            exportRecord['v2D_err']=math.sqrt(self.parent.binaryDetail.vRAerr[idxBin]**2+self.parent.binaryDetail.vDECerr[idxBin]**2)
            exportRecord['Log10vRA']=np.log10(self.parent.binaryDetail.vRA[idxBin])
            exportRecord['Log10vDEC']=np.log10(self.parent.binaryDetail.vDEC[idxBin])
            exportRecord['Log10r']=np.log10(self.parent.binaryDetail.r[idxBin])
            exportRecord['r']=self.parent.binaryDetail.r[idxBin]
            exportRecord['M']=self.parent.binaryDetail.M[idxBin]
            exportRecord['healpix']=self.parent.binaryDetail.healpix[idxBin]
        except Exception:
            #This is before self.parent.binaryDetail has been converted to a dataframe.
            exportRecord['vRA']=abs(self.parent.binaryDetail[idxBin][1])
            exportRecord['vRAerr']=abs(self.parent.binaryDetail[idxBin][2])
            exportRecord['vDEC']=abs(self.parent.binaryDetail[idxBin][3])
            exportRecord['vDECerr']=abs(self.parent.binaryDetail[idxBin][4]),                 
            exportRecord['V2D']=math.sqrt(self.parent.binaryDetail[idxBin][1]**2+self.parent.binaryDetail[idxBin][3]**2)
            exportRecord['Log10vRA']=np.log10(self.parent.binaryDetail[idxBin][1])
            exportRecord['Log10vDEC']=np.log10(self.parent.binaryDetail[idxBin][3])
            exportRecord['Log10r']=np.log10(self.parent.binaryDetail[idxBin][4])
            exportRecord['r']=self.parent.binaryDetail[idxBin][1]
            exportRecord['M']=self.parent.binaryDetail[idxBin][5]
            exportRecord['healpix']=self.parent.binaryDetail[idxBin][6]
        
        self.parent.export.append(exportRecord)
        #print(self.parent.export)
        return
    def saveConfFiles(self, statusKey):
        
        exportPD=pd.DataFrame(self.parent.export)
        exportPD.to_pickle(f'bindata/{RELEASE}/{CATALOG}/export.saved')
        if statusKey:
            self.parent.status[statusKey]=self.parent.status['include']
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
        
class dataRetrieval(masterProcessingPanel):
    
    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'
         
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
        global args
        if not args.ignore_saved:
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
                self.parent.starSystemList=binaryStarSystems(0, gl_cfg.getItem('mass-adjust','RETRIEVAL', '0.05'), gl_cfg.getItem('spher_corr','RETRIEVAL', True))
        else:
            for file in files:
                setattr(self.parent,file, pd.DataFrame())
            self.parent.starSystemList=binaryStarSystems(len(self.parent.status), gl_cfg.getItem('mass-adjust','RETRIEVAL', '0.05'), gl_cfg.getItem('spher_corr','RETRIEVAL', True))
            
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
        
        # Apply Spherical Correction
        spher_corr_StaticText = StaticText(self, id=wx.ID_ANY, label="Apply Spherical Correction?")
        self.sizer_h.Add(spher_corr_StaticText, 0, wx.ALL, 2)
        self.spher_corr_CheckBox = CheckBox(self)
        self.spher_corr_CheckBox.SetToolTip("Appy spherical correction to velocity calculations.")
        self.spher_corr_CheckBox.SetValue(gl_cfg.getBoolean('spher_corr', 'RETRIEVAL', True))
        self.sizer_h.Add(self.spher_corr_CheckBox, 0, wx.ALL, 2)

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
        
        screen = Display()
        diff = int(1080 - screen.screen_height)
        ctrl_height = 800-diff
        
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(1370,ctrl_height), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
        self.listctrl.InsertColumn(0, u"Gaia Star 1 Source ID", wx.LIST_FORMAT_RIGHT, width=200)
        self.listctrl.InsertColumn(1, u"Gaia Star 2 Source ID", wx.LIST_FORMAT_RIGHT, width=200)
        self.listctrl.InsertColumn(2, u"pairing no.", wx.LIST_FORMAT_RIGHT, width=80)
        self.listctrl.InsertColumn(3, u"separation  (pc)",  wx.LIST_FORMAT_RIGHT, width=100)
        self.listctrl.InsertColumn(4, u"Not grouped?", wx.LIST_FORMAT_CENTER,  width=80)
        self.listctrl.InsertColumn(5, u"Has RV?", wx.LIST_FORMAT_CENTER,  width=80)
        self.listctrl.InsertColumn(6, u"Status", wx.LIST_FORMAT_CENTER,  width=100)
        self.listctrl.InsertColumn(7, u"Release", wx.LIST_FORMAT_CENTER,  width=70)
        self.listctrl.InsertColumn(8, u"Catalogue", wx.LIST_FORMAT_CENTER, width=100)
        self.listctrl.InsertColumn(9, u"Healpix", wx.LIST_FORMAT_RIGHT, width=60)
        self.listctrl.InsertColumn(10, u"Mean Distance (pc)", wx.LIST_FORMAT_RIGHT, width=130)
        self.listctrl.InsertColumn(11, u"Spherical Corr", wx.LIST_FORMAT_RIGHT, width=100)
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
        static_Parallax_Over_Error = StaticText(self, id=wx.ID_ANY, label="Mean Error over parallax:")
        self.sizer_h2.Add(static_Parallax_Over_Error, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # RVnull
        ## List columns as a list
        #columns_list = self.parent.X.columns.tolist()
        #print(columns_list)
        # Calculate the ratio
        # Create a new DataFrame to store the ratio
        X_temp = pd.DataFrame(columns=['parallax_uncertainty'])
        try:
            X_temp['parallax_uncertainty'] = self.parent.X['parallax_error'] / self.parent.X['PARALLAX']
            # Calculate the mean of the ratio
            mean_parallax_X_uncertainty = X_temp['parallax_uncertainty'].mean()
            # Calculate the ratio
            Y_temp = pd.DataFrame()
            Y_temp['parallax_uncertainty'] = self.parent.Y['parallax_error'] / self.parent.Y['PARALLAX']
            # Calculate the mean of the ratio
            mean_parallax_Y_uncertainty = Y_temp['parallax_uncertainty'].mean()
        except:
            mean_parallax_X_uncertainty=0
            mean_parallax_Y_uncertainty=0
        ROWCOUNTMATRIX['GRP']=(mean_parallax_X_uncertainty + mean_parallax_Y_uncertainty)/2
        self.static_Parallax_Uncertainty = StaticText(self, id=wx.ID_ANY, label=f'{ROWCOUNTMATRIX["GRP"]:,}')
        self.sizer_h2.Add(self.static_Parallax_Uncertainty, 0, wx.ALL, 5)
        
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

        #Restore catalogue from a diretory
        
        self.restore = Button(self, id=wx.ID_ANY, label="&Restore", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.restore.Bind(wx.EVT_BUTTON, self.catalogRestore)
        self.restore.SetToolTip("Restore catalogue from diretory")
        self.sizer_v2.Add(self.restore, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel import or status update.")
        self.sizer_v2.Add(self.cancel, 0, wx.LEFT | wx.RIGHT , 5)
        
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
        self.move.Bind(wx.EVT_BUTTON, self.moveBinaries)
        self.move.SetToolTip("For binaries in one catalogue, move to a different catalogue 'KEB5E5-BA")
        self.sizer_v2.Add(self.move, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        #Delete binaries with that combination of 'release', 'catalogue', and 'healpix/RA/dec'
        
        self.deleteSelection = Button(self, id=wx.ID_ANY, label="Delete", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.deleteSelection.Bind(wx.EVT_BUTTON, self.OnDeleteSelection)
        self.deleteSelection.SetToolTip("Delete binaries with that combination of 'release', 'catalogue', and 'healpix/RA/dec'")
        self.sizer_v2.Add(self.deleteSelection, 0, wx.ALIGN_LEFT|wx.ALL, 5)

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
            try:
                V_spher_corr = str(round(abs(row.V_spher_corr),3))
            except Exception:
                V_spher_corr = 'Not Avail.'

            self.listctrl.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, index,round(float(separation),5), notGrouped, hasRadialVelocity, status, row.RELEASE_, row.CATALOG, healpix, round((self.parent.X.DIST[index]+self.parent.Y.DIST[index])/2, 2), V_spher_corr])

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
        global CATALOG, RELEASE, gl_cfg
        
        CATALOG=self.catalogue.GetValue()
        CATALOG_NUM=self.catalogue.GetSelection()
        RELEASE=self.release.GetValue()
        RELEASE_NUM=self.release.GetSelection()
        #Try to restore saved files, if not, error
        files=['selectedStarBinaryMappings','binaryDetail','star_rows','X','Y','status','export']
        for file in files:
            try:
                setattr(self.parent,file, pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved'))
                print(file)
                print(pd.read_pickle(f'bindata/{RELEASE}/{CATALOG}/{file}.saved'))
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
        
        # Reset defaults for 'Download stars and attributes' page'.
        
        self.parent.releasePage.release.SetSelection(RELEASE_NUM) # save setting in config file
        self.parent.releasePage.spin_RAfrom.SetValue(gl_cfg.getItem('rafrom','GAIASTAR')) # save setting in config file
        self.parent.releasePage.spin_RAto.SetValue(gl_cfg.getItem('rato','GAIASTAR')) # save setting in config file
        
        self.parent.releasePage.spin_PXto.SetValue(gl_cfg.getItem('pxto', 'GAIASTAR')) # save setting in config file
        self.parent.releasePage.spin_PXfrom.SetValue(gl_cfg.getItem('pxfrom', 'GAIASTAR')) # save setting in config file
        self.parent.releasePage.spin_Rp_err.SetValue(gl_cfg.getItem('rp_err','GAIASTAR')) # save setting in config file
        self.parent.releasePage.spin_Bp_err.SetValue(gl_cfg.getItem('bp_err','GAIASTAR')) # save setting in config file
        self.parent.releasePage.spin_Px_err.SetValue(gl_cfg.getItem('px_err','GAIASTAR')) # save setting in config file
        self.parent.releasePage.spin_G_err.SetValue(gl_cfg.getItem('g_err','GAIASTAR')) # save setting in config file
        
        self.parent.releasePage.downloadOnlyCheckBox.SetValue(gl_cfg.getBoolean('downloadonly','GAIASTAR')) # save setting in config file
        self.parent.releasePage.forceDownloadCheckBox.SetValue(gl_cfg.getBoolean('forceredownload', 'GAIASTAR')) # save notebook tab setting in config file
        self.parent.releasePage.deactivateIndicesCheckBox.SetValue(gl_cfg.getBoolean('deactivateindices','GAIASTAR')) # save notebook tab setting in config file
        
        # Reset defaults for 'Download binary catalogue' page.
    
        self.parent.catalogPage.catalogue.SetSelection(CATALOG_NUM) # save setting in config file
        self.parent.catalogPage.textctrl_Separation.SetValue(gl_cfg.getItem('value','GAIABINARY')) # save setting in config file 
        self.parent.catalogPage.release.SetSelection(RELEASE_NUM) # save setting in config file
        self.parent.catalogPage.spin_HPSfrom.SetValue(gl_cfg.getItem('hpsfrom','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_HPSto.SetValue(gl_cfg.getItem('hpsto','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.downloadOnlyCheckBox.SetValue(gl_cfg.getBoolean('downloadonly', 'GAIABINARY')) # save setting in config file
        self.parent.catalogPage.forceDownloadCheckBox.SetValue(gl_cfg.getBoolean('forceredownload', 'GAIABINARY')) # save notebook tab setting in config file
        self.parent.catalogPage.deactivateIndicesCheckBox.SetValue(gl_cfg.getBoolean('deactivateindices','GAIABINARY')) # save notebook tab setting in config file
        
        self.parent.catalogPage.spin_PXto1.SetValue(gl_cfg.getItem('pxto1','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.textctrl_PXfrom1.SetValue(gl_cfg.getItem('pxfrom1','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_Rp_err1.SetValue(gl_cfg.getItem('rp_err1','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_Bp_err1.SetValue(gl_cfg.getItem('bp_err1','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_Px_err1.SetValue(gl_cfg.getItem('px_err1','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_G_err1.SetValue(gl_cfg.getItem('g_err1','GAIABINARY')) # save setting in config file
        
        self.parent.catalogPage.spin_PXto2.SetValue(gl_cfg.getItem('pxto2', 'GAIABINARY')) # save setting in config file
        self.parent.catalogPage.textctrl_PXfrom2.SetValue(gl_cfg.getItem('pxfrom2','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_Rp_err2.SetValue(gl_cfg.getItem('rp_err2','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_Bp_err2.SetValue(gl_cfg.getItem('bp_err2','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_Px_err2.SetValue(gl_cfg.getItem('px_err2','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_G_err2.SetValue(gl_cfg.getItem('g_err2', 'GAIABINARY')) # save setting in config file
        self.parent.catalogPage.spin_mod_b_gt.SetValue(gl_cfg.getItem('mod_b_gt','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.textCtrl_max_data.SetValue(gl_cfg.getItem('max_data','GAIABINARY')) # save setting in config file
        self.parent.catalogPage.HPScale_combo.SetValue(int(gl_cfg.getItem('hps_scale','SETTINGS')))
        
        # Reset defaults for 'Load binary catalogue' page.
        
        self.parent.retrievalPage.catalogue.SetSelection(CATALOG_NUM) # save setting in config file
        self.parent.retrievalPage.loadType_combo.SetSelection(gl_cfg.getInt('loadType','RETRIEVAL')) # save setting in config file
        self.parent.retrievalPage.spin_loadType.SetValue(gl_cfg.getItem('value', 'RETRIEVAL')) # save setting in config file
        self.parent.retrievalPage.release.SetSelection(RELEASE_NUM) # save setting in config file
        self.parent.retrievalPage.unGroupedCheckBox.SetValue(gl_cfg.getBoolean('ungrouped','RETRIEVAL')) # save notebook tab setting in config file
        self.parent.retrievalPage.rvnullCheckBox.SetValue(gl_cfg.getBoolean('rvnull','RETRIEVAL')) # save notebook tab setting in config file       
        self.parent.retrievalPage.text_massAdjust.SetValue(gl_cfg.getItem('mass-adjust','RETRIEVAL'))
        
        # Reset defaults for 'Apply Binary filter' page.
        self.parent.filterPage.spin_parallax_SN.SetValue(gl_cfg.getItem('pxsn_gt','FILTER'))
        self.parent.filterPage.spin_red_mag_SN.SetValue(gl_cfg.getItem('rpsn_gt','FILTER'))
        self.parent.filterPage.spin_green_mag_SN.SetValue(gl_cfg.getItem('g_sn_gt','FILTER'))
        self.parent.filterPage.spin_blue_mag_SN.SetValue(gl_cfg.getItem('bpsn_gt','FILTER'))
        self.parent.filterPage.spin_pmsnratio.SetValue(gl_cfg.getItem('pmsn_gt','FILTER'))
        self.parent.filterPage.spin_diff_radial_velocity.SetValue(gl_cfg.getItem('rv_lt','FILTER'))
        self.parent.filterPage.text_ruwe.SetValue(gl_cfg.getItem('ruwe_lt','FILTER'))
        self.parent.filterPage.text_b.SetValue(gl_cfg.getItem('b_gt','FILTER'))
        self.parent.filterPage.text_binProbability.SetValue(gl_cfg.getItem('bin_probability_lt','FILTER'))
        #gl_cfg.getItem('io',self.parent.combo_InOut.GetSelection(),'FILTER'))
        self.parent.filterPage.spin_distCutoff.SetValue(gl_cfg.getItem('cutoff-outer','FILTER'))
        self.parent.filterPage.spin_distInnerCutoff.SetValue(gl_cfg.getItem('cutoff-inner','FILTER'))
        self.parent.filterPage.text_Min_Sepn.SetValue(gl_cfg.getItem('min-sepn','FILTER'))
        self.parent.filterPage.text_ageDiffMax.SetValue(gl_cfg.getItem('age-diff-max','FILTER'))
        self.parent.filterPage.activateAgeCompCheckBox.SetValue(gl_cfg.getBoolean('activate-age-comp','FILTER'))
        
        # Reset defaults for 'Sky Density plot' page.
        
        self.parent.skyPage.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion','SKYPLOT')) # save setting in config file
        self.parent.skyPage.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints','SKYPLOT')) # save setting in config file
        self.parent.skyPage.unselectedCheckBox.SetValue(gl_cfg.getBoolean('unselected','SKYPLOT')) # save setting in config file
        self.parent.skyPage.allWhiteCheckBox.SetValue(gl_cfg.getBoolean('allwhite','SKYPLOT')) # save setting in config file
        self.parent.skyPage.suppressGroupsCheckBox.SetValue(gl_cfg.getBoolean('suppressgroups','SKYPLOT')) # save setting in config file
        self.parent.skyPage.suppressRVZeroCheckBox.SetValue(gl_cfg.getBoolean('suppressrvzero','SKYPLOT')) # save setting in config file
        self.parent.skyPage.showGalacticCoordsCheckBox.SetValue(gl_cfg.getBoolean('galacticCoords','SKYPLOT')) # save setting in config file
        
        # Reset defaults for 'H-R plot' page.
        
        self.parent.hrPage.text_colourLower.SetValue(gl_cfg.getItem('col_lower','HRPLOT'))
        self.parent.hrPage.text_colourUpper.SetValue(gl_cfg.getItem('col_upper','HRPLOT'))
        self.parent.hrPage.text_magLower.SetValue(gl_cfg.getItem('mag_lower','HRPLOT'))
        self.parent.hrPage.text_magUpper.SetValue(gl_cfg.getItem('mag_upper','HRPLOT'))
        self.parent.hrPage.text_magRange.SetValue(gl_cfg.getItem('mag_range','HRPLOT'))
        self.parent.hrPage.allWhiteCheckBox.SetValue(gl_cfg.getBoolean('allwhite','HRPLOT')) # save setting in config file
        self.parent.hrPage.unselectedCheckBox.SetValue(gl_cfg.getBoolean('unselected','HRPLOT')) # save setting in config file
        self.parent.hrPage.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion','HRPLOT')) # save setting in config file
        self.parent.hrPage.M_KrefCheckBox.SetValue(gl_cfg.getBoolean('m_kref','HRPLOT')) # save setting in config file
        self.parent.hrPage.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints','HRPLOT')) # save setting in config file
        
        # Reset defaults for 'Kinematic plot' page.
        
        self.parent.plottingPage.spin_bins.SetValue(gl_cfg.getItem('no_bins','KINETIC'))
        self.parent.plottingPage.textctrl_xLower.SetValue(gl_cfg.getItem('x_lower','KINETIC'))
        self.parent.plottingPage.textctrl_xUpper.SetValue(gl_cfg.getItem('x_upper','KINETIC'))
        self.parent.plottingPage.textctrl_yLower.SetValue(gl_cfg.getItem('y_lower','KINETIC'))
        self.parent.plottingPage.textctrl_yUpper.SetValue(gl_cfg.getItem('y_upper','KINETIC'))
        self.parent.plottingPage.text_x_TopLeft.SetValue(gl_cfg.getItem('x_topLeft','KINETIC'))
        self.parent.plottingPage.text_y_TopLeft.SetValue(gl_cfg.getItem('y_topLeft','KINETIC'))
        self.parent.plottingPage.text_x_BottomRight.SetValue(gl_cfg.getItem('x_bottomRight','KINETIC'))
        self.parent.plottingPage.text_y_BottomRight.SetValue(gl_cfg.getItem('y_bottomRight','KINETIC'))
        self.parent.plottingPage.text_upperCutoff.SetValue(gl_cfg.getItem('upper_cutoff','KINETIC'))
        self.parent.plottingPage.text_v_tilde_upperCutoff.SetValue(gl_cfg.getItem('upper_v_tilde_cutoff','KINETIC'))
        self.parent.plottingPage.text_vxerrCutoff.SetValue(gl_cfg.getItem('v_dv_cutoff','KINETIC'))
        self.parent.plottingPage.lowerBinCutoffTextCtrl.SetValue(gl_cfg.getItem('lower_bin_cutoff','KINETIC'))
        self.parent.plottingPage.combo_yLog.SetSelection(gl_cfg.getInt('y_scale','KINETIC'))
        self.parent.plottingPage.combo_binReduction.SetSelection(gl_cfg.getInt('combo-bin-reduction','KINETIC'))
        self.parent.plottingPage.combo_yAvg.SetSelection(gl_cfg.getInt('y_avg','KINETIC'))
        self.parent.plottingPage.combo_xAvg.SetSelection(gl_cfg.getInt('x_avg','KINETIC'))
        self.parent.plottingPage.combo_xy_option.SetSelection(gl_cfg.getInt('xy_option','KINETIC'))
        self.parent.plottingPage.newtonian_CheckBox.SetValue(gl_cfg.getBoolean('newtonian','KINETIC')) # save setting in config file
        self.parent.plottingPage.mond_CheckBox.SetValue(gl_cfg.getBoolean('mond','KINETIC')) # save setting in config file
        self.parent.plottingPage.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints','KINETIC')) # save setting in config file
        self.parent.plottingPage.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion','KINETIC')) # save setting in config file
        self.parent.plottingPage.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints','KINETIC')) # save setting in config file
        self.parent.plottingPage.showBinsCheckBox.SetValue(gl_cfg.getBoolean('showbins','KINETIC')) # save setting in config file
        self.parent.plottingPage.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata','KINETIC')) # save setting in config file
        self.parent.plottingPage.outlierLineCheckBox.SetValue(gl_cfg.getBoolean('outlierline','KINETIC')) # save setting in config file
#        self.parent.plottingPage.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels','KINETIC')) # save setting in config file
        self.parent.plottingPage.combo_deselect_aboveBelow.SetSelection(gl_cfg.getInt('above-below-line','KINETIC'))
        
        # Reset defaults for 'Mass vs Flame plot' page.
        
        self.parent.GaiaMassPage.spin_bins.SetValue(gl_cfg.getItem('no_bins','GAIAMASS'))
        self.parent.GaiaMassPage.textctrl_xLower.SetValue(gl_cfg.getItem('x_lower','GAIAMASS'))
        self.parent.GaiaMassPage.textctrl_xUpper.SetValue(gl_cfg.getItem('x_upper','GAIAMASS'))
        self.parent.GaiaMassPage.lowerBinCutoffTextCtrl.SetValue(gl_cfg.getItem('lower_bin_cutoff','GAIAMASS'))
        self.parent.GaiaMassPage.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata','GAIAMASS')) # save setting in config file
        self.parent.GaiaMassPage.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion','GAIAMASS')) # save setting in config file
        self.parent.GaiaMassPage.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints','GAIAMASS')) # save setting in config file
        self.parent.GaiaMassPage.showBinsCheckBox.SetValue(gl_cfg.getBoolean('showbins','GAIAMASS')) # save setting in config file
        
        # Reset defaults for 'Velocity Vs Mass plot' page.
        
        self.parent.TulleyFisherPage.spin_bins.SetValue(gl_cfg.getItem('no_bins','TULLEYFISHER'))
        self.parent.TulleyFisherPage.textctrl_xLower.SetValue(gl_cfg.getItem('x_lower','TULLEYFISHER'))
        self.parent.TulleyFisherPage.textctrl_xUpper.SetValue(gl_cfg.getItem('x_upper','TULLEYFISHER'))
        self.parent.TulleyFisherPage.textctrl_yLower.SetValue(gl_cfg.getItem('y_lower','TULLEYFISHER'))
        self.parent.TulleyFisherPage.textctrl_yUpper.SetValue(gl_cfg.getItem('y_upper','TULLEYFISHER'))
        self.parent.TulleyFisherPage.text_upperRCutoff.SetValue(gl_cfg.getItem('upper_rcutoff','TULLEYFISHER'))
        self.parent.TulleyFisherPage.text_upperYCutoff.SetValue(gl_cfg.getItem('upper_ycutoff','TULLEYFISHER'))
        self.parent.TulleyFisherPage.lowerBinCutoffTextCtrl.SetValue(gl_cfg.getItem('lower_bin_cutoff','TULLEYFISHER'))
        self.parent.TulleyFisherPage.lowerBinCutoffTextCtrl.SetValue(gl_cfg.getItem('upper_bin_split','TULLEYFISHER'))
        self.parent.TulleyFisherPage.combo_yLog.SetSelection(gl_cfg.getInt('y_scale','TULLEYFISHER'))
        self.parent.TulleyFisherPage.combo_yAvg.SetSelection(gl_cfg.getInt('y_avg','TULLEYFISHER'))
        self.parent.TulleyFisherPage.combo_LtGt.SetSelection(gl_cfg.getInt('gtlt','TULLEYFISHER'))
        self.parent.TulleyFisherPage.TextCtrl_sepnCutoff.SetValue(gl_cfg.getItem('cutoff','TULLEYFISHER'))
        self.parent.TulleyFisherPage.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata','TULLEYFISHER') )# save setting in config file
        self.parent.TulleyFisherPage.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion','TULLEYFISHER')) # save setting in config file
        self.parent.TulleyFisherPage.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints','TULLEYFISHER')) # save setting in config file
        self.parent.TulleyFisherPage.V1D_CheckBox.SetValue(gl_cfg.getBoolean('v1d','TULLEYFISHER')) # save setting in config file
        self.parent.TulleyFisherPage.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels','TULLEYFISHER')) # save setting in config file
        
        # Reset defaults for 'Star Density Vs Distance plot' page.
        
        self.parent.NumberDensityPage.spin_bins.SetValue(gl_cfg.getItem('no_bins','NUMBERDENSITY'))
        self.parent.NumberDensityPage.textctrl_xUpper.SetValue(gl_cfg.getItem('x_upper','NUMBERDENSITY'))
        self.parent.NumberDensityPage.textctrl_yUpper.SetValue(gl_cfg.getItem('y_upper','NUMBERDENSITY'))
        self.parent.NumberDensityPage.prntVersionCheckBox.SetValue(gl_cfg.getBoolean('prntversion','NUMBERDENSITY')) # save setting in config file
        self.parent.NumberDensityPage.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels','NUMBERDENSITY')) # save setting in config file
        self.parent.NumberDensityPage.Series1CheckBox.SetValue(gl_cfg.getBoolean('rawdata1', 'NUMBERDENSITY'))
        self.parent.NumberDensityPage.Series2CheckBox.SetValue(gl_cfg.getBoolean('rawdata2', 'NUMBERDENSITY'))
        self.parent.NumberDensityPage.Series3CheckBox.SetValue(gl_cfg.getBoolean('rawdata3', 'NUMBERDENSITY'))
        self.parent.NumberDensityPage.Series4CheckBox.SetValue(gl_cfg.getBoolean('rawdata4','NUMBERDENSITY'))
        
        # Reset defaults for 'Aladin lite' page.
        try:
            self.parent.AladinPage.sort.SetSelection(int(gl_cfg.getInt('sort','ALADIN')))
            self.parent.AladinPage.ascBool.SetSelection(int(gl_cfg.getInt('order','ALADIN')))
        except Exception:
            pass
        
        self.parent.StatusBarNormal("\nPandas file restore done!\n")
        self.restoreListCtrl()
        
        self.static_Total.SetLabel(f'{int(len(self.parent.star_rows)/2):,}')
        
        
        X_temp = pd.DataFrame()
        X_temp['parallax_uncertainty'] = self.parent.X['parallax_error'] / self.parent.X['PARALLAX']
        # Calculate the mean of the ratio
        mean_parallax_X_uncertainty = X_temp['parallax_uncertainty'].mean()
        # Calculate the ratio
        Y_temp = pd.DataFrame()
        Y_temp['parallax_uncertainty'] = self.parent.Y['parallax_error'] / self.parent.Y['PARALLAX']
        # Calculate the mean of the ratio
        mean_parallax_Y_uncertainty = Y_temp['parallax_uncertainty'].mean()
        ROWCOUNTMATRIX['GRP']=(mean_parallax_X_uncertainty + mean_parallax_Y_uncertainty)/2
        self.static_Parallax_Uncertainty.SetLabel(f'{ROWCOUNTMATRIX["GRP"]:,}')
        
        #self.
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
        #
        self.rvnull.Enable()
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

        spher_corr=self.spher_corr_CheckBox.GetValue()
        #print(spher_corr)
        gl_cfg.setItem('spher_corr',spher_corr, 'RETRIEVAL') # save notebook tab setting in config file
        gl_cfg.setItem('ungrouped',self.unGroupedCheckBox.GetValue(), 'RETRIEVAL') # save notebook tab setting in config file
        gl_cfg.setItem('rvnull',self.rvnullCheckBox.GetValue(), 'RETRIEVAL') # save notebook tab setting in config file       

        gl_cfg.setItem('mass-adjust',self.text_massAdjust.GetValue(), 'RETRIEVAL')

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
        
                        o1.SOURCE_ID,
                        o1.RA_,
                        o1.RA_ERROR,
                        o1.DEC_,
                        o1.DEC_ERROR,
                        o1.PARALLAX,
                        o1.parallax_error,
                        o1.phot_g_mean_mag,
                        o1.PHOT_RP_MEAN_FLUX_OVER_ERROR,
                        o1.PHOT_G_MEAN_FLUX_OVER_ERROR,
                        o1.PHOT_BP_MEAN_FLUX_OVER_ERROR,
                        o1.BP_RP,
                        o1.RADIAL_VELOCITY,
                        o1.RADIAL_VELOCITY_ERROR,
                        o1.PMRA,
                        o1.PMRA_ERROR,
                        o1.PMDEC,
                        o1.PMDEC_ERROR,
                        o1.RELEASE_,
                        o1.RUWE,
                        1000/o1.PARALLAX as DIST,
                        1/o1.PARALLAX_OVER_ERROR as DIST_ERR,
                        o1.MASS_FLAME,
                        o1.MASS_FLAME_UPPER,
                        o1.MASS_FLAME_LOWER,
                        o1.AGE_FLAME,
                        o1.AGE_FLAME_UPPER,
                        o1.AGE_FLAME_LOWER,
                        o1.CLASSPROB_DSC_SPECMOD_BINARYSTAR,
                        o1.PARALLAX_PMRA_CORR,
                        o1.PARALLAX_PMDEC_CORR,
                        o1.RA_PARALLAX_CORR,
                        o1.DEC_PARALLAX_CORR,
                        o1.RA_PMRA_CORR,
                        o1.RA_PMDEC_CORR,
                        o1.DEC_PMRA_CORR,
                        o1.DEC_PMDEC_CORR,
                        o1.PMRA_PMDEC_CORR,
                        o1.PHOT_BP_MEAN_FLUX,
                        o1.PHOT_RP_MEAN_FLUX,
                        o1.PHOT_BP_MEAN_FLUX_ERROR,
                        o1.PHOT_RP_MEAN_FLUX_ERROR,
                        
                        o2.SOURCE_ID,
                        o2.RA_,
                        o2.RA_ERROR,
                        o2.DEC_,
                        o2.DEC_ERROR,
                        o2.PARALLAX,
                        o2.parallax_error,
                        o2.phot_g_mean_mag,
                        o2.PHOT_RP_MEAN_FLUX_OVER_ERROR,
                        o2.PHOT_G_MEAN_FLUX_OVER_ERROR,
                        o2.PHOT_BP_MEAN_FLUX_OVER_ERROR,
                        o2.BP_RP,
                        o2.RADIAL_VELOCITY,
                        o2.RADIAL_VELOCITY_ERROR, 
                        o2.PMRA,
                        o2.PMRA_ERROR,
                        o2.PMDEC,
                        o2.PMDEC_ERROR,
                        o2.RELEASE_,
                        o2.RUWE,
                        1000/o2.PARALLAX as DIST,
                        1/o2.PARALLAX_OVER_ERROR as DIST_ERR,
                        o2.MASS_FLAME,
                        o2.MASS_FLAME_UPPER,
                        o2.MASS_FLAME_LOWER,
                        o2.AGE_FLAME,
                        o2.AGE_FLAME_UPPER,
                        o2.AGE_FLAME_LOWER,
                        o2.CLASSPROB_DSC_SPECMOD_BINARYSTAR,
                        
                        o2.PARALLAX_PMRA_CORR,
                        o2.PARALLAX_PMDEC_CORR,
                        o2.RA_PARALLAX_CORR,
                        o2.DEC_PARALLAX_CORR,
                        o2.RA_PMRA_CORR,
                        o2.RA_PMDEC_CORR,
                        o2.DEC_PMRA_CORR,
                        o2.DEC_PMDEC_CORR,
                        o2.PMRA_PMDEC_CORR,
                        o2.PHOT_BP_MEAN_FLUX,
                        o2.PHOT_RP_MEAN_FLUX,
                        o2.PHOT_BP_MEAN_FLUX_ERROR,
                        o2.PHOT_RP_MEAN_FLUX_ERROR
                        
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
        #print(recordsAll)
        i=0
        lenArray=len(recordsAll)
        self.parent.StatusBarProcessing(f'lenArray={lenArray:,}')
        print("starSystemList (spher_corr) = ", spher_corr)
        self.parent.starSystemList=binaryStarSystems(lenArray, gl_cfg.getItem('mass-adjust','RETRIEVAL', '0.05'), spher_corr)
        
        #Mass_Correction=float()  #  0.05 correction to allow for low mass dispersion
        records=recordsAll.iloc[:,range(9)]
        records.drop(columns=['RELEASE_', 'CATALOG', 'SOURCE_ID_PRIMARY', 'SOURCE_ID_SECONDARY'])
        X=recordsAll.iloc[:,range(9,51)]
        #print(X)
        Y=recordsAll.iloc[:,range(51,93)]
        #print(Y)
        records=records.convert_dtypes()
        del recordsAll
        X=X.convert_dtypes()
        Y=Y.convert_dtypes()
        for index, row  in records.iterrows():
            i=i+1
            #print(f"Distance ({i}) = ", X.iloc[i], Y.iloc[i])

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

            #try:
            #Check for primary/companion

            if X.phot_g_mean_mag.iloc[index]<Y.phot_g_mean_mag.iloc[index]:
                # Add first star (primary star)
                self.parent.starSystemList.addSystem(X.iloc[index], i)
                #
                # Then add second star (companion star)
                (ccdm, R, Rerr, V, Verr, M, BIN, V_spher_corr) = self.parent.starSystemList.addSystem(Y.iloc[index], i)
            else:
                # Add first star in reverse order (primary star)
                self.parent.starSystemList.addSystem(Y.iloc[index], i)
                #
                # Add second star in reverse order  (companion star)
                (ccdm, R, Rerr, V, Verr, M, BIN, V_spher_corr) = self.parent.starSystemList.addSystem(X.iloc[index], i)
            '''except Exception:
                # Add first star (primary star)
                self.parent.starSystemList.addSystem(X.iloc[index], i)
                #
                # Add second star (companion star)
                (ccdm, R, Rerr, V, Verr, M, BIN, V_spher_corr) = self.parent.starSystemList.addSystem(Y.iloc[index], i)
                self.parent.StatusBarProcessing(f'Except: G_MEAN_MAG error')
                include=0'''
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
                'HEALPIX':healpix,
                'V_spher_corr':V_spher_corr
                
            }
            print("V_spher_corr",V_spher_corr)
            #Calulate mean, inverse-variance-weighted parallax
            sigma_squared_px_1 = primaryPointer.parallax_error**2
            sigma_squared_px_2 = star2Pointer.parallax_error**2
            varpi_1=primaryPointer.parallax*sigma_squared_px_2
            varpi_2=star2Pointer.parallax*sigma_squared_px_1
            meanParallax=(varpi_1+varpi_2)/(sigma_squared_px_1+sigma_squared_px_2)
            #RV_status=
            if index<1000:
                #try:
                #    if str(row.STATUS) == '<NA>':
                #        status=''
                #    else:
                #        status=str(row.STATUS)
                #except Exception:
                #    status = ''
                #print(str(row.STATUS))
                #print(type(row), row)
                #print(type(X), X)
                #print(type(Y), Y)
                #print(type(Y.DIST), Y.DIST)


                print("Mean Parallax Distance =", 1000/meanParallax)
                print("R = ", R, "V = ", V, "separation", separation, "SCorr simple = ", round(float(primaryPointer.radial_velocity)*round(float(R), 3)*meanParallax/1000,3), "SCorr full = ", round(V_spher_corr,3))
                print("RV = ", float(primaryPointer.radial_velocity), "abs = ", abs(float(primaryPointer.radial_velocity)), type(abs(float(primaryPointer.radial_velocity))), "condition =", abs(float(primaryPointer.radial_velocity)) > 0)
                #print (X.DIST[i])
                #print (Y.DIST[i])
                RV_status=str(round(float(primaryPointer.radial_velocity),1))
                if abs(float(primaryPointer.radial_velocity)) > 0:
                    RV_Status = str(float(primaryPointer.radial_velocity))
                else:
                    RV_status = hasRadialVelocity
                self.listctrl.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, index, round(float(separation),5), notGrouped, RV_status,status, RELEASE, CATALOG, healpix, round((X.DIST[i]+Y.DIST[i])/2, 2), round(V_spher_corr,3)])


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

            XRUWE=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "ruwe")
            YRUWE=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "ruwe")
                        
            XBminusR=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "bp_rp")
            YBminusR=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "bp_rp")
            
            XPHOT_G_MEAN_MAG=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "phot_g_mean_mag")
            YPHOT_G_MEAN_MAG=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "phot_g_mean_mag")
            
            Xmass_calc=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "mass_calc")
            Ymass_calc=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "mass_calc")

            print("Xmass_calc",Xmass_calc)
            
            Xmass_flame=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "mass_flame")
            Ymass_flame=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "mass_flame")
            
            Xparallax_pmra_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "parallax_pmra_corr")
            Yparallax_pmra_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "parallax_pmra_corr")
            
            Xparallax_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "parallax_pmdec_corr")
            Yparallax_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "parallax_pmdec_corr")
            
            Xra_parallax_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "ra_parallax_corr")
            Yra_parallax_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "ra_parallax_corr")
            
            Xdec_parallax_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "dec_parallax_corr")
            Ydec_parallax_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "dec_parallax_corr")
            
            Xra_pmra_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "ra_pmra_corr")
            Yra_pmra_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "ra_pmra_corr")
            
            Xra_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "ra_pmdec_corr")
            Yra_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "ra_pmdec_corr")
            
            Xdec_pmra_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "dec_pmra_corr")
            Ydec_pmra_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "dec_pmra_corr")
            
            Xdec_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "dec_pmdec_corr")
            Ydec_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "dec_pmdec_corr")
            
            Xpmra_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "pmra_pmdec_corr")
            Ypmra_pmdec_corr=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "pmra_pmdec_corr")
            
            Xphot_bp_mean_flux=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "phot_bp_mean_flux")
            Yphot_bp_mean_flux=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "phot_bp_mean_flux")
            
            Xphot_rp_mean_flux=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "phot_rp_mean_flux")
            Yphot_rp_mean_flux=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "phot_rp_mean_flux")
            
            Xphot_bp_mean_flux_error=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "phot_bp_mean_flux_error")
            Yphot_bp_mean_flux_error=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "phot_bp_mean_flux_error")
            
            Xphot_rp_mean_flux_error=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "phot_rp_mean_flux_error")
            Yphot_rp_mean_flux_error=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "phot_rp_mean_flux_error")
            
            Xmass_flame_upper=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "mass_flame_upper")
            Ymass_flame_upper=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "mass_flame_upper")
            
            Xmass_flame_lower=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "mass_flame_lower")
            Ymass_flame_lower=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "mass_flame_lower")

            Xage_flame=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "age_flame")
            Yage_flame=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "age_flame")

            Xage_flame_upper=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "age_flame_upper")
            Yage_flame_upper=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "age_flame_upper")

            Xage_flame_lower=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "age_flame_lower")
            Yage_flame_lower=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "age_flame_lower")

            Xclassprob_dsc_specmod_binarystar=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "classprob_dsc_specmod_binarystar")
            Yclassprob_dsc_specmod_binarystar=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "classprob_dsc_specmod_binarystar")
        
            
            Xage_flame_lower=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].primary, "age_flame_lower")
            Yage_flame_lower=self.get_value_or_default(self.parent.starSystemList.binaryList[str(index+1)].star2, "age_flame_lower")

            Xgal_l=float(self.parent.starSystemList.binaryList[str(index+1)].primary.gal_l)
            Xgal_b=float(self.parent.starSystemList.binaryList[str(index+1)].primary.gal_b)
            Ygal_l=float(self.parent.starSystemList.binaryList[str(index+1)].star2.gal_l)
            Ygal_b=float(self.parent.starSystemList.binaryList[str(index+1)].star2.gal_b)
            #print (f"Xgal_b:{Xgal_b}",f"Ygal_b:{Ygal_b}")
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
                    'DIST_ERR':float(self.parent.starSystemList.binaryList[str(index+1)].primary.DIST_ERR),
                    'RUWE':XRUWE,
                    'mass_calc':Xmass_calc,
                    'mass_flame':Xmass_flame,
                    'mass_flame_upper':Xmass_flame_upper,
                    'mass_flame_lower':Xmass_flame_lower,
                    'age_flame':Xage_flame,
                    'age_flame_upper':Xage_flame_upper,
                    'age_flame_lower':Xage_flame_lower,
                    'gal_l':Xgal_l,
                    'gal_b':Xgal_b,
                    'classprob_dsc_specmod_binarystar':Xclassprob_dsc_specmod_binarystar,
                    'parallax_pmra_corr':Xparallax_pmra_corr,
                    'parallax_pmdec_corr':Xparallax_pmdec_corr,
                    'ra_parallax_corr':Xra_parallax_corr,
                    'dec_parallax_corr':Xdec_parallax_corr,
                    'ra_pmra_corr':Xra_pmra_corr,
                    'ra_pmdec_corr':Xra_pmdec_corr,
                    'dec_pmra_corr':Xdec_pmra_corr,
                    'dec_pmdec_corr':Xdec_pmdec_corr,
                    'pmra_pmdec_corr':Xpmra_pmdec_corr,
                    'phot_bp_mean_flux':Xphot_bp_mean_flux,
                    'phot_rp_mean_flux':Xphot_rp_mean_flux,
                    'phot_bp_mean_flux_error':Xphot_bp_mean_flux_error,
                    'phot_rp_mean_flux_error':Xphot_rp_mean_flux_error
                }
            except Exception:
                    self.parent.StatusBarProcessing (f'Skipped X record {index}')
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
                    print('RUWE'+str(XRUWE))
                    print('gal_b'+str(Xgal_b))
                    print('mass_calc'+str(Xmass_calc))
                    print('mass_flame'+str(Xmass_flame))
                    print('mass_flame_upper'+str(Xmass_flame_upper))
                    print('mass_flame_lower'+str(Xmass_flame_lower))
                    print('gal_l'+str(Xgal_l))
                    print('gal_b'+str(Xgal_b))
                    print('age_flame'+str(Xage_flame))
                    print('age_flame_upper'+str(Xage_flame_upper))
                    print('age_flame_lower'+str(Xage_flame_lower))
                    print('classprob_dsc_specmod_binarystar'+str(Xclassprob_dsc_specmod_binarystar))
                    print('parallax_pmra_corr'+str(Xparallax_pmra_corr))
                    print('parallax_pmdec_corr'+str(Xparallax_pmdec_corr))
                    print('ra_parallax_corr'+str(Xra_parallax_corr))
                    print('dec_parallax_corr'+str(Xdec_parallax_corr))
                    print('ra_pmra_corr'+str(Xra_pmra_corr))
                    print('ra_pmdec_corr'+str(Xra_pmdec_corr))
                    print('dec_pmra_corr'+str(Xdec_pmra_corr))
                    print('dec_pmdec_corr'+str(Xdec_pmdec_corr))
                    print('pmra_pmdec_corr'+str(Xpmra_pmdec_corr))
                    print('phot_bp_mean_flux'+str(Xphot_bp_mean_flux))
                    print('phot_rp_mean_flux'+str(Xphot_rp_mean_flux))
                    print('phot_bp_mean_flux_error'+str(Xphot_bp_mean_flux_error))
                    print('phot_rp_mean_flux_error'+str(Xphot_rp_mean_flux_error))
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
                    'DIST_ERR':float(self.parent.starSystemList.binaryList[str(index+1)].star2.DIST_ERR),
                    'RUWE':YRUWE,
                    'mass_flame':Ymass_flame,
                    'mass_calc':Ymass_calc,
                    'mass_flame_upper':Ymass_flame_upper,
                    'mass_flame_lower':Ymass_flame_lower,
                    'age_flame':Yage_flame,
                    'age_flame_upper':Yage_flame_upper,
                    'age_flame_lower':Yage_flame_lower,
                    'gal_l':Ygal_l,
                    'gal_b':Ygal_b,
                    'classprob_dsc_specmod_binarystar':Yclassprob_dsc_specmod_binarystar,
                    'parallax_pmra_corr':Yparallax_pmra_corr,
                    'parallax_pmdec_corr':Yparallax_pmdec_corr,
                    'ra_parallax_corr':Yra_parallax_corr,
                    'dec_parallax_corr':Ydec_parallax_corr,
                    'ra_pmra_corr':Yra_pmra_corr,
                    'ra_pmdec_corr':Yra_pmdec_corr,
                    'dec_pmra_corr':Ydec_pmra_corr,
                    'dec_pmdec_corr':Ydec_pmdec_corr,
                    'pmra_pmdec_corr':Ypmra_pmdec_corr,
                    'phot_bp_mean_flux':Yphot_bp_mean_flux,
                    'phot_rp_mean_flux':Yphot_rp_mean_flux,
                    'phot_bp_mean_flux_error':Yphot_bp_mean_flux_error,
                    'phot_rp_mean_flux_error':Yphot_rp_mean_flux_error
                }
            except Exception:
                    print (f'Skipped Y record {index}')
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
                    print('mass_calc'+str(Ymass_calc))
                    print('mass_flame'+str(Ymass_flame))
                    print('mass_flame_upper'+str(Ymass_flame_upper))
                    print('mass_flame_lower'+str(Ymass_flame_lower))
                    print('gal_l'+str(Ygal_l))
                    print('gal_b'+str(Ygal_b))
                    print('age_flame'+str(Yage_flame))
                    print('age_flame_upper'+str(Yage_flame_upper))
                    print('age_flame_lower'+str(Yage_flame_lower))
                    print('classprob_dsc_specmod_binarystar'+str(Xclassprob_dsc_specmod_binarystar))
                    print('parallax_pmra_corr'+str(Yparallax_pmra_corr))
                    print('parallax_pmdec_corr'+str(Yparallax_pmdec_corr))
                    print('ra_parallax_corr'+str(Yra_parallax_corr))
                    print('dec_parallax_corr'+str(Ydec_parallax_corr))
                    print('ra_pmra_corr'+str(Yra_pmra_corr))
                    print('ra_pmdec_corr'+str(Yra_pmdec_corr))
                    print('dec_pmra_corr'+str(Ydec_pmra_corr))
                    print('dec_pmdec_corr'+str(Ydec_pmdec_corr))
                    print('pmra_pmdec_corr'+str(Ypmra_pmdec_corr))
                    print('phot_bp_mean_flux'+str(Yphot_bp_mean_flux))
                    print('phot_rp_mean_flux'+str(Yphot_rp_mean_flux))
                    print('phot_bp_mean_flux_error'+str(Yphot_bp_mean_flux_error))
                    print('phot_rp_mean_flux_error'+str(Yphot_rp_mean_flux_error))
                    self.dbload.SetBackgroundColour(Colour(150,20,20))
                    self.dbload.Enable()
                    return
            self.parent.binaryDetail.append([abs(R), abs(Rerr), abs(V[0]), abs(Verr[0]), abs(V[1]), abs(Verr[1]), abs(M), int(healpix), abs(V_spher_corr)])
            
            if include:
       
                self.createExportRecord(self.parent.X[index], self.parent.Y[index], index)

        self.parent.export=pd.DataFrame(self.parent.export)
        self.dbload.SetLabel(u"DB Load")
        
        ROWCOUNTMATRIX['ADQL']=len(self.parent.selectedStarBinaryMappings)
        self.static_Total.SetLabel(f'{int(len(self.parent.star_rows)/2):,}')
        self.parent.StatusBarProcessing('End DB Load')
        
        #self.parent.selectedStarIDs=pd.DataFrame(self.parent.selectedStarIDs, columns=['source_id'])
        self.parent.selectedStarBinaryMappings=pd.DataFrame.from_dict(self.parent.selectedStarBinaryMappings, orient='index')#, columns=['i', 'SOURCE_ID_PRIMARY', 'SOURCE_ID_SECONDARY'
        self.parent.status=pd.DataFrame(self.parent.status, columns=['include', 'notgroup', 'radialvelocity', 'pairnumber'])
        self.parent.status['dataLoadOut']=self.parent.status['include'].copy()
        self.parent.status['populateOut']=self.parent.status['include'].copy()
        self.parent.status['hrOut']=self.parent.status['include'].copy()
        self.parent.status['kineticOut']=self.parent.status['include'].copy()
        self.parent.status['massVmassOut']=self.parent.status['include'].copy()
        self.parent.status['tfOut']=self.parent.status['include'].copy()
        self.parent.binaryDetail=pd.DataFrame(self.parent.binaryDetail, columns=['r','r_err','vRA','vRAerr','vDEC','vDECerr', 'M', 'healpix', 'V_spher_corr'])
        self.parent.X=pd.DataFrame.from_dict(self.parent.X, orient='index') #, columns=['ra','dec','BminusR', 'mag']pd.DataFrame.from_dict(data, orient='index')
        self.parent.Y=pd.DataFrame.from_dict(self.parent.Y, orient='index') #, columns=['ra','dec','BminusR', 'mag'])
        self.parent.star_rows=pd.DataFrame.from_dict(self.parent.starSystemList.getStar_rows(), orient='index') #, columns=column_names)
        
        # Calculate 2D velocity using Pythagoras: v2D = sqrt(vRA^2 + vDEC^2)
        self.parent.binaryDetail['v2D'] = np.sqrt(self.parent.binaryDetail['vRA']**2 + self.parent.binaryDetail['vDEC']**2)
        
        # Calculate 2D v_Tilde using v2D/np.sqrt(G (M1 + M2)/r_sky)
        
        G=float(gl_cfg.getItem('g','RETRIEVAL', 4.30E-03))
        print(self.parent.X)
        self.parent.binaryDetail['v_tilde'] = self.parent.binaryDetail['v2D'] /np.sqrt(G*(self.parent.X['mass_calc'] + self.parent.Y['mass_calc'])/self.parent.binaryDetail['r'])
        
        # Calculate r_mond using np.sqrt(G (M1 + M2)/a_0)
        #km_pc=float(gl_cfg.getItem('km_pc','RETRIEVAL'))
        G2=float(gl_cfg.getItem('g2','RETRIEVAL', 1.393e-13))
        a_0=float(gl_cfg.getItem('a_0','RETRIEVAL', 1.2E-10))
        self.parent.binaryDetail['r_mond'] = np.sqrt(G2*(self.parent.X['mass_calc'] + self.parent.Y['mass_calc'])/(a_0))
        self.parent.binaryDetail['r_over_r_mond'] = self.parent.binaryDetail['r']/self.parent.binaryDetail['r_mond']
        self.parent.binaryDetail['r_over_r_mond_err'] = self.parent.binaryDetail['r_err']/self.parent.binaryDetail['r_mond']
        
        # Optionally, calculate the error in 2D velocity using error propagation:
        # v2D_error = sqrt((vRA * vRAerr)^2 + (vDEC * vDECerr)^2) / v2D
        self.parent.binaryDetail['v2D_err'] = np.sqrt(
            (self.parent.binaryDetail['vRA'] * self.parent.binaryDetail['vRAerr'])**2 + 
            (self.parent.binaryDetail['vDEC'] * self.parent.binaryDetail['vDECerr'])**2
        ) 
        
        self.parent.binaryDetail['v_tilde_err'] = self.parent.binaryDetail['v2D_err'] /np.sqrt(G*(self.parent.X['mass_calc'] + self.parent.Y['mass_calc'])/self.parent.binaryDetail['r'])
        self.parent.binaryDetail['v_tilde_sph_corr'] = self.parent.binaryDetail['V_spher_corr'] /np.sqrt(G*(self.parent.X['mass_calc'] + self.parent.Y['mass_calc'])/self.parent.binaryDetail['r'])
        #print(self.parent.X)
        
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
        
        self.parent.StatusBarNormal('DB Load completed OK')
        
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


# Always do all
        f"""
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
        """
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
            
                """
# Always do all
        """
                    {commentHP} and b.SOURCE_ID_PRIMARY < {healpix}
                    {commentRA} and o1.RA_ < {i}  and o2.RA_ < {i}
                    {commentDec} and o1.DEC_ < {i}  and o2.DEC_ < {i} and o1.DEC_ > {-i}  and o2.DEC_ > {-i}
                    {commentPx} and o1.PARALLAX > {i} and o2.PARALLAX > {i}
        """
 #and b.HAS_RADIAL_VELOCITY = False
        print(sql)
        print (iStro)
        print(database)
        records = pd.read_sql(sql, iStro)

        lenArray=len(records)
        print(lenArray)
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
                self.parent.StatusBarProcessing(f'Deselecting binaries with no RV - {label:,.1f}%')
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
#            self.static_RVnull.SetLabel(f'{row[0]:,}')
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
        
    def moveBinaries(self, event):
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
        fgsizer = wx.FlexGridSizer(cols=14, hgap=0, rows=3, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
        # Headings (ie row 1)
                
        # Signal to noise ratio for Px
        self.static_parallax = StaticText(self, label='Px S/N') 
        fgsizer.Add(self.static_parallax, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for Red Magnitude
        self.static_red_mag = StaticText(self, label='RP S/N') 
        fgsizer.Add(self.static_red_mag, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for Green Magnitude
        self.static_green_mag = StaticText(self, label='G S/N') 
        fgsizer.Add(self.static_green_mag, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        # Signal to noise ratio for Blue Magnitude
        self.static_blue_mag = StaticText(self, label='BP S/N') 
        fgsizer.Add(self.static_blue_mag, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Signal to noise ratio for PMRA and PMDEC
        self.pmsnratio = StaticText(self, label='pm S/N') 
        fgsizer.Add(self.pmsnratio, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Difference in radial veocities between the two stars.
        self.static_diff_radial_velocity = StaticText(self, label='diff in rad. vel.') 
        fgsizer.Add(self.static_diff_radial_velocity, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_ruwe = StaticText(self, label='RUWE') 
        fgsizer.Add(self.static_ruwe, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.static_b = StaticText(self, label='|b|')
        fgsizer.Add(self.static_b, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
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
        self.spin_diff_radial_velocity = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=0, max=500,initial=int(gl_cfg.getItem('rv_lt','FILTER',0)))
        fgsizer.Add(self.spin_diff_radial_velocity, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_diff_radial_velocity.SetToolTip("Difference in radial velocities between primary and companion stars.")
        
        #Max RUWE.
        self.text_ruwe = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('ruwe_lt','FILTER', 1), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_ruwe, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_ruwe.setValidRoutine(self.text_ruwe.Validate_Float)
        self.text_ruwe.SetToolTip("Maximum RUWE in either star.  Enter decimal x for RUWE < x")
        
        #Min |b|.
        self.text_b = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('b_gt','FILTER', 0), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_b, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_b.setValidRoutine(self.text_b.Validate_Float)
        self.text_b.SetToolTip("Minimum |b| from plan of Galaxy.  Enter decimal x for |b| > x")
        
        #Binary probability.
        self.text_binProbability = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('bin_probability_lt','FILTER', '0.1'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT)  
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
        
        
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel filter.")
        fgsizer.Add(self.cancel, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
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
                
        screen = Display()
        diff = int(1080 - screen.screen_height)
        ctrl_height = 750-diff
        
        self.listctrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(1920,ctrl_height), wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER | wx.VSCROLL | wx.LC_SORT_ASCENDING)
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
        attributes=[self.text_ruwe,self.text_b, self.text_binProbability, self.text_Min_Sepn, self.text_ageDiffMax]
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
        gl_cfg.setItem('b_gt',self.text_b.GetValue(),'FILTER')
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
        b_limit=float(self.text_b.GetValue())
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
        #`'binaryDetail', 'catalogPage', 'export', 'filterPage', 'hrPage', 'plottingPage', 'printArrays', 'releasePage', 'retrievalPage', 'selectedStarBinaryMappings', 'skyPage', 'starSystemList', 'star_rows'
        #print(self.parent.X.gal_b)
        for idxStar in statusIndicesList:
        #for idxStar, row in star_rows.iterrows():
            idxBin=int(idxStar/2)
            row=star_rows.iloc[idxStar]
            odd=(idxStar-2*idxBin)
            
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
                        print(f"row = {row}")
                        print(f"idxStar = {idxStar}")
                        print("star_rows = ", star_rows[:idxStar+2])
                        print("selectedStarBinaryMappings = ", selectedStarBinaryMappings[:int(idxStar/2+2)])
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
            
            if odd:
                #primaryPointer=self.parent.X.iloc[idxBin]
                #star2Pointer=self.parent.Y.iloc[idxBin]
                Xgal_b=float(self.parent.X.gal_b.iloc[idxBin])
                Ygal_b=float(self.parent.Y.gal_b.iloc[idxBin])
                prtTxt_gal_b=f'Cutoff ={round(b_limit,2)}, X|b|={round(float(Xgal_b),2)}, Y|b|={round(float(Ygal_b),2)}'
                #self.parent.StatusBarProcessing(excludeTxt)
                #include=0
                #print(prtTxt)
            #try:
            ##print(row)
            #b=float(self.parent.X.gal_b.iloc[idxBin])
            #except Exception:
            #    b=0
                
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

                if include and b_limit and odd:
                    Xb_row=abs(Xgal_b)
                    Yb_row=abs(Ygal_b)
                    #Exclude gal_b above limit (ie not available)
                    if Xb_row<=b_limit or Yb_row<=b_limit:
                        self.parent.StatusBarProcessing(prtTxt_gal_b)
                        include=0

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
                self.parent.status.loc[idxBin, 'include'] = 0
            odd=(idxStar-2*idxBin)
            if odd and self.parent.status.include[idxBin]:
                primaryPointer=self.parent.X.iloc[idxBin]
                star2Pointer=self.parent.Y.iloc[idxBin]
                self.createExportRecord(primaryPointer, star2Pointer, idxBin)
            excludeArr.append(excludeTxt)

        self.restoreListCtrl(txtArr=excludeArr)
        self.loadData.SetLabel(f'100%')
        self.parent.status['hrOut']=self.parent.status['include'].copy()
        self.parent.status['kineticOut']=self.parent.status['include'].copy()
        self.parent.status['massVmassOut']=self.parent.status['include'].copy()
        self.parent.status['tfOut']=self.parent.status['include'].copy()
        # Save pandas status file as pickle files for next time.

        self.saveConfFiles('populateOut')
        
        populateOut=self.parent.status['populateOut'].sum()
        self.dataInTotal.SetLabel(f'{populateOut:,}')
        self.loadData.Enable()
        #self.parent.printArrays()
        
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
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_v)
        fgsizer = wx.FlexGridSizer(cols=14, hgap=0, rows=2, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
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
        
        screen = Display()
        diff_h = int(1080 - screen.screen_height)
        diff_w = int(1920 - screen.screen_width)
        ctrl_height = 750-diff_h
        ctrl_width = 1350-diff_w
        # Draw velocity map
        #, projection='aitoff'
        try:
            self.skyGraph = MatplotlibPanel(parent=self, size=(ctrl_width, ctrl_height))
            self.fg2sizer.Add(self.skyGraph)
        except Exception as e:
            print("Error = ", e)
        
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
        
        #self.skyGraph.sizer.destroy()
        #
        #self.skyGraph.toolbar.destroy()
        
        #self.skyGraph.Destroy()
        
        prntVersion=self.prntVersionCheckBox.GetValue()
        gl_cfg.setItem('prntversion',prntVersion, 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('unselected',self.unselectedCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('allwhite',self.allWhiteCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('suppressgroups',self.suppressGroupsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('suppressrvzero',self.suppressRVZeroCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('galacticCoords',self.showGalacticCoordsCheckBox.GetValue(), 'SKYPLOT') # save setting in config file
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        
        #print(self.parent.X.ra)
        
        xdata1 = pd.DataFrame(self.parent.X.ra * self.parent.status['include'], columns=['ra'])
        ydata1 = pd.DataFrame(self.parent.X.dec * self.parent.status['include'], columns=['dec'])
        xdata2 = pd.DataFrame(self.parent.X.ra, columns=['ra'])
        ydata2 = pd.DataFrame(self.parent.X.dec, columns=['dec'])
        self.skyGraph.axes.set_yscale('linear')
        self.skyGraph.axes.set_xscale('linear')
        
        if self.showGalacticCoordsCheckBox.GetValue():
            #self.skyGraph.set_limits([-180,180],[-90, 90])
            self.skyGraph.axes.set_xlim(-180, 180)
            self.skyGraph.axes.set_ylim(-90, 90)
            self.skyGraph.axes.set_xticks(range(-180, 181, 30))  # Longitude ticks every 30 degrees
            self.skyGraph.axes.set_yticks(range(-90, 91, 30))    # Latitude ticks every 30 degrees
        else:
            #self.skyGraph.set_limits([360,0],[-90, 90])
            self.skyGraph.axes.set_xlim(360, 0)
            self.skyGraph.axes.set_ylim(-90, 90)
        
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
                #l=[]
                xdata2.ra = self.parent.X.gal_l
                ydata2.dec = self.parent.X.gal_b 
            
            marker = ','
            markersize=1
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
                markersize=1.5
            try:
                data0={'x':xdata2.ra.to_list(),
                       'y':ydata2.dec.to_list(),
                       'color':c,
                       'marker':marker,
                       'linestyle':'none',
                       'linewidth':0,
                       'markersize':markersize}
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
            #l=[]
            #b=[]
            #for i in range(len(xdata1.ra)):
            #    #if not self.parent.status.include.iloc[i]:
            #    #    continue
            #    # Convert to Galactic Coords.
            #    sc = SkyCoord(ra=xdata1.ra[i]*u.deg,dec=ydata1.dec[i]*u.deg)
            #    gal_l=str(sc.galactic.l)
            #    try:
            #        deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_l)
            #    except:
            #        self.parent.StatusBarProcessing(f'Missing decimal point in gal_l={gal_l}')
            #        deg, minutes, seconds, fraction  =  re.split('[dms]', gal_l)
            #    gal_l=float(deg) + float(minutes)/60  + float(seconds)/3600
            #    gal_l=(gal_l+180) % 360 -180
            #    l.append(gal_l)
            #    
            #    gal_b=str(sc.galactic.b)
            #    try:
            #        deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_b)
            #    except:
            #        self.parent.StatusBarProcessing(f'Missing decimal point in gal_b={gal_b}')
            #        deg, minutes, seconds, fraction  =  re.split('[dms]', gal_b)
            #    gal_b=float(deg) + float(minutes)/60 + float(seconds)/3600
            #    b.append(gal_b)
            #xdata1.ra=l
            #ydata1.dec=b
            xdata1.ra = self.parent.X.gal_l  * self.parent.status['include']
            ydata1.dec = self.parent.X.gal_b  * self.parent.status['include']
        try:
            #data1={'x':xdata1.ra.to_list(),
            #       'y':ydata1.dec.to_list(),
            #       'color':c,
            #       'marker':marker,
            #       'linestyle':'none',
            #       'linewidth':0,
            #       'markersize':markersize}
            self.line, = self.skyGraph.axes.plot(xdata1.ra.to_list(), ydata1.dec.to_list(), color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize)
        except Exception as e:
            self.parent.StatusBarProcessing (f'self.skyGraph.axes.plot Crash 2) "{e}"')
            print(xdata1)
            print(ydata1)
            self.plot_but.SetBackgroundColour(Colour(150,20,20))
            self.plot_but.Enable()
            return
        #self.skyGraph = MatplotlibPanel(parent=self, size=(1350, 750)) #, projection='aitoff', data=[data0, data1]
        #self.fg2sizer.Add(self.skyGraph)
        
        
        legend1.append(self.line)
        legend2.append('selected')
        self.skyGraph.axes.legend(legend1, legend2)
        if prntVersion:
            self.skyGraph.axes.get_legend().remove()
            
        if self.showGalacticCoordsCheckBox.GetValue():
            self.skyGraph.axes.set_ylabel("Galactic b (deg)", fontsize=FONTSIZE+4)
            self.skyGraph.axes.set_xlabel("Galactic l (deg)", fontsize=FONTSIZE+4)
        else:
            self.skyGraph.axes.set_ylabel('Declination (deg)', fontsize=FONTSIZE+4)
            self.skyGraph.axes.set_xlabel('Right Ascension (deg)', fontsize=FONTSIZE+4)

        self.skyGraph.draw(self.line, xdata1, ydata1, True,[] )
        #
        self.skyGraph.axes.tick_params(axis='both', which='major', labelsize=FONTSIZE+4)
        self.skyGraph.axes.tick_params(axis='both', which='minor', labelsize=FONTSIZE+4)

        self.skyGraph.figure.canvas.draw()
        try:   
            self.skyGraph.Layout()
        except Exception as e:
            print(f"Exception occurred: {e}")
        self.Layout()

        self.plot_but.Enable()
        
        self.parent.StatusBarNormal('Completed OK')
        
class HRDataPlotting(masterProcessingPanel):

# Plot HR diagram for chosen binaries.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_v)
        fgsizer = wx.FlexGridSizer(cols=15, hgap=0, rows=4, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
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

        # Create 'M_Kref' check box
        M_Kref_StaticText = StaticText(self, id=wx.ID_ANY, label="M_Kref")
        fgsizer.Add(M_Kref_StaticText, 0, wx.ALL, 2)
        self.M_KrefCheckBox = CheckBox(self)
        self.M_KrefCheckBox.SetToolTip("Produce print version of graph.")
        self.M_KrefCheckBox.SetValue(gl_cfg.getBoolean('m_krefversion', 'HRPLOT'))
        fgsizer.Add(self.M_KrefCheckBox, 0, wx.ALL, 2)

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
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel H-R filter.")
        fgsizer.Add(self.cancel, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # H-R Filter Reset button
        
        self.Reset_but = Button(self, id=wx.ID_ANY, label="&Reset", pos=wx.DefaultPosition,size=wx.DefaultSize)
        self.Reset_but.Bind(wx.EVT_BUTTON, self.OnReset)
        fgsizer.Add(self.Reset_but, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Draw velocity map

        screen = Display()
        diff_h = int(1080 - screen.screen_height)
        diff_w = int(1920 - screen.screen_width)
        ctrl_height = 750-diff_h
        ctrl_width = 1350-diff_w
        try:
            self.hrGraph = MatplotlibPanel(parent=self, size=(950, ctrl_height))
            self.fg2sizer.Add(self.hrGraph)
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
        
        self.parent.StatusBarProcessing('H-R filter commenced')
        
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
        gl_cfg.setItem('m_kref',self.M_KrefCheckBox.GetValue(), 'HRPLOT') # save setting in config file
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
                self.parent.status.loc[index, 'include'] = 0
                continue
            
            (Yup, Ydown)=self.XreturnY(X2.BminusR)
            if float(X2.mag) < Yup or float(X2.mag) > Ydown or float(X2.BminusR) < colourLower or float(X2.BminusR) > colourUpper :
                self.parent.status.loc[index, 'include'] = 0
                continue

            self.createExportRecord(X1, X2, index)
        
        self.parent.status['kineticOut']=self.parent.status['include'].copy()
        self.parent.status['massVmassOut']=self.parent.status['include'].copy()
        self.parent.status['tfOut']=self.parent.status['include'].copy()
        self.parent.status['numberOut']=self.parent.status['include'].copy()
        self.parent.status['hrOut']=self.parent.status['include'].copy()
        self.saveConfFiles('hrOut')
        self.OnPlot()
        label=int(100)
        self.Filter_but.SetLabel(f'{label:,.1f}%')
        self.Filter_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
    #def XreturnY(self, X):
    #    # Return range of acceptable magnitudes.
    #    Y=float(self.m*float(X) + float(self.c))
    #
    #    return [Y-self.Yerr,Y+self.Yerr]

    def XreturnY(self, X):
        try:
            X = float(X)  # Ensure X is a float
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid value for X: {X}") from e
        Y = float(self.m * X + self.c)
        return [Y - self.Yerr, Y + self.Yerr]
        
    # Define the function to map ruwe values to colors, considering selected/unselected status
    def map_colors(self, value, is_selected):
        if value <= 1.25:
            return 'lightblue' if is_selected else 'lightblue'  # Strong/Faint blue for ruwe <= 1.25
        elif 1.25 <= value <= 1.4:
            return 'lightcoral' if is_selected else 'lightcoral'  # Strong/Faint amber for 1.25 <= ruwe <= 1.4
        elif value > 1.4:
            return 'lightpink' if is_selected else 'lightpink'  # Strong/Faint red for ruwe > 1.4
        else:
            return 'gray' if is_selected else 'gray'  # Strong/Faint gray as default

    def OnPlot(self, event=0):

        global CANCEL
        CANCEL = False
        self.plot_but.Disable()
        # Draw velocity map
        xdata1=pd.concat([self.parent.X.BminusR * self.parent.status['include'], self.parent.Y.BminusR * self.parent.status['include']])
        ydata1=pd.concat([self.parent.X.mag * self.parent.status['include'], self.parent.Y.mag * self.parent.status['include']])
        selected=pd.concat([self.parent.status['include'], self.parent.status['include']])
        cdata1=pd.concat([self.parent.X.RUWE * self.parent.status['include'], self.parent.Y.RUWE * self.parent.status['include']])
        xdata2=pd.concat([self.parent.X.BminusR, self.parent.Y.BminusR])
        xdata2=xdata2.tolist()
        ydata2=pd.concat([self.parent.X.mag, self.parent.Y.mag])
        ydata2=ydata2.tolist()

        self.hrGraph.axes.set_ylabel('$M_G$', fontsize=FONTSIZE, rotation='horizontal')
        self.hrGraph.axes.set_xlabel('$BP - RP$', fontsize=FONTSIZE)
        self.hrGraph.axes.set_yscale('linear')
        self.hrGraph.axes.set_xscale('linear')
        self.hrGraph.set_limits([-.5,4],[18, -2.5])
        
        # To remove the artist
        for frame in self.hrGraph.frames:
            try:
                Artist.remove(frame)
            except Exception as e:
                print(f"Error occurred: {e}")
        try:
            self.line1.remove()
        except Exception as e:
            print(f"Error removing line1: {e}")

        try:
            self.line2.remove()
        except Exception as e:
            print(f"Error occurred: {e}")

        try:
            self.ol_line.remove()
        except Exception as e:
            print(f"Error occurred: {e}")

#        try:
#            if hasattr(self, 'cbar') and self.cbar:
#                self.cbar.remove()
#                self.cbar = None
#        except Exception as e:
            print(f"Error removing colorbar: {e}")
    
        unselectedBins=0
        M_Kref=self.M_KrefCheckBox.GetValue()
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
            ##Display graph
            try:
                self.line2, = self.hrGraph.axes.plot(xdata2, ydata2, color=c, marker=marker, linestyle='none', linewidth=0, markersize=markersize, zorder=1)
            except Exception:
                print(xdata2)
                print(ydata2)
            
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
    
        # Saves plot
        
        marker = ','
        markersize=1
        if self.largePointsCheckBox.GetValue():
            marker = 'o'
            markersize=1.5
        # Apply the map_colors function to the pandas Series using a lambda function to pass the selected value
        colors = pd.Series([self.map_colors(value, selected_val) for value, selected_val in zip(cdata1, selected)])

        xdata1=xdata1.tolist()
        ydata1=ydata1.tolist()
        cdata1=cdata1.tolist()

        # Define custom colors: green for <= 1.25, amber for 1.25 to 1.4, and red for > 1.4
        colors = ['blue', 'yellow', 'red']
        
        # Create a custom colormap
        cmap = ListedColormap(colors)
        
        # Define color boundaries (bins for the colorbar)
        bounds = [0, 1.25, 1.4, 2]  # RUWE values that correspond to the color changes
        norm = BoundaryNorm(bounds, cmap.N)

        self.line1 = self.hrGraph.axes.scatter(xdata1, ydata1, c=cdata1, cmap=cmap, norm=norm, marker=marker, s=markersize**2, zorder=2)
        #self.line1 = self.hrGraph.axes.scatter(xdata1, ydata1, c=cdata1, cmap='jet', vmin=1, vmax=1.5, marker=marker, s=markersize**2, zorder=2)
        # visualizing the mapping from values to colors
        if not hasattr(self, 'cbar'):
            # Add a colorbar
            self.cbar = self.hrGraph.figure.colorbar(self.line1, ax=self.hrGraph.axes,  ticks=[0, 1.25, 1.4, 2])  # You can adjust ticks based on your data range
            self.cbar.set_label('RUWE', fontsize=FONTSIZE)  # Add a label to the colorbar
            self.cbar.ax.tick_params(labelsize=FONTSIZE)  # Set tick label font size
        #legend1.append(self.line1)
        #legend2.append('Selected binaries')
        self.hrGraph.draw(self.line1, xdata1, ydata1, True,[] )
                
        if M_Kref:
            # Calculate Overluminosity values
            x_ol = np.linspace(-0.5, 4, 100)  # Generate x values (BP - RP)
            y_ol = 2.5 + (2.9 * x_ol)  # Compute M_G values using the formula

            # Plot the Overluminosity line
            self.ol_line, = self.hrGraph.axes.plot(x_ol, y_ol, color='cyan', linestyle='--', linewidth=2, label="Overluminosity")

            # Redraw the graph with the new line
            self.hrGraph.draw(self.ol_line, x_ol, y_ol, True, [])

        # Adjust layout after adding the colorbar
        #self.hrGraph.figure.tight_layout()
        self.hrGraph.figure.subplots_adjust()
        #    """
        #Attach a text label above each bar displaying its height
        #"""
        self.hrGraph.frames=[] 
        try:
            self.hrGraph.Layout()
        except Exception as e:
            print(f"Error occurred: {e}")
        self.Layout()

        self.parent.status['massVmassOut']=self.parent.status['include'].copy()
        self.parent.status['tfOut']=self.parent.status['include'].copy()
        self.parent.status['numberOut']=self.parent.status['include'].copy()
        self.saveConfFiles('hrOut')
        
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        self.plot_but.Enable()

        self.parent.StatusBarNormal(f'Completed OK')
        
class kineticDataPlotting(masterProcessingPanel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=19, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
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
        self.static_above_below = StaticText(self, label='Deselect above/\nbelow line') 
        fgsizer.Add(self.static_above_below, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.static_x_TopLeft = StaticText(self, label='x (Top Left)') 
        fgsizer.Add(self.static_x_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_y_TopLeft = StaticText(self, label='y (Top Left)') 
        fgsizer.Add(self.static_y_TopLeft , 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_x_BottomRight = StaticText(self, label='x (Bottom\nRight)') 
        fgsizer.Add(self.static_x_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_y_BottomRight = StaticText(self, label='y (Bottom\nRight)') 
        fgsizer.Add(self.static_y_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)     
        
        # Upper cutoff
        self.static_upperCutoff = StaticText(self, label='Upper v2D\ncutoff') 
        fgsizer.Add(self.static_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Upper cutoff
        self.static_v_tilde_upperCutoff = StaticText(self, label='Upper v-tilde\ncutoff') 
        fgsizer.Add(self.static_v_tilde_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # v x err reporting threshold.
        self.static_vxerrCutoff = StaticText(self, label="v/dv t'hold") 
        fgsizer.Add(self.static_vxerrCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)        
        
        # Lower bin cutoff header
        lowerBinCutoff_StaticText = StaticText(self, id=wx.ID_ANY, label="Lower Bin cutoff")
        fgsizer.Add(lowerBinCutoff_StaticText, 0, wx.ALL, 2)
        #T Reduce occupancy of bin
        self.static_binReduction = StaticText(self, label='Minus Bin %') 
        fgsizer.Add(self.static_binReduction, 0, wx.ALIGN_LEFT|wx.ALL, 5)
       
        self.static_xAverage = StaticText(self, label='x Average') 
        fgsizer.Add(self.static_xAverage, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yLog1 = StaticText(self, label='y axis') 
        fgsizer.Add(self.static_yLog1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_yLog = StaticText(self, label='y avg') 
        fgsizer.Add(self.static_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.static_xy_option = StaticText(self, label='x-y options') 
        fgsizer.Add(self.static_xy_option, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Axis limits
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','KINETIC', 5)))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer umber of bins to divide x-scale into.")
        BoxWidth = 60
        self.textctrl_xLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_lower','KINETIC', .0001), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xLower.SetToolTip("Lower end of x-scale.")
        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','KINETIC', .1), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_yLower = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_lower','KINETIC', .1), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yLower.SetToolTip("Lower end of y-scale.")
        self.textctrl_yUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_upper','KINETIC', 5), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_yUpper.SetToolTip("Upper end of y-scale.")       
        
        self.combo_deselect_aboveBelow = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['None', 'Above', 'Below'], value='')
        self.combo_deselect_aboveBelow.SetSelection(int(gl_cfg.getItem('above-below-line','KINETIC', 0)))
        self.combo_deselect_aboveBelow.SetToolTip("Choose above or below.  Above removes outliers above the line, below removes stars below the line.")
        fgsizer.Add(self.combo_deselect_aboveBelow, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Outlier values
        self.text_x_TopLeft = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_topLeft','KINETIC', .004), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT) 
        self.text_x_TopLeft.SetToolTip("Top left x of outlier line.") 
        fgsizer.Add(self.text_x_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_y_TopLeft = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_topLeft','KINETIC', 4), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        self.text_y_TopLeft.SetToolTip("Top left y of outlier line.") 
        fgsizer.Add(self.text_y_TopLeft, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_x_BottomRight = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_bottomRight','KINETIC', .1), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        self.text_x_BottomRight.SetToolTip("Bottom right x of outlier line.") 
        fgsizer.Add(self.text_x_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_y_BottomRight = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('y_bottomRight','KINETIC', 1), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        self.text_y_BottomRight.SetToolTip("Bottom right y of outlier line.") 
        fgsizer.Add(self.text_y_BottomRight, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Upper v2Dcutoff
        self.text_upperCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_cutoff','KINETIC', 4), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_upperCutoff.SetToolTip("Value of 2D velocity in the plane of sky above which values will be ignored.")
        
        # Upper v-tilde cutoff
        self.text_v_tilde_upperCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('upper_v_tilde_cutoff','KINETIC', 2.0), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.text_v_tilde_upperCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.text_v_tilde_upperCutoff.SetToolTip("Value of v-tilde velocity above which values will be ignored.")
        
        # v x err reporting threshold
        self.text_vxerrCutoff = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('v_dv_cutoff','KINETIC', 0), pos=wx.DefaultPosition,size=(BoxWidth,-1), style=wx.ALIGN_RIGHT)  
        self.text_vxerrCutoff.SetToolTip("v/v_error reporting threshold.")
        fgsizer.Add(self.text_vxerrCutoff, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Lower bin cutoff textctrl
        self.lowerBinCutoffTextCtrl = SpinCtrl(self, id=wx.ID_ANY, value='', pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=99,initial=int(gl_cfg.getItem('lower_bin_cutoff','KINETIC', 5)))   
        self.lowerBinCutoffTextCtrl.SetToolTip("Enter number below which occupancy not to display bins.")
        fgsizer.Add(self.lowerBinCutoffTextCtrl, 0, wx.ALL, 2)
        
        self.combo_binReduction = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15'], value='')
        self.combo_binReduction.SetSelection(int(gl_cfg.getItem('combo-bin-reduction','KINETIC', 0)))
        self.combo_binReduction.SetToolTip("Percentage of fast stars to remove from each bin to account for CBs and flybys.")
        fgsizer.Add(self.combo_binReduction, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.combo_xAvg = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['centre','mean'], value='')
        self.combo_xAvg.SetSelection(int(gl_cfg.getItem('x_avg','KINETIC', 0)))
        self.combo_xAvg.SetToolTip("Geometric mean of separations.")
        fgsizer.Add(self.combo_xAvg, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.combo_yLog = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['log','normal'], value='')
        self.combo_yLog.SetSelection(int(gl_cfg.getItem('y_scale','KINETIC', 0)))
        #self.combo_yLog.Hide()
        fgsizer.Add(self.combo_yLog, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.combo_yAvg = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['rms','mean', 'median'], value='')
        self.combo_yAvg.SetSelection(int(gl_cfg.getItem('y_avg','KINETIC', 0)))
        self.combo_yAvg.SetToolTip("Use RMS, mean or median.")
        #self.combo_yAvg.Hide()
        fgsizer.Add(self.combo_yAvg, 0, wx.ALIGN_LEFT|wx.ALL, 5)
                
        self.combo_xy_option = Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=['(r,v-sky)','(r,v-tilde)','(r/r-mond,v-tilde)','(r/r-mond,v-sky)'], value='')
        self.combo_xy_option.SetSelection(int(gl_cfg.getItem('xy_option','KINETIC', 0)))
        self.combo_xy_option.SetToolTip("XY axis options.")
        #self.combo_yAvg.Hide()
        fgsizer.Add(self.combo_xy_option, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        # Create show bins check box
        showRABinsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bins\n(RA|Dec)")
        fgsizer.Add(showRABinsStaticText, 0, wx.ALL, 2)
        self.showBinsCheckBox = CheckBox(self)
        self.showBinsCheckBox.SetValue(gl_cfg.getBoolean('showbins','KINETIC'))
        self.showBinsCheckBox.SetToolTip("Display 1D RA & Dec data in bins.")
        fgsizer.Add(self.showBinsCheckBox, 0, wx.ALL, 2)
        
        # Create newtonian_ check box
        newtonian_StaticText = StaticText(self, id=wx.ID_ANY, label="Newtonian\nline")
        fgsizer.Add(newtonian_StaticText, 0, wx.ALL, 2)
        
        # Create newtonian_ check box
        self.newtonian_CheckBox = CheckBox(self)
        self.newtonian_CheckBox.SetValue(gl_cfg.getBoolean('newtonian','KINETIC'))
        self.newtonian_CheckBox.SetToolTip("Show Newtonian line.")
        fgsizer.Add(self.newtonian_CheckBox, 0, wx.ALL, 2)
                
        # Create Mond check box
        mond_StaticText = StaticText(self, id=wx.ID_ANY, label="MOND line")
        fgsizer.Add(mond_StaticText, 0, wx.ALL, 2)
        
        # Create Mond check box
        self.mond_CheckBox = CheckBox(self)
        self.mond_CheckBox.SetValue(gl_cfg.getBoolean('norm','KINETIC'))
        self.mond_CheckBox.SetToolTip("Show MOND line.")
        fgsizer.Add(self.mond_CheckBox, 0, wx.ALL, 2)
                
        # Create show raw data check box
        rawDataStaticText = StaticText(self, id=wx.ID_ANY, label="Show raw\ndata")
        fgsizer.Add(rawDataStaticText, 0, wx.ALL, 2)
        self.rawDataCheckBox = CheckBox(self)
        self.rawDataCheckBox.SetValue(gl_cfg.getBoolean('rawdata', 'KINETIC'))
        self.rawDataCheckBox.SetToolTip("Display raw data on graph.")
        fgsizer.Add(self.rawDataCheckBox, 0, wx.ALL, 2)

        # Create show outlier line check box
        outlierStaticText = StaticText(self, id=wx.ID_ANY, label="Show outlier\nline")
        fgsizer.Add(outlierStaticText, 0, wx.ALL, 2)
        self.outlierLineCheckBox = CheckBox(self)
        self.outlierLineCheckBox.SetValue(gl_cfg.getBoolean('outlierline', 'KINETIC'))
        self.outlierLineCheckBox.SetToolTip("Show outlier line on graph.")
        fgsizer.Add(self.outlierLineCheckBox, 0, wx.ALL, 2)

        # Create show large data points
        largeStaticText = StaticText(self, id=wx.ID_ANY, label="Show large\ndata points")
        fgsizer.Add(largeStaticText, 0, wx.ALL, 2)
        self.largePointsCheckBox = CheckBox(self)
        self.largePointsCheckBox.SetValue(gl_cfg.getBoolean('largepoints', 'KINETIC'))
        self.largePointsCheckBox.SetToolTip("Shows larger dec & ra data points for actual stars on graph.")
        fgsizer.Add(self.largePointsCheckBox, 0, wx.ALL, 2)

        ## Create show labels line check box
        #labelsStaticText = StaticText(self, id=wx.ID_ANY, label="Show bin labels")
        #fgsizer.Add(labelsStaticText, 0, wx.ALL, 2)
        #self.showLabelsCheckBox = CheckBox(self)
        #self.showLabelsCheckBox.SetValue(gl_cfg.getBoolean('showlabels','KINETIC'))
        #self.showLabelsCheckBox.SetToolTip("Show labels above bins on graph.")
        #fgsizer.Add(self.showLabelsCheckBox, 0, wx.ALL, 2)

        # Create 'print version' check box
        prntVersion_StaticText = StaticText(self, id=wx.ID_ANY, label="Print\nVersion")
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
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel binning.")
        fgsizer.Add(self.cancel, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw velocity map
        screen = Display()
        diff_h = int(1080 - screen.screen_height)
        diff_w = int(1920 - screen.screen_width)
        ctrl_height = 750-diff_h
        ctrl_width = 1350-diff_w
        try:
            self.velocityGraph = MatplotlibPanel(parent=self, size=(ctrl_width, ctrl_height))
            self.fg2sizer.Add(self.velocityGraph)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(420, 750))
        self.fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
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
        #print(f'm = {self.m}, c = {self.c}')
        Y=self.m*float(math.log10(X)) + float(self.c)
        return 10**Y
    def log_log_interpolate(self, point1, point2, x):
        """
            Calculate the y-value on a log-log straight line graph, given two points and an x-value.
        
            Parameters:
            - point1: Tuple containing the first point (x1, y1)
            - point2: Tuple containing the second point (x2, y2)
            - x: The x-value for which you want to calculate the corresponding y-value
        
            Returns:
            - y: The calculated y-value corresponding to the given x-value
        """
        
        # Extract the coordinates from the points
        x1, y1 = point1
        x2, y2 = point2
    
        # Convert the points to their logarithms
        log_x1, log_y1 = math.log10(x1), math.log10(y1)
        log_x2, log_y2 = math.log10(x2), math.log10(y2)
        log_x = math.log10(x)
    
        # Calculate the slope of the line on the log-log graph
        slope = (log_y2 - log_y1) / (log_x2 - log_x1)
    
        # Calculate the corresponding log(y) using the equation of the line
        log_y = log_y1 + slope * (log_x - log_x1)
    
        # Convert log(y) back to y
        y = 10 ** log_y
    
        return y
    def log_log_interpolate_diff(self, point1, point2, x_series, v_series):
        """
        Calculate the difference between a series v and the interpolated y-values on a log-log straight line graph.
        If any value in the x_series is zero or NaN, return NaN for that corresponding v'.
    
        Parameters:
        - point1: Tuple containing the first point (x1, y1)
        - point2: Tuple containing the second point (x2, y2)
        - x_series: A pandas Series containing the x-values for which you want to calculate the corresponding y-values
        - v_series: A pandas Series containing the v-values from which the interpolated y-values will be subtracted
    
        Returns:
        - v_prime_series: A pandas Series containing the calculated v' values (v - y)
        """
        
        # Extract the coordinates from the points
 
        x1, y1 = point1
        x2, y2 = point2

    
        # Convert the points to their logarithms
        log_x1, log_y1 = math.log10(x1), math.log10(y1)
        log_x2, log_y2 = math.log10(x2), math.log10(y2)
    
        # Calculate the slope of the line on the log-log graph
        slope = (log_y2 - log_y1) / (log_x2 - log_x1)
    
        # Initialize the result series with NaNs
        v_prime_series = pd.Series(index=x_series.index, dtype=float)
    
        # Apply the log-log interpolation formula to the entire Series
        for i, x_value in x_series.items():  # Use items() instead of iteritems()
            if pd.isna(x_value) or x_value <= 0:
                v_prime_series[i] = np.nan
            else:
                log_x_value = math.log10(x_value)
                log_y_value = log_y1 + slope * (log_x_value - log_x1)
                y_value = 10 ** log_y_value
                v_prime_series[i] = v_series[i] - y_value
    
        return v_prime_series

    def OnReset(self, event=0):
        #if hasattr(self.parent, 'hrinclude'):
        self.parent.status['include']=self.parent.status['hrOut'].copy()
        self.parent.status['kineticOut']=self.parent.status['include'].copy()
        
    # Define the s-curve function
    def s_curve(self, r, N=0.5):
        #return N + 0.2*N / (1 + np.exp(-11*(r-.6)))
        
        # Constants
        g_Ne = 1.144  # a_0, from the reference.

        # Gravitational accelerations
        g_Ni = 1. / (1.5 * r * r)  # Prevent division by zero (r != 0)
        g_Nt = np.sqrt(g_Ni ** 2 + g_Ne ** 2)
        
        # Interpolation function and its derivative
        nu = 0.5 + np.sqrt(0.25 + 1. / g_Nt)  # g_Nt is in units of a_0
        dnu = -0.5 * 1. / (g_Nt ** 2 * np.sqrt(0.25 + 1. / g_Nt))  # dnu/dx, where x = g_Nt / a_0
        
        # Correction factor K
        K = dnu * g_Nt / nu
        
        # Velocity calculation with tanh term, ensuring valid inputs
        # Make sure g_Ne / g_Ni is finite, handle division by zero
        tanh_term = np.tanh(0.825 * g_Ne / np.where(g_Ni != 0, g_Ni, 1e-10)) ** 3.7
        vt = np.sqrt(nu * (1. + K / 3. * tanh_term))/2

        return vt

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
        gl_cfg.setItem('upper_v_tilde_cutoff',self.text_v_tilde_upperCutoff.GetValue(),'KINETIC')
        gl_cfg.setItem('v_dv_cutoff',self.text_vxerrCutoff.GetValue(),'KINETIC')
        gl_cfg.setItem('lower_bin_cutoff',self.lowerBinCutoffTextCtrl.GetValue(),'KINETIC')
        gl_cfg.setItem('y_scale',self.combo_yLog.GetSelection(),'KINETIC')
        gl_cfg.setItem('combo-bin-reduction',self.combo_binReduction.GetSelection(),'KINETIC')
        gl_cfg.setItem('y_avg',self.combo_yAvg.GetSelection(),'KINETIC')
        gl_cfg.setItem('x_avg',self.combo_xAvg.GetSelection(),'KINETIC')
        gl_cfg.setItem('xy_option',self.combo_xy_option.GetSelection(),'KINETIC')
        gl_cfg.setItem('norm',self.newtonian_CheckBox.GetValue(),'KINETIC')
        gl_cfg.setItem('norm',self.mond_CheckBox.GetValue(),'KINETIC')
        gl_cfg.setItem('tab',self.parent.GetSelection(), 'SETTINGS') # save notebook tab setting in config file
        gl_cfg.setItem('prntversion',self.prntVersionCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('largepoints',self.largePointsCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('showbins',self.showBinsCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('rawdata',self.rawDataCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('outlierline',self.outlierLineCheckBox.GetValue(), 'KINETIC') # save setting in config file
        #gl_cfg.setItem('showlabels',self.showLabelsCheckBox.GetValue(), 'KINETIC') # save setting in config file
        gl_cfg.setItem('above-below-line',self.combo_deselect_aboveBelow.GetSelection(), 'KINETIC')
        self.OnReset()
        # Draw kinematic map
        #self.parent.vdvExclude=0  # Keep track of how many pairs are excluded because 'v x vErr' exceeds a threshold.
        
        XArrayType=self.combo_xAvg.GetValue()
        newtonian_line=self.newtonian_CheckBox.GetValue()
        mond_line=self.mond_CheckBox.GetValue()
        # To remove the artist
        for frame in self.velocityGraph.frames:
            try:
                frame.remove()
            except Exception:
                pass
        try:
            self.line_raw.remove()
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

        try:
            self.lineOL.remove()
        except Exception:
            pass
        
        try:
            self.lineMond.remove()
        except Exception:
            pass
        
        # Remove the secondary x-axis if it already exists
        try:
            if hasattr(self, 'twinx'):
                self.twinx.remove()
        except Exception:
            pass
        #try:
        #    self.velocityGraph.axes.clear()
        #    self.axes.set_yscale('log', nonpositive='clip')
        #    self.axes.set_xscale('log', nonpositive='clip')
        #except Exception:
        #    pass
        
        legend1=[] 
        legend2=[] 
        yLower=float(self.textctrl_yLower.GetValue())
        yUpper=float(self.textctrl_yUpper.GetValue())
        xLower=float(self.textctrl_xLower.GetValue())
        xUpper=float(self.textctrl_xUpper.GetValue())
        self.velocityGraph.set_limits([float(self.textctrl_xLower.GetValue()),float(self.textctrl_xUpper.GetValue())],[yLower,yUpper])
        self.parent.binaryDetail['Msqrt']=self.parent.binaryDetail.M.apply(np.sqrt)
        prntVersion=self.prntVersionCheckBox.GetValue()
        
        #Set up local variables to avoid repeated calls to wx functions and for clarity
        x_BottomRight=float(self.text_x_BottomRight.GetValue())
        x_TopLeft=float(self.text_x_TopLeft.GetValue())
        y_BottomRight=float(self.text_y_BottomRight.GetValue())
        y_TopLeft=float(self.text_y_TopLeft.GetValue())
        aboveBelow=self.combo_deselect_aboveBelow.GetSelection()
        # Calculate parameters for outlier line.
        self.m=float(math.log10(y_BottomRight)-math.log10(y_TopLeft))/(math.log10(x_BottomRight)-math.log10(x_TopLeft)) # m = dy/dx
        self.c=float(math.log10(y_TopLeft) - math.log10(x_TopLeft)*self.m)
    
        lenArray=len(self.parent.binaryDetail)
        upperCutoff=float(self.text_upperCutoff.GetValue())
        upper_v_tilde_Cutoff=float(self.text_v_tilde_upperCutoff.GetValue())
        vxerrCutoff=float(self.text_vxerrCutoff.GetValue())
            
        if self.showBinsCheckBox.GetValue():   
            
            #
            # Convert data into bins
            #
#######################################################################

            top=float(self.textctrl_xUpper.GetValue())      #  Get top of range
            bottom=float(self.textctrl_xLower.GetValue())   #  Get bottom of range
            diff = math.log10(top)-math.log10(bottom)   #  Work out difference in log terms.
######################################################################
            numBins=int(self.spin_bins.GetValue())      #  Get number of bins.
            dataBins=binOrganiser(numBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            dataTotalBins=binOrganiser(numBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            dataSph_CorrBins=binOrganiser(numBins, int(float(self.lowerBinCutoffTextCtrl.GetValue())))
            upper=top
            factor=10**(diff/numBins)
            lower=upper/factor
            for i in range(numBins):
                dataBins.newBin(lower, upper)
                dataTotalBins.newBin(lower, upper)
                dataSph_CorrBins.newBin(lower, upper)
                upper=lower
                lower=upper/factor
            #    
            #Filter out currently inluded rows only
            indexStatus = self.parent.status.index
            condition = self.parent.status.include == True
            statusIndices = indexStatus[condition]
            statusIndicesList = statusIndices.tolist()
            listOfPairs=[]
            listOfPairSquares=[]
            
            # Pre-process individual pairs by total RA& DEC (ie pythagoras)
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.include[i]) or not int(self.parent.status.include[i]):
                    continue
                #else:
                #    include=int(self.parent.status.include[i])
                #Set up local valriables to avoid repeated PD access and for clarity
                v2D=0
                v_tilde=0
                excludev2D=0
                excludeTot=0
                v_tilde=float(self.parent.binaryDetail.v_tilde[i]) #/self.parent.binaryDetail.Msqrt[i]
                r_over_r_mond=float(self.parent.binaryDetail.r_over_r_mond[i]) #/self.parent.binaryDetail.Msqrt[i]
                v2D=float(self.parent.binaryDetail.v2D[i]) #/self.parent.binaryDetail.Msqrt[i]
                vRA=float(self.parent.binaryDetail.vRA[i]) #/self.parent.binaryDetail.Msqrt[i]
                vDEC=float(self.parent.binaryDetail.vDEC[i]) #/self.parent.binaryDetail.Msqrt[i]
                r=float(self.parent.binaryDetail.r[i])
                vRAerr=float(self.parent.binaryDetail.vRAerr[i])
                vDECerr=float(self.parent.binaryDetail.vDECerr[i])
                v2D_err=float(self.parent.binaryDetail.v2D_err[i])
                v_tilde_err=float(self.parent.binaryDetail.v_tilde_err[i])
                # Go through and bin
                label=float(50 * i /lenArray)
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
                if aboveBelow: 
                    Y=self.XreturnY(r)
                    #Outliers above line
                    if aboveBelow ==1 and (v2D > Y) and r > x_TopLeft and r < x_BottomRight:
                        self.parent.status.loc[i, 'include'] = 0
                    #Outliers below line
                    if aboveBelow ==2 and (v2D < Y ) and r > x_TopLeft and r < x_BottomRight:
                        self.parent.status.loc[i, 'include'] = 0
                        
                # Check for cutoff.  If we loose one, we should loose both.
                if (v2D>upperCutoff ):
                    self.parent.status.loc[i, 'include'] = 0
                    self.parent.StatusBarProcessing(f'Potential Flyby at v2D = {v2D}')
                    
                # Check for v-tilde cutoff.  If we loose one, we should loose both.
                if (v_tilde>upper_v_tilde_Cutoff ):
                    self.parent.status.loc[i, 'include'] = 0
                    self.parent.StatusBarProcessing(f'Potential Flyby at v2D = {v2D}')

                # Check RA limits
                if self.parent.status.include[i]:
                    #Exclude point if v/dv > vxerrCutoff
                    if self.combo_xy_option.GetSelection() == 0:
                        excludeTot = dataTotalBins.binAddDataPoint(x=r, y=v2D, dy=v2D_err, threshold_value=vxerrCutoff, idx=i)
                    elif self.combo_xy_option.GetSelection() == 1:
                        excludeTot = dataTotalBins.binAddDataPoint(x=r, y=v_tilde, dy=v_tilde_err, threshold_value=vxerrCutoff, idx=i)
                    elif self.combo_xy_option.GetSelection() == 2:
                        excludeTot = dataTotalBins.binAddDataPoint(x=r_over_r_mond, y=v_tilde, dy=v_tilde_err, threshold_value=vxerrCutoff, idx=i)
                    else:
                        excludeTot = dataTotalBins.binAddDataPoint(x=r_over_r_mond, y=v2D, dy=v2D_err, threshold_value=vxerrCutoff, idx=i)
                    # Exclude binary if both RA & Dec excluded.

                    if not excludeTot:
                        self.parent.status.loc[i, 'include'] = 0
                        self.parent.StatusBarProcessing(f'V/dv cuttoff excludeTot = {excludeTot}')
                
            #Remove top 'n' percent of each bin
            if int(self.combo_binReduction.GetValue()):   
                for binNum in range(numBins):
                    indices=dataTotalBins.binCalculateDataPoints(binNum, int(self.combo_binReduction.GetValue()))
                    if len(indices):
                        for index in indices:

                            try:
                                #Remove WB
                                self.parent.status.loc[dataTotalBins.indices[binNum][index], 'include'] = 0
                            except Exception as error_message:
                                print(f'Failed to remove index {index} from bin {binNum} - error {error_message}')
                
            # Process individual pairs by RA & DEC
            for i in statusIndicesList:
                
                if math.isnan(self.parent.status.include[i]) or not int(self.parent.status.include[i]):
                    continue
                #else:
                #    include=int(self.parent.status.include[i])
                #Set up local valriables to avoid repeated PD access and for clarity
                v_tilde=0
                excludev2D=0
                v2D=float(self.parent.binaryDetail.v2D[i])
                V_spher_corr=float(self.parent.binaryDetail.V_spher_corr[i])


                v_tilde=float(self.parent.binaryDetail.v_tilde[i]) #/self.parent.binaryDetail.Msqrt[i]
                r_over_r_mond=float(self.parent.binaryDetail.r_over_r_mond[i]) #/self.parent.binaryDetail.Msqrt[i]
                r=float(self.parent.binaryDetail.r[i])
                v2D_err=float(self.parent.binaryDetail.v2D_err[i])
                v_tilde_err=float(self.parent.binaryDetail.v_tilde_err[i])
                v_tilde_sph_corr=float(self.parent.binaryDetail.v_tilde_sph_corr[i])
                # Go through and bin
                label=float(50.0 * i /lenArray) + 50.0
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
                if aboveBelow: 
                    Y=self.XreturnY(r)
                    #Outliers above line
                    if aboveBelow ==1 and (v2D > Y  ) and r > x_TopLeft and r < x_BottomRight:
                        self.parent.status.loc[i, 'include'] = 0
                    #Outliers below line
                    if aboveBelow ==2 and (v2D < Y) and r > x_TopLeft and r < x_BottomRight:
                        self.parent.status.loc[i, 'include'] = 0
                        
                # Check for cutoff.  If we loose one, we should loose both.
                if (v2D>upperCutoff ):
                    self.parent.status.loc[i, 'include'] = 0
                    self.parent.StatusBarProcessing(f'Potential Flyby at v2D = {v2D}')
                # Check RA limits
                if self.parent.status.include[i]:                    
                    #Exclude point if v/dv > vxerrCutoff
                    if self.combo_xy_option.GetSelection() == 0:
                        excludev2D = dataBins.binAddDataPoint(x=r, y=v2D, dy=v2D_err, threshold_value=vxerrCutoff, idx=i)
                        dataSph_CorrBins.binAddDataPoint(x=r, y=V_spher_corr, dy=1, threshold_value=0, idx=i)
                    elif self.combo_xy_option.GetSelection() == 1:
                        excludev2D = dataBins.binAddDataPoint(x=r, y=v_tilde, dy=v2D_err, threshold_value=vxerrCutoff, idx=i)
                        dataSph_CorrBins.binAddDataPoint(x=r, y=v_tilde_sph_corr, dy=1, threshold_value=0, idx=i)
                    elif self.combo_xy_option.GetSelection() == 2:
                        excludev2D = dataBins.binAddDataPoint(x=r_over_r_mond, y=v_tilde, dy=v_tilde_err, threshold_value=vxerrCutoff, idx=i)
                        dataSph_CorrBins.binAddDataPoint(x=r_over_r_mond, y=v_tilde_sph_corr, dy=1, threshold_value=0, idx=i)
                    else:
                        excludev2D = dataBins.binAddDataPoint(x=r_over_r_mond, y=v2D, dy=v_tilde_err, threshold_value=vxerrCutoff, idx=i)
                        dataSph_CorrBins.binAddDataPoint(x=r_over_r_mond, y=V_spher_corr, dy=1, threshold_value=0, idx=i)
                    # Exclude binary if both RA & Dec excluded.
                    if not excludev2D:
                        self.parent.status.loc[i, 'include'] = 0
                        self.parent.StatusBarProcessing(f'V/dv cuttoff excludev2D = {excludev2D}')
                    else:
                        primaryPointer=self.parent.X.iloc[i]
                        star2Pointer=self.parent.Y.iloc[i]
                        self.createExportRecord(primaryPointer, star2Pointer, i)

            xdata3=dataBins.getBinXArray(XArrayType)
            ydata3=dataBins.getBinYArray(mean_type=self.combo_yAvg.GetValue())
            rerrbin3=dataBins.getBinXVarArray(XArrayType)
            verrbin3=dataBins.getBinYVarArray(type='var_qrms', mean_type=self.combo_yAvg.GetValue(), )
                        
            self.line3 = self.velocityGraph.axes.errorbar(xdata3, ydata3, xerr=rerrbin3, yerr=verrbin3, fmt='o', ecolor='r', elinewidth=2, capsize=0, mfc='r', mec='r', ms=3) #,label='Gaia binned'
            self.line3[-1][0].set_linestyle('-.') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            self.line3[-1][1].set_linestyle('-.') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            

            if not prntVersion:
                legend1.append(self.line3)
                legend2.append('Gaia binned data')
            
            xScaleBy=1.15
            yScaleBy=1.05

            if self.showBinsCheckBox.GetValue():
                #    """
                #Attach a text label above each bar displaying its height
                #"""
                self.velocityGraph.frames=[] 
                if prntVersion:
                    c='black'
                else:
                    c='white'
                for x,y,label in zip(xdata3, ydata3, dataBins.getBinYLabelArray()):
                   self.velocityGraph.frames.append(self.velocityGraph.axes.text(float(x)*xScaleBy, float(y)*yScaleBy, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE+4))
            
            
                #self.velocityGraph.twiny            
                self.velocityGraph.draw(self.line3, xdata3, ydata3, False, [] )
            
        self.velocityGraph.axes.set_ylabel(r'$\tilde{v}$ in sky plane', fontsize=FONTSIZE+4)
        self.velocityGraph.axes.set_xlabel(r'$r_{sky}$ / $r_{MOND}$', fontsize=FONTSIZE+4)

        ROWCOUNTMATRIX['BIN']=sum(self.parent.status['include'])
        if self.combo_xy_option.GetSelection() == 0:
            xdata1 = self.parent.binaryDetail.r * self.parent.status['include']
            xdata1err = self.parent.binaryDetail.r_err * self.parent.status['include']
            ydata1v = self.parent.binaryDetail.v2D * self.parent.status['include'] 
            ydata1err = self.parent.binaryDetail.v2D_err * self.parent.status['include'] 
            #Axes and title
            self.velocityGraph.axes.set_ylabel(r'2D relative velocity in sky plane [$km s^{-1}$]', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_xlabel(r'2D separation, $r_{sky}$ [$pc$]', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,}  WBs with actual 2D velocity vs separation", fontsize=FONTSIZE+4)
        elif self.combo_xy_option.GetSelection() == 1:
            xdata1 = self.parent.binaryDetail.r * self.parent.status['include']
            xdata1err = self.parent.binaryDetail.r_err * self.parent.status['include']
            ydata1v = self.parent.binaryDetail.v_tilde * self.parent.status['include'] 
            ydata1err = self.parent.binaryDetail.v_tilde_err * self.parent.status['include'] 
            #Axes and title
            self.velocityGraph.axes.set_ylabel(r'$\tilde{v}$ in sky plane', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_xlabel(r'2D separation, $r_{sky}$ [$pc$]', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,}  WBs with $\\tilde{{v}}$ vs separation", fontsize=FONTSIZE+4)
        elif self.combo_xy_option.GetSelection() == 2:
            xdata1 = self.parent.binaryDetail.r_over_r_mond * self.parent.status['include']
            xdata1err = self.parent.binaryDetail.r_over_r_mond_err * self.parent.status['include']
            ydata1v = self.parent.binaryDetail.v_tilde * self.parent.status['include'] 
            ydata1err = self.parent.binaryDetail.v_tilde_err * self.parent.status['include'] 
            #Axes and title
            self.velocityGraph.axes.set_ylabel(r'$\tilde{v}$ in sky plane', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_xlabel(r'$r_{sky}$ / $r_{MOND}$', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,}  WBs with $\\tilde{{v}}$ against separation over MOND radius", fontsize=FONTSIZE+4)
            # Remove the secondary x-axis if it already exists
            try:
                if hasattr(self, 'twinx'):
                    self.twinx.remove()
            except Exception:
                pass
        else:
            xdata1 = self.parent.binaryDetail.r_over_r_mond * self.parent.status['include']
            xdata1err = self.parent.binaryDetail.r_over_r_mond_err * self.parent.status['include']
            ydata1v = self.parent.binaryDetail.v2D * self.parent.status['include'] 
            ydata1err = self.parent.binaryDetail.v2D_err * self.parent.status['include'] 
            #Axes and title
            self.velocityGraph.axes.set_ylabel(r'2D relative velocity in sky plane [$km s^{-1}$]', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_xlabel(r'$r_{sky}$ / $r_{MOND}$', fontsize=FONTSIZE+4)
            self.velocityGraph.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,}  WBs showing actual 2D velocity against separation by MOND radius", fontsize=FONTSIZE+4)
            # Remove the secondary x-axis if it already exists
            try:
                if hasattr(self, 'twinx'):
                    self.twinx.remove()
            except Exception:
                pass
        
            
        #ydata1dec = self.parent.binaryDetail.vDEC * self.parent.status['include'] #/self.parent.binaryDetail.Msqrt
        #if normalise:
        #    ydata1v = self.log_log_interpolate_diff((1e-3,1.0079), (.5,.042),xdata1 , ydata1v)
        #    ydata1dec = self.log_log_interpolate_diff((1e-3,1.0079), (.5,.042), xdata1, ydata1dec)
        a=np.array(ydata1v)

        if self.rawDataCheckBox.GetValue():
            c='white'
            if prntVersion:
                c='black'
            marker = ','
            alpha=.5
            markersize=1
            if self.largePointsCheckBox.GetValue():
                marker = 'o'
                markersize=3
            #self.line_raw, = self.velocityGraph.axes.plot(xdata1.to_numpy(), ydata1v.to_numpy(), color=c, marker=marker, alpha=alpha, markeredgecolor='none', linestyle='none', linewidth=0, markersize=markersize)
            #self.velocityGraph.draw(self.line_raw, xdata1.to_numpy(), ydata1v.to_numpy(), True, [] )
            # Plotting with y-axis error bars
            self.line_raw = self.velocityGraph.axes.errorbar(
                xdata1.to_numpy(),          # x data
                ydata1v.to_numpy(),         # y data
                xerr=xdata1err.to_numpy(),  # x-axis error bars 
                yerr=ydata1err.to_numpy(),  # y-axis error bars 
                fmt='o',                    # format for points ('o' means circular markers)
                color=c,                    # color of the points and error bars
                alpha=alpha,                # transparency
                markersize=markersize,      # size of the marker
                markeredgecolor='none',     # no marker edge color
                linestyle='none',           # no connecting line between markers
            )
          
            # Draw the plot
            self.velocityGraph.draw(self.line_raw, xdata1.to_numpy(), ydata1v.to_numpy(), True, [])

            if not prntVersion:
                legend1.append(self.line_raw)
                legend2.append('Gaia raw data')
        if self.outlierLineCheckBox.GetValue():
            xdataOL=[x_TopLeft,x_BottomRight]
            ydataOL=[y_TopLeft,y_BottomRight]
            
            self.lineOL, = self.velocityGraph.axes.plot(xdataOL, ydataOL, 'r--', linewidth=2, markersize=1)
            self.velocityGraph.draw(self.lineOL, xdataOL, ydataOL, True, [] )
            
            if not prntVersion:
                legend1.append(self.lineOL)
                legend2.append('Flyby cutoff')
        
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
            #self.velocityGraph.axes.set_title(f"{ROWCOUNTMATRIX['BIN']:,} binary stars, Gaia {RELEASE}, velocity vs separation with Newtonian expectation", fontsize=FONTSIZE+4)
            self.velocityGraph.axes.patch.set_facecolor('0.25')  # Grey shade
        
        # Multiply each element in the lists by corrN
        
        avgMass=self.CalcMeanXYoverDxy('mass_calc',False)
        corrN=math.sqrt(avgMass)
        #
        print(corrN)
        G2=float(gl_cfg.getItem('g2','RETRIEVAL', 1.393e-13))
        a_0=float(gl_cfg.getItem('a_0','RETRIEVAL', 1.2E-10))
        r_mond=np.sqrt(G2*avgMass*2/(a_0))
            
        if prntVersion:
            try:
                self.velocityGraph.axes.get_legend().remove()
            except:
                pass
        if self.combo_xy_option.GetSelection() <= 1:
            # Recreate the secondary x-axis
            self.twinx = self.velocityGraph.axes.twiny()
            self.twinx.set_xlabel('2D projected separation [au]', fontsize=FONTSIZE+4)
            
            # Set the new limits after rescaling
            self.twinx.set_xlim(float(self.textctrl_xLower.GetValue()) * 206265, float(self.textctrl_xUpper.GetValue()) * 206265)
    
            # Apply log scale and other formatting options
            self.twinx.set_xscale('log', nonpositive='clip')
            self.twinx.tick_params(labelsize=20)
      
        if newtonian_line:
            if self.combo_xy_option.GetSelection() == 0:
                xdata2N = [x  for x in xdata2]
                ydata2N_1D = [y * corrN for y in ydata2]
                self.line2, = self.velocityGraph.axes.plot(xdata2N, ydata2N_1D, 'b:', lw=2)#,label='Newtonian')
            elif self.combo_xy_option.GetSelection() == 1:
                xdata2N = [x  for x in xdata2]
                ydata2N_1D = [.5 for y in ydata2]
                self.line2, = self.velocityGraph.axes.plot(xdata2N, ydata2N_1D, 'b:', lw=2)#,label='Newtonian')
            elif self.combo_xy_option.GetSelection() == 2:
                xdata2N = [x for x in xdata2]
                ydata2N_1D = [.5 for y in ydata2]
                self.line2, = self.velocityGraph.axes.plot(xdata2N, ydata2N_1D, 'b:', lw=2)#,label='New 
            else:
                xdata2N = [x / r_mond for x in xdata2]
                ydata2N_1D = [y * corrN for y in ydata2]
                self.line2, = self.velocityGraph.axes.plot(xdata2N, ydata2N_1D, 'b:', lw=2)#,label='Newtonian')
                
            if not prntVersion:
                legend1.append(self.line2)
                legend2.append('Newtonian value')
                
            self.velocityGraph.draw(self.line2, xdata2, ydata2_1D, False, [] )
        
        if mond_line:
            
            if self.combo_xy_option.GetSelection() == 0:
                xdata_mond = [.034* corrN * math.sqrt(2), .034* corrN * math.sqrt(2)]
                ydata_mond = [yLower, yUpper]
                
                ## Define r/rM values
                #xdata_mond = np.linspace(xLower,xUpper, 1000)
                #ydata_mond = self.s_curve(xdata_mond)
            elif self.combo_xy_option.GetSelection() == 1:
                xdata_mond = [.034* corrN * math.sqrt(2), .034* corrN * math.sqrt(2)]
                ydata_mond = [yLower, yUpper]
            elif self.combo_xy_option.GetSelection() == 2:
                # Define r/rM values
                xdata_mond = np.linspace(xLower,xUpper, 1000)
                ydata_mond = self.s_curve(xdata_mond)
            else:
                xdata_mond = [1, 1]
                ydata_mond = [yLower, yUpper]
                
            self.lineMond, = self.velocityGraph.axes.plot(xdata_mond,ydata_mond, 'g--', lw=2)#,label='Mond expectation')
            
            if not prntVersion:
                legend1.append(self.lineMond)
                legend2.append('Mond expectation')
            
            self.velocityGraph.axes.legend(legend1, legend2)
            self.velocityGraph.draw(self.lineMond, xdata_mond, ydata_mond, False, [] )
            
        self.velocityGraph.axes.tick_params(axis='both', which='major', labelsize=FONTSIZE+4)
        self.velocityGraph.axes.tick_params(axis='both', which='minor', labelsize=FONTSIZE+4)

        self.velocityGraph.axes.xaxis.label.set_fontsize(FONTSIZE + 4)
        self.velocityGraph.axes.yaxis.label.set_fontsize(FONTSIZE + 4)

        self.velocityGraph.figure.canvas.draw()
        self.velocityGraph.figure.canvas.flush_events()

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
        self.summaryList.InsertItem(rowCnt, 'Median Err/Px')
        snPxoverDpx=self.CalcMedianXYoverDxy('PARALLAX','parallax_error')
        #self.summaryList.SetItem(rowCnt, 1, f"{snPxoverDpx:,4}")
        self.summaryList.SetItem(rowCnt, 1, f"{snPxoverDpx:,.4f}")

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
        self.summaryList.InsertItem(rowCnt, 'Mean mass of Binaries')
        avgMass=self.CalcMeanXYoverDxy('mass_calc',False)
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass:,}")
        
        rowCnt += 1 #Next row 
        self.summaryList.InsertItem(rowCnt, 'Fraction of stars with FLAME Masses')
        avgMass=self.CalcPercentEitherNotNull('mass_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgMass*100:,} %")

        rowCnt += 1 #Next row
        self.summaryList.InsertItem(rowCnt, 'Binaries with 2 FLAME Ages')
        avgAge=self.CalcPercentPairNotNull('age_flame')
        self.summaryList.SetItem(rowCnt, 1, f"{avgAge*100:,} %")
        

        Rs=dataBins.getBinXArray("mean")
        spherical_corrections=dataSph_CorrBins.getBinYArray("mean")

        # Combine into a list of (x, y) pairs
        xy_coords = list(zip(Rs, spherical_corrections))

        # Sort by x-coordinate
        sorted_coords = sorted(xy_coords, key=lambda coord: coord[0])

        # Print each coordinate, rounded to 3 decimal places
        coord_count=0
        for coord in sorted_coords:
            #print(f"({round(coord[0], 3)}, {round(coord[1], 3)})")
            coord_count += 1 #Next coord
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, f'Spherical Correction, bin #{coord_count}')
            self.summaryList.SetItem(rowCnt, 1, f"({round(coord[0], 3)}, {round(coord[1], 3)})")



        if self.showBinsCheckBox.GetValue():  

            # Cookson_24 sample
            Observed_values = np.array(dataBins.getBinYArray(mean_type=self.combo_yAvg.GetValue()))
            Observation_Errors = np.array(dataBins.getBinYVarArray(type='var_qrms', mean_type=self.combo_yAvg.GetValue(), ))
            N_dof = len(Observed_values)

            Errors_sqinv = 1.0/(Observation_Errors*Observation_Errors)
            Varinv_weighted_mean = np.sum(Observed_values*Errors_sqinv)/np.sum(Errors_sqinv)
            Newt_1_exp = np.array([.5 for y in Observed_values])
            Newt_2_exp = np.array([Varinv_weighted_mean for y in Observed_values])
            MOND_exp = self.s_curve(np.array(rerrbin3))

            # Unweighted Newt 1 chi-2
            #chi_numerator_Newt_1=(Observed_values-Newt_1_exp)*(Observed_values-Newt_1_exp)
            #chi_sqN1 = np.sum(chi_numerator_Newt_1*Errors_sqinv)
            #chiN1 = np.sqrt(2.0)*erfinv(chi2.cdf(chi_sqN1, N_dof))
            #print(f"Cookson_24 chi^2 (Newt 1) = {round(chi_sqN1,3)} total, no DoF adjustment")
            #print(f"Cookson_24 z-score (Newt 1) = {round(chiN1,3)} for DoF = {N_dof}")

            # MOND chi-2
            MOND_residuals=Observed_values-MOND_exp
            rN_dof = N_dof -1 # Reduced N_DoF
            chi_numerator_mond=MOND_residuals*MOND_residuals
            chi_sqM = np.sum(chi_numerator_mond*Errors_sqinv)
            chiM = np.sqrt(2.0)*erfinv(chi2.cdf(chi_sqM, rN_dof))
            print(f"chi^2 (MOND) = {round(chi_sqM,4)} total, reduced DoF ")
            print(f"z-score (MOND) = {round(chiM,4)} for DoF = {rN_dof}")

            # MONDian chi_2 based on inverse-variance weighted mean
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'MONDian total Chi_2')
            self.summaryList.SetItem(rowCnt, 1, f"{round(chi_sqM,3)}")

            # MONDian z-score based on inverse-variance weighted mean and reduced DoF
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, f'MONDian z-score for {rN_dof} DoF' )
            self.summaryList.SetItem(rowCnt, 1, f"{round(chiM,3)}")


            # Weighted Newt 2 chi-2
            chi_numerator_Newt_2=(Observed_values-Newt_2_exp)*(Observed_values-Newt_2_exp)
            chi_sqN2 = np.sum(chi_numerator_Newt_2*Errors_sqinv)
            chiN2 = np.sqrt(2.0)*erfinv(chi2.cdf(chi_sqN2, rN_dof))

            #Mean binned binary RMS 1D relative velocity in RA
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'Mean binned velocity value')
            ydata3pd=pd.DataFrame(ydata3, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{np.mean(Observed_values):,.3f}")

            #Mean weighted binned binary RMS 1D relative velocity in RA
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'Weighted Mean binned velocity')
            #ydata3pd=pd.DataFrame(ydata3, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{Varinv_weighted_mean:,.3f}")

            #Number of degrees of freedom,. unadjusted
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'No. of degrees of freedom, unadjusted')
            #ydata3pd=pd.DataFrame(ydata3, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{len(Observed_values)}")

            #Number of degrees of freedom - adjusted
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'No. of degrees of freedom, adjusted')
            #ydata3pd=pd.DataFrame(ydata3, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{len(Observed_values)-1}")

            print(f"Cookson_24 chi^2 (Newt 2) = {round(chi_sqN2,4)} total, no DoF adjustment")

            # Newtonian chi_2 based on inverse-variance weighted mean
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'Newtonian total Chi_2')
            self.summaryList.SetItem(rowCnt, 1, f"{round(chi_sqN2,4)}")

            print(f"Cookson_24 z-score (Newt 2) = {round(chiN2,4)} for DoF = {rN_dof}")
            # Newtonian z-score based on inverse-variance weighted mean and reduced DoF
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, f'Newtonian z-score for {rN_dof} DoF' )
            self.summaryList.SetItem(rowCnt, 1, f"{round(chiN2,4)}")

            #STDEV binned binary RMS 1D relative velocity in RA (
            rowCnt += 1 #Next row
            self.summaryList.InsertItem(rowCnt, 'Velocity std dev from mean.')        
            ydata3pd=pd.DataFrame(ydata3, columns=['V'])
            self.summaryList.SetItem(rowCnt, 1, f"{ydata3pd.V.std():,.4f}")
        

            ##Mean binned binary 1D separation in RA
            #rowCnt += 1 #Next row
            #self.summaryList.InsertItem(rowCnt, 'Mean binned 2D separation in RA')        
            #xdata3pd=pd.DataFrame(xdata3, columns=['r'])
            #newlist = [x for x in xdata3pd.r if math.isnan(x) == False and float(x) > 0]
            #product = 0
            #for j in range(0, len(newlist)):
            #    product = product + math.log10(float(newlist[j]))
            #geoMean = product / float(len(newlist))
            #self.summaryList.SetItem(rowCnt, 1, f"{10**geoMean:,.4f}")
        
        self.parent.status['massVmassOut']=self.parent.status['include'].copy()
        self.parent.status['tfOut']=self.parent.status['include'].copy()
        self.parent.status['numberOut']=self.parent.status['include'].copy()
        self.saveConfFiles('kineticOut')

        self.plot_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
class TFDataPlotting(masterProcessingPanel):

#Plot mass of binary in solar masses and compare with in the plane velocity (1D or 2D).

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=13, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
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
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel binning.")
        fgsizer.Add(self.cancel, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw TF plot

        screen = Display()
        diff_h = int(1080 - screen.screen_height)
        diff_w = int(1920 - screen.screen_width)
        ctrl_height = 750-diff_h
        ctrl_width = 1350-diff_w
        try:
            self.TulleyFPlot = MatplotlibPanel(parent=self, size=(ctrl_width, ctrl_height))
            self.fg2sizer.Add(self.TulleyFPlot)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        self.fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
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
            
            primaryPointer=self.parent.X.iloc[i]
            star2Pointer=self.parent.Y.iloc[i]
            #
            # Check Separation limits
            if self.combo_LtGt.GetSelection()==0:
                # Ie 'Outer' shell
                if r>float(self.TextCtrl_sepnCutoff.GetValue()) and upperYCutoff>V2D and upperRCutoff>r:
                    self.createExportRecord(primaryPointer, star2Pointer, i)
                    if self.V1D_CheckBox.GetValue()==True:
                        if not dataTFBins.binAddDataPoint(x=M, y=vRA, dy=vRAerr, threshold_value=0) :
                            self.parent.StatusBarProcessing(f'Exclude "vRAerr (a)" x={M}, y={vRA}')
                        if not dataTFBins.binAddDataPoint(x=M, y=vDEC, dy=vDECerr, threshold_value=0) :
                            self.parent.StatusBarProcessing(f'Exclude "vDECerr (a)" x={M}, y={vDEC}')
                        
                    else:
                        if not dataTFBins.binAddDataPoint(x=M, y=V2D, dy=Verr, threshold_value=0) :
                            self.parent.status.loc[i, 'include'] = 0
                            self.parent.StatusBarProcessing(f'Exclude "Verr" x={M}, y={V2D}')
                else:
                    self.parent.status.loc[i, 'include'] = 0
            else:
                # Ie 'Inner' shell
                if r<float(self.TextCtrl_sepnCutoff.GetValue()) and upperYCutoff>V2D and upperRCutoff>r:
                    self.createExportRecord(primaryPointer, star2Pointer, i)
                    if self.V1D_CheckBox.GetValue()==True:
                        if not dataTFBins.binAddDataPoint(x=M, y=vRA, dy=vRAerr, threshold_value=0):
                            self.parent.StatusBarProcessing(f'Exclude "vRAerr (b)" x={M}, y={vRA}')
                        if not dataTFBins.binAddDataPoint(x=M, y=vDEC, dy=vDECerr, threshold_value=0) :
                            self.parent.StatusBarProcessing(f'Exclude "vDECerr (b)" x={M}, y={vDEC}')
                    else:
                        if not dataTFBins.binAddDataPoint(x=M, y=V2D, dy=Verr, threshold_value=0) :
                            self.parent.status.loc[i, 'include'] = 0
                            self.parent.StatusBarProcessing(f'Exclude "verr" x={M}, y={V2D}')
                else:
                    self.parent.status.loc[i, 'include'] = 0

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
        
        self.TulleyFPlot.axes.set_xlabel(r'total binary mass ($M_{\odot}$)', fontsize=FONTSIZE)
                
        self.TulleyFPlot.axes.set_ylabel(f'{ND}D relative velocity in sky plane [$km s^{-1}$]', fontsize=FONTSIZE)
        ####################################################################################################
        self.parent.binaryDetail['include']=self.parent.status['include'].copy()
        M=self.parent.binaryDetail.loc[(self.parent.binaryDetail['include'] > 0)]
        if self.V1D_CheckBox.GetValue()==True:
            xdata1 = M.M
            #xdata1 = xdata1.append(M.M)
            xdata1 = pd.concat([xdata1, pd.Series(M.M)])
            ydata1 = M.vRA
            #ydata1 = ydata1.append(M.vDEC)
            ydata1 = pd.concat([ydata1, pd.Series(M.vDEC)])
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
        
        self.parent.status['numberOut']=self.parent.status['include'].copy()
        self.saveConfFiles('tfOut')

        self.plot_but.Enable()

        self.parent.StatusBarNormal('Completed OK')
        
class MassPlotting(masterProcessingPanel):

#Plot Actual motion in the 1d plane of the sky vs separation of binaries and compare with Newtonian motion.

    def __init__(self, parent, mainPanel):
        wx.Panel.__init__(self, parent)
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=4, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
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
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel binning.")
        fgsizer.Add(self.cancel, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw mass plot

        screen = Display()
        diff_h = int(1080 - screen.screen_height)
        diff_w = int(1920 - screen.screen_width)
        ctrl_height = 650-diff_h
        ctrl_width = 900-diff_w
        try:
            self.MassPlot = MatplotlibPanel(parent=self, size=(ctrl_width, ctrl_height))
            self.MassPlot.axes.set_yscale('linear')
            self.MassPlot.axes.set_xscale('linear')
            self.fg2sizer.Add(self.MassPlot)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        self.fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
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
            if (primaryPointer.mass_flame and star2Pointer.mass_flame):
                ydata1.append(primaryPointer.mass_flame)
                ydata1.append(star2Pointer.mass_flame)
                xdata1.append(primaryPointer.mass_calc)
                xdata1.append(star2Pointer.mass_calc)
            
            #
            # Ie 'Outer' shell
            if float(primaryPointer.mass_flame):
                self.createExportRecord(primaryPointer, star2Pointer, i)
                if not dataBins.binAddDataPoint(x=primaryPointer.mass_calc, y=primaryPointer.mass_flame, dy=(primaryPointer.age_flame_upper-primaryPointer.age_flame_lower)/2.0, threshold_value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "Calculated mass (a)" x={primaryPointer.mass_calc}, y={primaryPointer.mass_flame}')

            if float(star2Pointer.mass_flame):
                self.createExportRecord(primaryPointer, star2Pointer, i)
                if not dataBins.binAddDataPoint(x=star2Pointer.mass_calc, y=star2Pointer.mass_flame, dy=(star2Pointer.age_flame_upper-star2Pointer.age_flame_lower)/2.0, threshold_value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "Calculated mass (b)" x={star2Pointer.mass_calc}, y={star2Pointer.mass_flame}')

        
        xdata3=dataBins.getBinXArray(type='mean')
        ydata3=dataBins.getBinYArray(mean_type='mean')
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
        self.MassPlot.axes.set_xlabel(r'Calculated stellar mass ($M_{\odot}$)', fontsize=FONTSIZE)
        self.MassPlot.axes.set_ylabel(r'FLAME mass from Gaia ($M_{\odot}$)', fontsize=FONTSIZE)
        ####################################################################################################
        self.parent.binaryDetail['include']=self.parent.status['include'].copy()
        M=self.parent.binaryDetail.loc[(self.parent.binaryDetail['include'] > 0)]
        
        self.parent.starSystemList.binaryList[str(i+1)].primary
                
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
                legend2.append('Raw data')
                
            self.MassPlot.draw(self.line1, xdata1, ydata1, True, [] )
                
            #self.line2, = self.MassPlot.axes.plot(xdata2, ydata2, color='silver', marker=marker, linestyle='none', linewidth=0, markersize=markersize)
            #if not prntVersion:
                #legend1.append(self.line2)
                #legend2.append('Secondary raw data')
                
            #self.MassPlot.draw(self.line2, xdata2, ydata2, True, [] )
                
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
        
        self.parent.status['numberOut']=self.parent.status['include'].copy()
        self.saveConfFiles('massVmassOut')
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
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=8, hgap=0, rows=6, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
        # Headings
        
        self.static_bins = StaticText(self, label='# bins:')
        fgsizer.Add(self.static_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.static_xLower = StaticText(self, label='x-lower') 
        #fgsizer.Add(self.static_xLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #self.static_yLower = StaticText(self, label='y-lower') 
        #fgsizer.Add(self.static_yLower, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        #
        
        fgsizer.AddSpacer(1)
        # Axis limits
        self.spin_bins = SpinCtrl(self, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.ALIGN_RIGHT, min=1, max=100,initial=int(gl_cfg.getItem('no_bins','NUMBERDENSITY')))  
        fgsizer.Add(self.spin_bins, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.spin_bins.SetToolTip("Integer number of bins to divide x-scale into.")
        
        self.static_xUpper = StaticText(self, label='x-upper:')
        fgsizer.Add(self.static_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        self.textctrl_xUpper = TextCtrl(self, id=wx.ID_ANY, value=gl_cfg.getItem('x_upper','NUMBERDENSITY'), pos=wx.DefaultPosition,size=wx.DefaultSize, style=wx.ALIGN_RIGHT)  
        fgsizer.Add(self.textctrl_xUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.textctrl_xUpper.SetToolTip("Upper end of x-scale.")
        self.textctrl_xUpper.setValidRoutine(self.textctrl_xUpper.Validate_Float)
        #

        self.static_yUpper = StaticText(self, label='y-upper:')
        fgsizer.Add(self.static_yUpper, 0, wx.ALIGN_LEFT|wx.ALL, 5)

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
        self.cancel = Button(self, wx.ID_ANY, u"Cancel")
        self.cancel.Bind(wx.EVT_LEFT_DOWN, self.OnCancel)
        self.cancel.SetToolTip("Cancel binning.")
        fgsizer.Add(self.cancel, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
                
        # Draw number density plot

        screen = Display()
        diff_h = int(1080 - screen.screen_height)
        diff_w = int(1920 - screen.screen_width)
        ctrl_height = 750-diff_h
        ctrl_width = 1350-diff_w
        try:
            self.NumberDensityPlot = MatplotlibPanel(parent=self, size=(ctrl_width, ctrl_height))
            self.fg2sizer.Add(self.NumberDensityPlot)
        except Exception:
            pass
        
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(400, 750)) 
        self.fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
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
                if not dataNDBins1.binAddDataPoint(x=DIST, y=1, dy=.00011, threshold_value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "vRAerr (c)" x={DIST}, y=1')
    
            xdata1ND=dataNDBins1.getBinXArray(type='centre')
            ydata1ND=dataNDBins1.getBinYLabelArray()
            rerrbin1ND=dataNDBins1.getBinXVarArray()
            verrbin1ND=dataNDBins1.getBinYVarArray(type='meanerror')

            width = float(upper/numNDBins)
            #self.line1ND = self.NumberDensityPlot.axes.bar(xdata1ND, ydata1ND, width=width, color='r', alpha=0.5, label='Total Unfiltered')
            self.line1ND = self.NumberDensityPlot.axes.plot(xdata1ND, ydata1ND, marker='o', linestyle='-', linewidth=2, color='r', label='Total Unfiltered')
            #self.line1ND = self.NumberDensityPlot.axes.errorbar(x=xdata1ND, y=ydata1ND, xerr=rerrbin1ND, yerr=verrbin1ND, fmt='o', ecolor='r', elinewidth=2, capsize=0, mfc='r', mec='r', ms=3) #,label='Gaia binned'
            #self.line1ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            #self.line1ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
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
                if not dataNDBins2.binAddDataPoint(x=DIST, y=1, dy=.00011, threshold_value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "vRAerr (d)" x={DIST}, y=1')
    
            xdata2ND=dataNDBins2.getBinXArray(type='centre')
            ydata2ND=dataNDBins2.getBinYLabelArray()
            rerrbin2ND=dataNDBins2.getBinXVarArray()
            verrbin2ND=dataNDBins2.getBinYVarArray(type='meanerror')
        
            self.line2ND = self.NumberDensityPlot.axes.plot(xdata2ND, ydata2ND, marker='o', linestyle='-', linewidth=2, color='r', label='Total Unfiltered')

            #self.line2ND = self.NumberDensityPlot.axes.errorbar(x=xdata2ND, y=ydata2ND, xerr=rerrbin2ND, yerr=verrbin2ND, fmt='o', ecolor='y', elinewidth=2, capsize=0, mfc='y', mec='y', ms=3) #,label='Gaia binned'
            #self.line2ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            #self.line2ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
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
                if not dataNDBins3.binAddDataPoint(x=DIST, y=1, dy=.00011, threshold_value=0) :
                    self.parent.StatusBarProcessing(f'Exclude "vRAerr (e)" x={DIST}, y=1')
    
            xdata3ND=dataNDBins3.getBinXArray(type='centre')
            ydata3ND=dataNDBins3.getBinYLabelArray()
            rerrbin3ND=dataNDBins3.getBinXVarArray()
            verrbin3ND=dataNDBins3.getBinYVarArray(type='meanerror')
        
            #self.line3ND = self.NumberDensityPlot.axes.errorbar(x=xdata3ND, y=ydata3ND, xerr=rerrbin3ND, yerr=verrbin3ND, fmt='o', ecolor='g', elinewidth=2, capsize=0, mfc='g', mec='g', ms=3) #,label='Gaia binned'
            self.line3ND = self.NumberDensityPlot.axes.plot(xdata3ND, ydata3ND, marker='^', linestyle='-.', linewidth=2, color='g', label='HR Filtered')
            #self.line3ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            #self.line3ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            
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
                if not dataNDBins4.binAddDataPoint(x=DIST, y=1, dy=.00011, threshold_value=0) :
                    self.parent.StatusBarProcessing(f'Exclude 1 pair "vRAerr (f)" Distance={DIST}')
    
            xdata4ND=dataNDBins4.getBinXArray(type='centre')
            ydata4ND=dataNDBins4.getBinYLabelArray()
            rerrbin4ND=dataNDBins4.getBinXVarArray()
            verrbin4ND=dataNDBins4.getBinYVarArray(type='meanerror')
        
            #self.line4ND = self.NumberDensityPlot.axes.errorbar(x=xdata4ND, y=ydata4ND, xerr=rerrbin4ND, yerr=verrbin4ND, fmt='o', ecolor='b', elinewidth=2, capsize=0, mfc='b', mec='b', ms=3) #,label='Gaia binned'
            self.line4ND = self.NumberDensityPlot.axes.plot(xdata4ND, ydata4ND, marker='d', linestyle='-', linewidth=2, color='b', label='Kinetic Filtered')

            #self.line4ND[-1][0].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
            #self.line4ND[-1][1].set_linestyle('--') #eb1[-1][0] is the LineCollection objects of the errorbar lines
        
        #if not prntVersion:
        #    legend1=[self.line1ND, self.line2ND, self.line3ND, self.line4ND]
        #    legend2=[f'Total Unfiltered.', f'S/N & Distance Filtered.', f'HR Filtered.', f'Kinetic Filtered']

        
        xScaleBy=1
        yScaleBy=1
        yScaleByPlus=0

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
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy+yScaleByPlus, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE+4))

            if self.Series2CheckBox.GetValue():
                legend1.append(self.line2ND)
                legend2.append(f'S/N & Distance Filtered.')
                for x,y,label in zip(xdata2ND, ydata2ND, dataNDBins2.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy+yScaleByPlus, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE+4))

            if self.Series3CheckBox.GetValue():
                legend1.append(self.line3ND)
                legend2.append(f'HR Filtered.')
                for x,y,label in zip(xdata3ND, ydata3ND, dataNDBins3.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy+yScaleByPlus, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE+4))

            if self.Series4CheckBox.GetValue():
                legend1.append(self.line4ND)
                legend2.append(f'Kinetic Filtered.')
                for x,y,label in zip(xdata4ND, ydata4ND, dataNDBins4.getBinYLabelArray()):
                   self.NumberDensityPlot.frames.append(self.NumberDensityPlot.axes.text(float(x)*xScaleBy, float(y)*yScaleBy+yScaleByPlus, f'{label}', ha='center', va='bottom', c=c, fontsize=FONTSIZE+4))

        self.NumberDensityPlot.axes.set_xlabel('Distance from Sol [pc]', fontsize=FONTSIZE+10)

        self.NumberDensityPlot.axes.set_ylabel(f'Systems per bin', fontsize=FONTSIZE+10)

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
        
        
        if prntVersion:
            legend = self.NumberDensityPlot.axes.get_legend()
            if legend:
                legend.remove()
        else:
            self.NumberDensityPlot.axes.legend(legend1, legend2)
            

        # Configure axes tick font size
        self.NumberDensityPlot.axes.tick_params(axis='both', which='major', labelsize=FONTSIZE + 4)
        self.NumberDensityPlot.axes.tick_params(axis='both', which='minor', labelsize=FONTSIZE + 4)

        # Configure x-axis and y-axis specifically
        self.NumberDensityPlot.axes.xaxis.set_major_locator(ticker.AutoLocator())
        self.NumberDensityPlot.axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        self.NumberDensityPlot.axes.xaxis.set_tick_params(labelsize=FONTSIZE + 6, direction='in', pad=10)

        self.NumberDensityPlot.axes.yaxis.set_tick_params(labelsize=FONTSIZE + 6, direction='in', pad=10)

        #self.NumberDensityPlot.axes.xaxis.set_major_locator(ticker.AutoLocator())
        #self.NumberDensityPlot.axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        self.NumberDensityPlot.axes.tick_params(axis='both', which='major', labelsize=FONTSIZE + 6)  # Adjust labelsize as needed

        self.NumberDensityPlot.axes.set_xlabel('Distance from Sol [pc]', fontsize=FONTSIZE+6)
        self.NumberDensityPlot.axes.set_ylabel(f'Systems per bin', fontsize=FONTSIZE+6)

        self.NumberDensityPlot.draw_linear()

        # Reapply font sizes
        self.NumberDensityPlot.axes.tick_params(axis='both', which='major', labelsize=FONTSIZE +6)
        self.NumberDensityPlot.axes.tick_params(axis='both', which='minor', labelsize=FONTSIZE + 6)
        self.NumberDensityPlot.canvas.draw()
        #self.drawLinear()
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
        
        self.saveConfFiles('numberOut')
             
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
        self.mainPanel=mainPanel
        self.parent=parent  # Keep notebook as common parent to store '.data'

        self.sizer_v=wx.BoxSizer(wx.VERTICAL)
        fgsizer = wx.FlexGridSizer(cols=12, hgap=0, rows=10, vgap=0)           # On left hand side
        self.sizer_v.Add(fgsizer)
        
        self.fg2sizer = wx.FlexGridSizer(cols=3, hgap=0, rows=1, vgap=0)           # On left hand side
        self.sizer_v.Add(self.fg2sizer)
        
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
        self.fg2sizer.Add(self.binaryList, 0, wx.ALL, 2)
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
        # webview.WebView.MSWSetEmulationLevel(webview.WEBVIEWIE_EMU_DEFAULT)

        # Find an available backend
        backend = None
        for id, name in backends:
            available = webview.WebView.IsBackendAvailable(id)
            #log.write("Backend 'wx.html2.{}' availability: {}\n".format(name, available))
            if available and backend is None:
                backend = id
        self.cosmicBrowser = webview.WebView.New(self, backend=backend, id=wx.ID_ANY, url="", pos=wx.DefaultPosition, size=(750, 750))
        #self.cosmicBrowser = wx.html2.WebView.New(self, id=wx.ID_ANY, url="", pos=wx.DefaultPosition, size=(750, 750))
        self.fg2sizer.Add(self.cosmicBrowser)
        # Create summary results list box.
        self.summaryList=ListCtrl(self, size=(500, 750)) 
        self.fg2sizer.Add(self.summaryList, 0, wx.ALL, 2)
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
        print(len(self.exportDisplay))
        for index, row  in self.exportDisplay.iterrows():
            try:
                V2D = math.sqrt(row.vRA**2+row.vDEC**2)
            except:
                V2D=0
            print(row)
            try:
                DIST = (row.DIST1+row.DIST2)/2
            except:
                DIST=0
            try:
                self.binaryList.Append([row.SOURCE_ID_PRIMARY,row.SOURCE_ID_SECONDARY, round(row.r,4), round(V2D,4), round(DIST,2)])
            except:
                pass
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
        try:
            self.summaryList.Append(['mag',self.returnRounded(binaryROW.mag1,4),self.returnRounded(binaryROW.mag2,4)])
        except Exception:
            return
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
        #for key, value in array:
        #    try:
        #        self.summaryList.Append([key,self.returnRounded(binaryROW.Log10r,4),''])
        #    except Excetion:
        #            print (key, value, "Missing")
    
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
#import wx
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
#
#FONTSIZE = 10  # Define the font size as a global variable

class MatplotlibPanel(wx.Panel):
    def __init__(self, parent, size, projection='rectilinear'):
        wx.Panel.__init__(self, parent, size=size)
        self.parent = parent
        
        self.projection=projection 
        self.figure = Figure(figsize=(8, 5))
        
        # Axes & labels
        self.axes = self.figure.add_subplot(111, projection=projection)
        self.frames = []
        
        if projection == 'aitoff':
            self.axes.set_xlabel('Longitude [radians]', fontsize=FONTSIZE)
            self.axes.set_ylabel('Latitude [radians]', fontsize=FONTSIZE)
            self.axes.set_title("Aitoff Projection", fontsize=FONTSIZE)
            self.axes.grid(visible=True, which='major', axis='both')
        else:
            self.axes.set_ylabel(r'$\tilde{v}$ in sky plane', fontsize=FONTSIZE)
            self.axes.set_xlabel(r'$r_{sky}$ / $r_{MOND}$', fontsize=FONTSIZE)
            self.axes.set_title("<n> binary pairs showing actual velocity and Newtonian expectation", fontsize=FONTSIZE)
            self.axes.set_yscale('log', nonpositive='clip')
            self.axes.set_xscale('log', nonpositive='clip')
        self.axes.patch.set_facecolor('0.25')  # Grey shade
        self.axes.grid(visible=True, which='major', axis='both')
        self.axes.set_autoscale_on(True)
        #
        self.figure.tight_layout(h_pad=1, w_pad=1)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        # Hidden toolbar
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)

    def set_limits(self, x_limits, y_limits):
        if self.projection == 'rectilinear':  # New condition
            x_limits = (max(1e-10, x_limits[0]), x_limits[1])  # Avoid setting zero or negative values
            y_limits = (max(1e-10, y_limits[0]), y_limits[1])
            self.axes.set_xlim(x_limits)
            self.axes.set_ylim(y_limits)    

    def draw(self, line, xdata, ydata, error, error_data):
        
        if self.projection == 'rectilinear':
            if hasattr(self.parent, 'combo_yLog') and self.parent.combo_yLog.GetValue() == 'log':
                self.axes.set_yscale('log', nonpositive='clip')
            else:
                self.axes.set_yscale('linear')
            self.axes.relim()
            self.axes.autoscale_view(True, True, True)
        
        self._set_tick_params()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
    def draw_linear(self):
        self.axes.set_xscale('linear')
        self.axes.set_yscale('linear')
        self.axes.relim()
        self.axes.autoscale_view(True, True, True)
        
        self._set_tick_params()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def format_print(self):
        self.axes.patch.set_facecolor('1')  # White


    def _set_tick_params(self):
        angle = 0
        for tick in self.axes.xaxis.get_major_ticks():
            tick.label1.set_fontsize(FONTSIZE2)  # Updated from tick.label to tick.label1
            tick.label1.set_rotation(angle)    # Updated from tick.label to tick.label1
        for tick in self.axes.yaxis.get_major_ticks():
            tick.label1.set_fontsize(FONTSIZE2)  # Updated from tick.label to tick.label1
            tick.label1.set_rotation(angle)    # Updated from tick.label to tick.label1
            
        if self.projection == 'rectilinear':
            for tick in self.axes.xaxis.get_minor_ticks():
                tick.label1.set_fontsize(FONTSIZE2)  # Updated from tick.label to tick.label1
                tick.label1.set_rotation(angle)    # Updated from tick.label to tick.label1
            for tick in self.axes.yaxis.get_minor_ticks():
                tick.label1.set_fontsize(FONTSIZE2)  # Updated from tick.label to tick.label1
                tick.label1.set_rotation(angle)    # Updated from tick.label to tick.label1


if __name__ == '__main__':
    app = wx.App(0)
    frame = wx.Frame(None, id=wx.ID_ANY, title="Binary Star Workbench", pos=wx.DefaultPosition, size=[1800,950])
    fa = MainPanel(frame)
    frame.Show()
    app.MainLoop()
