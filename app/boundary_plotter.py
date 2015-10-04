import shapefile
from glob import glob
import time
import random

def index():
	nyc = grab_nyc_neighborhoods()
	all_neighborhood_coords = {}
	for i in range(len(nyc)):
		my_points = nyc[i].shape.points
		name = str(nyc[i].record[3])
		print name
		new_list = get_neighborhood_coords(my_points)
		all_neighborhood_coords[name] = new_list
	return render_template('index.html', all_neighborhood_coords=all_neighborhood_coords)


# This method transforms the shapefile from zillow and finds all the points for the 
# different neighborhoods around the city
# This can easily be extended to find any neighborhood in the zillow dataset
# This method returns a list of geo objects which come from the shapefile object
def grab_nyc_neighborhoods():
	filename = glob("*.shp")
	ctr = shapefile.Reader(filename[0])
	geomet = ctr.shapeRecords()
	nyc = []
	for geo in geomet:
		if any([place for place in geo.record if type(place) == type(str()) and "New York City" in place]):
			nyc.append(geo)
	return nyc

def get_neighborhood_coords(my_points):
	new_list = []
	for point in my_points:
		temp = []
		temp.append(point[1])
		temp.append(point[0])
		new_list.append(temp)
	return new_list

index()