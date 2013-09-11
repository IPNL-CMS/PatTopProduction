import sys
sys.path.append(".")

# Request a global tag from user
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

from patTuple_PF2PAT_common_cfi import createProcess

import FWCore.ParameterSet.Config as cms

process = createProcess(False, options.globalTag)

process.source.fileNames = [
        ''
        ]

process.out.fileName = cms.untracked.string('patTuple.root')

process.maxEvents.input = 200
