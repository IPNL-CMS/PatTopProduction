#! /usr/bin/env python

import os, datetime, pwd

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(options, args) = parser.parse_args()

global_json = "Cert_190456-206940_8TeV_PromptReco_Collisions12_JSON.txt"

datasets = [
    ["/MuHad/Run2012A-13Jul2012-v1/AOD", "MuHad_Run2012A-13Jul2012", "Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt", [190456, 193621]],
    ["/MuHad/Run2012A-recover-06Aug2012-v1/AOD", "MuHad_Run2012A-recover-06Aug2012", "Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt", [190782, 190949]],
    ["/SingleMu/Run2012B-TOPMuPlusJets-13Jul2012-v1/AOD", "SingleMu_Run2012B-TOPMuPlusJets-13Jul2012", "Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt", [193833, 196531]],
    ["/SingleMu/Run2012C-TOPMuPlusJets-24Aug2012-v1/AOD", "SingleMu_Run2012C-TOPMuPlusJets-24Aug2012", "Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt", [198022, 198913]],
    ["/SingleMu/Run2012C-TOPMuPlusJets-PromptSkim-v3/AOD", "SingleMu_Run2012C-TOPMuPlusJets-PromptSkim", "", [198934, 203746]],
    ["/SingleMu/Run2012D-TOPMuPlusJets-PromptSkim-v1/AOD", "SingleMu_Run2012D-TOPMuPlusJets-PromptSkim", "", []],

    ["/ElectronHad/Run2012A-13Jul2012-v1/AOD", "ElectronHad_Run2012A-13Jul2012", "Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt", [190456, 193621]],
    ["/ElectronHad/Run2012A-recover-06Aug2012-v1/AOD", "ElectronHad_Run2012A-recover-06Aug2012", "Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt", [190782, 190949]],
    ["/SingleElectron/Run2012B-TOPMuPlusJets-13Jul2012-v1/AOD", "SingleElectron_Run2012B-TOPMuPlusJets-13Jul2012", "Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt", [193833, 196531]],
    ["/SingleElectron/Run2012C-TOPElePlusJets-24Aug2012-v1/AOD", "SingleElectron_Run2012C-TOPElePlusJets-24Aug2012", "Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt", [198022, 198913]],
    ["/SingleElectron/Run2012C-TOPElePlusJets-PromptSkim-v3/AOD", "SingleElectron_Run2012C-TOPElePlusJets-PromptSkim", "", [198934, 203746]],
    ["/SingleElectron/Run2012D-TOPElePlusJets-PromptSkim-v1/AOD", "SingleElectron_Run2012D-TOPElePlusJets-PromptSkim", "", []]

    ]

# Get email address
email = "%s@ipnl.in2p3.fr" % (pwd.getpwuid(os.getuid()).pw_name)

d = datetime.datetime.now().strftime("%d%b%y")

version = 1

print("Creating configs for crab. Today is %s, you are %s and it's version %d" % (d, email, version))
print("")

for dataset in datasets:
  dataset_path = dataset[0]
  dataset_name = dataset[1]
  dataset_json = dataset[2]
  if len(dataset_json) == 0:
    dataset_json = global_json

  runselection = ""
  if len(dataset) > 3 and len(dataset[3]) == 2:
    runselection = "runselection = %d-%d" % (dataset[3][0], dataset[3][1])

  publish_name = "%s_%s-v%d" % (dataset_name, d, version)
  ui_working_dir = ("crab_data_%s") % (dataset_name)
  output_file = "crab_data_%s.cfg" % (dataset_name)

  print("Creating config file for '%s'" % (dataset_path))
  print("\tName: %s" % dataset_name)
  print("\tJSON: %s" % dataset_json)
  print("\tRun selection: %s" % runselection)
  print("\tPublishing name: %s" % publish_name)
  print("")

  os.system("sed -e \"s#@datasetname@#%s#\" -e \"s#@uiworkingdir@#%s#g\" -e \"s#@lumi_mask@#%s#g\" -e \"s#@runselection@#%s#g\" -e \"s#@publish_data_name@#%s#g\" -e \"s#@email@#%s#g\" crab_data.cfg.template.ipnl > %s" % (dataset_name, ui_working_dir, dataset_json, runselection, publish_name, email, output_file))

  cmd = "crab -create -submit -cfg %s" % (output_file)
  if options.run:
    os.system(cmd)
