#!/bin/bash
# The script that libIGCM will call for executing the C-ESM-EP code

# Run time parameters are provided as arguments

# Setup parameters are read from libIGMCM_post.param (as written by
# libIGCM_install.sh when called by libIGCM ins_job)

begin=$1
end=$2

cd $(dirname $0)

#Read comparison and components to run from helper file
read comparison components DateBegin ConfigCesmep CesmepCode remain < libIGCM_post.param
[ $components = , ] && components=""

# Complement settings with runtime parameters
settings=$comparison/libIGCM_settings.py

OUT='Analyse'
frequency='monthly'
if [ $ConfigCesmep = SE ]; then
    frequency='seasonal'
elif [ $ConfigCesmep != TS ]; then
    OUT='Output'
fi
cat <<-EOF >> $settings
	DateBegin      = '${DateBegin/-/}'
	begin          = '${begin}'
	end            = '${end}'
	frequency      = '${frequency}'
	OUT            = '${OUT}' 
	EOF

out=$(pwd)/libIGCM_post.out
export PYTHONPATH=$CesmepCode:$PYTHONPATH
python run_C-ESM-EP.py $comparison $components > $out 2>&1
if [ $? -ne 0 ] ;then
    echo "Issue launching C-ESM-EP atlas - see $out"
    exit 1
else
    echo "C-ESM-EP atlas succesfully launched - see $out"
fi
