#!/bin/bash
set -e

# Testing that an execution of a reference comparison provides the reference results
# This script does launch the test comaprison; another one checks the results

test=${1:-test_comparison}
reference=${2:-reference_comparison}

rootdir=$(cd $(dirname $0); pwd)/..  # we assume that this script is in a subdir of C-ESM-EP main dir
cd $rootdir
rm -fr $test
cp -r $reference $test

# May need to use a dedicated cache for forcing re-compute
# e.g. in case CLIMAF_CACHE is shared with reference run
if [ ! -z $CESMEP_CLIMAF_CACHE ] ; then 
    mkdir -p ${CESMEP_CLIMAF_CACHE?}
    rm -fR $CESMEP_CLIMAF_CACHE/*
fi

python run_C-ESM-EP.py $test 

if [ ! -z $CESMEP_CLIMAF_CACHE ] ; then 
    echo "Don't forget to erase temporary cache after results check. It is at $CESMEP_CLIMAF_CACHE"
fi
