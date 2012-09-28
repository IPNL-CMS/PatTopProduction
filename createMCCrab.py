#! /usr/bin/env python

import os

version = 1
datasets = {
    "/TTJets_TuneZ2star_8TeV-madgraph-tauola/Summer12-PU_S7_START52_V5-v1/AODSIM": "TTJets",
    "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM": "Tbar_t-channel",
    "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM": "Tbar_tW-channel",
    "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM": "Tbar_s-channel",
    "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9_ext-v1/AODSIM": "T_t-channel",
    "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM": "T_tW-channel",
    "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM": "T_s-channel",
    "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM": "QCD_Pt_20_30_EMEnriched",
    "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM": "QCD_Pt_30_80_EMEnriched",
    "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM" : "QCD_Pt_80_170_EMEnriched",
    "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START52_V9-v1/AODSIM" : "QCD_Pt_20_MuEnriched",
    "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12-PU_S7_START52_V5-v2/AODSIM": "DYJetsToLL_M-50",
    "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12-PU_S7_START52_V9-v1/AODSIM": "WJetsToLNu"
    }

for dataset, ui in datasets.items():
  name = ("%s_2012_v%d") % (ui, version)
  ui_working_dir = ("crab_%s") % (name)
  publish_name = ("%s_2012_PF2PAT_v%d") % (ui, version)
  output_file = "crab_MC_%s.cfg" % name

  print "Creating config file for '%s', using publishing name '%s'" % (dataset, publish_name)
  os.system("sed -e \"s/@datasetname@/%s/g\" -e \"s/@uiworkingdir@/%s/g\" -e \"s/@publish_data_name@/%s/g\" crab_MC.cfg.template.ipnl > %s" % (dataset.replace("/", "\\/"), ui_working_dir, publish_name, output_file))
