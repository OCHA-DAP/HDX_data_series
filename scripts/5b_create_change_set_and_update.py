from IPython import embed

import json
import ckanapi, json
import math
from urllib.request import Request, urlopen
from datetime import datetime
import os

def updateDataset(datasetid,dataseries):
	d = {"dataseries_name": dataseries, "id": datasetid}
	print(d)
	data = json.dumps(d)
	data = data.encode()

	req = Request('https://data.humdata.org/api/action/hdx_dataseries_link')

	req.add_header('Content-Type', 'application/json')
	req.add_header('Authorization', authVar['authtoken'])
	req.add_header('User-Agent', 'HDXINTERNAL:DataSeries/Python-urllib/3.9')

	response_dict = json.loads(urlopen(req, data).read())
	
	if(response_dict['success']==True):
		print('success')
	else:
		print('Fail')

	print(datetime.now().time())

def removeDataset(datasetid,dataseries):
	d = {"dataseries_name": dataseries, "id": datasetid}
	print(d)
	data = json.dumps(d)
	data = data.encode()

	req = Request('https://data.humdata.org/api/action/hdx_dataseries_unlink')

	req.add_header('Content-Type', 'application/json')
	req.add_header('Authorization', authVar['authtoken'])
	req.add_header('User-Agent', 'HDXINTERNAL:DataSeries/Python-urllib/3.9')

	response_dict = json.loads(urlopen(req, data).read())
	
	if(response_dict['success']==True):
		print('success')
	else:
		print('Fail')

	print(datetime.now().time())


def downloadCurrentState():

	CKAN_URL = "https://data.humdata.org/"
	"""Base URL for the CKAN instance."""

	def find_datasets(start, rows):
	    """Return a page of HXL datasets."""
	    return ckan.action.package_search(start=start, rows=rows)

	# Open a connection to HDX
	ckan = ckanapi.RemoteCKAN(CKAN_URL)

	result = find_datasets(0, 0)
	result_total_count = result["count"]
	numOfFiles =  result["count"]
	#loops = int(math.ceil(numOfFiles/1000))
	output = []
	loops = 100
	j=0
	for i in range(0, loops):
		print(f'Getting packages from ckan. Loop {i}')
		result = find_datasets(1000*i, 1000)
		packages = result["results"]
		#print(packages)
		output  = output + packages
	with open('process_files/hdxMetaDataScrape_dataseries.json', 'w', encoding='utf-8') as file:
		json.dump(output, file)

def createLookUpFile(packages):

	output2 = {}
	for package in packages:
		if 'dataseries_name' in package:
			output2[package['id']] = package['dataseries_name']

	return output2

#file prefix
month = datetime.now().month
year = datetime.now().year

monthPrefix = str(year)[2:4]+'-'+str(month).zfill(2)+'-'
prevMonth = month-1
prevYear = year
if prevMonth == 0:
	prevMonth = 12
	prevYear = year-1
prevMonthPrefix = str(prevYear)[2:4]+'-'+str(prevMonth).zfill(2)+'-'


#overrides for when not working in the correct month
month = 10
monthPrefix = '25-10-'
prevMonth = 9
prevMonthPrefix = '25-09-'

targetFile = f'monthly_data_series/{monthPrefix}data_series.json'

print(f'monthPrefix is {monthPrefix}.')
print(f'prevMonthPrefix is {prevMonthPrefix}.')

with open(targetFile, encoding='utf-8') as json_file:
	dataseries = json.load(json_file)

if "HDX_auth" in os.environ:
	authVar = json.loads(os.environ['HDX_auth'])
else:
	with open('keys/auth.json', encoding='utf-8') as json_file:
		authVar =  json.load(json_file)



# Comment out the line below to use the existing (presumably recent) copy of the current state to avoid the long process of downloading all packages
downloadCurrentState()

with open('process_files/hdxMetaDataScrape_dataseries.json', 'r', encoding='utf-8') as file:
	packages = json.load(file)

lookUp = createLookUpFile(packages)

index = 0

#embed()


## data series to be added/changed
for series in dataseries:
	print(f'Starting data series index {index}. ID is {series["id"]}.')
	for dataset in series['datasets']:
		if index>0 and series['type']=='excluded':
			if dataset['id'] in lookUp: 
				oldSeries = lookUp[dataset['id']]
				if oldSeries != series['series']:
					print('======= REMOVING DATASET FROM SERIES =======')
					removeDataset(dataset['id'],None)
		if index>0 and series['type']=='data series':
			if dataset['id'] in lookUp: 
				oldSeries = lookUp[dataset['id']]
				if oldSeries != series['series']:
					print('======= MOVING DATASET TO DIFFERENT SERIES =======')
					# print(datetime.now().time())
					updateDataset(dataset['id'],series['series'])
				elif oldSeries == series['series']:
					print('====== LEAVING DATASET IN SAME SERIES ======')
			else:
				print('======= ADDING DATASET TO SERIES =======')
				# print(datetime.now().time())
				try:
					updateDataset(dataset['id'],series['series'])
				except:
					print('404 in updating')
			
	index = index+1

#data series to be removed

for series in dataseries:
	for dataset in series['datasets']:
		if dataset['id'] in lookUp:
			del lookUp[dataset['id']]

# this section is not currently working
# for dataset in lookUp:
# 	print('removing dataset')
# 	print(dataset)
# 	removeDataset(dataset['id'],None)

