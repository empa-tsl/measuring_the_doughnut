import brightway2 as bw
from brightway2 import *
import pandas as pd
import os

def rne_setup():
    #bio = bw.Database("biosphere3")
    
    bw.Method(('reactive nitrogen emissions', 'total', 'nitrogen total')).register()
    rNE = bw.Method(('reactive nitrogen emissions', 'total', 'nitrogen total'))
    rNE.metadata['unit'] = 'N-eq'
    rNE.metadata['description'] = 'Total of reactive nitrogen emissions. LCIA method for pressures on planetary boundary for nitrogen'
    
    cfs = [[('biosphere3', '4841a0fe-c250-4a39-94a1-1bc31426c0f1'), 0.368421053], #Nitrogen oxide 'air', 'lower stratosphere + upper troposphere'
       [('biosphere3', 'd068f3e2-b033-417b-a359-ca4f25da9731'), 0.368421053], #Nitrogen oxide 'air', 'urban air close to ground'
       [('biosphere3', 'c1b91234-6f24-417b-8309-46111d09c457'), 0.368421053], #Nitrogen oxide 'air'
       [('biosphere3', '9115356e-a534-4329-9ec6-d9208720241b'), 0.368421053], #Nitrogen oxide 'air', 'low population density, long-term'
       [('biosphere3', '77357947-ccc5-438e-9996-95e65e1e1bce'), 0.368421053], #Nitrogen oxide 'air', 'non-urban air or from high stacks'
       [('biosphere3', '0f440cc0-0f74-446d-99d6-8ff0e97a2444'), 0.823529412], #Ammonia 'air', 'non-urban air or from high stacks'
       [('biosphere3', '87883a4e-1e3e-4c9d-90c0-f1bea36f8014'), 0.823529412], #Ammonia 'air'
       [('biosphere3', '9990b51b-7023-4700-bca0-1a32ef921f74'), 0.823529412], #Ammonia 'air', 'urban air close to ground'
       [('biosphere3', '2b50f643-216a-412b-a0e5-5946867aa2ed'), 0.823529412], #Ammonia 'air', 'low population density, long-term'
       [('biosphere3', '8494ed3c-0416-4aa5-b100-51a2b2bcadbd'), 0.823529412], #Ammonia 'air', 'lower stratosphere + upper troposphere'      
       [('biosphere3', '774c181d-18a7-4096-aa99-56801ef6b909'), 0.222222222], #Nitrate 'soil'
       [('biosphere3', '43c700bb-0b3b-4fb1-8bd1-3d1da82b6844'), 0.222222222], #Nitrate 'water', 'ocean'
       [('biosphere3', '5e7cf95c-9cc3-4479-89af-55377b3db99c'), 0.222222222], #Nitrate 'air'
       [('biosphere3', '15ca802b-f541-44aa-bd33-35560a053193'), 0.222222222], #Nitrate 'air', 'urban air close to ground'
       [('biosphere3', 'b9291c72-4b1d-4275-8068-4c707dc3ce33'), 0.222222222], #Nitrate 'water', 'ground-'
       [('biosphere3', '7ce56135-2ca5-4fba-ad52-d62a34bfeb35'), 0.222222222], #Nitrate 'water', 'surface water'
       [('biosphere3', '0e9e6b81-0a68-4350-8368-566c083bd3e0'), 0.222222222], #Nitrate 'air', 'lower stratosphere + upper troposphere'
       [('biosphere3', 'b61057a3-a0bc-4158-882e-b819c4797419'), 0.222222222], #Nitrate 'water', 'ground-, long-term'
       [('biosphere3', '5189de76-6bbb-44ba-8c42-5714f1b4371f'), 0.222222222], #Nitrate 'water'
       [('biosphere3', '205617ae-ebc5-4245-8df6-8710d5d40615'), 0.222222222], #Nitrate 'air', 'low population density, long-term'
       [('biosphere3', 'cbd70647-6237-462a-9d01-d197a8b08506'), 0.222222222], #Nitrate 'air', 'non-urban air or from high stacks'
       [('biosphere3', '996829cc-2d40-418a-beda-7c50399952f9'), 1.0], #Nitrogen 'water', 'ocean'
       [('biosphere3', 'ae70ca6c-807a-482b-9ddc-e449b4893fe3'), 1.0], #Nitrogen 'water', 'surface water'
       [('biosphere3', 'e5ea66ee-28e2-4e9b-9a25-4414551d821c'), 1.0], #Nitrogen 'soil', 'industrial'
       [('biosphere3', 'b748f6f1-7061-4243-89c7-3f2d01dcec07'), 1.0], #Nitrogen 'air'
       [('biosphere3', 'eadc37a4-8b1e-4dd2-8f4a-39d89d5f39ba'), 1.0], #Nitrogen 'soil'
       [('biosphere3', 'dcfe0815-6fa3-4e1d-a55e-155b29904f1d'), 1.0], #Nitrogen 'water'
       [('biosphere3', '2a1c80de-a083-470b-80dd-ba11a5aeea8c'), 0.153846154], #Tetramethyl ammonium hydroxide, urban air close to ground
       [('biosphere3', '11f41c41-7733-49bc-b1b1-1f00fbade521'), 0,291666667], #Ammonium carbonate 'air', 'urban air close to ground'
       [('biosphere3', '736f52e8-9703-4076-8909-7ae80a7f8005'), 0.777777778], #Ammonium, ion 'water', 'ground-'
       [('biosphere3', '130cedc6-f6ed-4f1b-bd1e-881177f79e74'), 0.777777778], #Ammonium, ion 'water', 'ground-, long-term'
       [('biosphere3', 'bc069d24-fbbd-4c05-8b6e-4089dc8249ae'), 0.777777778], #Ammonium, ion 'water', 'ocean'
       [('biosphere3', '13331e67-6006-48c4-bdb4-340c12010036'), 0.777777778], #Ammonium, ion 'water', 'surface water'
       [('biosphere3', 'fb005c47-7b90-41f3-a5ca-f0eb11db354a'), 0.777777778], #Ammonium, ion 'water'
       [('biosphere3', '15cfc784-a719-4230-ad2e-f4104d56c427'), 1], #Nitrogen, organic bound 'water', 'ground-, long-term'
       [('biosphere3', 'd43f7827-b47b-4652-8366-f370995fd206'), 1], #Nitrogen, organic 'water', 'surface water'
       [('biosphere3', 'a703733d-fabc-487b-826a-06c11ac4c0c6'), 1], #Nitrogen, organic 'water'
       [('biosphere3', 'b646bb3e-65e2-4f85-8376-9408e94e4b59'), 1], #Nitrogen, organic 'water', 'ground-'
       [('biosphere3', 'b646bb3e-65e2-4f85-8376-9408e94e4b59'), 1]] #Nitrogen, organic 'water', 'ocean'
    rNE.validate(cfs)
    rNE.write(cfs)
    
    #load to excel file############
    flows=[]
    cfs_rne=[]
    for cf in cfs:
        flows.append(cf[0])
        cfs_rne.append(cf[1])
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs_rne})
    df_cfs.to_excel(r""+this_dir+"\characterization_factors_reactive_nitrogen_emissions.xlsx", sheet_name='cfs')
     ###############################
    return()

rne_setup()