from parsers.gpx import parse_gpx_geo_data 

def main():
    gpxfile = './fells_loop.gpx'
    waypoints, trackpoints, routepoints = parse_gpx_geo_data(gpxfile)
    print("waypoints:", waypoints)
    print("trackpoints:", trackpoints)
    print("routepoints:", routepoints)
if __name__== '__main__':
    main()

