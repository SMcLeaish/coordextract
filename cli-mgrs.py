import mgrs
import sys
import pyperclip as pc
lat = sys.argv[1]
long = sys.argv[2]
lat = lat.replace(',',"")
long =  long.replace(',',"")
m = mgrs.MGRS()
c = m.toMGRS(lat, long)

print(c)
pc.copy(c)
