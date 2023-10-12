echo "summaries = {" > datasetInfo_fromDAS.py

datasets_query="dataset dataset=/*/Run20*/RAW" 
dasgoclient -query="$datasets_query" > datasets.txt

second_query="summary dataset=\$item" 
while read item; do echo -e '"'$item'" : '  >> datasetInfo_fromDAS.py &&  eval dasgoclient -query=\"$second_query\" >> datasetInfo_fromDAS.py; echo -n ','  >> datasetInfo_fromDAS.py; done <  datasets.txt 

echo "}" >> datasetInfo_fromDAS.py


### summaries['/ZeroBias/Run2023E-v1/RAW'][0]['file_size']
