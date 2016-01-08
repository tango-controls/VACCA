import os,sys,traceback
from fandango.dicts import SortedDict
from fandango.device import get_matching_devices
from include import wdir
from PyQt4 import Qt

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
NBL = 11
TITLE = 'VACCA: The VACuum Control Application for BL%02d' % NBL
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
PANEL_WIDTH=450
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

#The device that will be shown by default when loading the application
DEVICE = 'BL%02d/VC/ALL'%NBL

import widgets
widgets.DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']
widgets.DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']

#-------------------------------------------------------------------

tg1 = None
def get_beamline_grid():
    import tau.widget.taugrid
    global tg1
    tg1 = tau.widget.taugrid.TauGrid()
    #tg.load(wdir('BL%02d/bl%02d.grid'%(NBL,NBL)))
    tg1.setRowLabels('VcGauges(mbar):VGCT, IonPumps(mbar):IPCT')
    #['Vacuum ctrl station 3: (bl11/vc/vgct-04/(P2|State))',
    #'Vacuum ctrl station 2: (bl11/vc/vgct-04/(P1|State))|(bl11/vc/ipct-05/(P2|State))',
    #'Photon Shutter: (bl11/vc/vgct-03/(P2|State))|(bl11/vc/ipct-05/(P1|State))',
    #'Differential Pump 2: (bl11/vc/vgct-03/(P1|State))|(bl11/vc/ipct-04/(P2|State))',
    #'Mirrors: (bl11/vc/vgct-02/(P2|State))|(bl11/vc/ipct-04/(P1|State))',
    #'Differential Pump 1: (bl11/vc/vgct-02/(P1|State))|(bl11/vc/ipct-03/(P2|State))',
    #'Attenuators: (bl11/vc/ipct-03/(P1|State))',
    #'DCM: (bl11/vc/vgct-01/(P2|State))|(bl11/vc/ipct-02/(P2|State))',
    #'Pumping Station 2: (bl11/vc/ipct-02/(P1|State))',
    #'Fixed Mask: (bl11/vc/ipct-01/(P2|State))',
    #'Pumping station 1: (bl11/vc/ipct-01/(P1|State))',
    #'Vacuum ctrl station 1: (bl11/vc/vgct-01/(P1|State))',
    #'Trigger Unit: (fe11/vc/vgct-01/(P1|State))|(fe11/vc/ipct-01/(P1|State))']
    tg1.setColumnLabels(','.join([
        'BLVS-3: (bl11/vc/vgct-04/(P2|State))',
        'BLVS-2: (bl11/vc/vgct-04/(P1|State))|(bl11/vc/ipct-05/(P2|State))',
        'PSH: (bl11/vc/vgct-03/(P2|State))|(bl11/vc/ipct-05/(P1|State))',
        'DIFF-2: (bl11/vc/vgct-03/(P1|State))|(bl11/vc/ipct-04/(P2|State))',
        'MIRR: (bl11/vc/vgct-02/(P2|State))|(bl11/vc/ipct-04/(P1|State))',
        'DIFF-1: (bl11/vc/vgct-02/(P1|State))|(bl11/vc/ipct-03/(P2|State))',
        'ATT: (bl11/vc/ipct-03/(P1|State))',
        'DCM: (bl11/vc/vgct-01/(P2|State))|(bl11/vc/ipct-02/(P2|State))',
        'PUMP-2: (bl11/vc/ipct-02/(P1|State))',
        'FMASK: (bl11/vc/ipct-01/(P2|State))',
        'PUMP-1: (bl11/vc/ipct-01/(P1|State))',
        'BLVS-1: (bl11/vc/vgct-01/(P1|State))',
        'TU: (fe11/vc/vgct-01/(P1|State))|(fe11/vc/ipct-01/(P1|State))']
        ))
    tg1.showRowFrame(False)
    tg1.showColumnFrame(False)
    tg1.setModel('(BL11|FE11)/VC/(VG|IP)CT-*/(P[12]|State)')
    return tg1

tg2 = None
def get_beamline_grid2():
    import tau.widget.taugrid
    global tg2
    tg2 = tau.widget.taugrid.TauGrid()
    tg2.setRowLabels('VcGauges(mbar):VGCT, IonPumps(mbar):IPCT')
    tg2.setColumnLabels(','.join([
        'BLVS-3: (bl11/vc/vgct-04/(P2|State))',
        'BLVS-2: (bl11/vc/vgct-04/(P1|State))|(bl11/vc/ipct-05/(P2|State))',
        'PSH: (bl11/vc/vgct-03/(P2|State))|(bl11/vc/ipct-05/(P1|State))',
        'DIFF-2: (bl11/vc/vgct-03/(P1|State))|(bl11/vc/ipct-04/(P2|State))',
        'MIRR: (bl11/vc/vgct-02/(P2|State))|(bl11/vc/ipct-04/(P1|State))',
        'DIFF-1: (bl11/vc/vgct-02/(P1|State))|(bl11/vc/ipct-03/(P2|State))',
        'ATT: (bl11/vc/ipct-03/(P1|State))',
        'DCM: (bl11/vc/vgct-01/(P2|State))|(bl11/vc/ipct-02/(P2|State))',
        'PUMP-2: (bl11/vc/ipct-02/(P1|State))',
        'FMASK: (bl11/vc/ipct-01/(P2|State))',
        'PUMP-1: (bl11/vc/ipct-01/(P1|State))',
        'BLVS-1: (bl11/vc/vgct-01/(P1|State))',
        'TU: (fe11/vc/vgct-01/(P1|State))|(fe11/vc/ipct-01/(P1|State))']
        ))
    tg2.showRowFrame(False)
    tg2.showColumnFrame(False)
    tg2.setModel('(BL11|FE11)/VC/(VG|IP)CT-*/(P[12]|State)')
    #tg2.setSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding)
    tg2.setMinimumHeight(175)
    return tg2

new_frame = None
def get_new_frame():
    global new_frame
    new_frame = Qt.QFrame()
    new_frame.setLayout(Qt.QVBoxLayout())
    new_frame.layout().addWidget(Qt.QLabel())#'BL11-NCD, vacuum application'))
    new_frame.setFixedHeight(35)
    return new_frame

def POST_HOOK(ui):
    print 'In bl%02d.rc.py POST_HOOK method ...'%NBL
    try:
        #Disabling TauGrid labels/units
        #global tg1
        #tg1.showAttributeLabels(False)
        #tg1.showAttributeUnits(False)
        global tg2
        tg2.showAttributeLabels(False)
        tg2.showAttributeUnits(False)
    except:
        print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       ('Schema',(wdir('BL%02d/BL%02d-schema.jdw'%(NBL,NBL)),get_beamline_grid2)),#,get_new_frame)),
       #('Schema',wdir('BL%02d/BL%02d-schema.jdw'%(NBL,NBL))),#,get_new_frame)),
       #('NCD',(wdir('BL%02d/BL%02d.jdw'%(NBL,NBL)),get_beamline_grid)),
       #('Grid',wdir('BL11/bl11.grid')),
       #('Drawing',wdir('BL%02d/BL%02d.jdw'%(NBL,NBL))),
       
       #('ALL',(wdir('BL%02d/BL%02d.jdw'%(NBL,NBL)),get_beamline_grid)),
       #('mbar',(get_beamline_grid,)),
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
    for i in (NBL,): #1,2,4,9,11,13,22,24,29,34):
        composer = 'BL%02d/VC/ALL'%i
        tree[composer] = dict((d.upper(),{}) for d in get_matching_devices('BL%02d/*/%s*'%(i,families)) if d.split('/')[-1]!='ALL')
    for dev in tau.Database().get_device_member('FE%02d/VC/*'%NBL): 
        tree[composer]['FE%02d/VC/%s'%(NBL,dev)]={}
    tree[composer]['BL%02d/CT/EPS-PLC-01'%NBL]={}
    tree[composer]['BL%02d/CT/EPS-PLC-01-MBUS'%NBL]={}
    tree[composer]['BL%02d/CT/ALARMS'%NBL]={}
    return tree

TREE=get_default_tree()

## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = {
    'PROFILE':'BL%02d/VC/ALL'%NBL,
    'BL*':'BL%02d/VC/ALL'%NBL,
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
        
## LOADING THE ALARM TOOLBAR
if False:
    try:
        #filters = 
        import panic
        TOOLBAR += [('','',None),('Alarms',panic.widgets.PanicToolbar,None)]
    except Exception,e:
        print 'Unable to load Alarms PanicToolbar: %s'%traceback.format_exc()
        TOOLBAR += [('','',None),('Alarms',wdir('image/icons/panic.gif'), lambda:launch('ctalarms'))]

#TOOLBAR += [('','',None),('Under Construction',QtGui.QIcon(wdir("image/icons/underconst10.gif")),lambda:openWebpage(URL_REDMINE)),]
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('EPS Gui',lambda:os.system('epsGUI &'),None), \
        ('Jive',lambda:os.system('jive &'),None), \
        ('Astor',lambda:os.system('astor &'),None), \
        ('Mambo',lambda:os.system('mambo &'),None), \
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None), \
        ('Archiving Webserver',lambda:os.system('konqueror ctbl11arch01 &'),None), \
        ]),
    ]
