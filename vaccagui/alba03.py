import imp,fandango,os
from taurus.qt import Qt
from fandango import SortedDict
import vacca.utils

import SR
from SR.sector import SYNOPTICS,COMPOSERS,\
    get_ids_grid,get_fes_grid,get_profiler,get_sectors_toolbar,\
    forward2device,forward2composer

from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath

from vacca.default import *

WDIR = WORKING_DIR

DOMAIN = 'SR'
GAUGES = ['sr/di/dcct/averagecurrent','sr/vc/all/averagepressure','sr/vc/all/ipsaveragepressure'] #fandango.get_matching_attributes(('%s/*/vgct*/p[12]'%DOMAIN.replace('BL','(BL|FE|ID)')))
JDRAW_FILE = wdir('SR/jdw/ALBA_ESH.jdw')
from taurus.qt.qtgui.graphic import TaurusGraphicsScene
TaurusGraphicsScene.ANY_ATTRIBUTE_SELECTS_DEVICE = False
TaurusGraphicsScene.TRACE_ALL = True
JDRAW_TREE = False
JDRAW_HOOK = lambda s: forward2device(s) if (s.count('/')-s.count(':'))>2 else (forward2composer(s) if 'ALL' not in s else s)

#The device that will be shown by default when loading the application
COMPOSER = DEVICE = 'SR/VC/ALL'
from taurus.qt.qtgui.tree import TaurusDevTree
TaurusDevTree.TRACE_ALL = True

EXTRA_DEVICES = [d for d in 
    fandango.get_matching_devices('*/(vc|eps|ct)/*(all|alarm|composer|elotech|vgct|ipct|spbx|ccg|pir|pnv|ip-|rga|plc-01$|plc-01$)*')
    if 'dserver' not in d.lower()]
        
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

#DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']
#DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']

#Examples of Attribute filters to be applied to DevicePanel
try:
  from config.filters import *
except:
  try:
    from filters import *
    from vacca.filters import *
  except:
    print 'UNABLE TO LOAD filters.py!'
    
GRID = {}
#GRID = {
    #'column_labels': 
        #','.join((
        #'DISET-EH:BL29/VC/IPCT-06/P2|BL29/VC/IPCT-06/State|BL29/VC/IPCT-07/P1|BL29/VC/IPCT-07/State|BL29/VC/VGCT-02/P2|BL29/VC/VGCT-02/P5|BL29/VC/VGCT-02/State|'+\
            #'BL29/VC/VGCT-03/P2|BL29/VC/VGCT-04/P1',
        #'MIR-EH:BL29/VC/IPCT-06/P1|BL29/VC/IPCT-06/State|BL29/VC/VGCT-03/P1|BL29/VC/VGCT-03/P4|BL29/VC/VGCT-03/State',
        #'SLIEX-EH:BL29/VC/IPCT-05/P1|BL29/VC/IPCT-05/State|BL29/VC/VGCT-03/P5|BL29/VC/VGCT-03/State|BL29/VC/VGCT-04/CP2|BL29/VC/VGCT-04/P2|BL29/VC/VGCT-04/State',
        #'SLIT-EH:BL29/VC/IPCT-04/P2|BL29/VC/IPCT-04/State',
        #'MONO-EH:BL29/VC/IPCT-03/P2|BL29/VC/IPCT-03/State|BL29/VC/IPCT-04/P1|BL29/VC/IPCT-04/State|BL29/VC/VGCT-02/P1|BL29/VC/VGCT-02/P4|BL29/VC/VGCT-02/State',
        #'IP75-EH:BL29/VC/IPCT-03/P1|BL29/VC/IPCT-03/State|BL29/VC/IPCT-05/P2|BL29/VC/IPCT-05/State',
        #'SLIE-OH:BL29/VC/IPCT-02/P2|BL29/VC/IPCT-02/State|BL29/VC/VGCT-01/P2|BL29/VC/VGCT-01/P5|BL29/VC/VGCT-01/State',
        #'IP200-OH:BL29/VC/IPCT-02/P1|BL29/VC/IPCT-02/State',
        #'MIR-OH:BL29/VC/IPCT-01/P2|BL29/VC/IPCT-01/State|BL29/VC/VGCT-01/P1|BL29/VC/VGCT-01/P4|BL29/VC/VGCT-01/State',
        #'DISET-OH:BL29/VC/IPCT-01/P1|BL29/VC/IPCT-01/State',
        #'TRU-F29:FE29/VC/IPCT-01/P1|FE29/VC/IPCT-01/State|FE29/VC/VGCT-01/P1|FE29/VC/VGCT-01/P4|FE29/VC/VGCT-01/State',
        #)),
    #'delayed': False,
    #'frames': False,
    #'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
    #'row_labels':'VcGauges(mbar):VGCT, IonPumps(mbar):IPCT',
    #}
    
TOOLBARS = [
    ('Sectors','SR.sector.get_sectors_toolbar')
    ]
    
###EXTRA_APPS = fandango.dicts.SortedDict()
EXTRA_APPS['Fandango'] = {'name':'QEval',
                'class':fandango.qt.QEvaluator,
                'icon':':apps/accessories-calculator.svg'}

EXTRA_TOOLS+=[
    ('Mambo',['mambo'],wdir('image/icons/Mambo-icon.png')),
    ('RGAs',['ctrga01'],wdir('image/equips/icon-rga.gif')),
    ('EPS',['alba_EPS'],wdir('image/equips/icon-eps.gif')),
    ('Snaps',['ctsnaps'],wdir('image/icons/Crystal_Clear_app_kedit.png')),
    ]
    
OLD_APPS = {
    #'xrga':{'name':'RGA','classname':'vacca.panel.VaccaAction',
            #'model':['RGA',wdir('image/equips/icon-rga.gif')]+' ctrga01'.split()},
    #'xtrend':{'name':'NewTrend','classname':'vacca.panel.VaccaAction',
              #'model':['Trend',wdir('image/icons/Mambo-icon.png')]+'taurustrend -a'.split()},
    #'xvalves':{'name':'Valves','classname':'vacca.panel.VaccaAction',
               #'model':['Valves',wdir('image/equips/icon-pnv.gif')]+'ctvalves'.split()},
    #'xtcs':{'name':'Thermocouples','classname':'vacca.panel.VaccaAction',
            #'model':['Thermocouples',wdir('image/equips/icon-eps.gif')]+'cttcs'.split()},
    }
for k,v in OLD_APPS.items():
    v['class'] = v['classname']
    v['icon'] = v['model'][1]
    EXTRA_APPS[v['name']] = v
    
try:
    from fandango.qt import QEvaluator
    EXTRA_WIDGETS = [
        ('fandango.qt.QEvaluator',wdir('image/icons/panic.gif')),
        ]
except:
    traceback.print_exc()

## ALL THIS LAUNCHERS SHOULD BE MIGRATED (or not) TO BE EXTRA_APPS
TOOLBAR = [
        ('','',None),
        #('Search',wdir('image/icons/search.png'),\
            #lambda: ui.tauDevTree.findInTree(str(Qt.QInputDialog.getText(ui.tauDevTree,'Search ...','Write a part of the name',Qt.QLineEdit.Normal)[0]))),
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
        ('RGA ProcessEye',wdir('image/equips/icon-rga.gif'), lambda:launch('ctrga01')),
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
        ('Logbook',Qt.QIcon(wdir("image/icons/elog.png")),lambda:openWebpage(URL_LOGBOOK)),
        #
        #('Under Construction',Qt.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),
        ]
 
_visor = 'kpdf'
MENUS = [
    #('Tools',[
        #('LTB Gui',lambda:os.system('vacca_LTB &'),None),
        #('Jive',lambda:os.system('jive &'),None),
        #('Astor',lambda:os.system('astor &'),None),
        #('EPS Gui',lambda:os.system('alba_EPS &'),None),
        #('Valves',lambda:valves.ValvesChooser().show(),None),
        #('TaurusTrend',lambda:os.system('taurustrend -a &'),None),
        #]),
    ('Drawings',[
        ('Naming Booster',lambda:os.system('%s %s &'%(_visor,wdir('SR/image/BoosterNaming.pdf'))),None), \
        ('Naming Storage Ring',lambda:os.system('%s %s &'%(_visor,wdir('SR/image/StorageNaming.pdf'))),None), \
        ('Thermocouples Q1',lambda:os.system('%s %s &'%(_visor,wdir('SR/image/TC_Q1.pdf'))),None), \
        ('Thermocouples Q2',lambda:os.system('%s %s &'%(_visor,wdir('SR/image/TC_Q2.pdf'))),None), \
        ('Thermocouples Q3',lambda:os.system('%s %s &'%(_visor,wdir('SR/image/TC_Q3.pdf'))),None), \
        ('Thermocouples Q4',lambda:os.system('%s %s &'%(_visor,wdir('SR/image/TC_Q4.pdf'))),None), \
        ])
    ]

# THIS METHOD IS NOT USED YET BUT WILL BE NEEDED 
def getNodeAdmin(node):
    """
    tree = TaurusDevTree()
    device = .../IP-... or .../CCG-...
    controller = .../IPCT- or /SPBX or /VGCT
    """
    name = ''
    try:
        import PyTango
        tree = node.parentTree
        name = tree.getNodeDeviceName(node)+'/Controller'
        return str(PyTango.AttributeProxy(name).read().value)
    except:
        print 'Unable to get %s'%name
        import traceback
        print traceback.format_exc()
        return None
TaurusDevTree.getNodeAdmin = staticmethod(getNodeAdmin)
