#!/bin/bash
# The script that libIGCM will call for executing the C-ESM-EP code

# Run time parameters are provided as arguments

# Setup parameters are read from libIGMCM_post.param (as written by
# libIGCM_install.sh when called by libIGCM ins_job)
#set -x

begin=$1
end=$2

cd $(dirname $0)
out=$(pwd)/libIGCM_post.out

# Read helper file
read CesmepCode comparison DateBegin CesmepPeriod CesmepSlices cache components < libIGCM_post.param

# Analyze if last batch of simulation outputs allow to compute a new atlas slice
# (where slices are aligned with DateBegin and have a duration of CesmepPeriod).
# i.e. that it exists a slice ending in the provided data period, 
# If there is multiple such slices, we use the last one

DateBegin=${DateBegin:0:4}
begin=${begin:0:4}
end=${end:0:4}

if [ $CesmepPeriod != 0 ] ; then 
    compute_new_slice=false
    slice_end=$(( DateBegin + CesmepPeriod -1 ))
    while [ $slice_end -le $end ]; do
	if [ $slice_end -ge $begin -a $slice_end -le $end ] ; then
	    compute_new_slice=true
	fi
	slice_end=$(( slice_end + CesmepPeriod ))
    done
    slice_end=$(( slice_end - CesmepPeriod ))

    if [ $compute_new_slice = false ] ; then
	echo "Not enough data for computing a new atlas slice ">$out
	echo "DateBegin=$DateBegin, CesmepPeriod=$CesmepPeriod, begin=$begin, end=$end " >> $out
	exit 0
    fi
else
    slice_end=$end
fi

# Complement settings with runtime parameters
fixed_settings=$comparison/libIGCM_fixed_settings.py
settings=$comparison/libIGCM_settings.py
cat $fixed_settings > $settings
cat <<-EOF >> $settings
	end            = $slice_end
	data_end       = $end
	EOF

export PYTHONPATH=$(pwd):$CesmepCode:$PYTHONPATH
export CESMEP_CLIMAF_CACHE=$cache
echo "Launching atlas for a period ending at $slice_end" > $out
python run_C-ESM-EP.py $comparison $components >> $out 2>&1
if [ $? -ne 0 ] ;then
    echo "Issue launching C-ESM-EP atlas - see $out"
    exit 1
else
    echo "C-ESM-EP atlas succesfully launched - see $out"
fi
