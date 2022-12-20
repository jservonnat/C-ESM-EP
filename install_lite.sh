#!/bin/bash

# Proceed with a light install of C-ESM-EP, that saves on i-nodes, and
# on disk usage, by refering (through symbolic links and PYTHONPATH)
# to the code in current dir

#   - First argument: the directory that will host C-ESM-EP (in a subdir
#         called cesmep_lite)
#   - Second argument is the single comparison to install

#   - The corresponding comparison sub-directory is copied (and not the other ones)
#   - Sub-directories 'Documentation', 'tests', '.git' and file README.md  are not installed
#   - Sub-directory 'share' is symbolically linked (this saves a lot of i-nodes)
#   - a few other files are also symbolically linked,
#   - make sure you add the current source code dir to PYTHONPATH when using
#       the target CESMEP light install

#set -x

o=$(cd $(dirname $0) ; pwd)  # Dir of current code
[ -h $o/share ] && echo "Cannot work from a lite install" && exit 1

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
[ ! -d $o/$comparison ] && echo "No access to $o/$comparison" && exit 1
(cd $o ; tar -chf - --exclude=*.out --exclude=*~ --exclude=climaf.log \
     --exclude=job.in  --exclude=cesmep_atlas_style_css $comparison) | \
    (cd $target; tar -xf - )

# Link a few files at C-ESM-EP root level 
 for file in share clean_out_error.sh libIGCM_clean.sh; do
     ln -sf $o/$file $target
 done

 # Copy only strictly necessary files (PYTHONPATH will help for the other ones)
 for fic in run_C-ESM-EP.py  setenv_C-ESM-EP.sh  settings.py \
 	    main_C-ESM-EP.py libIGCM_post.sh ; do    # pas PMP....
     cp -f $o/$fic $target
 done


