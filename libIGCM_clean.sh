#!/bin/bash

# The script that libIGCM calls for house-keeping on C-ESM-EP outputs

# It also erases the climaf_cache, which location is read from
# libIGMCM_post.param

# It works only if installed in a $SUBMIT_DIR/cesmep_lite directory,
# by libIGCM's script 'ins_job' 

set -e

cd $(dirname $0)

# Read helper file
read CesmepCode comparison foo foo foo cache foo < libIGCM_post.param

export PYTHONPATH=$(pwd):$CesmepCode:$PYTHONPATH
export CESMEP_CLIMAF_CACHE=$cache
python run_C-ESM-EP.py $comparison clean 
