# datasetPlots
Code to make historical plots about dataset rate, cross section, data, etc...

- Simply run `python3 plot.py` to make the final plots (it requires ROOT):
```
git clone git@github.com:silviodonato/datasetPlots.git
cd datasetPlots
python3 plot.py
```


Note that this code will use two files as input:
  - `datasetInfo_fromDAS.py` which contains the information about datasets from DAS.
It can be updated running `bash make_datasetInfo_fromDAS.sh`. It uses `dasgoclient` and therefore requires a CMSSW area and `voms-proxy-init --voms cms --valid 168:00`.
  - `recorded_lumi_fromOMS.py`which contains the information about eras, integrated luminosity, and time. 
It can be updated with `python3 make_recorded_lumi_fromOMS.py`. It works from `lxplus` and can also work also from a local computer if a OMS secret key is defined in [this location](https://github.com/silviodonato/datasetPlots/blob/main/tools.py#L12). This code is based on [OMS_ntuplizer](https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer#oms-ntuplizer) 
