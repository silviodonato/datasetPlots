## Modified version from https://github.com/silviodonato/OMSRatesNtuple/blob/main/OMS_ntuplizer/OMSAPI_test.py 
## Requires https://github.com/silviodonato/OMSRatesNtuple/blob/main/OMS_ntuplizer/ settings
max_pages = 1000
verbose = False

era = "Run2022G"
dataset = "Muon"

from tools import getOMSAPI, getAppSecret, getOMSdata

omsapi = getOMSAPI(getAppSecret())

def getDatasetEvents(omsapi, runMin, runMax, datasetName, verbose=verbose):
    data = getOMSdata(omsapi, "datasetrates", 
    #    attributes = ["fill_number","rate","counter","last_lumisection_number","first_lumisection_number","run_number","path_name"], 
        attributes = ["rate","events","dataset_name","run_number"], 
        filters = {
            "dataset_name": [datasetName],
            "run_number": [runMin, runMax],
        }, 
        customs = {
            "group[granularity]" : "run"
        },
        max_pages=max_pages,
        verbose=verbose
    )
    count = 0
    for d in data:
        run = d['attributes']['run_number']
        count += d['attributes']['events']
        print(run, d['attributes']['events'])
    return count

query = omsapi.query("eras")
query.set_verbose(verbose)
query.per_page = 1000  # to get all names in one go
query.attrs(["start_fill","end_fill","name"]) #
query.filter("name", era)

resp = query.data()
oms = resp.json()   # all the data returned by OMS
data = oms['data']

out = "recorded_lumi = { # delivered_lumi, recorded_lumi, duration, efficiency_time, efficiency_lumi \n"
eras = []
fill_min, fill_max = data[0]['attributes']['start_fill'], data[0]['attributes']['end_fill']
print(fill_min, fill_max)
query = omsapi.query("fills")
query.attrs(["delivered_lumi","recorded_lumi","duration","runs","first_run_number","last_run_number","fill_number"]) #
query.filter("fill_number", fill_min,"GE")
query.filter("fill_number", fill_max,"LE")
query.per_page = 1000  # to get all names in one go

resp = query.data()
oms = resp.json()   # all the data returned by OMS
data2 = oms['data']
delivered_lumi_tot, recorded_lumi_tot, duration_tot = 0, 0, 0
count = 0
for d2 in reversed(data2):
    print("### Fill = %d ###"%d2['attributes']['fill_number'])
    delivered_lumi, recorded_lumi, duration = d2['attributes']['delivered_lumi'], d2['attributes']['recorded_lumi'], d2['attributes']['duration']
    if delivered_lumi: delivered_lumi_tot += delivered_lumi
    if duration: duration_tot += duration
    if recorded_lumi: recorded_lumi_tot += recorded_lumi
    else: continue ##Ignore empty fills
    run_min, run_max = d2['attributes']['first_run_number'], d2['attributes']['last_run_number']
    events = getDatasetEvents(omsapi, run_min, run_max, dataset)
    print("Run = %d - %d, Count = %d"%(run_min, run_max, events))
    count += events

print(fill_min, fill_max)
print(delivered_lumi_tot, recorded_lumi_tot, duration_tot)
print(era, dataset, count)

