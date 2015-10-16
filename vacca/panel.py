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


import re,os,traceback,time,sys
import fandango,vacca
import fandango.functional as fun
from PyQt4 import Qt,Qwt5

from vacca.utils import wdir,get_White_palette,get_fullWhite_palette,get_halfWhite_palette
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

import taurus
import taurus.qt
from taurus.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget as WIDGET_CLASS
from taurus.qt.qtgui.panel import TaurusForm as FORM_CLASS
from taurus.qt.qtgui.panel.taurusdevicepanel import TaurusDevicePanel,get_regexp_dict,searchCl,matchCl,str_to_filter,get_White_palette,get_eqtype
import taurus.qt.qtgui.resource
from taurus.core import TaurusAttribute,TaurusDevice,TaurusDatabase
from taurus.qt.qtgui.container import TaurusWidget

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

###############################################################################
# Variables that control VaccaPanel attributes

## -> Moved to filters.py!

#DEV_ATTRS = fandango.dicts.CaselessDict({ #Put attribute names in lower case!
    #'ALARMS' : ['ActiveAlarms', 'PastAlarms', 'AlarmList', 'AlarmReceivers'],
    #'COMPOSER' : 'Q1,Q2,Q3,Q4,IPNames,CCGNames,.*Pressure.*'.split(','),
    #'ALL' : '.*Pressure.*,Average.*,DevStates,Thermocouples'.split(','),
    #'VGCT': ['ChannelState']+['p%d'%(i+1) for i in range(5)],
    ##'IPCT': [
                ##'hv1code','hv2code',
                ##'p1','p2','modelocal',
                ##'v1','v2','modestep',
                ##'i1','i2','modeprotect',
                ##'interlock',
                ###'hv1code','p1','i1','v1','hv2code','p2','i2','v2',
                ##'errorstatus','ionpump.*'],
    #'IPCT': [
                #('Attributes',['hv1code','p1','hv2code','p2']),
                #('CH1',['p1','v1','i1']),
                #('CH2',['p2','v2','i2']),
                ##'p1','p2','modelocal',
                ##'v1','v2','modestep',
                ##'i1','i2','modeprotect',
                ##'interlock',
                ###'hv1code','p1','i1','v1','hv2code','p2','i2','v2',
                ##'errorstatus','ionpump.*'],
            #],
    #'SPBX': ['totalcurrent','cableinterlocks','pressureinterlocks'] + 
            #reduce(list.__add__,(['p%d'%i] for i in range(1,1+8))) +
            #reduce(list.__add__,(['i%d'%i] for i in range(1,1+8))) +
            #['channelvoltages','ionpumpsconfig'] +
            #['interlockthresholds','warningthresholds'],
            ##reduce(list.__add__,(['p%d'%i,'i%d'%i] for i in range(1,1+8))),
    #'PNV': ['state','PLCAttribute'],
    #'SPNV': ['state'],
    #'EPS': ['CpuStatus','PLC_Config_Status','RGA_.*','THERMOCOUPLES','.*_T[0-9]+$','.*TC.*',], #These lines are overriden by blXX.rc.py files
    #'EPS-PLC': ['CpuStatus','PLC_Config_Status','RGA_.*','THERMOCOUPLES','.*_T[0-9]+$','.*TC.*',], #These lines are overriden by blXX.rc.py files
    ##'.*TC.*','.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_'],
    ##'EPS-PLC': ['CPU_STATUS','PLC_CONFIG_STATUS','THERMOCOUPLES'],
    #'CCG': ['pressure','channelstatus','controller'],
    #'PIR': ['pressure','channelstatus','controller'],
    #'IP': ['pressure','channelstatus','controller'],
    #})

#DEV_COMMS = fandango.dicts.CaselessDict({ #Put commands names in lower case!
    #'ALARMS': (('ResetAlarm',()),('ResetAll',())),
    #'VGCT': (('cc_on',('P1','P2')),  ('cc_off',('P1','P2')), ('sendcommand',())),
    #'IPCT': (('setmode',('SERIAL','LOCAL','STEP','FIXED','START','PROTECT')), 
                #('onhv1',()), ('offhv1',()), ('onhv2',()), ('offhv2',()), 
               #('sendcommand',())),
    #'SPBX': (
        #('GetAlarms',()),
        #('ResetAlarms',()),
        #('talk',()),
        #),
    #'PNV': (('open',()),('close',())),
    #'SPNV': (('open',()),('close',())),
    #'EPS': (),
    #'EPS-PLC': (),
    #'SERIAL': (('init',()),),
    #'CCG': (('on',()),('off',())),
    #'PIR': (),
    #'IP': (),    
    #})

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
            
class VaccaPanel(fandango.qt.Dropable(taurus.qt.qtgui.panel.TaurusDevicePanel)):
    
    def __init__(self,parent=None,model=None,palette=None,bound=True,filters=[]):
        
        self.call__init__(taurus.qt.qtgui.panel.TaurusDevicePanel, parent, model)
        taurus.qt.qtgui.panel.TaurusDevicePanel(self) #,parent,model,palette,bound)
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
        
    def setModel(self,model,pixmap=None):    
        try:    
          model,modelclass,raw = str(model).strip(),'',model
          model = fandango.tango.parse_tango_model(str(model))['device']
          self.warning('VaccaPanel(%s).setModel(%s,%s)'%(id(self),model,pixmap))
          if model: 
            model = model and model.split()[0] or ''
            modelclass = taurus.Factory().findObjectClass(model)
          self.warning('In TaurusDevicePanel.setModel(%s(%s),%s)'%(raw,modelclass,pixmap))
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
        print('panel 2 ........................')
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
                qpixmap = taurus.qt.qtgui.resource.getPixmap(':/logo.png')
            
            self._image.setPixmap(qpixmap)
            self._state.setModel(model+'/state')
            if hasattr(self,'_statelabel'): self._statelabel.setModel(model+'/state')
            self._status.setModel(model+'/status')
            try:
                self._attrsframe.clear()
                filters = get_regexp_dict(TaurusDevicePanel._attribute_filter,model,['.*'])
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

    @staticmethod
    def getDefaultIcon():
        path = 'image/widgets/DevicePanel.png'
        return path

    @staticmethod
    def getPanelDescription(name='VaccaDevicePanel',model=''):
        return PanelDescription(name,'vacca.panel.VaccaPanel',model)

        
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
        form = VaccaPanel(palette=get_fullWhite_palette(),filters=filters)
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
