import csv


dataFile = open('resources/311_Service_Requests_from_2010_to_Present.csv')
dataReader = csv.reader(dataFile)
i = 0 
column_names = []
for row in dataReader:
	if i == 0:
		column_names = list(row)
		print column_names
		i+=1
	#else:
		#print(row)