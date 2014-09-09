import FWCore.ParameterSet.Config as cms
import sys
sys.path.append('.')

from patTuple_PF2PAT_common_cfg import createPATProcess

process = createPATProcess(True, "POSTLS172_V1")

process.source.fileNames = cms.untracked.vstring(
        'file:Zprime750_13TeV_aodsim.root'
    )
process.maxEvents.input = cms.untracked.int32(100)
