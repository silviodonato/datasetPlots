from datasetInfo_fromDAS import summaries
from recorded_lumi_fromOMS import recorded_lumi
from copy import copy
from mergeDataset import mergeDataset

directoryPlot = "plot"
vars =  ['rate', 'aveLumi', 'intLumi', 'duration', 'xsect', 'rate_2E34', 'data', 'events', 'dataPerLumi', 'dataPerTime']
groups = ["main","lumi"]+list(mergeDataset)

groupsToBeRemoved = []

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

#groups = ["main","lumi","Prompt"]

#groups = ["main","lumi","Prompt","Parking", "Scouting"]
#groups = ["Prompt","Scouting","Parking"]
groupsToBeRemoved = [
#    "ZeroBias",
#    "AlCa",
#    "Reserved",
#    "HIon",
#    "ToBeRemoved",
#    "SmallEventContent",
#    "TOTEM",
#    "NoCollisions",
#    "DAQTest",
#    "Errors",
#    "lumi",
#    "Fake",
#    "Others",
#    "Parking",
#    "Scouting",
#    "Prompt",
]
#groupsToBeRemoved = []


#vars =  ['aveLumi','rate']
#vars =  ['dataPerLumi','data']

groups = ["Parking"]
vars =  ['rate']


minimalSize = 0 #in GB
minEventSize = 0 # B
minEraLumi = 1 # pb-1
#useYearInsteadOfEra = True
#useYearInsteadOfEra = False
#ROOTbatch = False
ROOTbatch = True

def datasetNoSplitting(dataset_name):
    new = ""
    for letter in dataset_name:
        if not letter.isdigit():
            new += letter
    return new

def sortEras(eras):
    sorted_eras = list(eras)
    sorted_eras = sorted(sorted_eras)
    return sorted_eras

def sortDatasets(datasets, summaries):
    sorted_datasets = list(datasets)
    sorted_datasets = sorted(sorted_datasets)
#    sorted_datasets = sorted(sorted_datasets, key=lambda val: not "Others" in val)
#    sorted_datasets = sorted(sorted_datasets, key=lambda val: not "Commisioning" in val)
#    sorted_datasets = sorted(sorted_datasets, key=lambda val: not "ark" in val)
#    sorted_datasets = sorted(sorted_datasets, key=lambda val: not "Scouting" in val)
#    sorted_datasets = sorted(sorted_datasets, key=lambda val: not "Prompt" in val)
    return sorted_datasets

def savePy(stack, outName):
    out = open(outName, 'w')
    hist = stack.GetHists()
    ax = stack.GetXaxis()
    outText = "## %s %s %s %s\n"%(stack.GetName(),stack.GetTitle(),stack.GetXaxis().GetTitle(),stack.GetYaxis().GetTitle())
    outText += "plot = {\n"
    for b in range(1, ax.GetNbins()+1):
        outText += '    "%s" : {\n'%ax.GetBinLabel(b)
        bins = {}
        for hist in stack.GetHists():
            if hist.GetBinContent(b)>0:
                bins[hist.GetName()] = hist.GetBinContent(b)
        for (bin, value) in sorted(bins.items(), key=lambda x:x[1], reverse=True):
            outText += '        "%s" : %f,\n'%(bin, value)
        outText += '    },\n'
    outText += "}"
    out.write(outText)
    out.close()

## change format and drop small datasets
for dataset in list(summaries.keys()):
    if summaries[dataset][0]['file_size']/1E9> minimalSize:
        nn, dataset_name, era, format = dataset.split("/")
        summaries[dataset] = summaries[dataset][0]
        summaries[dataset]["full_dataset_name"] = dataset_name
        summaries[dataset]["dataset_name"] = datasetNoSplitting(dataset_name)
        era = era.split("-")
        version = era[-1]
        era = era[0]
        summaries[dataset]["era"] = era
        summaries[dataset]["year"] = era[3:-1]
        if era in recorded_lumi:
           eraLumi = era
        elif era[3:] in recorded_lumi:
           eraLumi = era[3:]
        else:
            print(era, " not found in recorded_lumi.")
            eraLumi = None
        if eraLumi and not (era in removeEras):
            summaries[dataset]["delivered_lumi"], summaries[dataset]["recorded_lumi"], summaries[dataset]["duration"] = recorded_lumi[eraLumi][0], recorded_lumi[eraLumi][1], recorded_lumi[eraLumi][2]
        else:
            summaries[dataset]["delivered_lumi"] = 0
            summaries[dataset]["recorded_lumi"] = 0
            summaries[dataset]["duration"] = 1E-9
            del summaries[dataset]
            continue
        summaries[dataset]["version"] = version
        summaries[dataset]["format"] = format
        summaries[dataset]["event_size"] = summaries[dataset]['file_size']/summaries[dataset]['nevents'] if summaries[dataset]['nevents']>0 else 0
    else:
        print("Removing %s"%dataset)
        del summaries[dataset]

import pprint
#pprint.pprint(summaries)

def getDatasetEras(summaries):
    datasets_ = set()
    eras_ = set()
    for dataset in list(summaries.keys()):
        if summaries[dataset]["event_size"]>minEventSize and int(summaries[dataset]["year"])>=2011 and summaries[dataset]["recorded_lumi"]>minEraLumi:
            datasets_.add(summaries[dataset]["dataset_name"])
            eras_.add(summaries[dataset]["era"])
    for removeEra in removeEras:
        if removeEra in eras_: 
            eras_.remove(removeEra) ## 261380 - 261553. No stable beams. Test 5 TeV
            print("Removing %s"%removeEra)

    return datasets_, eras_

def mergeSummariesInYears(summaries):
    mergedSummaries = {}
    for summary in summaries.values():
        key = (summary["dataset_name"], summary["year"], summary["format"])
        if not (key in mergedSummaries.keys()): mergedSummaries[key] = copy(summary)
        else:
            for el in ["file_size", "delivered_lumi", "recorded_lumi", "duration", "nevents", "nlumis", "nblocks", "nfiles", "num_block", "num_lumi"]:
                if el == "recorded_lumi" and "EmptyBX" in key[0] and "2023" in key[1]:
#                    print(key, mergedSummaries[key][el], summary[el])
                    pass
                mergedSummaries[key][el] += summary[el]
        mergedSummaries[key]["era"] = copy(summary["year"])
    return mergedSummaries

def getLargestDatasets(summaries):
    mergedSummaries = {}
    for summary in summaries.values():
        key = (summary["dataset_name"], summary["year"], summary["format"])
        if not (key in mergedSummaries.keys()): mergedSummaries[key] = copy(summary)
        else:
            for el in ["file_size", "delivered_lumi", "recorded_lumi", "duration", "nevents", "nlumis", "nblocks", "nfiles", "num_block", "num_lumi"]:
                if el == "recorded_lumi" and "EmptyBX" in key[0] and "2023" in key[1]:
#                    print(key, mergedSummaries[key][el], summary[el])
                    pass
                mergedSummaries[key][el] += summary[el]
        mergedSummaries[key]["era"] = copy(summary["year"])
    return mergedSummaries
##################################################
#Add fake dataset
datasets_, eras_ = getDatasetEras(summaries)

for era in eras_:
    dataset = "/Fake/%s/RAW"%era
    summaries[dataset] = {}
    summaries[dataset]["era"] = era
    summaries[dataset]["year"] = era[3:-1]
    summaries[dataset]["full_dataset_name"] = dataset
    summaries[dataset]["dataset_name"] = "Fake"
    summaries[dataset]["format"] = "RAW"
    summaries[dataset]["event_size"] = 1E6
    for el in ["file_size", "delivered_lumi", "recorded_lumi", "duration", "nevents", "nlumis", "nblocks", "nfiles", "num_block", "num_lumi"]:
        summaries[dataset][el] = 0
    
    summaries[dataset]["year"] = era[3:-1]
    if era in recorded_lumi:
        eraLumi = era
    elif era[3:] in recorded_lumi:
        eraLumi = era[3:]
    else:
        print(era, " not found in recorded_lumi.")
        eraLumi = None
    if eraLumi:
        summaries[dataset]["delivered_lumi"], summaries[dataset]["recorded_lumi"], summaries[dataset]["duration"] = recorded_lumi[eraLumi][0], recorded_lumi[eraLumi][1], recorded_lumi[eraLumi][2]
    else:
        summaries[dataset]["delivered_lumi"] = 1E9
        summaries[dataset]["recorded_lumi"] = 1E9
        summaries[dataset]["duration"] = 1E-9
        del summaries[dataset]
mergeDataset["lumi"] = ["Fake"]
#datasets_.add("Fake")
#datasets_, eras_ = getDatasetEras(summaries)

######################################################################


#tot = 0
#print("CHECK 1")
#for i in summaries.keys():
#    if "Tau" in i and "2022" in i: 
#        print(i, summaries[i]['duration'], summaries[i]['recorded_lumi'], summaries[i]['recorded_lumi']/summaries[i]['duration']*1000)
#        tot += summaries[i]['duration']
#print(tot)

summariesEra = summaries
summariesYear = mergeSummariesInYears(summaries)
del summaries

#tot = 0
#print("CHECK 1")
#for i in summariesBak.keys():
#    if "Tau" in i and "2022" in i: 
#        print(i, summariesBak[i]['duration'], summariesBak[i]['recorded_lumi'], summariesBak[i]['recorded_lumi']/summariesBak[i]['duration']*1000)
#        tot += summariesBak[i]['duration']
#print(tot)

#tot = 0
#print("CHECK 2")
#for i in summaries.keys():
#    if "Tau" in i[0] and "2022" in i[1]: 
#        print(i, summaries[i]['duration'], summaries[i]['recorded_lumi'], summaries[i]['recorded_lumi']/summaries[i]['duration']*1000)
#        tot += summaries[i]['duration']
#print(tot)

######################################################################



##################################################

## make Canvas using TDR style
import ROOT
import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()

ROOT.gROOT.SetBatch(ROOTbatch)

colorMap = {
    "Parking": ROOT.kRed,
    "Prompt": ROOT.kBlue,
    "Scouting": ROOT.kGray,
    "Commissioning": ROOT.kGreen,
    "Others": ROOT.kMagenta,
    "Fake": ROOT.kYellow,
}
if len(groupsToBeRemoved) ==0: colorMap = {}

colors = [
#ROOT.kBlack,

#ROOT.kGreen-10,
ROOT.kGreen-9,
ROOT.kGreen,
ROOT.kGreen+2,
#ROOT.kGreen+4,

#ROOT.kBlue-10,
ROOT.kBlue-9,
ROOT.kBlue,
ROOT.kBlue+2,
#ROOT.kBlue+4,

#ROOT.kYellow-10,
ROOT.kYellow-9,
ROOT.kYellow,
ROOT.kYellow+2,
#ROOT.kYellow+4,

#ROOT.kRed-10,
ROOT.kRed-9,
ROOT.kRed,
ROOT.kRed+2,
#ROOT.kRed+4,

#ROOT.kCyan-10,
ROOT.kCyan-9,
ROOT.kCyan,
ROOT.kCyan+2,
#ROOT.kCyan+4,

#ROOT.kMagenta-10,
ROOT.kMagenta-9,
ROOT.kMagenta,
ROOT.kMagenta+2,
#ROOT.kMagenta+4,


#ROOT.kYellow+1,
#ROOT.kRed,
#ROOT.kMagenta,
#ROOT.kBlue,
#ROOT.kCyan+1,
#ROOT.kGreen+1,

#ROOT.kOrange,
#ROOT.kPink,
#ROOT.kViolet,
#ROOT.kAzure,
#ROOT.kTeal,
#ROOT.kSpring,

#ROOT.kGray,
]


for dataset in datasets_:
    noGroup = True
    for group in mergeDataset:
        if dataset in mergeDataset[group] or dataset==group:
            noGroup = False
    if noGroup: # and not ("Fake" in dataset)
        mergeDataset["Others"].append(dataset)

for merge in list(mergeDataset):
    if len(mergeDataset[merge])==0:
        del mergeDataset[merge]
        if merge in groups: 
            groups.remove(merge)


### Sanity check in mergeDataset
check = set()
for d in mergeDataset.keys():
    if not d in check: check.add(d)
    else: raise Exception("Duplicated dataset %s"%d)

for dd in mergeDataset.values():
    for d in dd:
        if not d in check: check.add(d)
        else: raise Exception("Duplicated dataset %s"%d)

notMergeableVariables = ['aveLumi', 'intLumi', 'duration']

def getVariable(summary, var, denominator=False):
#    print(summary)
    if not denominator:
        if var=='rate_2E34': return summary['nevents']
        elif var=='xsect': return summary['nevents']
        elif var=='rate': return summary['nevents']
        elif var=='data': return summary['file_size']/1E15
        elif var=='dataPerLumi': return summary['file_size']/1E15
        elif var=='dataPerTime': return summary['file_size']/1E9
        elif var=='events': return summary['nevents']/1E9
        elif var=='aveLumi': return summary['recorded_lumi']
        elif var=='intLumi': return summary['recorded_lumi']/1E3
        elif var=='duration': return summary['duration']
        else: return -1
    else:
        if var=='rate_2E34': return (summary['recorded_lumi']*1E36/2E34) if summary['recorded_lumi'] else 0
        elif var=='xsect': return (summary['recorded_lumi']*1E-3) if summary['recorded_lumi'] else 0
        elif var=='rate': return (summary['duration']) if summary['duration'] else 0
        elif var=='data': return 1
        elif var=='dataPerLumi': return (summary['recorded_lumi']/1E3)
        elif var=='dataPerTime': return (summary['duration'])
        elif var=='events': return 1
        elif var=='aveLumi': return summary['duration']/1E36
        elif var=='intLumi': return 1
        elif var=='duration': return 1
        else: return -1


def getLabel(var):
    if var=='rate_2E34': return "Average trigger rate @2E34cm-1s-1 [Hz]"
    elif var=='xsect': return "Average trigger cross section [fb]"
    elif var=='rate': return "Average trigger rate [Hz]"
    elif var=='data': return "Total recorded data [PB]"
    elif var=='dataPerLumi': return "Recorded data per integ. lumi[PB/fb-1]"
    elif var=='dataPerTime': return "Average bandwidth during stable beams [GB/s]"
    elif var=='events': return "Total events [B]"
    elif var=='aveLumi': return "Average instantaneous lumi [cm-2s-1]"
    elif var=='intLumi': return "Total integrated lumi [fb-1]"
    elif var=='duration': return "Total duration [s]"
    else: return -1


#    return summary['nevents']/(summary['num_lumi']*23.31) if summary['num_lumi']>0 else 0
#    return summary['file_size']/summary['num_lumi'] if summary['num_lumi']>0 else 0
#    return summary['file_size']/summary['nevents'] if summary['nevents']>0 else 0
#    return summary['file_size']

#var = 'rate_2E34'
#var = 'xsect'
#var = 'rate'
#var = 'data'
var = 'events'
#for var in ['xsect', 'rate_2E34', 'rate', 'data', 'events']:
for useYearInsteadOfEra in [True, False]:
    if useYearInsteadOfEra:
        summaries = summariesYear
    else:
        summaries = summariesEra
    datasets_, eras_ = getDatasetEras(summaries)
    eras = sortEras(eras_)
    ## template histogram, with era as x label
    dataset_size = ROOT.TH1F("dataset_size","",len(eras),0,len(eras))
    for i in range(len(eras)):
        dataset_size.GetXaxis().SetBinLabel(i+1, eras[i])
    
    for group in groups:
    #for group in ["main"]+list(mergeDataset):
    #for group in ["ToBeRemoved"]:
        for var in vars:
            print("DOING %s %s"%(var, group))
    #    for var in ['rate']:
    #    for var in ['data', 'intLumi', 'dataPerLumi']:
    #    for var in ['rate']:
        #for var in ['rate']:
        #for var in ['aveLumi']:
            if var in notMergeableVariables and group!="lumi": continue
            if not (var in notMergeableVariables) and group=="lumi": continue
            eras = sortEras(eras_)
            datasets = sortDatasets(datasets_, summaries)
    #        datasets.append("Fake")
    #        mergeDataset["Fake"]=["Fake"]
            
    #        canvas = ROOT.TCanvas("canvas", "", 1920, 1200)
            canvas = ROOT.TCanvas("canvas", "", 1920, 1600)
            canvas.SetGridx()
            canvas.SetGridy()
            ## initialize histograms
            dataset_sizes = {}
            dataset_sizes_num = {}
            dataset_sizes_den = {}
            for dataset in datasets:
                dataset_sizes[dataset] = dataset_size.Clone(dataset)
                dataset_sizes_num[dataset] = dataset_size.Clone(dataset)
            dataset_sizes_den["Fake"] = dataset_size.Clone("Fake")
    #            color = colors[datasets.index(dataset)%len(colors)]

            ## fill histograms
            for summary in summaries.values():
                datName = summary['dataset_name']
    #            print(datName, summary['era'], summary['era'] in eras, datName in datasets)
                if datName in datasets and summary['era'] in eras:
                    dataset_sizes_num[datName].Fill( eras.index(summary['era']), getVariable(summary, var)  ) #/ summary['num_lumi']
                    dataset_sizes_num[datName].SetBinError( eras.index(summary['era'])+1, 0.0001 )
    #                print(datName)
                    if datName == "Fake": 
                        dataset_sizes_den[datName].Fill( eras.index(summary['era']), getVariable(summary, var, denominator=True)  ) #/ summary['num_lumi']
                        dataset_sizes_den[datName].SetBinError( eras.index(summary['era'])+1, 0.0001 )
    #                    print("AAAA", datName, summary['era'], summary['file_size'])
            for d in dataset_sizes:
                if (var in notMergeableVariables) and (d != "Fake"): continue
                if dataset_sizes_den["Fake"].Integral()<=0:
                    for d in summaries:
                        print(d, summaries[d]['dataset_name'], summaries[d]['era'])
                    print(d)
                    print(dataset_sizes)
                    print(datasets)
                    print(eras)
                    raise Exception("dataset_sizes_den['Fake'].Integral()<=0")
                dataset_sizes[d].Divide(dataset_sizes_num[d], dataset_sizes_den["Fake"])
                print("Computing",d,var,dataset_sizes[d].Integral())
    #            print(d, dataset_sizes_num[d].Integral(), dataset_sizes_den["Fake"].Integral(), dataset_sizes[d].Integral())

            if group=="main":
                for merge in mergeDataset:
                    if not merge in dataset_sizes:
                        dataset_sizes[merge] = dataset_size.Clone(merge)
                    if not merge in datasets:
                        datasets.append(merge)
                    for tobemerged in mergeDataset[merge]:
                        if tobemerged in dataset_sizes:
                            dataset_sizes[merge].Add(dataset_sizes[tobemerged])
                            print("Merging %s in %s"%(tobemerged, merge))
                            if tobemerged in datasets: datasets.remove(tobemerged)
                if len(groupsToBeRemoved)>0:
                    for groupToBeRemoved in groupsToBeRemoved:
                        if groupToBeRemoved in datasets: datasets.remove(groupToBeRemoved)
    #                if "ToBeRemoved" in datasets: datasets.remove("ToBeRemoved")
    #                if "Commissioning" in datasets: datasets.remove("Commissioning")
    #                if "Others" in datasets: datasets.remove("Others")
            else:
                for g in mergeDataset:
                    if not g == group: ## remove all dataset which are not in the selected group
                        for d in mergeDataset[g]+[g]:
                            if d in datasets: 
                                datasets.remove(d)
            ##sort by size
    #        print("________________________________")
            sizes = []
            for dataset in datasets:
               sizes.append((dataset_sizes[dataset].Integral()/1E12, dataset))

            if len(sizes)==0: continue
            sizes = sorted(sizes)
            a,b = zip(*sizes)
            datasets = list(b)
    #        datasets = sorted(datasets, key=lambda val: "ReservedDouble" in val)
    #        datasets = sorted(datasets, key=lambda val: "Other Par" in val)
    #        datasets = sorted(datasets, key=lambda val: "Park" == val[0:4])
    #        datasets = sorted(datasets, key=lambda val: not "ALCA" in val)
    #        datasets = sorted(datasets, key=lambda val: not "ScoutingPFMonitor" in val)
    #        datasets = sorted(datasets, key=lambda val: not "HighMultiplicityEOF" in val)
            datasets = sorted(datasets, key=lambda val: not "Others" in val)
            datasets = sorted(datasets, key=lambda val: not "Commisioning" in val)
            datasets = sorted(datasets, key=lambda val: not "Park" in val)
            datasets = sorted(datasets, key=lambda val: not "Scouting" in val)
            datasets = sorted(datasets, key=lambda val: not "Prompt" in val)

            pprint.pprint(sizes)

            #dataset_sizes[datasets[0]].Draw()

            ## build stack
            if group == "main" or group == 'lumi':
                leg = ROOT.TLegend(0.12,0.65,0.30,0.88)
            else:
                leg = ROOT.TLegend(0.12,0.45,0.35,0.98)
            #leg.SetHeader("")
            stack = ROOT.THStack("stack", "")
            for i in range(len(datasets)):
                d = datasets[i]
                if dataset_sizes[d].Integral()>0: 
                    dataset_sizes[d].SetLineColor(ROOT.kBlack)
                    if d in colorMap:
                        color = colorMap[d]
                    else:
                        color = colors[i%len(colors)]
                    dataset_sizes[d].SetFillColor(color)
                    stack.Add(dataset_sizes[d])

            for i in range(len(datasets)):
                d = datasets[len(datasets)-1-i]
                print(d)
                if dataset_sizes[d].Integral()>0:
                    if leg.GetNRows()>30: leg.SetNColumns(2)
                    leg.AddEntry(dataset_sizes[d],d) # or lep or f

            #stack.Add("Others")

            #    print(dataset_sizes[datasets[i]].Integral())
            #    dataset_sizes[datasets[i]].Clone().Draw("same")
            #    canvas.Update()

    #        if stack.GetMaximum()<=0: continue
            stack.Draw("HIST")
        #    if var!='aveLumi': stack.Draw("HIST")
        #    else:  stack.Draw("E0")
            stack.SetMaximum(stack.GetMaximum()*1.6)
            if useYearInsteadOfEra:
                stack.GetXaxis().SetTitle("Year")
            else:
    #            stack.GetXaxis().SetTitle("Era")
                stack.GetXaxis().LabelsOption("v")
            stack.GetYaxis().SetTitle(getLabel(var))
            if not (var in notMergeableVariables): leg.Draw() 
            
            if useYearInsteadOfEra:
                period = "year"
            else:
                period = "era"
            import os
            
            if not os.path.exists(directoryPlot):
                os.mkdir(directoryPlot)
            canvas.SaveAs("%s/plot_"%directoryPlot+group+"_"+period+"_"+var+".png")
            canvas.SaveAs("%s/plot_"%directoryPlot+group+"_"+period+"_"+var+".root")
            savePy(stack, "%s/plot_"%directoryPlot+group+"_"+period+"_"+var+".py")
            del stack
            del canvas
            del dataset_sizes, dataset_sizes_num, dataset_sizes_den
    del dataset_size


