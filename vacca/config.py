#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
###########################################################################

"""
configuration file used by Vacca to construct a GUI based on TaurusGUI  

This configuration file determines the default, permanent, pre-defined
contents of the GUI. While the user may add/remove more elements at run
time and those customizations will also be stored, this file defines what a
user will find when launching the GUI for the first time.
"""

#==============================================================================
# Import section. You probably want to keep this line. Don't edit this block 
# unless you know what you are doing

import fandango
import taurus
import vacca
from taurus.qt import Qt
from taurus.qt.qtgui.taurusgui.utils import PanelDescription, ExternalApp, ToolBarDescription, AppletDescription
from vacca.panel import VaccaAction,VaccaSplash
import time
from fandango import partial,FakeLogger as FL

# (end of import section)
#==============================================================================

import os,sys,fandango,traceback,imp

#print ('*'*80+'\n')*1
print 'In vacca.config(%s)'%globals().get('CONFIG_DONE',None)
#print ('*'*80+'\n')*1

assert Qt.QApplication.instance(),'QApplication not running!'

from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath
WDIR = WORKING_DIR
print 'WORKING_DIR: %s:%s'%(WORKING_DIR,wdir(''))
print 'VACCA_PATH: %s:%s'%(VACCA_PATH,vpath(''))

try:
    import default
    from .utils import DB_HOST,DEFAULT_PATH,get_config_file
    splash = VaccaSplash()
    
    #===============================================================================
    # Loading of Config Files
    #===============================================================================
    
    #The Config file will be either TANGO_HOST.py or a python module passed as argument
    SETTINGS = '/home/$USER/.config/$ORGANIZATION/$GUI_NAME'
    
    #Options can be specified in default.py file and 
    #CONFIG can be a .py file passed as argument or a TANGO_HOST.py file in vacca folder.
    CONFIG = get_config_file()
    
    #ALL Variables that can be defined in CONFIG FILE
    OPTIONS = [
        'GUI_NAME','WDIR','DOMAIN','TARGET',
        'JDRAW_FILE','JDRAW_TREE','JDRAW_HOOK','GRID','USE_DEVICE_TREE',
        'COMPOSER','CUSTOM_TREE','EXTRA_DEVICES','GAUGES','DEVICE',
        'USE_DEVICE_PANEL','EXTRA_WIDGETS','EXTRA_PANELS','TOOLBARS','PANEL_COMMAND',
        'AttributeFilters','CommandFilters','IconMap',
        'URL_HELP','URL_LOGBOOK','VACCA_LOGO','ORGANIZATION_LOGO',
        ]
    for op in OPTIONS:
        if hasattr(CONFIG,op):
            v = getattr(CONFIG,op)
            print '\t%s: \t%s = %s'%(CONFIG.__name__,op,str(v)[:80])
            setattr(default,op,v)
    
    if hasattr(CONFIG,'COMPOSER') and not hasattr(CONFIG,'DEVICE'):
        default.DEVICE = default.COMPOSER
        
    #Trying to Load rith-toolbar apps from dictionary (NOTE: this doesn't work)
    if hasattr(CONFIG,'EXTRA_APPS'): 
        print 'Loading %s apps from %s'%(str(CONFIG.EXTRA_APPS.keys()),CONFIG.__name__)
        [setattr(default,X,AppletDescription(**app)) for X,app in CONFIG.EXTRA_APPS.items()]
    
    #Adding Variables to Namespace where taurusgui can found them
    from default import *
    
    #===============================================================================
    # General info.
    #===============================================================================
    GUI_NAME = '%s-%s at %s'%(GUI_NAME,getattr(CONFIG,'__name__',TARGET),DB_HOST)
    ORGANIZATION = 'VACCA'
    ORGANIZATION_LOGO = ORGANIZATION_LOGO
    
    SINGLE_INSTANCE = False
    
    # Specific logo. It can be an absolute path,or relative to the app dir or a 
    # resource path. If commented out, ":/taurus.png" will be used
    CUSTOM_LOGO = VACCA_LOGO
    
    # You can provide an URI for a manual in html format
    # (comment out or make MANUAL_URI=None to skip creating a Manual panel) 
    MANUAL_URI = '' #URL_HELP #'http://packages.python.org/taurus'
    
    #===============================================================================
    # Define panels to be shown.  
    # To define a panel, instantiate a PanelDescription object (see documentation
    # for the gblgui_utils module)
    #===============================================================================
    print '>'*20+'Loading Trend panel ... %s'%','.join(GAUGES)
    trend = PanelDescription('Gauges',
                        classname = 'vacca.plot.PressureTrend',
                        model = GAUGES)
    """
    ## Description of signals used in Vacca
    * SelectedInstrument: goes from taurusgui and tree into panel/synoptic
    * SelectionMultiple: goes from panic/finder/... to synoptic to display multiple elements
    * JDrawIn/JDrawOut: used only if JDRAW_HOOK defined, to transform data between synoptic and selection
    """
    
    #Removable due to high CPU usage due to dummy threads
    if USE_DEVICE_PANEL:
        print '>'*20+'Loading Device panel ...'
        #from taurus.qt.qtgui.panel import TaurusDevicePanel as VaccaPanel
        from vacca.panel import VaccaPanel
        #if AttributeFilters: VaccaPanel.setAttributeFilters(AttributeFilters)
        #if CommandFilters: VaccaPanel.setCommandFilters(CommandFilters)
        #if IconMap: VaccaPanel.setIconMap(IconMap)
        device = PanelDescription('Device',
                            classname = 'vacca.panel.VaccaPanel', 
                            model=DEVICE,
                            sharedDataRead={'SelectedInstrument':'setModel'},
                            )
    
    if USE_DEVICE_TREE or JDRAW_FILE or EXTRA_DEVICES:
        print '>'*20+'Loading Tree panel ...'
        from tree import *
        panelclass = VaccaAction(default=PANEL_COMMAND)        
        Qt.QObject.connect(Qt.QApplication.instance(), Qt.SIGNAL("lastWindowClosed()"), panelclass.kill )
        VaccaTree.setDefaultPanelClass(panelclass)
        logger = fandango.Logger()
        printf = logger.info
        def filterMatching(a,dct=AttributeFilters,p=printf):
            match = False
            if a.lower().endswith('/state'): return True
            elif a.lower().endswith('/status'): return False
            for k,l in dct.items():
                if fandango.searchCl(k,a.rsplit('/',1)[0]):
                    for t in l: #T is every declared Tab for panel (TabName,[attrlist]); or just attrname when not using tabs
                        p((k,t))
                        f = t[-1] if all(map(fandango.isSequence,(t,t[-1]))) else [t]
                        if any(fandango.matchCl(v,a.rsplit('/',1)[-1]) for v in f): 
                            match =True
            return match
        VaccaTree.setDefaultAttrFilter(filterMatching)
        if IconMap: VaccaTree.setIconMap(IconMap)
        tree = PanelDescription('Tree',
                            classname = 'vacca.VaccaTree',#'vacca.VaccaTree',#'TaurusDevTree',
                            model = CUSTOM_TREE or ','.join(EXTRA_DEVICES),
                            sharedDataRead={'LoadItems':'addModels',
                                ##DISABLED BECAUSE TRIGGERED RECURSIVE SELECTION, TO BE AVOIDED IN TREE
                                #'SelectedInstrument':'findInTree',
                                }, #It will load devices from synoptic
                            sharedDataWrite={'SelectedInstrument':'deviceSelected(QString)'}
                            )
    

    if JDRAW_FILE:
        print '>'*20+'Loading Synoptic panel new ... %s, %s, %s'%(JDRAW_FILE,
                                                         JDRAW_HOOK, JDRAW_TREE)
        print '>'*20
        print '>'*20
        print '>'*20
        from vacca.synoptics import VaccaSynoptic
        try:
            synoptic = VaccaSynoptic.getPanelDescription('Synoptic',JDRAW_FILE,JDRAW_HOOK,JDRAW_TREE)
        except:
            traceback.print_exc()
            sys.exit()



    if GRID:
        print '>'*20+'Loading Grid panels ...'
        
        GRID['frames'] = False
        GRID['labels'] = False
        GRID['units'] = False
        
        from .grid import VaccaGrid, VaccaVerticalGrid


        try:
            grid = VaccaGrid.getGridPanelDescription(GRID)
        except:
            print 'Unable to create Grid'

        try:
            vgrid = VaccaVerticalGrid.getVerticalGridPanelDescription(GRID)
        except:
            print 'Unable to create VerticalGrid'
    
    if COMPOSER:
        def VacuumProfile():
            print 'VacuumProfile()'
            from . import plot
            p = plot.VaccaProfilePlot()
            p.setModel(COMPOSER)
            return p
        try:
            print '>'*20+'Loading Profile panel ...'
            profile = PanelDescription('Profile',
                            classname = 'vacca.plot.VaccaProfilePlot',
                            model = COMPOSER,
                            )
        except:
            print 'Unable to create ProfilePlot'
            
    import vacca.properties
    properties = vacca.properties.VaccaPropTable.getPanelDescription('Properties')
            
    if EXTRA_PANELS:
        print '>'*20+'Loading Extra panels ... %s'%str(EXTRA_PANELS)
        if not fandango.isMapping(EXTRA_PANELS):
            EXTRA_PANELS = dict(('extra%d'%(i+1),p) for i,p in enumerate(EXTRA_PANELS))
            
        def get_panel(i):
            pargs = EXTRA_PANELS[i]
            if not fandango.isSequence(pargs): return pargs
            elif len(pargs)==3: return PanelDescription(pargs[0],classname=pargs[1],model=pargs[2])
            else: return PanelDescription(pargs[0],classname=pargs[1],model=pargs[2],sharedDataRead=pargs[3],sharedDataWrite=pargs[4])

        for k,p in EXTRA_PANELS.items(): # if k not in (1,2,3,4,5):
            try:
                vars()[k] = get_panel(k)
            except:
                traceback.print_exc()

    toolbars = []
    for name,obj in (TOOLBARS or []):
        toolbars.append(ToolBarDescription(name,
            classname = obj.split('.')[-1],
            modulename = obj.rsplit('.',1)[0],
            #sharedDataWrite={'selectedPerspective':'blabla'}
            ))
        toolbar = toolbars[-1]
    
    #===============================================================================
    # Adding other widgets to the catalog of the "new panel" dialog.
    # pass a tuple of (classname,screenshot)
    # -classname may contain the module name.
    # -screenshot can either be a file name relative to the application dir or 
    # a resource URL or None
    #===============================================================================
    EXTRA_CATALOG_WIDGETS = EXTRA_WIDGETS+[
        #('vacca.VacuumProfile',WDIR+'image/ProfilePlot.jpg'),
        #('vacca.plot.PressureTrend',WDIR+'image/PressureTrend.jpg'),
        #('vacca.VacuumGrid',WDIR+'image/BLGrid.jpg'),
        #('vacca.VerticalGrid',WDIR+'image/VerticalGrid.jpg'),
        ('vacca.properties.VaccaPropTable',':/designer/devs_table.png'),#WDIR+'image/equips/cable_serie_rs232.jpg'),
        ('fandango.qt.QEvaluator',':/designer/dockwidget.png'),
        ]

    #===============================================================================
    # Define custom toolbars to be shown. To define a toolbar, instantiate a
    # ToolbarDescription object (see documentation for the gblgui_utils module)
    #===============================================================================
    
    #dummytoolbar = ToolBarDescription('Empty Toolbar',
                            #classname = 'QToolBar',
                            #modulename = 'PyQt4.Qt')
    
    #panictoolbar = ToolBarDescription('Panic Toolbar',
    #                        classname = 'PanicToolbar',
    #                        modulename = 'tangopanic')
    
    #===============================================================================
    # Define custom applets to be shown in the applets bar (the wide bar that
    # contains the logos). To define an applet, instantiate an AppletDescription
    # object (see documentation for the gblgui_utils module)
    #===============================================================================
    
    #mon2 = AppletDescription('Dummy Monitor',
                            #classname = 'TaurusMonitorTiny',
                            #model='eval://1000*rand(2)')
    #import os
    #xmambo = AppletDescription('ctarchiving',
                            #classname = 'vacca.panel.VaccaAction',
                            #model=["Archiving",WDIR+'image/PressureTrend.jpg','ctarchiving'],
                            #)
    
    # ALREADY LOADED FROM vacca.default.EXTRA_APPS
    
    #===============================================================================
    # Define which External Applications are to be inserted.
    # To define an external application, instantiate an ExternalApp object
    # See TaurusMainWindow.addExternalAppLauncher for valid values of ExternalApp
    #===============================================================================

    xvacca = ExternalApp(cmdargs=['konqueror',URL_HELP], text="Alba VACuum Controls Application", icon=WDIR+'image/icons/cow-tux.png')
    xjive = ExternalApp(cmdargs=['jive'], text="Jive")#, icon=WDIR+'image/icons/cow-tux.png')
    xastor = ExternalApp(cmdargs=['astor'], text="Astor")#, icon=WDIR+'image/icons/cow-tux.png')
    
    #===============================================================================
    # POOL RELATED OPTIONS
    #===============================================================================
    
    #===============================================================================
    # Macro execution configuration
    # (comment out or make MACRO_SERVER=None to skip creating a macro execution 
    # infrastructure)
    #===============================================================================
    #MACROSERVER_NAME = 
    #DOOR_NAME = 
    #MACROEDITORS_PATH = 
    
    #===============================================================================
    # Monitor widget (This is obsolete now, you can get the same result defining a
    # custom applet with classname='TaurusMonitorTiny')
    #===============================================================================
    # MONITOR = ['sys/tg_test/1/double_scalar_rww']
    
    # Set INSTRUMENTS_FROM_POOL to True for enabling auto-creation of
    # instrument panels based on the Pool Instrument info
    INSTRUMENTS_FROM_POOL = False
    
    #===============================================================================
    # THIS SYNOPTIC OPTION IS POOL-related; IT'S NOT THE MAIN APPLICATION SYNOPTIC!!!
    # If you want an instrument selection synoptic, set the SYNOPTIC variable
    # to the file name of a jdraw file. If a relative path is given, the directory
    # containing this configuration file will be used as root
    # (comment out or make SYNOPTIC=None to skip creating a synoptic panel)
    #===============================================================================
    SYNOPTIC = [] #'images/example01.jdw','images/syn2.jdw']    
    
    #===============================================================================
    
    
    print '>'*20+'Config Finished ...'
    globals()['CONFIG_DONE'] = True

except:
    print traceback.format_exc()

