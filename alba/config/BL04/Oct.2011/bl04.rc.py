import os,sys,traceback
from fandango.dicts import SortedDict
from fandango.device import get_matching_devices
from include import wdir

"""
Configuration file for Storage Ring Vacuum Application

Variables to be configured:
    TITLE,LOG_LEVEL,
    URL_REDMINE,URL_DEVELOPER,URL_VACUUM,URL_HELP,
    SYNOPTICS,PLOT,TREE,COMPOSERS,DEVICE,
    POST_HOOK
"""

#print 'Uncomment these lines to force application folder if needed'
#os.chdir('/homelocal/sicilia/applications/vacca')
#sys.path.insert(2,'/homelocal/sicilia/applications/vacca')

#Global variables are defined here
TITLE = 'VACCA: The VACuum Control Application for BL04-MSPD'
LOG_LEVEL = 'WARNING'

URL_TRACKER = 'http://84.89.244.70:3000/projects/show/vaccabo'
URL_DEVELOPER = 'http://www.cells.es/Members/srubio'
URL_VACUUM = 'http://www.cells.es/Intranet/Divisions/Computing/Controls/Help/Vacuum/vacca_gui'
URL_HELP = wdir('doc/vacca_gui.html')

#------------------------------------------------------------------------------
## Default Values
#------------------------------------------------------------------------------
SYNOPTIC_WIDTH=1075
PLOT_HEIGHT=350
SYNOPTICS = {'Name':'.jdw/.grid'}
TREE = '' #pickle file
COMPOSERS = {'PROFILE':'SR/VC/ALL','*/*/*':'SR/VC/ALL'} # Assigns composer for PROFILE and each subdomain
TOOLBAR = [('','',None)] #Name,icon,action tuples
MENUS = [('',[('',None,None)])] #Name, Submenu((Name,Action,Icon tuples))
POST_HOOK = None #A function to be called once initialization has finished
DEVICE = '' #The device that will be shown by default when loading the application
EXCLUDE = []
#------------------------------------------------------------------------------

###############################################################################
# Edit whatever you want below this lines
###############################################################################

#The device that will be shown by default when loading the application
DEVICE = 'BL04/VC/ALL'

import widgets
widgets.DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_']
widgets.DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_']

tg = None

def get_MSPD_grid():
    import tau.widget.taugrid
    global tg
    tg = tau.widget.taugrid.TauGrid()
    tg.setRowLabels('VcGauges(mbar):VGCT, IonPumps(mbar):IPCT')
    
    #VGCT
    #fe04-01 : TU
    #bl1: filter, wbatt
    #bl2: mono, m1
    #bl3: ph shutt, ?
    
    #ipct
    #fe: TU
    #bl1: wbatt, filter
    #bl2: m1, mask
    #bl3: fluo1, mono
    
    tg.setColumnLabels(','.join(
        [
        'PH-SHUTTER:BL04/VC/VGCT-03/P1|BL04/VC/IPCT-04/P2',
	'2nd-COLL:BL04/VC/IPCT-04/P1',
        'MONO:BL04/VC/VGCT-02/P1|BL04/VC/IPCT-03/P2',
        'FLUO1:BL04/VC/IPCT-03/P1',
        '6w-BLVS:BL04/VC/VGCT-03/P2|BL04/VC/IPCT-02/P2',
        'MIRROR:BL04/VC/VGCT-02/P2|BL04/VC/IPCT-02/P1',
	'WBATT:BL04/VC/VGCT-01/P2|BL04/VC/IPCT-01/P1',
        'FILTER:BL04/VC/VGCT-01/P1|BL04/VC/IPCT-01/P2',        
        'FE:FE04/VC/(VGCT-01/P1|IPCT-01/P1)']
        ))
    tg.showRowFrame(False)
    tg.showColumnFrame(False)
    tg.setModel('(BL04|FE04)/VC/(VG|IP)CT-*/(P[12])')
    return tg

def POST_HOOK(ui):
    print 'In bl04.rc.py POST_HOOK method ...'
    try:
        #Disabling TauGrid labels/units
        global tg
        tg.showAttributeLabels(False)
        tg.showAttributeUnits(False)
    except:
        print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       ('ALL',(wdir('BL04/BL04.jdw'),get_MSPD_grid)),
       #('mbar',wdir('grids/bl04.grid')),
    ])

def get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    print 'Getting the device tree dictionary ...'
    import cabling,tau
    tree = {}
    families = '(CCG|PIR|FCV|VGCT|IP|IPCT|TSP|SPBX|PNV|OTR|FS-|VFCS)'
    for i in (4,): #1,2,4,9,11,13,22,24,29,34):
        tree['BL%02d/VC/ALL'%i] = dict((d.upper(),{}) for d in get_matching_devices('BL%02d/*/%s*'%(i,families)) if d.split('/')[-1]!='ALL')
    for dev in tau.Database().get_device_member('FE04/VC/*'): 
        tree['BL04/VC/ALL']['FE04/VC/%s'%dev]={}
    tree['BL04/VC/ALL']['BL04/CT/EPS-PLC-01']={}
    tree['BL04/VC/ALL']['BL04/CT/EPS-PLC-01-MBUS']={}
    tree['BL04/VC/ALL']['BL04/CT/ALARMS']={}
    return tree

TREE=get_default_tree()

## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = {
    'PROFILE':'BL04/VC/ALL',
    'BL04*':'BL04/VC/ALL',
    }
    
TOOLBAR = [
        ('','',None),
        ('Archiving Viewer',wdir('image/icons/Mambo-icon.png'), lambda:os.system('mambo &')),
        #('','',None),
        #('RGA ProcessEye',wdir('image/equips/icon-rga.gif'), lambda:os.system('rdesktop -g 1440x880 ctrga01 &')),
        ('','',None),
        ('EPS',wdir('image/equips/icon-eps.gif'), lambda:os.system('epsGUI &')),
        ('','',None),
        ('Alarms',wdir('image/icons/panic.gif'), lambda:os.system('ctalarms&')),
        ('','',None),
        ('Snapshots',wdir('image/icons/Crystal_Clear_app_kedit.png'), lambda:os.system('ctsnaps &')),
        ('','',None),
        ('12hours Profile',
            wdir('image/icons/clock.png'), 
            lambda:os.system('python /homelocal/sicilia/lib/python/site-packages/taurus/qt/extra_guiqwt/image.py bl04/vc/profile/historicprofile &')
            ),
        ('','',None),
        #('Under Construction',QtGui.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),
        ]
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('LTB Gui',lambda:os.system('vacca_LTB &'),None), \
        ('Jive',lambda:os.system('jive &'),None), \
        ('Astor',lambda:os.system('astor &'),None), \
        ('EPS Gui',lambda:os.system('epsGUI &'),None), \
        ]),
    #('Drawings',[
        #('Naming Booster',lambda:os.system('%s %s &'%(visor,wdir('image/BoosterNaming.pdf'))),None), \
        #('Naming Storage Ring',lambda:os.system('%s %s &'%(visor,wdir('image/StorageNaming.pdf'))),None), \
        #('Thermocouples Q1',lambda:os.system('%s %s &'%(visor,wdir('image/TC_Q1.pdf'))),None), \
        #('Thermocouples Q2',lambda:os.system('%s %s &'%(visor,wdir('image/TC_Q2.pdf'))),None), \
        #('Thermocouples Q3',lambda:os.system('%s %s &'%(visor,wdir('image/TC_Q3.pdf'))),None), \
        #('Thermocouples Q4',lambda:os.system('%s %s &'%(visor,wdir('image/TC_Q4.pdf'))),None), \
        #])
    ]
