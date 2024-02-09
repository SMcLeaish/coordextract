from xml.dom import minidom
import csv
from itertools import zip_longest
gpx = "data.gpx"
xml = minidom.parse(gpx)
trkpts = xml.getElementsByTagName("rtept")
lats = []
lons = []
for trkpt in trkpts:
    lat = float(trkpt.attributes["lat"].value)
    lon = float(trkpt.attributes["lon"].value)
    lats.append(lat)
    lons.append(lon)
d = [lats, lons]
export_data = zip_longest(*d, fillvalue = '')
with open('locations.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
    wr = csv.writer(myfile)
    wr.writerow(("Lat","Lon"))
    wr.writerows(export_data)
myfile.close()
