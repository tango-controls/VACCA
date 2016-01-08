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
TITLE = 'VACCA: The VACuum Control Application for ID11'
LOG_LEVEL = 'WARNING'
FAST_MODE = True
URL_TRACKER = 'http://84.89.244.70:3000/projects/show/vaccabo'
URL_DEVELOPER = 'http://www.cells.es/Members/srubio'
URL_VACUUM = 'http://www.cells.es/Intranet/Divisions/Computing/Controls/Help/Vacuum/vacca_gui'
URL_HELP = wdir('doc/vacca_gui.html')

#------------------------------------------------------------------------------
## Default Values
#------------------------------------------------------------------------------
SYNOPTIC_WIDTH=750
PLOT_HEIGHT=400
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
DEVICE = 'ID11/EPS/PLC-01'

import widgets
plc_attrs = ['CpuStatus','PLC_Config_Status','.*BK.*','CC.*VAL','RGA_.*',
            '_READY','OPEN_','CLOSE_',
            'THERMOCOUPLES','PT1000','.*_T[0-9]+$','.*_VAL']
widgets.DEV_ATTRS['PLC']=plc_attrs
widgets.DEV_ATTRS['ELOTECH']=['Output_[0-9]$','Temperature_[0-9]$']

def get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    print 'Getting the device tree dictionary ...'
    import cabling,tau
    tree = {}
    #families = '(CCG|PIR|FCV|VGCT|IP|IPCT|TSP|SPBX|PNV|OTR|FS-|VFCS)'
    families = '(VGCT|IPCT|PNV|EPS|PLC|MBUS|PNV|CCG|Elotech|PIR|IP)'
    composer = 'ID11/CT/ALARMS'
    tree[composer] = dict((d.upper(),{}) for d in get_matching_devices('ID11/*/%s*'%(families)) if d.split('/')[-1]!='ALL')
    tree[composer]['lab/vc/vgct-01'.upper()] = {}
    #tree[composer]['BL%02d/CT/EPS-PLC-01'%NBL]={}
    #tree[composer]['BL%02d/CT/EPS-PLC-01-MBUS'%NBL]={}
    #tree[composer]['BL%02d/CT/ALARMS'%NBL]={}
    return tree

TREE=get_default_tree()

## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = {
    'PROFILE':'',
    }
    
TOOLBAR = [
        ('','',None),
        ('Archiving Viewer',wdir('image/icons/Mambo-icon.png'), lambda:os.system('mambo &')),
        ('','',None),
        ('EPS',wdir('image/equips/icon-eps.gif'), lambda:os.system('epsGUI_ID11 &')),
        ('','',None),
        ('BakeOut',wdir('image/equips/icon-vgct.gif'), lambda:os.system('BakeOutProgrammer &')),
        ('','',None),        
        ]
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('EPS Gui',lambda:os.system('epsGUI_ID11 &'),None), \
        ('Jive',lambda:os.system('jive &'),None), \
        ('Astor',lambda:os.system('astor &'),None), \
        ('Mambo',lambda:os.system('mambo &'),None), \
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None), \
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
