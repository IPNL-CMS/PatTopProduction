def jetToolBox(process, postfix):
    """
    Add PU jet Id and quark / gluon tagger to the process
    Inspired by RecoJets/JetProducers/test/jettoolbox_cfg.py
    """

    import FWCore.ParameterSet.Config as cms

    # PU jet Id
    from PhysicsTools.PatAlgos.tools.helpers import loadWithPostfix, applyPostfix
    loadWithPostfix(process, 'RecoJets.JetProducers.pileupjetidproducer_cfi', postfix)

    # Customize to run on collections produced by PF2PAT
    applyPostfix(process, "pileupJetIdEvaluator", postfix).jets = cms.InputTag("pfNoTauClonesPFlow")
    applyPostfix(process, "pileupJetIdCalculator", postfix).jets = cms.InputTag("pfNoTauClonesPFlow")
    applyPostfix(process, "pileupJetIdEvaluator", postfix).rho = cms.InputTag("fixedGridRhoFastjetAll")
    applyPostfix(process, "pileupJetIdCalculator", postfix).rho = cms.InputTag("fixedGridRhoFastjetAll")

    # Add informations as userdata: easily accessible
    applyPostfix(process, "patJets", postfix).userData.userFloats.src += ['pileupJetIdEvaluator%s:fullDiscriminant' % postfix]
    applyPostfix(process, "patJets", postfix).userData.userInts.src += ['pileupJetIdEvaluator%s:cutbasedId' % postfix, 'pileupJetIdEvaluator%s:fullId' % postfix]

    # FIXME: Not sure if we want to keep this collection. It's just a bunch of number, so space shouldn't be a problem
    process.out.outputCommands += ['keep *_pileupJetIdEvaluator%s_*_*' % postfix]

    # Quark / gluon tagger
    loadWithPostfix(process, 'RecoJets.JetProducers.QGTagger_cfi', postfix)
    delattr(process, "QGTaggerMiniAOD" + postfix)

    # Customize to run on collections produced by PF2PAT
    applyPostfix(process, "QGTagger", postfix).srcJets = cms.InputTag("pfNoTauClonesPFlow")

    applyPostfix(process, "QGTagger", postfix).jetsLabel = cms.string('QGL_AK4PFchs')

    applyPostfix(process, "patJets", postfix).userData.userFloats.src += ['QGTagger%s:qgLikelihood' % postfix]

    # FIXME: Do we want to keep this?
    process.out.outputCommands += ['keep *_QGTagger%s_*_*' % postfix]
