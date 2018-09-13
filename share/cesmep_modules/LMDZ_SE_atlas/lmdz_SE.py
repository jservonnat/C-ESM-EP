# -*- coding: iso-8859-1 -*-
# Created : S.Sénési - nov 2015

""" 
Base pour le traitement des données SE de LMDZ : 
  - variables, saisons et grilles habituellement gérées, 
  - organisation des données LMDZ_SE
  - renommage et re-scaling des variables
  - dictionnaire de fichiers d'exemples pour les grilles traitées
et une fonction pour rendre un objet CliMAF pour tuple (simu, variable, saison, grille)
"""

from climaf.api import *

# Liste des variables LMDZ objet d'une cmorisation ou d'une projection+moyenne saisonniere
#########################################################################################
variables_list=['sfcWind','hfls','hfss','huss','hurs','pr',\
    'rldscs','rlds','rlus','rsdscs','rsds','rsuscs','rsus','rsutcs','rsut','rlut','rlutcs','rsdt',\
    'sfcWind','tas','ts','tauu','tauv','psl','zg500','hfns','ta','ua','va','wap','hus','hur',\
    'cllcalipso','clmcalipso','clhcalipso','cltcalipso','clt']

#Dictionnaire des grilles connues et de fichiers d'exemple
#########################################################################################
grid_remapfiles={ 'VLR' : '/data/ssenesi/stable/VLR.nc'}

# Saisons gérées et leur traduction CDO
#########################################################################################
seasons={ 'YEAR':"", 'DJF' : "selmon,1,2,12", 'JJA' : "selmon,6,7,8" , 'JJAS' : "selmon,6,7,8,9" }



#########################################################################################
# Definitions pour l'acces aux obs gérées par Ionela
#########################################################################################
cproject('LMDZ_OBS', ('period','fx'), ('simulation','refproduct'), ('product','LMDZ_OBS'), ('root','/prodigfs/ipslfs/dods/fabric/lmdz/SE/CMOR/OBS'))
#cproject('LMDZ_OBS', ('period','fx'),  ('root','/data/hourdin/LMDZ6/SE/CMOR/OBS'))  #, '/data/musat/LMDZ6/SE/CMOR/OBS'))
dataloc(project='LMDZ_OBS',url='${root}/${variable}.nc')
# Définiton de variables dérivées pour ce projet
calias('LMDZ_OBS','psl', scale = 100)

#########################################################################################
# Définition logique des donnees de type 'LMDZ_SE' de l'IPSL, et de leur localisation
# La periode n'est pas traitee comme un objet 'period' de CliMAF, mais comme une chaine 
# de caracteres dont le nom de facette est 'years'

# Le nommage des données découvert chez F.Hourdin est traité. On utilise la facette 'root' 
# pour indiquer le répertoire de base
# Les re-scaling habituels sont decrits a l'aide de la fonction calias
# Les variables dérivées sont décrites aussi
#########################################################################################

#cproject('LMDZ_SE', 
#         ('frequency','seasonal'), 
#         ('period','fx'), 
#         'years',
#         ('root','/data/hourdin/LMDZ6/SE/ORIG'), 
#         separator='|')
cproject('LMDZ_SE',
         ('frequency','seasonal'),
         ('period','fx'),
         ('model','LMDZ6'),
         'years',
         ('root','/prodigfs/ipslfs/dods/fabric/lmdz/SE/ORIG'),
         separator='|')

#exemple de nom de fichier : NPv3.1ada_LMDZ_SE_1982_1991_1M_histmthCOSP.nc
pattern='${root}/${simulation}_SE_${years}_1M_histmth*.nc'
dataloc(project='LMDZ_SE',url=pattern, organization='generic')
    
    
calias('LMDZ_SE','hfls','flat',scale=-1.)
calias('LMDZ_SE','hfss','sens',scale=-1.)
calias('LMDZ_SE','pr','precip')
calias('LMDZ_SE','sfcWind','wind10m')
calias('LMDZ_SE','rldscs','LWdnSFCclr')
calias('LMDZ_SE','rlds','LWdnSFC')
calias('LMDZ_SE','rlus','LWupSFC')
calias('LMDZ_SE','rsdscs','SWdnSFCclr')
calias('LMDZ_SE','rsds','SWdnSFC')
calias('LMDZ_SE','rsuscs','SWupSFCclr')
calias('LMDZ_SE','rsus','SWupSFC')
calias('LMDZ_SE','rsutcs','SWupTOAclr')
calias('LMDZ_SE','rsut','SWupTOA')
calias('LMDZ_SE','rsdt','SWdnTOA')
calias('LMDZ_SE','rlut','topl')
calias('LMDZ_SE','rlutcs','topl0')
calias('LMDZ_SE','sfcWind','wind10m')
calias('LMDZ_SE','tas','t2m')
calias('LMDZ_SE','ts','tsol')
calias('LMDZ_SE','huss','q2m')
calias('LMDZ_SE','hurs','rh2m')
calias('LMDZ_SE','tauu','taux_oce')
calias('LMDZ_SE','tauv','tauy_oce')
calias('LMDZ_SE','psl','slp')
calias('LMDZ_SE','zg500','z500')

calias('LMDZ_SE','ta','temp')
calias('LMDZ_SE','ua','vitu')
calias('LMDZ_SE','va','vitv')
calias('LMDZ_SE','wap','vitw')
calias('LMDZ_SE','hus','ovap')
calias('LMDZ_SE','hur','rhum')
calias('LMDZ_SE','clt','cldt',scale=100.)
calias('LMDZ_SE','cltcalipso', scale=100.)
calias('LMDZ_SE','clhcalipso', scale=100.)
calias('LMDZ_SE','clmcalipso', scale=100.)
calias('LMDZ_SE','cllcalipso', scale=100.)


def all_LMDZ_SE_simulations():
    """
    Listage de toutes les simulations du projet par listage de leurs 
    fichiers de données et décodage de leur nom
    
    Il faudrait quelque chose de moins adhoc ...
    """
    import re
    simus=[]
    # Listage des fichiers de donnees
    a=ds(project='LMDZ_SE',years="*", simulation='*', variable='*')
    for f in a.baseFiles().split(' ') : 
        basename=f.split('/')[-1].replace('_LMDZ_SE','')
        basename=re.sub(r'_1M_histmth.*.nc','',basename)
        if basename not in simus  : simus.append(basename)
    return simus


def svsg(simulation,variable,season='YEAR',grid='',root='/data/hourdin/LMDZ6/LMDZ_SE/ORIG'):
    """
    Rend l'objet CliMAF pour une variable d'une simulation, pour les  données 
    - LMDZ_SE d'un intervalle d'annéees (forme YYY1_YYY2)
    - ou LMDZ_OBS 
    et une saison et une grille

    (Le nom de la fonction est la concaténation des intiales des arguments)

    Exemples : 
    >>> svsg('NPv3.1ada','1982_1991','hurs')
    >>> svsg(simulation='NPv3.1ada',years='1982_1991',variable='hurs',season='DJF, grid='')
    >>> svsg('LMDZ_OBS','','hurs','JJA')

    Il faut au préalable avoir déclaré les projets 'LMDZ_SE' et 'LMDZ_OBS'
    """
    if simulation != 'LMDZ_OBS' :
        # Il faut identifier les annees dans le nom de la simu
        yeardeb=simulation.split('_')[1]
        yearfin=simulation.split('_')[2]
        years=yeardeb+"_"+yearfin
        simulation=simulation.split('_')[0]
        data=ds(project='LMDZ_SE',variable=variable,years=years, simulation=simulation)
    else:
        data=ds(project='OBS',variable=variable)
    if season != 'YEAR' : 
        seas=ccdo(data,operator=seasons[season])
    else : 
        seas=time_average(data)
    rds=seas
    if grid != '' : 
        if grid not in grid_remapfiles : 
            print "La grille %s n'est pas connue"%options.grid ; 
            return None
        rds=regrid(seas,fds(grid_remapfiles[grid],period='fx'))
    return rds

def bias_SE(simu,variable,season='YEAR',grid='',root='/data/hourdin/LMDZ6/SE/ORIG') :
    """
    Calcule le biais pour une variable d'une simu, vs 'LMDZ_OBS'
    Rend -999. en cas de probleme
    """
    try :
        sim=svsg(simu ,variable,season,grid,root)
        ref=svsg('LMDZ_OBS',variable,season,grid)
        if (grid == '' ) : ref=regrid(ref,sim)
        dif=minus(sim,ref)
        return cvalue(space_average(dif))
    except :
        return -999.

def is3d(variable) :
    if variable in ['ta','ua','va','hus','hur','wap','cl','clw','cli','mc','tro3','vitu', 'vitv', 'vitw','geop','temp'] :
        return True
    return False


