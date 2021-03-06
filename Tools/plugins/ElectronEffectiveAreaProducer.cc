// -*- C++ -*-
//
// Class:      ElectronEffectiveAreaProducer
// 
/*
Description: [one line class summary]

Implementation:
[Notes on implementation]
*/
//
// Original Author:  Brochet Sébastien,
//         Created:  Wed Nov 21 16:40:00
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/Common/interface/ValueMap.h>

#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"

#include <DataFormats/EgammaCandidates/interface/GsfElectron.h>

#include "PatTopProduction/Tools/interface/ElectronEffectiveArea.h"

class ElectronEffectiveAreaProducer: public edm::EDProducer {
  public:
    typedef edm::ValueMap<double> EffectiveAreaMap;

    explicit ElectronEffectiveAreaProducer(const edm::ParameterSet&);
    virtual ~ElectronEffectiveAreaProducer();

  private:

    ElectronEffectiveArea::ElectronEffectiveAreaType convertToType(const std::string& type) const;
    ElectronEffectiveArea::ElectronEffectiveAreaTarget convertToTarget(const std::string& target) const;

    virtual void beginRun(edm::Run const&, edm::EventSetup const&);
    virtual void produce(edm::Event&, const edm::EventSetup&);

    edm::InputTag                                      src_;
    ElectronEffectiveArea::ElectronEffectiveAreaType   type_;
    ElectronEffectiveArea::ElectronEffectiveAreaTarget target_;
};      

ElectronEffectiveAreaProducer::ElectronEffectiveAreaProducer(const edm::ParameterSet& iConfig) {

  src_               = iConfig.getParameter<edm::InputTag>("src");
  std::string type   = iConfig.getParameter<std::string>("type");
  std::string target = iConfig.getParameter<std::string>("target");

  type_ = convertToType(type);
  target_ = convertToTarget(target);

  if (type_ < 0)
    throw cms::Exception("Incorrect parameter") << "Type is invalid. Please check your value.";

  if (target_ < 0)
    throw cms::Exception("Incorrect parameter") << "Target is invalid. Please check your value.";

  produces<EffectiveAreaMap>();
}

ElectronEffectiveAreaProducer::~ElectronEffectiveAreaProducer() 
{}

void ElectronEffectiveAreaProducer::beginRun(edm::Run const& iRun, edm::EventSetup const& iSetup) {}

void ElectronEffectiveAreaProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {

  edm::Handle<reco::PFCandidateCollection> electronsHandle;
  iEvent.getByLabel(src_, electronsHandle);

  std::auto_ptr<EffectiveAreaMap> map(new EffectiveAreaMap());
  EffectiveAreaMap::Filler filler(*map);

  std::vector<double> areas;
  areas.reserve(electronsHandle->size());

  for (reco::PFCandidateCollection::const_iterator it = electronsHandle->begin(); it != electronsHandle->end(); ++it) {
    double effectiveArea = ElectronEffectiveArea::GetElectronEffectiveArea(type_, it->gsfElectronRef()->superCluster()->eta(), target_); 
    areas.push_back(effectiveArea);
  }

  filler.insert(electronsHandle, areas.begin(), areas.end());
  filler.fill();

  iEvent.put(map);
}

ElectronEffectiveArea::ElectronEffectiveAreaType ElectronEffectiveAreaProducer::convertToType(const std::string& type) const {
  if (type == "TrkIso03") {
    return ElectronEffectiveArea::kEleTrkIso03;
  } else if (type == "EcalIso03") {
    return ElectronEffectiveArea::kEleEcalIso03;
  } else if (type == "HcalIso03") {
    return ElectronEffectiveArea::kEleHcalIso03;
  } else if (type == "TrkIso04") {
    return ElectronEffectiveArea::kEleTrkIso04;
  } else if (type == "EcalIso04") {
    return ElectronEffectiveArea::kEleEcalIso04;
  } else if (type == "HcalIso04") {
    return ElectronEffectiveArea::kEleHcalIso04;
  } else if (type == "ChargedIso03") {
    return ElectronEffectiveArea::kEleChargedIso03;
  } else if (type == "GammaIso03") {
    return ElectronEffectiveArea::kEleGammaIso03;
  } else if (type == "NeutralHadronIso03") {
    return ElectronEffectiveArea::kEleNeutralHadronIso03;
  } else if (type == "GammaAndNeutralHadronIso03") {
    return ElectronEffectiveArea::kEleGammaAndNeutralHadronIso03;
  } else if (type == "ChargedIso04") {
    return ElectronEffectiveArea::kEleChargedIso04;
  } else if (type == "GammaIso04") {
    return ElectronEffectiveArea::kEleGammaIso04;
  } else if (type == "NeutralHadronIso04") {
    return ElectronEffectiveArea::kEleNeutralHadronIso04;
  } else if (type == "GammaAndNeutralHadronIso04") {
    return ElectronEffectiveArea::kEleGammaAndNeutralHadronIso04;
  } else if (type == "GammaIsoDR0p0To0p1") {
    return ElectronEffectiveArea::kEleGammaIsoDR0p0To0p1;
  } else if (type == "GammaIsoDR0p1To0p2") {
    return ElectronEffectiveArea::kEleGammaIsoDR0p1To0p2;
  } else if (type == "GammaIsoDR0p2To0p3") {
    return ElectronEffectiveArea::kEleGammaIsoDR0p2To0p3;
  } else if (type == "GammaIsoDR0p3To0p4") {
    return ElectronEffectiveArea::kEleGammaIsoDR0p3To0p4;
  } else if (type == "GammaIsoDR0p4To0p5") {
    return ElectronEffectiveArea::kEleGammaIsoDR0p4To0p5;
  } else if (type == "NeutralHadronIsoDR0p0To0p1") {
    return ElectronEffectiveArea::kEleNeutralHadronIsoDR0p0To0p1;
  } else if (type == "NeutralHadronIsoDR0p1To0p2") {
    return ElectronEffectiveArea::kEleNeutralHadronIsoDR0p1To0p2;
  } else if (type == "NeutralHadronIsoDR0p2To0p3") {
    return ElectronEffectiveArea::kEleNeutralHadronIsoDR0p2To0p3;
  } else if (type == "NeutralHadronIsoDR0p3To0p4") {
    return ElectronEffectiveArea::kEleNeutralHadronIsoDR0p3To0p4;
  } else if (type == "NeutralHadronIsoDR0p4To0p5") {
    return ElectronEffectiveArea::kEleNeutralHadronIsoDR0p4To0p5;
  }

  return static_cast<ElectronEffectiveArea::ElectronEffectiveAreaType>(-1);
}

ElectronEffectiveArea::ElectronEffectiveAreaTarget ElectronEffectiveAreaProducer::convertToTarget(const std::string& target) const {
  if (target == "EANoCorr") {
    return ElectronEffectiveArea::kEleEANoCorr;
  } else if (target == "EAData2011") {
    return ElectronEffectiveArea::kEleEAData2011;
  } else if (target == "EASummer11MC") {
    return ElectronEffectiveArea::kEleEASummer11MC;
  } else if (target == "EAFall11MC") {
    return ElectronEffectiveArea::kEleEAFall11MC;
  } else if (target == "EAData2012") {
    return ElectronEffectiveArea::kEleEAData2012;
  }

  return static_cast<ElectronEffectiveArea::ElectronEffectiveAreaTarget>(-1);
}

DEFINE_FWK_MODULE(ElectronEffectiveAreaProducer);
