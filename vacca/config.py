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
TaurusGUI configuration file used to convert Taurus into VACCA

This file should be NOT modified.

.. toctree::
   :maxdepth: 4

h2. Usage
=========

This configuration file determines the default, permanent, pre-defined
contents of the GUI. While the user may add/remove more elements at run
time and those customizations will also be stored, this file defines what a
user will find when launching the GUI for the first time.

Don't modify this file, use default.py to do a simple setup of your
facility and paths and a CONFIG.py file (based on default.py format) to 
construct a VACCA gui for each subsystem.

h3. Contents
------------

This file mainly defines two kinds of objects:

 * Panel descriptors: the panels to be shown.
   To define a panel, instantiate a PanelDescription object (see documentation
   for the gblgui_utils module)
 * Panels will be TREE, JDRAW_FILE, DEVICE, ...
   
 * QSignals (managed by Taurus Shared Data Manager):
  * SelectedInstrument: goes from taurusgui and tree into panel/synoptic
  * SelectionMultiple: goes from panic/finder/... to synoptic to display multiple elements
  * JDrawIn/JDrawOut: used only if JDRAW_HOOK defined, to transform data between synoptic and selection
  * lastWindowClosed: signal will close all opened widgets and dialogs on application exit

h3. Extending Taurus GUI
------------------------

We will differentiate between:

 - Tools (applications launched in a separate process)
 - Panels (widgets embeddable in the application)
 - Applets (widgets or applications launched from the right-side bar)
 - Widgets (widgets not instantiated, but added to the catalog when adding a new panel).
 
The config variables to include new Tools/Panels/Apps/Widgets are:

Use EXTRA_WIDGETS to add new widgets to the catalog and the right-side toolbar.
They will be added to EXTRA_CATALOG_WIDGETS, that contains default extra widgets.

Use EXTRA_PANELS to force new Panels always at startup.
They will be instantiated and running in background.

Use EXTRA_APPS to add launchers to the toolbar.
Creates new AppletDescription objects to add elements to the right-side toolbar.

Use EXTRA_TOOLS to add launchers to the "External Apps" toolbar.
Creates new ExternalApp objects to add elements to the top menu and toolbar.

Use TOOLBARS to add new Toolbars: 
  TOOLBARS = [('Sectors','SR.sector.get_sectors_toolbar')]
Creates new ToolBarDescription objects.


h2. Config Variables
====================

Described below

"""

#==============================================================================
# Import section. You probably want to keep this line. Don't edit this block 
# unless you know what you are doing

import time,os,sys,traceback,imp,inspect
from PyQt4.QtCore import SIGNAL
import fandango,taurus
import vacca,vacca.utils
from .doc import get_autodoc,get_vars_docs
from fandango import partial,FakeLogger as FL
from taurus.qt import Qt
from taurus.qt.qtgui.taurusgui.utils import \
  PanelDescription, ExternalApp, ToolBarDescription, AppletDescription
from vacca.panel import VaccaAction,VaccaSplash
from vacca.utils import *

# (end of import section)
#==============================================================================

#print ('*'*80+'\n')*1
print 'In vacca.config(%s)'%globals().get('CONFIG_DONE',None)
#print ('*'*80+'\n')*1

VACCA_DIR = get_config_properties(os.getenv('VACCA_CONFIG')).get('VACCA_DIR',VACCA_DIR)
vacca.utils.VACCA_DIR = VACCA_DIR
WDIR = VACCA_DIR

try:

    if VACCA_DIR:
        print('Changing directory to VACCA_DIR:%s,%s' %(VACCA_DIR,os.environ['VACCA_DIR' ]))
        os.chdir(os.environ['VACCA_DIR'])
        sys.path.append(os.environ['VACCA_DIR'])

    try:
        app = Qt.QApplication.instance()
        assert app,'QApplication not running!'
        splash = VaccaSplash()
    except:
        print "QApplication Instance do not exist!"
        app = None

    try:
        import default
    except:
        try:
            default = get_config_file(imp.find_module('vacca')[1]+'/default.py.ini')
        except:
            traceback.print_exc()

    #===============================================================================
    # Loading of Config Files
    #===============================================================================

    #: Config file where perspectives will be saved
    SETTINGS = '/home/$USER/.config/$ORGANIZATION/$GUI_NAME'

    #: Default options are set in default.py file and later customized in a config file.
    #: This CONFIG can be a .py file passed as argument or a TANGO_HOST.py file in
    #: vacca folder.
    CONFIG = get_config_file()

    #: ALL Variables that can be defined in CONFIG FILE
    OPTION_LISTS = [
        ('General Info', ['GUI_NAME','URL_HELP','URL_LOGBOOK','VACCA_LOGO','ORGANIZATION','ORGANIZATION_LOGO',]),
        ('Installation', ['WDIR','SETTINGS']),
        ('Sub systems', ['DOMAIN','TARGET','COMPOSER',]),
        ('Device Tree', ['USE_DEVICE_TREE','CUSTOM_TREE','EXTRA_DEVICES',]),
        ('Synoptics', ['JDRAW_FILE','JDRAW_TREE','JDRAW_HOOK','GRID',]),
        ('Device Panel', ['USE_DEVICE_PANEL','DEVICE','PANEL_COMMAND','AttributeFilters','CommandFilters','IconMap',]),
        ('Plot', ['GAUGES']),
        ('Widgets', ['EXTRA_WIDGETS','EXTRA_PANELS','TOOLBARS','MENUS','EXTRA_APPS','EXTRA_CATALOG_WIDGETS']),]

    OPTIONS = [o for c,l in OPTION_LISTS for o in l]
    
    for c,l in OPTION_LISTS:
        __doc__ += get_vars_docs(__name__,title=c+' Options',module_vars=l,subtitle=False)
    
    if CONFIG:
        for op in OPTIONS:
            limit = 800
            if hasattr(CONFIG,op):
                v = getattr(CONFIG,op)
                print '\t%s: \t%s = %s'%(CONFIG.__name__,op,str(v)[:limit])
                setattr(default,op,v)
        
        if hasattr(CONFIG,'COMPOSER') and not hasattr(CONFIG,'DEVICE'):
            default.DEVICE = default.COMPOSER
            
        #Trying to Load rith-toolbar apps from dictionary (NOTE: this doesn't work)
        #if hasattr(CONFIG,'EXTRA_APPS'): 
            #print 'Loading %s apps from %s'%(str(CONFIG.EXTRA_APPS.keys()),CONFIG.__name__)
            #[setattr(default,X,AppletDescription(**app)) for X,app in CONFIG.EXTRA_APPS.items()]
    
    #Adding all variables to Namespace where taurusgui can found them
    try:
        for k,v in vars(default).items():
            if not any((k.startswith('_'),inspect.ismodule(v))): #inspect.isfunction(v)
                vars()[k] = v
    except:
        traceback.print_exc()
    
    #===============================================================================
    # General info.
    #===============================================================================
    #: GUI_NAME will be used on application title and settings filenames
    GUI_NAME = '%s-%s at %s'%(GUI_NAME,getattr(CONFIG,'__name__',TARGET),DB_HOST)
    #: Name to be shown in right-side bar
    ORGANIZATION = ORGANIZATION
    #: Logo to be shown in right-side bar
    ORGANIZATION_LOGO = ORGANIZATION_LOGO
    
    print('SETTINGS: Perspectives will be saved/loaded from %s'%(
        SETTINGS.replace('$USER',get_env_variable('USER')).replace('$ORGANIZATION',ORGANIZATION).replace('$GUI_NAME',GUI_NAME)))
    
    SINGLE_INSTANCE = False

    #: CUSTOM_LOGO. It can be an absolute path,or relative to the app dir or a
    #: resource path. If commented out, ":/taurus.png" will be used
    CUSTOM_LOGO = VACCA_LOGO

    #: You can provide an URI for a manual in html format
    #: (comment out or make MANUAL_URI=None to skip creating a Manual panel)
    MANUAL_URI = URL_HELP #'http://packages.python.org/taurus'

    #===============================================================================
    # Define panels to be shown.
    # To define a panel, instantiate a PanelDescription object (see documentation
    # for the gblgui_utils module)
    #===============================================================================
    
    print '>'*20+'Loading Trend panel ... %s'%','.join(GAUGES)
    
    #: If defined, the default trend will be shown in logarithmic scale
    GAUGES=GAUGES
    if GAUGES:
        trend = PanelDescription('Gauges',
            classname = 'vacca.plot.PressureTrend',
            model = GAUGES)

    trends = PanelDescription('Trends',
        classname = 'vacca.plot.VaccaTrend',
        model = '')

    #: USE_DEVICE_PANEL:  True or False, To Show by default the DevicePanel
    USE_DEVICE_PANEL = USE_DEVICE_PANEL
    if USE_DEVICE_PANEL:
        print '>'*20+'Loading Device panel (%s)...' % DEVICE
        from vacca.panel import VaccaPanel
        panel = VaccaPanel.getPanelDescription('Device',model=DEVICE)

    #: USE_DEVICE_TREE:  True or False, To Show by default the Device_Tree
    USE_DEVICE_TREE = USE_DEVICE_TREE

    if USE_DEVICE_TREE or JDRAW_FILE or EXTRA_DEVICES:
        print '>'*20+'Loading Tree panel ...'
        from tree import *
        try:
            # The lastWindowClosed() signal will close all opened widgets and dialogs on application exit
            assert Qt.QApplication.instance(),'QApplication not running!'
            panelclass = VaccaAction(default=PANEL_COMMAND)
            Qt.QObject.connect(Qt.QApplication.instance(), Qt.SIGNAL(
             "lastWindowClosed()"), panelclass.kill )
            VaccaTree.setDefaultPanelClass(panelclass)
        except:
            print("Cannot instance Device Tree")
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

    #: JDRAW_FILE:  The JDRAW file to create the Synoptic, 
    #: it can be .jdw or .svg but the second option will require the svgsynoptic module from maxlab.
    JDRAW_FILE = JDRAW_FILE

    if JDRAW_FILE:
        print '>'*20+'Loading Synoptic panel new ... %s, %s, %s'%(JDRAW_FILE,
                                                         JDRAW_HOOK, JDRAW_TREE)
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
        
        from vacca.grid import VaccaGrid, VaccaVerticalGrid

        try:
            assert Qt.QApplication.instance(),'QApplication not running!'
            grid = VaccaGrid.getGridPanelDescription(GRID)
        except:
            print 'Unable to create Grid'

        ##VGRID disabled, the Vertical layout should be added as option to common GRID
        #try:
            #assert Qt.QApplication.instance(),'QApplication not running!'
            #vgrid = VaccaVerticalGrid.getVerticalGridPanelDescription(GRID)
        #except:
            #print 'Unable to create VerticalGrid'

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


    #: EXTRA_PANELS:  dictionary of Extra Panels to be shown by default.
    #: Each element may be a PanelDescription object or a tuple with its arguments.
    #:
    #: The dictionary will be defined like:
    #:  * key: Panel name
    #:  * value: list of arguments to PanelDescription
    #:  * value[0]: panel name
    #:  * value[1]: class name
    #:  * value[2]: default model
    #:  * value[3]: shared data read signal
    #:  * value[4]: shared data write signal
    #:
    #: As example, to add PANIC as extra panel use:
    #: EXTRA_PANELS['PANIC'] = ('PANIC','panic.gui.AlarmGUI','',{},{'HighlightInstruments':'devicesSelected'})
    EXTRA_PANELS = EXTRA_PANELS

    if EXTRA_PANELS:
        print '>'*20+'Loading Extra panels ... %s'%str(EXTRA_PANELS)
        if not hasattr(EXTRA_PANELS,'items'):
            EXTRA_PANELS = dict(('extra%d'%(i+1),p) for i,p in enumerate(EXTRA_PANELS))
            
        def get_panel(i):
            pargs = EXTRA_PANELS[i]
            if not fandango.isSequence(pargs): return pargs
            elif len(pargs)==3: return PanelDescription(pargs[0],classname=pargs[1],model=pargs[2])
            else: return PanelDescription(pargs[0],classname=pargs[1],model=pargs[2],sharedDataRead=pargs[3],sharedDataWrite=pargs[4])

        for k,p in EXTRA_PANELS.items():
            try:
                vars()[k] = get_panel(k)
            except:
                traceback.print_exc()

    #===============================================================================
    #: EXTRA_WIDGETS: The Dictionary of EXTRA_WIDGETS Panels
    #:
    #: Adding other widgets to the catalog of the "new panel" dialog.
    #: pass a tuple of (classname,screenshot)
    #:
    #: - classname may contain the module name.
    #: - screenshot can either be a file name relative to the application dir or
    #:   a resource URL or None
    #:
    #: examples:
    #:
    #:    ('vacca.properties.VaccaPropTable',wdir('vacca/image/widgets/Properties.png')),
    #:    ('vacca.panel.VaccaPanel',wdir('vacca/image/widgets/Panel.png')),
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
        ('vacca.properties.VaccaPropTable',vpath('image/widgets/Properties.png')),
        ('fandango.qt.QEvaluator',':/snapshot/large/snapshot/TaurusShell.png'),
        ]

    #===============================================================================
    #: TOOLBARS
    #:
    #: Define custom toolbars to be shown. To define a toolbar, instantiate a
    #: ToolbarDescription object (see documentation for the gblgui_utils module)
    #===============================================================================
    
    #dummytoolbar = ToolBarDescription('Empty Toolbar',
                            #classname = 'QToolBar',
                            #modulename = 'PyQt4.Qt')
    
    #panictoolbar = ToolBarDescription('Panic Toolbar',
    #                        classname = 'PanicToolbar',
    #                        modulename = 'tangopanic')
    
    toolbars = []
    for name,obj in (TOOLBARS or []):
        toolbars.append(ToolBarDescription(name,
            classname = obj.split('.')[-1],
            modulename = obj.rsplit('.',1)[0],
            #sharedDataWrite={'selectedPerspective':'blabla'}
            ))
        toolbar = toolbars[-1]
        
    try:
        for menu,actions in MENUS:
            vacca.utils.add_menu(menu,actions)
    except:
        traceback.print_exc()
        
    #===============================================================================
    # Define custom applets to be shown in the applets bar (the wide bar that
    # contains the logos). To define an applet, instantiate an AppletDescription
    # object (see documentation for the gblgui_utils module)
    #===============================================================================
    
    # ALREADY LOADED FROM vacca.default.EXTRA_APPS
    
    #xmambo = AppletDescription('Mambo',classname = 'vacca.panel.VaccaAction',
    # model=["Archiving",wdir('vacca/image/widgets/ProfilePlot.png'),'mambo'],)
    
    #===============================================================================
    # Define which External Applications are to be inserted.
    # To define an external application, instantiate an ExternalApp object
    # See TaurusMainWindow.addExternalAppLauncher for valid values of ExternalApp
    #===============================================================================

    # ALREADY LOADED FROM vacca.default.EXTRA_TOOLS
    
    #xvacca = ExternalApp(cmdargs=['konqueror',URL_HELP], text="Alba VACuum Controls Application", icon=WDIR+'image/icons/cow-tux.png')
    #DEFAULT_APPS = 
    
    EXTRA_TOOLS = EXTRA_TOOLS
    for name,cmdargs,icon in EXTRA_TOOLS:
        locals()['x'+name] = ExternalApp(cmdargs=cmdargs,text=name,icon=icon or None)
    
    #xjive = ExternalApp(cmdargs=['jive'], text="Jive")#, icon=WDIR+'image/icons/cow-tux.png')
    #xastor = ExternalApp(cmdargs=['astor'], text="Astor")#, icon=WDIR+'image/icons/cow-tux.png')
    
    #===============================================================================
    # POOL RELATED OPTIONS
    #===============================================================================
    
    # Set INSTRUMENTS_FROM_POOL to True for enabling auto-creation of
    # instrument panels based on the Pool Instrument info
    #MACROSERVER_NAME = 
    #DOOR_NAME = 
    #MACROEDITORS_PATH = 
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

    #: 
    from PyQt4 import Qt

    EXTRA_APPS = EXTRA_APPS
    """ The Vacca Panels to show in the JogsBar. Use EXTRA_APPS to add launchers to the toolbar.
    It will create new AppletDescription objects to add elements to the right-side toolbar.

    Examples:
     * EXTRA_APPS['Properties'] = {'class' : vacca.VaccaPropTable}
     * EXTRA_APPS['DevicePanel'] = {'class' : vacca.VaccaPanel}
     * EXTRA_APPS['Panic']= {'class' : vacca.VaccaPanic       }
     * EXTRA_APPS['ExtraDock']= {'class' : Qt.QMainWindow       }
    """
    adder = vacca.addCustomPanel2Gui(EXTRA_APPS)
    
    #Forcing nesting of dock widgets
    if app:
        try:
            main = vacca.utils.get_main_window(app)
            main.setDockNestingEnabled(True)
        except:
            traceback.print_exc()

    print '>'*20+'Config Finished ...'
    globals()['CONFIG_DONE'] = True

except:
    print traceback.format_exc()

