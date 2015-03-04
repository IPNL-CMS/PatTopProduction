from CRABClient.UserUtilities import config
config = config()

# General section
config.General.requestName = "@uiworkingdir@"
config.General.workArea = "tasks"
config.General.transferOutputs = True
config.General.transferLogs = False

# JobType section
config.JobType.pluginName = "Analysis"
config.JobType.psetName = "patTuple_PF2PAT_MC_cfg.py"
config.JobType.pyCfgParams = []
config.JobType.outputFiles = ['patTuple.root']
config.JobType.eventsPerLumi = 100
config.JobType.allowNonProductionCMSSW = True

# Data section
config.Data.inputDataset = "@datasetname@"
config.Data.inputDBS = "@dbs_url@"
config.Data.splitting = "EventAwareLumiBased"
config.Data.unitsPerJob = 50000

config.Data.publication = True
config.Data.publishDBS = "phys03"
config.Data.publishDataName = "@publish_data_name@"

# Site section
config.Site.storageSite = "T3_FR_IPNL"
