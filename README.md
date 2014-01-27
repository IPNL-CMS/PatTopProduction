How-to use PatTopProduction
===========================

Git branches
------------

Each different version of CMSSW is supported in a separate branch :

  - cmssw_5_3_5: CMSSW 5.3.5 (SL5)
  - cmssw_5_3_9: CMSSW 5.3.9_patch2 (SL5)
  - cmssw_5_3_12: CMSSW 5.3.12_patch3 (*SL6*)
  - cmssw_5_3_14_patch2: CMSSW 5.3.14_patch2 (current branch) (*SL6*)
  - master: CMSSW 6.2.0_patch1 (SL5)

Setup local area
----------------

### CMSSW

    export SCRAM_ARCH=slc6_amd64_gcc472
    cmsrel CMSSW_5_3_14_patch2
    cd CMSSW_5_3_14_patch2
    cmsenv

    cd src/

### PAT

Nothing to be done here, fully integrated.

### Configuration

    git cms-addpkg EgammaAnalysis/ElectronTools
    cd EgammaAnalysis/ElectronTools/data
    cat download.url | xargs wget
    cd -

### Effective area for electron isolation

    git cms-addpkg CommonTools/ParticleFlow

### MET Filters

    git cms-merge-topic -u TaiSakuma:53X-met-131120-01

### Final configuration

    git clone https://github.com/IPNL-CMS/PatTopProduction.git
    git checkout cmssw_5_3_14_patch2
    git apply PatTopProduction/0001-added-support-for-effective-area-correction-on-Isola.patch

### Build

    scram b -j8
