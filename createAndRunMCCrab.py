#! /usr/bin/env python

import os, datetime, pwd, re, json

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--create", action="store_true", dest="create", default=False, help="create crab task")
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
parser.add_option("", "--submit", action="store_true", dest="submit", default=False, help="submit crab jobs")
(options, args) = parser.parse_args()

if options.run:
    options.create = True

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

  ui_working_dir = ("crab_MC_%s") % (dataset_name)
  output_file = "crab_MC_%s.py" % (dataset_name)

  if options.create:
    print("Creating config file for '%s'" % (dataset_path))
    print("\tName: %s" % dataset_name)
    print("\tPublishing name: %s" % publish_name)
    print("")

    if "/USER" in dataset_path:
        dbs_url = "http://cmsdbsprod.cern.ch/cms_dbs_ph_analysis_02/servlet/DBSServlet"
    else:
        dbs_url = "http://cmsdbsprod.cern.ch/cms_dbs_prod_global/servlet/DBSServlet"

    os.system("sed -e \"s#@datasetname@#%s#\" -e \"s#@uiworkingdir@#%s#g\" -e \"s#@publish_data_name@#%s#g\" -e \"s#@email@#%s#g\" -e \"s#@dbs_url@#%s#g\" crab_MC_template.py > %s" % (dataset_path, ui_working_dir, publish_name, email, dbs_url, output_file))


  if options.run:
    cmd = "crab -create -submit -cfg %s" % (output_file)
    os.system(cmd)

  if options.submit:
    cmd = "crab -submit 1-500 -c %s" % ui_working_dir
    os.system(cmd)

    cmd = "crab -submit 500-1000 -c %s" % ui_working_dir
    os.system(cmd)

    cmd = "crab -submit 1000-1500 -c %s" % ui_working_dir
    os.system(cmd)
