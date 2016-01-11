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
#############################################################################

__doc__ = """vacca.utils python module, by srubio@cells.es

vacca.utils contains several methods and classes for:
 
 - manage environment variables
 - loading config files
 - manipulate Qt color palettes
 - custom Taurus event filters
 
This file is part of Tango Control System

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

Variables can be declared in OS or as Tango.VACCA free properties

VACCA_CONFIG: *get_config_file()*

    The config file to be loaded, it can be absolute path or 
    relative to WORKING_DIR. Returned by 
    
    e.g. /homelocal/sicilia/applications/vacca/tbl2401.py
    
VACCA_DIR: *wdir('path/to/icon')* 

    The folder were VACCA should be executed, all paths within 
    the application will be relative to it. It includes all custom icons 
    that are not part of the vacca package.
    
    e.g. /homelocal/sicilia/applications/vacca/
    
VACCA_PATH: *vpath('path/to/icon')*

    Path to the VACCA library, tipically used for icons of vacca package

    e.g. /homelocal/sicilia/lib/python/site-packages/vacca

"""

import os,sys,traceback,imp,time
import fandango
from fandango.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.core.util.eventfilters import ONLY_CHANGE_AND_PERIODIC
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

def get_env_variable(var,default=''):
    """ It will try to get value from OS, then Tango.VACCA, then default """
    v = os.environ.get(var,None)
    if v: return v
    v = fandango.get_database().get_property('VACCA',var)[var]
    v =  v[0] if v and len(v) == 1 else v
    if v: return v
    return default

def get_class_property(dev_class,prop,extract=False):
    db = fandango.get_database()
    props = db.get_class_property(dev_class,prop)
    if prop in props:
        v = props[prop]
        if fandango.isSequence(v): v = list(v)
        if v == ['']: return []
        if extract and fandango.isSequence(v) and len(v)==1:
            v = v[0]
        return v
    return []
   
def get_vacca_property(prop,extract=True):
    db = fandango.get_database()
    props = db.get_property('VACCA',prop)
    if prop in props:
        v = props[prop]
        if fandango.isSequence(v): v = list(v)
        if v == ['']: return []
        if extract and fandango.isSequence(v) and len(v)==1:
            v = v[0]
        return v
    return []   

DB_HOST = fandango.tango.get_tango_host().split(':')[0]

VACCA_PATH = get_env_variable('VACCA_PATH', imp.find_module('vacca')[1]+'/../')
"""
VACCA_PATH: *vpath('path/to/icon')*

    Path to the VACCA library parent folder, tipically used for icons of vacca package
    Note, vpath(folder) will append /vacca to VACCA_PATH, to get internal vacca files.

    e.g. VACCA_PATH = /homelocal/sicilia/lib/python/site-packages
    e.g. vpath = /homelocal/sicilia/lib/python/site-packages/vacca
"""
VACCA_DIR = get_env_variable('VACCA_DIR', get_env_variable('WORKING_DIR',VACCA_PATH))
"""
VACCA_DIR: *wdir('path/to/icon')* 

    The folder were VACCA should be executed, all paths within 
    the application will be relative to it. It includes all custom icons 
    that are not part of the vacca package.
    
    e.g. /homelocal/sicilia/applications/vacca/
"""

VACCA_CONFIG = get_env_variable('VACCA_CONFIG',DB_HOST+'.py')
VACCA_CONFIG = VACCA_CONFIG.replace('$VACCA_DIR',VACCA_DIR).replace('$VACCA_PATH',VACCA_PATH)
"""
VACCA_CONFIG: 

    The config file to be loaded, it can be absolute path or 
    relative to WORKING_DIR. *get_config_file()* will import it and 
    return the content as a python module.
    
    e.g. /homelocal/sicilia/applications/vacca/tbl2401.py
"""

def _joiner(a,s,b):
    return '%s%s%s'%(a,s if a and b and s not in (a[-1],b[0]) else '',b)

if not VACCA_DIR.endswith('/'): VACCA_DIR += '/'
WORKING_DIR = VACCA_DIR #For compatibility with previous versions
#Needed for backwards compatibility
DEFAULT_PATH =  WORKING_DIR #'/homelocal/sicilia/applications/vacca/'

wdir = lambda s: _joiner(VACCA_DIR,'/',s)
vpath = lambda s: _joiner(VACCA_PATH+'/vacca','/',s)

def get_config_file(config=None):
    CONFIG_FILE = config or VACCA_CONFIG
    print('get_config_file(%s)'%CONFIG_FILE)

    if not CONFIG_FILE.startswith('/'):
        CONFIG_FILE = wdir(CONFIG_FILE)
        
    if not fandango.linos.file_exists(CONFIG_FILE):
        if fandango.linos.file_exists(CONFIG_FILE+'.py'):
            CONFIG_FILE += '.py'
        else:
            print('WARNING: %s config file not found!'%CONFIG_FILE)
            return

    print 'VaccaGUI: Loading %s ...' % CONFIG_FILE
    try: 
        CONFIG = globals().get(CONFIG_FILE,fandango.objects.loadModule(CONFIG_FILE))
        #print '\n'.join(sorted('\t%s:\t%s'%(k,getattr(CONFIG,k)) for k in dir(CONFIG) if not k.startswith('_')))
    except: 
        print traceback.format_exc()
        raise Exception,'Unable to load %s' % CONFIG_FILE
    return CONFIG

def get_shared_data_manager():
    """
    sdm = get_shared_data_manager() #Qt.qApp.SDM Singletone
    sdm.connectReader('channelName',objectInstance.method,readOnConnect=False) #Using instantiated object/function instead of names!!
    sdm.connectWriter('SelectedInstrument',out_hook,'modelChanged') #'Channel', object, 'qt signal name'
    """
    try:
        return Qt.qApp.SDM
    except:
        print('Shared Data Manager is not available! (no TaurusGUI instance?)')
        return None
    
def get_shared_data_signals():
    """
    Return the dictionary of signals and registered Qt objects.
    """
    try:
        sdm = get_shared_data_manager()
        signals = {}
        for k,v in sdm._SharedDataManager__models.items():
            signals[k] = {'readers':[],'writers':[]}
            for o,s in v._DataModel__readerSlots:
                signals[k]['readers'].append((o(),s))
            for o,s in v._DataModel__writerSignals:
                signals[k]['writers'].append((o(),s))
        return signals
    except:
        traceback.print_exc()
        return {}
                
###############################################################################
# Methods for managing palettes
    
def get_solid_brush(r, g, b, pattern=None):
    from taurus.external.qt import Qt
    brush = Qt.QBrush(Qt.QColor(r, g, b))
    brush.setStyle(Qt.Qt.SolidPattern if pattern is None else pattern)
    return brush

def get_White_palette(palette = None):
    from taurus.external.qt import Qt
    if palette is None:
        palette = Qt.QPalette()

    for e in (Qt.QPalette.Base,Qt.QPalette.Window): #QtGui.QPalette.BrightText,QtGui.QPalette.ButtonText,Qt.QPalette.Button
        for r in (Qt.QPalette.Active, Qt.QPalette.Inactive,
                  Qt.QPalette.Disabled):
            palette.setBrush(r, e, get_solid_brush(255, 255, 255))
    return palette
    
def get_halfWhite_palette(palette = None):
    from taurus.external.qt import Qt
    if palette is None:
        palette = Qt.QPalette()
    palette.setBrush(Qt.QPalette.Active, Qt.QPalette.Button,
                     get_solid_brush(255, 255, 255))
    palette.setBrush(Qt.QPalette.Inactive, Qt.QPalette.Button,
                     get_solid_brush(255, 255, 255))
    palette.setBrush(Qt.QPalette.Disabled, Qt.QPalette.Button,
                     get_solid_brush(255, 255, 255))
    return palette

def get_fullWhite_palette(palette = None):
    from taurus.external.qt import Qt
    if palette is None:
        palette = Qt.QPalette()
    palette = get_halfWhite_palette(palette)
    palette = get_White_palette(palette)
    return palette

###############################################################################
# Methods for using Taurus Event Filters

import fandango as f

class EventFilter(object):
    """ Generic event filter for taurus """
    def __init__(self,condition=None):
        self.condition = condition
    def __call__(self,s,t,v):
        if (self.condition() if f.isCallable(self.condition) else self.condition):
            return s,t,v
        else:
            return None

class EventCounter(EventFilter):
    """ Generic event counter for taurus """
    @f.Catched
    def __call__(self,s,t,v):
        try: src = s.getFullName()
        except: src = str(s)
        if not hasattr(self,'counts'): self.counts = f.defaultdict(int)
        self.counts[src] += 1
        return s,t,v
        
class OnChangeOrTimeEventFilter(EventFilter):
    """
    The instances of this class will be callables that can be used as filters
    of repeated-value events.
    If the event type is Change or Periodic, it will only pass when its
    evt_value.value is different from that of the last event received from the
    same source and type. If evt_value.value is not available in the current
    event, the whole evt_value is used for comparison and as a future reference.
    But!, if setMaxDeltaTime is set, then any event that occurred more than Delta Time seconds 
    after the last one will be allowed to pass through the chain.
    

    This is useful to avoid processing repetitive events.

    Note that you cannot use this class as a filter: you need to use an
    instance of it.

    Note 2: Use a different instance each time you insert this filter
    into a different widget unless you *really* know what you are doing.

    Example of usage::
        evf = OnChangeOrTimeEventFilter()
        evf.setDeltaTime(60.)
        filters = [evf, IGNORE_CONFIG]
        MyTaurusComponentInstance.setEventFilters(filters,preqt=True)
        filterEvent(s, t, v, filters)
    """
    def __init__(self):
        self._lastValues = {}
        self._lastTimes = {}
        self.deltaValue = 0
        self.deltaTime = 0
        
    def setDeltaValue(self,mindiff):
        self.deltaValue = mindiff
        
    def setDeltaTime(self,mindiff):
        self.deltaTime = mindiff
        
    @f.Catched
    def __call__(self, s, t, v):
        # restrict this  filter only to change and periodic events.
        if ONLY_CHANGE_AND_PERIODIC(s, t, v) is None: return s,t,v
        # block event if we recorded one before with same src, type and v.value
        new_value = getattr(v, 'value', v)
        try: new_time = ctime2time(v.time)
        except: new_time = time.time()
        try:
            if self._lastValues[(s, t)] == new_value and (not self.deltaTime or new_time<self._lastTimes[s]+self.deltaTime):
                return None
        except KeyError: pass
        # if it was't blocked, store src, type and v.value for future checks
        self._lastValues[(s, t)] =  new_value
        self._lastTimes[s] = new_time
        return s, t, v
    
    @staticmethod
    def __test__():
        import taurus,time
        from vacca.utils import EventFilter,EventCounter,OnChangeOrTimeEventFilter,MyTaurusComponent
        tbc = MyTaurusComponent('test')
        attr1,attr2 = 'test/sim/tonto/temperature','test/sim/tonto/temperate'
        tbc.setMyHandler(lambda *args:fandango.printf(str(
                    (time.ctime(),getattr(args[-1],'value',args[-1]),
                    taurus.Attribute(attr2).read().value))))
        evf = OnChangeOrTimeEventFilter()
        evf.setDeltaTime(10.)
        tbc.setEventFilters((evf,))
        tbc.setEventBufferPeriod(3.)
        tbc.setModel(attr1)
        ta = tbc.getModelObj()
        ta.changePollingPeriod(1000)
        
###############################################################################
# QT Helping Classes

from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE, TAURUS_MODEL_LIST_MIME_TYPE

class WidgetAcceptDrops(object):
    """
    Template for Taurus widgets accepting drops, deprecated by fandango.qt.Dropable
    """
    TAURUS_DEV_MIME_TYPE = TAURUS_DEV_MIME_TYPE
    TAURUS_ATTR_MIME_TYPE = TAURUS_ATTR_MIME_TYPE
    TAURUS_MODEL_MIME_TYPE = TAURUS_MODEL_MIME_TYPE
    TAURUS_MODEL_LIST_MIME_TYPE = TAURUS_MODEL_LIST_MIME_TYPE
    TEXT_MIME_TYPE = 'text/plain'
    _supportedMimeTypes = None
    
    def checkDrops(self): 
        try: self.setAcceptDrops(True)
        except: pass
    def getSupportedMimeTypes(self):
        self.checkDrops() 
        if self._supportedMimeTypes is not None: return self._supportedMimeTypes
        else: return [TEXT]
    def setSupportedMimeTypes(self,mimes):
        self._supportedMimeTypes = mimes
    def setDropEventCallback(self,callback):
        self._dropeventcallback = callback
        
    # ENABLING DROP OF DEVICE NAMES :
    def checkSupportedMimeType(self,event,accept=False): 
        if any(t in self.getSupportedMimeTypes() for t in event.mimeData().formats()):
            if accept: event.acceptProposedAction()
            return True
        return False
    def dragEnterEvent(self,event): self.checkSupportedMimeType(event,accept=True)
    def dragMoveEvent(self,event): event.acceptProposedAction()
            
    def dropEvent(self, event):
        '''reimplemented to support drag&drop of models. See :class:`QWidget`'''
        print 'In dropEvent',event
        for t in self.getSupportedMimeTypes():
            try:
                t = str(event.mimeData().data(t))
                try:
                    if t.strip():
                        print t
                        self._dropeventcallback(t)
                        return
                except: self.info(traceback.warning_exc())
            except: pass
        self.debug('Invalid data (%s) for MIMETYPE'%(repr(d)))
        event.acceptProposedAction()
        
class Draggable(object):
    """
    Template for Taurus widgets accepting drops, deprecated by fandango.qt.Draggable
    """
    
    def __init__(self):
        self._drageventcallback = lambda s=self:s.text() if hasattr(s,'text') else ''
    
    def setDragEventCallback(self,hook):
        self._drageventcallback = hook
    
    def mousePressEvent(self, event):
        '''reimplemented to provide drag events'''
        print 'In DefaultLabelWidget.mousePressEvent'
        Qt.QLabel.mousePressEvent(self, event)
        if event.button() == Qt.Qt.LeftButton:
            self.dragStartPosition = event.pos()
            
    def mouseMoveEvent(self, event):
        '''reimplemented to provide drag events'''
        if not event.buttons() & Qt.Qt.LeftButton:
            return
        mimeData = Qt.QMimeData()
        txt = str(self._drageventcallback())
        print 'Draggable.mouseMoveEvent',self._drageventcallback,txt
        mimeData.setText(txt)
        drag = Qt.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.Qt.CopyAction)
    
class DraggableLabel(Draggable,Qt.QLabel):
    def __init__(self,parent=None,text=''):
        Qt.QLabel.__init__(self,text)
        Draggable.__init__(self)

class MyTaurusComponent(TaurusBaseComponent,Qt.QObject):
    def __init__(self,name='test'):
        Qt.QObject.__init__(self)
        TaurusBaseComponent.__init__(self,name)
        self.my_handler = f.printf
        
    def fireEvent(self, evt_src=None, evt_type=None, evt_value=None):
        if self._eventBufferPeriod:
            # If we have an active event buffer delay, store the event...
            with self._eventsBufferLock:
                self._bufferedEvents[(evt_src, evt_type)] =  (evt_src, evt_type, 
                                                              evt_value) 
        else:
            # if we are not buffering, directly emit the signal
            try: 
                self.getSignaller().emit(Qt.SIGNAL('taurusEvent'), evt_src, evt_type, evt_value)
            except: 
                self.error('%s.fireEvent(...) failed!'%type(self))
                self.error(f.getLastException())

    def setMyHandler(self,handler):
        self.my_handler = handler                
    @f.Catched
    def handleEvent(self,*args):
        #self.error('in handleEvent(%s,%s)'%(str(args[0]),len(args)))
        self.my_handler(*args)
        
class addCustomPanel2Gui(object):
    """
    this Class is used to add new panel to existing TaurusGUI with
    the same Context.
    Each extra_panel class should have a 'getPaneldescription' and
    getDefaultIcon methods.
    
    Pass a dictionary like this:
       EXTRA_PANELS['VaccaProperties'] = {
        'class': vacca.VaccaPropTable,
        'icon': ':/places/network-server.svg',
        }
    """

    def __init__(self, extra_panels= None):
        print '>>'*80
        print '>>'*80
        print '>>'*80

        exist_instance = False
        try:
            #find actual Taurusgui Instance
            
            app = Qt.QApplication.instance()
            assert app
        except:
            traceback.print_exc()
            return
        
        try:
            taurusgui = None
            widgets = app.allWidgets()
            for widget in widgets:
                widgetType = str(type(widget))
                if 'taurus.qt.qtgui.taurusgui.taurusgui.TaurusGui' in widgetType:
                    taurusgui = widget

            #Launch method
            def _launchPanel(panelName, panelClass, *args):
                #print args
                #print panelName, panelClass
                #print "Launch Panel"

                exist = False

                #find if exists instance with this Widget
                for widget in app.allWidgets():
                    widgetType = str(type(widget))
                    if str(panelClass) in widgetType:

                        #If exist set Flag to know it
                        exist = True
                        taurusgui.setFocusToPanel(panelName)
                        break

                if not exist:
                    try:
                        taurusgui.createCustomPanel(panelClass.getPanelDescription(panelName))
                    except:
                        taurusgui.createCustomPanel(PanelDescription(panelName,panelClass.__module__+'.'+panelClass.__name__))

            def launchPanel(panelName, panelClass):
                return lambda args: _launchPanel(panelName, panelClass, args)

            for panel in extra_panels.keys():
                class_Panel = extra_panels[panel]['class']
                try:
                    icon = extra_panels[panel].get('icon',None) or class_Panel.getDefaultIcon()
                except Exception,e:
                    print('Icon exception in addCustomPanel2Gui: %s'%traceback.format_exc())
                    icon = ':/places/network-server.svg'
                final_icon_url = icon if fandango.matchCl('^[\:/]',icon) else wdir('vacca/'+icon)
                #button = TaurusLauncherButton(
                #    widget=class_Panel.getPanelDescription(panel))
                #taurusgui.jorgsBar.addWidget(button)
                action = Qt.QAction(Qt.QIcon(final_icon_url),
                    panel, taurusgui)
                #func = launchPanel(panel, class_Panel)
                func = lambda args,panelName=panel,panelClass=class_Panel: \
                    _launchPanel(panelName,panelClass, args)
                Qt.QObject.connect(action, Qt.SIGNAL("triggered(bool)"), func)
                print "%s Added in jorgsBar"%(panel)
                taurusgui.jorgsBar.addAction(action)
        except:
            traceback.print_exc()

from .doc import get_autodoc
__doc__ = get_autodoc(__name__,vars())
