import os,sys
from fandango.dicts import SortedDict
from include import wdir

"""
Configuration file for Storage Ring Vacuum Application

Variables to be configured:
    TITLE,LOG_LEVEL,
    URL_REDMINE,URL_DEVELOPER,URL_VACUUM,URL_HELP,
    SYNOPTICS,PLOT,TREE,COMPOSERS
"""

__all__ = [
    'TITLE','LOG_LEVEL','TOOLBAR','MENUS',
    'URL_TRACKER','URL_DEVELOPER','URL_VACUUM','URL_HELP',
    'SYNOPTICS','SYNOPTIC_WIDTH','PLOT_HEIGHT','POST_HOOK',
    'DEVICE','TREE','COMPOSERS','EXCLUDE','CABLING_TREE'
    ]

#print 'Uncomment these lines to force application folder if needed'
#os.chdir('/homelocal/sicilia/applications/vacca')
#sys.path.insert(2,'/homelocal/sicilia/applications/vacca')

#Global variables are defined here
TITLE = 'LaVACCA: The VACuum Control Application for ALBA Synchrotron'
LOG_LEVEL = 'WARNING'

URL_TRACKER = 'http://84.89.244.70:3000/projects/show/vaccabo'
URL_DEVELOPER = 'http://www.cells.es/Members/srubio'
URL_VACUUM = 'http://www.cells.es/Intranet/Divisions/Computing/Controls/Help/Vacuum/vacca_gui'
URL_HELP = wdir('doc/vacca_gui.html')
URL_LOGBOOK = 'http://logbook.cells.es/vacuum/'
 #Searches:
 #http://logbook.cells.es/vacuum/?System=%5EStorage+ring%24&Equipment=IP-15|
 #IP-4
 #OR
 #http://logbook.cells.es/vacuum/?SubSystem=%5ES10%24       

#------------------------------------------------------------------------------
## Default Values
#------------------------------------------------------------------------------
SYNOPTIC_WIDTH=1075
PLOT_HEIGHT=350
PANEL_WIDTH=350
SYNOPTICS = {} #{'Name':'.jdw/.grid'} #This dictionary defines the synoptic for each domain
TREE = {} #{'topnode':{'branch':{'endnode':{}}}} #'pickle file' #Dictionary with all device tree nodes
COMPOSERS = {'PROFILE':''} #{'PROFILE':'SR/VC/ALL','*/*/*':'SR/VC/ALL'} # Assigns composer for PROFILE and each subdomain
TOOLBAR = [] #[('','',None)] #Name,icon,action tuples
MENUS = [] #[('',[('',None,None)])] #Name, Submenu((Name,Action,Icon tuples))
POST_HOOK = None #Method called at the end of application initialization
DEVICE = '' #The device that will be shown by default when loading the application
EXCLUDE = []
#------------------------------------------------------------------------------

###############################################################################
# Edit whatever you want below this lines
###############################################################################

DEVICE = 'SR/VC/ALL' 
import widgets
widgets.DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']
widgets.DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']

import fandango.linos

def get_bo_grid():
    import tau.widget.taugrid
    global tg_bo
    tg_bo = tau.widget.taugrid.TauGrid()
    tg_bo.load({
        #'model':'BO/VC/ALL/.*(VGCT|IPCT|SPBX|Pressures|PNV|CCG|PIR|IP-|Thermo|EPS-PLC-01$).*',
        'model':'BO/VC/ALL/.*(Pressures|PNV|Thermo|EPS-PLC-01$).*',
        'frames': False,
        'delayed': False,
        'row_labels': ','.join(':'.join(t) for t in [
            #('Vacuum', 'VGCT|IPCT|PIR-|CCG-|IP-|SPBX'),
            ('EPS', 'EPS|Pressures|PNV'),
            ('Others', '.*')
            ]),
        'column_labels': ','.join(':'.join(t) for t in [
            #('EPS', 'VGCT|EPS'),
            #('PNV', 'IPCT|PNV'),
            #('Temp.', 'SPBX|Thermo'),
            #('mbar', 'Pressure'),
            #('Gauges', 'CCG|PIR'),
            ('BO01','BO01'),
            ('BO02','BO02'),
            ('BO03','BO03'),
            ('BO04','BO04'),
            ('BO','.*'),
            ]),
        })
    tg_bo.showRowFrame(False)
    tg_bo.showColumnFrame(False)
    return tg_bo

def POST_HOOK(ui):
    print 'In sr.rc.py POST_HOOK method ...'
    try:
        global tg_bo
        #tg_bo.showAttributeLabels(False)
        #tg_bo.showAttributeUnits(False)
    except:
        print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
def get_fes_grid():
    import tau.widget.taugrid
    #global tg
    tg = tau.widget.taugrid.TauGrid()
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
    tg.showColumnFrame(False)
    #tg.setModel('(FE*/(VC|EPS)/(IPCT|VGCT|SPBX|PLC)*)')
    tg.setModel('FE*/VC/ALL/*',load=False)
    tg.setModel('FE*/VC/VGCT*/(P1|P2)',append=True)
    #tg.setModel('(FE*/VC/ALL/*|FE*/VC/VGCT*/P1|FE*/VC/VGCT*/P2)')
    return tg

def get_ids_grid():
    import tau.widget.taugrid
    #global tg
    tg = tau.widget.taugrid.TauGrid()
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
    from vacca.widgets import Qt,setup_profile_plot
    import taurus
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
        plot = taurus.qt.qtgui.plot.TaurusPlot()
        plot.setFixedHeight(200)
        setup_profile_plot(plot,
            '%s/vc/all/ccgaxxis|%s/vc/all/ccgpressures'%(sector,sector),
            '%s/vc/all/ipaxxis|%s/vc/all/ippressures'%(sector,sector),
            '%s/vc/all/thermoaxxis|%s/vc/all/thermocouples'%(sector,sector))
        f2.layout().addWidget(plot)
        f2.show()
        return f2
    button.connect(button,Qt.SIGNAL('pressed()'),show_plot)
    frame.layout().addWidget(button)
    return frame

#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       ('ALL',wdir('jdw/ALBA_ESH.jdw')),
        ('mbar',wdir('grids/ALL.grid')), 
        ('LT',wdir('grids/LT.grid')),    
        ('BO',wdir('jdw/Booster_Gauges.jdw')),
        ('BOg',(wdir('grids/BO.grid')
            ,(lambda s='BO':get_profiler(s)))
            ),
        ('BT',wdir('grids/BT.grid')),            
        ('SR01',(wdir('grids/SR01.grid')
            ,(lambda s='SR01':get_profiler(s)))
            ),
        ('SR02',(wdir('grids/SR02.grid')
            ,(lambda s='SR02':get_profiler(s)))
            ),
        ('SR03',(wdir('grids/SR03.grid')
            ,(lambda s='SR03':get_profiler(s)))
            ),
        ('SR04',(wdir('grids/SR04.grid')
            ,(lambda s='SR04':get_profiler(s)))
            ),
        ('SR05',(wdir('grids/SR05.grid')
            ,(lambda s='SR05':get_profiler(s)))
            ),
        ('SR06',(wdir('grids/SR06.grid')
            ,(lambda s='SR06':get_profiler(s)))
            ),  
        ('SR07',(wdir('grids/SR07.grid')
            ,(lambda s='SR07':get_profiler(s)))
            ),
        ('SR08',(wdir('grids/SR08.grid')
            ,(lambda s='SR08':get_profiler(s)))
            ),
        ('SR09',(wdir('grids/SR09.grid')
            ,(lambda s='SR09':get_profiler(s)))
            ),
        ('SR10',(wdir('grids/SR10.grid')
            ,(lambda s='SR10':get_profiler(s)))
            ),
        ('SR11',(wdir('grids/SR11.grid')
            ,(lambda s='SR11':get_profiler(s)))
            ),
        ('SR12',(wdir('grids/SR12.grid')
            ,(lambda s='SR12':get_profiler(s)))
            ),
        ('SR13',(wdir('grids/SR13.grid')
            ,(lambda s='SR13':get_profiler(s)))
            ),
        ('SR14',(wdir('grids/SR14.grid')
            ,(lambda s='SR14':get_profiler(s)))
            ),
        ('SR15',(wdir('grids/SR15.grid')
            ,(lambda s='SR15':get_profiler(s)))
            ),
        ('SR16',(wdir('grids/SR16.grid')
            ,(lambda s='SR16':get_profiler(s)))
            ),
        ('IDs',get_ids_grid),
        ('FEs',get_fes_grid),
    ])
    
    
import pickle
try: CABLING_TREE = pickle.load(open(wdir('etc/BO_VC_Connections.pck')))
except: CABLING_TREE = {}

def _get_exclude():
    exclude = ['sr16/vc/rga-01','sr16/vc/rga-tcp-01','bo/vc/ccg_profile']
    exclude += 'fe09/vc/vgct-bl,fe09/vc/ipct-bl,sr04/vc/daq-01,sr04/vc/plc-test'.split(',')
    exclude += ['sr%02d/vc/eps-plc-01-mbus'%i for i in range(1,17)]
    exclude += ['eps-plc-01-mbus']
    exclude += ['spbx-02a02-01']
    hosts = fandango.linos.ping(['alba04']+['ivc%02d01'%i for i in range(1,17)]+['ife%02d01'%j for j in (1,4,9,11,13,22,24,29,34)])
    for host,ping in hosts.items():
        if not ping:
            print 'Excluding %s host devices' % host
            exclude.extend([m for m in fandango.ServersDict(hosts=[host]).get_all_devices()])
    return [m.lower() for m in exclude]
        
EXCLUDE = _get_exclude()

def _get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    print 'Getting the device tree dictionary ...'
    import tau,fandango
    from vacca import cabling
    
    tree = cabling.get_tango_nodes(CABLING_TREE)
    tree['BO/VC/ALL'] = {
        'BO/VC/Alarms':{},
        'BO01/VC/ALL':{},'BO02/VC/ALL':{},'BO03/VC/ALL':{},'BO04/VC/ALL':{},
        'BO01/VC/PNV-01':{},'BO01/VC/PNV-02':{},
        'BO02/VC/PNV-01':{},'BO02/VC/PNV-02':{},
        'BO03/VC/PNV-01':{},
        'BO04/VC/PNV-01':{},'BO04/VC/PNV-02':{},'BO04/VC/PNV-03':{},
        'BO04/VC/PIR-05':{},'BO04/VC/IP-KICKER':{},
        }
    tree['BO/VC/ALL'].update(('SR%02d/VC/EPS-PLC-01'%s,{}) for s in (4,7,12,16))
    tree['LT/VC/ALL'] = {}
    tree['LT/VC/ALL'].update([('LT/VC/%s'%m.upper(),{}) for m in tau.Database().get_device_member('LT/VC/*') if m!='ALL' and m.lower() not in EXCLUDE])
    tree['LT/VC/ALL'].update([('LT01/VC/%s'%m.upper(),{}) for m in tau.Database().get_device_member('LT01/VC/*')  if m.lower() not in EXCLUDE])
    tree['LT/VC/ALL'].update([('LT02/VC/%s'%m.upper(),{}) for m in tau.Database().get_device_member('LT02/VC/*')  if m.lower() not in EXCLUDE])
    
    #Adding BT:
    tree['BT/VC/ALL'] = dict([('BT/VC/%s'%(m.upper()),{}) for m in tau.Database().get_device_member('BT/VC/*') if m!='ALL' and m.lower() not in EXCLUDE]+[('BT/VC/CCG-02',{})])
    #Adding Storage Ring sectors:
    tree['SR/VC/ALL'] = {'BO/DI/DCCT':{},'SR/DI/DCCT':{},'SR/MAIN/MACHINESTATUS':{},'SR/VC/ALARMS':{},'SR/VC/GAUGESPROFILE':{}}
    for i in range(1,17):
        tree['SR/VC/ALL']['SR%02d/VC/ALL'%i] = dict([('SR%02d/VC/%s'%(i,m.upper()),{}) for m in tau.Database().get_device_member('SR%02d/VC/*'%i) if m.lower()!='all' and m.lower() not in EXCLUDE])
    #Adding FrontEnds
    for i in (1,2,4,9,11,13,22,24,29,34):
        tree['FE%02d/VC/ALL'%i] = dict(
            [('FE%02d/VC/%s'%(i,m.upper()),{}) for m in tau.Database().get_device_member('FE%02d/VC/*'%i) if m!='ALL'  and m.lower() not in EXCLUDE]+
            [('FE%02d/EPS/%s'%(i,m.upper()),{}) for m in tau.Database().get_device_member('FE%02d/EPS/*'%i) if 'MBUS' not in m and m.lower() not in EXCLUDE]+
            [('FE/VC/ALARMS',{})]
            )
    for i in (04,11,13):
        tree['ID%02d/VC/ALL'%i] = dict(
            [('ID%02d/VC/%s'%(i,m.upper()),{}) for m in tau.Database().get_device_member('ID%02d/VC/*'%i) if m!='ALL'  and m.lower() not in EXCLUDE]+
            [('ID%02d/EPS/%s'%(i,m.upper()),{}) for m in tau.Database().get_device_member('ID%02d/EPS/*'%i) if 'MBUS' not in m and m.lower() not in EXCLUDE]+
            [('ID/CT/ALARMS',{})]
            )
            
    pops = [p for p in tree if p.lower() in EXCLUDE]
    [tree.pop(p) for p in pops]

    return tree
    
TREE=_get_default_tree()

#Not used anymore, replaced by COMPOSERS['PROFILE']
#PLOT = wdir('etc/PressuresProfile_BO.pck')

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
    'FE[^0-9]*':'FE/VC/ALL',
    'ID[^0-9]*':'ID/VC/ALL',
    }.items() if k not in EXCLUDE)

IMAGE_PROFILE = 'sr/vc/gaugesprofile/historicprofile'

def launch(script,args=[]):
    import os
    f = '%s %s &'%(script,' '.join(args))
    print 'launch(%s)'%f
    os.system(f)

def openWebpage(URL):
    """ launches konqueror """
    import subprocess
    subprocess.Popen(['konqueror',URL])
    
from vacca import valves

TOOLBAR = [
        ('','',None),
        #('Search',wdir('image/icons/search.png'),\
            #lambda: ui.tauDevTree.findInTree(str(QtGui.QInputDialog.getText(ui.tauDevTree,'Search ...','Write a part of the name',QtGui.QLineEdit.Normal)[0]))),
        #('','',None),
        #('LTB Gui',wdir('image/icons/cow_icon-LTB.png'),lambda:os.system('vacca_LTB &')),
        ('','',None),
        ('Archiving Viewer',wdir('image/icons/Mambo-icon.png'), lambda:launch('mambo')),
        ('','',None),
        ('Image Profile',
            wdir('image/icons/profile.png'), 
            lambda:launch('python -c "import vacca;vacca.image_profile.show(\'%s\');"'%str(IMAGE_PROFILE))
            ),
        ('','',None),
        ('RGA ProcessEye',wdir('image/equips/icon-rga.gif'), lambda:launch('rdesktop -g 1440x880 ctrga01')),
        ('','',None),
        ('EPS',wdir('image/equips/icon-eps.gif'), lambda:launch('alba_EPS')),
        ('','',None),
        ('Valves',wdir('image/equips/icon-pnv.gif'), lambda:valves.ValvesChooser().show()), #lambda:os.system('python %s &'%wdir('valves.py'))),
        ('','',None),
        ('Alarms',wdir('image/icons/panic.gif'), lambda:launch('ctalarms')),
        ('','',None),
        ('Snapshots',wdir('image/icons/Crystal_Clear_app_kedit.png'), lambda:os.system('ctsnaps')),
        ('','',None),
        ('Thermocouples',wdir('image/equips/icon-eps.gif'), lambda:launch('cttcs')),
        ('','',None),
        ('Logbook',QtGui.QIcon(wdir("image/icons/elog.png")),lambda:openWebpage(URL_LOGBOOK)),
        #
        #('Under Construction',QtGui.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),
        ]
    
_visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('LTB Gui',lambda:os.system('vacca_LTB &'),None),
        ('Jive',lambda:os.system('jive &'),None),
        ('Astor',lambda:os.system('astor &'),None),
        ('EPS Gui',lambda:os.system('alba_EPS &'),None),
        ('Valves',lambda:valves.ValvesChooser().show(),None),
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None),
        ]),
    ('Drawings',[
        ('Naming Booster',lambda:os.system('%s %s &'%(_visor,wdir('image/BoosterNaming.pdf'))),None), \
        ('Naming Storage Ring',lambda:os.system('%s %s &'%(_visor,wdir('image/StorageNaming.pdf'))),None), \
        ('Thermocouples Q1',lambda:os.system('%s %s &'%(_visor,wdir('image/TC_Q1.pdf'))),None), \
        ('Thermocouples Q2',lambda:os.system('%s %s &'%(_visor,wdir('image/TC_Q2.pdf'))),None), \
        ('Thermocouples Q3',lambda:os.system('%s %s &'%(_visor,wdir('image/TC_Q3.pdf'))),None), \
        ('Thermocouples Q4',lambda:os.system('%s %s &'%(_visor,wdir('image/TC_Q4.pdf'))),None), \
        ])
    ]
