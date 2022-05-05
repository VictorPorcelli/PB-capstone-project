import pandas as pd
import json
from shapely.geometry import shape, Point

import requests
import censusgeocode as cg

#create a dataframe using the csv
budget_info = pd.read_csv("discr_budget_fy_09_17 copy.csv")

ct_clusters = open('ct_clusters_named.csv', 'r')
clusters = [[]]

for line in ct_clusters:
    if line.find("Council") == -1:
        line = line.split(",")
        census_tracts = line[2].split(" ")
        for tract in census_tracts:
            clusters[0].append(tract)
            clusters.append(line[1])
            
ct_clusters.close()

'''
#response = cg.coordinates(x = row['longitude'], y =row['latitude'])
response = cg.coordinates(x = -73.86538, y =40.8868801, timeout = 3)
#tract = str(response['Census Tracts'][0]['TRACT CODE'])
print(response['Counties'][0]['COUNTY'])
'''


def fill_cluster(row):
    cluster = ""
    try:
        int(row['longitude'])
        response = cg.coordinates(x = row['longitude'], y =row['latitude'], timeout = 5)
        tract = str(response['Census Tracts'][0]['TRACT'])
        county_code = str(response['Counties'][0]['COUNTY'])

        if county_code == '061':
            tract = '1'+tract
        elif county_code == '005':
            tract = '2'+tract
        elif county_code == '047':
            tract = '3'+tract
        elif county_code == '081':
            tract = '4'+tract
        elif county_code == '085':
            tract = '5'+tract

        cluster = clusters[clusters[0].index(tract)+1]
    except:
        pass

    return cluster

budget_info['CT Cluster'] = budget_info.apply(fill_cluster, axis = 1)

budget_info.to_csv('discr_budget_fy_09_17_CTClusters.csv')
