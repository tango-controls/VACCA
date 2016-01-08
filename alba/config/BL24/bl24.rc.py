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
NBL = 24
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
PLOT_HEIGHT=400
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
DEVICE = 'BL%02d/VC/ALL'%NBL

import widgets
widgets.DEV_ATTRS['EPS']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']
widgets.DEV_ATTRS['EPS-PLC']+=['.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_','*RGA*']

tg1 = None
def get_empty_grid():
    import tau.widget.taugrid
    global tg1
    tg1 = tau.widget.taugrid.TauGrid()
    tg1.showRowFrame(False)
    tg1.showColumnFrame(False)
    return tg1

tg1,tg2 = None,None

def get_beamline_grid1():
    import tau.widget.taugrid
    global tg1
    tg1 = tau.widget.taugrid.TauGrid()
    #tg.load(wdir('BL%02d/bl%02d.grid'%(NBL,NBL)))
    tg1.load({'row_labels': 'IPs(mbar):*IPCT*, CCGs(mbar):*VGCT*',
        'delayed': False,
        'frames': False,
        'model': '*/VC/(IPCT|VGCT)*/(P[12]|State)',
        'column_labels': ','.join([
                    'PEEM_I0:(BL24/VC/IPCT-07/(P2|State))|(BL24/VC/VGCT-05/(P1|State))',
                    'KB:(BL24/VC/IPCT-07/(P1|State))|(BL24/VC/VGCT-04/(P2|State))',
                    'PEEM_BRFM:(BL24/VC/IPCT-06/(P2|State))|(BL24/VC/VGCT-04/(P1|State))',
                    'PEEM_IC:(BL24/VC/IPCT-06/(P1|State))|(BL24/VC/VGCT-03/(P2|State))',
                    'PEEM_FSMM:BL24/VC/IPCT-05/(P2|State)',
                    'PEEM_PIPE:BL24/VC/IPCT-05/(P1|State)',
                    
                    'YCH:BL24/VC/IPCT-04/(P2|State)',
                    
                    'M3:(BL24/VC/IPCT-04/(P1|State))|(BL24/VC/VGCT-03/(P1|State))',
                    '4JAW:BL24/VC/IPCT-03/(P2|State)',
                    'MONO:(BL24/VC/IPCT-03/(P1|State))|(BL24/VC/VGCT-02/(P2|State))',
                    'BCC:(BL24/VC/IPCT-02/(P2|State))|(BL24/VC/VGCT-02/(P1|State))',
                    'M1:(BL24/VC/IPCT-02/(P1|State))|(BL24/VC/VGCT-01/(P2|State))',
                    'ATTE:BL24/VC/VGCT-01/(P1|State)',
                    'FE_TU:FE24/VC/VGCT-01/(P1|State)'
        ])})
    
    tg1.showRowFrame(False)
    tg1.showColumnFrame(False)
    return tg1

#{'column_labels': 'NAPP_I0:BL24/VC/VGCT-07/(P1|State),M4B:(BL24/VC/IPCT-09/(P2|State))|(BL24/VC/VGCT-06/(P2|State)),NAPP_BRFM:(BL24/VC/IPCT-09/(P1|State))|(BL24/VC/VGCT-06/(P1|State)),NAPP_IC:BL24/VC/VGCT-05/(P2|State),NAPP_FSMM:BL24/VC/IPCT-08/(P2|State),NAPP_PIPE:BL24/VC/IPCT-08/(P1|State),PEEM_I0:(BL24/VC/IPCT-07/(P2|State))|(BL24/VC/VGCT-05/(P1|State)),KB:(BL24/VC/IPCT-07/(P1|State))|(BL24/VC/VGCT-04/(P2|State)),PEEM_BRFM:(BL24/VC/IPCT-06/(P2|State))|(BL24/VC/VGCT-04/(P1|State)),PEEM_IC:(BL24/VC/IPCT-06/(P1|State))|(BL24/VC/VGCT-03/(P2|State)),PEEM_FSMM:BL24/VC/IPCT-05/(P2|State),PEEM_PIPE:BL24/VC/IPCT-05/(P1|State),YCH:BL24/VC/IPCT-04/(P2|State),M3:(BL24/VC/IPCT-04/(P1|State))|(BL24/VC/VGCT-03/(P1|State)),4JAW:BL24/VC/IPCT-03/(P2|State),MONO:(BL24/VC/IPCT-03/(P1|State))|(BL24/VC/VGCT-02/(P2|State)),BCC:(BL24/VC/IPCT-02/(P2|State))|(BL24/VC/VGCT-02/(P1|State)),M1:(BL24/VC/IPCT-02/(P1|State))|(BL24/VC/VGCT-01/(P2|State)),ATTE:BL24/VC/VGCT-01/(P1|State),FE_TU:FE24/VC/VGCT-01/(P1|State)',
# 'delayed': False,
# 'frames': False,
# 'model': '*/VC/(IPCT|VGCT)*/(P[12]|State)',
# 'row_labels': 'IonPumps(mbar):*IPCT*, VcGauges(mbar):*VGCT*'}


def get_beamline_grid2():
    import tau.widget.taugrid
    global tg2
    tg2 = tau.widget.taugrid.TauGrid()
    #tg2.load(wdir('BL%02d/bl%02d.grid'%(NBL,NBL)))
    tg2.load({'row_labels': 'IPs(mbar):*IPCT*, CCGs(mbar):*VGCT*',
        'delayed': False,
        'frames': False,
        'model': '*/VC/(IPCT|VGCT)*/(P[12]|State)',
        'column_labels': ','.join([
                    'NAPP_I0:BL24/VC/VGCT-07/(P1|State)',
                    'M4B:(BL24/VC/IPCT-09/(P2|State))|(BL24/VC/VGCT-06/(P2|State))',
                    'NAPP_BRFM:(BL24/VC/IPCT-09/(P1|State))|(BL24/VC/VGCT-06/(P1|State))',
                    'NAPP_IC:BL24/VC/VGCT-05/(P2|State)',
                    'NAPP_FSMM:BL24/VC/IPCT-08/(P2|State)',
                    'NAPP_PIPE:BL24/VC/IPCT-08/(P1|State)',

                    'YCH:BL24/VC/IPCT-04/(P2|State)',
                    
                    'M3:(BL24/VC/IPCT-04/(P1|State))|(BL24/VC/VGCT-03/(P1|State))',
                    '4JAW:BL24/VC/IPCT-03/(P2|State)',
                    'MONO:(BL24/VC/IPCT-03/(P1|State))|(BL24/VC/VGCT-02/(P2|State))',
                    'BCC:(BL24/VC/IPCT-02/(P2|State))|(BL24/VC/VGCT-02/(P1|State))',
                    'M1:(BL24/VC/IPCT-02/(P1|State))|(BL24/VC/VGCT-01/(P2|State))',
                    'ATTE:BL24/VC/VGCT-01/(P1|State)',
                    'FE_TU:FE24/VC/VGCT-01/(P1|State)'

        ])})
    tg2.showRowFrame(False)
    tg2.showColumnFrame(False)
    return tg2

def POST_HOOK(ui):
    print 'In bl%02d.rc.py POST_HOOK method ...'%NBL
    #try:
        ##Disabling TauGrid labels/units
        #global tg1,tg2
        #tg1.showAttributeLabels(False)
        #tg1.showAttributeUnits(False)
        #tg2.showAttributeLabels(False)
        #tg2.showAttributeUnits(False)
    #except:
        #print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       #('NCD',get_beamline_grid),
       #('Grid',wdir('BL%s/bl%s.grid'%(NBL,NBL))),
       ('CIRCE',(wdir('BL24/BL24-Y.jdw'),get_empty_grid)),
       #('CIRCE',(wdir('BL%02d/BL%02d.jdw'%(NBL,NBL)),get_beamline_grid1,get_beamline_grid2)),
       #('ALL',(wdir('BL%02d/BL%02d.jdw'%(NBL,NBL)),wdir('BL24/bl24.horz.grid'))),
       #('2Lines',(wdir('BL%02d/BL%02d.jdw'%(NBL,NBL)),wdir('BL24/bl24.horz.grid'),wdir('BL24/bl24.horz.grid'))),
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
    
visor = 'kpdf'
MENUS = [
    ('Tools',[
        ('EPS Gui',lambda:os.system('epsGUI &'),None), \
        ('Jive',lambda:os.system('jive &'),None), \
        ('Astor',lambda:os.system('astor &'),None), \
        ('Mambo',lambda:os.system('mambo &'),None), \
        ('TaurusTrend',lambda:os.system('taurustrend -a &'),None), \
        ('Archiving Webserver',lambda:os.system('konqueror ctbl24arch01 &'),None), \
        ]),
    ]
