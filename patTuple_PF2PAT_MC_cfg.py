import FWCore.ParameterSet.Config as cms
import sys
sys.path.append('.')

from patTuple_PF2PAT_common_cfg import createPATProcess

process = createPATProcess(True, "MCRUN2_74_V9A")

process.source.fileNames = cms.untracked.vstring(
        'root://xrootd-cms.infn.it://store/mc/RunIISpring15DR74/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/Asympt50ns_MCRUN2_74_V9A-v1/00000/02B15AC7-E701-E511-8C2C-002590596486.root'
    )
process.maxEvents.input = cms.untracked.int32(100)
