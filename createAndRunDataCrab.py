#! /usr/bin/env python

import os, datetime, pwd

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(options, args) = parser.parse_args()

global_json = "Cert_190456-203742_8TeV_22Jan2013ReReco_Collisions12_JSON.txt"

datasets = [
    ["/MuHad/Run2012A-22Jan2013-v1/AOD", "MuHad_Run2012A-22Jan2013", "", "FT_53_V21_AN3", [190456, 193621]],
    ["/SingleMu/Run2012B-TOPMuPlusJets-22Jan2013-v1/AOD", "SingleMu_Run2012B-TOPMuPlusJets-22Jan2013", "", "FT_53_V21_AN3", [193833, 196531]],
    ["/SingleMu/Run2012C-TOPMuPlusJets-22Jan2013-v1/AOD", "SingleMu_Run2012C-TOPMuPlusJets-22Jan2013", "", "FT_53_V21_AN3", [198022, 203742]],
    ["/SingleMu/Run2012D-TOPMuPlusJets-22Jan2013-v1/AOD", "SingleMu_Run2012D-TOPMuPlusJets-22Jan2013", "", "FT_53_V21_AN3", [203768, 208686 ]],
    ["/ElectronHad/Run2012A-22Jan2013-v1/AOD", "ElectronHad_Run2012A-22Jan2013", "", "FT_53_V21_AN3", [190456, 193621]],
    ["/SingleElectron/Run2012B-TOPElePlusJets-22Jan2013-v1/AOD", "SingleElectron_Run2012B-TOPElePlusJets-22Jan2013", "", "FT_53_V21_AN3", [193833, 196531]],
    ["/SingleElectron/Run2012C-TOPElePlusJets-22Jan2013-v1/AOD", "SingleElectron_Run2012C-TOPElePlusJets-22Jan2013", "", "FT_53_V21_AN3", [198022, 203742]],
    ["/SingleElectron/Run2012D-TOPElePlusJets-22Jan2013-v1/AOD", "SingleElectron_Run2012D-TOPElePlusJets-22Jan2013", "", "FT_53_V21_AN3", [203768, 208686 ]],
## ["/DoubleElectron/Run2012A-22Jan2013-v1/AOD", "DoubleElectron_Run2012A-22Jan2013", "", "FT_53_V21_AN3", [190456, 193621]],
##     ["/DoubleElectron/Run2012B-22Jan2013-v1/AOD", "DoubleElectron_Run2012B-22Jan2013", "", "FT_53_V21_AN3", [193833, 196531]],
##     ["/DoubleElectron/Run2012C-22Jan2013-v1/AOD", "DoubleElectron_Run2012C-22Jan2013", "", "FT_53_V21_AN3", [198022, 203742]],
##     ["/DoubleElectron/Run2012D-22Jan2013-v1/AOD", "DoubleElectron_Run2012D-22Jan2013", "", "FT_53_V21_AN3", [203768, 208686 ]],
##     ["/DoubleMu/Run2012A-22Jan2013-v1/AOD", "DoubleMu_Run2012A-22Jan2013", "", "FT_53_V21_AN3", [190456, 193621]],
##     ["/DoubleMuParked/Run2012B-22Jan2013-v1/AOD", "DoubleMuParked_Run2012B-22Jan2013", "", "FT_53_V21_AN3", [193833, 196531]],
##     ["/DoubleMuParked/Run2012C-22Jan2013-v1/AOD", "DoubleMuParked_Run2012C-22Jan2013", "", "FT_53_V21_AN3", [198022, 203742]],
##     ["/DoubleMuParked/Run2012D-22Jan2013-v1/AOD", "DoubleMuParked_Run2012D-22Jan2013", "", "FT_53_V21_AN3", [203768, 208686 ]],
##     ["/MuEG/Run2012A-22Jan2013-v1/AOD", "MuEG_Run2012A-22Jan2013", "", "FT_53_V21_AN3", [190456, 193621]],
##     ["/MuEG/Run2012B-22Jan2013-v1/AOD", "MuEG_Run2012B-22Jan2013", "", "FT_53_V21_AN3", [193833, 196531]],
##     ["/MuEG/Run2012C-22Jan2013-v1/AOD", "MuEG_Run2012C-22Jan2013", "", "FT_53_V21_AN3", [198022, 203742]],
##     ["/MuEG/Run2012D-22Jan2013-v1/AOD", "MuEG_Run2012D-22Jan2013", "", "FT_53_V21_AN3", [203768, 208686 ]],
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

  dataset_globaltag = dataset[3]

  runselection = ""
  if len(dataset) > 4 and len(dataset[4]) == 2:
    runselection = "runselection = %d-%d" % (dataset[4][0], dataset[4][1])

  publish_name = "%s_%s-v%d" % (dataset_name, d, version)
  ui_working_dir = ("crab_data_%s") % (dataset_name)
  output_file = "crab_data_%s.cfg" % (dataset_name)

  print("Creating config file for '%s'" % (dataset_path))
  print("\tName: %s" % dataset_name)
  print("\tJSON: %s" % dataset_json)
  print("\tGlobal tag: %s" % dataset_globaltag)
  print("\tRun selection: %s" % runselection)
  print("\tPublishing name: %s" % publish_name)
  print("")

  os.system("sed -e \"s#@datasetname@#%s#\" -e \"s#@uiworkingdir@#%s#g\" -e \"s#@lumi_mask@#%s#g\" -e \"s#@runselection@#%s#g\" -e \"s#@publish_data_name@#%s#g\" -e \"s#@email@#%s#g\" -e \"s#@globaltag@#%s#g\" crab_data.cfg.template.ipnl > %s" % (dataset_path, ui_working_dir, dataset_json, runselection, publish_name, email, dataset_globaltag, output_file))

  cmd = "crab -create -submit -cfg %s" % (output_file)
  if options.run:
    os.system(cmd)
