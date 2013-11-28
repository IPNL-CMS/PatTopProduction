from PhysicsTools.PatAlgos.patTemplate_cfg import *

print("Loading python config...")

runOnMC = True

process.load("PhysicsTools.PatAlgos.patSequences_cff")

process.primaryVertexFilter = cms.EDFilter("VertexSelector",
    src = cms.InputTag("offlinePrimaryVertices"),
    cut = cms.string("!isFake & ndof > 4 & abs(z) <= 24 & position.Rho <= 2"),
    filter = cms.bool(True)
    )

process.goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
    filterParams = cms.PSet(minNdof = cms.double(4.), maxZ = cms.double(24.) , maxRho = cms.double(2.)),
    filter = cms.bool(True),
    src = cms.InputTag('offlinePrimaryVertices')
    )

from PhysicsTools.PatAlgos.tools.pfTools import *

postfix = "PFlow"
jetAlgo = "AK5"
# Jet corrections when using CHS (L2L3Residual IS mandatory on data)
jetCorrections = ('AK5PFchs', ['L1FastJet','L2Relative','L3Absolute'] )
# Jet corrections when NOT using CHS
#jetCorrections = ('AK5PF', ['L1FastJet','L2Relative','L3Absolute'] )

# Type I MET enabled
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=runOnMC , postfix=postfix, jetCorrections = jetCorrections, typeIMetCorrections=True,
  pvCollection = cms.InputTag('goodOfflinePrimaryVertices'))

# Add Type-0 corrections to path
process.patType0MetCorrections = cms.Sequence(
		process.type0PFMEtCorrection *
		process.patPFMETtype0Corr
		)

cloneProcessingSnippet(process, process.patType0MetCorrections, postfix);

process.producePatPFMETCorrectionsPFlow.replace(getattr(process, 'patPFJetMETtype2Corr' + postfix), getattr(process, 'patPFJetMETtype2Corr' + postfix) * getattr(process, 'patType0MetCorrections' + postfix))

# Turn on Type 0 + Type I correction for MET on a cloned collection
setattr(process, 'patType0p1CorrectedPFMet' + postfix, getattr(process, 'patType1CorrectedPFMet' + postfix).clone(
    srcType1Corrections = cms.VInputTag(
      cms.InputTag("patPFJetMETtype1p2Corr" + postfix, "type1"),
      cms.InputTag("patPFMETtype0Corr" + postfix)
    )
  )
)

setattr(process, 'patMETsType0p1' + postfix, getattr(process, 'patMETs' + postfix).clone(
    metSource = cms.InputTag("patType0p1CorrectedPFMet" + postfix)
    )
)

process.producePatPFMETCorrectionsPFlow.replace(getattr(process, 'patType1CorrectedPFMet' + postfix),
  getattr(process, 'patType1CorrectedPFMet' + postfix) * getattr(process, 'patType0p1CorrectedPFMet' + postfix))

process.patDefaultSequencePFlow.replace(getattr(process, 'patMETs' + postfix),
  getattr(process, 'patMETs' + postfix) * getattr(process, 'patMETsType0p1' + postfix)
)

# Clone our METs, and apply x/y shift correction (phi modulation)
process.load("JetMETCorrections.Type1MET.pfMETCorrections_cff")
process.load("JetMETCorrections.Type1MET.pfMETsysShiftCorrections_cfi")

# use for 2012 Data
#process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runAplusBvsNvtx_data

# use for Spring'12 MC
process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_mc

# CLone our Type 0 + Type I MET, and add Phi corrections
setattr(process, 'patType0p1ShiftCorrCorrectedPFMet' + postfix, getattr(process, 'patType1CorrectedPFMet' + postfix).clone(
    srcType1Corrections = cms.VInputTag(
      cms.InputTag("patPFJetMETtype1p2Corr" + postfix, "type1"),
      cms.InputTag("patPFMETtype0Corr" + postfix),
      cms.InputTag('pfMEtSysShiftCorr')
    )
  )
)

setattr(process, 'patMETsType0p1ShiftCorr' + postfix, getattr(process, 'patMETs' + postfix).clone(
    metSource = cms.InputTag("patType0p1ShiftCorrCorrectedPFMet" + postfix)
    )
)

process.producePatPFMETCorrectionsPFlow.replace(getattr(process, 'patType1CorrectedPFMet' + postfix),
  getattr(process, 'patType1CorrectedPFMet' + postfix) * getattr(process, 'patType0p1ShiftCorrCorrectedPFMet' + postfix))

process.patDefaultSequencePFlow.replace(getattr(process, 'patMETs' + postfix),
  getattr(process, 'patMETs' + postfix) * getattr(process, 'patMETsType0p1ShiftCorr' + postfix)
)

# Clone our Type I MET, and add Phi corrections
setattr(process, 'patType1ShiftCorrCorrectedPFMet' + postfix, getattr(process, 'patType1CorrectedPFMet' + postfix).clone(
    srcType1Corrections = cms.VInputTag(
      cms.InputTag("patPFJetMETtype1p2Corr" + postfix, "type1"),
      cms.InputTag('pfMEtSysShiftCorr')
    )
  )
)

setattr(process, 'patMETsShiftCorr' + postfix, getattr(process, 'patMETs' + postfix).clone(
    metSource = cms.InputTag("patType1ShiftCorrCorrectedPFMet" + postfix)
    )
)

process.producePatPFMETCorrectionsPFlow.replace(getattr(process, 'patType1CorrectedPFMet' + postfix),
  getattr(process, 'patType1CorrectedPFMet' + postfix) * getattr(process, 'patType1ShiftCorrCorrectedPFMet' + postfix))

process.patDefaultSequencePFlow.replace(getattr(process, 'patMETs' + postfix),
  getattr(process, 'patMETs' + postfix) * getattr(process, 'patMETsShiftCorr' + postfix)
)

process.patDefaultSequencePFlow.replace(getattr(process, 'producePatPFMETCorrections' + postfix),
    process.pfMEtSysShiftCorrSequence * getattr(process, 'producePatPFMETCorrections' + postfix))

# Enable CHS
process.pfPileUpPFlow.Enable = True
process.pfPileUpPFlow.checkClosestZVertex = cms.bool(False)
process.pfPileUpPFlow.Vertices = 'goodOfflinePrimaryVertices'
process.pfJetsPFlow.doAreaFastjet = True
process.pfJetsPFlow.doRhoFastjet = False

# Should be fine in recent version of PAT, but in case of...
process.patJetCorrFactorsPFlow.rho = cms.InputTag("kt6PFJets", "rho")

###############################
###### Electron ID ############
###############################

# Use a 0.3 cone for electrons
# For PF2PAT...
process.pfIsolatedElectronsPFlow.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFIdPFlow"))
process.pfIsolatedElectronsPFlow.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFIdPFlow")
process.pfIsolatedElectronsPFlow.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFIdPFlow"), cms.InputTag("elPFIsoValueGamma03PFIdPFlow"))

process.pfElectronsPFlow.isolationValueMapsCharged  = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFIdPFlow"))
process.pfElectronsPFlow.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFIdPFlow" )
process.pfElectronsPFlow.isolationValueMapsNeutral  = cms.VInputTag(cms.InputTag( "elPFIsoValueNeutral03PFIdPFlow"), cms.InputTag("elPFIsoValueGamma03PFIdPFlow"))

# ... And for PAT
adaptPFIsoElectrons(process, process.patElectronsPFlow, postfix, "03")

process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi') 
process.eidMVASequence = cms.Sequence(process.mvaTrigV0 + process.mvaNonTrigV0)
#Electron ID
process.patElectronsPFlow.electronIDSources.mvaTrigV0    = cms.InputTag("mvaTrigV0")
process.patElectronsPFlow.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0") 
process.patDefaultSequencePFlow.replace(process.patElectronsPFlow, process.eidMVASequence * process.patElectronsPFlow)

# Produce electron conversions selection for Electron ID
process.patConversions = cms.EDProducer("PATConversionProducer",
    # input collection
    electronSource = cms.InputTag("selectedPatElectronsPFlow")
    # this should be your last selected electron collection name since currently index is used to match with electron later. We can fix this using reference pointer.
)

# Produce electron conversions selection for Electron ID
process.patConversionsLoose = cms.EDProducer("PATConversionProducer",
    # input collection
    electronSource = cms.InputTag("selectedPatElectronsLoosePFlow")
    # this should be your last selected electron collection name since currently index is used to match with electron later. We can fix this using reference pointer.
)

# This rho value is needed for computing effective area for 2011 MC corrections. This won't be needed anymore as soon as corrections are available for 2012 MC
from RecoJets.JetProducers.kt4PFJets_cfi import *
process.kt6PFJetsForIsolation = kt4PFJets.clone(rParam = 0.6, doRhoFastjet = True)
process.kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)

# Compute effective areas for correcting isolation
process.load("EGamma.EGammaAnalysisTools.electronEffectiveAreaProducer_cfi")

process.elEffectiveAreas03.src    = cms.InputTag("pfSelectedElectrons" + postfix)
process.elEffectiveAreas03.target = cms.string("EAFall11MC")

getattr(process, "pfElectronIsolationSequence" + postfix).replace(
    getattr(process, "elPFIsoValuePU04NoPFId" + postfix),
    getattr(process, "elPFIsoValuePU04NoPFId" + postfix) * process.elEffectiveAreas03
    )

# top projections in PF2PAT:
getattr(process,"pfNoPileUp"+postfix).enable = True 
getattr(process,"pfNoMuon"+postfix).enable = True 
getattr(process,"pfNoElectron"+postfix).enable = True 
getattr(process,"pfNoTau"+postfix).enable = False 
getattr(process,"pfNoJet"+postfix).enable = True 

#MET customization
#process.pfMETPFlow.src = cms.InputTag("pfNoPileUpPFlow")

# jet customization
process.selectedPatJetsPFlow.cut = 'pt > 10. & abs(eta) < 3.'

# muons customization
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiTopRefEventSel#Muons
process.patMuonsPFlow.usePV = False
process.patMuonsPFlow.embedTrack = True
process.pfIsolatedMuonsPFlow.isolationCut = .120
process.pfIsolatedMuonsPFlow.doDeltaBetaCorrection = True
process.pfSelectedMuonsPFlow.cut = 'pt > 10 & muonRef().isNonnull & muonRef().isGlobalMuon()'

# electrons customization
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiTopRefEventSel#Electrons
process.patElectronsPFlow.usePV = False
process.patElectronsPFlow.embedTrack = True
process.pfIsolatedElectronsPFlow.isolationCut = .1
process.pfIsolatedElectronsPFlow.doDeltaBetaCorrection = False
process.pfIsolatedElectronsPFlow.doEffectiveAreaCorrection = True
process.pfIsolatedElectronsPFlow.rho = cms.InputTag("kt6PFJetsForIsolation", "rho")
process.pfSelectedElectronsPFlow.cut = 'pt > 10'

# Clone selectedPatMuonsPFlow / selectedPatElectronsPFlow, and use in input pfMuonsPFlow / pfElectronsPFlow

process.patMuonsLoosePFlow = process.patMuonsPFlow.clone(
  pfMuonSource = cms.InputTag("pfMuonsPFlow"),
  embedGenMatch = False,
  addGenMatch = False
)
process.selectedPatMuonsLoosePFlow = process.selectedPatMuonsPFlow.clone(
  src = cms.InputTag("patMuonsLoosePFlow")
)
process.patDefaultSequencePFlow += (process.patMuonsLoosePFlow * process.selectedPatMuonsLoosePFlow)

process.patElectronsLoosePFlow = process.patElectronsPFlow.clone(
  pfElectronSource = cms.InputTag("pfElectronsPFlow"),
  embedGenMatch = False,
  addGenMatch = False
)
process.selectedPatElectronsLoosePFlow = process.selectedPatElectronsPFlow.clone(
  src = cms.InputTag("patElectronsLoosePFlow")
)
adaptPFIsoElectrons(process, process.patElectronsLoosePFlow, postfix, "03")
process.patDefaultSequencePFlow += (process.patElectronsLoosePFlow * process.selectedPatElectronsLoosePFlow)

removeSpecificPATObjects(process, names = ['Electrons', 'Muons', 'Taus', 'Jets', 'METs'])

process.photonPFIsolation = cms.EDProducer("PhotonIsolationProducer",
       src = cms.InputTag("selectedPatPhotons")
       )

process.patSeq = cms.Sequence(
    process.goodOfflinePrimaryVertices +
    process.kt6PFJetsForIsolation +
    getattr(process, "patPF2PATSequence" + postfix) +
    process.patConversions +
    process.patConversionsLoose +
    process.patDefaultSequence +
    process.photonPFIsolation
    )

if runOnMC == False:
  removeMCMatchingPF2PAT(process, '') 

removeSpecificPATObjects(process, names = ['Photons', 'Taus'], postfix = postfix)

# require physics declared
process.load('HLTrigger.special.hltPhysicsDeclared_cfi')
process.hltPhysicsDeclared.L1GtReadoutRecordTag = 'gtDigis'

# require scraping filter
process.scrapingVeto = cms.EDFilter("FilterOutScraping",
    applyfilter = cms.untracked.bool(True),
    debugOn = cms.untracked.bool(False),
    numtrack = cms.untracked.uint32(10),
    thresh = cms.untracked.double(0.25)
    )

# MET Filters
process.load('RecoMET.METFilters.metFilters_cff')

# load the PU JetID sequence
process.load("CMGTools.External.pujetidsequence_cff")
process.puJetId.jets =  cms.InputTag("selectedPatJetsPFlow")
process.puJetMva.jets =  cms.InputTag("selectedPatJetsPFlow")

process.filtersSeq = cms.Sequence(
   process.primaryVertexFilter *
   #process.scrapingVeto *
   process.metFilters
)

# Let it run
process.p = cms.Path(
    process.filtersSeq +
    process.patSeq *
    process.puJetIdSqeuence
    )

# Add PF2PAT output to the created file
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
process.out.outputCommands = cms.untracked.vstring('drop *',
    'keep GenEventInfoProduct_generator_*_*',
    'keep *_genParticles*_*_*',
    'keep edmTriggerResults_*_*_*',
    'keep *_*fflinePrimaryVertices_*_*', # It's NOT a typo
    'keep recoPFCandidates_particleFlow_*_*',
    'keep PileupSummaryInfos_*_*_*',
    'keep double_kt6PFJets*_rho_*',
    'keep *_patConversions*_*_*',
    *patEventContentNoCleaning ) 

process.out.outputCommands += [
  'drop *_selectedPatJetsForMET*_*_*',
  'drop *_selectedPatJets*_pfCandidates_*',
  'keep *_patPFMet*_*_PAT', # Keep raw met
  'keep *_allConversions*_*_*',

  # For isolations and conversions vetoes
  'keep *_gsfElectron*_*_*',
  'keep *_offlineBeamSpot*_*_*',

  # For pile-up jet ID
  'keep *_puJetId_*_*', # input variables
  'keep *_puJetMva_*_*', # final MVAs and working point flags

  #photon isolation
  'keep *_photonCore_*_*',
  'keep *_photonPFIsolation*_*_*'
  ]

## ------------------------------------------------------
## Geometry and Detector Conditions (needed for a few patTuple production steps)
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
# See https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions#Summary_of_Global_Tags_used_in_o
process.GlobalTag.globaltag = cms.string('START53_V21::All')

# RelVal in inputs
#from PhysicsTools.PatAlgos.tools.cmsswVersionTools import pickRelValInputFiles
#process.source.fileNames = pickRelValInputFiles(cmsswVersion = "CMSSW_5_3_6", globalTag = "PU_START53_V14", debug = True, numberOfFiles = 1)

process.source.fileNames = [
  #'file:input_mc.root'
  'file:/gridgroup/cms/brochet/MC_QCD_HT-250To500.root'
  #'/store/user/sbrochet/../../mc/Summer12_DR53X/TTWJets_8TeV-madgraph/AODSIM/PU_S10_START53_V7A-v1/0000/A4438E84-97DA-E111-BF02-002481E101DA.root'
  #'/store/mc/Summer12_DR53X/ZPrimeToTTJets_M1250GeV_W125GeV_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7A-v1/00000/7E5CC86C-7703-E211-9542-00215E221098.root'
  #'file:/scratch/brochet/MC/TTJets_SemiLeptMGDecays_8TeV-madgraph/00188A34-1224-E211-833B-003048D4612C.root'
  ]

process.out.fileName = cms.untracked.string('patTuple.root')

process.maxEvents.input = -1

process.options.wantSummary = False

process.MessageLogger.cerr.FwkReport.reportEvery = 100

print("Config loaded")
