import brightway2 as bw
from brightway2 import *
import pandas as pd     # "high-performance, easy-to-use data structures and data analysis tools" for Python
import os


def bio_setup():
    #Some basic tasks need to be fulfilled to start...
    bio = bw.Database("biosphere3")

    #First, we define a new method called 'biodiversity species loss' - short 'bio'
    bw.Method(('biodiversity', 'species loss', 'total')).register()
    bioSL = bw.Method(('biodiversity', 'species loss', 'total'))
    bioSL.metadata['unit'] = 'species*years'
    bioSL.metadata['description'] = 'Biodiversity species loss based on (E/H/I) ReCiPe Midpoint indictors V1.13. LCIA method for pressures on planetary boundary for biodiversity.'
    
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory

    try: #shortcut: load characterization factors
        #a=1/0 #does'nt work 
        cfs_bioSL_raw=pd.read_excel(r""+this_dir+"\characterization_factors_biodiversity_loss.xlsx",sheet_name='cfs',usecols=['flow','characterization factor'], engine='openpyxl')
        flows=cfs_bioSL_raw['flow'].to_list()
        flows=[x.split(",")[1][2:38] for x in flows] #remove ,
        cfs=cfs_bioSL_raw['characterization factor'].to_list()
        cfs_bioSL=[(('biosphere3',flows[i]), cfs[i]) for i in range(0, len(flows))]
    except:#if not saved before: calculate cfs

        #Than we need to get all methods that need to calculate bio...

        ReCiPe_mid = [method for method in bw.methods if "ReCiPe Midpoint" in str(method)
                 and not "no LT" in str(method)
                 and "V1.13" in str(method)
                 and not "metal depletion" in str(method)
                 and not "particulate matter formation" in str(method)
                 and not "fossil depletion" in str(method)
                 and not "human toxicity" in str(method)
                 and not "ionising radiation" in str(method)
                 and not "photochemical oxidant formation" in str(method)
                 and not "natural land transformation" in str(method)
                 and not "ozone depletion" in str(method)
                 ]

        #And seperate them by their cultural perspective, since we need to average them later

        ReCiPe_mid_E=ReCiPe_mid[0:10]
        ReCiPe_mid_H=ReCiPe_mid[10:20]
        ReCiPe_mid_I=ReCiPe_mid[20:30]

        #Than we define the conversion factors for each method. The unit is [species.years/[unit of method result]].

        conv_f_E=[
              0.0000000135,                   #'water depletion', 'WDP'
              0.0000000017,                   #'marine eutrophication', 'MEP'
              0.000000025,                    #'climate change', 'GWP500'
              0.00000000888,                  #'agricultural land occupation', 'ALOP'
              0.000000000105,                 #'marine ecotoxicity', 'METPinf'
              0.0000000000114,                #'terrestrial ecotoxicity', 'TETPinf'
              0.000000212,                    #'terrestrial acidification', 'TAP500'
              0.000000000695,                 #'freshwater ecotoxicity', 'FETPinf'
              0.00000000888,                  #'urban land occupation', 'ULOP'
              0.000000671072608705938         #'freshwater eutrophication', 'FEP'
                ]
        conv_f_H=[
              0.00000000888,                  #'agricultural land occupation', 'ALOP'
              0.0000000028,                   #'climate change', 'GWP100'
              0.000000212,                    #'terrestrial acidification', 'TAP100'
              0.0000000135,                   #'water depletion', 'WDP'
              0.000000000695,                 #'freshwater ecotoxicity', 'FETPinf'
              0.00000000888,                  #'urban land occupation', 'ULOP'
              0.000000671072608705938,        #'freshwater eutrophication', 'FEP'
              0.0000000017,                   #'marine eutrophication', 'MEP'
              0.0000000000114,                #'terrestrial ecotoxicity', 'TETPinf'
              0.000000000105                  #'marine ecotoxicity', 'METPinf'
                ]
        conv_f_I=[
              0.000000000532,                 #'climate change', 'GWP20'
              0.000000001700,                 #'marine eutrophication', 'MEP'
              0.000000671072608705938,        #'freshwater eutrophication', 'FEP'
              0.000000000000604,              #'water depletion', 'WDP'
              0.000000000695,                 #'freshwater ecotoxicity', 'FETP100'
              0.00000000888,                  #'agricultural land occupation', 'ALOP'
              0.000000000105,                 #'marine ecotoxicity', 'METP100'
              0.0000000000114,                #'terrestrial ecotoxicity', 'TETP100'
              0.000000212,                    #'terrestrial acidification', 'TAP20'
              0.000000008880                  #'urban land occupation', 'ULOP'
                ]


        #Now we have to get the characterisation factors of all methods and convert them by multiplying them by their conversion factor and their weight.

        i=0 #counter
        cfs_E=[] #array of arrays with new characterisation factors in format (flow, characterisation factor)
        for method in ReCiPe_mid_E:
            met=bw.Method(method) #get method
            cfs_old=[(bw.get_activity(flow), cf) for flow, cf in met.load()] #get the old cfs
            cfs_of_method=[] #array with new characterisation factors in format (flow, characterisation factor)
            for cf_old in cfs_old: #for each cf in each method
                flow_name=cf_old[0]  #store flow
                old_cf=cf_old[1]     #store cf value
                new_cf=old_cf*conv_f_E[i] #new cf=conversion factor*old cf
                cf_new=(flow_name, new_cf) #new characterisation factor in tuple format
                cfs_of_method.append(cf_new)
            cfs_E.append(cfs_of_method) #append to array
            i=i+1 #counter up

        i=0 #counter
        cfs_H=[] #array of arrays with new characterisation factors in format (flow, characterisation factor)
        for method in ReCiPe_mid_H:
            met=bw.Method(method) #get method
            cfs_old=[(bw.get_activity(flow), cf) for flow, cf in met.load()] #get the old cfs
            cfs_of_method=[] #array with new characterisation factors in format (flow, characterisation factor)
            for cf_old in cfs_old: #for each cf in each method
                flow_name=cf_old[0]  #store flow
                old_cf=cf_old[1]     #store cf value
                new_cf=old_cf*conv_f_H[i]#new cf=conversion factor 'old cf'
                cf_new=(flow_name, new_cf) #new characterisation factor in tuple format
                cfs_of_method.append(cf_new)
            cfs_H.append(cfs_of_method) #append to array
            i=i+1 #counter up

        i=0 #counter    
        cfs_I=[] #array of arrays with new characterisation factors in format (flow, characterisation factor)
        for method in ReCiPe_mid_I:
            met=bw.Method(method) #get method
            cfs_old=[(bw.get_activity(flow), cf) for flow, cf in met.load()] #get the old cfs
            cfs_of_method=[] #array with new characterisation factors in format (flow, characterisation factor)
            for cf_old in cfs_old: #for each cf in each method
                flow_name=cf_old[0]  #store flow
                old_cf=cf_old[1]     #store cf value
                new_cf=old_cf*conv_f_I[i]#new cf=conversion factor *old cf
                cf_new=(flow_name, new_cf) #new characterisation factor in tuple format
                cfs_of_method.append(cf_new)
            cfs_I.append(cfs_of_method) #append to array
        i=i+1 #counter up



        #E    
        cf_flows_E=[] #empty array soon to filled with char. flow names
        for cfs_method_list in cfs_E:
            for i in range(len(cfs_method_list)):
                cfs=cfs_method_list[i]
                cf_flows_E.append(cfs[0])
        unique_cf_flows_E=sorted(list(dict.fromkeys(cf_flows_E)))    

        agg_cfs_E=[] #empty array soon to filled with aggragated characterisation factors
        for flow in unique_cf_flows_E:
            cf_of_flow=[]
            for cfs_method_list in cfs_E:
                for method in cfs_method_list:
                    if method[0]==flow:
                        cf_of_flow.append(method[1])
            agg_cf=sum(cf_of_flow)
            agg_cfs_E.append(agg_cf)

        new_cfs_E=[]
        for j in range(len(unique_cf_flows_E)):
            new_cfs_E.append((unique_cf_flows_E[j], agg_cfs_E[j]))

        #H
        cf_flows_H=[] #empty array soon to filled with char. flow names
        for cfs_method_list in cfs_H:
            for i in range(len(cfs_method_list)):
                cfs=cfs_method_list[i]
                cf_flows_H.append(cfs[0])
        unique_cf_flows_H=sorted(list(dict.fromkeys(cf_flows_H)))

        agg_cfs_H=[] #empty array soon to filled with aggragated characterisation factors
        for flow in unique_cf_flows_H:
            cf_of_flow=[]
            for cfs_method_list in cfs_H:
                for method in cfs_method_list:
                    if method[0]==flow:
                        cf_of_flow.append(method[1])
            agg_cf=sum(cf_of_flow)
            agg_cfs_H.append(agg_cf)

        new_cfs_H=[]
        for j in range(len(unique_cf_flows_H)):
            new_cfs_H.append((unique_cf_flows_H[j], agg_cfs_H[j]))


        #I
        cf_flows_I=[] #empty array soon to filled with char. flow names
        for cfs_method_list in cfs_I:
            for i in range(len(cfs_method_list)):
                cfs=cfs_method_list[i]
                cf_flows_I.append(cfs[0])
        unique_cf_flows_I=sorted(list(dict.fromkeys(cf_flows_I)))

        agg_cfs_I=[] #empty array soon to filled with aggragated characterisation factors
        for flow in unique_cf_flows_I:
            cf_of_flow=[]
            for cfs_method_list in cfs_I:
                for method in cfs_method_list:
                    if method[0]==flow:
                        cf_of_flow.append(method[1])
            agg_cf=sum(cf_of_flow)
            agg_cfs_I.append(agg_cf)

        new_cfs_I=[]
        for j in range(len(unique_cf_flows_I)):
            new_cfs_I.append((unique_cf_flows_I[j], agg_cfs_I[j]))

        cfs_bioSL=[]
        for k in range(len(unique_cf_flows_E)):
            cf=(new_cfs_E[k][1]+new_cfs_H[k][1])/2 #taking the average of H and E
            if k<len(unique_cf_flows_I):
                if unique_cf_flows_I[k]==unique_cf_flows_E[k]:# if the flow matches, we can sum them up
                    cf=((cf*2/3)+new_cfs_I[k][1]/3) 
            flow=sorted(unique_cf_flows_E)[k]
            cfs_bioSL.append((flow, cf)) #nicely put together in a tuple
            
            
        #load to excel file############
        flows=[]
        cfs=[]
        for cf in cfs_bioSL:
            flows.append(cf[0].key)
            cfs.append(cf[1])

        df_cfs=pd.DataFrame({'flow': flows, 'characterization factor':cfs})
        df_cfs.to_excel(r""+this_dir+"\characterization_factors_biodiv.xlsx", sheet_name='cfs')
        ###############################    

    bioSL.write(cfs_bioSL)
    return()


bio_setup()