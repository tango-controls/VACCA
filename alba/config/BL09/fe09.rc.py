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
#SYNOPTICS = {'Name':'.jdw/.grid'}
#TREE = '' #pickle file
#COMPOSERS = {'PROFILE':'SR/VC/ALL','*/*/*':'SR/VC/ALL'} # Assigns composer for PROFILE and each subdomain
#TOOLBAR = [('','',None)] #Name,icon,action tuples
#MENUS = [('',[('',None,None)])] #Name, Submenu((Name,Action,Icon tuples))
#------------------------------------------------------------------------------

#This dictionary defines the synoptic for each domain
SYNOPTICS = SortedDict([
       ('ALL',wdir('jdw/FE09.jdw')),
    ])

def get_default_tree():
    """ 
    Gets the tree tango names tree and adds all composers, valves and LT devices 
    Order of nodes in the tree is managed by the Vacca.tree module
    """
    print 'Getting the device tree dictionary ...'
    import cabling,tau
    tree = {}
    #Adding FrontEnds
    for i in (9,): #1,2,4,9,11,13,22,24,29,34):
        tree['FE%02d/VC/ALL'%i] = dict([('FE%02d/VC/%s'%(i,m.upper()),{}) for m in tau.Database().get_device_member('FE%02d/VC/*'%i) if m!='ALL'])
    return tree

TREE=get_default_tree()

## This dictionary defines the composer for each domain (by regexp)
# The composer with the key 'PLOT' will be used to generate the main pressure profile
COMPOSERS = {
    'PROFILE':'FE09/VC/ALL',
    'FE09*':'FE09/VC/ALL',
    }
    
TOOLBAR = [
        ('','',None),
        #('Search',wdir('image/icons/search.png'),\
            #lambda: ui.tauDevTree.findInTree(str(QtGui.QInputDialog.getText(ui.tauDevTree,'Search ...','Write a part of the name',QtGui.QLineEdit.Normal)[0]))),
        ('','',None),
        ('LTB Gui',wdir('image/icons/cow_icon-LTB.png'),lambda:os.system('vacca_LTB &')),
        ('','',None),
        ('Archiving Viewer',wdir('image/icons/Mambo-icon.png'), lambda:os.system('mambo &')),
        ('','',None),
        #('12hours Profile',wdir('image/icons/clock.png'), lambda:os.system(wdir('profile.qub.py bo/vc/ip_profile/historicprofile &'))),
        #('','',None),
        ('RGA ProcessEye',wdir('image/equips/icon-rga.gif'), lambda:os.system('rdesktop -g 1440x880 ctrga01 &')),
        ('','',None),
        ('EPS',wdir('image/equips/icon-eps.gif'), lambda:os.system('epsGUI &')),
        #('','',None),        
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