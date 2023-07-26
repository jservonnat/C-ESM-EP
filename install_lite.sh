#!/bin/bash

# Proceed with a light install of C-ESM-EP, that saves on i-nodes, and
# on disk usage, by refering (through symbolic links and PYTHONPATH)
# to the code in current dir

#   - First argument: the directory that will host C-ESM-EP (in a subdir
#         called cesmep_lite)
#   - Second argument is the single comparison to install

#   - The C-ESM-EP code is aasumed to be located in this script's directory
#   - The comparison directory can be a subdir of this script dir or located
#       somewhere else; it is copied
#   - Sub-directories 'Documentation', 'tests', '.git' and file README.md
#       are not installed
#   - Sub-directory 'share' is symbolically linked (this saves a lot of i-nodes)
#   - a few other files are also symbolically linked,
#   - file setenv.sh is modified so that PYTHONPATH includes the dir of current code

#set -x

cesmep_dir=$(cd $(dirname $0) ; pwd)  # Dir of current code
[ -h $cesmep_dir/share ] && echo "Cannot work from a lite install" && exit 1

target=${1?} 
comparison=$2

target=$(cd $target ; pwd)
[ ! -d $target ] && \
    echo "$0 : Must provide an existing directory as first argument" && exit 1
target=$target/cesmep_lite
if [ -d $target ] ; then
    chmod -R 777 $target
    rm -fR $target
fi
mkdir -p $target

# Copy the comparison subdir
if [ -d $cesmep_dir/$comparison ] ; then
    comparison_dir=$cesmep_dir
elif [ -d $comparison ] ; then
    comparison=$(realname $comparison)
    comparison_dir=$(dirname $comparison)
    comparison=$(basename $comparison)
else
    echo "No access to C-ESM-EP comparison $comparison"
    exit 1
fi
(cd $comparison_dir ; tar -chf - --exclude=*.out --exclude=*~ --exclude=climaf.log \
     --exclude=job.in  --exclude=cesmep_atlas_style_css $comparison) | \
    (cd $target; tar -xf - )

# Link a few files at C-ESM-EP root level 
for file in share clean_out_error.sh libIGCM_clean.sh run_C-ESM-EP.py \
	    main_C-ESM-EP.py libIGCM_post.sh locations.py; do
     ln -sf $cesmep_dir/$file $target
 done

 # Copy only files that will or could be changed
 for fic in setenv_C-ESM-EP.sh  settings.py ; do 
     cp -f $cesmep_dir/$fic $target
 done

 # Add directory of current source in PYTHONPATH set by setenv.sh
 echo "export PYTHONPATH=\$PYTHONPATH:$cesmep_dir" >> $target/setenv_C-ESM-EP.sh
 echo "echo PYTHONPATH=\$PYTHONPATH" >> $target/setenv_C-ESM-EP.sh
