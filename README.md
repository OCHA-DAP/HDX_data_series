# HDX_data_series

1 - .\scripts\1_scrape_HDX_and_create_lookups.py

This script downloads the latest meta from HDX from which the clustering will be made. In addition it creates a lookup file for getting the package name from a package ID used by later scripts.

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
Approved - adds to data series. Need to make sure only one value in "Data series ID" column.
Exclude - add to list of data sets to be excluded (dataseries ID 0)

- matchedToMany_{month suffix}.csv
The concatenated 'Data series ID' values must be split to separate rows (i.e. only one data series id is allowed per row) and with the desired dataset ids concatenated in the corresponding 'Dataset Names' column (i.e. multiple dataset ids are allowed in this column). The 'Key' column should have only one value: 'data series' or 'excluded'. The 'Dataset Names' column is only for convenience and does not need to be split.

Approved - adds to data series
Exclude - add to data sets to be excluded (dataseries ID = 0)

- cods_{month suffix}.csv
Approved - adds to data series. For AB, set 'Data series ID' to 12. For PS, set 'Data series ID' to 13.
Exclude - add to data sets to be excluded (dataseries ID = 0)

- new_{month suffix}.csv
Add the desired data series name in cell A1 to create a new series. 
To prevent datasets from being included, delete them from the list.
To ignore this tab completely, delete it from the gsheet. If the sheet remains and cell A1 is empty, then a new no-name dataseries is created in the json file (not sure if that can make it's way to HDX or not).

5 - 4_merge_changes.py

All sheets will be downloaded from gsheet and saved as separate CSV in ./process_files/csv_outputs/yy-mm/  

Files created:
1. ./monthly_data_series/yy-mm-dataseries.json

6 - 5b_create_change_set_and_update.py (note that script 5a was an initial setup script is should no longer be needed)

This file compares the current state of HDX (it downloads all metadata for public datasets), with the yy-mm-dataseries.json generated in the previous step and decides what kind of update to make. 

TODO: This script tries to update any deleted or private datasets that are in the json (from past runs). To the script, they appear to be new (i.e. they are not assigned to a dataseries because their metadata is not in the package metadata download which is limited to only public datasets), but they appear in the json because they are grandfathered in from previous runs. So the script performs an update to all of them. This are many like this and it makes the update slow. A future improvement would be to include deleted/private datasets in the "current state" download so they they would be skipped. This also means that deleted datasets are in some data series (example: https://data.humdata.org/dataset/d5188a72-05f5-407e-b852-17da5ad71e31), which probably should be cleaned up.


The remaining scrips (6, 7, 8) are utilties and not run as part of the monthly update.
