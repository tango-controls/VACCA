from PyQt4 import Qt
import taurus
import PyTango
import re,sys,os,time
import fandango
import fandango.functional as fun

from tau.widget.utils.emitter import modelSetter,TauEmitterThread,SingletonWorker
from taurus.qt.qtgui.panel.taurusvalue import TaurusValue
from taurus.qt.qtgui.display.taurusstateled import TaurusStateLed
from taurus.qt.qtgui.display.taurusconfiglabel import TaurusConfigLabel
from taurus.qt.qtgui.display.taurusvaluelabel import TaurusValueLabel


def get_distinct_domains(l):
    return sorted(set(str(s).upper().split('/')[0] for s in l))

#tango = PyTango.Database()
#valves = tango.get_device_exported('*/*/*pnv-*')

DEV_COMMANDS = {
    '*pnv*':['Open','Close'],
    '*vgct*':['On','Off'],
    '*ipct*':['On','Off'],
    }
DEV_TYPES = {
    'Valves':['*pnv-*'],
    'Gauges':['vgct-*'],
    'Pumps':['ipct-*'],
    }

class DomainRow(Qt.QWidget):
    def __init__(self,
            domain,
            label='Valves',
            dev_types=['*pnv'],
            parent=None
            ):
        print 'In DomainRow(%s,%s,%s)'%(domain,label,dev_types)
        Qt.QWidget.__init__(self,parent)
        self.setLayout(Qt.QHBoxLayout())
        self.domain = str(domain)
        self.label = label
        self.dev_types = dev_types
        self.qlabel = Qt.QLabel(domain)
        self.qlabel.setAlignment(Qt.Qt.AlignLeft)
        self.qlabel.setMinimumWidth(50)
        self.layout().setAlignment(Qt.Qt.AlignLeft)
        self.layout().addWidget(self.qlabel)
        if 'pnv' in self.dev_types[0]:
            if 'FE' in domain:
                regexp = {
                    'FE01':'SR01/VC/PNV-*','FE02':'SR02/VC/PNV-*','FE04':'SR03/VC/PNV-*','FE09':'SR05/VC/PNV-*',
                    'FE11':'SR11/VC/PNV-*','FE13':'SR07/VC/PNV-*','FE22':'SR11/VC/PNV-*','FE24':'SR12/VC/PNV-*',
                    'FE29':'SR14/VC/PNV-*','FE34':'SR16/VC/PNV-*',
                }.get(domain.upper(),'FE*/VC/*PNV*')
                domain = regexp.split('/')[0]
            else:
                regexp = str(domain)+'/VC/'+('spnv-*' if 'SR' in domain else '*pnv-*')
        else:
            regexp = str(domain)+'/VC/'+dev_types[0]+'*'
            
        self.devices = [str('%s/VC/%s'%(domain,m)).upper() for m in taurus.Database().get_device_member(regexp)]
        print 'In DomainRow(%s), %d devices found matching %s'%(self.domain,len(self.devices),regexp)
        self.addPressure()
        for v in self.devices:
            model = v+'/State'
            print 'DomainRow(%s): adding %s'%(domain,model)
            tsl = TaurusStateLed(self)
            tsl.model = model
            self.layout().addWidget(tsl)
            tvl = TaurusValueLabel(self)
            tvl.model = model
            tvl.setMinimumWidth(60),tvl.setMaximumWidth(60)
            tvl.setShowQuality(False)
            self.layout().addWidget(tvl)
        self.layout().addStretch(10)
        if self.devices:
            self.buttons = []
            commands = fun.join(*[fun.matchMap(DEV_COMMANDS,t) for t in dev_types])
            for c in commands:
                self.buttons.append(Qt.QPushButton(c,self))
                self.connect(self.buttons[-1], Qt.SIGNAL("pressed()"),(lambda x=c:self.OnPressed(command=x)))
                self.layout().addWidget(self.buttons[-1])
            #self.openButton = Qt.QPushButton('Open',self)
            #self.connect(self.openButton, Qt.SIGNAL("pressed()"),self.Open)
            #self.layout().addWidget(self.openButton)
        self.worker = SingletonWorker()
        self.worker.log.setLogLevel(self.worker.log.Warning)
        self.worker.start()
        return
        
    def addPressure(self):        
        self.pressure = '%s/vc/all/MaxPressure'%self.domain
        print 'DomainRow(%s): adding %s'%(self.domain,self.pressure)
        self.tvl = TaurusValueLabel(self)
        self.tcl = TaurusConfigLabel(self)
        for widget,model,size in ((self.tvl,'%s'%self.pressure,75),(self.tcl,'%s?configuration=unit'%self.pressure,50)):
            self.layout().addWidget(widget)
            widget.setModel(model)
            widget.setMaximumWidth(size)
            widget.setMinimumWidth(size)
            #widget.setShowQuality(False)
        return
        
    def OnPressed(self,command=None,msg=True):
        print 'In DomainRow(%s).OnPressed(%s)'%(self.domain,command)
        if command is None: return
        v = Qt.QMessageBox.warning(None,'%s'%command, \
            'This action may affect other systems!, do you want to proceed?', \
            Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel);
        if v == Qt.QMessageBox.Cancel:
            return
        self.t0,self.errors = time.time(),[]
        for v in self.devices:
            self.worker.queue.put([self.Command,v,command])
        if msg: self.worker.queue.put([self.Done])
        self.worker.next()
        
    #def Open(self,msg=True):
        #print 'In DomainRow(%s).Open(%s)'%(self.domain,self.devices)
        #v = Qt.QMessageBox.warning(None,'OpenValves', \
            #'This action may affect other systems!, do you want to proceed?', \
            #Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel);
        #if v == Qt.QMessageBox.Cancel:
            #return
        #self.t0,self.errors = time.time(),[]
        #for v in self.devices:
            #self.worker.queue.put([self.Command,v,'open'])
        #if msg: self.worker.queue.put([self.Done])
        #self.worker.next()
        
    #def Close(self,msg=True):
        #print 'In DomainRow(%s).Close(%s)'%(self.domain,self.devices)
        #v = Qt.QMessageBox.warning(None,'CloseValves', \
            #'This action may affect other systems!, do you want to proceed?', \
            #Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel);
        #if v == Qt.QMessageBox.Cancel:
            #return
        #self.t0,self.errors = time.time(),[]
        #for v in self.devices:
            #self.worker.queue.put([self.Command,v,'close'])
        #if msg: self.worker.queue.put([self.Done])
        #self.worker.next()
        
    def Command(self,device,command):
        try:
            print '===> In DomainRow(%s).Command(%s,%s)'%(self.domain,device,command)
            if '4' in device: raise Exception('4is4')
            taurus.Device(device).command_inout(command)
        except:
            self.errors.append(device)
            print traceback.format_exc()
        return
            
    def Done(self):
        print 'In DomainRow(%s).Done()'%(self.domain)
        text = '%d %s commands processed in %2.1f seconds.'%(len(self.devices)-len(self.errors),self.label,time.time()-self.t0)
        if self.errors: text+='\n%d %s failed: %s' % (len(self.errors),self.label,self.errors)
        msgBox = Qt.QMessageBox()
        msgBox.setText(text)
        msgBox.exec_()
		
PARENT_KLASS = Qt.QFrame #Qt.QWidget
class DevicesPanel(PARENT_KLASS):
    
    def __init__(self,
            parent=None,
            label='Valves',
            dev_types=['pnv'],
            domains = (['LI','LT']+['LT%02d'%i for i in range(1,3)]+['BO%02d'%i for i in range(1,5)]+['BT']+['SR%02d'%i for i in range(1,17)])
            ):
        self.label = label
        self.dev_types = dev_types
        print 'In DevicesPanel(%s,%s,%s)'%(self.label,dev_types,domains)
        DevicesPanel._domains = domains
        PARENT_KLASS.__init__(self,parent)
        self.setSizePolicy(Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding))
        self.setLayout(Qt.QVBoxLayout())
        self.layout().setAlignment(Qt.Qt.AlignTop)
        self.setDomains('BO*')
        if hasattr(self,'setFrameStyle'):
            self.setFrameStyle(self.Box)
    
    def setDomains(self,domains=''):
        print 'In DevicesPanel.setDomains(%s)'%domains
        self.domains = domains
        if 'FE' in domains and 'pnv' in self.dev_types:
            regexp = 'SR*/VC/PNV-*'
            _fes = [f for f in get_distinct_domains(taurus.Database().get_device_exported('fe*')) if re.match('fe[0-9]'.lower(),f.lower())]
            domains = _fes
        else:
            regexp = str(domains)+'*/vc/%s'%self.dev_types[0]
            print '\tregexp = %s'%regexp
            domains = domains if hasattr(domains,'__iter__') and not isinstance(domains,basestring) else get_distinct_domains(taurus.Database().get_device_domain(regexp))
        print 'domains: %s'%domains
        self.rows = []
        for d in domains: #(domains+fes):
            print '\tAdding row for domain %s'%d
            self.rows.append(DomainRow(d,self.label,self.dev_types,parent=self))
            self.layout().addWidget(self.rows[-1])
            
    def clear(self):
        print 'In %sPanel.clear()'%self.label
        while self.layout().count():
            wi = self.layout().itemAt(0)
            w = wi.widget()
            w.hide()
            self.layout().removeItem(wi)
            
class DomainsChooser(Qt.QWidget):
    _persistent_ = None #It prevents the instances to be destroyed if not called explicitly
    
    def __init__(self,
            parent=None,
            label='Valves',
            dev_types=['pnv'],
            domains=['LI','LT','BO','BT','SR','FE'],
            ):
        self.label = label
        print 'In DomainsChooser(%s,%s,%s)'%(label,dev_types,domains)
        Qt.QWidget.__init__(self,parent)
        self.setWindowTitle('Vacuum %s Manager'%self.label)
        self.setLayout(Qt.QVBoxLayout())
        self.setMinimumWidth(800)#550)
        self.setMinimumHeight(700)
        self.layout().setAlignment(Qt.Qt.AlignTop)
        self.combo = Qt.QComboBox(self)
        self.domains = ['Choose...']+domains
        self.combo.addItems(self.domains)
        self.panel = DevicesPanel(self,label,dev_types)
        self.layout().addWidget(Qt.QLabel('Choose a domain to see %s status:'%self.label))
        self.layout().addWidget(self.combo)
        USE_SCROLL = False
        if USE_SCROLL:
            self.scroll = Qt.QScrollArea(self)
            self.scroll.setWidget(self.panel)        
            self.layout().addWidget(self.scroll)
        else:
            self.layout().addWidget(self.panel)
        self.combo.connect(self.combo, Qt.SIGNAL("currentIndexChanged (const QString&)"), self.comboIndexChanged)
        self.connect(self.combo, Qt.SIGNAL("currentIndexChanged (const QString&)"), self.comboIndexChanged)
        type(self)._persistent_ = self
        
    def closeEvent(self,evt):
        Qt.QWidget.closeEvent(self,evt)
        type(self)._persistent_ = None
    
    def comboIndexChanged(self,text):
        print 'In comboIndexChanged(%s)'%text
        if str(text)=='Choose...' or str(text)==self.panel.domains: 
            return
        self.panel.clear()
        self.panel.setDomains(str(text))
        
    def OpenAll(self):
        return
    def CloseAll(self):
        return

def main():
    print 'In main()'
    if 'qapp' not in locals() and 'qapp' not in globals():
        qapp = Qt.QApplication([])
    import sys
    label = sys.argv[1]
    if sys.argv[2:]: dev_types = sys.argv[2:]
    else: dev_types = DEV_TYPES.get(label,[])
    vp = DomainsChooser(label=label,dev_types=dev_types)
    vp.show()
    sys.exit(qapp.exec_())

if __name__ == "__main__":
    main()