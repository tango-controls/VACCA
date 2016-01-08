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

class DomainRow(Qt.QWidget):
    def __init__(self,domain,parent=None):
        print 'In DomainRow(%s)'%domain		
        Qt.QWidget.__init__(self,parent)
        self.setLayout(Qt.QHBoxLayout())
        self.domain = str(domain)
        self.label = Qt.QLabel(domain)
        self.label.setAlignment(Qt.Qt.AlignLeft)
        self.label.setMinimumWidth(50)
        self.layout().setAlignment(Qt.Qt.AlignLeft)
        self.layout().addWidget(self.label)
        if 'FE' in domain:
            regexp = {
                'FE01':'SR01/VC/PNV-*','FE02':'SR02/VC/PNV-*','FE04':'SR03/VC/PNV-*','FE09':'SR05/VC/PNV-*',
                'FE11':'SR11/VC/PNV-*','FE13':'SR07/VC/PNV-*','FE22':'SR11/VC/PNV-*','FE24':'SR12/VC/PNV-*',
                'FE29':'SR14/VC/PNV-*','FE34':'SR16/VC/PNV-*',
            }.get(domain.upper(),'FE*/VC/*PNV*')
            domain = regexp.split('/')[0]
        else:
            regexp = str(domain)+'/VC/'+('spnv-*' if 'SR' in domain else '*pnv-*')
            
        self.valves = [str('%s/VC/%s'%(domain,m)).upper() for m in taurus.Database().get_device_member(regexp)]
        print 'In DomainRow(%s), %d devices found matching %s'%(self.domain,len(self.valves),regexp)
        self.addPressure()
        for v in self.valves:
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
        if self.valves:
            self.openButton = Qt.QPushButton('Open',self)
            self.closeButton = Qt.QPushButton('Close',self)
            self.connect(self.openButton, Qt.SIGNAL("pressed()"),self.Open)
            self.connect(self.closeButton, Qt.SIGNAL("pressed()"),self.Close)
            self.layout().addWidget(self.openButton)
            self.layout().addWidget(self.closeButton)
        else: self.openButton,self.closeButton = None,None
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
        
    def Open(self,msg=True):
        print 'In DomainRow(%s).Open(%s)'%(self.domain,self.valves)
        v = Qt.QMessageBox.warning(None,'OpenValves', \
            'This action may affect other systems!, do you want to proceed?', \
            Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel);
        if v == Qt.QMessageBox.Cancel:
            return
        self.t0,self.errors = time.time(),[]
        for v in self.valves:
            self.worker.queue.put([self.Command,v,'open'])
        if msg: self.worker.queue.put([self.Done])
        self.worker.next()
        
    def Close(self,msg=True):
        print 'In DomainRow(%s).Close(%s)'%(self.domain,self.valves)
        v = Qt.QMessageBox.warning(None,'CloseValves', \
            'This action may affect other systems!, do you want to proceed?', \
            Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel);
        if v == Qt.QMessageBox.Cancel:
            return
        self.t0,self.errors = time.time(),[]
        for v in self.valves:
            self.worker.queue.put([self.Command,v,'close'])
        if msg: self.worker.queue.put([self.Done])
        self.worker.next()
        
    def Command(self,device,command):
        try:
            print '===> In DomainRow(%s).Command(%s,%s)'%(self.domain,device,command)
            if '4' in device: raise Exception('4is4')
            taurus.Device(device).command_inout(command)
        except:
            self.errors.append(device)
        return
            
    def Done(self):
        print 'In DomainRow(%s).Done()'%(self.domain)
        text = '%d valves commands processed in %2.1f seconds.'%(len(self.valves)-len(self.errors),time.time()-self.t0)
        if self.errors: text+='\n%d valves failed: %s' % (len(self.errors),self.errors)
        msgBox = Qt.QMessageBox()
        msgBox.setText(text)
        msgBox.exec_()
		
PARENT_KLASS = Qt.QFrame #Qt.QWidget
class ValvesPanel(PARENT_KLASS):
    
    _domains = ['LI','LT']+['LT%02d'%i for i in range(1,3)]+['BO%02d'%i for i in range(1,5)]+['BT']+['SR%02d'%i for i in range(1,17)]
    _fes = [f for f in get_distinct_domains(taurus.Database().get_device_exported('fe*')) if re.match('fe[0-9]'.lower(),f.lower())]        
    
    def __init__(self,parent=None,regexp='*pnv-*'):
        print 'In ValvesPanel()'
        PARENT_KLASS.__init__(self,parent)
        self.setSizePolicy(Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding))
        self.regexp=regexp
        self.setLayout(Qt.QVBoxLayout())
        self.layout().setAlignment(Qt.Qt.AlignTop)
        self.setDomains()#'BO')
        if hasattr(self,'setFrameStyle'):
            self.setFrameStyle(self.Box)
    
    def setDomains(self,domains=''):
        print 'In ValvesPanel.setDomains(%s)'%domains
        self.domains = domains
        if 'FE' in domains:
            regexp = 'SR*/VC/PNV-*'
            domains = type(self)._fes
        else:
            regexp = str(domains)+self.regexp
            domains = domains if hasattr(domains,'__iter__') and not isinstance(domains,basestring) else get_distinct_domains(taurus.Database().get_device_domain(regexp))
        print 'domains: %s'%domains
        self.rows = []
        for d in domains: #(domains+fes):
            self.rows.append(DomainRow(d,self))
            self.layout().addWidget(self.rows[-1])
            
    def clear(self):
        print 'In ValvesPanel.clear()'
        while self.layout().count():
            wi = self.layout().itemAt(0)
            w = wi.widget()
            w.hide()
            self.layout().removeItem(wi)
            
class ValvesChooser(Qt.QWidget):
    _persistent_ = None #It prevents the instances to be destroyed if not called explicitly
    
    def __init__(self,parent=None,domains=None,regexp='*pnv-*'):
        print 'In ValvesChooser()'
        Qt.QWidget.__init__(self,parent)
        self.setWindowTitle('Vacuum Valves Manager')
        self.setLayout(Qt.QVBoxLayout())
        self.setMinimumWidth(800)#550)
        self.setMinimumHeight(700)
        self.layout().setAlignment(Qt.Qt.AlignTop)
        self.combo = Qt.QComboBox(self)
        domains = domains if domains else ['LI','LT','BO','BT','SR','FE']
        self.domains = (['Choose...']+domains) if len(domains)>1 else domains
        self.combo.addItems(self.domains)
        self.panel = ValvesPanel(self)
        self.layout().addWidget(Qt.QLabel('Choose a domain to see valves status:'))
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
        if len(domains)==1: self.emit(Qt.SIGNAL("currentIndexChanged (const QString&)"),Qt.QString(domains[0]))
        type(self)._persistent_ = self
        
    def closeEvent(self,evt):
        Qt.QWidget.closeEvent(self,evt)
        type(self)._persistent_ = None
    
    #def __del__(self):
        #print 'In ValvesChooser.del()'
        ##try: Qt.QWidget.__del__(self)
        ##except: pass
        #type(self)._persistent_ = None
        
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
    import sys
    print 'In main()'
    args = sys.argv[1:]
    if 'qapp' not in locals() and 'qapp' not in globals():
        qapp = Qt.QApplication([])
    vp = ValvesChooser(domains=args)
    vp.show()
    sys.exit(qapp.exec_())

if __name__ == "__main__":
    main()