import FWCore.ParameterSet.Config as cms

from patTuple_PF2PAT_common_cfg import createPATProcess

process = createPATProcess(True, "START53_V21")

process.source.fileNames = cms.untracked.vstring(
   '/store/mc/Summer12_DR53X/ZPrimeToTTJets_M1250GeV_W125GeV_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7A-v1/00000/7E5CC86C-7703-E211-9542-00215E221098.root' 
    )
process.maxEvents.input = cms.untracked.int32(100)
