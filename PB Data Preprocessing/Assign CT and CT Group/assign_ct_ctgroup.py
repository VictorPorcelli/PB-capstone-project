import pandas as pd
import json
from shapely.geometry import shape, Point, Polygon, MultiPolygon
from shapely.ops import nearest_points
import geopandas as gpd
import geopy.distance

import requests
import censusgeocode as cg

projects_data = pd.read_csv("discr_budget_fy_09_17 copy.csv")

with open("2010_census_tracts_edited copy.geojson") as f:
    ct_js = json.load(f)

#assign census tracts using lat/long and the DCP geojson
def fill_ct(row):
    ct = ""
    
    try:
        point = Point(float(row['longitude']), float(row['latitude']))
        for feature in ct_js['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                ct = str(feature['properties']['BoroCT2010'])
                break
    except:
        pass

    return ct

projects_data['CT (lat/long)'] =  projects_data.apply(fill_ct, axis = 1)

#add a flag if the CD does not match it's origin CD
cds_and_tracts = open("cds_and_tracts.csv", "r")
cd_ct_combos = []

for line in cds_and_tracts:
    if line.find("Council District") == -1:
        line = line.split(",")
        cd_ct_combos.append([line[0], line[1]])

def flag_ct(row):
    origin_cd = str(row['orcd'])
    tract = str(row['CT (lat/long)'])
    cd = ""
    flag = 0

    for cd in cd_ct_combos:
        if tract in cd[1]:
            cd = str(cd[0])
            break

    if origin_cd.find(","):
        possible_cds = origin_cd.split(",")
        flag_bool = True
        
        for val in possible_cds:
            if val.strip() == cd:
                flag_bool = False

        if flag_bool:
            flag = 1
                
    elif cd != origin_cd:
        flag = 1

    return flag

projects_data['CD Flag'] = projects_data.apply(flag_ct, axis = 1)

with open("City Council Districts.geojson") as d:
    cd_js = json.load(d)

def recode_tract(row):
    origin_cd = str(row['orcd'])
    new_ct = ""
    origin_cds = []

    origin_cd = origin_cd.replace(" ","")
    origin_cds = origin_cd.split(",")
    
    if row['CD Flag'] == 0:
        new_ct = row['CT (lat/long)']
        return new_ct
    else:
        try:
            point = Point(row['longitude'], row['latitude'])
            if len(origin_cds) > 1:
                smallest_dist = 99999.99
                outside_bounds = True

                for feature in cd_js['features']:
                    current_cd = ""
                    cd_match = False
                    old_smallest = smallest_dist
                    for val in origin_cds:
                        if str(feature['properties']['coun_dist']) == val:
                            cd_match = True
                            current_cd = val
                                        
                    if cd_match:
                        multi_poly = shape(feature['geometry'])
                        polygons = list(multi_poly.geoms)
                                    
                        for polygon in polygons:
                            p1, p2 = nearest_points(polygon, point)
                            dist = float(str(geopy.distance.geodesic((p1.y,p1.x),(point.y,point.x))).replace(" km",""))
                            dist_miles = dist * 0.621371

                            if dist_miles<smallest_dist:
                                smallest_dist = dist_miles

                            if smallest_dist < 0.5 and smallest_dist != old_smallest:
                                outside_bounds = False
                                new_point = Point(float(p1.x), float(p1.y))
                                ct_smallest_dist = 0.5
                                for feature in ct_js['features']:
                                    if str(feature['properties']['BoroCT2010']) in cd_ct_combos[int(current_cd)-1][1]:
                                        polygon = shape(feature['geometry'])
                                        p1, p2 = nearest_points(polygon, new_point)
                                        ct_dist = float(str(geopy.distance.geodesic((p1.y,p1.x),(new_point.y,new_point.x))).replace(" km",""))
                                        ct_dist_miles = dist * 0.621371
                                        if ct_dist_miles < ct_smallest_dist:
                                            new_ct = str(feature['properties']['BoroCT2010'])
                                            ct_smallest_dist = ct_dist_miles

                                if new_ct == "":
                                    new_point = Point(float(p2.x), float(p2.y))
                                    ct_smallest_dist = 0.5
                                    for feature in ct_js['features']:
                                        if str(feature['properties']['BoroCT2010']) in cd_ct_combos[int(current_cd)-1][1]:
                                            polygon = shape(feature['geometry'])
                                            p1, p2 = nearest_points(polygon, new_point)
                                            ct_dist = float(str(geopy.distance.geodesic((p1.y,p1.x),(new_point.y,new_point.x))).replace(" km",""))
                                            ct_dist_miles = dist * 0.621371
                                            if ct_dist_miles < ct_smallest_dist:
                                                new_ct = str(feature['properties']['BoroCT2010'])
                                                ct_smallest_dist = ct_dist_miles
                                                
                if outside_bounds or new_ct == "":
                    return "Outside of Bounds"
                else:
                    return new_ct
            else:
                for feature in cd_js['features']:
                    if str(feature['properties']['coun_dist']) == origin_cd:
                        multi_poly = shape(feature['geometry'])
                        polygons = list(multi_poly.geoms)

                        smallest_dist = 99999.99
                        
                        for polygon in polygons:
                            p1, p2 = nearest_points(polygon, point)
                            dist = float(str(geopy.distance.geodesic((p1.y,p1.x),(point.y,point.x))).replace(" km",""))
                            dist_miles = dist * 0.621371

                            if dist_miles<smallest_dist:
                                smallest_dist = dist_miles

                        if smallest_dist < 0.5:
                            new_point = Point(float(p1.x), float(p1.y))
                            ct_smallest_dist = 0.5
                            for feature in ct_js['features']:
                                if str(feature['properties']['BoroCT2010']) in cd_ct_combos[int(origin_cd)-1][1]:
                                    polygon = shape(feature['geometry'])
                                    p1, p2 = nearest_points(polygon, new_point)
                                    ct_dist = float(str(geopy.distance.geodesic((p1.y,p1.x),(new_point.y,new_point.x))).replace(" km",""))
                                    ct_dist_miles = dist * 0.621371
                                    if ct_dist_miles < ct_smallest_dist:
                                        new_ct = str(feature['properties']['BoroCT2010'])
                                        ct_smallest_dist = ct_dist_miles

                            if new_ct == "":
                                new_point = Point(float(p2.x), float(p2.y))
                                ct_smallest_dist = 0.5
                                for feature in ct_js['features']:
                                    if str(feature['properties']['BoroCT2010']) in cd_ct_combos[int(origin_cd)-1][1]:
                                        polygon = shape(feature['geometry'])
                                        p1, p2 = nearest_points(polygon, new_point)
                                        ct_dist = float(str(geopy.distance.geodesic((p1.y,p1.x),(new_point.y,new_point.x))).replace(" km",""))
                                        ct_dist_miles = dist * 0.621371
                                        if ct_dist_miles < ct_smallest_dist:
                                            new_ct = str(feature['properties']['BoroCT2010'])
                                            ct_smallest_dist = ct_dist_miles

                if new_ct == "":
                    return "Outside of Bounds"
                else:
                    return new_ct
        except:
            return new_ct

projects_data['Recoded CT'] = projects_data.apply(recode_tract, axis = 1)

def fill_group(row):
    arr = []
    cluster = ""
    cd = ""

    new_tract = str(row['Recoded CT'])
    if new_tract != "Outside of Bounds":
        try:
            for feature in ct_js['features']:
                if str(feature['properties']['BoroCT2010']) == new_tract:
                    cluster = str(feature['properties']['CTCluster'])
                    cd = cluster[cluster.index("CD")+2:cluster.index("CD")+4]
                    cd = cd.replace(".","")
                    break
        except:
            pass

    arr.append(cluster)
    arr.append(cd)
    
    return pd.Series(arr)

projects_data[['CT Group', 'CD-final']] = projects_data.apply(fill_group, axis = 1)

projects_data.to_csv('discr_budget_fy_09_17_03.28.22.csv')




