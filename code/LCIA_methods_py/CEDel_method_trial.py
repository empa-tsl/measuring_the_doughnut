import brightway2 as bw
from brightway2 import *
import pandas as pd
import os

def cedel_setup():
    bio = bw.Database("biosphere3")
    CED = [method for method in bw.methods if "cumulative energy demand" in str(method)]
    CED_fossil = bw.Method(('cumulative energy demand', 'fossil', 'non-renewable energy resources, fossil'))
    
    bw.Method(('cumulative energy demand', 'total', 'energy resources, total')).register()
    CED_total = bw.Method(('cumulative energy demand', 'total', 'energy resources, total'))
    print(CED_total)
    CED_total.metadata['unit'] = 'MJ-eq'
    CED_total.metadata['description'] = 'Total of all cumulative energy demand methods'
    [m for m in bw.methods if 'cumulative energy demand' in str(m)]

    cfs = []
    for m in bw.methods:
        if "cumulative energy demand" in str(m) and 'total' not in str(m):
            method = bw.Method(m)
            for flow, cf in method.load():
                cfs.append((bw.get_activity(flow), cf))
                
    CED_total.write(cfs)
    conversion_factors_el = [
    {
        'category':'wind',
        'efficiency': 1
    },
    {
        'category':'biomass',
        'efficiency': 0.25
    },
    {
        'category':'fossil',
        'efficiency': 0.36
    },
    {
        'category':'geothermal',
        'efficiency': 1
    },
    {
        'category':'nuclear',
        'efficiency': 0.33
    },
    {
        'category':'primary forest',
        'efficiency': 0.25
    },
    {
        'category':'solar',
        'efficiency': 1
    },
    {
        'category':'water',
        'efficiency': 1
    },
    
    ]
    bw.Method(('cumulative energy demand, electricity', 'total', 'energy resources, total')).register()

    CED_el_total = bw.Method(('cumulative energy demand, electricity', 'total', 'energy resources, total'))
    CED_el_total.metadata['unit'] = 'MJ-eq'
    CED_el_total.metadata['description'] = 'Total of all cumulative energy demand methods converted to electric energy equivalents'
    [m for m in bw.methods if "cumulative energy demand" in str(m)]
    
    cfs_el = []
    for m in bw.methods:
        if "cumulative energy demand" in str(m) and 'total' not in str(m) and 'electricity' not in str(m):
            method = bw.Method(m)
            for conv_f in conversion_factors_el:
                if conv_f['category'] in str(method):
                    for flow, cf in method.load():
                        cfs_el.append((bw.get_activity(flow), cf * conv_f['efficiency']))

    CED_el_total.write(cfs_el)
    [(bw.get_activity(flow), cf) for flow, cf in CED_el_total.load()]
    
    #load to excel file############
    flows=[]
    cfs=[]
    for cf in cfs_el:
        flows.append(cf[0].key)
        cfs.append(cf[1])
    
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs})
    df_cfs.to_excel(r""+this_dir+"\characterization_factors_cumulative_energy_demand_electric.xlsx", sheet_name='cfs')
     ###############################    
    return()
    
cedel_setup()