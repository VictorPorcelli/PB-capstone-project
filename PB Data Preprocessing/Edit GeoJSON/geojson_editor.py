import pandas as pd

census_clusters = open("ct_clusters_named.csv")
clusters_and_cts = []
for line in census_clusters:
    if line.find("Council") == -1:
        line = line.split(",")
        clusters_and_cts.append([line[1],line[2],line[0]])
census_clusters.close()

geojson = open("2010_censustracts.geojson","r")
geojson_text = geojson.read()
new_geojson = open("2010_census_tracts_edited.geojson","w")

while (geojson_text.find("BoroCT2010") != -1):
    index = geojson_text.find("BoroCT2010")+15
    boro_ct = geojson_text[index:index+7]

    assigned_cluster = ""
    for cluster in clusters_and_cts:
        cts = cluster[1].split(" ")
        found = False
        for ct in cts:
            if ct == boro_ct and found == False:
                assigned_cluster = cluster[0]
                cd = cluster[2]
                found = True
                break
            elif found:
                break

    new_geojson.write(geojson_text[:index+9]+'\n \t\t\t\t"CTCluster" : "'+str(assigned_cluster)+'",')
    new_geojson.write('\n \t\t\t\t"CD" : "'+str(cd)+'",')
    new_geojson.write(geojson_text[index+9:index+51])

    geojson_text = geojson_text[index+51:]

new_geojson.write(geojson_text)

geojson.close()
new_geojson.close()

