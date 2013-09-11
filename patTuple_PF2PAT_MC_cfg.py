import sys
sys.path.append(".")

from patTuple_PF2PAT_common_cfi import createProcess

import FWCore.ParameterSet.Config as cms

process = createProcess(True, "START62_V1")

process.source.fileNames = [
        'file:relval_TTbar_CMSSW_6_2_0.root'
        ]

process.out.fileName = cms.untracked.string('patTuple.root')

process.maxEvents.input = 200
