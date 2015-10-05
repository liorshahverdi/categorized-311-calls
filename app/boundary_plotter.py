import shapefile
from glob import glob
import time
import random
import json
from pymongo import MongoClient
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def index():
	#cursor = db.complaints.find({'Complaint Type': 'Blocked Driveway'})
	nyc = grab_nyc_neighborhoods()
	all_neighborhood_coords = {}
	for i in range(len(nyc)):
		my_points = nyc[i].shape.points # extract that neighboorhods border coordinates
		neighborhood_name = str(nyc[i].record[3]) # name of neighborhood
		new_list = get_neighborhood_coords(my_points)
		all_neighborhood_coords[neighborhood_name] = new_list
	num_complaints_by_neighborhood = {}
	bronx_dat = categorize_complaints_to_neighborhood("BRONX")
	print 'finished bronx.'
	staten_island_dat = categorize_complaints_to_neighborhood("STATEN ISLAND")
	print 'finished staten island.'
	queens_dat = categorize_complaints_to_neighborhood("QUEENS")
	print 'finished queens.'
	brooklyn_dat = categorize_complaints_to_neighborhood("BROOKLYN")
	print 'finished brooklyn.'
	manhattan_dat = categorize_complaints_to_neighborhood("MANHATTAN")
	print 'finished manhattan.'
	num_complaints_by_neighborhood = bronx_dat.copy()
	num_complaints_by_neighborhood.update(staten_island_dat)
	num_complaints_by_neighborhood.update(queens_dat)
	num_complaints_by_neighborhood.update(brooklyn_dat)
	num_complaints_by_neighborhood.update(manhattan_dat)
	json.dump(num_complaints_by_neighborhood, open("neighborhood_data.txt",'w'))
	print 'Done!'

def categorize_complaints_to_neighborhood(borough):
	local_temp = {}
	client = MongoClient()
	db = client.complaints
	cursor = db.complaints.find({"Borough": borough})
	geolocator = Nominatim()
	n_len = 0
	for complaint in cursor:
		n_len += 1
		incident_address = str(complaint['Incident Address'])
		city = str(complaint['City'])
		query = None
		location = None
		if incident_address != '':
			query = incident_address +' '+ city
		try:
			location = geolocator.geocode(query)
		except GeocoderTimedOut as error_message:
			print ("Error: geocode failed on input %s with message %s"%(query, error_message))

		if location != None:
			neighborhood = location.address.split(', ')[2]
			if neighborhood in local_temp:
				local_temp[neighborhood]['Total Complaints'] += 1
				if complaint['Complaint Type'] in local_temp[neighborhood]:
					local_temp[neighborhood][complaint['Complaint Type']] += 1
				else:
					local_temp[neighborhood][complaint['Complaint Type']] = 1
			else:
				local_temp[neighborhood] = {}
				local_temp[neighborhood]['Total Complaints'] = 1
				type_str = str(complaint['Complaint Type'])
				local_temp[neighborhood][type_str] = 1

			print local_temp
			#print '\n\n\n\n\n\n'
			#print neighborhood_name
			#print complaint
	#print 'Done!'
	return local_temp


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