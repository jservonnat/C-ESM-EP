#!/bin/bash

# Helper script for preparing C-ESM-EP runs to be launched by libIGCM during a simulation

# It is called by libIGCM at the stage of simulation preparation, and creates :
#    - libIGCM_run.sh : a script that will be called by libIGCM during simulation
#    - a relevant datasets_setups.py file (by copying a fixed file)
#    - a settings file imported by that datasets_setup.py file

# The created sript activates a set of components which matches the type of experiment

#set -x

# LibIGCM provided parameters
R_SAVE=$1
PackFrequency=$2
comparison=${3?Must provide comaprison as third arg }

if [[ ! -d "/ccc" ||  -d "/data" ]] ; then
    # Computing centers other than TGCC
    echo "echo No C-ESM-EP available on this center ($(uname -n))" > libIGCM_run.sh
    chmod +x libIGCM_run.sh
    exit 1
fi

# We are at TGCC
root=$(echo $R_SAVE | cut -d / -f 1-5)
Login=$(echo $R_SAVE | cut -d / -f 6)
TagName=$(echo $R_SAVE | cut -d / -f 8)
SpaceName=$(echo $R_SAVE | cut -d / -f 9)
ExpType=$(echo $R_SAVE | cut -d / -f 10)
ExperimentName=$(echo $R_SAVE | cut -d / -f 11)

if [ $SpaceName = TEST ] && [ $PackFrequency = NONE ] ; then
    PackFrequency=1Y
fi
# This script can be called from anywhere, but is supposed to work in its directory
dir=$(cd $(dirname $0); pwd)
cd $dir

cp libIGCM_datasets.py $comparison/datasets_setup.py

cat <<-EOF > $comparison/libIGCM_settings.py
	root           = '$root'
	Login          = '${Login}'
	TagName        = '${TagName}'
	SpaceName      = '${SpaceName}'
	ExpType        = '${ExpType}'
	ExperimentName = '${ExperimentName}'
	PackFrequency  = '${PackFrequency}'
	EOF

# Set components list according to experiment type (e.g. LMDZOR/amip)
case $ExpType in
    LMDZOR*)
	
	#components=MainTimeSeries,Atmosphere_Surface,Atmosphere_StdPressLev,Atmosphere_zonmean,NH_Polar_Atmosphere_StdPressLev,NH_Polar_Atmosphere_Surface,SH_Polar_Atmosphere_StdPressLev,SH_Polar_Atmosphere_Surface
	components=AtlasExplorer ;;
     ORCHIDEE_OL*)
	components=MainTimeSeries,ORCHIDEE ;;
     NEMO*) 
        components=MainTimeSeries,NEMO_main,NEMO_zonmean,NEMO_depthlevels,ENSO ;;
     *)
	components=""
esac

echo "cd $dir ; python run_C-ESM-EP.py $comparison $components" > libIGCM_run.sh
chmod +x libIGCM_run.sh



