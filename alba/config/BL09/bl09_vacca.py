import imp,fandango
from vacca.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE

#options copied from /homelocal/sicilia/lib/python/site-packages/vacca/beamlines.py

#The device that will be shown by default when loading the application
COMPOSER = DEVICE = fandango.get_matching_devices('BL*/VC/ALL')[0]
DOMAIN = BL = COMPOSER.split('/')[0]

print '>'*20+' Loading config for beamline %s'%BL

EXTRA_DEVICES = [
    d for d in (
        fandango.get_matching_devices('*(pnv|eps|vfcs|ccg|tpg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*')+
        fandango.Astor('PyAlarm/*').get_all_devices())
    if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba'))
    ]
#print 'EXTRA_DEVICES: %s'%EXTRA_DEVICES

GAUGES = [
    'BL09/VC/VGCT-01/P1','BL09/VC/VGCT-01/P2','BL09/VC/VGCT-02/P1','BL09/VC/VGCT-02/P2','BL09/VC/TPG-01/P1','BL09/CT/EPS-PLC-01/mir_oh01_01_pt',
    ]
    
JDRAW_FILE = '/beamlines/bl09/controls/vacca/BL09.jdw'
#imp.find_module('vacca')[1]+'/%s/%s.jdw'%(BL,BL)

#GAUGES = fandango.get_matching_attributes('*/*/*ccg*/pressure')

GRID = {
        'column_labels': ','.join([
            'TXM:(BL09/VC/TPG-01/P1)',
            'DIAG2:(BL09/VC/IPCT-04/P2)',
            'DPS:(BL09/VC/IPCT-03/P2)',
            'M4:(BL09/VC/VGCT-02/P2)|(BL09/VC/IPCT-04/P1)',
            'MONO:(BL09/VC/VGCT-02/P1)|(BL09/VC/IPCT-03/P1)',
            'DIAG1:(BL09/VC/IPCT-02/P2)',
            'JJ:(BL09/VC/VGCT-03/P1)',
            'M2:(BL09/VC/VGCT-01/P2)|(BL09/VC/IPCT-02/P1)',
            'M1:(BL09/VC/VGCT-01/P1)|(BL09/VC/IPCT-01/P2)',
            'WBD:(BL09/VC/IPCT-01/P1)',
            'FE:FE09/VC/(VG|IP)CT-01/P(1|2)']),
        'delayed': False,
        'frames': False,
        'model': '*/(VC|EH)/(IPCT|VGCT|TPG|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|TPG|CCG, IonPumps(mbar):IPCT'
    }


rfamilies = '*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*'
myCUSTOM_TREE = {
    '0.CT':'BL*(VC/ALL|CT/ALARMS|PLC-01|FE_AUTO)$',
    '1.FE24':'FE24/VC/*',
    '2.EH02-PEEM':'',
    '3.EH03-NAPP':'*-EH03-*',
    '4.MKS937 (ccg+pir)':'BL24*(vgct)-[0-9]+$',
    '5.VarianDUAL (pumps)':'BL24*(ipct)-[0-9]+$',
    '6.Valves':{
        '.OH':'*OH/PNV*',
        'EH01':'*EH01/PNV*',
        'EH02':'*EH02/PNV*',
        'EH03':'*EH03/PNV*',
        },
    '7.BAKEOUTS':'BL*(BAKE|ELOTECH|BK)*',
    }