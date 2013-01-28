#! /usr/bin/env python

import os, datetime, pwd, re

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(options, args) = parser.parse_args()

datasets = {
    ## Single top
    #"/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Tbar_s-channel",
    #"/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Tbar_t-channel",
    #"/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Tbar_tW-channel",

    ## Single anti-top
    #"/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "T_t-channel",
    #"/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "T_tW-channel",
    #"/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "T_s-channel",

    ## TT + jets
    #"/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "TTJets_MassiveBinDECAY",

    ##"/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM": "QCD_Pt_20_30_EMEnriched",
    ##"/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM": "QCD_Pt_30_80_EMEnriched",
    ##"/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM" : "QCD_Pt_80_170_EMEnriched",
    ##"/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM" : "QCD_Pt_20_MuEnriched",

    #"/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "DYJetsToLL_M-50",
    #"/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM": "WJetsToLNu"

    # Signal datasets
    # RS Gluons
    #"/RSGluonToTT_M-700_Tune4C_8TeV-pythia8/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "RSGluon700",
    #"/RSGluonToTT_M-1000_Tune4C_8TeV-pythia8/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "RSGluon1000",
    #"/RSGluonToTT_M-1200_Tune4C_8TeV-pythia8/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "RSGluon1200",
    #"/RSGluonToTT_M-1500_Tune4C_8TeV-pythia8/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "RSGluon1500",
    #"/RSGluonToTT_M-1600_Tune4C_8TeV-pythia8/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "RSGluon1600",
    #"/RSGluonToTT_M-2000_Tune4C_8TeV-pythia8/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "RSGluon2000",

    # Z' narrow
    #"/ZPrimeToTTJets_M500GeV_W5GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Zprime_500_Narrow",
    "/ZPrimeToTTJets_M500GeV_W5GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM": "Zprime_500_Narrow_ext",
    #"/ZPrimeToTTJets_M750GeV_W7p5GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_750_Narrow",
    #"/ZPrimeToTTJets_M750GeV_W7p5GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_750_Narrow_ext",
    #"/ZPrimeToTTJets_M1000GeV_W10GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_1000_Narrow",
    #"/ZPrimeToTTJets_M1000GeV_W10GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_1000_Narrow_ext",
    #"/ZPrimeToTTJets_M1250GeV_W12p5GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_1250_Narrow",
    #"/ZPrimeToTTJets_M1250GeV_W12p5GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_1250_Narrow_ext",
    #"/ZPrimeToTTJets_M1500GeV_W15GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_1500_Narrow",
    #"/ZPrimeToTTJets_M1500GeV_W15GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_1500_Narrow_ext",
    #"/ZPrimeToTTJets_M2000GeV_W20GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_2000_Narrow",
    #"/ZPrimeToTTJets_M2000GeV_W20GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_2000_Narrow_ext",

    # Z' large
    "/ZPrimeToTTJets_M500GeV_W50GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Zprime_500_Large",
    "/ZPrimeToTTJets_M500GeV_W50GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM": "Zprime_500_Large_ext",
    #"/ZPrimeToTTJets_M750GeV_W75GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_750_Large",
    #"/ZPrimeToTTJets_M750GeV_W75GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_750_Large_ext",
    #"/ZPrimeToTTJets_M1000GeV_W100GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_1000_Large",
    #"/ZPrimeToTTJets_M1000GeV_W100GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_1000_Large_ext",
    #"/ZPrimeToTTJets_M1250GeV_W125GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_1250_Large",
    #"/ZPrimeToTTJets_M1250GeV_W125GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_1250_Large_ext",
    #"/ZPrimeToTTJets_M1500GeV_W150GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_1500_Large",
    #"/ZPrimeToTTJets_M1500GeV_W150GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_1500_Large_ext",
    #"/ZPrimeToTTJets_M2000GeV_W200GeV_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM" : "Zprime_2000_Large"
    #"/ZPrimeToTTJets_M2000GeV_W200GeV_TuneZ2star_8TeV_ext-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM" : "Zprime_2000_Large_ext"

    }

# Get email address
email = "%s@ipnl.in2p3.fr" % (pwd.getpwuid(os.getuid()).pw_name)

d = datetime.datetime.now().strftime("%d%b%y")

version = 1

print("Creating configs for crab. Today is %s, you are %s and it's version %d" % (d, email, version))
print("")

for dataset_path, dataset_name in datasets.items():

  dataset_globaltag = re.search('START\d{0,2}_V\d[A-Z]?', dataset_path).group(0)

  publish_name = "%s_%s_%s-v%d" % (dataset_name, dataset_globaltag, d, version)
  ui_working_dir = ("crab_MC_%s") % (dataset_name)
  output_file = "crab_MC_%s.cfg" % (dataset_name)

  print("Creating config file for '%s'" % (dataset_path))
  print("\tName: %s" % dataset_name)
  print("\tPublishing name: %s" % publish_name)
  print("")

  os.system("sed -e \"s#@datasetname@#%s#\" -e \"s#@uiworkingdir@#%s#g\" -e \"s#@publish_data_name@#%s#g\" -e \"s#@email@#%s#g\" crab_MC.cfg.template.ipnl > %s" % (dataset_path, ui_working_dir, publish_name, email, output_file))

  cmd = "crab -create -submit -cfg %s" % (output_file)
  if options.run:
    os.system(cmd)
