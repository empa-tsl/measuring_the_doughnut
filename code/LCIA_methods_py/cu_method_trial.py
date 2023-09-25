import brightway2 as bw
from brightway2 import *
import pandas as pd
import os

def cu_setup():
    #bio = bw.Database("biosphere3")
    #nflows=bio.search('Occupation, permanent crop')

    #for i in range(len(nflows)):
     #   fl=nflows[i]
        
    bw.Method(('cropland use', 'occupation', 'total')).register()
    CU = bw.Method(('cropland use', 'occupation', 'total'))
    CU.metadata['unit'] = 'm2*year'
    CU.metadata['description'] = 'Total occupation of area by cropland use. LCIA method for pressures on planetary boundary for Land use changes.'

    cfs = [[('biosphere3', 'c5aafa60-495c-461c-a1d4-b262a34c45b9'), 1], #Occupation, annual crop
       [('biosphere3', 'c4a82f46-381f-474c-a362-3363064b9c33'), 1], #Occupation, annual crop, irrigated
       [('biosphere3', '9e80f7cd-47fa-4c7f-8f2c-bdb9731b3196'), 1], #Occupation, annual crop, greenhouse
       [('biosphere3', 'a6889a22-e99e-42ea-85cd-4a68d7975dcd'), 1], #Occupation, annual crop, non-irrigated
       [('biosphere3', '8c173ca1-5f74-4a6e-89e5-dd18e0f18d1a'), 1], #Occupation, arable land, unspecified use
       [('biosphere3', '9fd128fe-d8c5-476f-af42-2795d5f5d227'), 1], #Occupation, annual crop, irrigated, intensive
       [('biosphere3', 'e063ee9c-9850-42b5-b01e-4cc9b5ad7152'), 1], #Occupation, annual crop, non-irrigated, intensive
       [('biosphere3', '1b0a8570-eab4-46c2-9b67-c9b918e75676'), 1], #Occupation, annual crop, non-irrigated, extensive
       [('biosphere3', 'e9007a6f-7244-44d4-a561-91ae1b6c6cfc'), 1], #Occupation, permanent crop
       [('biosphere3', '1896b498-8d13-4f58-8c17-21fe57740158'), 1], #Occupation, permanent crop, irrigated
       [('biosphere3', 'f318deb8-ac36-47c0-bb00-e3022b583c7e'), 1], #permanent crop, non-irrigated, intensive
       [('biosphere3', 'c9461a73-d00a-4fc7-a890-a9eda6af3185'), 1], #Occupation, permanent crop, irrigated, intensive
      ]
    CU.validate(cfs)
    CU.write(cfs)
    
    #load to excel file############
    flows=[]
    cfs_cu=[]
    for cf in cfs:
        flows.append(cf[0])
        cfs_cu.append(cf[1])
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs_cu})
    df_cfs.to_excel(r""+this_dir+"\characterization_factors_cropland_use.xlsx", sheet_name='cfs')
     ###############################
    return()
    
cu_setup()