import csv
import json
from datetime import datetime
import gspread
import os
from pathlib import Path


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
# month = 12
# monthPrefix = '24-12-'
# prevMonth = 11
# prevMonthPrefix = '24-03-'



lastFile = f'monthly_data_series/{prevMonthPrefix}data_series.json'
targetFile = f'monthly_data_series/{monthPrefix}data_series.json'
packageLookupFile = f'process_files/package_title_lookup/{monthPrefix}package_title_lookup.json'


def getDataseriesIndex(seriesID):
	index = -1
	count = 0
	for series in dataseries:
		if seriesID == series['id']:
			index = count
		count=count+1
	return index

def transformDataseriesToNewForm(dataseries):
	output = []
	for key in dataseries:
		for series in dataseries[key]:
			series['type'] = key
			output.append(series)
	return output

def highestDataseriesID(dataseries):
	maxID = 0
	for series in dataseries:
		if int(series['id']) > maxID:
			maxID = int(series['id'])
	return maxID

def signInGoogleSheets():
	if "credentials" in os.environ:
		credentials = json.loads(os.environ['credentials'])
	else:
		credFile = 'keys/credentials.json'

		with open(credFile) as json_file:
			credentials = json.load(json_file)

	gc = gspread.service_account_from_dict(credentials)

	return gc

def downloadGoogleSheets():
	title =  monthPrefix+'checks'
	gc = signInGoogleSheets()
	print(title)
	sh = gc.open(title)

	sheets = sh.worksheets()

	changeFiles = []
	newFiles = []
	fileDir = f'process_files/csv_outputs/{monthPrefix[:-1]}/'
	print(fileDir)
	for sheet in sheets:
		Path(fileDir).mkdir(parents=False, exist_ok=True)
		fileName = monthPrefix+'checks - '+sheet.title+'.csv'
		if 'matchedToOne' in sheet.title:
			changeFiles.append(fileDir+fileName)
		if 'matchedToMany' in sheet.title:
			changeFiles.append(fileDir+fileName)
		if 'cods' in sheet.title:
			changeFiles.append(fileDir+fileName)
		if 'new' in sheet.title:
			newFiles.append(fileDir+fileName)
		with open(fileDir+fileName, 'w', newline='', encoding='utf-8') as f:
		    writer = csv.writer(f)
		    writer.writerows(sheet.get_all_values())
	return [changeFiles,newFiles]

[changeFiles,newFiles] = downloadGoogleSheets()

with open(lastFile, encoding='utf-8') as json_file:
	dataseries = json.load(json_file,)

with open(packageLookupFile, encoding='utf-8') as json_file:
	packageLookup = json.load(json_file)

for file in changeFiles:
	print(file)
	with open(file, 'r') as csvfile:
		reader = csv.reader(csvfile)
		next(reader)
		for row in reader:
			if row[0] in(['Approve','Approved']) or row[0] in(['Exclude','Excluded']):
				dataseriesID = row[6]
				if dataseriesID[0:5] == 'none|':
					dataseriesID = dataseriesID[5:]
				if row[0] in(['Exclude','Excluded']):
					dataseriesID = 0
				print(dataseriesID)
				datasets = row[7].split('|')
				dataseriesIndex = getDataseriesIndex(int(dataseriesID))
				for dataset in datasets:
					datasetName = packageLookup[dataset]
					dataseries[dataseriesIndex]['datasets'].append({'id':dataset,'key':datasetName})

for file in newFiles:
	with open(file, 'r') as csvfile:
		reader = csv.reader(csvfile)
		currentID = highestDataseriesID(dataseries)
		currentID = currentID + 1
		index = 0
		series = {'id':currentID,'series':'','datasets':[],'count':0,'type':'data series'}
		exclude = False
		dataExcludeIndex = getDataseriesIndex(0)
		for row in reader:
			if index == 0:
				if row[0]=='clean' or row[0]=='Clean':
					series['type']='clean'
				if row[0] in(['Exclude','Excluded']):
					exclude = True
				series['series'] = row[0]
			if index>1:
				if exclude == True:
					dataseries[dataseriesIndex]['datasets'].append({'id':row[0],'key':row[1]})
				else:
					series['datasets'].append({'id':row[0],'key':row[1]})
			index= index+1
		series['count'] = len(datasets)
		dataseries.append(series) 

with open(targetFile, 'w', encoding='utf-8') as f:
	json.dump(dataseries, f, ensure_ascii=False, indent=4)

