from datasetInfo_fromDAS import summaries

removeEras = [ ##https://cmsoms.cern.ch/cms/fills/summary?cms_era_name=2015E
##    "Run2018D", ## HIon test only in
##    "Run2015A", ## HIon test ? only in 247584 - 247934. See run #247702, low PU fill, fill 3851, LHCf run https://schwick.web.cern.ch/schwick/rctools/dailyReport/detailReport/display/2015-06-12 
    "Run2013A", ## 2.76 TeV https://cmsoms.cern.ch/cms/fills/summary?cms_era_name=2013A
    "Run2015A", ## data taken at 0T, including commissioning runs and low-PU runs for FSQ physics. https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2015Analysis
    "Run2015E",  ## Run 261380 - 261553. No beams.
    "Run2017H", ## low PU SMP "W mass" (fill 6413)
    "Run2017G", ## 5 TeV
    "Run2018E", ## solo un fill (7358) ad altissimo PU (108.128)
    "Run2022A", ## 500 GeV collisions
    "Run2023F", ## High Beta*
#    "Run2022B", ## ok, ramp up
#    "Run2017A", ## ok, ramp up
#    "Run2015B", ## two fills with B=0
#    "Run2015C", ## many fills with B=0
## HIRateRest 322729 (no collisions)
## RateTestHI 322763 and 322800 (no collisions)
]

def datasetNoSplitting(dataset_name):
    new = ""
    for letter in dataset_name:
        if not letter.isdigit():
            new += letter
    new = new.replace("ns","")
    new = new.replace("Single","")
    new = new.replace("Double","")
    new = new.replace("-Error","")
    return new

debug = ["ZeroBias", "AlCaLumiPixels", "EphemeralZeroBias", "SpecialHLTPhysics", "EphemeralHLTPhysics", "ParkingHT", "ParkingHTto", "HLTPhysics", "ParkingZeroBias", "RPCMonitor", "TestEnablesEcalHcal", "AlCaP","LAccept", "RateTestHI"]

sizes = {}
dataset_ = set()
eras_ = set()
for dataset in summaries:
    d = datasetNoSplitting(dataset.split("/")[1])
    era = dataset.split("/")[2].split("-")[0]
    if era in removeEras: 
#        print("Dropping %s"%dataset)
        continue
    size = summaries[dataset][0]['file_size']
#    if d in debug and size/1E12>1:
#        print(d, (size/1E12), dataset)
    era = era[3:7]
    for key in [d, d+"_"+era]:
        if key in sizes:
            sizes[key] += size
        else:
            sizes[key] = size
    dataset_.add(d)
    eras_.add(era)


sizesList = []
for s in sizes:
    if "_" in s: continue
    sizesList.append((sizes[s], s))

sizesList = sorted(sizesList, reverse=True)
eraSorted = sorted(list(eras_))

out = "\\begin{tabular}{%s}\n"%("c"*(len(eraSorted)+2))
out += "\hline \n"
out += "Dataset& Total"
for era in eraSorted:
    out += "& %s"%era 
out += "\\\\\n"
out += "\hline \n"

for s, d in sizesList:
    if sizes[d]/1E15<0.2: continue
    out += "%s& %.1f"%(d, sizes[d]/1E15)
    for era in eraSorted:
        key = "%s_%s"%(d, era)
        if key in sizes:
            size = "%.1f"%(sizes[key]/1E15) #TB
        else:
            size = "-"
        out += "& %s"%size 
    out += "\\\\\n"
out += "\hline \n"
out += "\end{tabular} \n"

#for s, d in sizesList:
#    print(d, s/1E15)

outF = open("sizeTable.txt", 'w')
outF.write(out)
outF.close()


