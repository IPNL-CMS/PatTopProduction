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
    process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
    process.load('Configuration.StandardSequences.MagneticField_38T_cff')
    process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
    process.GlobalTag.globaltag = cms.string("%s" % globalTag)

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
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

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

    getattr(process, "patJetCorrFactors%s" % postfix).payload = 'AK4PFchs'

    if not runOnMC:
        removeMCMatchingPF2PAT(process, postfix)


    # FIXME: Add phi modulation corrections for MET

    if runOnMC:
      setupGenParticles(process, postfix)
      setupForMC(process, postfix)

    setupMisc(process, postfix)
    setupElectrons(process, postfix)
    setupMuons(process, postfix)
    setupJets(process, postfix, runOnMC)
    setupMETs(process, postfix)
    setupTaus(process, postfix)
    setupPhotons(process, postfix)


    # Add PF2PAT output to the created file
    process.out.outputCommands += [

            # Reduced EGamma
            'keep recoPhotonCores_reducedEgamma_*_*',
            'keep recoGsfElectronCores_reducedEgamma_*_*',
            'keep recoConversions_reducedEgamma_*_*',
            'keep recoSuperClusters_reducedEgamma_*_*',
            'keep recoCaloClusters_reducedEgamma_*_*',
            'keep EcalRecHitsSorted_reducedEgamma_*_*',

            # Remove unneeded stuff
            'drop *_*_caloTowers_*',
            'drop *_*_pfCandidates_*',
            'drop *_*_genJets_*',

            # Drop PF particles, keep only the slimmed version
            'drop *_particleFlow_*_*',
            'drop *_selectedPatPFParticles*_*_*',
            'keep patPackedCandidates_packedPFCandidates*_*_*',

            # Trigger
            'keep *_selectedPatTrigger*_*_PAT',
            'keep patPackedTriggerPrescales_patTrigger__PAT',
            'keep edmTriggerResults_*_*_*',
            'keep *_offlineSlimmedPrimaryVertices_*_*',
            'keep *_goodOfflineSlimmedPrimaryVertices*_*_*',
            'keep PileupSummaryInfos_*_*_*',
            'keep double_fixedGridRho*_*_*',
            'keep *_offlineBeamSpot*_*_*'
            ]

    process.MessageLogger.cerr.FwkReport.reportEvery = 100

    print("Config loaded")

    return process

def setupMisc(process, postfix):
    """
    Setup various things into process
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    process.load('CommonTools.PileupAlgos.Puppi_cff')

    # Create packed PF candidates
    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.packedPFCandidates_cfi', postfix)
    applyPostfix(process, 'packedPFCandidates', postfix).inputCollectionFromPVLoose = cms.InputTag("pfNoPileUpJME%s" % postfix)
    applyPostfix(process, 'packedPFCandidates', postfix).inputCollectionFromPVTight = cms.InputTag("pfNoPileUp%s" % postfix)

    # Lost tracks
    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.lostTracks_cfi', postfix)
    applyPostfix(process, 'lostTracks', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)

    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedSecondaryVertices_cfi', postfix)
    applyPostfix(process, 'slimmedSecondaryVertices', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)
    applyPostfix(process, 'slimmedSecondaryVertices', postfix).lostTracksCandidates = cms.InputTag('lostTracks%s' % postfix)


    # Replace 'offlinePrimaryVertices' by the slimmed version of miniAOD
    process.load('PhysicsTools.PatAlgos.slimming.offlineSlimmedPrimaryVertices_cfi')
    process.load('PhysicsTools.PatAlgos.slimming.primaryVertexAssociation_cfi')

    process.goodPrimaryVertexAssociation = process.primaryVertexAssociation.clone(
            vertices = cms.InputTag('goodOfflinePrimaryVertices%s' % postfix),
            jets = cms.InputTag('pfNoTauClonesPFBRECO%s' % postfix)
            )
    process.primaryVertexAssociation.jets = cms.InputTag('pfNoTauClonesPFBRECO%s' % postfix)
    setattr(process, 'goodOfflineSlimmedPrimaryVertices%s' % postfix,
            process.offlineSlimmedPrimaryVertices.clone(
                score = cms.InputTag("goodPrimaryVertexAssociation", "original"),
                src = cms.InputTag('goodOfflinePrimaryVertices%s' % postfix)
                )
            )

    # Import reduce EGamma
    process.load('RecoEgamma.EgammaPhotonProducers.reducedEgamma_cfi')

    # Trigger
    from PhysicsTools.PatAlgos.tools.trigTools import switchOnTriggerStandAlone
    switchOnTriggerStandAlone(process, outputModule = '')
    process.patTrigger.packTriggerPathNames = cms.bool(True)
    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.selectedPatTrigger_cfi', postfix)

    # MET filters
    process.load("PhysicsTools.PatAlgos.slimming.metFilterPaths_cff")
    process.trackingFailureFilter.JetSource = cms.InputTag("ak4PFJetsCHS")

    process.out.outputCommands += [
            'keep *_slimmedSecondaryVertices*_*_*',
            'keep patPackedCandidates_lostTracks%s_*_PAT' % postfix
            ]


def setupElectrons(process, postfix):
    """
    Setup electrons into process
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    # FIXME: Review electron isolation. For the moment, it's a basic isolation without effective areas. Still needed for 13 TeV?

    # Origin cut string
    # pt > 5 & gsfElectronRef.isAvailable() & gsfTrackRef.hitPattern().numberOfLostHits(\'MISSING_INNER_HITS\')<2 & gsfElectronRef.pfIsolationVariables().sumChargedHadronPt + gsfElectronRef.pfIsolationVariables().sumNeutralHadronEt + gsfElectronRef.pfIsolationVariables().sumPhotonEt  < 0.2 * pt

    # FIXME: Check if gsfElectron isolation is computed with a cone size of 0.3
    # Switch to isolation of 0.1
    getattr(process, "pfIsolatedElectrons%s" % postfix).cut = "pt > 5 & gsfElectronRef.isAvailable() & gsfTrackRef.hitPattern().numberOfLostHits(\'MISSING_INNER_HITS\') < 2 & (gsfElectronRef.pfIsolationVariables().sumChargedHadronPt + gsfElectronRef.pfIsolationVariables().sumNeutralHadronEt + gsfElectronRef.pfIsolationVariables().sumPhotonEt) < 0.1 * pt"

    # FIXME: Add MVA isolation to electrons

    # Disable embedding of electron and photon associated objects already stored by the ReducedEGProducer
    applyPostfix(process, 'patElectrons', postfix).embedGsfElectronCore = False  ## process.patElectrons.embed in AOD externally stored gsf electron core
    applyPostfix(process, 'patElectrons', postfix).embedSuperCluster    = False  ## process.patElectrons.embed in AOD externally stored supercluster
    applyPostfix(process, 'patElectrons', postfix).embedPflowSuperCluster         = False  ## process.patElectrons.embed in AOD externally stored supercluster
    applyPostfix(process, 'patElectrons', postfix).embedSeedCluster               = False  ## process.patElectrons.embed in AOD externally stored the electron's seedcluster
    applyPostfix(process, 'patElectrons', postfix).embedBasicClusters             = False  ## process.patElectrons.embed in AOD externally stored the electron's basic clusters
    applyPostfix(process, 'patElectrons', postfix).embedPreshowerClusters         = False  ## process.patElectrons.embed in AOD externally stored the electron's preshower clusters
    applyPostfix(process, 'patElectrons', postfix).embedPflowBasicClusters        = False  ## process.patElectrons.embed in AOD externally stored the electron's pflow basic clusters
    applyPostfix(process, 'patElectrons', postfix).embedPflowPreshowerClusters    = False  ## process.patElectrons.embed in AOD externally stored the electron's pflow preshower clusters
    applyPostfix(process, 'patElectrons', postfix).embedRecHits         = False  ## process.patElectrons.embed in AOD externally stored the RecHits - can be called from the PATElectronProducer
    applyPostfix(process, 'patElectrons', postfix).addPFClusterIso = cms.bool(True)
    applyPostfix(process, 'patElectrons', postfix).ecalPFClusterIsoMap = cms.InputTag("reducedEgamma", "eleEcalPFClusIso")
    applyPostfix(process, 'patElectrons', postfix).hcalPFClusterIsoMap = cms.InputTag("reducedEgamma", "eleHcalPFClusIso")
    applyPostfix(process, 'patElectrons', postfix).electronSource = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")
    applyPostfix(process, 'patElectrons', postfix).electronIDSources = cms.PSet(
            # configure many IDs as InputTag <someName> = <someTag> you
            # can comment out those you don't want to save some disk space
            eidRobustLoose      = cms.InputTag("reducedEgamma", "eidRobustLoose"),
            eidRobustTight      = cms.InputTag("reducedEgamma", "eidRobustTight"),
            eidLoose            = cms.InputTag("reducedEgamma", "eidLoose"),
            eidTight            = cms.InputTag("reducedEgamma", "eidTight"),
            eidRobustHighEnergy = cms.InputTag("reducedEgamma", "eidRobustHighEnergy"),
        )


    applyPostfix(process, 'elPFIsoDepositChargedPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")
    applyPostfix(process, 'elPFIsoDepositChargedAllPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")
    applyPostfix(process, 'elPFIsoDepositNeutralPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")
    applyPostfix(process, 'elPFIsoDepositGammaPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")
    applyPostfix(process, 'elPFIsoDepositPUPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")

    #VID Electron IDs
    from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDElectronIdProducer, setupAllVIDIdsInModule, setupVIDElectronSelection, DataFormat
    electron_ids = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_PHYS14_PU20bx25_V2_cff',
            'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV51_cff']

    switchOnVIDElectronIdProducer(process, DataFormat.AOD)
    process.egmGsfElectronIDs.physicsObjectSrc = cms.InputTag("reducedEgamma","reducedGedGsfElectrons")
    process.electronIDValueMapProducer.src = cms.InputTag("reducedEgamma","reducedGedGsfElectrons")
    process.electronIDValueMapProducer.ebReducedRecHitCollection = cms.InputTag("reducedEgamma","reducedEBRecHits")
    process.electronIDValueMapProducer.eeReducedRecHitCollection = cms.InputTag("reducedEgamma","reducedEERecHits")
    process.electronIDValueMapProducer.esReducedRecHitCollection = cms.InputTag("reducedEgamma","reducedESRecHits")
    for idmod in electron_ids:
        setupAllVIDIdsInModule(process, idmod, setupVIDElectronSelection, patProducer=getattr(process, 'patElectrons%s' % postfix))

    # Add new electron collection without isolation cut; use already existing 'pfElectrons' collection, which has the following cuts:
    #  pt > 5 & gsfElectronRef.isAvailable() & gsfTrackRef.hitPattern().numberOfLostHits(\'MISSING_INNER_HITS\')<2
    getattr(process, 'pfElectronsPFBRECO%s' % postfix).cut = " pt > 5 & gsfElectronRef.isAvailable() & gsfTrackRef.hitPattern().numberOfLostHits(\'MISSING_INNER_HITS\')<2"

    setattr(process, 'patAllElectrons%s' % postfix,
            getattr(process, 'patElectrons%s' % postfix).clone(
                pfElectronSource = cms.InputTag('pfElectronsPFBRECO%s' % postfix)
                )
            )

    setattr(process, 'selectedPatAllElectrons%s' % postfix,
            getattr(process, 'selectedPatElectrons%s' % postfix).clone(
                src = cms.InputTag('patAllElectrons%s' % postfix)
                )
            )

    # Slim electrons
    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedElectrons_cfi', postfix)
    applyPostfix(process, 'slimmedElectrons', postfix).src = cms.InputTag('selectedPatElectrons%s' % postfix)
    applyPostfix(process, 'slimmedElectrons', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)

    setattr(process, 'slimmedAllElectrons%s' % postfix,
            applyPostfix(process, 'slimmedElectrons', postfix).clone(
                src = cms.InputTag('selectedPatAllElectrons%s' % postfix)
                )
            )

    process.out.outputCommands += [
            'drop *_selectedPatElectrons%s_*_*' % postfix,
            'drop *_selectedPatAllElectrons%s_*_*' % postfix,
            'keep *_slimmedElectrons%s_*_*' % postfix,
            'keep *_slimmedAllElectrons%s_*_*' % postfix
            ]

def setupMuons(process, postfix):
    """
    Setup muons into process
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    # Origin cut string
    # pt > 5 & muonRef.isAvailable() & muonRef.pfIsolationR04().sumChargedHadronPt + muonRef.pfIsolationR04().sumNeutralHadronEt + muonRef.pfIsolationR04().sumPhotonEt  < 0.15 * pt

    # FIXME: This isolation is not beta corrected
    getattr(process, "pfIsolatedMuons%s" % postfix).cut = "pt > 5 & muonRef.isAvailable() & muonRef.isGlobalMuon() & (muonRef.pfIsolationR04().sumChargedHadronPt + muonRef.pfIsolationR04().sumNeutralHadronEt + muonRef.pfIsolationR04().sumPhotonEt) < 0.12 * pt"

    # Reduce output size using miniAOD format, see https://github.com/cms-sw/cmssw/blob/CMSSW_7_2_X/PhysicsTools/PatAlgos/python/slimming/miniAOD_tools.py
    applyPostfix(process, 'patMuons', postfix).embedTrack         = True  # used for IDs
    applyPostfix(process, 'patMuons', postfix).embedCombinedMuon  = True  # used for IDs
    applyPostfix(process, 'patMuons', postfix).embedMuonBestTrack = True  # used for IDs
    applyPostfix(process, 'patMuons', postfix).embedStandAloneMuon = True # maybe?
    applyPostfix(process, 'patMuons', postfix).embedPickyMuon = False   # no, use best track
    applyPostfix(process, 'patMuons', postfix).embedTpfmsMuon = False   # no, use best track
    applyPostfix(process, 'patMuons', postfix).embedDytMuon   = False   # no, use best track
    applyPostfix(process, 'selectedPatMuons', postfix).cut = cms.string("pt > 5 || isPFMuon || (pt > 3 && (isGlobalMuon || isStandAloneMuon || numberOfMatches > 0 || muonID('RPCMuLoose')))")

    # Add new muon collection without isolation cut; use already existing 'pfMuons' collection, which has the following cuts:
    # pt > 5 & muonRef.isAvailable()
    getattr(process, 'pfMuonsPFBRECO%s' % postfix).cut = "pt > 5 & muonRef.isAvailable()"

    # Clone 'muonMatch' collection to operate on 'pfMuons'
    setattr(process, 'allMuonMatch%s' % postfix,
            getattr(process, 'muonMatch%s' % postfix).clone(
                src = cms.InputTag('pfMuonsPFBRECO%s' % postfix)
                )
            )

    setattr(process, 'patAllMuons%s' % postfix,
            getattr(process, 'patMuons%s' % postfix).clone(
                genParticleMatch = cms.InputTag('allMuonMatch%s' % postfix),
                pfMuonSource = cms.InputTag('pfMuonsPFBRECO%s' % postfix)
                )
            )

    setattr(process, 'selectedPatAllMuons%s' % postfix,
            getattr(process, 'selectedPatMuons%s' % postfix).clone(
                src = cms.InputTag('patAllMuons%s' % postfix)
                )
            )

    # Slim muons
    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedMuons_cfi', postfix)
    applyPostfix(process, 'slimmedMuons', postfix).src = cms.InputTag('selectedPatMuons%s' % postfix)
    applyPostfix(process, 'slimmedMuons', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)

    setattr(process, 'slimmedAllMuons%s' % postfix,
            applyPostfix(process, 'slimmedMuons', postfix).clone(
                src = cms.InputTag('selectedPatAllMuons%s' % postfix)
                )
            )

    process.out.outputCommands += [
            'drop *_selectedPatMuons%s_*_*' % postfix,
            'drop *_selectedPatAllMuons%s_*_*' % postfix,
            'keep *_slimmedMuons%s_*_*' % postfix,
            'keep *_slimmedAllMuons%s_*_*' % postfix
            ]

def setupJets(process, postfix, runOnMC):
    """
    Setup jets into process
    """

    # Setup PU jet Id and quark / gluon tagger
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    from PatTopProduction.Tools.jetToolBox_cfi import jetToolBox
    jetToolBox(process, postfix)

    getattr(process, "selectedPatJets%s" % postfix).cut = "pt > 10."

    process.load("RecoVertex.AdaptiveVertexFinder.inclusiveVertexing_cff")
    applyPostfix(process, 'patJets', postfix).tagInfoSources = cms.VInputTag(cms.InputTag("secondaryVertexTagInfosEI"))
    applyPostfix(process, 'patJets', postfix).addTagInfos = cms.bool(True)

    # Puppi jets
    process.load('RecoJets.JetProducers.ak4PFJetsPuppi_cfi')
    process.ak4PFJetsPuppi.doAreaFastjet = True

    from RecoJets.JetAssociationProducers.j2tParametersVX_cfi import j2tParametersVX
    process.ak4PFJetsPuppiTracksAssociatorAtVertex = cms.EDProducer("JetTracksAssociatorAtVertex",
        j2tParametersVX,
        jets = cms.InputTag("ak4PFJetsPuppi")
    )
    process.patJetPuppiCharge = cms.EDProducer("JetChargeProducer",
        src = cms.InputTag("ak4PFJetsPuppiTracksAssociatorAtVertex"),
        var = cms.string('Pt'),
        exp = cms.double(1.0)
    )

    # FIXME: Use PUPPI corrections when available
    if not runOnMC:
        jetCorrections = ('AK4PFchs', ['L2Relative', 'L3Absolute', 'L2L3Residual'], 'None')
    else:
        jetCorrections = ('AK4PFchs', ['L2Relative', 'L3Absolute'], 'None')

    from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
    addJetCollection(process, postfix="", labelName='Puppi', jetSource=cms.InputTag('ak4PFJetsPuppi'),
            jetCorrections=jetCorrections, algo= 'AK', rParam = 0.4,
            btagDiscriminators = map(lambda x: x.value(), getattr(process, 'patJets%s' % postfix).discriminatorSources)
            )
    
    process.patJetGenJetMatchPuppi.matched = 'slimmedGenJets' + postfix
    
    process.patJetsPuppi.userData.userFloats.src = cms.VInputTag(cms.InputTag(""))
    process.patJetsPuppi.jetChargeSource = cms.InputTag("patJetPuppiCharge")

    process.selectedPatJetsPuppi.cut = cms.string("pt > 10")

    if not runOnMC:
        jetCorrections = ('AK8PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual'], 'None')
    else:
        jetCorrections = ('AK8PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

    addJetCollection(process,
            labelName = 'AK8',
            jetSource = cms.InputTag('ak8PFJetsCHS'),
            algo= 'AK',
            rParam = 0.8,
            jetCorrections = jetCorrections,
            postfix = postfix)

    applyPostfix(process, 'patJetsAK8', postfix).userData.userFloats.src = [] # start with empty list of user floats
    applyPostfix(process, 'selectedPatJetsAK8', postfix).cut = cms.string("pt > 100")
    if runOnMC:
        applyPostfix(process, 'patJetGenJetMatchAK8', postfix).matched = 'slimmedGenJets%s' % postfix
        applyPostfix(process, 'slimmedGenJets', postfix).packedGenParticles = 'packedGenParticles%s' % postfix
        applyPostfix(process, 'slimmedGenJetsAK8', postfix).packedGenParticles = 'packedGenParticles%s' % postfix

    # Groom mass
    from RecoJets.Configuration.RecoPFJets_cff import ak8PFJetsCHSPruned, ak8PFJetsCHSSoftDrop, ak8PFJetsCHSFiltered, ak8PFJetsCHSTrimmed
    process.ak8PFJetsCHSPruned   = ak8PFJetsCHSPruned.clone(src = cms.InputTag('pfNoPileUpJME%s' % postfix))
    process.ak8PFJetsCHSSoftDrop = ak8PFJetsCHSSoftDrop.clone(src = cms.InputTag('pfNoPileUpJME%s' % postfix))
    process.ak8PFJetsCHSTrimmed  = ak8PFJetsCHSTrimmed.clone(src = cms.InputTag('pfNoPileUpJME%s' % postfix))
    process.ak8PFJetsCHSFiltered = ak8PFJetsCHSFiltered.clone(src = cms.InputTag('pfNoPileUpJME%s' % postfix))

    process.load("RecoJets.JetProducers.ak8PFJetsCHS_groomingValueMaps_cfi")
    applyPostfix(process, 'patJetsAK8', postfix).userData.userFloats.src += ['ak8PFJetsCHSPrunedMass', 'ak8PFJetsCHSSoftDropMass', 'ak8PFJetsCHSTrimmedMass', 'ak8PFJetsCHSFilteredMass']

    # CMS Top tagger
    process.cmsTopTagPFJetsCHSMassAK8 = process.ak8PFJetsCHSPrunedMass.clone()
    process.cmsTopTagPFJetsCHSMassAK8.src = cms.InputTag("ak8PFJetsCHS")
    process.cmsTopTagPFJetsCHSMassAK8.matched = cms.InputTag("cmsTopTagPFJetsCHS")
    applyPostfix(process, 'patJetsAK8', postfix).userData.userFloats.src += ['cmsTopTagPFJetsCHSMassAK8']

    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedJets_cfi', postfix)
    applyPostfix(process, 'slimmedJets', postfix).src = cms.InputTag('selectedPatJets%s' % postfix)
    applyPostfix(process, 'slimmedJets', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)

    process.slimmedJetsPuppi = getattr(process, 'slimmedJets%s' % postfix).clone()
    process.slimmedJetsPuppi.src = cms.InputTag("selectedPatJetsPuppi") 
    process.slimmedJetsPuppi.packedPFCandidates = cms.InputTag("packedPFCandidates%s" % postfix)

    applyPostfix(process, 'slimmedJetsAK8', postfix).src = cms.InputTag('selectedPatJetsAK8%s' % postfix)
    applyPostfix(process, 'slimmedJetsAK8', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)

    process.out.outputCommands += [
            'drop *_selectedPatJets%s_*_*' % postfix,
            'drop *_selectedPatJetsAK8%s_*_*' % postfix,
            'drop *_selectedPatJetsPuppi_*_*',
            'keep *_slimmedJets%s_*_*' % postfix,
            'keep *_slimmedJetsPuppi_*_*',
            'keep *_slimmedJetsAK8%s_*_*' % postfix
            ]


def setupMETs(process, postfix):
    # PUPPI MET
    import FWCore.ParameterSet.Config as cms

    process.load('JetMETCorrections.Configuration.JetCorrectors_cff')

    process.pfMetPuppi = getattr(process, 'pfMETPFBRECO%s' % postfix).clone()
    process.pfMetPuppi.src = cms.InputTag("puppi")
    process.pfMetPuppi.alias = cms.string('pfMetPuppi')

    ## Type 1 corrections
    from JetMETCorrections.Type1MET.correctionTermsPfMetType1Type2_cff import corrPfMetType1
    from JetMETCorrections.Type1MET.correctedMet_cff import pfMetT1
    process.corrPfMetType1Puppi = corrPfMetType1.clone(
        src = 'ak4PFJetsPuppi',
        jetCorrLabel = 'ak4PFCHSL2L3Corrector',
    )
    del process.corrPfMetType1Puppi.offsetCorrLabel # no L1 for PUPPI jets
    process.pfMetT1Puppi = pfMetT1.clone(
        src = 'pfMetPuppi',
        srcCorrections = [ cms.InputTag("corrPfMetType1Puppi", "type1") ]
    )

    from PhysicsTools.PatAlgos.tools.metTools import addMETCollection
    addMETCollection(process, labelName='patMETsPuppi',   metSource='pfMetT1Puppi') # Puppi T1
    addMETCollection(process, labelName='patPFMetPuppi', metSource='pfMetPuppi')   # Puppi RAW
    addMETCollection(process, labelName='patPFMet%s' % postfix, metSource='pfMETPFBRECO%s' % postfix)   # Puppi RAW
    process.patMETsPuppi.addGenMET = cms.bool(False)
    process.patPFMetPuppi.addGenMET = cms.bool(False)
    getattr(process, 'patMETs%s' %postfix).addGenMET = False

    process.load('PhysicsTools.PatAlgos.slimming.slimmedMETs_cfi')
    process.slimmedMETs.src = cms.InputTag("patMETs%s" % postfix)
    process.slimmedMETs.rawUncertainties = cms.InputTag("patPFMet%s" % postfix)
    del process.slimmedMETs.caloMET # not available
    del process.slimmedMETs.type1Uncertainties # not available
    del process.slimmedMETs.type1p2Uncertainties # not available
    getattr(process, 'patPFMet%s' %postfix).addGenMET = False

    process.slimmedMETsPuppi = process.slimmedMETs.clone()
    process.slimmedMETsPuppi.src = cms.InputTag("patMETsPuppi")
    process.slimmedMETsPuppi.rawUncertainties   = cms.InputTag("patPFMetPuppi") # only central value

    process.out.outputCommands += [
            'keep *_slimmedMETs*_*_*',
            ]

def setupTaus(process, postfix):
    """
    Setup taus into process
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    applyPostfix(process, 'patTaus', postfix).isoDeposits = cms.PSet()
    applyPostfix(process, 'selectedPatTaus', postfix).cut = cms.string("pt > 18. && tauID('decayModeFinding')> 0.5")

    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedTaus_cfi', postfix)
    applyPostfix(process, 'slimmedTaus', postfix).src = cms.InputTag('selectedPatTaus%s' % postfix)
    applyPostfix(process, 'slimmedTaus', postfix).packedPFCandidates = cms.InputTag('packedPFCandidates%s' % postfix)

    process.out.outputCommands += [
            'drop *_selectedPatTaus*_*_*',
            'keep *_slimmedTaus*_*_*'
            ]

def setupPhotons(process, postfix):
    """
    Setup photons into process
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    applyPostfix(process, 'patPhotons', postfix).embedSuperCluster = False ## whether to process.patPhotons.embed in AOD externally stored supercluster
    applyPostfix(process, 'patPhotons', postfix).embedSeedCluster = False  ## process.patPhotons.embed in AOD externally stored the photon's seedcluster
    applyPostfix(process, 'patPhotons', postfix).embedBasicClusters = False  ## process.patPhotons.embed in AOD externally stored the photon's basic clusters
    applyPostfix(process, 'patPhotons', postfix).embedPreshowerClusters = False  ## process.patPhotons.embed in AOD externally stored the photon's preshower clusters
    applyPostfix(process, 'patPhotons', postfix).embedRecHits = False  ## process.patPhotons.embed in AOD externally stored the RecHits - can be called from the PATPhotonProducer
    applyPostfix(process, 'patPhotons', postfix).addPFClusterIso = cms.bool(True)
    applyPostfix(process, 'patPhotons', postfix).ecalPFClusterIsoMap = cms.InputTag("reducedEgamma", "phoEcalPFClusIso")
    applyPostfix(process, 'patPhotons', postfix).hcalPFClusterIsoMap = cms.InputTag("reducedEgamma", "phoHcalPFClusIso")
    applyPostfix(process, 'patPhotons', postfix).photonSource = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    applyPostfix(process, 'patPhotons', postfix).photonIDSources = cms.PSet(
            PhotonCutBasedIDLoose = cms.InputTag('reducedEgamma', 'PhotonCutBasedIDLoose'),
            PhotonCutBasedIDTight = cms.InputTag('reducedEgamma', 'PhotonCutBasedIDTight')
            )

    applyPostfix(process, 'phPFIsoDepositChargedPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    applyPostfix(process, 'phPFIsoDepositChargedAllPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    applyPostfix(process, 'phPFIsoDepositNeutralPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    applyPostfix(process, 'phPFIsoDepositGammaPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    applyPostfix(process, 'phPFIsoDepositPUPAT', postfix).src = cms.InputTag("reducedEgamma", "reducedGedPhotons")

    # VID Photon IDs - crash for unknown reasons
    #from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDPhotonIdProducer, setupAllVIDIdsInModule, setupVIDPhotonSelection, DataFormat
    #photon_ids = ['RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_PHYS14_PU20bx25_V2_cff']

    #switchOnVIDPhotonIdProducer(process, DataFormat.AOD)
    #process.egmPhotonIDs.physicsObjectSrc = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    #process.photonIDValueMapProducer.src = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    #process.photonIDValueMapProducer.pfCandidates = cms.InputTag("packedPFCandidates%s" % postfix)
    #process.photonIDValueMapProducer.particleBasedIsolation = cms.InputTag("reducedEgamma", "reducedPhotonPfCandMap")
    #process.photonIDValueMapProducer.ebReducedRecHitCollection = cms.InputTag("reducedEgamma", "reducedEBRecHits")
    #process.photonIDValueMapProducer.eeReducedRecHitCollection = cms.InputTag("reducedEgamma", "reducedEERecHits")
    #process.photonIDValueMapProducer.esReducedRecHitCollection = cms.InputTag("reducedEgamma", "reducedESRecHits")
    #for idmod in photon_ids:
        #setupAllVIDIdsInModule(process, idmod, setupVIDPhotonSelection, patProducer=getattr(process, 'patPhotons%s' % postfix))

    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedPhotons_cfi', postfix)
    applyPostfix(process, 'slimmedPhotons', postfix).src = cms.InputTag("selectedPatPhotons%s" % postfix)
    applyPostfix(process, 'slimmedPhotons', postfix).packedPFCandidates = cms.InputTag("packedPFCandidates%s" % postfix)

    process.out.outputCommands += [
            'drop *_selectedPatPhotons*_*_*',
            'keep *_slimmedPhotons*_*_*'
            ]

def setupGenParticles(process, postfix):
    """
    Setup gen particles into process
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.genParticles_cff', postfix)

def setupForMC(process, postfix):
    """
    Setup various things if running on MC
    """
    import FWCore.ParameterSet.Config as cms
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix

    loadWithPostfix(process, 'PhysicsTools.PatAlgos.slimming.slimmedGenJets_cfi', postfix)
    applyPostfix(process, 'slimmedGenJets', postfix).src = cms.InputTag('ak4GenJetsNoNu%s' % postfix)

    applyPostfix(process, 'muonMatch', postfix).matched = "prunedGenParticles%s" % postfix
    applyPostfix(process, 'electronMatch', postfix).matched = "prunedGenParticles%s" % postfix
    applyPostfix(process, 'electronMatch', postfix).src = cms.InputTag("reducedEgamma", "reducedGedGsfElectrons")
    applyPostfix(process, 'photonMatch', postfix).matched = "prunedGenParticles%s" % postfix
    applyPostfix(process, 'photonMatch', postfix).src = cms.InputTag("reducedEgamma", "reducedGedPhotons")
    applyPostfix(process, 'tauMatch', postfix).matched = "prunedGenParticles%s" % postfix
    applyPostfix(process, 'patJetPartonMatch', postfix).matched = "prunedGenParticles%s" % postfix
    applyPostfix(process, 'patJetPartonMatch', postfix).mcStatus = [3, 23]
    applyPostfix(process, 'patJetGenJetMatch', postfix).matched = "slimmedGenJets%s" % postfix
    applyPostfix(process, 'patMuons', postfix).embedGenMatch = False
    applyPostfix(process, 'patElectrons', postfix).embedGenMatch = False
    applyPostfix(process, 'patPhotons', postfix).embedGenMatch = False
    applyPostfix(process, 'patTaus', postfix).embedGenMatch = False
    applyPostfix(process, 'patJets', postfix).embedGenPartonMatch = False
    #also jet flavour must be switched to ak4
    applyPostfix(process, 'patJetFlavourAssociation', postfix).rParam = 0.4
    process.patMETsPuppi.addGenMET = cms.bool(True)
    process.patPFMetPuppi.addGenMET = cms.bool(True)
    getattr(process, 'patMETs%s' %postfix).addGenMET = True
    getattr(process, 'patPFMet%s' %postfix).addGenMET = True

    process.out.outputCommands += [
            'keep *_slimmedGenJets*_*_*',
            'keep *_packedGenParticles*_*_*',
            'keep recoGenParticles_prunedGenParticles*_*_*',
            'drop recoGenParticles_prunedGenParticlesWithStatusOne*_*_*'
            ]
