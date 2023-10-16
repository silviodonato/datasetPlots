from datasetInfo_fromDAS import summaries
from recorded_lumi_fromOMS import recorded_lumi
from copy import copy

minimalSize = 0 #in GB
minEventSize = 1000 # B
minEraLumi = 1000 # pb-1
useYearInsteadOfEra = True
#useYearInsteadOfEra = False
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
    if "Run2015E" in eras_: 
        eras_.remove("Run2015E")
        print("Removing Run2015E")
    return datasets_, eras_

##################################################
#Add fake dataset
datasets_, eras_ = getDatasetEras(summaries)

for era in eras_:
    dataset = "Fake"+era
    summaries[dataset] = {}
    summaries[dataset]["era"] = era
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
        summaries[dataset]["delivered_lumi"] = 1E9
        summaries[dataset]["recorded_lumi"] = 1E9
        summaries[dataset]["duration"] = 1E-9
        del summaries[dataset]

######################################################################

def mergeSummariesInYears(summaries):
    mergedSummaries = {}
    for summary in summaries.values():
        key = (summary["dataset_name"], summary["year"], summary["format"])
        if not (key in mergedSummaries.keys()): mergedSummaries[key] = copy(summary)
        else:
            for el in ["file_size", "delivered_lumi", "recorded_lumi", "duration", "nevents", "nlumis", "nblocks", "nfiles", "num_block", "num_lumi"]:
                if el == "recorded_lumi" and "EmptyBX" in key[0] and "2023" in key[1]:
                    print(key, mergedSummaries[key][el], summary[el])
                mergedSummaries[key][el] += summary[el]
        mergedSummaries[key]["era"] = copy(summary["year"])
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

ROOT.gROOT.SetBatch(ROOTbatch)

eras = sortEras(eras_)
## template histogram, with era as x label
dataset_size = ROOT.TH1F("dataset_size","",len(eras),0,len(eras))
for i in range(len(eras)):
    dataset_size.GetXaxis().SetBinLabel(i+1, eras[i])


colorMap = {
    "Parking": ROOT.kRed,
    "Prompt": ROOT.kBlue,
    "Scouting": ROOT.kGray,
    "Commissioning": ROOT.kGreen,
    "Others": ROOT.kMagenta,
    "Fake": ROOT.kYellow,
}

colors = [
#ROOT.kBlack,

#ROOT.kGreen-10,
ROOT.kGreen-7,
ROOT.kGreen,
ROOT.kGreen+2,
#ROOT.kGreen+4,

ROOT.kYellow-10,
ROOT.kYellow-7,
ROOT.kYellow,
ROOT.kYellow+2,
#ROOT.kYellow+4,

#ROOT.kRed-10,
ROOT.kRed-7,
ROOT.kRed,
ROOT.kRed+2,
#ROOT.kRed+4,

#ROOT.kMagenta-10,
ROOT.kMagenta-7,
ROOT.kMagenta,
ROOT.kMagenta+2,
#ROOT.kMagenta+4,

#ROOT.kBlue-10,
ROOT.kBlue-7,
ROOT.kBlue,
ROOT.kBlue+2,
#ROOT.kBlue+4,

#ROOT.kCyan-10,
ROOT.kCyan-7,
ROOT.kCyan,
ROOT.kCyan+2,
#ROOT.kCyan+4,

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

## merge "other" histograms
mergeDataset = {
    "Others" : [
        "ReservedDoubleMuonLowMass",
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

#    ],
#    "HIon" : [
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
        "ScoutingPFMuons",
        "ScoutingPFRun",
        "ScoutingCaloMuon",
        "ScoutingPFMuon",
        "ScoutingCaloHT",
        "ScoutingPFHT",
        "DataScouting",
    ],
    "Parking" : [
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
        
        ## large rate parking
        "ParkingDoubleMuonLowMass",
        "ParkingBPH",
        "ParkingDoubleElectronLowMass",
        "ParkingVBF",
        "ParkingSingleMuon",
        "ParkingMuon",
        "ParkingHH",
        "ParkingLLP",
    
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
    "Prompt" : [
        "HighMultiplicityEOF", ##large rate, small event size
        "NoBPTX", ##large rate, small event size
        "SingleMuLowPt",
        "SingleMuHighPt",
        "BTagMu",
        "EGamma",
        "DoubleMuonLowMass",
        "JetMET",
        "Tau",
        "Muon",
        "DisplacedJet",
#    "DoubleMuonLowMass" : [
        "MuOnia",
        "Charmonium",
#    ],
#    "JetMET" : [
        "JetHT",
        "HTMHT",
        "MET",
        "BTagCSV",
        "HT",
        "BJetPlusX",
        "MultiJet",
#    ],
#    "Tau" : [
        "TauPlusX",
#    ],
#    "Muon" : [
        "SingleMuon",
        "DoubleMuon",
        "MuonEG",
        "DoubleMu",
        "MuHad",
        "SingleMu",
#    ],
#    "EGamma" : [
        "SingleElectron",
        "SinglePhoton",
        "Photon",
        "DoubleEG",
        "ElectronHad",
        "DoublePhoton",
        "DoubleElectron"
    ],
    "Commissioning" : [
        "L1Accept", ##small event size
        "TestEnables", ##small event size
        "TOTEM", ##small event size
        "TOTEM_zeroBias", ##small event size

        "TOTEM_romanPotsTTBB_", 
        "ZeroBiasTOTEM", 
        "TOTEM_romanPots2_", 
        "TOTEM_minBias", 
        "ToTOTEM", 

        "HcalHPDNoise", 
        "MiniDaq", 


        "ZeroBiasIsolatedBunch", 
        "ZeroBiasPixelHVScan", 
        "ZeroBias25ns", 
        "ZeroBiasHPF", 
        "ZeroBiasBunchTrains", 
        "HINMuon_HFveto", 
        "HighMultiplicity", 
        "HLTPhysics25ns", 
        "ZeroBiasVdM", 
        "ZeroBiasFirstBunchInTrain", 
        "LogMonitor", 
        "ZeroBiasFirstBunchAfterTrain", 
        "VRRandom", 
        "JetMon", 
        "L1JetHPF", 
        "L1EGHPF", 
        "HighPileUp", 
        "HLTPhysicsIsolatedBunch", 
        "HighPileUpHPF", 

        "ScoutingPFMonitor",
#        "HIon",
#    ],
#    "ALCA" : [
        "AlCaElectron", ##small event size
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

        "AllPhysics2",
        "FSQJet",
        "Jet",
        "MuEG",
        "ForwardTriggers",
        "PhotonHad",
        "FSQJets",
        "DoublePhotonHighPt",
        "BTag",
        "METBTag",

        "SingleElectron_0T",
        "JetHT_0T",
        "SinglePhoton_0T",
        "Commissioning_0T",
        "HTMHT_0T",
        "MET_0T",
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
        ## Cosmics
        "Cosmics",  ##small event size
        "Interfill",  ##small event size
        
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

        "ParkingZeroBiasPONIES2-Error",
        "ParkingZeroBiasPONIES3-Error",
        "AlCaLumiPixels-Error",
        "AlCaPhiSym-Error",
        "Interfill-Error",
        "Commissioning-Error",
        "NoBPTX-Error",
        "HLTPhysicsIsolatedBunch-Error",
        "VirginRawZeroBias-Error",

        "PPRefZeroBias",
        "PPRefDoubleMuon",
        "PPRefExotica",
        "PPRefHardProbes",
        "PPRefSingleMuon",

        "Fake",
    ],
}

for dataset in datasets_:
    noGroup = True
    for group in mergeDataset:
        if dataset in mergeDataset[group] or dataset==group:
            noGroup = False
    if noGroup:
        mergeDataset["Others"].append(dataset)

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
#for group in ["main","Prompt"]:
for group in ["main"]+list(mergeDataset):
    for var in ['rate', 'aveLumi', 'intLumi', 'duration', 'xsect', 'rate_2E34', 'data', 'events', 'dataPerLumi', 'dataPerTime']:
#    for var in ['data', 'intLumi', 'dataPerLumi']:
#    for var in ['rate']:
    #for var in ['rate']:
    #for var in ['aveLumi']:
        eras = sortEras(eras_)
        datasets = sortDatasets(datasets_, summaries)
        if var in notMergeableVariables: 
            datasets.append("Fake")
            if group!="main": continue

        canvas = ROOT.TCanvas("canvas", "", 1280, 1024)
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
#            print(summary)
            if datName in datasets and summary['era'] in eras:
                dataset_sizes_num[datName].Fill( eras.index(summary['era']), getVariable(summary, var)  ) #/ summary['num_lumi']
                dataset_sizes_num[datName].SetBinError( eras.index(summary['era'])+1, 0.0001 )
                if datName == "Fake": 
                    dataset_sizes_den[datName].Fill( eras.index(summary['era']), getVariable(summary, var, denominator=True)  ) #/ summary['num_lumi']
                    dataset_sizes_den[datName].SetBinError( eras.index(summary['era'])+1, 0.0001 )
#                print(datName, summary['era'], summary['file_size'])
        for d in dataset_sizes:
            if var in notMergeableVariables and d != "Fake": continue
            dataset_sizes[d].Divide(dataset_sizes_num[d], dataset_sizes_den["Fake"])

        if group=="main":
            for merge in mergeDataset:
                if not merge in dataset_sizes:
                    dataset_sizes[merge] = dataset_size.Clone(merge)
                    datasets.append(merge)
                for tobemerged in mergeDataset[merge]:
                    if tobemerged in dataset_sizes:
                        dataset_sizes[merge].Add(dataset_sizes[tobemerged])
                        if tobemerged in datasets: datasets.remove(tobemerged)
            
                if "ToBeRemoved" in datasets: datasets.remove("ToBeRemoved")
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
        sorted(sizes)
        a,b = zip(*sizes)
        datasets = list(b)
        datasets = sorted(datasets, key=lambda val: "ReservedDouble" in val)
        datasets = sorted(datasets, key=lambda val: "Other Par" in val)
        datasets = sorted(datasets, key=lambda val: "Park" == val[0:4])
        datasets = sorted(datasets, key=lambda val: not "ALCA" in val)
        datasets = sorted(datasets, key=lambda val: not "ScoutingPFMonitor" in val)
        datasets = sorted(datasets, key=lambda val: not "HighMultiplicityEOF" in val)
        datasets = sorted(datasets, key=lambda val: not "Others" in val)
        datasets = sorted(datasets, key=lambda val: not "Commisioning" in val)
        datasets = sorted(datasets, key=lambda val: not "Park" in val)
        datasets = sorted(datasets, key=lambda val: not "Scouting" in val)
        datasets = sorted(datasets, key=lambda val: not "Prompt" in val)

#        pprint.pprint(sizes)

        #dataset_sizes[datasets[0]].Draw()

        ## build stack
        if group == "main":
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
            if dataset_sizes[d].Integral()>0: leg.AddEntry(dataset_sizes[d],d) # or lep or f

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
            stack.GetXaxis().SetTitle("Era")
        stack.GetYaxis().SetTitle(getLabel(var))
        if not (var in notMergeableVariables): leg.Draw() 
        
        canvas.SaveAs("plot_"+group+"_"+var+".png")
        canvas.SaveAs("plot_"+group+"_"+var+".root")


