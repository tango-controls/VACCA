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

import time,os,sys,traceback,imp
from PyQt4.QtCore import SIGNAL
import fandango,taurus
import vacca
from fandango import partial,FakeLogger as FL
from taurus.qt import Qt
from taurus.qt.qtgui.taurusgui.utils import PanelDescription, ExternalApp, ToolBarDescription, AppletDescription
from vacca.panel import VaccaAction,VaccaSplash
from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath,DB_HOST,\
    DEFAULT_PATH,get_config_file

# (end of import section)
#==============================================================================

#print ('*'*80+'\n')*1
print 'In vacca.config(%s)'%globals().get('CONFIG_DONE',None)
#print ('*'*80+'\n')*1

WDIR = WORKING_DIR
print 'WORKING_DIR: %s:%s'%(WORKING_DIR,wdir(''))
print 'VACCA_PATH: %s:%s'%(VACCA_PATH,vpath(''))

try:

    try:
        assert Qt.QApplication.instance(),'QApplication not running!'
        splash = VaccaSplash()
    except:
        print "QApplication Instance do not exist!"

    try:
        import default
    except:
        traceback.print_exc()        

    #===============================================================================
    # Loading of Config Files
    #===============================================================================

    #: The Config file will be either TANGO_HOST.py or a python module passed
    #: as argument
    SETTINGS = '/home/$USER/.config/$ORGANIZATION/$GUI_NAME'

    #: Options can be specified in default.py file and
    #: CONFIG can be a .py file passed as argument or a TANGO_HOST.py file in
    #: vacca folder.
    CONFIG = get_config_file()

    #: ALL Variables that can be defined in CONFIG FILE
    OPTIONS = [
        'GUI_NAME','WDIR','DOMAIN','TARGET',
        'JDRAW_FILE','JDRAW_TREE','JDRAW_HOOK','GRID','USE_DEVICE_TREE',
        'COMPOSER','CUSTOM_TREE','EXTRA_DEVICES','GAUGES','DEVICE',
        'USE_DEVICE_PANEL','EXTRA_WIDGETS','EXTRA_PANELS','TOOLBARS','PANEL_COMMAND',
        'AttributeFilters','CommandFilters','IconMap',
        'URL_HELP','URL_LOGBOOK','VACCA_LOGO','ORGANIZATION_LOGO',
        ]
    
    if CONFIG:
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

    #: CUSTOM_LOGO. It can be an absolute path,or relative to the app dir or a
    #: resource path. If commented out, ":/taurus.png" will be used
    CUSTOM_LOGO = VACCA_LOGO

    # You can provide an URI for a manual in html format
    # (comment out or make MANUAL_URI=None to skip creating a Manual panel)
    #MANUAL_URI = '' #URL_HELP #'http://packages.python.org/taurus'

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

    #: USE_DEVICE_PANEL:  True or False, To Show by default the DevicePanel
    USE_DEVICE_PANEL = USE_DEVICE_PANEL

    if USE_DEVICE_PANEL:
        print '>'*20+'Loading Device panel ...'
        from vacca.panel import VaccaPanel
        panel = VaccaPanel.getPanelDescription('Device')

    #: USE_DEVICE_TREE:  True or False, To Show by default the Device_Tree
    USE_DEVICE_TREE = USE_DEVICE_TREE

    if USE_DEVICE_TREE or JDRAW_FILE or EXTRA_DEVICES:
        print '>'*20+'Loading Tree panel ...'
        from tree import *


        #why?
        # try:
        #     panelclass = VaccaAction(default=PANEL_COMMAND)
        #     Qt.QObject.connect(Qt.QApplication.instance(), Qt.SIGNAL(
        #      "lastWindowClosed()"), panelclass.kill )
        #     VaccaTree.setDefaultPanelClass(panelclass)
        # except:
        #     print "Cannot instance Device Tree"
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

    #: JDRAW_FILE:  The JDRAW file to create the Synoptic
    JDRAW_FILE = JDRAW_FILE

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

    #: GRID:  True/False to show by default ehe GRID Panel.
    GRID = GRID


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

    #: COMPOSER:  True/False to show by default the COMPOSER Panel.
    COMPOSER = COMPOSER

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


    #: EXTRA_PANELS:  disctionary of Extra Panels to Show by default.
    EXTRA_PANELS = EXTRA_PANELS

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



    #: EXTRA_WIDGETS: The Dictionary of EXTRA_WIDGETS Panels
    #:
    #:('vacca.properties.VaccaPropTable',wdir('vacca/image/widgets/Properties.png')),
    #:('vacca.panel.VaccaPanel',wdir('vacca/image/widgets/Panel.png')),
    EXTRA_WIDGETS = EXTRA_WIDGETS





    #: EXTRA_CATALOG_WIDGETS: The Dictionary of EXTRA_CATALOG_WIDGETS Panels to Show by
    #: default.
    #:Is the Sum of EXTRA_WIDGETS and the custom Widgets defined in config.py
    EXTRA_CATALOG_WIDGETS = []
    EXTRA_CATALOG_WIDGETS = EXTRA_WIDGETS+[
        #('vacca.VacuumProfile',WDIR+'image/ProfilePlot.jpg'),
        #('vacca.plot.PressureTrend',WDIR+'image/PressureTrend.jpg'),
        #('vacca.VacuumGrid',WDIR+'image/BLGrid.jpg'),
        #('vacca.VerticalGrid',WDIR+'image/VerticalGrid.jpg'),
        ('vacca.properties.VaccaPropTable',wdir('vacca/image/widgets/Properties.png')),
        ('fandango.qt.QEvaluator',':/snapshot/large/snapshot/TaurusShell.png'),
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





    #: The Vacca Panels to show in the JogsBar
    EXTRA_PANELS = {}

    EXTRA_PANELS['Properties'] = {'class' : vacca.VaccaPropTable}
    EXTRA_PANELS['DevicePanel'] = {'class' : vacca.VaccaPanel}
    EXTRA_PANELS['Panic']= {'class' : vacca.VaccaPanic       }

    vacca.addCustomPanel2Gui(EXTRA_PANELS)

    # from fandango.qt import Qt
    # app = Qt.QApplication.instance()
    # button = TaurusLauncherButton(widget =
    #                            vacca.properties.VaccaPropTable.getPanelDescription('Properties2'))
    #
    # widgets = app.allWidgets()
    # print widgets
    # taurusgui = None
    # for widget in widgets:
    #     print type(widget)
    #     widgetType = str(type(widget))
    #     if 'taurus.qt.qtgui.taurusgui.taurusgui.TaurusGui' in widgetType:
    #         taurusgui = widget
    # taurusgui.jorgsBar.addWidget(button)
    #
    # from taurus.external.qt import QtGui
    # exitAction = QtGui.QAction(QtGui.QIcon(WDIR+'vacca/image/icons/panic.gif'),
    #                            'vacca.properties.VaccaPropTable.getPanelDescription', app)
    # #print WDIR
    # #exitAction.setShortcut('Ctrl+Q')
    #
    # def launchProp():
    #     print "LaunchProp"
    #     #c = vacca.properties.VaccaPropTable.getPanelDescription('test')
    #     taurusgui = None
    #     for widget in widgets:
    #         widgetType = str(type(widget))
    #         if 'taurus.qt.qtgui.taurusgui.taurusgui.TaurusGui' in widgetType:
    #             taurusgui = widget
    #     taurusgui.createCustomPanel(vacca.properties.VaccaPropTable.getPanelDescription())
    #
    # Qt.QObject.connect(exitAction, SIGNAL("triggered()"),
    #         launchProp)
    #
    # #exitAction.triggered.connect(QtGui.qApp.quit)
    # taurusgui.jorgsBar.addAction(exitAction)

    print '>'*20+'Config Finished ...'
    globals()['CONFIG_DONE'] = True

except:
    print traceback.format_exc()

