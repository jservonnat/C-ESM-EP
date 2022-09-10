#!/bin/bash

# Helper script for preparing C-ESM-EP runs to be launched by libIGCM during a simulation

# It is called by libIGCM at the stage of simulation preparation (ins_job), and creates :
#    - a relevant datasets_setups.py file (by copying a fixed file)
#    - a settings file imported by that datasets_setup.py file
#    - libIGCM_run.sh : a script that will be called by libIGCM during simulation
#    - a relevant entry for 'account' in file settings.py

# The created script activates a set of components which matches the type of experiment

#set -x
set -e

# LibIGCM provided parameters
target=$1            # Directory where C-ESM-EP  should be installed
comparison=$2        # Which C-ESM-EP 'comparison' will be run
jobname=$3           # Used as a prefix for comparison's name
R_SAVE=$4            # Directory holding simulation outputs
ProjectId=$5         # Which project ressource allocation should be charged
MailAdress=$6        # Mail adress as in libIGCM
DateBegin=$7         # Start date for the simulation
Post_Cesmep=$8       # Value of config.card Post section variable Cesmep

#CesmepFrequency=$6   # Time period , e.g. 10Y or AtEnd
#clim_period='last_'${CesmepFrequency}

if [[ ! -d "/ccc" ||  -d "/data" ]] ; then
    # Computing centers other than TGCC
    echo "echo No C-ESM-EP available on this center ($(uname -n))" 
    exit 1
fi

# We are at TGCC

# This script can be called from anywhere
dir=$(cd $(dirname $0); pwd)

# First install a light copy of C-ESM-EP and cd to there
$dir/install_lite.sh $target $comparison 
cd $target/cesmep_lite
mv $comparison ${jobname}_${comparison}
comparison=${jobname}_${comparison}

# Derive a set of parameters from output's path
root=$(echo $R_SAVE | cut -d / -f 1-5)
Login=$(echo $R_SAVE | cut -d / -f 6)
TagName=$(echo $R_SAVE | cut -d / -f 8)
SpaceName=$(echo $R_SAVE | cut -d / -f 9)
ExpType=$(echo $R_SAVE | cut -d / -f 10)
ExperimentName=$(echo $R_SAVE | cut -d / -f 11)

# Create comparison's parameters file and set first part
cat <<-EOF > $comparison/libIGCM_settings.py
	root           = '$root'
	Login          = '${Login}'
	TagName        = '${TagName}'
	SpaceName      = '${SpaceName}'
	ExpType        = '${ExpType}'
	ExperimentName = '${ExperimentName}'
	EOF

# Install a dedicated datasets_setup file
cp $dir/libIGCM_datasets.py $comparison/datasets_setup.py

# Compute components list according to experiment type (e.g. LMDZOR/amip)
case $TagName in
    LMDZOR*)
	#components=MainTimeSeries,Atmosphere_Surface,Atmosphere_StdPressLev,Atmosphere_zonmean,NH_Polar_Atmosphere_StdPressLev,NH_Polar_Atmosphere_Surface,SH_Polar_Atmosphere_StdPressLev,SH_Polar_Atmosphere_Surface
	components=AtlasExplorer ;;
     ORCHIDEE*)
	components=MainTimeSeries,ORCHIDEE ;;
     OL2)
	components=MainTimeSeries ;;
     NEMO*) 
        components=MainTimeSeries,NEMO_main,NEMO_zonmean,NEMO_depthlevels,ENSO ;;
     *)
	components=","
esac

# Filter components list by actually existing components in the chosen comparison
activable_components=","
for c in $(echo $components | tr "," " "); do
    [ -d $comparison/$c ] && activable_components=${activable_components},${c}
done

# Write down comparison and components in a file that will be read by libIGCM_post.sh
echo "$comparison $activable_components $DateBegin $Post_Cesmep $dir" > libIGCM_post.param

# Set account/project to charge, and mail to use, in relevant file
sed -i \
    -e "s/account *=.*/account = $ProjectId/" \
    -e "s/mail *=.*/mail = ${MailAdress}/" \
    settings.py



