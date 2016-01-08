import os,sys
from fandango.dicts import SortedDict
from include import wdir

"""
Default Configuration file for VACCA

Variables to be configured:
    TITLE,LOG_LEVEL,
    URL_REDMINE,URL_DEVELOPER,URL_VACUUM,URL_HELP,
    SYNOPTICS,PLOT,TREE,COMPOSERS
"""


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

#------------------------------------------------------------------------------
## Default Values
#------------------------------------------------------------------------------
SYNOPTIC_WIDTH=1075
PLOT_HEIGHT=350
SYNOPTICS = {} #{'Name':'.jdw/.grid'} #This dictionary defines the synoptic for each domain
TREE = {} #{'topnode':{'branch':{'endnode':{}}}} #'pickle file' #Dictionary with all device tree nodes
COMPOSERS = {'PROFILE':''} #{'PROFILE':'SR/VC/ALL','*/*/*':'SR/VC/ALL'} # Assigns composer for PROFILE and each subdomain
DEVICE = '' #'sys/tg_test/1' #The device that will be shown by default when loading the application
TOOLBAR = [] #[('','',None)] #Name,icon,action tuples
MENUS = [] #[('',[('',None,None)])] #Name, Submenu((Name,Action,Icon tuples))
POST_HOOK = None #Method called at the end of application initialization
#------------------------------------------------------------------------------

###############################################################################
# Edit whatever you want below this lines
###############################################################################

#The device that will be shown by default when loading the application
#DEVICE = 'sys/tg_test/1'

import widgets
widgets.DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_']
widgets.DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_']

#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
#       ('Default',wdir('jdw/default.jdw')),
    ])
    
def POST_HOOK(ui):
    print 'In empty.rc.py POST_HOOK method ...'
    try:
        #Disabling TauGrid labels/units
        global tg
        tg.showAttributeLabels(False)
        tg.showAttributeUnits(False)
    except:
        print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
import pickle
CABLING_TREE = {} #pickle.load(open(wdir('etc/BO_VC_Connections.pck')))

def get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    return {}
    
TREE=get_default_tree()

#-------------------------------------------------------------------

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
        ('12hours Profile',wdir('image/icons/clock.png'), lambda:os.system('python /homelocal/sicilia/lib/python/site-packages/taurus/qt/extra_guiqwt/image.py bl04/vc/profile/historicprofile &'))),
        ('','',None),
        #('Under Construction',QtGui.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),
        ]
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
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
