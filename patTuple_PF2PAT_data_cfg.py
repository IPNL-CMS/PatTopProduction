from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing()

options.register ('globalTag',
        '',
        VarParsing.multiplicity.singleton,
        VarParsing.varType.string,
        "The globaltag to be used")

options.parseArguments()
if len(options.globalTag) == 0:
    raise Exception("You _must_ pass a globalTag options to this script. Use --help for more informations")

import sys
sys.path.append('.')

from patTuple_PF2PAT_common_cfg import createPATProcess
process = createPATProcess(False, options.globalTag)

process.source.fileNames = [ 
        #'file:input_data.root'
        #'/store/data/Run2012C/SingleMu/AOD/TOPMuPlusJets-24Aug2012-v1/00000/C8186FFC-2BEF-E111-80FB-001EC9D8D993.root'
        '/store/data/Run2012B/SingleMu/AOD/TOPMuPlusJets-22Jan2013-v1/20000/FA21ADAF-AE71-E211-83D4-90E6BA19A243.root'
        ]

process.maxEvents.input = -1
process.options.wantSummary = False
process.MessageLogger.cerr.FwkReport.reportEvery = 100
