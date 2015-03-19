#! /usr/bin/env python

import os, datetime, pwd, re, json

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--status", action="store_true", dest="status", default=False, help="status of crab jobs")
parser.add_option("", "--submit", action="store_true", dest="submit", default=False, help="submit crab jobs")
parser.add_option("", "--get", action="store_true", dest="get", default=False, help="getlog crab jobs")
(options, args) = parser.parse_args()

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

for dataset_path, dataset_name in datasets.items():

  gt = re.search('START\d{0,2}_V\d[A-Z]?', dataset_path)
  dataset_globaltag = None

  if gt is not None:
    dataset_globaltag = gt.group(0)

  if dataset_globaltag is not None:
    publish_name = "%s_%s_%s-v%d" % (dataset_name, dataset_globaltag, d, version)
  else:
    publish_name = "%s_%s-v%d" % (dataset_name, d, version)

  ui_working_dir = ("MC_%s") % (dataset_name)
  output_file = "crab_MC_%s.py" % (dataset_name)

  if options.submit:
    print("Creating config file for '%s'" % (dataset_path))
    print("\tName: %s" % dataset_name)
    print("\tPublishing name: %s" % publish_name)
    print("")

    if "/USER" in dataset_path:
        dbs_url = "phys02"
    else:
        dbs_url = "global"

    os.system("sed -e \"s#@datasetname@#%s#\" -e \"s#@uiworkingdir@#%s#g\" -e \"s#@publish_data_name@#%s#g\" -e \"s#@email@#%s#g\" -e \"s#@dbs_url@#%s#g\" crab_MC_template.py > %s" % (dataset_path, ui_working_dir, publish_name, email, dbs_url, output_file))


  if options.submit:
    cmd = "crab submit -c %s" % (output_file)
    os.system(cmd)

  correct_ui_working_dir = "crab_%s" % ui_working_dir
  ui_working_dir_area = (os.path.join("tasks", correct_ui_working_dir)) 

  if options.status:
    cmd = "crab status -d %s" % ui_working_dir_area
    os.system(cmd)

  if options.get:
    cmd = "crab getlog -d %s" % ui_working_dir_area
    os.system(cmd)

