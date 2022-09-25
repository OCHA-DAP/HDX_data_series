#########################################
### create search index for browsing site
#########################################

# improvements to make
# don't allow country tags to be secondary tag of another country

import json
import os
import csv
import Levenshtein
from difflib import SequenceMatcher
import operator


def substringCounter(names):
	substring_counts={}
	for i in range(0, len(names)):
	    for j in range(i+1,len(names)):
	        string1 = names[i]
	        string2 = names[j]
	        match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
	        matching_substring=string1[match.a:match.a+match.size]
	        if(matching_substring not in substring_counts):
	            substring_counts[matching_substring]=1
	        else:
	            substring_counts[matching_substring]+=1

	return (max(substring_counts.items(), key=operator.itemgetter(1))[0])

def regroupOnName(series):
	output = {}
	for row in series:
		seriesValue = row[1]+' '+row[0]
		if seriesValue in output:
			output[seriesValue][1] = output[seriesValue][1] + ' & ' + row[1]
			output[seriesValue][2] = output[seriesValue][2] + ' & ' + row[2]
			output[seriesValue][3] = output[seriesValue][3] + ' & ' + row[3]
			output[seriesValue][4] = output[seriesValue][4] + row[4]
		else:
			output[seriesValue] = row

	outputseries = []
	for key in output:
		outputseries.append(output[key])
	return outputseries

packageFile = 'hdxMetaDataScrape.json'

print('Loading file')
with open(packageFile) as json_file:
	packages = json.load(json_file)

output = {};

for package in packages:
	if package['metadata_created']<'2022-01-01':
		taglist = []
		for tag in package['tags']:
			taglist.append(tag['display_name'])
		taglist = sorted(taglist)
		hashInput = package['organization']['title'] + ''.join(taglist)
		hashValue = hash(hashInput)
		batch = ''
		try:
			batch = package['batch']
		except:
			print('No batch')
		if hashValue in output:
			output[hashValue]['titles'].append(package['title'])
			output[hashValue]['batch'].append(batch)
		else:
			output[hashValue] = {'titles':[package['title']],'org':package['organization']['title'],'tags':taglist,'batch':[batch]}

count = 0
csvOutput = []
for key in output:
	series = output[key]
	if len(series['titles'])>2 and len(series['tags'])>0:
		print(series)
		count = count+1
		#name = Levenshtein.quickmedian(series['titles'])
		#print(name)
		name = substringCounter(series['titles'])
		print(name)
		csvOutput.append([name,series['org'],'|'.join(series['tags']),'|'.join(series['batch']),len(series['titles'])] + series['titles'])

csvOutput = regroupOnName(csvOutput)

with open("series_january.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csvOutput)