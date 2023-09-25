import brightway2 as bw
from brightway2 import *
import pandas as pd
import os

def p2s_setup():
    bio = bw.Database("biosphere3")

    nflows=bio.search('Phosphorus')
    for i in range(14):
        fl=nflows[i]
        
    bw.Method(('Phosphorus to soil', 'total', 'total')).register()
    P2s = bw.Method(('Phosphorus to soil', 'total', 'total'))
    P2s.metadata['unit'] = 'P-eq'
    P2s.metadata['description'] = 'Total of P flow to soil. LCIA method for pressures on planetary boundary for Phosphorus (biogeochemical flow).'
    
    cfs = [[('biosphere3', 'c89a0749-40a5-4c9c-8770-c4295ea34977'), 1], #Phosphorus 'soil', 'agricultural
           [('biosphere3', '2f8952b0-c90c-4e3d-b546-52b862fc8f11'), 1], #Phosphorus 'soil', 'industrial'
           [('biosphere3', '8b0a4a41-c65c-4d94-b10c-94ddb98abdd2'), 1], #Phosphorus 'soil',
           #[('biosphere3', 'b6e2f7f4-6b2e-4b3e-be1f-67626cb8205d'), 1], #Phosphorus ('soil', 'forestry')
           [('biosphere3', '3850d44e-8919-47bc-9c0a-51ccc4ec9d9f'), 0.183], #Glyphosate	('soil', 'agricultural')
           [('biosphere3', 'b4f9a201-2a20-4f41-a572-eabc98c75e1b'), 0.183], #Glyphosate	('soil', 'industrial')
            [('biosphere3', '6f5f2323-f747-5578-a3a7-d6a750ca3884'), 0.459], #Magnesium phosphide	('soil', 'agricultural')
      ]
    P2s.validate(cfs)
    P2s.write(cfs)
    
    #load to excel file############
    flows=[]
    cfs_p2s=[]
    for cf in cfs_p2s:
        flows.append(cf[0])
        cfs.append(cf[1])
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs_p2s})
    df_cfs.to_excel(r""+this_dir+"\characterization_factors_phophorous_to_soil.xlsx", sheet_name='cfs')
     ###############################
    return()
    
p2s_setup()