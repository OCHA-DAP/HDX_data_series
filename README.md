# HDX_data_series

1 - 1_scrape_HDX_and_create_lookups.py

This script downloads the latest meta from HDX from which the clustering will be made. In addition it create a lookup file for getting the package name from a package ID used by later scripts.

Files created:

1. process_files/HDXMetaDataScrape/{month prefix}hdxMetaDataScrape.json
2. process_files/package_title_lookup/{month prefix}package_title_look_up.json

2 - 2_tag_hash_analysis.py

This script creates clusters which are data series from the latest meta data scrape

Input files:
1. process_files/HDXMetaDataScrape/{month prefix}hdxMetaDataScrape.json
2. process_files/package_title_lookup/{month prefix}package_title_look_up.json

Files created:
1. /process_files/initial_clustering/{month prefix}data_series_first_cluster

3 - 3_compare_to_last_set.py

This scripts compares the new clustering against the old clustering and creates change files for approval

Input files:
1. /process_files/initial_clustering/{month prefix}data_series_first_cluster.json
2. /monthly_data_series/{month prefix}data_series.json
3. /process_files/package_title_lookup/{month prefix}package_title_lookup.json

Files created:
1. cods_{month suffix}.csv
2. matchedToMany_{month suffix}.csv
3. matchedToOne_{month suffix}.csv
4. new_{month suffix}.csv

4 - These files are exported to a google spreadsheet and then reviewed.  In the first coloumn indicate what action should be taken

- matchedToOne_{month suffix}.csv
Approved - adds to data series
Exclude - add to list of data sets to be excluded (dataseries ID 0)

- matchedToMany_{month suffix}.csv
choose which data series for it to be added to in the match column. Delete the other IDs. Split the row into two if it matches two.  Ensure the dataset ID columns is split correctly

Approved - adds to data series
Exclude - add to data sets to be excluded (dataseries ID 0)

- cods_{month suffix}.csv
Approved - adds to data series
Exclude - add to data sets to be excluded (dataseries ID 0)

- new_{month suffix}.csv
Create - add to data set
Move to another file and leave as approved

5 - 4_merge_changes.py

Download the 4 spreadsheets for google drive as CSV and rename

Input files:
1. {month}_cods_approved.csv
2. {month}_matchedToMany_approved.csv
3. {month}_matchedToOne_approved.csv
4. {month}_new_approved.csv

Files created:
data_series_{month suffix}