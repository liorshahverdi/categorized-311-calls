from pymongo import MongoClient
import csv

client = MongoClient()
db = client.complaints

csv_dataFile = open('resources/311_Service_Requests_from_2010_to_Present.csv')
dataReader = csv.DictReader(csv_dataFile)

# Get our column headers
i = 0
headers = None
for row in dataReader:
	if i == 0:
		headers = list(row)
		break

for eachline in dataReader:
	row = {}
	for field in headers:
		row[field] = eachline[field]
	db.complaints.insert_one(row)
print 'Done!'


'''
result = db.complaints.insert_one (
		{
			"address": {
				"street": "2 Avenue",
	            "zipcode": "10075",
	            "building": "1480",
	            "coord": [-73.9557413, 40.7720266]	
			}
		}
	)
'''