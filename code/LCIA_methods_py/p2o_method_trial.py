import brightway2 as bw
from brightway2 import *
import os
import pandas as pd

def p2o_setup():
    bw.Method(('Phosphorus to ocean', 'total', 'total')).register()
    P2o = bw.Method(('Phosphorus to ocean', 'total', 'total'))
    P2o.metadata['unit'] = 'P-eq'
    P2o.metadata['description'] = 'Total of P flow to oceans. LCIA method for pressures on planetary boundary for Phosphorus (biogeochemical flow).'
    cfs = [[('biosphere3', 'd761f94e-517d-41cf-89fa-17dc72f7a69b'), 0.534], #Phosphorus 'air', 
       [('biosphere3', '198ce8e3-f05a-4bec-9f7f-325347453326'), 0.534], #Phosphorus 'air', 'urban air close to ground'
       [('biosphere3', 'ea4e9316-5080-4b3b-bbf3-1949f6d7577a'), 0.534], #Phosphorus 'air', 'non-urban air or from high stacks'
       [('biosphere3', 'e2d35af7-9806-46ff-9b75-b124a48fa5a1'), 0.534], #Phosphorus 'air', 'low population density, long-term'
       [('biosphere3', '2f8952b0-c90c-4e3d-b546-52b862fc8f11'), 0.337], #Phosphorus 'soil', 'industrial')
       [('biosphere3', 'c89a0749-40a5-4c9c-8770-c4295ea34977'), 0.337], #Phosphorus 'soil', 'agricultural'
       [('biosphere3', '8b0a4a41-c65c-4d94-b10c-94ddb98abdd2'), 0.337], #Phosphorus 'soil'
       [('biosphere3', 'b2631209-8374-431e-b7d5-56c96c6b6d79'), 0.352], #Phosphorus 'water', 'surface water'
       [('biosphere3', 'b1fca66f-8e83-469a-a7b5-018e14d5d545'), 0.352], #Phosphorus 'water', 'ground-'
       [('biosphere3', '2d4b8ec1-8d53-4e62-8a11-ebc45909b02e'), 0.352], #Phosphorus 'water'
       [('biosphere3', '62f3d964-9b53-4d01-9ee0-04112dcfc6d2'), 1], #Phosphorus 'water' , 'ocean'
           
        [('biosphere3', '329fc7d8-4011-4327-84e4-34ff76f0e42d'), 0.326*0.352],#Phosphate ('water', 'ground-')
        [('biosphere3', '3aaf9017-0d8a-42aa-9a60-cbc39e994e73'), 0.326*0.352],#Phosphate ('water', 'ocean')
        [('biosphere3', 'c8791f3c-3c4a-4278-91c0-483797d14da2'), 0.326*0.352],#Phosphate ('water',)
        #[('biosphere3', '490b267b-f429-4d9a-ac79-224e37fb4d58'), 0.326*0.352],#Phosphate ('water', 'ground-, long-term')
        [('biosphere3', '1727b41d-377e-43cd-bc01-9eaba946eccb'), 0.326*0.352],#Phosphate ('water', 'surface water')
        #[('biosphere3', '6dfe5f74e8eb26eb6b479071113dc0f1'), 0.326*0.352],    #Phosphate ('water', 'ground-', 'long-term')
           
        [('biosphere3', '094310bb-49db-5b2d-ae1b-e7b4ffca1d03'), 0.166*0.534],#Trisodium phosphate ('air',)
           
        [('biosphere3', '3850d44e-8919-47bc-9c0a-51ccc4ec9d9f'), 0.183*0.337], #Glyphosate ('soil', 'agricultural')
        [('biosphere3', 'b4f9a201-2a20-4f41-a572-eabc98c75e1b'), 0.183*0.337], #Glyphosate ('soil', 'industrial')
        [('biosphere3', '17955b10-4c04-4fff-91e7-cf89ef1a7cca'), 0.183*0.352], #Glyphosate ('water', 'ground-')
        [('biosphere3', 'e157e3dd-88b9-4256-ab2e-ff82e7b8d088'), 0.183*0.352], #Glyphosate ('water', 'surface water')
        [('biosphere3', 'd2d93101-7555-4c77-b4b8-ddac7f6eba50'), 0.183*0.352], #Glyphosate ('water',)
        [('biosphere3', 'bd02a7ec-dcb5-4609-bc96-cc7a96601ce2'), 0.183*0.534], #Glyphosate ('air', 'non-urban air or from high stacks')
   
        [('biosphere3', '6f5f2323-f747-5578-a3a7-d6a750ca3884'), 0.459*0.337], #Magnesium phosphide	('soil', 'agricultural')
	]
    P2o.validate(cfs)
    P2o.write(cfs)
    
    #load to excel file############
    flows=[]
    cfs_p2o=[]
    for cf in cfs:
        flows.append(cf[0])
        cfs_p2o.append(cf[1])
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs_p2o})
    df_cfs.to_excel(r""+this_dir+"\characterization_factors_phosphorous_to_ocean.xlsx", sheet_name='cfs')
     ###############################
    return()

p2o_setup()
