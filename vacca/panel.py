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

__doc__ = """Custom widgets for panels, forms and buttons in Vacca"""

import re,os,traceback,time,sys
import fandango,vacca
import fandango.functional as fun

from vacca.utils import *
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

import taurus
import taurus.qt
from taurus.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget as WIDGET_CLASS
from taurus.qt.qtgui.panel import TaurusForm as FORM_CLASS
from taurus.qt.qtgui.panel.taurusdevicepanel import TaurusDevicePanel,get_regexp_dict,searchCl,matchCl,str_to_filter,get_White_palette,get_eqtype
from taurus.qt.qtgui.resource import getPixmap
from taurus.core import TaurusAttribute,TaurusDevice,TaurusDatabase
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.panel.taurusform import TaurusCommandsForm

###############################################################################
# Help Methods
def init_qt():
    return Qt.QApplication([])
            
def get_dev_attrs(dev):
    default = ['state','status']    
    #: DEV_ATTRS definition
    #: The lists of attributes to visualize for each vacuum device class    
    #attrs = taurus.Device(dev).get_attribute_list()
    for k,v in DEV_ATTRS.items():
        if re.match(k,dev.lower()): 
            return default+v
    return default
    
def get_eqtype(dev):
    ''' It extracts the eqtype from a device name like domain/family/eqtype-serial'''
    try: eq = str(dev).split('/')[-1].split('-',1)[0].upper()
    except: eq = ''
    return eq

###############################################################################
# Variables that control VaccaPanel shape
STATUS_HEIGHT=170
SPLIT_SIZES=[] #[15,50,35]

#APP_FOLDER = '/homelocal/sicilia/applications/vacca/'
EQUIP_IMAGE=wdir('image/equips/icon-%s.gif')
IMAGE_SIZE=(200,100) #(width,height)

class VaccaSplash(Qt.QSplashScreen, fandango.Singleton):

    def __init__(self, timeout=10000):
        self._pixmap = Qt.QPixmap(wdir('image/icons/alba-entry.JPG'))
        Qt.QSplashScreen.__init__(self, self._pixmap)
        self.showMessage('initializing application...')
        self._timer = Qt.QTimer.singleShot(timeout, self.close)
        self.show()

class DomainButton(Qt.QToolButton):

    def __init__(self, parent=None):
        #self.call__init__wo_kw(Qt.QToolButton, parent)
        Qt.QToolButton.__init__(self, parent)
        self.setLayout(Qt.QVBoxLayout())

        from taurus.qt.qtgui.display import TaurusLed
        self._led = TaurusLed()
        self._label = Qt.QLabel()
        self.layout().addWidget(self._led)
        self.layout().addWidget(self._label)
        self.layout().setAlignment(Qt.Qt.AlignCenter)

    def setLabel(self, txt):
        self._label.setText(txt)

    def setModel(self, model, action):
        #print 'DomainButton.setModel(%s,%s)'%(model,action)
        self._model = model
        self._led.setModel(model)
        if not self._label.text(): self.setLabel(model.split('/')[0])
        self._cmd = action#action.split()
        self._action = taurus.qt.qtgui.util.ExternalAppAction(cmdargs=self._cmd)
        self.connect(self, Qt.SIGNAL("pressed()"), self.show)
        #_action.actionTriggered)

    def show(self, args=None):
        #print('VaccaAction(%s).show(%s,%s)'%(self._default_cmd,self._cmdargs,args))
        print 'Launching %s'%self._cmd
        self._action.actionTriggered(args)


class VaccaAction(Qt.QToolButton,taurus.qt.qtgui.base.TaurusBaseWidget):

    def __init__(self, parent=None, designMode=False, default=None):
        #print('VaccaAction()')
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QToolButton, parent)
        self.call__init__(taurus.qt.qtgui.base.TaurusBaseWidget, name,
                          designMode=designMode)
        self._text, self._icon, self._cmdargs, self._action = '', '', [], None
        self._default_cmd = default.split() if default is not None else []
        
    def setCommand(self, cmd):
        if not fandango.isSequence(cmd):
            cmd = fandango.toList(cmd)
        self._default_cmd = cmd

    def setModel(self, model):
        self.info('VaccaAction(%s).setModel(%s)' % (self._default_cmd, model))
        model = fandango.toSequence(model)
        if len(model) > 1:
            self._text = model[0]
        if len(model) > 2:
            self._icon = model[1]
        self._cmdargs = model[2 if len(model) > 2 else 1 if len(model) > 1 else
        0:]
        self._action = taurus.qt.qtgui.util.ExternalAppAction(
            cmdargs=self._default_cmd+self._cmdargs,
            text=self._text,
            icon=self._icon
        )

        #self._action = ExternalApp(cmdargs=['mambo'], text="ArchivingViewer", icon=WDIR+'image/icons/Mambo-icon.png')
        self.setDefaultAction(self._action)
        self.setText(self._text)
        self.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)

    def show(self, args=None):
        #print('VaccaAction(%s).show(%s,%s)'%(self._default_cmd,self._cmdargs,args))
        self._action.actionTriggered(args)

    def kill(self):
        if self._action:
            self._action.kill()
            
try:
  import MySQLdb
  from PyTangoArchiving.widget.ArchivingBrowser import ArchivingBrowser
  BROWSER = ArchivingBrowser
except:
  print('Failed to load PyTangoArchiving!')
  BROWSER = Qt.QWidget
  
class VaccaFinder(BROWSER):
  """
  Convenience class to deal with alternatives to ArchivingBrowser when not available in the PYTHONPATH
  """
  def __init__(self,parent=None,domains=None,regexp='*pnv-*',USE_SCROLL=True,USE_TREND=False):
        print 'In DomainChooser(), loading thermocouples from Tango'
        if BROWSER is Qt.QWidget:
            Qt.QWidget.__init__(self,parent)
        else:
            BROWSER.__init__(self,parent,domains,regexp,USE_SCROLL,USE_TREND)
  pass


class SimplePanel(WIDGET_CLASS):

    def getInnerPanel(self):
        return getattr(self, 'innerPanel', None)
        
    def setModel(self, model):
        if not hasattr(self, '_layout'):
            self._layout = Qt.QVBoxLayout()
            self.setLayout(self._layout)
            
        print('In SimplePanel.setModel(%s)' % model)
        prev = self.getInnerPanel()
        print('previous was %s,%s' % (prev, prev and prev.getModel()))
        old = prev and prev.getModel()
        if prev:
            try:
                print('\t dettaching %s' % old)
                self._layout.removeWidget(prev)
                #prev.setModel(None)
            except:
                traceback.print_exc()
        self.innerPanel = TaurusDevicePanel()
        self.innerPanel.setModel(model)
        self._layout.addWidget(self.innerPanel)
        
    def getModel(self):
        i = self.getInnerPanel()
        return i.getModel() if i else None

class VaccaDocker(Qt.QMainWindow):
    
    def __init__(self,*args):
        Qt.QMainWindow(self,*args)
        self.setDockNestingEnabled(True)
        
    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        path = 'image/widgets/DevicePanel.png'
        return path

    @staticmethod
    def getPanelDescription(name='VaccaDocker',model=''):
        """
        :param name: Name for the Panel
        :param model: Model for the panel
        :return:
        """
        return PanelDescription(name,'vacca.panel.VaccaDocker')
        
class VaccaPanel(fandango.qt.Dropable(taurus.qt.qtgui.panel.TaurusDevicePanel)):
    """

    :param parent:
    :param model: a device name or an state attribute
    :param palette:
    :param bound:
    :param filters:
    :return:

    It is a class that inherits from TaurusDevicePanel and Dropable module from fandango.

    In Init, the class VaccaPanel check if exist any shareDataManager to
        subscribe in it.

    This Widget shows the device Commands and Attributes, it is listening the shareDataManager to show the device selected information.

    The title of this Widget can be draggable.

    This class has the follow functionalities:

        * Title is draggable.
        * Is connected to shareDataManager to share information in the GUI.

    """
    
    def __init__(self,parent=None,model=None, filters=[]): #,palette=None, bound=True,filters=[]):
        """
        In Init, the class VaccaPanel check if exist any shareDataManager to
        subscribe in it.

        :param parent:
        :param model: Model to start the Panel.
        :param filters: List of filters, by default is None
        :return:
        """
        
        self.call__init__(taurus.qt.qtgui.panel.TaurusDevicePanel, parent, model)
        sdm = vacca.utils.get_shared_data_manager()
        if sdm:
            sdm.connectReader('SelectedInstrument',self.setModel,
                              readOnConnect=True)

        if self.checkDropSupport():
            self.setSupportedMimeTypes([self.TAURUS_DEV_MIME_TYPE,
                                        self.TEXT_MIME_TYPE, self.TAURUS_MODEL_MIME_TYPE])
            self.setDropEventCallback(self.setModel)
        self._header.layout().removeWidget(self._label)
        #self._label = vacca.utils.DraggableLabel()
        self._label = fandango.qt.Draggable(Qt.QLabel)()
        self._label.font().setBold(True)
        self._header.layout().addWidget(self._label,0,1,Qt.Qt.AlignLeft)
        self._label.setDragEventCallback(self._label.text)
        self.setToolTip(getattr(self,'__help__',self.__doc__))
        
    @classmethod
    def getAttributeFilters(klass,dev_class=None):
        """
        TaurusDevicePanel filters are fixed to work by device name.
        But, if AttributeFilters is declared as class property, it will override them.
        
        get{Property}(klass,dev_class) will update it from Tango DB and return the matching values.
        set{Property}(dict) will update the parent TaurusDevicePanel dictionary, not the DB
        """
        if dev_class is not None and dev_class not in klass._attribute_filter:
            filters = get_class_property(dev_class,'AttributeFilters',extract=False)
            if filters:
                filters = dict((k,eval(v)) for k,v in (l.split(':',1) for l in filters))
                klass._attribute_filter[dev_class] = filters
                return {'.*':filters}
        #if dev_name is not None: 
            #filters = get_regexp_dict(klass._attribute_filter,dev_name,[])
            #if filters:
                #return {'.*':filters}
        return klass._attribute_filter
        
    @classmethod
    def getCommandFilters(klass,dev_class=None):
        """
        get{Property}(klass,dev_class) will update it from Tango DB and return the matching values.
        set{Property}(dict) will update the parent TaurusDevicePanel dictionary, not the DB
        """      
        if dev_class is not None and dev_class not in klass._attribute_filter:
            filters = get_class_property(dev_class,'CommandFilters',extract=False)
            if filters:
                filters = dict((k,eval(v)) for k,v in (l.split(':',1) for l in filters))
                klass._attribute_filter[dev_class] = filters
                return {'.*':filters}
        return klass._command_filter
      
    def setModel(self,model,pixmap=None):
        """
        Set Model is the callback used in shareDataManager to manage device
        selections.

        :param model: Model to VaccaPanel
        :param pixmap:
        :return:
        """
        try:    
          model,modelclass,raw = str(model).strip(),'',model
          model = fandango.tango.parse_tango_model(str(model))['device']
          self.info('VaccaPanel(%s).setModel(%s,%s)'%(id(self),model,pixmap))
          if model: 
            model = model and model.split()[0] or ''
            modelclass = taurus.Factory().findObjectClass(model)
          self.debug('In TaurusDevicePanel.setModel(%s(%s),%s)'%(raw,modelclass,pixmap))
          if model == self.getModel():
            return
          elif raw is None or not model or not modelclass: 
            if self.getModel(): self.detach()
            return
          elif issubclass(modelclass, TaurusAttribute):
            #if model.lower().endswith('/state'): 
            model = model.rsplit('/',1)[0]
          elif not issubclass(modelclass, TaurusDevice):
            self.warning('TaurusDevicePanel accepts only Device models')
            return
        except:
          traceback.print_exc()
          
        try:
            taurus.Device(model).ping()
            if self.getModel(): self.detach() #Do not dettach previous model before pinging the new one (fail message will be shown at except: clause)
            TaurusWidget.setModel(self,model)
            self.setWindowTitle(str(model).upper())
            model = self.getModel()
            self._label.setText(model.upper())
            font = self._label.font()
            font.setPointSize(15)
            self._label.setFont(font)
            if pixmap is None and self.getIconMap():
                for k,v in self.getIconMap().items():
                    if searchCl(k,model):
                        pixmap = v                  
            if pixmap is not None:
                #print 'Pixmap is %s'%pixmap
                qpixmap = Qt.QPixmap(pixmap)
                if qpixmap.height()>.9*IMAGE_SIZE[1]: qpixmap=qpixmap.scaledToHeight(.9*IMAGE_SIZE[1])
                if qpixmap.width()>.9*IMAGE_SIZE[0]: qpixmap=qpixmap.scaledToWidth(.9*IMAGE_SIZE[0])
            else:
                qpixmap = getPixmap(':/logo.png')
            
            self._image.setPixmap(qpixmap)
            self._state.setModel(model+'/state')
            if hasattr(self,'_statelabel'): self._statelabel.setModel(model+'/state')
            self._status.setModel(model+'/status')
            try:
                self._attrsframe.clear()
                dev_class = fandango.get_device_info(model).dev_class
                filters = type(self).getAttributeFilters(dev_class=dev_class)
                #filters = get_class_property(dev_class,'AttributeFilters',extract=False)
                #if filters:
                    #filters = dict((k,eval(v)) for k,v in (l.split(':',1) for l in filters))
                #else:
                filters = get_regexp_dict(self._attribute_filter,model,['.*'])
                if hasattr(filters,'keys'): filters = filters.items() #Dictionary!
                if filters and isinstance(filters[0],(list,tuple)): #Mapping
                    self._attrs = []
                    for tab,attrs in filters:
                        self._attrs.append(self.get_attrs_form(device=model,filters=attrs,parent=self))
                        self._attrsframe.addTab(self._attrs[-1],tab)
                else:
                    if self._attrs and isinstance(self._attrs,list): self._attrs = self._attrs[0]
                    self._attrs = self.get_attrs_form(device=model,form=self._attrs,filters=filters,parent=self)
                    if self._attrs: self._attrsframe.addTab(self._attrs,'Attributes')
                    
                if not TaurusDevicePanel.READ_ONLY:
                    self._comms = self.get_comms_form(model,self._comms,self)
                    if self._comms: self._attrsframe.addTab(self._comms,'Commands')
                if SPLIT_SIZES: self._splitter.setSizes(SPLIT_SIZES)
            except:
                self.warning( traceback.format_exc())
                qmsg = Qt.QMessageBox(Qt.QMessageBox.Critical,'%s Error'%model,'%s not available'%model,Qt.QMessageBox.Ok,self)
                qmsg.setDetailedText(traceback.format_exc())
                qmsg.show()
        except:
            self.warning(traceback.format_exc())
            qmsg = Qt.QMessageBox(Qt.QMessageBox.Critical,'%s Error'%model,'%s not available'%model,Qt.QMessageBox.Ok,self)
            qmsg.show()
        self.setWindowTitle(self.getModel())
        return
    
    def get_comms_form(self,device,form=None,parent=None):
        self.trace( 'In TaurusDevicePanel.get_comms_form(%s)'%device)
        dev_class = fandango.get_device_info(device).dev_class
        filters = type(self).getCommandFilters(dev_class)
        params = get_regexp_dict(filters,device,[])
        if filters and not params: #If filters are defined only listed devices will show commands
            self.debug('TaurusDevicePanel.get_comms_form(%s): By default an unknown device type will display no commands'% device)
            return None 
        if not form: 
            form = TaurusCommandsForm(parent)
        elif hasattr(form,'setModel'): 
            form.setModel('')
        try:
            form.setModel(device)
            if params: 
                form.setSortKey(lambda x,vals=[s[0].lower() for s in params]: vals.index(x.cmd_name.lower()) if str(x.cmd_name).lower() in vals else 100)
                form.setViewFilters([lambda c: str(c.cmd_name).lower() not in ('state','status') and any(searchCl(s[0],str(c.cmd_name)) for s in params)])
                form.setDefaultParameters(dict((k,v) for k,v in (params if not hasattr(params,'items') else params.items()) if v))
            for wid in form._cmdWidgets:
                if not hasattr(wid,'getCommand') or not hasattr(wid,'setDangerMessage'): continue
                if re.match('.*(on|off|init|open|close).*',str(wid.getCommand().lower())):
                    wid.setDangerMessage('This action may affect other systems!')
            #form._splitter.setStretchFactor(1,70)
            #form._splitter.setStretchFactor(0,30)
            form._splitter.setSizes([80,20])
        except Exception: 
            self.warning('Unable to setModel for TaurusDevicePanel.comms_form!!: %s'%traceback.format_exc())
        return form

    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        path = vpath('image/widgets/DevicePanel.png')
        return path

    @staticmethod
    def getPanelDescription(name='VaccaDevicePanel',model=''):
        """
        :param name: Name for the Panel
        :param model: Model for the panel
        :return:
        """
        return PanelDescription(name,classname='vacca.panel.VaccaPanel',model=model)

        
def configure_form(dev,form=None):
    """ Creates a TauForm and configures its Status fields 
    """
    if form is None:
        form = FORM_CLASS()
    elif hasattr(form, 'setModel'):
        form.setModel([])
    ##Configuring the TauForm:
    form.setWithButtons(False)
    form.setWindowTitle(dev)
    form.setModel('%s/%s' % (dev, a) for a in get_dev_attrs(dev))
    ##Adapting the status widget to show properly an status
    status = form.getItemByModel(dev+'/status') #A TauValue object (containing label and value widgets)
    sw = status.readWidget() #A TauStatusLabel object
    sw.setAlignment(Qt.Qt.AlignLeft)
    sw.setMinimumHeight(STATUS_HEIGHT)
    #sw.setShowQuality(False) #It didn't work as expected
    return form

if __name__ == '__main__':
    #!/usr/bin/python
    import sys,re,traceback,taurus
    taurus.setLogLevel(taurus.core.util.Logger.Debug)
    app = Qt.QApplication(sys.argv)
    assert len(sys.argv)>1, '\n\nUsage:\n\t> python widgets.py a/device/name [attr_regexp]'
    model = sys.argv[1]
    filters = fun.first(sys.argv[2:],'')
    form = None
    if re.match('[\w-]+/[\w-]+/[\w-]+.*',model):
        print 'loading a device panel'
        form = VaccaPanel(filters=filters)  #palette=get_fullWhite_palette()
        form.setModel(model)
    elif model.lower().endswith('.jdw'):
        print 'loading a synoptic'
        form = taurus.qt.qtgui.graphic.TauJDrawSynopticsView(designMode=False,
          updateMode=taurus.qt.qtgui.graphic.TauJDrawSynopticsView.NoViewportUpdate
          ) 
        #FullViewportUpdate, : AWFUL CPU USAGE!!!!!!!!
        #MinimalViewportUpdate, : Qt Defaults
        #SmartViewportUpdate, : ?
        #BoundingRectViewportUpdate, : ?
        #NoViewportUpdate : Tau defaults
        form.setModel(model)
        models = form.get_item_list()
        for m in models:
            m = str(m)
            if m.count('/')==2: m+='/state'
            period = 120000.
            try: 
                taurus.Attribute(m).changePollingPeriod(period)
            except: print '(%s).changePollingPeriod(%s): Failed: %s'%(m,period,traceback.format_exc())
    print 'showing ...'
    form.show()
    sys.exit(app.exec_())

__doc__ = vacca.get_autodoc(__name__,vars())