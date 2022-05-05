import pandas as pd
import json
from shapely.geometry import shape, Point, Polygon, MultiPolygon

from shapely.ops import nearest_points
from shapely import wkt
import geopandas as gpd
import geopy.distance

with open("2010_censustracts.geojson") as f:
    ct_js = json.load(f)

with open("City Council Districts.geojson") as g:
    cd_js = json.load(g)

count = 0
count_in = 0
count_out = 0

perfect_fit_cts = [[]]
imperfect_fit_cts = []

for ct_feature in ct_js['features']:
    inside_cd = False
    ct_poly = shape(ct_feature['geometry'])
    ct = ct_feature['properties']['BoroCT2010']
    for cd_feature in cd_js['features']:
        cd_poly = shape(cd_feature['geometry'])
        cd = cd_feature['properties']['coun_dist']
        if cd_poly.contains(ct_poly) and inside_cd == False:
            if cd in perfect_fit_cts[0]:
                perfect_fit_cts[perfect_fit_cts[0].index(cd)+1].append(ct)
            else:
                perfect_fit_cts[0].append(cd)
                perfect_fit_cts.append([cd, ct])
            inside_cd = True
            count_in += 1
    if inside_cd == False:
        intersecting_cds = []
        for cd_feature in cd_js['features']:
            cd_poly = shape(cd_feature['geometry'])
            cd = cd_feature['properties']['coun_dist']
            if cd_poly.intersects(ct_poly):
                  intersecting_cds.append(cd)
        imperfect_fit_cts.append([ct, intersecting_cds])
                  
        count_out += 1

for ct in imperfect_fit_cts:
    cd = ct[1][0]
    if len(ct[1]) == 1:
        if cd in perfect_fit_cts[0]:
            perfect_fit_cts[perfect_fit_cts[0].index(cd)+1].append(ct[0])
            imperfect_fit_cts.remove(ct)
            count_in+=1
            count_out-=1
        else:
            perfect_fit_cts[0].append(cd)
            perfect_fit_cts.append([cd, ct[0]])
            count_in+=1
            count_out-=1
    if ct[1] == "":
        print(ct[0])

outfile = open("cd_tract_combos.csv","w")
outfile.write("Council District, Census Tract \n")

for val in perfect_fit_cts:
    if perfect_fit_cts.index(val) != 0:
        cts = val[1:]
        for ct in cts:
            outfile.write(str(val[0])+",")
            outfile.write(str(ct)+"\n")
            count+=1

for val in imperfect_fit_cts:
    cds = val[1]
    ct = val[0]
    count+=1
    for cd in cds:
        outfile.write(str(cd)+",")
        outfile.write(str(ct)+"\n")

print(count)
            
outfile.close()
