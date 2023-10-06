#!/bin/bash
#set -x

# Duplique le répertoire cesmep_lite/ d'une simulation, pour permettre
# de ré-exécuter la CESMEP, pas forcément par le même user, et en pouvant
# modifier le code CESMEP

# Pour ré-exécuter, on exécute simplement le script libIGCM_post.sh de la copie
# Pour l'instant, adapté et testé au TGCC

# Répertoire de la simulation (qui contient un rép cesmep_lite/)
source=${1:-/ccc/workflash/cont003/gen0826/fallettl/modipsl_20230802-1129_CESMEP/config/LMDZOR_v6/LMDZOR-DEVT-1Y-20230913}

# Répertoire ou installer la copie de cesemp_lite/ (un sous-répertoire
# JobName y sera créé)
target=${2:-~/work/debug_graphs}

# Répertoire des sources de CESMEP à utiliser et qu'on pourra
# modifier (Nota: certains des sources sont copiés plutôt que liés;
# il faut le prendre en compte quand on modifie)
cesmep=~/work/cesmep

# Compte à utiliser pour les jobs
account=gen0826

# Adresse mail pour les comptes-rendus (peut être None)
mail=None

# Répertoire racine pour les caches CliMAF. Un sous-rép dédié sera créé
cache_root=/ccc/scratch/cont003/gen0826/senesis

# Nom de la comparaison traitée par la simulation (pourrait être
# diagnostiqué automatiquement)
comparison=run_comparison


# Création d'un rép cesmep_lite
#------------------------------------------
jobname=$(basename $source)
mkdir -p $target/$jobname
$cesmep/install_lite.sh $target/$jobname $comparison with_libIGCM
cd $target/$jobname/cesmep_lite
mv $comparison ${jobname}_${comparison}
comparison=${jobname}_${comparison}
source=$source/cesmep_lite


# Copie des settings CESMEP inchangés depuis la simu d'origine
#-------------------------------------------------------------
cp $source/$comparison/libIGCM_fixed_settings.py $comparison
cp $source/$comparison/datasets_setup.py $comparison


# Copie des settings CESMEP à modifier
#-------------------------------------------------------------
cp $source/libIGCM_post.param .
#echo "In libIGCM_post.param : adapt root and cache"
read d comp DateBegin CesmepPeriod CesmepSlices cache comps rest < libIGCM_post.param
cache=$cache_root/cesmep_climaf_caches/$comparison
echo "$cesmep $comp $DateBegin $CesmepPeriod $CesmepSlices $cache $comps " > libIGCM_post.param

cp $source/settings.py .
#echo "In settings.py : adapt project and mail"
sed -i \
    -e "s/account *=.*/account = \"$account\"/" \
    -e "s/mail *=.*/mail = \"$mail\"/" \
    settings.py


# C'est tout
#---------------------------------------
echo "OK - you can now execute CESEMP with :"
echo "   $target/$jobname/cesmep_lite/libIGCM_post.sh <year_begin> <year_end>"
