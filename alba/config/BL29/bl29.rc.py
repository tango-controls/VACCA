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

#blrc = wdir('etc/bl.rc.py')
#from imp import load_source
#try: 
#    blconfig = load_source('blconfig',blrc)
#    from blconfig import *
#except Exception,e: 
#    print 'Errors in config files!'
#    print traceback.format_exc()

#Global variables are defined here
TITLE = 'VACCA: The VACuum Control Application for BL29-XMCD-Boreas'
LOG_LEVEL = 'WARNING'

URL_TRACKER = 'http://84.89.244.70:3000/projects/show/vaccabo'
URL_DEVELOPER = 'http://www.cells.es/Members/srubio'
URL_VACUUM = 'http://www.cells.es/Intranet/Divisions/Computing/Controls/Help/Vacuum/vacca_gui'
URL_HELP = wdir('doc/vacca_gui.html')

#------------------------------------------------------------------------------
## Default Values
#------------------------------------------------------------------------------
SYNOPTIC_WIDTH=1075
PLOT_HEIGHT=300
PANEL_WIDTH=450
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
DEVICE = 'BL29/VC/ALL'

import widgets
widgets.DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']
widgets.DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']

#-------------------------------------------------------------------

tg = None

def get_beamline_grid():
    import tau.widget.taugrid
    global tg
    tg = tau.widget.taugrid.TauGrid()
    tg.setRowLabels('VcGauges(mbar):VGCT, IonPumps(mbar):IPCT')
    tg.setColumnLabels(','.join((
        'DISET-EH:BL29/VC/IPCT-06/P2|BL29/VC/IPCT-06/State|BL29/VC/IPCT-07/P1|BL29/VC/IPCT-07/State|BL29/VC/VGCT-02/P2|BL29/VC/VGCT-02/P5|BL29/VC/VGCT-02/State|'+\
            'BL29/VC/VGCT-03/P2|BL29/VC/VGCT-04/P1',
        'MIR-EH:BL29/VC/IPCT-06/P1|BL29/VC/IPCT-06/State|BL29/VC/VGCT-03/P1|BL29/VC/VGCT-03/P4|BL29/VC/VGCT-03/State',
        'SLIEX-EH:BL29/VC/IPCT-05/P1|BL29/VC/IPCT-05/State|BL29/VC/VGCT-03/P5|BL29/VC/VGCT-03/State|BL29/VC/VGCT-04/CP2|BL29/VC/VGCT-04/P2|BL29/VC/VGCT-04/State',
        'SLIT-EH:BL29/VC/IPCT-04/P2|BL29/VC/IPCT-04/State',
        'MONO-EH:BL29/VC/IPCT-03/P2|BL29/VC/IPCT-03/State|BL29/VC/IPCT-04/P1|BL29/VC/IPCT-04/State|BL29/VC/VGCT-02/P1|BL29/VC/VGCT-02/P4|BL29/VC/VGCT-02/State',
        'IP75-EH:BL29/VC/IPCT-03/P1|BL29/VC/IPCT-03/State|BL29/VC/IPCT-05/P2|BL29/VC/IPCT-05/State',
        'SLIE-OH:BL29/VC/IPCT-02/P2|BL29/VC/IPCT-02/State|BL29/VC/VGCT-01/P2|BL29/VC/VGCT-01/P5|BL29/VC/VGCT-01/State',
        'IP200-OH:BL29/VC/IPCT-02/P1|BL29/VC/IPCT-02/State',
        'MIR-OH:BL29/VC/IPCT-01/P2|BL29/VC/IPCT-01/State|BL29/VC/VGCT-01/P1|BL29/VC/VGCT-01/P4|BL29/VC/VGCT-01/State',
        'DISET-OH:BL29/VC/IPCT-01/P1|BL29/VC/IPCT-01/State',
        'TRU-F29:FE29/VC/IPCT-01/P1|FE29/VC/IPCT-01/State|FE29/VC/VGCT-01/P1|FE29/VC/VGCT-01/P4|FE29/VC/VGCT-01/State',
        )))    
    #tg.setColumnLabels(','.join([
        #'DISET-EH:(BL29/VC/IPCT-06/P2|BL29/VC/IPCT-07/P1|BL29/VC/VGCT-02/P2|BL29/VC/VGCT-02/P5|'+\
            #'BL29/VC/VGCT-03/P2|BL29/VC/VGCT-04/P1)',
        #'MIR-EH:(BL29/VC/IPCT-06/P1|BL29/VC/VGCT-03/P1|BL29/VC/VGCT-03/P4)',
        #'SLIEX-EH:(BL29/VC/IPCT-05/P1|BL29/VC/VGCT-04/P2)',
        #'SLIT-EH:(BL29/VC/IPCT-04/P2)',
        #'MONO-EH:(BL29/VC/IPCT-03/P2|BL29/VC/IPCT-04/P1|BL29/VC/VGCT-02/P1|BL29/VC/VGCT-02/P4)',
        #'IP75-EH:(BL29/VC/IPCT-03/P1|BL29/VC/IPCT-05/P2)',
        #'SLIE-OH:(BL29/VC/IPCT-02/P2|BL29/VC/VGCT-01/P2|BL29/VC/VGCT-01/P5)',
        #'IP200-OH:(BL29/VC/IPCT-02/P1)',
        #'MIR-OH:(BL29/VC/IPCT-01/P2|BL29/VC/VGCT-01/P1|BL29/VC/VGCT-01/P4)',
        #'DISET-OH:(BL29/VC/IPCT-01/P1)',
        #'TRU-F29:(FE29/VC/IPCT-01/P1|FE29/VC/VGCT-01/P1|FE29/VC/VGCT-01/P4)',
        #]))        
    #tg.load(wdir('BL29/bl29.grid'))
    tg.showRowFrame(False)
    tg.showColumnFrame(False)
    tg.setModel('*/VC/(IPCT|VGCT)*/(P[12]|State)')
    return tg

def POST_HOOK(ui):
    print 'In bl29.rc.py POST_HOOK method ...'
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
       #('BOREAS',get_beamline_grid),
       #('BOREAS',(wdir('BL29/BL29.jdw'),get_beamline_grid)),
       ('BOREAS',(
            (wdir('BL29/BL29.jdw')),
            get_beamline_grid,
            )),
       #('mbar',wdir('grids/bl29.grid')),
    ])
    
#-------------------------------------------------------------------

def get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    print 'Getting the device tree dictionary ...'
    import cabling,tau
    tree = {}
    #families = '(CCG|PIR|FCV|VGCT|IP|IPCT|TSP|SPBX|PNV|OTR|FS-|VFCS)'
    families = '(VGCT|IPCT|PNV|EPS)'
    for i in (29,): #1,2,4,9,11,13,22,24,29,34):
        tree['BL%02d/VC/ALL'%i] = dict((d.upper(),{}) for d in get_matching_devices('BL%02d/*/%s*'%(i,families)) if d.split('/')[-1]!='ALL')
    for dev in tau.Database().get_device_member('FE29/VC/*'): 
        tree['BL29/VC/ALL']['FE29/VC/%s'%dev]={}
    tree['BL29/VC/ALL']['BL29/CT/EPS-PLC-01']={}
    tree['BL29/VC/ALL']['BL29/CT/EPS-PLC-01-MBUS']={}
    tree['BL29/VC/ALL']['BL29/CT/ALARMS']={}
    return tree

TREE=get_default_tree()

## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = {
    'PROFILE':'BL29/VC/ALL',
    'BL29*':'BL29/VC/ALL',
    }
    
#-------------------------------------------------------------------

IMAGE_PROFILE = 'blxx/vc/profile/historicprofile'

def launch(script,args=[]):
    import os
    f = '%s %s &'%(script,' '.join(args))
    print 'launch(%s)'%f
    os.system(f)

TOOLBAR = [
        ('','',None),
        ('Archiving Viewer',wdir('image/icons/Mambo-icon.png'), lambda:launch('mambo')),
        ('','',None),
        ('EPS',wdir('image/equips/icon-eps.gif'), lambda:launch('epsGUI')),
        ('','',None),
        ('Alarms',wdir('image/icons/panic.gif'), lambda:launch('ctalarms')),
        ('','',None),
        ('Snapshots',wdir('image/icons/Crystal_Clear_app_kedit.png'), lambda:os.system('ctsnaps')),
        ('','',None),
        #('Image Profile',
        #    wdir('image/icons/profile.png'), 
        #    lambda:launch('python /homelocal/sicilia/lib/python/site-packages/taurus/qt/extra_guiqwt/image.py',[IMAGE_PROFILE])
        #    ),
        #('','',None),
        #('RGA ProcessEye',wdir('image/equips/icon-rga.gif'), lambda:launch('rdesktop -g 1440x880 ctrga01')),
        #('','',None),
        #('Under Construction',QtGui.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),
        ]
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('EPS Gui',lambda:os.system('epsGUI &'),None), \            
        ('Jive',lambda:os.system('jive &'),None), \
        ('Astor',lambda:os.system('astor &'),None), \
        ('Mambo',lambda:os.system('mambo &'),None), \
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None), \
        ('Archiving Webserver',lambda:os.system('konqueror ctbl29arch01 &'),None), \
        ]),
    ]
