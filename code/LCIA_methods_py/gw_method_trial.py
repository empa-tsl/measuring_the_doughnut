import brightway2 as bw
from brightway2 import *

def gw_setup():
    #bio = bw.Database("biosphere3")
        
    bw.Method(('green water', 'use', 'total')).register()
    CU = bw.Method(('green water', 'use', 'total'))
    CU.metadata['unit'] = 'm3'
    CU.metadata['description'] = 'Total use of green water volume flow. LCIA method for pressures on planetary boundary for green water (freshwater demand).'

    cfs = [[('biosphere3', 'c5aafa60-495c-461c-a1d4-b262a34c45b9'), 1], #
           [('biosphere3', 'c4a82f46-381f-474c-a362-3363064b9c33'), 1], #
           [('biosphere3', '9e80f7cd-47fa-4c7f-8f2c-bdb9731b3196'), 1], #
      ]
    CU.validate(cfs)
    CU.write(cfs)
    return()
    
gw_setup()
