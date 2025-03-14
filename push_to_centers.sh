#!/bin/bash
# Push a version of C-ESM-EP to reference locations at TGCC, IDRIS and
# Spirit, along with an information file (named 'versions')

# On spirit, the version is added besides the former ones, in a
# directory named by the version, and accessible by a symbolic link
# 'cesmep_for_libIGCM,
# On other centers, the pushed version replaces the former one
# This can be changed, see variable 'locations' below

# The version to push is identified by a git branch, tag or commit
# provided as first argument
version=${1?Please provide a C-ESM-EP version tag}

# The repository used is the one in current directory, except
# if it is provided as second argument
if [ -z $2 ] ; then
    remote_repo=""
else
    remote_repo="--remote=$2"
fi

# The target locations are :
locations="
    senesis@irene-fr.ccc.cea.fr:/ccc/cont003/home/igcmg/igcmg/Tools/cesmep
    upe47jz@jean-zay.idris.fr:/gpfswork/rech/psl/commun/Tools/cesmep
    ssenesi@spirit2.ipsl.fr:/net/nfs/tools/Users/SU/jservon/cesmep_installs/$version
    "

olocations="
    upe47jz@jean-zay.idris.fr:/gpfswork/rech/psl/upe47jz/cesmep_for_test
    "

set -e
tarfile=$(mktemp cesmep_archive.$version.XXXX.tar)
git archive $remote_repo -o $tarfile --format=tar $version
commit=$(cat $tarfile | git get-tar-commit-id)
for loc in $locations; do
    machine=${loc%:*}
    dir=${loc#*:}
    echo "Pushing to $machine"
    cat $tarfile | \
	ssh $machine "(mkdir -p $dir; cd $dir; tar -xf - ; echo $version $commit $(date) >> versions)" \
	    2> >(grep -v key_.*_blob >&2)
    if [[ $machine = *spirit* ]] ; then
	ssh $machine "cd $dir/..; rm cesmep_for_libIGCM; ln -sf $version cesmep_for_libIGCM" \
	    2> >(grep -v key_.*_blob >&2)
    fi
done
rm $tarfile
    
