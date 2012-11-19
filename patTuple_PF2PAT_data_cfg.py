from PhysicsTools.PatAlgos.patTemplate_cfg import *

print("Loading python config...")

runOnMC = False

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
jetCorrections = ('AK5PFchs', ['L1FastJet','L2Relative','L3Absolute', 'L2L3Residual'] )
# Jet corrections when NOT using CHS
#jetCorrections = ('AK5PF', ['L1FastJet','L2Relative','L3Absolute', 'L2L3Residual'] )

# Type I MET enable
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=runOnMC , postfix=postfix, jetCorrections = jetCorrections, typeIMetCorrections=True,
  pvCollection = cms.InputTag('goodOfflinePrimaryVertices'))

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
process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runAplusBvsNvtx_data

# use for Spring'12 MC
#process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runAplusBvsNvtx_mc

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
process.pfIsolatedMuonsPFlow.doDeltaBetaCorrection = False
process.pfSelectedElectronsPFlow.cut = 'pt > 10'

# Clone selectedPatMuonsPFlow / selectedPatElectronsPFlow, and use in input pfMuonsPFlow / pfElectronsPFlow

process.patMuonsLoosePFlow = process.patMuonsPFlow.clone(
  pfMuonSource = cms.InputTag("pfMuonsPFlow")
)
process.selectedPatMuonsLoosePFlow = process.selectedPatMuonsPFlow.clone(
  src = cms.InputTag("patMuonsLoosePFlow")
)
process.patDefaultSequencePFlow += (process.patMuonsLoosePFlow * process.selectedPatMuonsLoosePFlow)

process.patElectronsLoosePFlow = process.patElectronsPFlow.clone(
  pfElectronSource = cms.InputTag("pfElectronsPFlow")
)
process.selectedPatElectronsLoosePFlow = process.selectedPatElectronsPFlow.clone(
  src = cms.InputTag("patElectronsLoosePFlow")
)
adaptPFIsoElectrons(process, process.patElectronsLoosePFlow, postfix, "03")
process.patDefaultSequencePFlow += (process.patElectronsLoosePFlow * process.selectedPatElectronsLoosePFlow)


process.patSeq = cms.Sequence(
    process.goodOfflinePrimaryVertices +
    getattr(process, "patPF2PATSequence" + postfix) +
    process.patConversions +
    process.patConversionsLoose
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

# HB + HE noise filtering
process.load('CommonTools/RecoAlgos/HBHENoiseFilter_cfi')

## The CSC beam halo tight filter
process.load('RecoMET.METAnalyzers.CSCHaloFilter_cfi')

## The HCAL laser filter _____________________________________________________||
process.load("RecoMET.METFilters.hcalLaserEventFilter_cfi")
process.hcalLaserEventFilter.vetoByRunEventNumber=cms.untracked.bool(False)
process.hcalLaserEventFilter.vetoByHBHEOccupancy=cms.untracked.bool(True)

## The ECAL dead cell trigger primitive filter _______________________________||
process.load('RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi')
## For AOD and RECO recommendation to use recovered rechits
process.EcalDeadCellTriggerPrimitiveFilter.tpDigiCollection = cms.InputTag("ecalTPSkimNA")

## The EE bad SuperCrystal filter ____________________________________________||
process.load('RecoMET.METFilters.eeBadScFilter_cfi')

## The Good vertices collection needed by the tracking failure filter ________||
process.goodVertices = cms.EDFilter(
  "VertexSelector",
  filter = cms.bool(False),
  src = cms.InputTag("offlinePrimaryVertices"),
  cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2")
)

## The tracking failure filter _______________________________________________||
process.load('RecoMET.METFilters.trackingFailureFilter_cfi')

process.filtersSeq = cms.Sequence(
   process.primaryVertexFilter *
   process.scrapingVeto *
   process.HBHENoiseFilter *
   process.CSCTightHaloFilter *
   process.hcalLaserEventFilter *
   process.EcalDeadCellTriggerPrimitiveFilter *
   process.goodVertices * process.trackingFailureFilter *
   process.eeBadScFilter
)

# Let it run
process.p = cms.Path(
    process.filtersSeq +
    process.patSeq
    )

# Add PF2PAT output to the created file
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
process.out.outputCommands = cms.untracked.vstring('drop *',
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
  'keep *_offlineBeamSpot*_*_*'
  ]

## ------------------------------------------------------
## Geometry and Detector Conditions (needed for a few patTuple production steps)
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('GR_R_53_V13::All')
process.source.fileNames = [ 
    #'file:input_data.root'
    #'/store/data/Run2012C/SingleMu/AOD/TOPMuPlusJets-24Aug2012-v1/00000/C8186FFC-2BEF-E111-80FB-001EC9D8D993.root'
    '/store/data/Run2012C/SingleElectron/AOD/TOPElePlusJets-24Aug2012-v1/00000/E0E40F2F-BDFB-E111-A073-0026189438FE.root'
    ]

process.out.fileName = cms.untracked.string('patTuple.root')

process.maxEvents.input = 200

process.options.wantSummary = True 

process.MessageLogger.cerr.FwkReport.reportEvery = 1

print("Config loaded")
