def createPATProcess(runOnMC, globalTag):

    import FWCore.ParameterSet.Config as cms

    #####
    # Init the process with some default options
    #####

    process = cms.Process("PAT")

    ## MessageLogger
    process.load("FWCore.MessageLogger.MessageLogger_cfi")

    ## Options and Output Report
    process.options = cms.untracked.PSet(
            wantSummary = cms.untracked.bool(False),
            allowUnscheduled = cms.untracked.bool(True),
            compressionAlgorithm = cms.untracked.string("LZMA"),
            eventAutoFlushCompressedSize = cms.untracked.int32(15728640),
            compressionLevel = cms.untracked.int32(4)
            )

    ## Source
    process.source = cms.Source("PoolSource",
            fileNames = cms.untracked.vstring()
            )

    ## Maximal Number of Events
    process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

    ## Geometry and Detector Conditions (needed for a few patTuple production steps)
    process.load("Configuration.Geometry.GeometryIdeal_cff")
    process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
    process.GlobalTag.globaltag = cms.string("%s::All" % globalTag)
    process.load("Configuration.StandardSequences.MagneticField_cff")

    from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
    process.out = cms.OutputModule("PoolOutputModule",
            fileName = cms.untracked.string('patTuple.root'),
            SelectEvents = cms.untracked.PSet(
                SelectEvents = cms.vstring('Flag_METFilters')
                ),
            outputCommands = cms.untracked.vstring('drop *', *patEventContentNoCleaning)
            )

    process.outpath = cms.EndPath(process.out)

    print("Loading python config...")

    from PhysicsTools.PatAlgos.tools.pfTools import usePF2PAT, removeMCMatchingPF2PAT

    postfix = "PFlow"
    jetAlgo = "AK4"
    # Jet corrections when using CHS (L2L3Residual IS mandatory on data)
    if not runOnMC:
        jetCorrections = ('AK4PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual'], 'None')
    else:
        jetCorrections = ('AK4PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

    # FIXME: Enable Type I when ak4 corrections are in global tag

    # Add PF2PAT sequence to the process
    usePF2PAT(process,
            runPF2PAT = True,
            jetAlgo = jetAlgo,
            runOnMC = runOnMC,
            postfix = postfix,
            jetCorrections = jetCorrections
            )

    # FIXME: Temporary fix to have AK5 payloads until the AK4 payloads are ready
    getattr(process, "patJetCorrFactors%s" % postfix).payload = 'AK5PFchs'

    if not runOnMC:
        removeMCMatchingPF2PAT(process, ['All'])


    # FIXME: Add phi modulation corrections for MET

    setupElectrons(process, postfix)
    setupMuons(process, postfix)
    setupJets(process, postfix)

    # FIXME: Add collections without isolation cuts

    # MET filters
    process.load("PhysicsTools.PatAlgos.slimming.metFilterPaths_cff")
    process.trackingFailureFilter.JetSource = cms.InputTag("ak4PFJetsCHS")


    # FIXME: Review list of kept collections
    # FIXME: Are we sure we want to keep pf particles?

    # Add PF2PAT output to the created file
    process.out.outputCommands += [
            'keep edmTriggerResults_*_*_*',
            'keep *_*fflinePrimaryVertices_*_*', # It's NOT a typo
            'keep *_particleFlow_*_*',
            'keep PileupSummaryInfos_*_*_*',
            'keep double_fixedGridRho*_*_*',
            'drop *_selectedPatJetsForMET*_*_*',
            'drop *_selectedPatJets*_pfCandidates_*',
            'keep *_patPFMet*_*_PAT', # Keep raw met
            # For isolations and conversions vetoes
            'keep *_gedElectron*_*_*',
            'keep *_offlineBeamSpot*_*_*'
            ]

    process.MessageLogger.cerr.FwkReport.reportEvery = 100

    print("Config loaded")

    return process

def setupElectrons(process, postfix):
    """
    Setup electrons into process
    """
    from PhysicsTools.PatAlgos.tools.pfTools import adaptPFIsoElectrons

    # FIXME: Review electron isolation. For the moment, it's a basic isolation without effective areas. Still needed for 13 TeV?

    # Origin cut string
    # pt > 5 & gsfElectronRef.isAvailable() & gsfTrackRef.hitPattern().numberOfLostHits(\'MISSING_INNER_HITS\')<2 & gsfElectronRef.pfIsolationVariables().sumChargedHadronPt + gsfElectronRef.pfIsolationVariables().sumNeutralHadronEt + gsfElectronRef.pfIsolationVariables().sumPhotonEt  < 0.2 * pt 

    # FIXME: Check if gsfElectron isolation is computed with a cone size of 0.3
    # Switch to isolation of 0.1
    getattr(process, "pfIsolatedElectrons%s" % postfix).cut = "pt > 10 & gsfElectronRef.isAvailable() & gsfTrackRef.hitPattern().numberOfLostHits(\'MISSING_INNER_HITS\') < 2 & (gsfElectronRef.pfIsolationVariables().sumChargedHadronPt + gsfElectronRef.pfIsolationVariables().sumNeutralHadronEt + gsfElectronRef.pfIsolationVariables().sumPhotonEt) < 0.1 * pt"
    adaptPFIsoElectrons(process, getattr(process, "patElectrons%s" % postfix), postfix, "03")

    # FIXME: Add MVA isolation to electrons

def setupMuons(process, postfix):
    """
    Setup muons into process
    """

    # Origin cut string
    # pt > 5 & muonRef.isAvailable() & muonRef.pfIsolationR04().sumChargedHadronPt + muonRef.pfIsolationR04().sumNeutralHadronEt + muonRef.pfIsolationR04().sumPhotonEt  < 0.15 * pt 

    # FIXME: This isolation is not beta corrected
    getattr(process, "pfIsolatedMuons%s" % postfix).cut = "pt > 10 & muonRef.isAvailable() & muonRef.isGlobalMuon() & (muonRef.pfIsolationR04().sumChargedHadronPt + muonRef.pfIsolationR04().sumNeutralHadronEt + muonRef.pfIsolationR04().sumPhotonEt) < 0.12 * pt"

def setupJets(process, postfix):
    """
    Setup jets into process
    """

    # Setup PU jet Id and quark / gluon tagger
    from PatTopProduction.Tools.jetToolBox_cfi import jetToolBox
    jetToolBox(process, postfix)

    getattr(process, "selectedPatJets%s" % postfix).cut = "pt > 10."

