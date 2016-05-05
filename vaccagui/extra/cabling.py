
import fandango.functional as fun
from fandango.arrays import CSVArray

#####################################################################################
# Managing Cabling, tree and sorting
#####################################################################################

csvs = type('struct',(object,),{
        'tango_names':None,
        'tango_channel_names':None,
        'tango_port_names':None,
        '__repr__':lambda s:str(s.__dict__),
        })()

def load_from_csv():
    csvs.tango_names = CSVArray(wdir('etc/cts_names.csv'))
    csvs.tango_names.setOffset(1)
    csvs.tango_channel_names = CSVArray(wdir('etc/serial_names.csv'))
    csvs.tango_channel_names.setOffset(1)
    csvs.tango_port_names = CSVArray(wdir('etc/port_names.csv'))
    csvs.tango_port_names.setOffset(0)

def getTangoName(equipment_code,channel=''):
    """
    retorna un array amb els noms dels tango device server del equip
    @param equipment_code: string with the equipment name
    @param channel: check if the tango name is linked to a channel name (str)
    """
    if csvs.tango_names is None: load_from_csv()
    try:
      if not channel:
        for i in range(csvs.tango_names.size()[0]):
            line = csvs.tango_names.getd(i)
            if line['CCDB'].lower() == equipment_code.lower():
                return [line['Tango']]
      else:
        for i in range(csvs.tango_names.size()[0]):
            line = csvs.tango_channel_names.getd(i)
            if line['CCDB'].lower() == equipment_code.lower() and line['Channel'].lower() == str(channel).lower():
                return [line['Tango']]
    except:
      print 'Unable to get a TangoName for %s'%(' ').join([equipment_code,channel])
    return []

def getDevicePort(device_name):
    """ Returns the port assigned to each device; it is used to translate CCG to VGCT/P1 in trends """
    if csvs.tango_names is None: load_from_csv()
    target = '/'.join(device_name.split('/')[:3])
    for alias,port,dev in csvs.tango_port_names.rows:
      if dev.lower().strip()==target.lower().strip():
        #print 'Vacca.getDevicePort(...): %s is replaced by %s' % (device_name,'/'.join((alias,port))) 
        return '/'.join((alias,port))
    return ''#device_name #It was leading to errors retrieving attribute names

########################################################################################################################################
## Tree management methods

def get_tango_nodes(dct):
    """ gets a dictionary with equipment,channel connections and returns a nested dictionary with tango names. """
    result = {}
    if csvs.tango_names is None: load_from_csv()
    for k,v in dct.iteritems():
        if 'PAPA' in k:
            for channel,equips in v.iteritems():
                d2 = {}
                #print '%s:%s,%s'%(k,channel,equips)
                tango = getTangoName(k,channel)
                d2.update(get_tango_nodes(equips))
                #print 'd2 of %s is %s' % (k,d2)
                if tango: 
                    result[tango[0]+('RKA' in k and ' (%s)'%(k.split('-')[3]) or '')] = d2
                else: print '%s-%s has not Tango Name !!'%(k,channel)
        else:
            d2 = {}
            tango = getTangoName(k)
            [d2.update(get_tango_nodes(value)) for value in v.values()]
            if tango: 
                if d2 or 'RKA' not in k: result[tango[0]+('RKA' in k and ' (%s)'%(k.split('-')[3]) or '')] = d2
            else: print '%s has not Tango Name !!'%k
    return result

        
def get_connections_tree(device):
    from CCDB import ccdbAPI
    from tau.widget import TauDevTree
    ccdbAPI.initApi()
    cnames = []
    tdt = TauDevTree()
    def get_children(dev):
        cn = ccdbAPI.getCCDBName(dev)
        children = {}
        if cn:
            cnames.append(cn[0][0])
            for c in ccdbAPI.getEquipmentConnections(cnames[-1]):
                if c['dest_equipment'] in cnames: continue
                tname = ccdbAPI.getTangoName(c['dest_equipment'])
                if tname:
                    children[c['source_channel']] = {tname[0]:get_children(tname[0])}
        return children
    device = device.upper()
    tdt.setTree(tdt,{device:get_children(device)})
    tdt.headerItem().setText(0,'%s Cabling Tree'%device)
    return tdt
