import brightway2 as bw
from brightway2 import *
import os               # to use "operating system dependent functionality"
import numpy as np      # "the fundamental package for scientific computing with Python"
import pandas as pd     # "high-performance, easy-to-use data structures and data analysis tools" for Python
from openpyxl import Workbook
from bw2data.parameters import *
from bw2analyzer import ContributionAnalysis
import seaborn as sns
from scipy import stats
from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import itertools
from itertools import chain
from varname import nameof
from ast import literal_eval as make_tuple
import openpyxl


def setup(mode):
    print('Setting up current project...')
    bw.projects.set_current('FFEI')
    print('Project name set up.')
    bw.bw2setup()
    print('Brightway2 set up. \n')
    
    global this_dir
    this_dir = os.path.dirname(os.path.abspath(globals().get("__file__", "./_"))) #current directory
    
    print('Importing ecoinvent databases...') #edit file paths 
    (path_ei371, ei_db_name371)= (r""+this_dir+"\ecoinvent\datasets", "ecoinvent 3.7.1 cutoff")
    (path_ei38, ei_db_name38)  = (r""+this_dir+"\ecoinvent\ecoinvent 3.8_cutoff_ecoSpold02.7z", "ecoinvent 3.8 cutoff")
    #(path_ei_e, ei_db_name_e)  = (r""+this_dir+"\ecoinvent\\lci-ecoinvent-371_cutoff_ecoSpold02_electric.xlsx", "ecoinvent-371_cutoff_ecoSpold02_electric")
    (path_ei_ff, ei_db_name_ff)= (r""+this_dir+"\ecoinvent\ecoinvent 3.8 cutoff_fossilfree.xlsx", "ecoinvent 3.8 cutoff_fossilfree")

    try:# IMPORT ecoinvent 3.7.1
        import_ecoinvent_database(path_ei371, ei_db_name371,'ecospold')
        print('{0} ready'.format(ei_db_name371))
    except:
        print('Problem occurred while importing ecoinvent database: {0}.'.format(ei_db_name371))
        
    try:# IMPORT ecoinvent 3.8
        import_ecoinvent_database(path_ei38, ei_db_name38,'ecospold')
        print('{0} ready.'.format(ei_db_name38))
    except:
        print('Problem occurred while importing ecoinvent database: {0}.'.format(ei_db_name38))

        
    #######import ecoinvent fossilfree#####
    try:# IMPORT ecoinvent fossilfree
        import_ecoinvent_database(path_ei_ff, ei_db_name_ff,'excel')
        print('{0} ready.'.format(ei_db_name_ff))
    except:
        print('Problem occurred while importing ecoinvent database: {0}.'.format(ei_db_name_ff))
    ###################################
    
    global ei38
    ei38 =bw.Database(ei_db_name38)
    global ei371
    ei371=bw.Database(ei_db_name371)
    
    try:
        global ei_ff
        ei_ff=bw.Database(ei_db_name_ff)
    except:
        print('{0}: Import not possible.'.format(ei_db_name_ff))
        
    print('\nImporting DLS-basket databases...')
    
    global scenarios
    if mode=='test':
        scenarios=pd.read_excel(r""+this_dir+"\DLS_basket_databases\scenarios.xlsx",sheet_name='test',usecols=[1])['name'].tolist() #get scenario names
    else:
        scenarios=pd.read_excel(r""+this_dir+"\DLS_basket_databases\scenarios.xlsx",sheet_name='scenarios',usecols=[1])['name'].tolist() #get scenario names
    
    [import_dls_basket_database(scenario) for scenario in scenarios]
    
    print('All databases imported! \n')
    
    print('Importing additional LCIA methods...')
    define_LCIA_methods()
    print('LCIA methods added and defined!\n')
    print('Setup completed! \n')
    return()

def import_ecoinvent_database(path, name, filetype):
    if name in bw.databases:     
        print("Database {0} has already been imported".format(name))
    elif filetype=='ecospold':
        ei = bw.SingleOutputEcospold2Importer(path, name)
        ei.apply_strategies()
        ei.statistics()
        ei.write_database()
        return()
    elif filetype=='excel' :
        imp = ExcelImporter(path)
        imp.apply_strategies()
        try:
            imp.match_database("biosphere3", fields=('name','unit','categories'))
            imp.add_unlinked_flows_to_biosphere_database()
        except:
            if name=="ecoinvent 3.7.1_cutoff_ecoSpold02_electric":
                imp.match_database("ecoinvent 3.7.1_cutoff_ecoSpold02_electric", fields=('name','unit','categories'))
            else:
                imp.match_database("ecoinvent 3.8 cutoff", fields=('name','unit','location'))  
        imp.match_database(fields=('name', 'unit', 'location'))
        imp.statistics()
        imp.write_excel(only_unlinked=True) #unlinked=False export the full list of exchanges
            
        imp.write_database()
        print('{0} was imported\n'.format(name))
        return()
    
def import_dls_basket_database(name):
    if name in bw.databases:     
        print("Database {0} has already been imported".format(name))
        return()
    try: 
        imp = ExcelImporter("DLS_basket_databases/"+name+".xlsx")
        imp.apply_strategies()
        if 'ff' in name and 'wo_LUC' not in name:
            imp.match_database("ecoinvent 3.8 cutoff_fossilfree", fields=('name','unit','location'))
        elif 'wo_LUC' in name and 'ff' in name:
            print('importing dls no land use: ', name)
            imp.match_database("ecoinvent 3.8 cutoff_fossilfree_wo_LUC", fields=('name','unit','location'))
        else:
            imp.match_database("ecoinvent 3.8 cutoff", fields=('name','unit','location'))

        imp.match_database(fields=('name', 'unit', 'location'))
        imp.statistics()

        imp.write_database()
        print('{0} was imported\n'.format(name))
    except:
        imp.write_excel(only_unlinked=True) #unlinked=False export the full list of exchanges
    return()

def define_LCIA_methods():
    from LCIA_methods_py.bio_method_trial     import bio_setup
    from LCIA_methods_py.CEDel_method_trial   import cedel_setup
    from LCIA_methods_py.cu_method_trial      import cu_setup
    from LCIA_methods_py.odpplus_method_trial import odpplus_setup
    from LCIA_methods_py.p2o_method_trial     import p2o_setup
    from LCIA_methods_py.p2s_method_trial     import p2s_setup
    from LCIA_methods_py.rne_method_trial     import rne_setup
    
    ###### GLOBAL WARMING POTENTIAL ##############################
    print('Defining: Global Warming Potential 100a IPCC 2013')
    global GWP
    GWP = [m for m in bw.methods if 'climate change' in str(m) 
           and 'IPCC 2013' in str(m) 
           and 'GWP 100' in str(m)
           #and 'V1.13' in str(m)
           and not 'LT' in str(m)
            ][0]
    print('{0} is defined'.format(GWP))
    #############################################################
    
    
    ###### CO2 EMISSIONS ########################################
    print('Defining: CO2 emissions')
    global CO2
    CO2 =[m for m in bw.methods if 'CO2, fossil' in str(m)][0]
    print('{0} is defined'.format(CO2))
    ############################################################
    
    
    ##### BIODIVERSITY LOSS ####################################
    global BIO
    print('Defining: biodiversity loss')
    bio_setup()
    BIO =[m for m in bw.methods if 'biodiversity' in str(m)][0]
    print('{0} is defined'.format(BIO))
    ###########################################################
    
    
    ##### CROPLAND USE ########################################
    global CU
    try:
        print('{0} is already defined'.format(CU))
    except:
        print('Defining: cropland use')
        cu_setup()
        CU = [m for m in bw.methods if 'cropland use' in str(m)][0]
        print('{0} is defined'.format(CU))
    ###########################################################
    
    ##### PHOSPHORUS to SOIL ##################################
    global P2S
    try:
        print('{0} is already defined'.format(P2S))
    except:
        print('Defining: phosphorus to soil')
        p2s_setup()
        P2S = [m for m in bw.methods if 'Phosphorus to soil' in str(m) and 'glyphosate' in str(m)][0]
        print('{0} is defined'.format(P2S))
    ##########################################################
    
    ##### PHOSPHORUS to OCEAN ###############################
    global P2O
    try:
        print('{0} is already defined'.format(P2O))
    except:
        print('Defining: phosphorous to ocean')
        p2o_setup()
        P2O = [m for m in bw.methods if 'Phosphorus to ocean' in str(m) and 'phosphate' in str(m)][0]
        print('{0} is defined'.format(P2O))
    #########################################################
    
    
    ##### REACTIVE NITROGEN EMISSIONS #######################
    global RNE
    try:
        print('{0} is already defined'.format(RNE))
    except:
        print('Defining: reactive Nitrogen emissions')
        rne_setup()
        RNE = [m for m in bw.methods if 'reactive nitrogen emissions' in str(m)][0]
        print('{0} is defined'.format(RNE))
    ########################################################
    
    
    ##### CUMULATIVE ENERGY DEMAND ELECTRIC TOTAL ##########
    global CED_el
    try:
        print('{0} is already defined'.format(CED_el))
    except:
        print('Defining: cumulative energy demand')
        cedel_setup()
        CED_el = [m for m in bw.methods if 'cumulative energy demand' in str(m) 
               and 'electric' in str(m) ][0]    
        print('{0} is defined'.format(CED_el))
    #######################################################
    
    
    ##### FRESHWATER DEMAND BLUEWATER #####################
    print('Defining: freshwater demand: blue water')
    global WD
    WD = [m for m in bw.methods if 'water depletion' in str(m) 
           and 'ReCiPe Midpoint (E)' in str(m) 
           and 'LT' in str(m)
           and 'V1.13' in str(m)
      ][0]
    print('{0} is defined'.format(WD))
    #######################################################
    
    
    ##### LAND OCCUPATION/USE #############################
    print('Defining: land occupation/use')
    global LO
    LO =[m for m in bw.methods if 'selected LCI result' in str(m)
        and 'land occupation' in str(m)][0]
    print('{0} is defined'.format(LO))
    #######################################################
    
    
    ##### OZONE DEPLETION POTENTIAL #######################
    global ODPplus
    try:
        print('{0} is already defined'.format(ODPplus))
    except:
        print('Defining: ozone depletion')
        odpplus_setup()
        ODPplus =[m for m in bw.methods if 'including N2O' in str(m)][0]
        print('{0} is defined'.format(ODPplus))
    #######################################################
    
    return()

def calculate_SoSOS(scenario,parent,methods, primary_activities, overwrite):    
    
    flow_amount=1
    level, cutoff =methods[0][2], methods[0][3]
    
    filepath=r"SoSOS/primary_flows_up_to_level_"+str(level)+"_"+scenario+".xlsx"
    
    try:
        pd.read_excel(r"SoSOS/primary_flows_up_to_level_"+str(level)+"_"+scenario+".xlsx")
        is_existent = True
    except:
        is_existent = False
        
    if overwrite and not is_existent: #if data already saved: overwrite option
        get_primary_flows_up_to_level(parent, flow_amount, level, cutoff, primary_activities, filepath)
    
    database=bw.Database(bw.Database(parent['database']).metadata['depends'][0])
    
    #print("Calculating MultiLCA for basket of {0} for {1} methods in database: {2}".format(scenario, len(methods), database))
    LCIA_names  =[method[1] for method in methods] #definition of calculation parameters
    LCIA_methods=[method[0] for method in methods] #definition of calculation parameters 
    
    absolute_scores = []
    for method in LCIA_methods:
        lca = bw.LCA({parent.key: flow_amount}, method) #LCA for total score
        lca.lci()
        lca.lcia()
        absolute_scores.append(lca.score)
        
    results_matrix=contribution(absolute_scores, filepath, LCIA_methods, LCIA_names, database)
    
    count=0
    for results in results_matrix:
        LCIA_name = LCIA_names[count]
        #saves activity with respective share and class in DataFrame
        df=pd.DataFrame(results, columns=['activities','products','amounts','units','location','shares_abs','shares_norm','classification', 'keys'])
        
        df.to_excel(r"SoSOS/sosos_raw_"+str(level)+"_"+scenario+"_"+LCIA_name+".xlsx")
        sharesum=df['shares_norm'].sum() #percent of found shares e.g. 79 %

        SoSOS=get_SoSOS(df, LCIA_name) #extracts SoSOS from raw data ('df')
        SoSOS.rename(columns={'sector':'sector', 'SoSOS':LCIA_name}, inplace=True)

        if count>0: 
            SoSOS_append[LCIA_name]=SoSOS[LCIA_name]
            sharesums.append(sharesum)
        elif count==0:
            sharesums=['found shares', sharesum]
            SoSOS_append=SoSOS

        count=count+1
        
    SoSOS_append=pd.concat([SoSOS_append, pd.DataFrame([sharesums],columns=SoSOS_append.columns)])
    
    filepath_SoSOS_data=r""+this_dir+"\SoSOS\SoSOS_data_"+scenario+".xlsx"
    SoSOS_append.to_excel(filepath_SoSOS_data, sheet_name=scenario, index = False) #saves to excel file

    filepath_sop_data=r""+this_dir+"\FlowsForSoP_"+scenario+".xlsx"
    df_SoP      =df[['activities','products' ,'amounts','units','classification', 'keys']]
    df_SoP.columns = 'activity','product','production','unit','classification','key'
    df_SoP.to_excel(filepath_sop_data, sheet_name=str(LCIA_name), index = False) #<----unlock
    
    print('\nSoSOS saved at directory:\n {0}'.format(filepath_SoSOS_data))
    return()

def calculate_all_SoSOS(mode, overwrite):
    primary_activities=get_primary_activities()
    for scenario in scenarios:
        methods=get_CA_parameters(scenario, mode)
        dls_basket=bw.Database(scenario).get('basket')
        print('---------------------------------------------')
        print('Calculating SoSOS for: {0}.'.format(scenario))
        print('---------------------------------------------')
        calculate_SoSOS(scenario, dls_basket, methods, primary_activities, overwrite)
        print('Calculation of SoSOS for {0} completed!'.format(scenario))
    return()

def get_CA_parameters(scenario, mode):
    filename_CA_param=r""+this_dir+"\ContributionAnalysis_parameters.xlsx"
    if mode=='test':
        CA_param=pd.read_excel(filename_CA_param, sheet_name='test')
        LCIA_methods=[CED_el] #<---- enter LCIA-methods for test run
    else:
        if scenario == 'dls_basket_ff_LD_wb_wo_LUC':
            CA_param=pd.read_excel(filename_CA_param, sheet_name='dls_basket_ff_LD')
        else:
            CA_param=pd.read_excel(filename_CA_param, sheet_name=scenario)
        LCIA_methods=[CO2, GWP, BIO, ODPplus, P2O, P2S, RNE, LO, CU, WD, CED_el]
    
    methods=[]
    for i in range(len(LCIA_methods)):
        method=(LCIA_methods[i], CA_param['short name'][i], CA_param['max level'][i], CA_param['cutoff'][i])
        methods.append(method)
    return methods

def get_primary_activities():
    primary_activities_list = pd.read_excel (r""+this_dir+"\SoSOS\primary_activities_labeled.xlsx")
    primary_activities=[] #empty array
    for i in range(len(primary_activities_list)):
        if primary_activities_list.values[i][1]==1: #if is_primary_activity in table is true
            primary_activities.append(primary_activities_list.values[i][0])  #add to list
    return(primary_activities)

def get_primary_activities_in_level(parent, flow, primary_activities, level, acts_and_amounts, cont, memory, cutoff, switch_to_memory, search_further):
    
    if level==0:
        if parent["name"] in primary_activities:
            acts_and_amounts.append((parent, flow))
    elif not cont or memory==[]:
        if parent["name"] not in primary_activities:
            for exc in [exc for exc in parent.technosphere() if abs(exc.amount*flow)>cutoff 
                        or exc.input['unit'] == 'unit']:
                memory.append((exc.input, exc.amount*flow))
                get_primary_activities_in_level(exc.input, exc.amount*flow, primary_activities, level-1, acts_and_amounts, cont, memory, cutoff, switch_to_memory, search_further)
        if memory!=[]:
            switch_to_memory=True
    elif cont and not memory==[]:
        new_memory=[]
        for act_and_flow in memory:
            act, flow =act_and_flow
            if act["name"] not in primary_activities:
                for exc in [exc for exc in act.technosphere() if abs(exc.amount*flow)>cutoff
                            or exc.input['unit'] == 'unit']:
                    new_memory.append((exc.input, exc.amount*flow))
                    get_primary_activities_in_level(exc.input, exc.amount*flow, primary_activities, 0, acts_and_amounts, cont, memory, cutoff, switch_to_memory, search_further)                
        memory=new_memory
    if memory==[] and switch_to_memory:
        search_further=False
    return acts_and_amounts, memory, switch_to_memory, search_further

def redo_lcia(activity, flow_amount, con_type, total_score):
    """
    DEPRECATED
    """
    lca.redo_lcia({activity: flow_amount})
    if con_type=='relative':
        result=lca.score/total_score 
    else:
        result=lca.score
    clas=next(itertools.dropwhile(lambda s: 'ISIC rev.4 ecoinvent' not in s, activity['classifications']))[1]
    result_array=(activity["name"], activity['reference product'] ,flow_amount, activity["unit"], activity["location"], result, clas, activity['code'])
    return(result_array)

def progress_bar(current, total, bar_length=50):
    fraction = current / total

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    ending = '\n' if current == total else '\r'

    print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)


def get_primary_flows_up_to_level(parent, flow, level, cutoff, primary_activities, filepath):
    print("Collecting all primary flows.\n")
    current_level=0
    memory=[]
    switch_to_memory=False
    search_further=True
    while current_level<=level:
        acts_and_amounts, memory, switch_to_memory, search_further=get_primary_activities_in_level(parent, flow,
                                    primary_activities, current_level, [], True,
                                        memory, cutoff,switch_to_memory, search_further)
        
        if current_level==0 and search_further:
            try:
                acts=[ele[0] for ele in acts_and_amounts]
                amounts=[ele[1] for ele in acts_and_amounts]
            except:
                acts=[]
                amounts=[]
            
            df=pd.DataFrame({"keys": [act["code"] for act in acts], "names": [act["name"] for act in acts], "amounts": amounts})
            df=df.groupby(['keys','names'])['amounts'].sum().reset_index()
            df.to_excel(filepath)
            
        if current_level>0 and len(acts_and_amounts)!=0 and search_further:
            df=pd.read_excel(filepath)
            try:
                prev_keys, prev_amounts, prev_names=df["keys"], df["amounts"], df["names"]
            except: 
                prev_keys, prev_amounts, prev_names=[], [], []
            
            acts=[ele[0] for ele in acts_and_amounts]
            amounts=[ele[1] for ele in acts_and_amounts]
            names=[act["name"] for act in acts]
            
            new_keys=list(prev_keys)+[act["code"] for act in acts]
            new_amounts= list(prev_amounts)+amounts
            new_names=list(prev_names)+names
            
            df_nextlevel=pd.DataFrame({"keys": new_keys,  "names": new_names,"amounts": new_amounts})
            df_nextlevel=df_nextlevel.groupby(['keys','names'])['amounts'].sum().reset_index()
            df_nextlevel.to_excel(filepath)
            
        progress_bar(current_level, level)
        current_level+=1
    print("\nCollected all primary flows up to level "+str(level))
    return filepath

def contribution(absolute_scores, filepath, LCIA_methods, LCIA_names, database):
    df=pd.read_excel(filepath)
    
    print(database)
    activities   = [database.get(key) for key in df["keys"]]
    names        = [act['name'] for act in activities]
    ref_products = [act['reference product'] for act in activities]
    amounts      = df["amounts"]
    units        = [act['unit'] for act in activities]
    locations    = [act['location'] for act in activities]
    classifaction= [next(itertools.dropwhile(lambda s: 'ISIC rev.4 ecoinvent' not in s, act['classifications']))[1] for act in activities]
    codes        = [act['code'] for act in activities]
    
    functional_units = [{act:amount} for act, amount in zip(activities, amounts)]
    bw.calculation_setups['contribution'] = {'inv': functional_units, 'ia': LCIA_methods}
    mlca = bw.MultiLCA('contribution')
    
    results_matrix_list = []
    for i in range(len(LCIA_names)):
        results_abs = list(np.array([mlca.results[j,i] for j in range(len(activities))])) #absolute
        results_norm = list(np.array([mlca.results[j,i] for j in range(len(activities))])/absolute_scores[i]) #normalize
        result_matrix=zip(names, ref_products ,amounts, units , locations, results_abs, results_norm, classifaction, codes)
        results_matrix_list.append(result_matrix)
   
    return(results_matrix_list)


def get_SoSOS(df_shares, LCIA_name):
    #this function aggregates the shares over (1) the division groups after ISIC4 and (2) then over ressource segments.
    
    #aggregate shares by division (1)
    df_sosos_div=aggregated_SoSOS_by_division(df_shares, LCIA_name)

    #aggregate shares by ressource segment (2)
    df_sosos_seg=aggregated_SoSOS_by_segment(df_sosos_div, LCIA_name, df_shares)

    return(df_sosos_seg)

def get_division_for_shares(df_shares, sector_codes):
    division_codes=get_division_codes(sector_codes)     #get codes of divisions (subsector)
    
    share_of_subsector=df_shares.groupby(['classification'])['shares_norm'].sum() #Aggregation of shares over classification
    total_share=share_of_subsector.sum() #total share (probably <100%)
    
    subsectors=list(df_shares['classification']) #get class for each share
    
    ##########
    #df_shares.to_excel(r""+this_dir+"\Results\\test_shares.xlsx")
    ##########
    division=[] #empty array for divisions occuring
    division_short=[] #empty array for division codes
    for subsector in subsectors:
        #find division for classes
        division_name=division_codes['Description'][division_codes.index[division_codes['Code'] == subsector[0:2]].tolist()[0]]
        division.append(division_name)
    return(division, total_share, division_codes)

def get_division_codes(sector_codes):
    divisions=[]
    description=[]
    codes=sector_codes['Code'].to_list()
    for i in range(len(codes)):
        if len(codes[i])==2 or codes[i]=='B' or codes[i]=='D':
            divisions.append(sector_codes['Code'][i])
            description.append(sector_codes['Description'][i])
    division_codes=pd.DataFrame({'Code': divisions, 'Description':description})
    return(division_codes)

def aggregated_SoSOS_by_division(df_shares, LCIA_name):
    sector_codes=get_sector_codes()
                           
    (division, total_share, division_codes)=get_division_for_shares(df_shares, sector_codes)#allocated division to class
        
    df_shares['division']=division #allocates division to each share
    SoSOS_raw=df_shares.groupby(['division'])['shares_norm'].sum()
       
    division_list = sorted(list(dict.fromkeys(division))) #list of unique divisions in occuring divisions
    alldiv_idx=[] #indices where all_div_list meets occuring division list
    SoSOS_idx=[] #indices where SoSOS meets all division list
    for a in list(division_codes['Description']):
        for b in division_list:
            if a==b:
                alldiv_idx.append(list(division_codes['Description']).index(a))
                SoSOS_idx.append(division_list.index(b))
    
    SoSOS=[0]*len(division_codes['Description']) #prelimenary SoSOS
    for i in range(len(alldiv_idx)):
        SoSOS[alldiv_idx[i]]=SoSOS_raw[SoSOS_idx[i]] #allocate to division
    
    df_sosos_div=pd.DataFrame({'sectors':division_codes['Description'], LCIA_name: SoSOS}) #SoSOS for divisions
    df_sosos_div.to_excel(r""+this_dir+"\SoSOS\sosos_div_test.xlsx")
    return(df_sosos_div)

def aggregated_SoSOS_by_segment(df_sosos_div, LCIA_name, df_shares):
    matrix=pd.read_excel(r""+this_dir+"\SoSOS\division_to_segment_matrix.xlsx", "matrix")
    shifts=pd.read_excel(r""+this_dir+"\SoSOS\division_to_segment_matrix.xlsx", "shifts")
    segment_name=get_segment_names() #segment names, e.g., 'Metals, Chemicals,...'
    
    #aggregating the shares over segments
    M        =matrix.iloc[:, 1:matrix.shape[1]].to_numpy() #Matrix conversion: division to segments (9x88)
    
    agg_shares=list(df_sosos_div[LCIA_name])
    
    agg_segment_share=np.dot([agg_shares],M)[0]
    
    
    #balancing the shares that need to be shifted from one segment to another
    Q         =shifts.iloc[:, 2:shifts.shape[1]].to_numpy() #Matrix conversion: shifts to segments (Qx9)
    types     =shifts.iloc[:, 0].tolist()
    products=shifts.iloc[:, 1].tolist()
    
    shift_shares=[]
    for i in range(shifts.shape[0]):
        if types[i]=='product':
            try:
                shift_share=df_shares[df_shares['products']==products[i]]['shares_norm'].sum()
            except:
                shift_share=df_shares[df_shares.eq(products[i]).any(1)]['shares_norm'].sum()
        if types[i]=='class':
            try:
                shift_share=df_shares[df_shares['classification']==products[i]]['shares_norm'].sum()
            except:
                Print('{0}: shifting share failed!'.format(products[i]))

        shift_shares.append(shift_share)
    
    segment_shift_share=np.dot([shift_shares],Q)[0]

    # considering shifted shares with addition or subtraction
    agg_segment_share=np.add(agg_segment_share,segment_shift_share)
        
    #balancing shares to 100%
    K=sum(agg_segment_share)
    
    if any([x<0 for x in agg_segment_share]): #check if all positive
        idx = list([x<0 for x in agg_segment_share]).index(1)
        print('Negative aggregated share in ',segment_names(idx), LCIA_name)
        
    agg_segment_share=[x / K for x in agg_segment_share]
    
    SoSOS=pd.DataFrame({'segment':segment_name, 'SoSOS':agg_segment_share})
    return(SoSOS)

def get_production_DataFrame(scenario, flows_raw):
    amounts    =list(flows_raw.groupby(['key'])['production'].sum()) #list of all production amounts for products aggregation over location
    keys = list(flows_raw.groupby(['key']).groups.keys()) #list of unique product names
    
    activities     =[flows_raw[flows_raw.eq(key).any(1)]['activity'].to_list()[0] for key in keys]
    products       =[flows_raw[flows_raw.eq(key).any(1)]['product'].to_list()[0] for key in keys]
    classifications=[flows_raw[flows_raw.eq(key).any(1)]['classification'].to_list()[0] for key in keys]
    units          =[flows_raw[flows_raw.eq(key).any(1)]['unit'].to_list()[0] for key in keys]
    
    divisions=[classification[0:2] for classification in classifications]
    
    production=pd.DataFrame({'product': products , 'activity': activities, 'amount': amounts, 'unit': units, 'sector': divisions, 'key':keys})
    return(production)

def get_division_code_names(n):
    div_nr=list(range(1,n))
    div=[]
    for i in div_nr:
        if i<10:
            div.append('0'+str(i))
        else:
            div.append(str(i))
    div[88]='R'
    div[82]='O'
    div[75]='N'
    div[66]='L'
    div[56]='J'
    div[53]='I'
    div[47]='H'
    div[43]='G'
    div[39]='F'
    div[33]='D'
    div[3]='B'
    return(div)

def get_sector_codes():
    sector_codes=pd.read_excel(r""+this_dir+"\SoSOS\ISIC4_sector_codes.xlsx")
    return(sector_codes)

def get_products_with_class(keys, classification):
    shift_products=[]
    
    for key in keys:
        try:
            act=ei38.get(key)
            clas=next(itertools.dropwhile(lambda s: 'ISIC rev.4 ecoinvent' not in s, act['classifications']))[1]
        except:
            clas=''
            
        if clas==classification:
            shift_products.append(act['reference product'])
    return(shift_products)
              
def get_div_num(string):
    string = string[string.rindex('SoP'):] #only filename, not path
    intstr=''.join([str(integer) for integer in [int(s) for s in string if s.isdigit()]])
    if intstr[0]=='0': return(int(intstr[1])) 
    else: return(int(intstr))

def get_agg_product_names(segment_name):
    table=pd.read_excel(this_dir+"\\Results\\UI\\product_aggregation_tables.xlsx", sheet_name=segment_name)
    agg_prod_names=table.columns[2:len(table.columns)].to_list()
    return(agg_prod_names)

def check_fuel(activity):
    fuel_data=pd.read_excel(r""+this_dir+"\ecoinvent\\Combustion processes\\fuels.xlsx")
    fuels=fuel_data["fuel activities"].to_list()
    if activity["reference product"] in fuels:
        return True
    else:
        return False
    
def get_combustion_process(activity_to_combust):
    print('THis is new', end='\r')
    for act in ffcomb:
        if activity_to_combust['reference product']+' combustion'==act['name']:
            return(act)
    print('Found no combustion process for ',activity_to_combust['reference product'])
    return []

def diff_list(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))

def get_treatment_processes(db_name, activities, products):
    segment_names     =get_segment_names()                        
    conv_filepath     =r""+this_dir+"\Results\\UI\\conversion_factors.xlsx"
    conv_data         =[pd.read_excel(conv_filepath, sheet_name=segment_name) for segment_name in segment_names]
    conv_activities   =[table['activity'].to_list() for table in conv_data]
    sop_activities    =activities
    sop_products      =products
    
    treatment_keys= []
    for k in range(len(segment_names)):
        factor_list = []
        for activity, product in list(zip(sop_activities[k], sop_products[k])):
            factor = [conv_data[k].loc[(conv_data[k]['activity']==activity['name']) & (conv_data[k]['product']==product)].iat[0,7]][0]
            factor_list.append(factor)
        treatment_keys.append(factor_list)
                            
    treatments=[[bw.Database(db_name).get(key) for key in sector_keys] for sector_keys in treatment_keys]
    return(treatments)

def database2scenario(db_name):
    scen2db=pd.read_excel(this_dir+"\\Results\\UI\\scenario2database.xlsx", sheet_name='sheet')
    scenario=scen2db.iloc[scen2db[db_name].loc[scen2db[db_name]==1].first_valid_index(),0]
    return(scenario)

def scenario2database(scenario):
    scen2db=pd.read_excel(this_dir+"\\Results\\UI\\scenario2database.xlsx", sheet_name='sheet')
    try:
        row=scen2db["scenario/database"].to_list().index(scenario)
    except:
        print(scenario, "is not included in the scenarios.")
    db_names=list(scen2db.columns[1:])    
    scen2db=scen2db.iloc[:,1:].transpose().set_axis(list(scen2db["scenario/database"]),axis=1, inplace=False)
    db_name=db_names[scen2db[scenario].to_list().index(1)]
    return(db_name)

def get_segment_names():
    matrix=pd.read_excel(r""+this_dir+"\SoSOS\division_to_segment_matrix.xlsx", "matrix")
    segment_names=list(matrix.columns.values)[1:len(matrix.columns.values)] #segment names, e.g., 'Metals, Chemicals,...'
    return(segment_names)

def calculate_all_MC(mode, iters):
    if mode=='test':
        methods=[P2S] #<----TEST
        iterations=1000
    else:
        methods=[CO2, GWP, BIO, ODPplus, P2O, P2S, RNE, LO, CU, WD, CED_el]
        iterations=iters
    for scenario in scenarios:
        simulations=calculate_MC(scenario, methods,iterations)
        write_MC_to_excel(simulations, scenario, methods, mode)
    print('Monte-Carlo-Simulations completed!')
    return()

def write_MC_to_excel(simulations, scenario, methods, mode):
    data={methods[j]: simulations[j] for j in range(len(methods))}
    df_mc=pd.DataFrame(data)
    df_mc.to_excel(r""+this_dir+"\Monte-Carlo-Sim_"+scenario+"_"+mode+".xlsx")
    return()
                   
def calculate_MC(scenario, methods, iterations):
    print('Performing Monte-Carlo-Simulation for {0}'.format(scenario))
    database=bw.Database(scenario).get('basket')
    demand = {database: 1}

    store_of_simulations=[]
    for method in methods:
        mc=bw.MonteCarloLCA(demand,method)
        simulations=[]

        for _ in range(iterations):
            next(mc)
            mc.redo_lci(demand)
            simulations.append(mc.score)
    
        store_of_simulations.append(simulations)
    print('Finished Monte-Carlo-Simulation for {0}'.format(scenario))    
    return(store_of_simulations)

def activity_test():
    return(ei38.random())

def database_test():
    return(ei38)

def random_lca():
    method=[m for m in bw.methods if 'water depletion' in str(m)][0]
    act=activity_test()
    lca=bw.LCA({act:1}, method)
    lca.lci()
    lca.lcia()
    return(act, lca)
