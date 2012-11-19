#! /usr/bin/env python

import os, datetime, pwd, re

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(options, args) = parser.parse_args()

datasets = {
    # Single top
    "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Tbar_s-channel",
    "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Tbar_t-channel",
    "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "Tbar_tW-channel",

    # Single anti-top
    "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "T_t-channel",
    "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "T_tW-channel",
    "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "T_s-channel",

    # TT + jets
    "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "TTJets_MassiveBinDECAY",

    #"/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM": "QCD_Pt_20_30_EMEnriched",
    #"/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM": "QCD_Pt_30_80_EMEnriched",
    #"/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM" : "QCD_Pt_80_170_EMEnriched",
    #"/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM" : "QCD_Pt_20_MuEnriched",

    "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM": "DYJetsToLL_M-50",
    "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM": "WJetsToLNu"
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

  os.system("sed -e \"s#@datasetname@#%s#\" -e \"s#@uiworkingdir@#%s#g\" -e \"s#@publish_data_name@#%s#g\" -e \"s#@email@#%s#g\" crab_MC.cfg.template.ipnl > %s" % (dataset_name, ui_working_dir, publish_name, email, output_file))

  cmd = "crab -create -submit -cfg %s" % (output_file)
  if options.run:
    os.system(cmd)
