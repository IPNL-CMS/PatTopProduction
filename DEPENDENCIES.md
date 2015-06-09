Dependencies
============

## CMSSW

    export SCRAM_ARCH=slc6_amd64_gcc491
    cmsrel CMSSW_7_4_4_patch4
    cd CMSSW_7_4_4_patch4
    cmsenv

    cd src/
    git cms-init

## Electron ID

    git cms-merge-topic 9003 #this is the version that is in CMSSW_7_4_X
