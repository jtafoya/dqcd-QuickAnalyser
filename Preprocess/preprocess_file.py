#This code runs a script over a whole dataset using HTCondor
import os
import argparse
import ROOT as root
root.gROOT.SetBatch(True)
import re

#Get current directory
current_dir = os.getcwd()

#Argument parser
#python3 Preprocess/preprocess_file.py --input GIVE/EXAMPLE/PATH.root --output /vols/cms/jtafoyav/parking/QuickChecks/CMSSW_14_0_6_patch1/src/QuickAnalyser/Preprocess/output/MC
parser = argparse.ArgumentParser(description='Preprocess Dataset')
#parser.add_argument('--input', '-i', type=str, help='Input dataset path')
#parser.add_argument('--output', '-o', type=str, help='Output dataset path')
parser.add_argument('--input', '-i', default="davs://redirector.t2.ucsd.edu:1095//store/user/tafoyava/samples/nanotron/GluGluHToDarkShowers-ScenarioA_Par-ctau-0p1-mA-0p25-mpi-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24_nanotron_v15-150X_mcRun3_2024_realistic/250812_093711/0000/nano_1.root", type=str, help='Input dataset path')
parser.add_argument('--output', '-o', default="/vols/cms/jtafoyav/parking/QuickChecks/CMSSW_14_0_6_patch1/src/QuickAnalyser/Preprocess/output/MC/preprocessed_nano_1.root", type=str, help='Output dataset path')

args = parser.parse_args()

input_file=args.input
output=args.output
output_plot=output.replace(".root",".pdf")


f = root.TFile.Open(input_file, "read")
f_out = root.TFile.Open(output, "recreate")

if f and not f.IsZombie():
    print("File opened successfully!")
    print(f"Reading {input_file}")
else:
    print("Error opening file.")


tree = f.Get("Events")
if not tree:
    raise RuntimeError("Tree 'Events' not found in file!")

print(f"Tree 'Events' loaded with {tree.GetEntries()} entries.")

# Disable all branches
tree.SetBranchStatus("*", 0)

# Enable only relevant branches
tree.SetBranchStatus("fourmuonSV_mass", 1)
tree.SetBranchStatus("muonSV_mass", 1)


h_fourmuonSV_mass = root.TH1F("h_fourmuonSV_mass", "Four-muon SV Mass;Mass [GeV];Events", 100, 0, 100)
h_muonSV_mass = root.TH1F("h_muonSV_mass", "Muon SV Mass;Mass [GeV];Events", 100, 0, 50)


#for event in tree:
for i, event in enumerate(tree):
    if i % 1000 == 0:
        print(f"Processed {i} events")

    for val in event.fourmuonSV_mass:
        h_fourmuonSV_mass.Fill( val )

    for val in event.muonSV_mass:
        h_muonSV_mass.Fill( val )


#Draw outputs
c = root.TCanvas("c", "Histograms", 800, 600)
c.Divide(2,1)

c.cd(1)
h_fourmuonSV_mass.SetLineColor(root.kBlue)
h_fourmuonSV_mass.Draw()

c.cd(2)
h_muonSV_mass.SetLineColor(root.kRed)
h_muonSV_mass.Draw()

c.Update()
c.Draw()

c.SaveAs(output_plot,"pdf")

# Write histograms into the output ROOT file
f_out.cd()
h_fourmuonSV_mass.Write()
h_muonSV_mass.Write()
f_out.Close()
f.Close()

print(f"Output saved to {output}")
