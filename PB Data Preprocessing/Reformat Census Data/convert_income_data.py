clusters = open('ct_clusters_named.csv','r')
clusters_and_tracts = []
tally = 0
for line in clusters:
    if line.find("Council") == -1:
        line = line.split(",")
        clusters_and_tracts.append([line[1], line[2]])
        #tally+=len(line[2].split(" "))
clusters.close()

income_data = open('ACSST5Y2011.S1903_data_with_overlays_2022-02-01T183920 copy.txt','r')
outfile = open('income_data_clustered.csv','w')
outfile.write("Census Tract, Cluster, Median Income \n")

for line in income_data:
    if line.upper().find("ID") == -1:
        line = line.split("\t")
        ct = line[0]
        ct = ct[len(ct)-6:]
        
        if line[1].upper().find("BRONX") != -1:
            ct = "2"+ct
        elif line[1].upper().find("KINGS") != -1:
            ct = "3"+ct
        elif line[1].upper().find("NEW YORK COUNTY") != -1:
            ct = "1"+ct
        elif line[1].upper().find("QUEENS") != -1:
            ct = "4"+ct
        elif line[1].upper().find("RICHMOND") != -1:
            ct = "5"+ct
            
        found = False
        for cluster in clusters_and_tracts:
            cts_in_cluster = cluster[1].split(" ")
            for val in cts_in_cluster:
                if val == ct:
                    found = True
            if found:
                outfile.write(ct+","+cluster[0]+","+str(line[62])+"\n")
                break

        #if found == False:
            #print(ct)
            #print(line[0])
            #print()

#print("Tally:")
#print(tally)

outfile.close()
income_data.close()
