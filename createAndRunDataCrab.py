#! /usr/bin/env python

import os, datetime, pwd, json

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(option, args) = parser.parse_args()

global_json = "Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt"

# Load each json files and build dataset array
datasets = {}
for file in args:
    with open(file) as f:
        datasets.update(json.load(f))

# Get email address
email = "%s@ipnl.in2p3.fr" % (pwd.getpwuid(os.getuid()).pw_name)

d = datetime.datetime.now().strftime("%d%b%y")

version = 1

print("Creating configs for crab. Today is %s, you are %s and it's version %d" % (d, email, version))
print("")

for (dataset, options) in datasets.items():
  dataset_path = dataset
  dataset_name = options["name"]
  dataset_json = options["json_file"] if "json_file" in options else ""
  if len(dataset_json) == 0:
    dataset_json = global_json

  dataset_globaltag = options["global_tag"]

  runselection = ""
  if "run_range" in options and len(options["run_range"]) == 2:
    runselection = "runselection = %d-%d" % (options["run_range"][0], options["run_range"][1])

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
  if option.run:
    os.system(cmd)
