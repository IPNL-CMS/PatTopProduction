def createProcess(isMC, globalTag):

    import FWCore.ParameterSet.Config as cms

    #####
    # Init the process with some default options
    #####

    process = cms.Process("PAT")

    ## MessageLogger
    process.load("FWCore.MessageLogger.MessageLogger_cfi")

    ## Options and Output Report
    process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True),
            allowUnscheduled = cms.untracked.bool(True) )

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

    ## Output Module Configuration (expects a path 'p')
    from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
    process.out = cms.OutputModule("PoolOutputModule",
            fileName = cms.untracked.string('patTuple.root'),
            ## save only events passing the full path
            #SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
            ## save PAT output; you need a '*' to unpack the list of commands
            ## 'patEventContent'
            outputCommands = cms.untracked.vstring('drop *', *patEventContentNoCleaning )
            )

    process.outpath = cms.EndPath(process.out)

    #####
    # Customize process for top pat Tuples production
    #####

    print("Loading python config...")

    #process.load("PhysicsTools.PatAlgos.patSequences_cff")

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

    from PhysicsTools.PatAlgos.tools.pfTools import usePF2PAT, adaptPFIsoElectrons

    postfix = "PFlow"
    jetAlgo = "AK5"
    # Jet corrections when using CHS (L2L3Residual IS mandatory on data)

    if isMC:
        jetCorrections = ('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'] )
    else:
        jetCorrections = ('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual'] )

    # Jet corrections when NOT using CHS
    #jetCorrections = ('AK5PF', ['L1FastJet','L2Relative','L3Absolute'] )

    # Type I MET enabled
    usePF2PAT(process, runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=isMC , postfix=postfix, jetCorrections = jetCorrections, typeIMetCorrections=True, pvCollection = cms.InputTag('goodOfflinePrimaryVertices'))

    # We want:
    # - Uncorrected MEt: patMETsRawPFlow
    # - Type I corrected MEt: patMETsPFlow
    # - Type 0+I correct MEt: patMETsType0p1PFlow

    # Create PAT MEt from raw MEt collection (pfMET<postfix>))
    setattr(process, "patMETsRaw%s" % postfix, getattr(process, "patMETs%s" % postfix).clone( metSource = cms.InputTag("pfMET%s" % (postfix)) ))

    # Type 0, 1 or 2 corrected MEt is produced by the module CorrectedPFMETProducer

    # Clone the module <jetcorrectorlabel>Type1CorMet<postfix> (eg, AK5PFchschsTypeICorMetPFlow),
    # to create a Type 0 + I MEt

    setattr(process, "%sType0p1CorMet%s" % (jetCorrections[0], postfix), getattr(process, "%sType1CorMet%s" % (jetCorrections[0], postfix)).clone( applyType0Corrections = cms.bool(True), srcCHSSums = cms.VInputTag("pfchsMETcorr%s:type0" % postfix) ))

    # Now, convert the PF met to patMET. Clone patMETs<postfix>

    setattr(process, "patMETsType0p1%s" % postfix, getattr(process, "patMETs%s" % postfix).clone( metSource = cms.InputTag("%sType0p1CorMet%s" % (jetCorrections[0], postfix)) ))

    #####
    # Add sys shift correction to our Met
    #####

    # Output:
    # - Type I + sys shift: patMETsSysShiftPFlow
    # - Type 0 + I + sys shift: patMETsType0p1pSysShiftPFlow

    #process.load("JetMETCorrections.Type1MET.pfMETCorrections_cff")
    process.load("JetMETCorrections.Type1MET.pfMETsysShiftCorrections_cfi")

    if not isMC:
        process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_data
    else:
        process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_mc

    # Clone the Type I MEt producer and add Sys Shift corrections
    setattr(process, "%sType1pSysShiftCorMet%s" % (jetCorrections[0], postfix), getattr(process, "%sType1CorMet%s" % (jetCorrections[0], postfix)).clone())
    getattr(process, "%sType1pSysShiftCorMet%s" % (jetCorrections[0], postfix)).srcType1Corrections.append(
            cms.InputTag('pfMEtSysShiftCorr')
            )

    # Clone the Type 0+I MEt producer and add Sys Shift corrections
    setattr(process, "%sType0p1pSysShiftCorMet%s" % (jetCorrections[0], postfix), getattr(process, "%sType0p1CorMet%s" % (jetCorrections[0], postfix)).clone())
    getattr(process, "%sType0p1pSysShiftCorMet%s" % (jetCorrections[0], postfix)).srcType1Corrections.append(
            cms.InputTag('pfMEtSysShiftCorr')
            )

    # Convert PF MEt to PAT MEt
    setattr(process, "patMETsSysShift%s" % postfix, getattr(process, "patMETs%s" % postfix).clone( metSource = cms.InputTag("%sType1pSysShiftCorMet%s" % (jetCorrections[0], postfix)) ))

    setattr(process, "patMETsType0p1pShiftCorr%s" % postfix, getattr(process, "patMETs%s" % postfix).clone( metSource = cms.InputTag("%sType0p1pSysShiftCorMet%s" % (jetCorrections[0], postfix)) ))

    getattr(process, "pfJets%s" % postfix).doAreaFastjet = True
    getattr(process, "pfJets%s" % postfix).doRhoFastjet = False

    # Should be fine in recent version of PAT, but in case of...
    #process.patJetCorrFactorsPFlow.rho = cms.InputTag("kt6PFJets", "rho")

    #####
    # Configure muon & electron isolation cuts
    #####

    # Electrons need a deltaR = 0.3 cone for isolation values.

    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix

    loadWithPostfix(process, "CommonTools.ParticleFlow.Isolation.pfElectronIsolation_cff", postfix)

    # Fix input tags
    deposit = getattr(process, "elPFIsoDepositCharged%s" % postfix)
    deposit.src = cms.InputTag("pfSelectedElectrons%s" % postfix)
    deposit.ExtractorPSet.inputCandView = cms.InputTag("pfAllChargedHadrons%s" % postfix)

    deposit = getattr(process, "elPFIsoDepositChargedAll%s" % postfix)
    deposit.src = cms.InputTag("pfSelectedElectrons%s" % postfix)
    deposit.ExtractorPSet.inputCandView = cms.InputTag("pfAllChargedParticles%s" % postfix)

    deposit = getattr(process, "elPFIsoDepositGamma%s" % postfix)
    deposit.src = cms.InputTag("pfSelectedElectrons%s" % postfix)
    deposit.ExtractorPSet.inputCandView = cms.InputTag("pfAllPhotons%s" % postfix)

    deposit = getattr(process, "elPFIsoDepositNeutral%s" % postfix)
    deposit.src = cms.InputTag("pfSelectedElectrons%s" % postfix)
    deposit.ExtractorPSet.inputCandView = cms.InputTag("pfAllNeutralHadrons%s" % postfix)

    deposit = getattr(process, "elPFIsoDepositPU%s" % postfix)
    deposit.src = cms.InputTag("pfSelectedElectrons%s" % postfix)
    deposit.ExtractorPSet.inputCandView = cms.InputTag("pfPileUpAllChargedParticles%s" % postfix)

    # Adapt cut for pfSelectedElectrons
    # Default cut: pt > 5 & gsfElectronRef.isAvailable() & gsfTrackRef.trackerExpectedHitsInner.numberOfLostHits<2

    setattr(process, "pfSelectedElectrons%s" % postfix, cms.EDFilter(
        "GenericPFCandidateSelector",
        src = cms.InputTag("pfElectronsFromVertex%s" % postfix),
        cut = cms.string("pt > 10 && gsfTrackRef.isNonnull && gsfTrackRef.trackerExpectedHitsInner.numberOfLostHits<2")
        )
        )

    process.pfIsolatedElectronsClones  = cms.EDFilter(
            "IsolatedPFCandidateSelector",
            src = cms.InputTag("pfSelectedElectrons%s" % postfix),
            isolationValueMapsCharged = cms.VInputTag(
                cms.InputTag("elPFIsoValueCharged03PFId%s" % postfix),
                ),
            isolationValueMapsNeutral = cms.VInputTag(
                cms.InputTag("elPFIsoValueNeutral03PFId%s" % postfix),
                cms.InputTag("elPFIsoValueGamma03PFId%s" % postfix)
                ),
            doDeltaBetaCorrection = cms.bool(False),
            deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFId%s" % postfix),
            deltaBetaFactor = cms.double(-0.5),
            ## if True isolation is relative to pT
            isRelative = cms.bool(True),
            isolationCut = cms.double(0.10),
            ## Added in attached patch
            doEffectiveAreaCorrection = cms.bool(True),
            effectiveAreas = cms.InputTag("elEffectiveAreas03%s" % postfix),
            rho = cms.InputTag("kt6PFJets", "rho")
            )

    pfIsolatedElectrons = cms.EDFilter("PFCandidateFwdPtrCollectionStringFilter",
            src = cms.InputTag("pfIsolatedElectronsClones"),
            cut = cms.string(""),
            makeClones = cms.bool(True)
            )

    # Override default electron collection by our new one
    setattr(process, "pfIsolatedElectrons%s" % postfix, pfIsolatedElectrons) 

    # Set correct isolation deposits for patElectron production
    # FIXME: This should be enable if we want to recompute isolation from the pat electrons collections.
    # Unfortunately, it crashes sometimes when accessing deposits, because they are created from
    # pfSelectedElectrons<postfix> and patElectrons<postfix> red deposits using electrons coming from
    # pfIsolatedElectrons<postfix>.

    # adaptPFIsoElectrons(process, getattr(process, "patElectrons%s" % postfix), postfix, "03")

    # Produce electron conversions selection for Electron ID
    process.patConversions = cms.EDProducer("PATConversionProducer",
            # input collection
            electronSource = cms.InputTag("selectedPatElectrons%s" % postfix)
            # this should be your last selected electron collection name since currently index is used to match with electron later. We can fix this using reference pointer.
            )

    # Produce electron conversions selection for Electron ID
    process.patConversionsLoose = cms.EDProducer("PATConversionProducer",
            # input collection
            electronSource = cms.InputTag("selectedPatElectronsLoose%s" % postfix)
            # this should be your last selected electron collection name since currently index is used to match with electron later. We can fix this using reference pointer.
            )

    # Enable deltaBeta correction for muon isolation
    # Default cut from https://github.com/cms-sw/cmssw/blob/CMSSW_6_2_X/CommonTools/ParticleFlow/python/Isolation/pfIsolatedMuons_cfi.py
    # pt > 5 & muonRef.isAvailable() & muonRef.pfIsolationR04().sumChargedHadronPt + muonRef.pfIsolationR04().sumNeutralHadronEt + 
    #   muonRef.pfIsolationR04().sumPhotonEt < 0.15 * pt
    # deltaBeta isolation is: [sumChargedHadronPt + max(0., sumNeutralHadronPt + sumPhotonPt - 0.5 * sumPUPt] / pt

    # pt > 10, global muon, deltaBeta isolation < 0.12
    cut = "pt > 10 & muonRef.isAvailable() & muonRef.isGlobalMuon() & ((muonRef.pfIsolationR04().sumChargedHadronPt + max(0.0, muonRef.pfIsolationR04().sumNeutralHadronEt + muonRef.pfIsolationR04().sumPhotonEt - 0.5 * muonRef.pfIsolationR04().sumPUPt)) < 0.12 * pt)"
    getattr(process, "pfIsolatedMuons%s" % postfix).cut = cut

    #process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi') 
    #process.eidMVASequence = cms.Sequence(process.mvaTrigV0 + process.mvaNonTrigV0)
    ##Electron ID
    #process.patElectronsPFlow.electronIDSources.mvaTrigV0    = cms.InputTag("mvaTrigV0")
    #process.patElectronsPFlow.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0") 
    #process.patDefaultSequencePFlow.replace(process.patElectronsPFlow, process.eidMVASequence * process.patElectronsPFlow)

    # Compute effective areas for correcting isolation
    loadWithPostfix(process, "PatTopProduction.Tools.electronEffectiveAreaProducer_cfi", postfix)

    getattr(process, "elEffectiveAreas03%s" % postfix).src = cms.InputTag("pfSelectedElectrons%s" % postfix)

    if isMC:
        getattr(process, "elEffectiveAreas03%s" % postfix).target = cms.string("EAFall11MC")

    #####
    # PAT object configuration
    #####

    # jets
    process.selectedPatJetsPFlow.cut = 'pt > 10. & abs(eta) < 3.'

    # muons
    process.patMuonsPFlow.usePV = False
    process.patMuonsPFlow.embedTrack = True

    # electrons
    process.patElectronsPFlow.usePV = False
    process.patElectronsPFlow.embedTrack = True

    #####
    # Loose collections with no isolation cut applied
    # Clone selectedPatMuons / selectedPatElectrons, and use in input pfMuons / pfElectrons
    #####

    setattr(process, "selectedPatMuonsLoose%s" % postfix, getattr(process, "patMuons%s" % postfix).clone(
        pfMuonSource = cms.InputTag("pfMuons%s" % postfix),
        embedGenMatch = False,
        addGenMatch = False
        )
        )

    setattr(process, "selectedPatElectronsLoose%s" % postfix, getattr(process, "patElectrons%s" % postfix).clone(
        pfElectronSource = cms.InputTag("pfSelectedElectrons%s" % postfix),
        embedGenMatch = False,
        addGenMatch = False
        )
        )


    adaptPFIsoElectrons(process, getattr(process, "selectedPatElectronsLoose%s" % postfix), postfix, "03")

    if not isMC:
        removeMCMatchingPF2PAT(process, '') 

    #####
    # P2FPAT is done. Now setup some filters
    #####

    # require physics declared
    process.load('HLTrigger.special.hltPhysicsDeclared_cfi')
    process.hltPhysicsDeclared.L1GtReadoutRecordTag = 'gtDigis'

    # require scraping filter
    if not isMC:
        process.scrapingVeto = cms.EDFilter("FilterOutScraping",
                applyfilter = cms.untracked.bool(True),
                debugOn = cms.untracked.bool(False),
                numtrack = cms.untracked.uint32(10),
                thresh = cms.untracked.double(0.25)
                )

    # MET Filters
    process.load('RecoMET.METFilters.metFilters_cff')

    # Remove uneeded filter
    del(process.tobtecfakesfilter)

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
            'keep *_patMETsRaw*_*_PAT', # Keep raw met
            'keep *_allConversions*_*_*',

            # For isolations and conversions vetoes
            'keep *_gsfElectron*_*_*',
            'keep *_offlineBeamSpot*_*_*'
            ]

    # RelVal in inputs
    #from PhysicsTools.PatAlgos.tools.cmsswVersionTools import pickRelValInputFiles
    #process.source.fileNames = pickRelValInputFiles(cmsswVersion = "CMSSW_5_3_6", globalTag = "PU_START53_V14", debug = True, numberOfFiles = 1)

    process.options.wantSummary = False

    process.MessageLogger.cerr.FwkReport.reportEvery = 1

    print("Config loaded")

    return process
