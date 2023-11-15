import ROOT 

import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()

yTitle = "Average event size [MB/event]" ## PB/B = E15/E9 = E6 --> MB/event

ROOTbatch = False
ROOTbatch = True
ROOT.gROOT.SetBatch(ROOTbatch)

num_, den_ = "data", "events"

fNames = [
#    "plot/plot_main_era_%s.root",
#    "plot/plot_main_year_%s.root",
    "plot_main/plot_main_era_%s.root",
    "plot_main/plot_main_year_%s.root",
]

#firstHisto = "DisplacedJet"
firstHisto = "Prompt"


for fName in fNames:
    num = ROOT.TFile.Open(fName%num_)
    den = ROOT.TFile.Open(fName%den_)
    
    canvas_den = den.Get("canvas")
    stack_den = canvas_den.GetPrimitive("stack")
    
    canvas_num = num.Get("canvas")
    stack_num = canvas_num.GetPrimitive("stack")
    #leg = canvas.GetPrimitive("leg")

    hists_den = {}
    hists_num = {}

    markerMap = {
        "Prompt" : 21,
        "Scouting" : 22,
        "Parking" : 23,
#        "PromptParking" : 24,
    }

    colorMap = {
        "Prompt" : ROOT.kBlue,
        "Scouting" : ROOT.kRed,
        "Parking" : ROOT.kMagenta,
#        "PromptParking" : ROOT.kGreen+3,
    }
    
    for hist in stack_den.GetHists():
        hists_den[hist.GetName()] = hist
    
    for hist in stack_num.GetHists():
        hists_num[hist.GetName()] = hist

    for hist in list(hists_num.values()):
        hist = hist.Divide(hists_den[hist.GetName()])
    
    c2 = ROOT.TCanvas("c2", "", 1920, 1600)
    c2.SetGridx()
    c2.SetGridy()

    #hists[firstHisto].Draw()
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
    
    for histo in list(hists_num.values())+list(hists_den.values()):
        histName = histo.GetName()
        histo.SetFillStyle(0)
        histo.SetFillStyle(0)
        if histName in colorMap:
            color = colorMap[histName]
        else:
            color = histo.GetFillColor()
    #    color = histo.GetFillColor()
        histo.SetLineColor(color)
        histo.SetLineWidth(2)
        histo.SetMarkerSize(3)
        histo.SetMarkerColor(color)
        histo.SetLineStyle(7)
        if histName in markerMap:
            histo.SetMarkerStyle(markerMap[histName])
        else:
            histo.SetMarkerStyle(21)
        histo.GetXaxis().SetTitle(stack_num.GetXaxis().GetTitle())
        histo.GetYaxis().SetTitle(yTitle)
        
    hists_num[firstHisto].SetMinimum(0)
    y_max =  hists_num[firstHisto].GetMaximum()
    y_min =   hists_num[firstHisto].GetMinimum()
    x_max =  hists_num[firstHisto].GetXaxis().GetXmax()
    x_min =   hists_num[firstHisto].GetXaxis().GetXmin()
    
    if "Scouting" in hists_num:
        #scoutingRateLabel = "Average scouting Rate [Hz]"
        scoutingRateLabel = hists_num["Scouting"].GetYaxis().GetTitle()
        rightmax = hists_num["Scouting"].GetMaximum() * 1.3
        scaled = hists_num["Scouting"].Clone(hists_num["Scouting"].GetName()+"_scaled")
        canvas_num.Update()
        canvas_num.Modify()
        rightmin = y_min / y_max * rightmax
        print(y_max, y_min, rightmax, rightmin)
        scale = (y_max - y_min)/(rightmax-rightmin)
        scaled.Scale(scale)

        #scoutingAxis = ROOT.TGaxis(canvas.GetUxmax()+1.0,canvas.GetUymin(), canvas.GetUxmax()+1.0, canvas.GetUymax(),rightmin,rightmax,510,"+L");
        scoutingAxis = ROOT.TGaxis(x_max, y_min, x_max, y_max,rightmin,rightmax,510,"+L");
        scoutingAxis.SetLineColor(hists_num["Scouting"].GetLineColor())
        scoutingAxis.SetLabelColor(hists_num["Scouting"].GetLineColor())
        scoutingAxis.SetTitleColor(hists_num["Scouting"].GetLineColor())
        scoutingAxis.SetTitle(scoutingRateLabel)
        scoutingAxis.SetTitleFont(hists_num["Scouting"].GetYaxis().GetTitleFont())
        scoutingAxis.SetTitleSize(hists_num["Scouting"].GetYaxis().GetTitleSize())
        scoutingAxis.SetTitleOffset(hists_num["Scouting"].GetYaxis().GetTitleOffset())
        scoutingAxis.SetLabelSize(hists_num["Scouting"].GetYaxis().GetLabelSize())

    hists_num[firstHisto].Draw("L HIST P")
    for hist in hists_num:
        if hist == firstHisto: continue
        hists_num[hist].Draw("L HIST P same")
    
    leg = ROOT.TLegend(0.12,0.65,0.30,0.88)
    if "Scouting" in hists_num:
        scaled.Draw("L HIST P same")
        scoutingAxis.Draw()
        leg.AddEntry(scaled, "Scouting", "lp") # or lep or f
    
    for hist in hists_num:
        if hist == "Scouting": continue
        leg.AddEntry(hists_num[hist], hist, "lp") # or lep or f
#    leg.AddEntry(hists_num[firstHisto], firstHisto, "lp") # or lep or f
#    leg.AddEntry(hists_num["Parking"], "Parking", "lp") # or lep or f
    leg.Draw()
    
    fNameNew = (fName%num_).replace(".root","_%s.root"%den_)
    c2.SaveAs(fNameNew)
    c2.SaveAs(fNameNew.replace(".root",".png"))
    del c2
