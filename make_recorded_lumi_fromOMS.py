## Modified version from https://github.com/silviodonato/OMSRatesNtuple/blob/main/OMS_ntuplizer/OMSAPI_test.py 
## Requires https://github.com/silviodonato/OMSRatesNtuple/blob/main/OMS_ntuplizer/ settings

from tools import getOMSAPI, getAppSecret

omsapi = getOMSAPI(getAppSecret())

query = omsapi.query("eras")
query.set_verbose(True)
query.per_page = 1000  # to get all names in one go
query.attrs(["start_fill","end_fill","name"]) #
#query.filter("name", "Run2023A")
query.filter("end_fill", -9076,"GE")

resp = query.data()
oms = resp.json()   # all the data returned by OMS
data = oms['data']

out = "recorded_lumi = { # delivered_lumi, recorded_lumi, duration, efficiency_time, efficiency_lumi \n"
eras = []
for d1 in reversed(data):
    fill_min, fill_max = d1['attributes']['start_fill'], d1['attributes']['end_fill']
    print(fill_min, fill_max)
    eras.append(d1['attributes']['start_fill'])
    query = omsapi.query("fills")
    query.attrs(["delivered_lumi","recorded_lumi","duration"]) #
    query.filter("fill_number", fill_min,"GE")
    query.filter("fill_number", fill_max,"LE")
    query.per_page = 1000  # to get all names in one go

    resp = query.data()
    oms = resp.json()   # all the data returned by OMS
    data = oms['data']
    delivered_lumi_tot, recorded_lumi_tot, duration_tot = 0, 0, 0
    for d2 in reversed(data):
        delivered_lumi, recorded_lumi, duration = d2['attributes']['delivered_lumi'], d2['attributes']['recorded_lumi'], d2['attributes']['duration']
#        print(fill_number, delivered_lumi, recorded_lumi, recorded_lumi_tot)
        if delivered_lumi: delivered_lumi_tot += delivered_lumi
        if recorded_lumi: recorded_lumi_tot += recorded_lumi
        if duration: duration_tot += duration
#        print(d1['attributes']['name'], delivered_lumi_tot, recorded_lumi_tot)
    print(d1['attributes']['name'], delivered_lumi_tot, recorded_lumi_tot, duration_tot)
    out += ' "%s" : (%f, %f, %f), \n'%(d1['attributes']['name'], delivered_lumi_tot, recorded_lumi_tot, duration_tot )

out += "}\n"


f_ = open("recorded_lumi_fromOMS.py",'w')
f_.write(out)
f_.close()


