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
The concatenated 'Data series ID' values must be split to separate rows (i.e. only one data series id is allowed per row) and with the desired dataset ids concatenated in the corresponding 'Dataset Names' column (i.e. multiple dataset ids are allowed in this column). The 'Dataset Names' column is only for convenience and does not need to be split.

Approved - adds to data series
Exclude - add to data sets to be excluded (dataseries ID 0)

- cods_{month suffix}.csv
Approved - adds to data series
Exclude - add to data sets to be excluded (dataseries ID 0)

- new_{month suffix}.csv
Create - add to data set
Move to another file and leave as approved

5 - 4_merge_changes.py

All sheets will be downloaded from gsheet and saved as separate CSV in ./process_files/csv_outputs/yy-mm/  
Files created:
1. ./monthly_data_series/yy-mm-dataseries.json
