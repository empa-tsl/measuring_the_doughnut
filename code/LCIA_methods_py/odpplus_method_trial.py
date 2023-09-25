import brightway2 as bw
from brightway2 import *
import pandas as pd
import os

def odpplus_setup():
    bio = bw.Database("biosphere3")
    
#     First, collect all the methods you want to combine within the ODPplus method
    
    odp_cml=[method for method in bw.methods if "ozone depletion" in str(method)
    and 'CML 2001' in str(method)
    and not 'LT' in str(method)]
    
    odp_recipe=[method for method in bw.methods if "ozone depletion" in str(method)
    and 'ReCiPe Midpoint (E) V1.13' in str(method)
    and not 'LT' in str(method)]
    
    from itertools import chain
    methods=list(chain.from_iterable([odp_cml, odp_recipe]))
    
#     Also, we want to add N2O to the characterisation factors

    n2o=bio.search('dinitrogen monoxide')
    
#     First, get all charactization flows and their factors

    flows=[]
    cfs=[]
    for method in methods:
        met=bw.Method(method)
        flows_and_cfs=[(bw.get_activity(flow), cf) for flow, cf in met.load()]
        for cf in flows_and_cfs:
            flows.append(cf[0])
            cfs.append(cf[1])
            
            # get the mean characterization factors
            
    df=pd.DataFrame({'flow': list(flows), 'cf': cfs})
    mean_cfs=df.groupby('flow')['cf'].mean()
    unique_flows=list(df.groupby('flow').groups.keys())
    
    # N2O characterization factors for all compartments
    cfs_n2o=[0.011]*len(n2o)
    
    #list all flows and cf
    
    all_flows=list(chain.from_iterable([unique_flows, n2o]))
    all_cfs=list(chain.from_iterable([mean_cfs, cfs_n2o]))
    
    cfs_ODPplus=[]
    for i in range(len(all_flows)):
        cfs_ODPplus.append((all_flows[i], all_cfs[i]))
        
        #register the method
        
    bw.Method(('ozone depletion', 'including N2O', 'average')).register()
    ODPplus = bw.Method(('ozone depletion', 'including N2O', 'average'))
    ODPplus.metadata['unit'] = 'kg CFC-11 eq'
    ODPplus.metadata['description'] = 'Ozone depletion potential as an average of CML 2001 and ReCiPe Midpoint (E) V1.13 methods and including N2O. LCIA method for pressures on planetary boundary for stratospheric ozone.'

    ODPplus.write(cfs_ODPplus)
    
    #load to excel file############
    flows=[]
    cfs=[]
    for cf in cfs_ODPplus:
        flows.append(cf[0].key)
        cfs.append(cf[1])
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs})
    df_cfs.to_excel(r""+this_dir+"\characterization_factors_ozone_depletion_potential_plus.xlsx", sheet_name='cfs')
     ###############################
    return()

odpplus_setup()