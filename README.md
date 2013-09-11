How-to use PatTopProduction
===========================

Git branches
------------

Each different version of CMSSW is supported in a separate branch :

  - cmssw_5_3_5: CMSSW 5.3.5
  - cmssw_5_3_9: CMSSW 5.3.9_patch2
  - master: CMSSW 6.2.0_patch1 (current branch)

WARNING
-------

This PAT recipe is still under development. Use with caution.

Setup local area
----------------

### CMSSW

    export SCRAM_ARCH=slc5_amd64_gcc472
    cmsrel CMSSW_6_2_0_patch1
    cd CMSSW_6_2_0_patch1
    cmsenv

    cd src/

### Various fixes

    # Waiting for upstream integration: https://github.com/cms-sw/cmssw/pull/750
    git cms-merge-topic -u IPNL-CMS:sys_shift_met_corrections

    # Waiting for upstream integration: https://github.com/cms-sw/cmssw/pull/757
    git cms-merge-topic -u blinkseb:fix_met_filters

    git cms-addpkg CommonTools/ParticleFlow

    git clone https://github.com/IPNL-CMS/PatTopProduction.git
    git apply PatTopProduction/0001-added-support-for-effective-area-correction-on-Isola.patch

    scram b -j8
