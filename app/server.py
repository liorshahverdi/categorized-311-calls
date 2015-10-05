from flask import Flask, render_template, url_for
from pymongo import MongoClient
import shapefile
from glob import glob
import time
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
	nyc = grab_nyc_neighborhoods()
	all_neighborhood_coords = {}
	for i in range(len(nyc)):
		my_points = nyc[i].shape.points
		name = str(nyc[i].record[3])
		new_list = get_neighborhood_coords(my_points)
		all_neighborhood_coords[name] = new_list

	neighborhood_data_list = {}

	bronx_dat = categorize_complaints_to_neighborhood("BRONX")
	'''staten_island_dat = categorize_complaints_to_neighborhood("STATEN ISLAND")
	queens_dat = categorize_complaints_to_neighborhood("QUEENS")
	brooklyn_dat = categorize_complaints_to_neighborhood("BROOKLYN")
	manhattan_dat = categorize_complaints_to_neighborhood("MANHATTAN")'''

	neighborhood_data_list = bronx_dat.copy()
	'''
	neighborhood_data_list.update(staten_island_dat)
	neighborhood_data_list.update(queens_dat)
	neighborhood_data_list.update(brooklyn_dat)
	neighborhood_data_list.update(manhattan_dat)
	'''
	return render_template('index.html', all_neighborhood_coords=all_neighborhood_coords, neighborhood_data_list=neighborhood_data_list)

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
			print '\n\n\n\n\n\n'
	return local_temp

app.run(debug=True)