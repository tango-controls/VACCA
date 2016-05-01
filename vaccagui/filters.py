import fandango
import imp
from vacca.utils import wdir,vpath

__itemConfigurations__ = []
nostatus = '(?!.*(status|alarm|warning)$).*'
noaaf = '(?!.*a_af$).*'

#Attribute filters to be applied to DevicePanel
AttributeFilters = fandango.dicts.CaselessDict({ #Put attribute names in lower case!
    'ALARMS' : ['ActiveAlarms', 'PastAlarms', 'AlarmList', 'AlarmReceivers'],
    'COMPOSER' : 'Q1,Q2,Q3,Q4,IPNames,CCGNames,.*Pressure.*'.split(','),
    'ALL' : [ #'.*Pressure.*,Average.*,DevStates,Thermocouples'.split(','),
        ('Status',['.*(pressure|current|temperature)$','.*pnv.*']),
        ('Plots',['.*(pressure|current|state|thermocouple|temperature)s$']),
        ],
    'VGCT': ['ChannelState']+['p%d'%(i+1) for i in range(5)]+['Value','Relay','Protect'],
    ##'IPCT': [
                ##'hv1code','hv2code',
                ##'p1','p2','modelocal',
                ##'v1','v2','modestep',
                ##'i1','i2','modeprotect',
                ##'interlock',
                ###'hv1code','p1','i1','v1','hv2code','p2','i2','v2',
                ##'errorstatus','ionpump.*'],
    'IPCT': [
                ('Status',['hv1status','p1','hv2status','p2',]),
                ('CH1',['hv1','p1','v1','i1']),
                ('CH2',['hv2','p2','v2','i2']),
                ('Config',['mode','interlock','error','ionpump',]),
                #'p1','p2','modelocal',
                #'v1','v2','modestep',
                #'i1','i2','modeprotect',
                #'interlock',
                ##'hv1code','p1','i1','v1','hv2code','p2','i2','v2',
                #'errorstatus','ionpump.*'],
            ],                   
    'SPBX': [
            ('Pressures',reduce(list.__add__,(['p%d'%i] for i in range(1,1+8)))),
            ('Currents',['totalcurrent']+reduce(list.__add__,(['i%d'%i] for i in range(1,1+8)))),
            ('Control',['cableinterlocks','pressureinterlocks']+['channelvoltages','ionpumpsconfig']+['interlockthresholds','warningthresholds'],),
            ],
    'PNV': ['state','PLCAttribute'],
    'SPNV': ['state'],
    '.*EPS-PLC-01$': [
        ('Status',['CpuStatus','PLC_Config_Status','READY','ENABLE','DISABLE']),
        ('ACT',
            #[t+nostatus for t in ('BL_','FE_','RGA_','_ITL','ENABLE','_OPEN')]
            [t+nostatus for t in ('READY','INTERLOCK','ITL','OPEN','CLOSE','AUTO','RESET','ENABLE','DISABLE','PNV')]
            ),
        ('Temperatures',['THERMOCOUPLES',]+[t+nostatus for t in 
            ('(?!^.*fsotr|ccg|brtu|pnv|vl|li|lt)_T[0-9]+','.*TC','.*_PT')]),
        ('VC',['vc_','_ip','cath','ccg','pst_','pir']),
        ('Flows',[t+nostatus for t in ('co_','coas_','was_','paas_','fsw','_fs_',)]),
        #'_READY','OPEN_','CLOSE_'
        #'.*TC.*','.*_PT.*','_READY','OPEN_','CLOSE_','was_','paas_'],
        #'EPS-PLC': ['CPU_STATUS','PLC_CONFIG_STATUS','THERMOCOUPLES'],
        ],
    'CCG-': ['pressure','channelstatus','controller'],
    'V-PEN': ['pressure','channelstatus','controller'],
    'V-VARIP': ['pressure','channelstatus','controller'],
    'PIR-': ['pressure','channelstatus','controller'],
    'IP-': ['pressure','channelstatus','controller'],
    })

CommandFilters = fandango.dicts.CaselessDict({ #Put commands names in lower case!
    'ALL': (('evaluateFormula',()),('updateDynamicAttributes',()),('Open*',()),('Close*',())),
    'ALARMS': (('ResetAlarm',()),('ResetAll',()),('Init',()),),
    'VGCT': (('cc_on',('P1','P2')),  ('cc_off',('P1','P2')), ('sendcommand',())),
    'IPCT': (('setmode',('SERIAL','LOCAL','STEP','FIXED','START','PROTECT')), 
                ('onhv1',()), ('offhv1',()), ('onhv2',()), ('offhv2',()), 
               ('sendcommand',())),
    'ELOTECH': (('Init',()),('Start',()),('Stop',())),
    'SPBX': (
        ('GetAlarms',()),
        ('ResetAlarms',()),
        ('talk',()),
        ),
    'PNV-': (('open',()),('close',())),
    'SPNV-': (('open',()),('close',())),
    '.*EPS-PLC-01$': (),
    'SERIAL': (('init',()),),
    'CCG-': (('on',()),('off',())),
    'V-PEN': (('on',()),('off',())),
    'PIR-': (),
    'V-VARIP': (),
    'IP-': (),
    })
    
cleanup = lambda k: fandango.replaceCl('[\[\]\{\}\(\)\.\*\$\?\+/,]','',k.lower())

# Default icon could be taurus.qt.qtgui.resource.getIcon(':/places/network-server.svg')
def getDefaultIcon(k=None):
    import taurus.qt.qtgui.resource
    return taurus.qt.qtgui.resource.getIcon(':/places/network-server.svg')

IconMap = fandango.dicts.CaselessDefaultDict(getDefaultIcon)
IconMap.update(dict((k,wdir('image/equips/icon-%s.gif'%fandango.replaceCl('^[- ]|[- ][0-9]{0,3}$','',cleanup(k)))) for k in AttributeFilters))
IconMap['v-pen'] = IconMap['ccg-']
IconMap['v-pir'] = IconMap['pir-']
IconMap['v-varip'] = IconMap['ip-']


