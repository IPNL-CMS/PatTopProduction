import FWCore.ParameterSet.Config as cms

elEffectiveAreas03 = cms.EDProducer("ElectronEffectiveAreaProducer",
    src = cms.InputTag("pfSelectedElectrons"),
    type = cms.string("GammaAndNeutralHadronIso03"),
    target = cms.string("EAData2012")  # Use "EAFall11MC" for MC
)

elEffectiveAreas04 = cms.EDProducer("ElectronEffectiveAreaProducer",
    src = cms.InputTag("pfSelectedElectrons"),
    type = cms.string("GammaAndNeutralHadronIso04"),
    target = cms.string("EAData2012")  # Use "EAFall11MC" for MC
)
