=====================================================
Principes d'interfaçage de la C-ESM-EP à libIGCM :
=====================================================

S.Sénési - sept 2022

Principes:

   - le nouveau flag Cesmep de la section Post de config.card (donc la variable config_Post_Cesmep de libIGCM) commande la réalisation d'un atlas C-ESM-EP, il est à FALSE par défaut; un autre flag (CesmepComparison) indique la 'comparaison' C-ESM-EP à lancer (par défaut 'standard_comparison'); un 3° flag optionnel, CesmepCode, permet d'indiquer où prendre les sources C-ESM-EP (par défaut c'est dans un espace commun, sur ~igcmg (à terme :-)); un dernier flag, CesmepSlices, fixe le nombre de périodes temporelles que montre l'atlas

   - en pratique, l'atlas C-ESM-EP peut être lancé par l'un ou l'autre des scripts de post-traitement : create_se, create_ts, pack_output (dans leur dernière étape), et aussi directement par la fonction IGCM_post_Submit (cf infra). L'idée est de faire travailler l'atlas C-ESM-EP sur le dernier jeu disponible de celui des types de données post-traitées qui est le plus adapté ou efficace. Le choix parmi ces possibilités est piloté par la valeur du flag config_Post_Cesmep, que les scripts de post-traitement reçoivent (via libIGCM_post.ksh:IGCM_post_Submit). Pour l'instant, la logique de chaque script est simplement, par ex pour create_se : si le flag vaut SE, l'atlas est effectivement lancé par create_se (en fin du script). On peut implémenter une autre logique dans ces scripts, basée sur un jeu de valeurs du flag config_Post_Cesmep.

   - Le cas de lancement direct par la fonction IGCM_post_Submit est destiné à traiter les simulations TEST qui ne lancent aucun post-traitement (ni SE, ni TS, et, par construction, ni Pack ); l'atlas C-ESM-EP y est lancé (en fin de fonction) si le flag config_Post_Cesmep vaut AtEnd.

   - le paramètre Cesmep peut être fixé par l'utilisateur dans la config.card (section Post) selon , parmi les valeurs : FALSE, SE, TS, Pack, AtEnd, TRUE et <n>Y. S'il vaut TRUE ou <n>Y, un choix est fait (dans la fonction IGCM_config_CommonConfiguration), selon cet algorithme : si les SE sont activés, on retient SE, sinon, si les TS sont activés, on retient TS, sinon, si les Pack sont activés, on retient Pack, sinon on retient AtEnd. Un autre algorithme peut être envisagé. Un paramètre CesmepPeriod définissant la durée des périodes de l'atlas est calculé à partir de la valeur de <n>Y, à défaut du paramètre Frequency associé au type de sorties choisies (e.g. TimeSeriesFrequency)

   - la réalisation d'un atlas respecte l'organisation pré-existante de C-ESM-EP : un répertoire dédié héberge des codes C-ESM-EP et un sous-répertoire pour la 'comparaison' à réaliser (qui comporte lui-même des répertoires de 'composantes'); l'utilisateur a la main sur ce répertoire pour pouvoir y modifier avant le run divers paramètres dans des fichiers python, voire même y ajouter du code; par contre, on évite au maximum de dupliquer ceux des fichiers de code C-ESM-EP qui n'ont pas (ou ont peu) vocation à être modifiés par l'utilisateur (ex : répertoire 'share'); ce, en usant du PYTHONPATH ou de liens symboliques pour y accéder 

   - à l'install du job de la simulation (à la fin de ins_job), si on tourne sur Irene, Rome, Jean Zay ou Spirit, une commande invoque un script de C-ESM-EP (libIGCM_install.sh) qui réalise plusieurs opérations :
     * il installe dans $SUBMIT_DIR/cesmep_lite une copie légère des sources C-ESM-EP indiqués par config_Post_CesmepCode; il y crée un répertoire de comparaison basé sur celle demandée par le paramètre CesmepComparison de la config.card mais de nom préfixé par le nom de job
     * il décide de la liste des 'components' de la comparaison, sur la base de la liste ds composantes physiques activées dans la simulation, et de le liste des répertoires de components dasn la comparaison
     * il crée dans cesmep_lite/ un fichier de manœuvre (libIGCM_post.param) consignant le répertoire d'origine du code Cesmep, le nom de comparaison, la date de début de la simulation, la valeur des paramètres CesmepPeriod et CesmepSlices, le nom du répertoire de cache CliMAF à utiliser, et la liste des 'components'
     * il crée et renseigne le fichier libIGCM_fixed_settings.py, lequel sert à décrire le dataset de type IGCM_Out représentant le dernier jeu de données de la simulation;
     * il particularise le fichier C-ESM-EP datasets_setup.py de la comparaison pour qu'il utilise (en l'important) le fichier libIGCM_settings.py
     * il crée le fichier C-ESM-EP settings.py, pour le nom de projet fournissant les ressources, et le mail à utiliser (tels que connus de libIGCM)

   - avant le run, l'utilisateur peut modifier le contenu de $SUBMIT_DIR/cesmep_lite, et en particulier enrichir le fichier datasets_setup.py; il peut aussi particulariser les fichiers 'params' des composantes;

   - lors du run, le script de post-traitement activé (ou, pour de cas d'une simu TEST, la fonction IGCM_post_Submit) invoque le script C-ESM-EP libIGCM_post.sh en lui indiquant la période traitée; ce dernier script complète le fichier libIGCM_fixed_settings.py pour créer le fichier libIGCM_settings.py, en y ajoutant ce qui concerne la période disponible, et invoque le script principal de C-ESM-EP, run_C-ESM-EP.py (dont l'output est envoyé dans cesmep_lite/libIGCM_post.out); le fonctionnement de la C-ESM-EP est standard : ce script lance des jobs d'atlas C-ESM-EP, ces atlas sont créés à l'emplacement habituel (piloté par locations.py), et les outputs dans les répertoires de composantes. Le script libIGCM_post.sh est modifiable par l'utilisateur

   - pour le nettoyage des sorties de la C-ESM-EP, l'option est que purge_simuation.job et clean_Period.job suppriment tant les atlas (présents au TGCC et à l'IDRIS sur workdir et espace thredds) que le cache CliMAF dédié; ceci sous le contrôle d'une confirmation (globale) par l'utilisateur de ces scripts de nettoyage. Supprimer le cache permet de traiter le cas où des sorties de modèle erronées ont été utilisées, puis rectifiées.

   - les ajouts aux sources C-ESM-EP sont :
        * install_lite.sh    : copie ou linke les sources C-ESM-EP de référence dans $SUBMIT_DIR (ou ailleurs)
        * libIGCM_install.sh : invoque install_lite.sh, crée le fichier libIGCM_settings.py et datasets_setup.py, décide des composantes
        * libIGCM_post.sh    : complète le fichier libIGCM_settings.py et lance run_C-ESM-EP.py
        * libIGCM_datasets.py: modèle de datasets_setup.py, qui importe libIGCM_settings.py
	* libIGCM_clean.sh   : détruit les répertoires d'atlas et le cache CliMAF dédié

   - les fichiers de source python de la C-ESM-EP qui ne sont pas copiés (mais importés via PYTHONPATH) sont : locations.py, custom_obs_dict.py, custom_plot_params.py, cesmep_simu_finder.py, set_available_period_ts_clim.py ; pour utiliser une version modifiée, il faut la localiser dans le répertoire cesmep_lite.

   - les sources libIGCM impliqués sont : AA_create_se, AA_create_ts, AA_pack_ouput, AA_purge_simulation, AA_clean_Period, ins_job, libIGCM_config.ksh et libIGCM_post.ksh


