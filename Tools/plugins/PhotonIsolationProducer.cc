// system include files
#include <memory>
#include <iostream>
#include <string>
#include <vector>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include <DataFormats/PatCandidates/interface/Photon.h>

#include "EGamma/EGammaAnalysisTools/interface/PFIsolationEstimator.h"
#include "RecoEgamma/EgammaTools/interface/ConversionTools.h"

class PhotonIsolationProducer : public edm::EDProducer {
  public:
    explicit PhotonIsolationProducer(const edm::ParameterSet&);
    ~PhotonIsolationProducer();

  private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;

    // ----------member data --------------------------
    edm::InputTag src_;

    // Photon ID
    PFIsolationEstimator mPFIsolator;
};

PhotonIsolationProducer::PhotonIsolationProducer(const edm::ParameterSet& iConfig)
{
  src_= iConfig.getParameter<edm::InputTag>("src");

  mPFIsolator.initializePhotonIsolation(true);
  mPFIsolator.setConeSize(0.3);

  produces<edm::ValueMap<double>>("chargedHadronsIsolation");
  produces<edm::ValueMap<double>>("photonIsolation");
  produces<edm::ValueMap<double>>("neutralHadronsIsolation");
  produces<edm::ValueMap<bool>>("hasMatchedPromptElectron");
}


PhotonIsolationProducer::~PhotonIsolationProducer()
{

}

// ------------ method called to produce the data  ------------
void PhotonIsolationProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  std::auto_ptr<edm::ValueMap<double>> chIsoMap(new edm::ValueMap<double>());
  edm::ValueMap<double>::Filler chFiller(*chIsoMap);

  std::auto_ptr<edm::ValueMap<double>> phIsoMap(new edm::ValueMap<double>());
  edm::ValueMap<double>::Filler phFiller(*phIsoMap);

  std::auto_ptr<edm::ValueMap<double>> nhIsoMap(new edm::ValueMap<double>());
  edm::ValueMap<double>::Filler nhFiller(*nhIsoMap);

  std::auto_ptr<edm::ValueMap<bool>> promptConvMap(new edm::ValueMap<bool>());
  edm::ValueMap<bool>::Filler promptConvFiller(*promptConvMap);

  edm::Handle<pat::PhotonCollection> photonsHandle;
  iEvent.getByLabel(src_, photonsHandle);
  
  // First, conversion safe electron veto
  edm::Handle<reco::BeamSpot> bsHandle;
  iEvent.getByLabel("offlineBeamSpot", bsHandle);
  const reco::BeamSpot &beamspot = *bsHandle;

  edm::Handle<reco::ConversionCollection> hConversions;
  iEvent.getByLabel("allConversions", hConversions);

  edm::Handle<reco::GsfElectronCollection> hElectrons;
  iEvent.getByLabel("gsfElectrons", hElectrons);

  edm::Handle<reco::PFCandidateCollection> hPFCandidates;
  iEvent.getByLabel("particleFlow", hPFCandidates);
  const reco::PFCandidateCollection& pfCandidates = *hPFCandidates;

  edm::Handle<reco::VertexCollection>  vertexCollection;
  iEvent.getByLabel("goodOfflinePrimaryVertices", vertexCollection);
  reco::VertexRef vertexRef(vertexCollection, 0);

  if (vertexCollection->empty())
    return;

  std::vector<double> chIsoValues;
  std::vector<double> phIsoValues;
  std::vector<double> nhIsoValues;
  std::vector<bool>   promptConvValues;
  chIsoValues.reserve(photonsHandle->size());
  phIsoValues.reserve(photonsHandle->size());
  nhIsoValues.reserve(photonsHandle->size());
  promptConvValues.reserve(photonsHandle->size());

  pat::PhotonCollection::const_iterator it = photonsHandle->begin();
  for (; it != photonsHandle->end(); ++it) {
    pat::Photon photon = *it;

    promptConvValues.push_back(ConversionTools::hasMatchedPromptElectron(photon.superCluster(), hElectrons, hConversions, beamspot.position()));

    mPFIsolator.fGetIsolation(&photon, &pfCandidates, vertexRef, vertexCollection);

    chIsoValues.push_back(mPFIsolator.getIsolationCharged());
    phIsoValues.push_back(mPFIsolator.getIsolationPhoton());
    nhIsoValues.push_back(mPFIsolator.getIsolationNeutral());
  }
  
  chFiller.insert(photonsHandle, chIsoValues.begin(), chIsoValues.end());
	chFiller.fill();
	
	phFiller.insert(photonsHandle, phIsoValues.begin(), phIsoValues.end());
	phFiller.fill();
	
	nhFiller.insert(photonsHandle, nhIsoValues.begin(), nhIsoValues.end());
	nhFiller.fill();

  promptConvFiller.insert(photonsHandle, promptConvValues.begin(), promptConvValues.end());
  promptConvFiller.fill();

  iEvent.put(chIsoMap, "chargedHadronsIsolation");
  iEvent.put(phIsoMap, "photonIsolation");
  iEvent.put(nhIsoMap, "neutralHadronsIsolation");
  iEvent.put(promptConvMap, "hasMatchedPromptElectron");
}

// ------------ method called once each job just before starting event loop  ------------
  void
PhotonIsolationProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
PhotonIsolationProducer::endJob() {
}

//define this as a plug-in
DEFINE_FWK_MODULE(PhotonIsolationProducer);
