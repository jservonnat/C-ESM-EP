#!/bin/bash

# Testing that an execution of a reference comparison provides the
# reference results

# Another script does launch the test comparison; the present script
# checks the results and should be executed once batch jobs launched
# by the first one are completed

set -x
rootdir=$(cd $(dirname $0); pwd)/..  # we assume that this script is in a subdir of C-ESM-EP main dir
test=${1:-test_comparison}
ref_outputs=${2:-$rootdir/tests/reference_results}
ref_name=${3:-reference_comparison}

cd $rootdir

# Get output directories for both comparisons
test_outputs=$(python run_C-ESM-EP.py $test url | tail -n 1 | cut -c 4-)
test_outputs=$(dirname $test_outputs)

# List png files in reference comparison
refs=$(ls $ref_outputs/*/*.png)

# Check that components list is OK for test comparison
nok=0
dirs=$(echo $refs | xargs -n 1 dirname | sort -u)
for dir in $dirs; do
    component=$(basename $dir)
    other_dir=$test_outputs/$component
    if [ ! -d $other_dir ]; then
	echo "Missing component directory $other_dir "
	nok=$(( nok + 1 ))
    fi
done
if [ $nok -ne 0 ] && [ ${strict:-1} -eq 1 ]  ; then
    exit $nok
fi


# Test differences in graphics output, based on html index, using a CliMAF test utility
# Set your CliMAF version if needed

#CLIMAF=/home/ssenesi/climaf_installs/climaf_running
module load ${climaf_module:?Please set variable climaf_module}

export PYTHONPATH=${CLIMAF?}:$CLIMAF/tests:$PYTHONPATH

htmls=$(ls $ref_outputs/*/*.html | tr "\n" " ")
echo $htmls
cat <<-EOF >tmp.py
	import sys, os
	from tests.tools_for_tests import compare_html_files
	print("Comparing outputs for components :")#, end='')
	for file_ref in "$htmls".split() :
	   component = file_ref.split("/")[-2]
	   print(component)#, end='')
	   fic = file_ref.split("/")[-1].replace("$ref_name","$test")
	   print(fic)#, end='')
	   file_test="$test_outputs"+"/"+component+"/"+fic
	   print(file_test)
	   dn=os.path.dirname(file_ref)
	   bn=os.path.basename(file_ref)
	   compare_html_files(file_test, bn, dn, display_error=False,\
	                        replace="$ref_name", by="$test", allow_url_change=True)
	print()
EOF
python tmp.py
if [ $? -eq 0 ] ; then 
    echo 
    echo "--------------------------------------------------"
    echo "Comparison successful. Should clean test run cache"
    echo "--------------------------------------------------"
fi
