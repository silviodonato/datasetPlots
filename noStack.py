import ROOT 

import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()


ROOTbatch = False
ROOTbatch = True
ROOT.gROOT.SetBatch(ROOTbatch)

fName = "plot_main/plot_main_era_rate.root"

f = ROOT.TFile.Open(fName)

canvas = f.Get("canvas")
stack = canvas.GetPrimitive("stack")
#leg = canvas.GetPrimitive("leg")

hists = {}

markerMap = {
    "Prompt" : 21,
    "Scouting" : 22,
    "Parking" : 23,
    "PromptParking" : 24,
}

colorMap = {
    "Prompt" : ROOT.kBlue,
    "Scouting" : ROOT.kRed,
    "Parking" : ROOT.kMagenta,
    "PromptParking" : ROOT.kGreen+3,
}

for hist in stack.GetHists():
    hists[hist.GetName()] = hist

c2 = ROOT.TCanvas("c2", "", 1920, 1600)
c2.SetGridx()
c2.SetGridy()

#hists["Prompt"].Draw()
#hists["Scouting"].Draw("same")
#hists["Parking"].Draw("same")


def convertToGraph(histo):
    graph = ROOT.TGraph(histo.GetNbinsX())
    graph.SetName("graph_"+histo.GetName())
    for i in range(len(histo)):
        if histo.GetBinContent(i)>0:
            print(i, histo.GetBinCenter(i), histo.GetBinContent(i))
            graph.SetPoint(i, histo.GetBinCenter(i), histo.GetBinContent(i))
            histo.SetBinError(i, 0)
    graph.SetTitle(stack.GetTitle())
    graph.GetXaxis().SetTitle(stack.GetXaxis().GetTitle())
    graph.GetYaxis().SetTitle(stack.GetYaxis().GetTitle())
    for i in range(stack.GetXaxis().GetNbins()):
        graph.GetXaxis().SetBinLabel(i, stack.GetXaxis().GetBinLabel(i))
    return graph

hists["PromptParking"] = hists["Prompt"].Clone("PromptParking")
hists["PromptParking"].Add(hists["Parking"])
hists["PromptParking"].SetMaximum(hists["PromptParking"].GetMaximum()*1.2)
hists["PromptParking"].SetMinimum(0)

for histName in hists:
    histo = hists[histName]
    histo.SetFillStyle(0)
    histo.SetFillStyle(0)
    color = colorMap[histName]
#    color = histo.GetFillColor()
    histo.SetLineColor(color)
    histo.SetLineWidth(2)
    histo.SetMarkerSize(3)
    histo.SetMarkerColor(color)
    histo.SetLineStyle(7)
    histo.SetMarkerStyle(markerMap[histName])
    histo.GetXaxis().SetTitle(stack.GetXaxis().GetTitle())
    histo.GetYaxis().SetTitle(stack.GetYaxis().GetTitle())
    
#     = convertToGraph(hists[histName])
#    hists[histName].SetMarkerStyle(markerMap[histName])
#    hists[histName].SetLineStyle(7)
#    hists[histName].SetLineColor(color)
#    hists[histName].SetMarkerColor(color)


#hists["Prompt"].SetMaximum( max(hists["Parking"].GetMaximum(), hists["Prompt"].GetMaximum())*1.2)

#hists["Scouting"].Draw("APL")
y_max =  hists["PromptParking"].GetMaximum()
y_min =   hists["PromptParking"].GetMinimum()
x_max =  hists["PromptParking"].GetXaxis().GetXmax()
x_min =   hists["PromptParking"].GetXaxis().GetXmin()


#scoutingRateLabel = "Average scouting Rate [Hz]"
scoutingRateLabel = hists["Scouting"].GetYaxis().GetTitle()
rightmax = hists["Scouting"].GetMaximum() * 1.3
scaled = hists["Scouting"].Clone(hists["Scouting"].GetName()+"_scaled")
canvas.Update()
canvas.Modify()
rightmin = y_min / y_max * rightmax
print(y_max, y_min, rightmax, rightmin)
scale = (y_max - y_min)/(rightmax-rightmin)
scaled.Scale(scale)

#scoutingAxis = ROOT.TGaxis(canvas.GetUxmax()+1.0,canvas.GetUymin(), canvas.GetUxmax()+1.0, canvas.GetUymax(),rightmin,rightmax,510,"+L");
scoutingAxis = ROOT.TGaxis(x_max, y_min, x_max, y_max,rightmin,rightmax,510,"+L");
scoutingAxis.SetLineColor(hists["Scouting"].GetLineColor())
scoutingAxis.SetLabelColor(hists["Scouting"].GetLineColor())
scoutingAxis.SetTitleColor(hists["Scouting"].GetLineColor())
scoutingAxis.SetTitle(scoutingRateLabel)
scoutingAxis.SetTitleFont(hists["Scouting"].GetYaxis().GetTitleFont())
scoutingAxis.SetTitleSize(hists["Scouting"].GetYaxis().GetTitleSize())
scoutingAxis.SetTitleOffset(hists["Scouting"].GetYaxis().GetTitleOffset())
scoutingAxis.SetLabelSize(hists["Scouting"].GetYaxis().GetLabelSize())

hists["PromptParking"].Draw("L HIST P")

hists["Prompt"].Draw("L HIST P same")
hists["Parking"].Draw("L HIST P same")


scaled.Draw("L HIST P same")
scoutingAxis.Draw()

leg = ROOT.TLegend(0.12,0.65,0.30,0.88)
leg.AddEntry(scaled, "Scouting", "lp") # or lep or f
leg.AddEntry(hists["Prompt"], "Prompt", "lp") # or lep or f
leg.AddEntry(hists["Parking"], "Parking", "lp") # or lep or f
leg.AddEntry(hists["PromptParking"], "PromptParking", "lp") # or lep or f
leg.Draw()

fNameNew = fName.replace(".root","_nostack.root")
c2.SaveAs(fNameNew)
c2.SaveAs(fNameNew.replace(".root",".png"))
