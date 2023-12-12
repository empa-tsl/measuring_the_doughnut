"""
This code removes all land use change inputs to agriculture.
"""

eidb_LUC = bw.Database('ecoinvent 3.8 cutoff_fossilfree_wo_LUC') #set database name
consumers=[]
LOC_markets = [act for act in eidb_LUC if 'land use change' in act['name']]
for market in LOC_markets:
    consumer = [exc.output for exc in market.upstream() if 'land use change' not in exc.output['reference product']]
    consumers+=consumer
    
for consumer in list(set(consumers)):
    consumer['comment']+= ". WARNING: Land use change changed to zero. Assuming no expansion of agricultural area."
    consumer.save()
    for exchange in [exc for exc in consumer.technosphere() if 'land use change' in exc.input['reference product']]:
        exchange.delete()
