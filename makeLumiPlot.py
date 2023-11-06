# Read the .csv file
## lumi.csv done with brilcalc 
# lumi --byls  -b "STABLE BEAMS"  --begin 366396  --end 370865  -o tmp/lumi.csv
## lumi_golden.csv done with 
# lumi --byls  -b "STABLE BEAMS"  -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json  -o lumi_golden.csv

import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()

golden = False
golden = True
f = 'lumi.csv'
if golden:
    f = 'lumi_golden.csv'
with open(f, 'r') as file:
    lines = file.readlines()

# Initialize an empty list to store dictionaries
data_list = []

# Process each line starting from the third line (skipping comments and column descriptions)
for line in lines[2:-5]:
    # Split the line by commas
    values = line.strip().split(',')

    # Extract column descriptions from the second line
    columns = lines[1].strip().split(',')

    # Create a dictionary for the current line
    data_dict = {}
    for i in range(len(columns)):
        data_dict[columns[i]] = values[i]

    # Append the dictionary to the list
    data_list.append(data_dict)

# Print the list of dictionaries
#for item in data_list:
#    print(item)

import ROOT

histo_PU = ROOT.TH1F("histo_PU","",100,0,100)
histo_lumi = ROOT.TH1F("histo_lumi","",100,0,2.5)
histo_PU.GetYaxis().SetTitle("# lumisections ")
histo_lumi.GetYaxis().SetTitle("# lumisections ")
histo_PU.GetXaxis().SetTitle("average pileup")
histo_lumi.GetXaxis().SetTitle("instantaneous luminosity 10^{34}cm^{-2}s^{-1}")

histo_PU.SetLineColor(ROOT.kBlack)
histo_PU.SetFillColor(ROOT.kBlue)
histo_lumi.SetLineColor(ROOT.kBlack)
histo_lumi.SetFillColor(ROOT.kBlue)

histo_lumiRec = histo_lumi.Clone("histo_lumiRec")
xsection = 80000
for ls in data_list:
    lumi = float(ls["delivered(/ub)"])
    lumiRec = float(ls["recorded(/ub)"])
    pu = float(ls["avgpu"])
    histo_PU.Fill(pu)
    histo_lumi.Fill(lumi/23.31/1E4)
    histo_lumiRec.Fill(lumiRec/23.31/1E4)

c1 = ROOT.TCanvas("c1")
outFile = "brilcal_PU.png"
if golden:
    outFile = outFile.replace(".png", "_golden.png")
histo_PU.Draw()
c1.SaveAs(outFile)

outFile = outFile.replace("_PU", "_recLumi")
histo_lumi.Draw()
c1.SaveAs(outFile)

outFile = outFile.replace("_recLumi", "_lumi")
histo_lumiRec.Draw()
c1.SaveAs(outFile)

print("Mean pileup=%.1f, delivered lumi=%.2f, recorded lumi=%.f"%(histo_PU.GetMean(), histo_lumi.GetMean(), histo_lumiRec.GetMean()))

