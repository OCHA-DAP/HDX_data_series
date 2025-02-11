import json
import csv
from datetime import datetime
from pathlib import Path
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import gspread
import os
import time

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

def createDataSetLookUp(dataseries):
	datasetLookUp = {}
	for series in dataseries:
		seriesID = series['id']
		for dataset in series['datasets']:
			datasetLookUp[dataset['id']] = {'id':seriesID,'name':series['series'],'type':series['type'],'count':series['count']}
	return datasetLookUp

def listOfKeys(matches):
	output = []
	for key in matches:
		if key!='None':
			output.append(str(key))
	return output

def propertyToList(matches,key):
	output = []
	for match in matches:
		if match!='none':
			output.append(str(match[key]))
	return output

def listOfPropertiesToList(dataseries,key):
	output = []
	for series in dataseries:
		if key!='none':
			output.append(str(series[key]))
	return output


def candidateSeriesCSV(dataseriess):
	output = [['Action','Notes','title','key','Org','count','Data series ID','Dataset IDs','Dataset Names']]
	
	for dataseries in dataseriess:
		unmatchedNames = []
		for dataset in dataseries['unmatched']:
			unmatchedNames.append('=HYPERLINK("https://data.humdata.org/dataset/'+dataset+'","'+titleLookUp[dataset]+'")')
		seriesTitles = '|'.join(listOfPropertiesToList(dataseries['details'],'name'))
		seriesTypes = '|'.join(listOfPropertiesToList(dataseries['details'],'type'))
		counts = '|'.join(listOfPropertiesToList(dataseries['details'],'count'))
		matches = '|'.join(listOfKeys(dataseries['matches']))
		unmatched = '|'.join(dataseries['unmatched'])
		line = ['','',seriesTitles,seriesTypes,dataseries['org'],counts,matches,unmatched]+unmatchedNames
		output.append(line)
	return output

def signInGoogleDrive():
	if "credentials" in os.environ:
		credentials = json.loads(os.environ['credentials'])
	else:
		credFile = 'keys/credentials.json'

		with open(credFile) as json_file:
			credentials = json.load(json_file)

	credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scopes=['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive'])
	service = build('drive', 'v3', credentials=credentials)
	return service


def createSpreadsheet(service,title,destFolderId):
	file_metadata = {
	    'name': title,
	    'mimeType': 'application/vnd.google-apps.spreadsheet',
	    'parents': [destFolderId]
	}

	file = service.files().create(body=file_metadata,supportsAllDrives=True).execute()


def signInGoogleSheets():
	if "credentials" in os.environ:
		credentials = json.loads(os.environ['credentials'])
	else:
		credFile = 'keys/credentials.json'

		with open(credFile) as json_file:
			credentials = json.load(json_file)

	gc = gspread.service_account_from_dict(credentials)

	return gc

def numberToLetters(q):
    """
    Helper function to convert number of column to its index, like 10 -> 'A'
    """
    q = q - 1
    result = ''
    while q >= 0:
        remain = q % 26
        result = chr(remain+65) + result;
        q = q//26 - 1
    return result

def colrow_to_A1(col, row):
    return numberToLetters(col)+str(row)


def update_sheet(ws, rows, left=1, top=1):
    """
    updates the google spreadsheet with given table
    - ws is gspread.models.Worksheet object
    - rows is a table (list of lists)
    - left is the number of the first column in the target document (beginning with 1)
    - top is the number of first row in the target document (beginning with 1)
    """

    # number of rows and columns
    num_lines = len(rows)
    num_columns = max(len(row) for row in rows)
    print(num_columns)
    # selection of the range that will be updated
    cell_list = ws.range(
        colrow_to_A1(left,top)+':'+colrow_to_A1(left+num_columns-1, top+num_lines-1)
    )

    # modifying the values in the range

    for cell in cell_list:
        try:
            val = rows[cell.row-top][cell.col-left]
            cell.value = val
        except:
        	cell.value = None

    # update in batch
    ws.update_cells(cell_list,value_input_option='USER_ENTERED')
    time.sleep(1.1)


lastMonthFile = 'monthly_data_series/'+ prevMonthPrefix +'data_series.json'
thisMonthFile = 'process_files/initial_clustering/'+ monthPrefix +'data_series_first_cluster.json'
lookUpFile = 'process_files/package_title_lookup/'+ monthPrefix +'package_title_lookup.json'

files = os.listdir('monthly_data_series/')

for file in files:
	print(file)

with open(lastMonthFile, encoding='utf-8') as json_file:
	lastMonth = json.load(json_file)

with open(thisMonthFile, encoding='utf-8') as json_file:
	thisMonth = json.load(json_file)

with open(lookUpFile, encoding='utf-8') as json_file:
	titleLookUp = json.load(json_file)

datasetLookUp = createDataSetLookUp(lastMonth)
unmatched = 0

for candidateSeries in thisMonth:
	candidateSeries['matches'] = {'none':0}
	candidateSeries['unmatched'] = []
	candidateSeries['details'] = []
	for dataset in candidateSeries['IDs']:
		if dataset in datasetLookUp:
			dataSeriesID = datasetLookUp[dataset]['id']
			dataSeriesDetails = datasetLookUp[dataset]
			if dataSeriesID in candidateSeries['matches']:
				candidateSeries['matches'][dataSeriesID] = candidateSeries['matches'][dataSeriesID]+1
			else:
				candidateSeries['matches'][dataSeriesID] = 1
				candidateSeries['details'].append(dataSeriesDetails)
		else:
			candidateSeries['matches']['none'] = candidateSeries['matches']['none'] + 1
			unmatched = unmatched + 1
			candidateSeries['unmatched'].append(dataset)
		
summary = {'total':0,'matchedToOne':0,'matchedToMany':0,'new':0,'cods':0}
assessmentSummary = {'total':0,'matchedToOne':0,'matchedToMany':0,'new':0,'cods':0}

output = {'matchedToOne':[],'matchedToMany':[],'new':[],'cods':[]}

for candidateSeries in thisMonth:
	
	summary['total'] = summary['total']+1
	percentNotMatched = candidateSeries['matches']['none'] / len(candidateSeries['IDs'])
	if percentNotMatched < 0.75:
		if len(candidateSeries['matches'])==2:
			if percentNotMatched!=0:
				summary['matchedToOne'] = summary['matchedToOne'] + 1
				assessmentSummary['matchedToOne'] = assessmentSummary['matchedToOne'] + candidateSeries['matches']['none']
				output['matchedToOne'].append(candidateSeries)
		else:
			if percentNotMatched!=0:
				summary['matchedToMany'] = summary['matchedToMany'] + 1
				assessmentSummary['matchedToMany'] = assessmentSummary['matchedToMany'] + candidateSeries['matches']['none']
				output['matchedToMany'].append(candidateSeries)
	else:
		if 'common operational dataset - cod' in candidateSeries['tags']:
			summary['cods'] = summary['cods'] + 1
			assessmentSummary['cods'] = assessmentSummary['cods'] + candidateSeries['matches']['none']
			output['cods'].append(candidateSeries)
		else:
			summary['new'] = summary['new'] + 1
			assessmentSummary['new'] = assessmentSummary['new'] + candidateSeries['matches']['none']
			output['new'].append(candidateSeries)


print('creating spreadsheets')


destFolderId = '1vKD6HRabh1QQ52x15zGhW-NZZFzW5vbO' # gdrive/Data Systems/Projects/Data Series
title =  monthPrefix+'checks'

service = signInGoogleDrive()
createSpreadsheet(service,title,destFolderId)

gc = signInGoogleSheets()

sh = gc.open(title)

url = 'https://data.humdata.org/dataset?dataseries_name='

outputSummary = [['ID','Data series name','Link']]
for series in lastMonth:
	if series['type'] == 'data series':
		name = series['series']
		link = url + series['series']
		row = [series['id'],series['series'],link]
		outputSummary.append(row)

title = 'Last month summary'
worksheet = sh.add_worksheet(title=title, rows=1000, cols=20)
rows = outputSummary

update_sheet(worksheet,rows)

for key in output:
	if key!='new':
		title = key
		worksheet = sh.add_worksheet(title=title, rows=500, cols=20)
		rows = []
		rows = candidateSeriesCSV(output[key])

		update_sheet(worksheet,rows)

for key in output:
	if key=='new':
		index = 1
		for candidateSeries in output[key]:
			title = '|'.join(listOfPropertiesToList(candidateSeries['details'],'name'))
			candidateOutput = [['',''],[candidateSeries['org'],'']]
			for dataset in candidateSeries['unmatched']:
				name = titleLookUp[dataset]
				candidateOutput.append([dataset,name])
			title = 'new_' + str(index)
			worksheet = sh.add_worksheet(title=title, rows=500, cols=20)
			update_sheet(worksheet,candidateOutput)
			index= index+1

outputClean = [['Data series name','Data set name']]
	
title = 'Manual additions to data series'
worksheet = sh.add_worksheet(title=title, rows=500, cols=20)
rows = outputClean

update_sheet(worksheet,outputClean) 

print('Data series count')
print(summary)
print('unmatched')
print(unmatched)
print('assessment summary')
print(assessmentSummary)
