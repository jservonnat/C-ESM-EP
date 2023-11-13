#!/bin/bash
# Script called by libIGCM for executing the C-ESM-EP code

# Setup parameters are read from libIGCM_post.param (as written by
# libIGCM_install.sh when called by libIGCM ins_job)

# Run-time parameters are provided as arguments. They are date begin and end
# for the time slice to process. In these dates, only years are used

# Execution occurs in the directory of the script, which is a C-ESM-EP code
# 'lite' directory

#set -x

begin=${1?Please provide begin year of the period to process}
end=${2??Please provide end year of the period to process}

cd $(dirname $0)
out=$(pwd)/libIGCM_post.out

# Read setup parameters
read CesmepCode comparison DateBegin CesmepPeriod CesmepSlices \
     CesmepSlicesDuration cache components < libIGCM_post.param

# Analyze if last batch of simulation outputs allow to compute a new
# atlas slice (where slices are aligned with DateBegin and have a
# duration of CesmepPeriod).  i.e. that it exists a slice ending in
# the provided data period, If there is multiple such slices, we use
# the last one

DateBegin=${DateBegin:0:4}
begin=${begin:0:4}
end=${end:0:4}

if [ $CesmepPeriod != 0 ] ; then
    
    # Check that a slice ends in [begin,end]
    got_a_slice_end=false
    slice_end=$(( DateBegin + CesmepPeriod -1 ))
    slice_begin=$(( slice_end - CesmepSlicesDuration +1 ))
    nb=0
    while [ $slice_end -le $end ]; do
	#echo "Checking for [$slice_begin,$slice_end]"
	if [ $slice_end -ge $begin -a $slice_end -le $end -a $slice_begin -ge $DateBegin ]
	then 
	    got_a_slice_end=true
	fi
	new_end=$(( slice_end + CesmepPeriod ))
	if [ $new_end -le $slice_end ] ; then 
	    echo "Issue: cannot increment with CesmepPeriod=$CesmepPeriod "
	    exit 1
	fi
	slice_end=$new_end
	slice_begin=$(( slice_end - CesmepSlicesDuration +1 ))
    done
    slice_end=$(( slice_end - CesmepPeriod ))
    slice_begin=$(( slice_end - CesmepSlicesDuration + 1))

    if [ $got_a_slice_end = false ] ; then
	echo "No relevant slice ends in [$begin,$end]  "
	echo "(DateBegin=$DateBegin, CesmepPeriod=$CesmepPeriod, CesmepSlicesDuration=$CesmepSlicesDuration) " 
	exit 1
    fi
else

    # Script is supposed to have been called at simulations's end
    slice_end=$end
fi

# Complement settings with runtime parameters
fixed_settings=$comparison/libIGCM_fixed_settings.py
settings=$comparison/libIGCM_settings.py
cat $fixed_settings > $settings
cat <<-EOF #>> $settings
	end            = $slice_end
	data_end       = $end
	EOF

export CESMEP_CLIMAF_CACHE=$cache
source $(pwd)/setenv_C-ESM-EP.sh
echo "Launching atlas for a period ending at $slice_end" > $out
submit_dir=$(basename $(cd ..; pwd))
python3 run_C-ESM-EP.py $comparison $components ${slice_end}_${submit_dir} >> $out 2>&1
if [ $? -ne 0 ] ;then
    echo "Issue launching C-ESM-EP atlas - see $out"
    exit 1
else
    echo "C-ESM-EP atlas succesfully launched - see $out"
fi
