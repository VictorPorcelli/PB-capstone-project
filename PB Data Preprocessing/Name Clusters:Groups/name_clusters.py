file = open("ct_clusters.csv","r")
outfile = open("ct_clusters_named.csv","w")
outfile.write("Council District, Cluster, Census Tracts \n")

cd_track = ""
counter = 1
for line in file:
    if line.find("CD") == -1:
        line = line.split(",")
        cd = line[0]
        if cd_track == "":
            cd_track = cd  
        elif cd != cd_track:
            cd_track = cd
            counter = 1

        if counter < 10:
            name = "CD"+cd+".0"+str(counter)
        else:
            name = "CD"+cd+"."+str(counter)

        outfile.write(line[0]+","+name+","+line[1].replace("\n","")+"\n")
        counter += 1

file.close()
outfile.close()
