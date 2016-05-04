#!/usr/bin/python
import sys
sys.path.insert(0,'/homelocal/sicilia/lib/python/site-packages/vacca/lib')

import fandango,imp,time,traceback
from fandango import SortedDict,partial
import taurus
from taurus.qt import Qt
import taurus.qt.qtgui.plot
from taurus.qt.qtgui.plot import TaurusPlot
from taurus.qt.qtgui.table import TaurusGrid
from taurus.qt.qtgui.panel import TaurusDevicePanel

from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath
WDIR = WORKING_DIR

def get_fes_grid():
    tg = TaurusGrid()
    tg.setColumnLabels('VcGauges:FE*FE*VGCT,Pressures:*VGCT*/P*,VcPumps:IPCT|SPBX, EPS:EPS|PNV')
    tg.setRowLabels(','.join([
        'FE01:FE01/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE02:FE02/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE04:FE04/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE09:FE09/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE11:FE11/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE13:FE13/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE22:FE22/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE24:FE24/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE29:FE29/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',
        'FE34:FE34/*/*/*(IPCT|VGCT|SPBX|PLC|P1|P2)*',]
        ))
    tg.showRowFrame(False)
    tg.showColumnFrame(True)
    #tg.setModel('(FE*/(VC|EPS)/(IPCT|VGCT|SPBX|PLC)*)')
    tg.setModel('FE*/VC/ALL/*',load=False)
    tg.setModel('FE*/VC/VGCT*/(P1|P2)',append=True)
    #tg.setModel('(FE*/VC/ALL/*|FE*/VC/VGCT*/P1|FE*/VC/VGCT*/P2)')
    return tg

def get_ids_grid():
    #global tg
    tg = TaurusGrid()
    tg.setRowLabels('VcGauges:VGCT|Pressure|Vacuum, VarianDUAL:IPCT, EPS:EPS|PNV|SCW|Error')
    tg.setColumnLabels(','.join([
        'ID04:*(ID04|SCW)*',
        'ID11:ID11/*/*/*',
        'ID13:ID13/*/*/*',]))
    tg.showRowFrame(True)
    tg.showColumnFrame(True)
    #tg.showAttributeLabels(False)
    #tg.showAttributeUnits(False)    
    tg.setModel('ID*/*/(PLC-01|VGCT*|IPCT*)/(State|P[12]|Thermocouples)$',load=False)
    tg.setModel('SR/ID/SCW01/(State|Pressure|Vacuum|Cooler*Error)',append=True)
    #tg.showAttributeLabels(False)
    #tg.showAttributeUnits(False)
    return tg

def get_profiler(sector):
    from vacca.plot import setup_profile_plot
    frame = Qt.QFrame()
    frame.setLayout(Qt.QVBoxLayout())
    button = Qt.QPushButton('See Profile')
    def show_plot(sector=sector):
        global f2
        f2 = Qt.QFrame()
        f2.setLayout(Qt.QVBoxLayout())
        label = Qt.QLabel()
        image = wdir('image/%s-synoptic.jpg'%sector)
        print image
        label.setPixmap(Qt.QPixmap(image).scaledToHeight(200))
        f2.layout().addWidget(label)
        plot = TaurusPlot()
        plot.setFixedHeight(200)
        setup_profile_plot(plot,sector+'/vc/all')
        f2.layout().addWidget(plot)
        f2.show()
        return f2
    button.connect(button,Qt.SIGNAL('pressed()'),show_plot)
    frame.layout().addWidget(button)
    return frame

USE_TAU_MAIN_WINDOW = False

isString = lambda s: any(isinstance(s,t) for t in (basestring,Qt.QString))

def forward2device(item_name,target=None,resume=False,trace=True):
    #This method parses composed state attributes
    m = item_name
    item_name = str(item_name).split('?')[0]
    if item_name.split('/')[-1].count('_')==2: #Attribute name seems to be a device name!
        item_name = '/'.join(item_name.split('/')[-1].split('_'))
    elif item_name.count('/')>2: #Attribute names are reduced to device names!
        item_name = '/'.join(item_name.split('/')[:3])
    if trace: print 'forward2device(%s) => %s'%(m,item_name)
    if target is not None: target(item_name)
    return item_name
    
def forward2composer(item_name,target=None,resume=False,trace=True):
    #This method parses devices to composed state attributes
    m = item_name
    item_name = str(item_name)
    name_in_tab = True
    if name_in_tab: item_name = '.*'+item_name.replace('/','.')
    if trace: print 'forward2composer(%s) => %s'%(m,item_name)
    if target is not None: target(item_name)
    return item_name

class SectorWidget(Qt.QSplitter):
    
    def __init__(self,parent=None):
        Qt.QWidget.__init__(self,parent)
        
        from taurus.qt.qtgui.panel import TaurusDevicePanel
        from taurus.qt.qtgui.plot import TaurusPlot
        try:
            from vacca.config import AttributeFilters,CommandFilters
            if AttributeFilters: TaurusDevicePanel.setAttributeFilters(AttributeFilters)
            if CommandFilters: TaurusDevicePanel.setCommandFilters(CommandFilters)
        except:
            print 'SectorWidget(): Unable to load AttributeFilters'
            print traceback.format_exc()
        #self.setLayout(Qt.QHBoxLayout())
        self.MaxSynopticSize = (0,0)
        self.GRID_CLASS = TaurusGrid
        self.devicePanel = TaurusDevicePanel(self)
        self.devicePanel.setMinimumWidth(300)
        self.addWidget(self.devicePanel)
        self.plotSplit = Qt.QSplitter()
        self.plotSplit.setOrientation(Qt.Qt.Vertical)
        self.addWidget(self.plotSplit)
        self.synopticPanel = Qt.QWidget(self)
        self.synopticPanel.setLayout(Qt.QVBoxLayout())
        self.plotSplit.addWidget(self.synopticPanel)
        self.frame = Qt.QFrame()
        self.frame.setLayout(Qt.QVBoxLayout())
        self.scrollable = Qt.QScrollArea()
        self.scrollable.setAlignment(Qt.Qt.AlignCenter)
        self.drawing = Qt.QLabel()
        self.scrollable.setWidget(self.drawing)
        self.scrollable.setMinimumHeight(200)
        #self.frame.layout().addWidget(self.drawing)#self.scrollable)
        self.plot = TaurusPlot()
        #self.frame.layout().addWidget(self.scrollable)
        #self.frame.layout().addWidget(self.plot)
        #self.plotSplit.addWidget(self.frame)
        self.plotSplit.addWidget(self.scrollable)
        self.plotSplit.addWidget(self.plot)
        self.setSizes([1,1])
        
    def setModel(self,model):
        self.devicePanel.setModel(model)
        self.setSizes([1,1])
    
    def trace(self,msg):
        print '%s: %s' % (type(self).__name__,msg)    
        
    def get_empty_grid(self):
        import taurus.qt.qtgui.table.taurusgrid
        #global tg1
        tg1 = taurus.qt.qtgui.table.taurusgrid.TaurusGrid()
        tg1.showRowFrame(False)
        tg1.showColumnFrame(True)
        return tg1
    
    def createJdraw(self,alias=None,CONNECT_JDRAW = False):
        self.trace('%s: In PySynopticTree.createJDraw()'%time.ctime())
        from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView
        jdr = TaurusJDrawSynopticsView(alias=(alias or {}))
        self.trace('%s: Out of PySynopticTree.createJDraw()'%time.ctime())
        return jdr
        
    def forceJdrawSize(self,jdr):
        self.trace('='*80)
        self.trace('In PySynopticTree.forceJdrawSize()')
        jdr.size0 = jdr.sizeHint() #Recording the original size of the jdraw file
        height,width = jdr.size0.height(),jdr.size0.width()
        self.MaxSynopticSize = (
            self.MaxSynopticSize[0] or width,
            (height*float(self.MaxSynopticSize[0])/width) if (self.MaxSynopticSize[0] and not self.MaxSynopticSize[1]) else  (self.MaxSynopticSize[1] or height)
            #(height*self.MaxSynopticSize[0]/width) if (self.MaxSynopticSize[0] and not self.MaxSynopticSize[1]) else  (self.MaxSynopticSize[1] or height)
            )
        self.trace('\t%s size is (%s,%s) vs Max(%s)' % (str(jdr.getModel()),width,height,self.MaxSynopticSize))
        
        FACTOR = 0.9
        w,h = int(FACTOR*self.MaxSynopticSize[0]),int(FACTOR*self.MaxSynopticSize[1])
        self.trace('\tForcing Synoptic Size from %s,%s to %s,%s'%(width,height,w,h))
        jdr.adjustSize()
        #This line avoid resizing of the synoptic when maximizing
        jdr.setMinimumWidth(w) #setFixedWidth(w)
        jdr.setMinimumHeight(h) #setFixedHeight(h)
        jdr.adjustSize()
        self.trace('='*80)
        return jdr
    
    def refreshJDraw(self):
        self.trace('In PySynopticTree.refreshJDraw()')
        [s.getSynoptic().refreshModel() for s in self.Tabs.values()]    
    
    def loadJdraw(self,jdr=None,filename=None,alias=None,delayed=False,forcesize=True):
        self.trace(time.ctime()+'In PySynopticTree.loadJDraw(%s,forcesize=%s)'%(filename,forcesize))
        if jdr is None: 
            jdr = self.createJdraw(alias=alias)
        if filename is not None: 
            self.trace(time.ctime()+': In PySynopticTree.loadJDraw(%s): jdr.setModel()'%filename)
            jdr.setModel(model=filename,delayed=delayed) #False)
            jdr.setResizable(True)
            #Forcesize is True only when NSynopctics>1
            if forcesize: self.forceJdrawSize(jdr)
        else:
            jdr.setObjectName(filename)
            filename = jdr.openJDraw()
            jdr.setResizable(True)
            #Forcesize is True only when NSynopctics>1
            if forcesize: self.forceJdrawSize(jdr)
        
        self.trace(time.ctime()+': Out of PySynopticTree.loadJDraw(%s)'%filename)
        return jdr
            
    #def loadSynoptic(self,name='',filename=None,alias=None,delayed=True,forcesize=True,update_tree=True):
    def setSector(self,sector):
        filenames = SYNOPTICS[sector]
        synoptics = []
        print 'setSector(%s): %s'%(sector,filenames)
        if not fandango.isSequence(filenames): filenames = [filenames]
        for index,filename in enumerate(filenames):
            if isinstance(filename,Qt.QWidget):
                # The QWidget is used directly
                synoptic = filename
            elif isString(filename):
                if filename.endswith('.jdw'):
                    print('loadSynoptic(%s): open a JDraw file in a new tab'%filename)
                    synoptic = self.loadJdraw(filename=filename) #bool(1<len(filenames)))
                    synoptic.setVerticalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOff)
                    synoptic.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOff)                    
                    Qt.QObject.connect(synoptic, Qt.SIGNAL("graphicItemSelected(QString)"), partial(forward2device,target=self.devicePanel.setModel))
                    self.setWindowTitle(filename.rsplit('.',1)[0])
                else:
                    print('loadSynoptic(%s): opens a New TaurusGrid instance in a new tab'%filename)
                    synoptic = self.GRID_CLASS()
                    if filename.endswith('.grid'):
                        synoptic.load(filename,delayed=False)
                        models = synoptic.getModel()
                    else:
                        #Try to initialize a grid from a model string
                        models =  sorted(set(m.rsplit('/',1)[0] for m in get_all_models(filename)))
                        assert  models,'Unknown file type (.jdw or .grid file required): %s' % filename
                        synoptic.setModel(filename,delayed=False)
                    synoptic.showColumnFrame(True)
            elif callable(filename):
                print('loadSynoptic(%s): The result of the method call is used directly'%filename)
                synoptic = filename()
                if not isinstance(synoptic,Qt.QWidget): raise Exception,'A method returning QWidget is required!'
            Qt.QObject.connect(synoptic, Qt.SIGNAL("itemClicked(QString)"), partial(forward2device,target=self.devicePanel.setModel))
            self.synopticPanel.layout().addWidget(synoptic) #Adding second widget in the same tab
        try:
            image = wdir('SR/image/%s-synoptic.jpg'%sector)
            print image
            px = Qt.QPixmap(image).scaledToWidth(1000)
            assert px.height()>0,'NullPixmap'
            self.drawing.setPixmap(px)
            self.drawing.setMinimumWidth(px.width())
            self.drawing.setMinimumHeight(px.height())
            self.drawing.setSizePolicy(Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Fixed)
            self.scrollable.setWidget(self.drawing)
        except:
            print 'VaccaGUI: unable to set %s image: %s' % (sector,image)
            self.scrollable.setFixedHeight(0)
        #self.drawing.setSizePolicy(Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding))
        if sector.lower() in ('fe','id'):
            self.plot.hide()
            self.plot.setFixedHeight(0)
        else: 
            try:
                taurus.Device(sector+'/vc/all').ping()
                setup_profile_plot(self.plot,sector+'/vc/all')
            except:
                print 'VaccaGUI: unable to set %s profile'%sector
                self.plot.setFixedHeight(0)

#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       #('ALL',wdir('jdw/ALBA_ESH.jdw')),
        ('mbar',wdir('SR/grids/ALL.grid')), 
        ('LT',wdir('SR/grids/LT.grid')),    
        ('BO',wdir('SR/jdw/Booster_Gauges.jdw')),
        ('BOg',(wdir('SR/grids/BO.grid')
            ,)#(lambda s='BO':get_profiler(s)))
            ),
        ('BT',wdir('SR/grids/BT.grid')),            
        ('SR01',(wdir('SR/grids/SR01.grid')
            ,)#(lambda s='SR01':get_profiler(s)))
            ),
        ('SR02',(wdir('SR/grids/SR02.grid')
            ,(lambda s='SR02':get_profiler(s)))
            ),
        ('SR03',(wdir('SR/grids/SR03.grid')
            ,)#(lambda s='SR03':get_profiler(s)))
            ),
        ('SR04',(wdir('SR/grids/SR04.grid')
            ,)#(lambda s='SR04':get_profiler(s)))
            ),
        ('SR05',(wdir('SR/grids/SR05.grid')
            ,)#(lambda s='SR05':get_profiler(s)))
            ),
        ('SR06',(wdir('SR/grids/SR06.grid')
            ,)#(lambda s='SR06':get_profiler(s)))
            ),  
        ('SR07',(wdir('SR/grids/SR07.grid')
            ,)#(lambda s='SR07':get_profiler(s)))
            ),
        ('SR08',(wdir('SR/grids/SR08.grid')
            ,)#(lambda s='SR08':get_profiler(s)))
            ),
        ('SR09',(wdir('SR/grids/SR09.grid')
            ,)#(lambda s='SR09':get_profiler(s)))
            ),
        ('SR10',(wdir('SR/grids/SR10.grid')
            ,)#(lambda s='SR10':get_profiler(s)))
            ),
        ('SR11',(wdir('SR/grids/SR11.grid')
            ,)#(lambda s='SR11':get_profiler(s)))
            ),
        ('SR12',(wdir('SR/grids/SR12.grid')
            ,)#(lambda s='SR12':get_profiler(s)))
            ),
        ('SR13',(wdir('SR/grids/SR13.grid')
            ,)#(lambda s='SR13':get_profiler(s)))
            ),
        ('SR14',(wdir('SR/grids/SR14.grid')
            ,)#(lambda s='SR14':get_profiler(s)))
            ),
        ('SR15',(wdir('SR/grids/SR15.grid')
            ,)#(lambda s='SR15':get_profiler(s)))
            ),
        ('SR16',(wdir('SR/grids/SR16.grid')
            ,)#(lambda s='SR16':get_profiler(s)))
            ),
        ('ID',get_ids_grid),
        ('FE',get_fes_grid),
    ])

EXCLUDE = []


## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = dict((k,d) for k,d in {
    'PROFILE':'SR/VC/ALL',
    '(LI|LT)([^0-9/]|$)*':'LT/VC/ALL',
    'BO([^0-9/]|$)*':'BO/VC/ALL',
    'BT(/|$)*':'BT/VC/ALL',
    '^(SR|ALL|ALBA|mBar)(/*|$)':'SR/VC/ALL',
    'SR01*':'SR01/VC/ALL',
    'SR02*':'SR02/VC/ALL',
    'SR03*':'SR03/VC/ALL',
    'SR04*':'SR04/VC/ALL',
    'SR05*':'SR05/VC/ALL',
    'SR06*':'SR06/VC/ALL',
    'SR07*':'SR07/VC/ALL',
    'SR08*':'SR08/VC/ALL',
    'SR09*':'SR09/VC/ALL',
    'SR10*':'SR10/VC/ALL',
    'SR11*':'SR11/VC/ALL',
    'SR12*':'SR12/VC/ALL',
    'SR13*':'SR13/VC/ALL',
    'SR14*':'SR14/VC/ALL',
    'SR15*':'SR15/VC/ALL',
    'SR16*':'SR16/VC/ALL',
    'FE[^0-9]?*':'FE/VC/ALL',
    'ID[^0-9]?*':'ID/VC/ALL',
    }.items() if k not in EXCLUDE)

def get_sectors_toolbar():
    try:
        import vacca.panel,os
        from taurus.qt.qtgui.display import TaurusConfigLabel,TaurusValueLabel,TaurusLabel
        from taurus.qt.qtgui.panel import TaurusForm
        sectors = Qt.QToolBar()
        print '#'*240
        print vacca.utils.WORKING_DIR
        print WDIR
        print os.getenv('WORKING_DIR')
        w = TaurusConfigLabel()
        w.setDragEnabled(True)
        w.setModel('sr/di/dcct/averagecurrent?configuration=Label')
        w.setFixedWidth(70)
        sectors.addWidget(w)
        c = TaurusLabel()
        c.setModel('sr/di/dcct/averagecurrent')
        c.setFixedWidth(70)
        c.setDragEnabled(True)
        sectors.addWidget(c)
        buttons = []
        for k in SYNOPTICS:
            buttons.append(vacca.panel.DomainButton(sectors))
            buttons[-1].setLabel(k)
            buttons[-1].setModel(fandango.matchMap(COMPOSERS,k)+'/State',wdir('SR/sector.py %s'%k))
            buttons[-1].setFixedHeight(60)
            sectors.addWidget(buttons[-1])
        sectors.setFixedHeight(60)
        return sectors
    except:
        traceback.print_exc()
    
if __name__ == '__main__':
    import sys
    qapp = Qt.QApplication([])
    arg = sys.argv[1]
    import vacca.panel
    splash = vacca.panel.VaccaSplash()
    panel = SectorWidget()
    panel.setSector(arg)
    panel.setModel(fandango.matchMap(COMPOSERS,arg))
    panel.show()
    splash.close()
    qapp.exec_()
