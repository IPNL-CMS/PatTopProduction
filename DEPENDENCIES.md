Dependencies
============

## CMSSW

    export SCRAM_ARCH=slc6_amd64_gcc472
    cmsrel CMSSW_5_3_18
    cd CMSSW_5_3_18
    cmsenv

    cd src/

## PAT

    git cms-addpkg PhysicsTools/PatAlgos
    git cms-addpkg CommonTools/Utils
    git cms-addpkg PhysicsTools/Configuration
    git cms-addpkg PhysicsTools/PatExamples
    git cms-addpkg PhysicsTools/PatUtils
    git cms-addpkg PhysicsTools/SelectorUtils
    git cms-addpkg PhysicsTools/UtilAlgos
    git cms-addpkg RecoBTag/SoftLepton
    git cms-addpkg RecoMET/METFilters
    git cms-merge-topic -u cms-analysis-tools:5_3_13-newJetFlavour
    git cms-merge-topic -u cms-analysis-tools:5_3_13-updatedPATConfigs

## Configuration

    git cms-addpkg EgammaAnalysis/ElectronTools
    cd EgammaAnalysis/ElectronTools/data
    cat download.url | xargs wget
    cd -

## Effective area for electron isolation

    git cms-addpkg CommonTools/ParticleFlow

## MET Filters

    git cms-merge-topic -u TaiSakuma:53X-met-140217-01

## PU Jet ID

    git cms-merge-topic -u IPNL-CMS:53x_pujetid

## Quark / gluon discriminator

    git clone https://github.com/amarini/QuarkGluonTagger.git
    cd QuarkGluonTagger
    git checkout v1-3-0
    cd ..
