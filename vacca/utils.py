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
    relative to VACCA_DIR.
    
    e.g. /homelocal/sicilia/applications/vacca/tbl2401.py
    
VACCA_DIR: *wdir('path/to/icon')* 

    The folder were VACCA should be executed, all paths within 
    the application will be relative to it. It includes all custom icons 
    that are not part of the vacca package.

    If VACCA_CONFIG is defined, it defaults to the path to config file.
    At ALBA installations it defaults to the path of vaccagui library.    
    Extra modules or plugins to be imported will be loaded from this directory.
    
    e.g. /homelocal/sicilia/applications/vacca/
    
VACCA_PATH: *vpath('path/to/icon')*

    Not mandatory, it defaults to the path of vacca library.
    Used for launchers and default icons of vacca widgets.

    e.g. /homelocal/sicilia/lib/python/site-packages/vacca

"""

from taurus.external.qt import Qt, Qwt5
import os,sys,traceback,imp,time,re
import fandango
from fandango import printf,get_database,first,\
    isString,isRegexp,clmatch
from fandango.dicts import SortedDict

try:
  from taurus.core import TaurusDatabase as TaurusAuthority
  print('Using Taurus <=3')
except:
  from taurus.core import TaurusAuthority
  print('Using Taurus >=4')

from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.core.util.eventfilters import ONLY_CHANGE_AND_PERIODIC
from taurus.qt.qtgui.taurusgui.utils import PanelDescription
from taurus.qt.qtgui.taurusgui import TaurusGui

###############################################################################

DB_HOST = fandango.tango.get_tango_host().split(':')[0]

def get_env_variable(var,default=''):
    """ It will try to get value from OS, then Tango.VACCA, then default """
    v = os.environ.get(var,None)
    if v: return v
    try:
      v = fandango.get_database().get_property('VACCA',var)[var]
      v =  v[0] if v and len(v) == 1 else v
      if v: return v
    except:
      traceback.print_exc()
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
   
def get_vacca_property(prop,extract=False):
    #print('get_vacca_property(%s)'%prop)
    db = fandango.get_database()
    props = db.get_property('VACCA',prop)
    if prop in props:
        v = props[prop]
        if fandango.isSequence(v): v = list(v)
        else: v = [v]
        if not any(v): return []
        for i,vv in enumerate(v):
          v[i] = vv = replace_env(vv,'VACCA_PATH')
          v[i] = vv = replace_env(vv,'VACCA_DIR')
        if extract and len(v)==1:
            v = v[0]
        return v
    return [] if not extract else ''

def replace_env(text,var=('VACCA_DIR','VACCA_PATH'),value=None):
    """
    Replaces each occurrence of $ENV_VARIABLE by its value.
    Var names can be a sequence.
    """
    if not fandango.isString(text):
      return text
    elif fandango.isSequence(var):
      return reduce(replace_env,[text]+list(var))
    else:
      if value is None: value = os.getenv(var)
      e = '[$][(]?'+var+'[)]?(?![a-zA-Z_0-9])'
      return re.sub(e,str(value),text)
  
###############################################################################

global VACCA_PATH
VACCA_PATH = get_env_variable('VACCA_PATH', imp.find_module('vacca')[1])
"""
VACCA_PATH: *vpath('path/to/icon')*

    Path to the VACCA library parent folder, tipically used for icons of vacca package
    Note, vpath(folder) will append /vacca to VACCA_PATH, to get internal vacca files.

    e.g. VACCA_PATH = /homelocal/sicilia/lib/python/site-packages
    e.g. vpath = /homelocal/sicilia/lib/python/site-packages/vacca
"""

os.environ['VACCA_PATH'] = VACCA_PATH
if VACCA_PATH+'/ini' not in sys.path:
  sys.path.append(VACCA_PATH+'/ini')

global VACCA_DIR
VACCA_DIR = get_env_variable('VACCA_DIR', get_env_variable('WORKING_DIR',''))
VACCA_DIR = replace_env(VACCA_DIR,'VACCA_PATH',VACCA_PATH) or VACCA_PATH
"""
VACCA_DIR: *wdir('path/to/icon')* 

    The folder were VACCA should be executed, all paths within 
    the application will be relative to it. It includes all custom icons 
    that are not part of the vacca package.
    
    Extra modules or plugins to be imported will be loaded from this directory.
    
    e.g. /homelocal/sicilia/applications/vacca/
"""

#Needed for backwards compatibility
#VACCA_DIR NOT FORCED HERE TO ALLOW OVERRIDE BY VACCA_CONFIG
WORKING_DIR = VACCA_DIR
DEFAULT_PATH =  WORKING_DIR

global VACCA_CONFIG
VACCA_CONFIG = get_env_variable('VACCA_CONFIG',DB_HOST+'.py')
VACCA_CONFIG = replace_env(replace_env(VACCA_CONFIG,'VACCA_DIR',VACCA_DIR),
                           'VACCA_PATH',VACCA_PATH)
VACCA_CONFIG = VACCA_CONFIG if os.path.isfile(VACCA_CONFIG) else VACCA_PATH+'/default.py'
"""
VACCA_CONFIG: 

    The config file to be loaded, it can be absolute path or 
    relative to WORKING_DIR. *get_config_file()* will import it and 
    return the content as a python module.
    
    e.g. /homelocal/sicilia/applications/vacca/tbl2401.py
"""
  
###############################################################################

def _joiner(a,s,b):
    return '%s%s%s'%(a or '',s if a and b and s not in (a[-1],b[0]) else '',b or '')

def wdir(s=''):
    #It tries to convert all paths to absolute
    global VACCA_DIR
    d = VACCA_DIR = os.getenv('VACCA_DIR')
    if not d and not os.path.exists(s): 
        d = os.path.dirname(VACCA_CONFIG)
    d = _joiner(d,'/',s)
    return d

def vpath(s=''):
    #It tries to convert all paths to absolute
    global VACCA_PATH
    VACCA_PATH = os.getenv('VACCA_PATH')
    s2 = _joiner(VACCA_PATH,'/',s)
    return s2
  
def expand_device_list(expressions):
    """
    Expands a list of regular expressions into a list of devices
    
    It adds 2 new reserverd characters:
     - ! , at the beginning of the expression is a negative lookup
     - ? , at the beginning of the expression, matches only exported devices
    """
    devices,ins,outs = [],set(),set()
    if isString(expressions):
      expressions = (','.join(expressions.split())).split(',')
    [(ins,outs)['!' in s].add(s.strip().lower()) 
            for s in expressions if s.strip()]

    for s in ins:
      try:
        if isRegexp(s):
          ds = fandango.get_matching_devices(s.strip('?'),
                exported='?' in s)
          devices.extend(d for d in ds 
                if not clmatch('*dserver/*/*',d))
        else:
          devices.append(s)

      except Exception,e:
        print(e,traceback.format_exc())
        
    #print('expand_device_list(%s): %s'%(
        #expressions,str(devices)[:80]))
    
    for o in outs:       
      try:
        n = len(devices)
        devices = [d for d in devices 
            if not fandango.matchCl(o.strip('!'),d)]
      except:
        print(e,traceback.format_exc())
        
    #print('expand_device_list(%s): %s'%(expressions,len(devices)))
    return sorted(devices)
  
###############################################################################
  
global VACCA_PROFILES
VACCA_PROFILES=[]
"""
VACCA_PROFILES: 

    Sets of environment variables declared as free properties
    in the Tango Database.
    
"""

def create_config_properties():
    global VACCA_PATH
    configs = ['DEFAULT']
    get_database().put_property('VACCA',{
        'VaccaConfigs':configs})
    get_database().put_property('VACCA',{
        'DEFAULT':['VACCA_CONFIG='+VACCA_PATH+'/default.py']})
    print('Created default VACCA properties')
    return get_config_properties()    

def load_config_properties(config,export=True):
    """
    It will load env variables from VACCA.$config property
    
    NOT USED!?
    """
    print('In load_config_properties(%s)'%config)
    props = get_vacca_property(config)
    props = [l.split('#')[0].strip() for l in props]
    props = dict(l.split('=',1) for l in props if l)
    if export:
        global VACCA_CONFIG,VACCA_DIR,VACCA_PATH

        if not VACCA_DIR and 'VACCA_DIR' in props:
            VACCA_DIR=props['VACCA_DIR']

        if not VACCA_PATH and 'VACCA_PATH' in props:
            VACCA_CONFIG=props['VACCA_PATH']            

        if not VACCA_CONFIG and 'VACCA_CONFIG' in props:
            
            l=props['VACCA_CONFIG']
            for p in ('VACCA_DIR','VACCA_PATH'):
                l=replace_env(l,p,globals()[p])
            VACCA_CONFIG = props['VACCA_CONFIG'] = l
            
        if not VACCA_DIR and '/' in VACCA_CONFIG:
            VACCA_DIR=os.path.dirname(VACCA_CONFIG)
    print(props)
    return props
  
def get_config_properties(config=''):
    """
    This method will get the list of VACCA free properties.
    If a config is passed, it will parse its contents as a dictionary.
    A new declaration of VACCA_CONFIG will be parsed as CONFIG_FILE instead.
    """
    #print('vacca.utils.get_config_properties(%s)'%config)
    global VACCA_PROFILES
    if not VACCA_PROFILES:
        VACCA_PROFILES = SortedDict()
        for k in get_vacca_property('VaccaConfigs',False):
          VACCA_PROFILES[k] = {}
    if not config:
        r = VACCA_PROFILES
    else:
        if not VACCA_PROFILES.get(config):
          VACCA_PROFILES[config] = [l.split('#')[0].strip() \
            for l in get_vacca_property(config,False)]
        config = VACCA_PROFILES[config]
        r = dict(l.split('=',1) for l in config if l)
        if 'VACCA_CONFIG' in r and 'CONFIG_FILE' not in r:
          r['CONFIG_FILE'] = r.pop('VACCA_CONFIG')
    return r

def get_config_file(config=None):
    """
    This method parses properties and returns the value of CONFIG_FILE.
    If undefined, VACCA_CONFIG is returned as fallback.
    """
    global VACCA_CONFIG,VACCA_DIR
    print('-')*80
    if not config:
        VACCA_CONFIG = get_env_variable('VACCA_CONFIG',DB_HOST)
        configs = get_config_properties()
        if VACCA_CONFIG in configs:
          CONFIG_FILE = get_config_properties(VACCA_CONFIG).get('CONFIG_FILE',VACCA_CONFIG)
        else:
          CONFIG_FILE = VACCA_CONFIG
        #CONFIG_FILE = CONFIG_FILE.replace('$VACCA_DIR',VACCA_DIR or '').replace('$VACCA_PATH',VACCA_PATH or '')
        CONFIG_FILE = replace_env(CONFIG_FILE,'VACCA_DIR',VACCA_DIR or '')
        CONFIG_FILE = replace_env(CONFIG_FILE,'VACCA_PATH',VACCA_PATH or '')
    else:
        CONFIG_FILE = config
    print('In get_config_file(%s)'%CONFIG_FILE)

    if not CONFIG_FILE.startswith('/'):
      if not os.path.isfile(CONFIG_FILE):
        cf = os.path.abspath(CONFIG_FILE)
        CONFIG_FILE = cf if os.path.isfile(cf) else wdir(CONFIG_FILE)
    print CONFIG_FILE
    
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
    print('Out of get_config_file(...)\n')
    return CONFIG
  
###############################################################################
# Miscellaneous methods to be used with Taurus GUI
  
def get_os_launcher(cmd,args=[]):
    """
    Returns a Linux launcher method for "cmd".
    @TODO: Study Taurus.ExternalApp and use the same methods used there.
    """
    import os
    cmd += ' '.join(args)
    if '&' not in cmd: cmd+='&'
    f = (lambda : os.system(cmd))
    return f
  
def get_main_window(app=None):
    app = app or Qt.QApplication.instance()
    main = fandango.first((a for a in app.allWidgets() 
                           if isinstance(a,Qt.QMainWindow)),default=None)
    if not main:
        print('No QMainWindow instance found!?!?')
    return main

def get_taurus_gui(app=None):
    try:
        #find actual Taurusgui Instance
        app = app or Qt.QApplication.instance()
        assert app
    except:
        traceback.print_exc()
        return
    
    try:
        taurusgui = None
        widgets = app.allWidgets()
        for widget in widgets:
            if isinstance(widget, TaurusGui):
                taurusgui = widget  
        return taurusgui
    except:
        traceback.print_exc()
        return

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
      
def add_menu(menuname,actions):
    '''
    The arguments must be a list of tuples with action names and action methods.
    
    e.g.:
    EXTRA_MENUS = [
    ('Tools',[
        ('LTB Gui',lambda:os.system('vacca_LTB &'),None),
        ('Jive',lambda:os.system('jive &'),None),
        ('Astor',lambda:os.system('astor &'),None),
        ('EPS Gui',lambda:os.system('alba_EPS &'),None),
        ('Valves',lambda:valves.ValvesChooser().show(),None),
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None),
        ]),
    '''
    self = get_main_window()
    if not self:
        print('ERROR: Unable to add %s menu, QMainWindow not found'%menuname)
        return
        
    print('Adding new menu %s'%menuname)
    MenuBar = self.menuBar()
    newmenu = Qt.QMenu(MenuBar)
    newmenu.setTitle(menuname)
    newmenu.setObjectName(menuname)
    newaction = Qt.QAction(MenuBar)
    for name,method,mnemonic in actions:
        act = Qt.QAction(newmenu)
        act.setObjectName(name)
        act.setText(name)
        newmenu.addAction(act)
        Qt.QObject.connect(act,Qt.SIGNAL("triggered()"),method)            

    #self.MenuBar.addAction(newmenu.menuAction())
    MenuBar.insertMenu(newaction,newmenu)
    return

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
        
def YesNoDialog(title,message):
    v = Qt.QMessageBox.warning(None,title,message, \
    Qt.QMessageBox.Yes|Qt.QMessageBox.No);
    return v == Qt.QMessageBox.Yes


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
                if isinstance(widget, TaurusGui):
                    taurusgui = widget
            #taurusgui = get_taurus_gui() #get_main_window() does not work here!?
            
            assert taurusgui, 'TaurusGui instance not found!?'

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
              action = None
              try:
                d = extra_panels[panel]
                class_Panel = d.get('class',d.get('classname'))
                print panel,class_Panel,d
                try:
                    icon = extra_panels[panel].get('icon',None) or class_Panel.getDefaultIcon()
                except Exception,e:
                    print('Icon exception in addCustomPanel2Gui(%s)!! %s'%(panel,e))
                    icon = ':/places/network-server.svg'
                final_icon_url = icon if fandango.matchCl('^[\:/]',icon) else wdir('vacca/'+icon)

                #button = TaurusLauncherButton(
                #    widget=class_Panel.getPanelDescription(panel))
                #taurusgui.jorgsBar.addWidget(button)
                FUNCTION_TYPE = type(launchPanel)
                METHOD_TYPE = type(MyTaurusComponent.fireEvent)
                
                if 'VaccaAction' in str(class_Panel):
                    import vacca.panel
                    action = vacca.panel.VaccaAction(parent=taurusgui)
                else:
                    action = Qt.QAction(Qt.QIcon(final_icon_url),
                        panel, taurusgui)
                    if d.get('name'): action.setText(d['name'])
                    
                if isinstance(action,Qt.QAction):
                    #func = launchPanel(panel, class_Panel)
                    if isinstance(class_Panel,(FUNCTION_TYPE,METHOD_TYPE)):
                        func = class_Panel
                    else:
                        func = lambda args,panelName=panel,panelClass=class_Panel: \
                            _launchPanel(panelName,panelClass, args)
                    Qt.QObject.connect(action, Qt.SIGNAL("triggered(bool)"), func)
                    taurusgui.jorgsBar.addAction(action)
                else:
                    if d.get('model'): action.setModel(d['model'])
                    taurusgui.jorgsBar.addWidget(action)

                print "%s Added in jorgsBar"%(panel)
              except:
                print('Error creating %s: %s,%s'%(panel,extra_panels[panel],action))
                traceback.print_exc()
        except:
            traceback.print_exc()

from .doc import get_autodoc
__doc__ = get_autodoc(__name__,vars())
