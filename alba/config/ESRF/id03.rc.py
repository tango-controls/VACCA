import os,sys,traceback
from fandango.dicts import SortedDict
from fandango.device import get_database,get_matching_devices
from include import wdir,Qt

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

#blrc = wdir('etc/bl.rc.py')
#from imp import load_source
#try: 
#    blconfig = load_source('blconfig',blrc)
#    from blconfig import *
#except Exception,e: 
#    print 'Errors in config files!'
#    print traceback.format_exc()

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
SYNOPTICS = {} #{'Name':'.jdw/.grid'} #This dictionary defines the synoptic for each domain
TREE = {} #{'topnode':{'branch':{'endnode':{}}}} #'pickle file' #Dictionary with all device tree nodes
COMPOSERS = {'PROFILE':''} #{'PROFILE':'SR/VC/ALL','*/*/*':'SR/VC/ALL'} # Assigns composer for PROFILE and each subdomain
DEVICE = '' #'sys/tg_test/1' #The device that will be shown by default when loading the application
TOOLBAR = [] #[('','',None)] #Name,icon,action tuples
MENUS = [] #[('',[('',None,None)])] #Name, Submenu((Name,Action,Icon tuples))
POST_HOOK = None #Method called at the end of application initialization
DEVICE = '' #The device that will be shown by default when loading the application
EXCLUDE = []
DEV_ATTRS = {}
DEV_COMMS = {}
#------------------------------------------------------------------------------

###############################################################################
# Edit whatever you want below this lines
###############################################################################

#The device that will be shown by default when loading the application
#DEVICE = 'sys/tg_test/1'

DEV_ATTRS['EPS']=['.*_PT.*','.*_READY','OPEN_','CLOSE_','was_','paas_']
DEV_ATTRS['EPS-PLC']=DEV_ATTRS['EPS']

#-------------------------------------------------------------------

tg = None

def get_beamline_grid():
    import tau.widget.taugrid
    global tg
    #Grid generated with: generate_grids.get_bl_grid_from_ccdb('bl22.grid',CCDB.ccdbAPI,generate_grids.bl22_translate)
    grid = {
        'column_labels': 'BSH,PEN,PIR,RV,VARIP',
        'delayed': False,
        'frames': False,
        'model': 'ID03/*/*/(Pressure|State)$',
        'row_labels': 'mbar:.*'
        }    
    tg = tau.widget.taugrid.TauGrid()
    tg.setRowLabels(grid['row_labels'])
    tg.setColumnLabels(grid['column_labels'])    
    tg.setModel(grid['model'])
    tg.showRowFrame(False)
    tg.showColumnFrame(False)
    return tg

def POST_HOOK(ui):
    print 'In empty.rc.py POST_HOOK method ...'
    try:
        #Disabling TauGrid labels/units
        global tg
        if tg:
            tg.showAttributeLabels(False)
            tg.showAttributeUnits(False)
    except:
        print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       ('ID03',wdir('ESRF/id03.jdw')),
       #('GRID',get_beamline_grid),
    ])

#-------------------------------------------------------------------

import pickle
CABLING_TREE = {} #pickle.load(open(wdir('etc/BO_VC_Connections.pck')))

def get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    print 'Getting the device tree dictionary ...'
    tree = {}
    families = 'BSH,PEN,PIR,RV,VARIP'.split(',')
    tree = {'ID03':dict((f,dict((d,{}) for d in get_matching_devices('ID03/v-%s/*'))) for f in families)}
    return tree
    
TREE=get_default_tree()

## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = {
    #'PROFILE':'BLXX/VC/ALL',
    #'BLXX*':'BLXX/VC/ALL',
    }

#-------------------------------------------------------------------

IMAGE_PROFILE = 'blxx/vc/profile/historicprofile'

def launch(script,args=[]):
    import os
    f = '%s %s &'%(script,' '.join(args))
    print 'launch(%s)'%f
    os.system(f)

def openWebpage(URL):
    """ launches konqueror """
    import subprocess
    subprocess.Popen(['konqueror',URL])


TOOLBAR = [
        ('','',None),
        ('Archiving Viewer',wdir('image/icons/Mambo-icon.png'), lambda:launch('mambo')),
        ('','',None),
        ('EPS',wdir('image/equips/icon-eps.gif'), lambda:launch('epsGUI')),
        ('','',None),
        ('Alarms',wdir('image/icons/panic.gif'), lambda:launch('ctalarms')),
        ('','',None),
        ('Snapshots',wdir('image/icons/Crystal_Clear_app_kedit.png'), lambda:os.system('ctsnaps')),
        #('','',None),
        #('Valves List',wdir('image/equips/icon-pnv.gif'), lambda:valves.ValvesChooser(domains=['BL22']).show()), #lambda:os.system('python %s &'%wdir('valves.py'))),
        #('','',None),        
        #('Image Profile',
        #    wdir('image/icons/profile.png'), 
        #    lambda:launch('python /homelocal/sicilia/lib/python/site-packages/taurus/qt/extra_guiqwt/image.py',[IMAGE_PROFILE])
        #    ),
        ('','',None),
        ('Logbook',Qt.QIcon(wdir("image/icons/elog.png")),lambda:openWebpage(URL_LOGBOOK)),
        ('','',None),
        ('TaurusTrend','',lambda:os.system('taurustrend -a &'),), \
        #('','',None),
        #('RGA ProcessEye',wdir('image/equips/icon-rga.gif'), lambda:launch('rdesktop -g 1440x880 ctrga01')),
        #
        #('Under Construction',Qt.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),
        ]
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('Jive',lambda:os.system('jive &'),None), \
        ('Astor',lambda:os.system('astor &'),None), \
        ('EPS Gui',lambda:os.system('epsGUI &'),None), \
        ('Mambo',lambda:os.system('mambo &'),None), \
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None), \
        #('Archiving Webserver',lambda:os.system('konqueror ctbl22arch01 &'),None), \        
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
