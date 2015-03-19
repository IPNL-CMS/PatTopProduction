import FWCore.ParameterSet.Config as cms
import sys
sys.path.append('.')

from patTuple_PF2PAT_common_cfg import createPATProcess

process = createPATProcess(True, "PHYS14_25_V2")

process.source.fileNames = cms.untracked.vstring(
        'root://xrootd-cms.infn.it://store/relval/CMSSW_7_3_3/RelValTTbar_13/GEN-SIM-RECO/PU25ns_MCRUN2_73_V11-v1/00000/D0E8B3FA-E3C3-E411-9E60-002618943959.root'
    )
process.maxEvents.input = cms.untracked.int32(100)
