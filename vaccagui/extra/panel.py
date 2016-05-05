#!/usr/bin/python

import re,os,traceback,time,sys
import fandango
import fandango.functional as fun
from PyQt4 import Qt,Qwt5
from PySynopticTree import palettes

if '--use-tau' not in sys.argv:
    import taurus
    TAU=taurus
    from taurus.qt import Qt
    from taurus.qt.qtgui.container import TaurusWidget as WIDGET_CLASS
    from taurus.qt.qtgui.display import TaurusValueLabel as LABEL_CLASS
    from taurus.qt.qtgui.display import TaurusStateLed as LED_CLASS
    from taurus.qt.qtgui.panel import TaurusValue as VALUE_CLASS
    from taurus.qt.qtgui.panel import TaurusForm as FORM_CLASS
    from taurus.qt.qtgui.panel import TaurusCommandsForm as COMMAND_CLASS
    #from PySynopticTree.mytaurus.tauvalue import TauValue as COMMAND_CLASS
    #from PySynopticTree.mytaurus.forms import TauCommandsForm as COMMAND_CLASS
    #from PySynopticTree.mytaurus.forms import TauForm as FORM_CLASS
else:
    import tau
    TAU=tau
    from tau.widget import Qt
    from tau.widget import TauWidget as WIDGET_CLASS
    from tau.widget import TauValueLabel as LABEL_CLASS
    from tau.widget import TauValue as VALUE_CLASS
    from tau.widget.forms import TauForm as FORM_CLASS
    from tau.widget.forms import TauCommandsForm as COMMAND_CLASS
    from tau.widget import TauStateLed as LED_CLASS


###############################################################################
# Help Methods
def init_qt():
    return Qt.QApplication([])
            
def get_dev_attrs(dev):
    default = ['state','status']    
    #: DEV_ATTRS definition
    #: The lists of attributes to visualize for each vacuum device class    
    #attrs = tau.Device(dev).get_attribute_list()
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
from include import wdir
#APP_FOLDER = '/homelocal/sicilia/applications/vacca/'
EQUIP_IMAGE=wdir('image/equips/icon-%s.gif')
IMAGE_SIZE=(200,100) #(width,height)

###############################################################################
# Variables that control VaccaPanel attributes

DEV_ATTRS = fandango.dicts.CaselessDict({ #Put attribute names in lower case!
    'ALARMS' : ['ActiveAlarms', 'PastAlarms', 'AlarmList', 'AlarmReceivers'],
    'COMPOSER' : 'Q1,Q2,Q3,Q4,IPNames,CCGNames,.*Pressure.*'.split(','),
    'ALL' : '.*Pressure.*,Average.*,DevStates,Thermocouples'.split(','),
    'VGCT': ['ChannelState']+['p%d'%(i+1) for i in range(5)],
    'IPCT': [
                'hv1code','hv2code',
                'p1','p2','modelocal',
                'v1','v2','modestep',
                'i1','i2','modeprotect',
                'interlock',
                #'hv1code','p1','i1','v1','hv2code','p2','i2','v2',
                'errorstatus','ionpump.*'],
    'SPBX': ['totalcurrent','cableinterlocks','pressureinterlocks'] + 
            reduce(list.__add__,(['p%d'%i] for i in range(1,1+8))) +
            reduce(list.__add__,(['i%d'%i] for i in range(1,1+8))) +
            ['channelvoltages','ionpumpsconfig'] +
            ['interlockthresholds','warningthresholds'],
            #reduce(list.__add__,(['p%d'%i,'i%d'%i] for i in range(1,1+8))),
    'PNV': ['state','PLCAttribute'],
    'SPNV': ['state'],
    'EPS': ['CpuStatus','PLC_Config_Status','RGA_.*','THERMOCOUPLES','.*_T[0-9]+$','.*TC.*',], #These lines are overriden by blXX.rc.py files
    'EPS-PLC': ['CpuStatus','PLC_Config_Status','RGA_.*','THERMOCOUPLES','.*_T[0-9]+$','.*TC.*',], #These lines are overriden by blXX.rc.py files
    #'.*TC.*','.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_'],
    #'EPS-PLC': ['CPU_STATUS','PLC_CONFIG_STATUS','THERMOCOUPLES'],
    'CCG': ['pressure','channelstatus','controller'],
    'PIR': ['pressure','channelstatus','controller'],
    'IP': ['pressure','channelstatus','controller'],
    })

DEV_COMMS = fandango.dicts.CaselessDict({ #Put commands names in lower case!
    'ALARMS': (('ResetAlarm',()),('ResetAll',())),
    'VGCT': (('cc_on',('P1','P2')),  ('cc_off',('P1','P2')), ('sendcommand',())),
    'IPCT': (('setmode',('SERIAL','LOCAL','STEP','FIXED','START','PROTECT')), 
                ('onhv1',()), ('offhv1',()), ('onhv2',()), ('offhv2',()), 
               ('sendcommand',())),
    'SPBX': (
        ('GetAlarms',()),
        ('ResetAlarms',()),
        ('talk',()),
        ),
    'PNV': (('open',()),('close',())),
    'SPNV': (('open',()),('close',())),
    'EPS': (),
    'EPS-PLC': (),
    'SERIAL': (('init',()),),
    'CCG': (('on',()),('off',())),
    'PIR': (),
    'IP': (),    
    })


class VaccaPanel(WIDGET_CLASS):
    
    READ_ONLY = False
    
    def __init__(self,parent=None,model=None,palette=None,filters=None,bound=True):
        WIDGET_CLASS.__init__(self,parent)
        self.info('In VaccaPanel.__init__()')
        if palette: self.setPalette(palette)
        self.setLayout(Qt.QGridLayout())
        self.bound = bound
        self._filters = filters and (filters.split(',') if ',' in filters else [filters])
        self._dups = []
        self._label = Qt.QLabel()
        self._label.font().setBold(True)
        
        self._stateframe = WIDGET_CLASS(self)
        self._stateframe.setLayout(Qt.QGridLayout())
        self._stateframe.layout().addWidget(Qt.QLabel('State'),0,0,Qt.Qt.AlignCenter)
        self._statelabel = LABEL_CLASS(self._stateframe)
        self._statelabel.setMinimumWidth(100)        
        self._statelabel.setShowQuality(False)
        self._statelabel.setShowState(True)
        self._stateframe.layout().addWidget(self._statelabel,0,1,Qt.Qt.AlignCenter)
        self._state = LED_CLASS(self._stateframe)
        self._state.setShowQuality(False)
        self._stateframe.layout().addWidget(self._state,0,2,Qt.Qt.AlignCenter)        
        
        self._statusframe = Qt.QScrollArea(self)
        self._status = LABEL_CLASS(self._statusframe)
        self._status.setShowQuality(False)
        self._status.setAlignment(Qt.Qt.AlignLeft)
        self._status.setFixedHeight(2000)
        self._status.setFixedWidth(5000)
        #self._statusframe.setFixedHeight(STATUS_HEIGHT)
        self._statusframe.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOn)
        self._statusframe.setVerticalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOn)
        self._statusframe.setWidget(self._status)
        self._statusframe.setPalette(palettes.get_White_palette())
        
        self._attrsframe = Qt.QTabWidget(self)
        
        self._splitter = Qt.QSplitter(Qt.Qt.Vertical,self) ##Horizontal will not allow to show labels of attributes!
        self._splitter.setChildrenCollapsible(False)        
        
        self._attrs,self._comms = None,None
        
        self.layout().addWidget(self._splitter,0,0)
        self._header = Qt.QFrame()
        self._header.setFixedHeight(1.1*IMAGE_SIZE[1])
        self._header.setLayout(Qt.QGridLayout())
        
        #When bound; the image will be a push button allowing to duplicate the widget
        if self.bound:
            self._image = Qt.QPushButton()
            self.connect(self._image,Qt.SIGNAL("pressed()"),self.duplicate)
        else:
            self._image = Qt.QLabel()
        self._header.layout().addWidget(self._image,0,1,2,1,Qt.Qt.AlignCenter)
        self._header.layout().addWidget(self._label,0,0,Qt.Qt.AlignCenter)
        self._header.layout().addWidget(self._stateframe,1,0,Qt.Qt.AlignCenter)
        
        self._splitter.insertWidget(0,self._header)
        self._splitter.insertWidget(1,self._attrsframe)
        self._splitter.insertWidget(2,self._statusframe)
        self._splitter.setStretchFactor(0,15)
        self._splitter.setStretchFactor(1,65)
        self._splitter.setStretchFactor(2,20)
        
        if model: self.setModel(model)
        
    def duplicate(self):
        self._dups.append(VaccaPanel(bound=False))
        self._dups[-1].setModel(self.model)
        self._dups[-1].show()
    
    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self,model):
        self.info('In VaccaPanel.setModel(%s)'%model)
        if not model: return None
        model = str(model).split()[0].strip()
        print 'In VaccaPanel.setModel(%s)'%model
        if model == self.getModel():
          pass
        elif not fandango.device.check_device(model):
            qmsg = Qt.QMessageBox(Qt.QMessageBox.Critical,'%s Error'%model,'%s not available'%model,Qt.QMessageBox.Ok,self)
            qmsg.show()
        else:
            WIDGET_CLASS.setModel(self,model)
            self.setWindowTitle(str(model).upper())
            model = self.getModel()
            self.info('VaccaPanel.TauWidget model set to %s'%model)
            self._label.setText(model.upper())
            font = self._label.font()
            font.setPointSize(15)
            self._label.setFont(font)
            
            pixmap = EQUIP_IMAGE%get_eqtype(model).lower()
            #print 'Pixmap is %s'%pixmap
            qpixmap = Qt.QPixmap(pixmap)
            if qpixmap.height()>.9*IMAGE_SIZE[1]: qpixmap=qpixmap.scaledToHeight(.9*IMAGE_SIZE[1])
            if qpixmap.width()>.9*IMAGE_SIZE[0]: qpixmap=qpixmap.scaledToWidth(.9*IMAGE_SIZE[0])
            if self.bound:
                icon = Qt.QIcon(qpixmap)
                if not icon.isNull():
                    self._image.setIcon(icon)
                    self._image.setIconSize(Qt.QSize(*IMAGE_SIZE))
                    #self._image.setBaseSize(*IMAGE_SIZE)
                    #self._image.setMinimumHeight(.9*IMAGE_SIZE[1])
                else:
                    self._image.setText('Duplicate Panel')
            else:
                self._image.setPixmap(qpixmap)
            
            self._state.setModel(model+'/state')
            if hasattr(self,'_statelabel'): self._statelabel.setModel(model+'/state')
            self._status.setModel(model+'/status')
            try:
                self._attrsframe.clear()
                
                self._attrs = self.get_attrs_form(model,self._attrs,self)
                if self._attrs: self._attrsframe.addTab(self._attrs,'Attributes')               
                if not VaccaPanel.READ_ONLY:
                    self._comms = self.get_comms_form(model,self._comms,self)
                    if self._comms: self._attrsframe.addTab(self._comms,'Commands')
            except:
                print traceback.format_exc()
                qmsg = Qt.QMessageBox(Qt.QMessageBox.Critical,'%s Error'%model,'%s not available'%model,Qt.QMessageBox.Ok,self)
                qmsg.setDetailedText(traceback.format_exc())
                qmsg.show()
        if SPLIT_SIZES: self._splitter.setSizes(SPLIT_SIZES)
        return
        
    
    @staticmethod
    def get_attrs_form(device,form=None,parent=None):
        filters = parent._filters or DEV_ATTRS.get(get_eqtype(device),['.*'])
        print 'In VaccaPanel.get_attrs_form(%s,%s)'%(device,filters)
        all = sorted(str(a) for a in TAU.Device(device).get_attribute_list())
        attrs = []
        for a in filters:
            for t in all:
                if a and fandango.matchCl(a.strip(),t.strip()):
                    aname = '%s/%s' % (device,t)
                    if not aname in attrs:
                        attrs.append(aname)  
        if attrs:
            print 'Matching attributes are: %s' % str(attrs)[:100]
            if form is None: form = FORM_CLASS(parent)
            elif hasattr(form,'setModel'): form.setModel([])
            ##Configuring the TauForm:
            form.setWithButtons(False)
            form.setWindowTitle(device)
            try: form.setModel(attrs)
            except Exception,e: print('Vacca.widgets.ERROR: Unable to setModel for VaccaPanel.attrs_form!!: %s'%traceback.format_exc())
            #form.setPalette(palettes.get_fullWhite_palette())
            return form
        else: return None
    
    @staticmethod
    def get_comms_form(device,form=None,parent=None):
        print 'In VaccaPanel.get_comms_form(%s)'%device
        params = DEV_COMMS.get(get_eqtype(device),[])
        if not params: #By default an unknown device type will display no commands
            print('VaccaPanel.get_comms_form(%s): By default an unknown device type will display no commands'% device)
            return None 
        if not form: 
            form = COMMAND_CLASS(parent)
        elif hasattr(form,'setModel'): 
            form.setModel('')
        try:
            form.setModel(device)
            if params: 
                form.setSortKey(lambda x,vals=[s[0] for s in params]: vals.index(x.cmd_name.lower()) if str(x.cmd_name).lower() in vals else 10)
                form.setViewFilters([lambda c: any(re.match(s[0].lower(),str(c.cmd_name).lower()) for s in params)])
                form.setDefaultParameters(dict((k,v) for k,v in params if v))
            #form.setPalette(palettes.get_halfWhite_palette())
            for wid in form._cmdWidgets:
                if not hasattr(wid,'getCommand') or not hasattr(wid,'setDangerMessage'): continue
                if re.match('.*(on|off|init|open|close).*',str(wid.getCommand().lower())):
                    wid.setDangerMessage('This action may affect other systems!')
            form._splitter.setStretchFactor(0,70)
            form._splitter.setStretchFactor(1,30)
            form._splitter.setSizes([70,30])
        except Exception,e: 
                print('Unable to setModel for VaccaPanel.comms_from!!: %s'%e)
        return form

def configure_form(dev,form=None):
    """ Creates a TauForm and configures its Status fields 
    """
    if form is None:
        form = FORM_CLASS()
    elif hasattr(form,'setModel'):
        form.setModel([])
    ##Configuring the TauForm:
    form.setWithButtons(False)
    form.setWindowTitle(dev)
    form.setModel('%s/%s' % (dev,a) for a in get_dev_attrs(dev))
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
    filters = sys.argv[2]
    form = None
    if re.match('[\w-]+/[\w-]+/[\w-]+.*',model):
        print 'loading a device panel'
        form = VaccaPanel(palette=palettes.get_fullWhite_palette(),filters=filters)
        form.setModel(model)
    elif model.lower().endswith('.jdw'):
        print 'loading a synoptic'
        form = tau.widget.TauJDrawSynopticsView(designMode=False,
          updateMode=tau.widget.TauJDrawSynopticsView.NoViewportUpdate
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
                TAU.Attribute(m).changePollingPeriod(period)
                if tau!=TAU: tau.Attribute(m).changePollingPeriod(period)
            except: print '(%s).changePollingPeriod(%s): Failed: %s'%(m,period,traceback.format_exc())
    form.show()
    sys.exit(app.exec_())
