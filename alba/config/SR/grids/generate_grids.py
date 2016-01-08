import pickle
import fandango

def generate_grids():
    
    for sector in ['ALL']:
        d = dict()
        d['model'] = '.*/VC/(ALL|Composer).*/(State|MaxPressure|Thermocouples)$'#|(SR/VC/ALL/Thermocouples)'
        d['row_labels'] = 'VC:State|Pressure,TC:Thermocouples'
        d['column_labels'] = 'LT:LT.*,BO:BO.*,BT:BT.*,SR/MaxPressure:SR.*Pressure,SR:SR.*State|SR/VC/ALL/Thermocouples'
        d['delayed'] = False
        d['frames'] = False
        pickle.dump(d,open('%s.grid'%sector,'w'))
        
    for sector in ['LT']:
        d = dict()
        d['model'] = "%s/VC/ALL/.*(VGCT|IPCT|SPBX|Pressure|PNV|CCG|PIR|IP-|Thermo|EPS-PLC-01$).*"%sector
        d['row_labels'] = "Vacuum:VGCT|IPCT|PIR-|CCG-|IP-|SPBX,EPS:EPS|Pressure|PNV"
        d['column_labels'] = (
        'VGCT/EPS:VGCT|EPS,'+
        'IPCT:IPCT|PNV,SPBX:SPBX|Thermo,'+                
        'Gauges:CCG|PIR|CCGPressures|L*Pressures|PressureProfile,'+
        'Pumps:IP-|IPPressures')
        d['frames'] = False
        pickle.dump(d,open('%s.grid'%sector,'w'))
        
    for sector in ['BO']:
        d = dict()
        d['model'] ="BO/VC/ALL/.*(VGCT|IPCT|SPBX|Pressures|PNV|CCG|PIR|IP-|Thermo|EPS-PLC-01$).*"
        d['row_labels'] = "Vacuum:VGCT|IPCT|PIR-|CCG-|IP-|SPBX,EPS:EPS|Pressures|PNV"
        d['column_labels'] = (
        'VGCT/EPS:VGCT|EPS,'+
        'IPCT:IPCT|PNV,SPBX:SPBX|Thermo,'+
        'mbar:Pressure,'+
        'Gauges:CCG|PIR')
        #'Pumps:IP-|IPPressures')
        d['frames'] = False
        pickle.dump(d,open('%s.grid'%sector,'w'))             

    for sector in ['BT']+['SR%02d'%i for i in range(1,17)]:
        d = dict()
        d['model'] = "%s/VC/ALL/.*(VGCT|IPCT|SPBX|Pressures|PNV|CCG|PIR|IP-|Thermo|EPS-PLC-01$).*"%sector
        d['row_labels'] = "Vacuum:VGCT|IPCT|PIR-|CCG-|IP-|SPBX,EPS:EPS|Pressures|Thermo|PNV"
        d['column_labels'] = (
        'VGCT/EPS:VGCT|EPS,'+
        'IPCT:IPCT|PNV,SPBX:SPBX|Thermo,'+
        'Gauges:CCG|PIR|CCGPressures,'+
        'Pumps:IP-|IPPressures')
        d['frames'] = False
        pickle.dump(d,open('%s.grid'%sector,'w'))

CABLES = {
 'CCG-FCV':'TRIAX-1',
 'FCV':'UMW12-1',
 'TSP':'STP16-5',
 'IP':'CoaxHV-1b?',
 'CCG':'COAXHV-5',
 'PIR':'STP6-1',
 'PNV':'SMW4-3',
 'SPBX':'CoaxHV-2',
 }

def get_bl_grid_from_ccdb(gridfile,ccdb,translator,filters=CABLES.values(),branch=False,prune=False):
    """
    gridfile: the file in wich the grid dictionary is written
    ccdb is a ccdbAPI initialized module
    translator is a method for converting between CCDB and Tango names in racks
    branch, if False removes %02d from EH/OH families
    prune, if active all IPCT are removed when VGCT is present in column
    """
    d = dict()
    model = '*/VC/(IPCT|VGCT)*'
    d['model'] = model+'/(P[12]|State)'
    d['row_labels'] = 'VcGauges(mbar):VGCT, IonPumps(mbar):IPCT'
    d['frames'] = False
    d['column_labels']=''
    d['delayed'] = False
    cts = fandango.device.get_matching_devices(model)
    # Getting a dictionary {CT:{Port:Eq}}
    result = dict()
    for ct in cts:
        if not translator(ct): continue
        result[ct]= dict((a['source_channel'],a['dest_equipment']) 
                        for a in ccdb.getEquipmentConnections(translator(ct))\
                        if any(fandango.functional.matchCl(f,a['cable_configuration']) for f in filters))
        print '%s: %s' % (ct,result[ct])
    import collections
    cols = collections.defaultdict(list)
    for ct,ports in result.items():
     for port,eq in ports.items():
      if 'CC' in port: attr = port.replace('CC','P')
      elif 'CHV' in port: attr = port.replace('CHV','P')
      elif 'HV' in port: attr = port.replace('HV','P')
      elif 'PI' in port: attr = 'P4' if port=='PI1' else 'P5'
      else: continue
      col = eq.split('-',2)[-1].rsplit('-',1)[0]
      if not branch: col = col.replace('01','')
      cols[col].append(ct+'/'+attr)
      if ct+'/State' not in cols[col]: cols[col].append(ct+'/State')
    if prune: #Removes all IPCTs if there are gauges around
        for col,eqs in cols.items():
            if any('VGCT' in e.upper() for e in eqs):
                print 'pruning IPCT units in column %s'%col
                cols[col] = [e for e in eqs if 'IPCT' not in e.upper()]
    vals = sorted((('|'.join(sorted(cts)),col) for col,cts in cols.items() if not any('FE' in c for c in cts)),reverse=True)
    vals += [('|'.join(sorted(cts)),col) for col,cts in cols.items() if any('FE' in c for c in cts)]
    d['column_labels'] = ','.join('%s:%s'%(eq,v) for v,eq in vals)
    for v,eq in vals:
        print v
        for e in eq.split('|'):
            print '\t%s'%e
    pickle.dump(d,open(gridfile,'w'))
    return d

def bl22_translate(d):
    import re
    if not re.match('(vgct|ipct)-[0-9]+$',d.lower().split('/')[-1]): return ''
    eq = d.split('/')[-1].split('-')[0]
    domain = d.split('/')[0]
    rack = 'RKX22A02' if eq.lower().strip()=='ipct' else 'RKX22A01'
    return '%s-VC-%s-%s-%s'%(domain,eq,rack,d.split('-')[-1])
    
def bl29_translate(d):
    import re
    if not re.match('(vgct|ipct)-[0-9]+$',d.lower().split('/')[-1]): return ''
    eq = d.split('/')[-1].split('-')[0]
    domain = d.split('/')[0]
    rack = 'RKX29A02' if eq.lower().strip()=='ipct' else 'RKX29A03'
    return '%s-VC-%s-%s-%s'%(domain,eq,rack,d.split('-')[-1])

def generate_bl29_grid():
    sector = 'bl29'

    #VGCT
    FE29 = "Front End:(FE29/VC/VGCT-01/P(1|2|4))|(FE29/VC/IPCT-01/P(1|2))," 
    PMTM = "PM-TM:(BL29/VC/VGCT-01/P1)|(BL29/VC/IPCT-01/P2)," 
    ESLI = "esli:(BL29/VC/VGCT-01/P2)|None," 
    MONO = "Mono:(BL29/VC/VGCT-02/P1)|None," 
    GAS = "Gas Cell:(BL29/VC/VGCT-02/P2)|None," 
    KB = "KB:(BL29/VC/VGCT-03/P1)|(BL29/VC/IPCT-06/P1)," 
    BRFM = "BRFM:(BL29/VC/VGCT-03/P2)|(BL29/VC/IPCT-06/P2)," 
    I0 = "I0:(BL29/VC/VGCT-04/P1)|(BL29/VC/IPCT-07/P1)," 
    XS_VERTICAL = "XS vertical:(BL29/VC/VGCT-04/P2)|None," 

    #IPCT
    DIAGON = "Diagn-On:None|(BL29/VC/IPCT-01/P1)," 
    PC1 = "Pumping chamber 1: None|(BL29/VC/IPCT-02/P1)," 
    ES_HORIZONTAL = "ES horizontal: None|(BL29/VC/IPCT-02/P2)," 
    PC2 = "Pumping chamber 2: None|(BL29/VC/IPCT-03/P1)," 
    MONO1 = "Mono 1: None|(BL29/VC/IPCT-03/P2)," 
    MONO2 = "Mono 2: None|(BL29/VC/IPCT-04/P1)," 
    BLADE2 = "4-Blade 2: None|(BL29/VC/IPCT-04/P2)," 
    XS_HORIZONTAL = "XS horizontal: None|(BL29/VC/IPCT-05/P1)," 
    PC3 = "Pumping chamber 3: None|(BL29/VC/IPCT-05/P2)," 
    SPARE = "Spare: None|(BL29/VC/IPCT-07/P2)," 

    d = dict()
    d['row_labels'] = 'Vacuum Gauges:VGCT, Ion Pumps:IPCT'
    d['column_labels'] = (
        "Tango State:*/*/*/State,"+#','.join(reversed((
        FE29+PMTM+ESLI+MONO+GAS+DIAGON+KB+BRFM+I0+
        XS_VERTICAL+DIAGON+PC1+ES_HORIZONTAL+PC2+
        MONO1+MONO2+BLADE2+XS_HORIZONTAL+PC3+SPARE#).split(',')))
    )
    d['model'] = "(FE29|BL29)/VC/(VG|IP)CT-*/(P[12])|State"
    d['frames'] = False
    d['delayed'] = False #True

    #for col in range(len(gui.columns)):
    #    gui.table.setColumnWidth(col,150)
    #gui.resize(Qt.QSize(300,666))
    
    pickle.dump(d,open('%s.grid.org'%sector,'w'))
    return d


if __name__ == '__main__':
    generate_grids()
