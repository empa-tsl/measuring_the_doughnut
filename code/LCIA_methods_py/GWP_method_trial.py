import brightway2 as bw
from brightway2 import *

def GWP_setup():
    """
    Generates a LCIA method based on IPCC 2013, in which the flow Carbon dioxide, in air ((natural resource, in air)) is added as a negative flow.
    
    """
    
    bw.Method(('GWP 100a', 'climate change', 'including CO2 as natural resource')).register()
    GWP = bw.Method(('GWP 100a', 'climate change', 'including CO2 as natural resource'))
    GWP.metadata['unit'] = 'kg CO2-Eq'
    GWP.metadata['description'] = 'Global Warming Potential based on IPCC 2013 including Carbon dioxide, in air ((natural resource, in air)) . LCIA method for pressure on planetary boundary for climate stability.'
    
    GWP_IPCC_2013 = [m for m in bw.methods if 'climate change' in str(m) 
                       and 'IPCC 2013' in str(m) 
                       and 'GWP 100' in str(m)
                       and not 'LT' in str(m)
                        ][0]
    
    method=bw.Method(GWP_IPCC_2013)
    cfs_old=[(bw.get_activity(flow), cf) for flow, cf in method.load()] #get the old cfs
    
    CO2_resource = bw.get_activity(('biosphere3', 'cc6a1abb-b123-4ca6-8f16-38209df609be')) #Carbon dioxide, in air ((natural resource, in air))
    CF = -1 #is equivalent to -1 kg CO2
    
    cfs_old.append((CO2_resource, CF))
    
    GWP.write(cfs_old)
    
    return

GWP_setup()
    
    
    
    
