from datasetInfo_fromDAS import summaries
from recorded_lumi_fromOMS import recorded_lumi

minimalSize = 10000 #in GB
minEventSize = 0.2E6 # B
minEraLumi = 1000.0 # pb-1
useYearInsteadOfEra = True

def datasetNoSplitting(dataset_name):
    if dataset_name[-1].isdigit(): dataset_name = dataset_name[:-1]
    if dataset_name[-1].isdigit(): dataset_name = dataset_name[:-1]
    if dataset_name[-1].isdigit(): dataset_name = dataset_name[:-1]
    return dataset_name

def sortEras(eras):
    sorted_eras = list(eras)
    sorted_eras = sorted(sorted_eras)
    return sorted_eras

def sortDatasets(datasets, summaries):
    sorted_datasets = list(datasets)
    sorted_datasets = sorted(sorted_datasets)
    return sorted_datasets

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
        if eraLumi:
            summaries[dataset]["delivered_lumi"], summaries[dataset]["recorded_lumi"], summaries[dataset]["duration"] = recorded_lumi[eraLumi][0], recorded_lumi[eraLumi][1], recorded_lumi[eraLumi][2]
        else:
            summaries[dataset]["delivered_lumi"] = -1
            summaries[dataset]["recorded_lumi"] = -1
            summaries[dataset]["duration"] = -1
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
    return datasets_, eras_

##################################################
#Add fake dataset
datasets_, eras_ = getDatasetEras(summaries)

for era in eras_:
    dataset = "Fake"+era
    summaries[dataset] = {}
    summaries[dataset]["eras"] = era
    summaries[dataset]["year"] = era[3:-1]
    summaries[dataset]["full_dataset_name"] = "Fake"
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
        summaries[dataset]["delivered_lumi"] = -1
        summaries[dataset]["recorded_lumi"] = -1
        summaries[dataset]["duration"] = -1

######################################################################

def mergeSummariesInYears(summaries):
    mergedSummaries = {}
    for name in summaries:
        summary = summaries[name]
        key = (summary["full_dataset_name"], summary["year"], summary["format"])
        if not key in mergedSummaries.keys(): mergedSummaries[key] = summary.copy()
        else:
            for el in ["file_size", "delivered_lumi", "recorded_lumi", "duration", "nevents", "nlumis", "nblocks", "nfiles", "num_block", "num_lumi"]:
                mergedSummaries[key][el] += summary[el]
        mergedSummaries[key]["era"] = summary["year"]
    return mergedSummaries


#tot = 0
#print("CHECK 1")
#for i in summaries.keys():
#    if "Tau" in i and "2022" in i: 
#        print(i, summaries[i]['duration'], summaries[i]['recorded_lumi'], summaries[i]['recorded_lumi']/summaries[i]['duration']*1000)
#        tot += summaries[i]['duration']
#print(tot)

if useYearInsteadOfEra:
    summariesBak = summaries
    summaries = mergeSummariesInYears(summaries)
    datasets_, eras_ = getDatasetEras(summaries)

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

eras = sortEras(eras_)
## template histogram, with era as x label
dataset_size = ROOT.TH1F("dataset_size","",len(eras),0,len(eras))
for i in range(len(eras)):
    dataset_size.GetXaxis().SetBinLabel(i+1, eras[i])


colors = [
#ROOT.kBlack,

ROOT.kYellow+1,
ROOT.kRed,
ROOT.kMagenta,
ROOT.kBlue,
ROOT.kCyan+1,
ROOT.kGreen+1,

ROOT.kOrange,
ROOT.kPink,
ROOT.kViolet,
ROOT.kAzure,
ROOT.kTeal,
ROOT.kSpring,

ROOT.kGray,
]

## merge "other" histograms
mergeDataset = {
    "Others" : [
#        "BTagMu",
#        "Commissioning",
        "CommissioningRawPrime",
        "CommissioningZDC",
#        "Cosmics",
#        "DisplacedJet",
        "EmptyBX",
        "MinimumBias",
#        "NoBPTX",
#        "MuonEG",
#        "ReservedDoubleMuonLowMass",
#        "ScoutingPFMonitor",
#        "Tau",
        "HLTPhysics",
        "MuonShower",
#        "ZeroBias",
        "ZeroBiasNonColliding",
        "IsolatedBunch",
        "PPRefZeroBias",
        "PPRefDoubleMuon",
        "PPRefExotica",
        "PPRefHardProbes",
        "PPRefSingleMuon",
        "HLTRAWTest",
        "RandomTOTEM",
        "L1MinimumBias",
        "DoubleMuonLowPU",
        "JetsTOTEM",
        "SingleTrack",
        "MuonEGammaTOTEM",
        "CommissioningEGamma",
        "CommissioningMuons",
        "ScoutingPFCommissioning",
        "CommissioningSingleJet",
        "CommissioningTaus",
        "HFvetoTOTEM",
        "Totem",
        "CommissioningHTT",
        "ScoutingCaloCommissioning",
        "CommissioningETM",
        "CommissioningDoubleJet",
        "TestEnablesEcalHcalDT",
        "EcalLaser",
        "TestEnablesEcalHcalXeXeTest",
        "HighPtLowerPhotons",
        "L1AcceptXeXeTest",

        "ZeroBiasPD",
        "ZeroBias8b4e",
        "ZeroBiasNominalTrains",
        "ZeroBiasIsolatedBunches",
        "VRZeroBias",

    ],
    "HIon" : [
        "HIDoubleMuon",
        "HIMinimumBias",
        "HIHardProbes",
        "HIOniaTnP",
        "HIOnia",
        "HIHardProbesPrescaleJets",
        "HIHardProbesPrescaleEGs",
        "HIHardProbesPrescaled",
        "HIHardProbesPeripheral",
        "HITrackerVriginRaw",
        "HIForward",
        "HIExpressPhysics",
        "HIHLTMonitor",
        "HITrackerNZS",
        "HITestRawPrime",
        "HITestRaw",
        "HIRateTest",
        "HITestFull",
        "HighPtPhoton30AndZ",
        "HITestReduced",
        "HIMinimumBiasReducedFormat",
        "HICosmicsTestXeXeTest",
        "HISingleMuon",
        "HICosmicsTestXeXeTest-Error",
        "HIEmptyBX",
        "HIExpressPhysicsRawPrime",
        "HIHLTPhysics",
        "HIHcalNZS",
        "HIPhysicsRawPrime",
        "HIRateRest",
        "HINCaloJets",
        "HINPFJets",
        "HITestVR",
        "HIZeroBias",
        "RateTestHI",
        "HeavyFlavor",
        "ScoutingMonitor",
        "ParkingMonitor"
        
    ],
    "Scouting" : [
        "ScoutingPFRun",
        "ScoutingCaloMuon",
        "ScoutingPFMuon",
        "ScoutingCaloHT",
        "ScoutingPFHT",
    ],
    "Other Parking" : [
        "ParkingHLTPhysicsTrains",
        "ParkingZeroBiasTrains",
        "ParkingZeroBias",
        "ParkingL1SingleEGer",
        "ParkingL1SingleJet",
        "ParkingL1DoubleEG",
        "ParkingL1SingleMu",
        "ParkingZeroBiasIndiv",
        "ParkingL1SingleTau",
        "ParkingL1HTTer",
        "ParkingL1DoubleIsoTau",
        "ParkingL1SingleEG",
        "ParkingL1TripleMu",
        "ParkingL1DoubleJet",
        "ParkingL1DoubleMu",
        "ParkingCosmicsVirginRaw",
        "ParkingHLTPhysicsIndiv",
        "ParkingL1ETMHF",
        "ParkingBPHPromptCSCS",
        "ParkingHIZeroBias",
        "ParkingHT",
        "ParkingHLTPhysics",
        "ParkingScoutingMonitor",
        "ParkingL1MinimumBias",
        "DoubleMuParked",
        "TauParked",
        "HTMHTParked",
        "ParkingMuons",
        "METParked",
        "ZeroBiasParked",
        "HLTPhysicsParked",
        "SinglePhotonParked",
        "MuOniaParked",
        "MultiJet1Parked",
        "ParkingHT450to",
        "ParkingHT470to",
        "ParkingHT410to",
        "ParkingHT430to",
        "ParkingHT500to",
        "ParkingHT550to",
        "VBF1Parked",
    ],
#    "Parking" : [
#        "ParkingHLTPhysicsTrains",
#        "ParkingZeroBiasTrains",
#        "ParkingZeroBias",
#        "ParkingL1SingleEGer",
#        "ParkingL1SingleJet",
#        "ParkingL1DoubleEG",
#        "ParkingL1SingleMu",
#        "ParkingZeroBiasIndiv",
#        "ParkingL1SingleTau",
#        "ParkingL1HTTer",
#        "ParkingL1DoubleIsoTau",
#        "ParkingL1SingleEG",
#        "ParkingL1TripleMu",
#        "ParkingL1DoubleJet",
#        "ParkingL1DoubleMu",
#        "ParkingCosmicsVirginRaw",
#        "ParkingHLTPhysicsIndiv",
#        "ParkingL1ETMHF",
#        "ParkingBPHPromptCSCS",
#        "ParkingHIZeroBias",
#        "ParkingDoubleElectronLowMass",
#        "ParkingSingleMuon",
#        "ParkingDoubleMuonLowMass",
#        "ParkingHH",
#        "ParkingLLP",
#        "ParkingVBF",
#        "ParkingHT",
#        "ParkingBPH", ##2018
#        "ParkingHLTPhysics",
#        "ParkingMuon",
#        "ParkingScoutingMonitor",
#        "ParkingL1MinimumBias",
#    ],
    "DoubleMuonLowMass" : [
        "MuOnia",
        "Charmonium",
    ],
    "JetMET" : [
        "JetHT",
        "HTMHT",
        "MET",
        "BTagCSV",
        "HT",
        "BJetPlusX",
        "MultiJet"
    ],
    "Tau" : [
        "TauPlusX",
    ],
    
    "Muon" : [
        "SingleMuon",
        "DoubleMuon",
        "MuonEG",
        "DoubleMu",
        "MuHad",
        "SingleMu"
    ],
    "EGamma" : [
        "SingleElectron",
        "SinglePhoton",
        "DoubleEG",
        "ElectronHad",
        "DoublePhoton",
        "DoubleElectron"
    ],
    "ALCA" : [
        "AlCaLowPtJet",
        "AlCaLumiPixelsCountsGated",
        "AlCaLumiPixelsCountsPrompt",
        "AlCaP",
        "AlCaPPSPrompt",
        "AlCaPhiSym",
        "HcalNZS",
        "RPCMonitor",
        "TestEnablesEcalHcal",
        "AlcaLumiPixelsExpress",
        "AlCaLumiPixelsCountsUngated",
        "AlCaPPS",
        "AlCaLumiPixelsXeXeTest",
        "ALCAP",
        "AlCaLumiPixels",
        "ExpressAlignment",
    ],
#    "ZeroBias" : [
#        "ZeroBiasPD",
#        "ZeroBias8b4e",
#        "ZeroBiasNominalTrains",
#        "ZeroBiasIsolatedBunches",
#        "VRZeroBias",
#    ],
#    "Ephemeral" : [
#        "EphemeralHLTPhysics",
#        "EphemeralZeroBias",
#    ],
#    "Special" : [
#        "SpecialHLTPhysics",
#        "SpecialZeroBias",
#        "SpecialRandom",
#    ],
    "ToBeRemoved" : [
        
        ## ZeroBias
        "ZeroBias",
        
        ## Ephemeral
        "EphemeralHLTPhysics",
        "EphemeralZeroBias",
        
        ## Special
        "SpecialHLTPhysics",
        "SpecialZeroBias",
        "SpecialRandom",
        
        "D",
        "ParkingDoubleElectronLowMass-Error",
        "EGamma-Error",
        "CommissioningEGamma-Error",
        "MET-Error",
        "ZeroBias2-Error",
        "ZeroBias4-Error",
        "ZeroBias1-Error",
        "ZeroBias3-Error",
        "ZeroBias9-Error",
        "ZeroBias6-Error",
        "ZeroBias5-Error",
        "ZeroBias8-Error",
        "ZeroBias7-Error",
        "ZeroBias0-Error",
        "LowEGJet-Error",
        "FSQJet2-Error",
        "HFvetoTOTEM-Error",
        "SingleMuon-Error",
        "IsolatedBunch-Error",
        "Cosmics-Error",
        "MinimumBias-Error",
        "Commissioning3-Error",
        "ZeroBias-Error",
        "CommissioningSingleJet-Error",
        "ZeroBias10-Error",
        "Totem12-Error",
        "Commissioning2-Error",
        "DoubleEG-Error",
        "VRRandom2-Error",
        "VRRandom1-Error",
        "VRRandom3-Error",
        "VRRandom0-Error",
        "VRRandom4-Error",
        "ParkingHT-Error",
        "CommissioningETM-Error",
        "JetHT-Error",
        "Fake",
    ],
}

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

def getVariable(summary, var):
    print(summary)
    if var=='rate_2E34': return summary['nevents']/(summary['recorded_lumi']*1E36/2E34) if summary['recorded_lumi'] else 0
    elif var=='xsect': return summary['nevents']/(summary['recorded_lumi']*1E-3) if summary['recorded_lumi'] else 0
    elif var=='rate': return summary['nevents']/(summary['duration']) if summary['duration'] else 0
    elif var=='data': return summary['file_size']/1E15
    elif var=='dataPerLumi': return summary['file_size']/1E15/(summary['recorded_lumi']/1E3)
    elif var=='dataPerTime': return summary['file_size']/1E9/(summary['duration'])
    elif var=='events': return summary['nevents']/1E9
    elif var=='aveLumi': 
        if summary["dataset_name"]=="Fake": return summary['recorded_lumi']*1E36/summary['duration']
        else: return 0
    elif var=='intLumi': 
        if summary["dataset_name"]=="Fake": return summary['recorded_lumi']/1E3
        else: return 0
    elif var=='duration': 
        if summary["dataset_name"]=="Fake": return summary['duration']
        else: return 0
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
for var in ['rate', 'aveLumi', 'intLumi', 'duration', 'xsect', 'rate_2E34', 'rate', 'data', 'events', 'dataPerLumi', 'dataPerTime']:
#for var in ['aveLumi']:
    eras = sortEras(eras_)
    datasets = sortDatasets(datasets_, summaries)
    if var in notMergeableVariables: datasets.append("Fake")

    canvas = ROOT.TCanvas("canvas", "", 1280, 1024)
    canvas.SetGridx()
    canvas.SetGridy()
    ## initialize histograms
    dataset_sizes = {}
    for dataset in datasets:
        dataset_sizes[dataset] = dataset_size.Clone(dataset)
        color = colors[datasets.index(dataset)%len(colors)]

    ## fill histograms
    for summary in summaries.values():
        datName = summary['dataset_name']
        if datName in datasets and summary['era'] in eras:
            dataset_sizes[datName].Fill( eras.index(summary['era']), getVariable(summary, var)  ) #/ summary['num_lumi']
            dataset_sizes[datName].SetBinError( eras.index(summary['era'])+1, 0.0001 )
            print(datName, summary['era'], summary['file_size'])

    for merge in mergeDataset:
        if not merge in dataset_sizes:
            dataset_sizes[merge] = dataset_size.Clone(merge)
            datasets.append(merge)
        for tobemerged in mergeDataset[merge]:
            if tobemerged in dataset_sizes:
                dataset_sizes[merge].Add(dataset_sizes[tobemerged])
                if tobemerged in datasets: datasets.remove(tobemerged)
    
        if "ToBeRemoved" in datasets: datasets.remove("ToBeRemoved")

    ##sort by size
    print("________________________________")
    sizes = []
    for dataset in datasets:
       sizes.append((dataset_sizes[dataset].Integral()/1E12, dataset))
       sizes = sorted(sizes)

    sorted(sizes)
    a,b = zip(*sizes)
    datasets = list(b)

    pprint.pprint(sizes)

    #dataset_sizes[datasets[0]].Draw()

    ## build stack
    leg = ROOT.TLegend(0.12,0.55,0.35,0.88)
    #leg.SetHeader("")
    stack = ROOT.THStack("stack", "")
    for i in range(len(datasets)):
        d = datasets[i]
        dataset_sizes[d].SetLineColor(ROOT.kBlack)
        dataset_sizes[d].SetFillColor(colors[i%len(colors)])
        if dataset_sizes[d].Integral()>0: stack.Add(dataset_sizes[d])

    for i in range(len(datasets)):
        d = datasets[len(datasets)-1-i]
        print(d)
        if dataset_sizes[d].Integral()>0: leg.AddEntry(dataset_sizes[d],d) # or lep or f

    #stack.Add("Others")

    #    print(dataset_sizes[datasets[i]].Integral())
    #    dataset_sizes[datasets[i]].Clone().Draw("same")
    #    canvas.Update()

    stack.Draw("HIST")
#    if var!='aveLumi': stack.Draw("HIST")
#    else:  stack.Draw("E0")
    stack.SetMaximum(stack.GetMaximum()*1.6)
    stack.GetXaxis().SetTitle("Eras")
    stack.GetYaxis().SetTitle(getLabel(var))
    if not (var in notMergeableVariables): leg.Draw() 
    
    canvas.SaveAs("plot_"+var+".png")


