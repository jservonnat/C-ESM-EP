# -*- coding: iso-8859-1 -*-
# Created : S.Sénési - nov 2015

# 
desc="\nCreation d'un atlas pour une simu, une grille et une liste de variables et de saisons \n"+\
"  Exemples : \n"+\
"  >>> python ./atlas.py -v tas,hfls -s NPv3.1ada_1982_1991\n"+\
""
# Avec CliMAF, cette etape est loin d'etre necessaire; on la réalise pour 'exposer' ces fichiers
# dans une arborescence à laquelle sont habitues certains utilisateurs


# Répertoire de base pour les entrées et les résultats
dir_default='/data/hourdin/LMDZ6/SE/ORIG'

# Gestion des options et arguments d'appel
from optparse import OptionParser
parser = OptionParser(desc) ; parser.set_usage("%%prog [-h]\n%s" % desc)
parser.add_option("-i", "--input", help="repertoire des donnes d'entree(defaut : %s)"%dir_default, 
                  action="store",default=dir_default)
parser.add_option("-g", "--grid", help="nom de grille (default: VLR)", action="store",default='VLR')
parser.add_option("-r", "--region", help="nom de zone (default: GLOB)", action="store",default='GLOB')
parser.add_option("-p", "--season", help="saison a traiter " "(eg : JJA, DJF, YEAR, defaut=%YEAR)", 
                  action="store", default='YEAR')
parser.add_option("-s", "--simulation", help="simulation+annees a traiter (sim_YYY1_YYY2) - laisser vide pour lister",
                  action="store",default=None)
parser.add_option("-t", "--reference", help="simulation de reference (sim_YYY1_YYY2, default=LMDZ_OBS) ",
                  action="store",default='LMDZ_OBS')
parser.add_option("-v", "--variables", help="liste des variables (separees par des virgules)", action="store",default=None)
parser.add_option("-f", "--force", help="force le recalcul de champs existants", 
                  action="store_true",default=None)
parser.add_option("-o", "--pdf", help="nom du pdf de sortie (default: atlas_<SIMU>_<SAISON>.pdf)", action="store")
(opts, args) = parser.parse_args()

#opts.input
#opts.grid
#opts.region
#opts.season
#opts.simulation
#opts.reference
#opts.variables
#opts.force
#opts.pdf

#---------------------------------------------------------------------------------
import math
from climaf.api import *
from climaf.html import * 
# La description de l'organisation des données SE et des alias et rescalings 
# est partagée dans une micro-librairie :
from atlas_LMDZ_SE import * # svsg, all_SE_simulations
from plot_params import plot_params
#---------------------------------------------------------------------------------
#
#craz()
if opts.simulation is None:
    print "Available simulations at %s are : "%opts.input,
    for s in all_LMDZ_SE_simulations() : print s,
    exit(0)
#
# --> 
lvars=opts.variables
if lvars is not None : lvars=lvars.split(',')
else : lvars=variables_list
#
# Preparons une commande pour assembler les sorties Pdf
if opts.pdf : pdffile=opts.pdf
else: pdffile="atlas_"+opts.simulation+"_"+opts.season+".pdf"
pdfargs=["pdfjam","--landscape","-o ",pdffile]
#
# Initialisation de l'index html
index= header("LMDZ Atlas for "+opts.simulation+ " versus "+opts.reference+" ("+opts.season+")") 
index += cell('PDF',pdffile)
index += section("2d vars", level=4)
index += open_table()
#
# Titres de colonnes
ref=opts.reference ; 
if (ref == 'LMDZ_OBS' ) : text_diff='bias'
else:                text_diff='diff'
index+=open_line('VARIABLE')+cell('bias')+cell('rmse')+cell('mean')+cell(ref)+cell(text_diff)+\
        cell('zonal')+cell('all')+cell('pdf')+close_line()
#
# -- Declare the script ml2pl for vertical interpolation
cscript("ml2pl", "/home/jservon/Evaluation/CliMAF/Atlas_LMDz/ml2pl.sh -p ${var_2} -v ${var_1} ${in_1} ${out} ${in_2}",
    commuteWithTimeConcatenation=True, commuteWithSpaceConcatenation=True)
# -- Vertical levels for the vertical interpolation
fixed_fields("ml2pl",("press_levels.txt","/home/jservon/Evaluation/CliMAF/press_levels.txt"))
#
for variable  in lvars :
    # Get the model and the reference
    simu=svsg(opts.simulation,variable,opts.season,opts.grid)
    print 'variable = ',variable
    reff=svsg(opts.reference,variable,opts.season,opts.grid)
    #
    # If the variable is a 3D field:
    #  - interpolate the variable on the standard pressure levels with ml2pl (L. Guez)
    #  - Compute the difference model-ref with diff_zonmean (computes the zonal mean lat/pressure fields,
    #    interpolates the model on the ref, both vertically and horizontally, and returns the difference)
    if is3d(variable) :
       simu_pres = svsg(opts.simulation,'pres',opts.season,opts.grid)
       simu = ml2pl(simu,simu_pres)
       simu = zonmean(simu)
       reff = zonmean(reff)
       diff = diff_zonmean(simu,reff)
    else:
	if (opts.grid == '' ) : reff=regrid(reff,simu)
    	diff=minus(simu,reff)

    pparams = plot_params(variable,'full_field')
    vertical_interval = 'trYMaxF=1000|trYMinF=1'
    stringFontHeight=0.018
    if is3d(variable):
    	pparams.update({'options':vertical_interval})
        stringFontHeight=0.03
    # Map for simulation
    simu_fig=plot(simu,title="",
                  gsnLeftString=variable,
		  gsnCenterString=opts.simulation,
		  gsnRightString=opts.season,
		  gsnStringFontHeightF=stringFontHeight,
		  mpCenterLonF=0,
		  **pparams)
    simu_avg=cvalue(space_average(simu))
    #
    # Map for reference
    ref_fig=plot(reff,title="",
                 gsnLeftString=variable,
		 gsnCenterString=ref,
		 gsnRightString=opts.season,
		 gsnStringFontHeightF=stringFontHeight,
		 mpCenterLonF=0,
                 **pparams)
    ref_avg=cvalue(space_average(reff))
    #
    # Bias (or difference between simulations) map
    if (ref == 'LMDZ_OBS' ) : p=plot_params(variable,'bias')
    else:                p=plot_params(variable,'model_model')
    tmp_aux_params = plot_params(variable,'full_field')
    scale = 1.0 ; offset = 0.0
    if 'offset' in tmp_aux_params or 'scale' in tmp_aux_params:
       if 'offset' in tmp_aux_params:
          offset = tmp_aux_params['offset']
       else:
	  offset=0.0
       if 'scale' in tmp_aux_params:
          scale = tmp_aux_params['scale']
       else:
          scale=1.0
       wreff = apply_scale_offset(reff,scale,offset)
       wsimu = apply_scale_offset(simu,scale,offset)
    else:
       wreff = reff
       wsimu = simu
    #
    if is3d(variable):
    	p.update({'options':vertical_interval})
    if variable in ['ua','va','ta','hus']:
        tmp_levs = tmp_aux_params['colors']
        p.update({'contours':tmp_levs})
    	diff_fig=plot(diff,wreff,title="", format='png', mpCenterLonF=0,
    		  gsnLeftString=variable,
		  gsnCenterString=opts.simulation+' - '+ref,
		  gsnRightString=opts.season,
		  gsnStringFontHeightF=stringFontHeight,
                  aux_options='cnLineThicknessF=2|cnLineLabelsOn=True', **p)
    else:
        p.update({'contours':1})
        diff_fig=plot(diff,title="", format='png', mpCenterLonF=0,
                  gsnLeftString=variable,
                  gsnCenterString=opts.simulation+' - '+ref,
                  gsnRightString=opts.season,
                  gsnStringFontHeightF=stringFontHeight,
                  **p)

    #
    # Bias mean value, and RMSD/RMSE
    diff_avg=cvalue(space_average(diff))
    rmsd=math.sqrt(cvalue(space_average(ccdo(diff,operator='-b F64 sqr'))))
    #
    # Zonal means
    if not is3d(variable):
        # -- apply a mask corresponding to the reference
	mask = div(reff,reff)
	msimu = mul(wsimu,mask)
	# -- Compute the zonal mean
    	zmean=ccdo(msimu, operator='zonmean')
    	ref_zmean=ccdo(wreff, operator='zonmean')
    	#
    	sim=opts.simulation
    	zmean_fig=curves(cens([sim,ref],zmean,ref_zmean),
			 title="",
			 lgcols=3,
                         options=#'tiYAxisString=""|'+\
				 #'+\'+\
			 	 'tmYROn=True|'+\
			 	 'tmYRBorderOn=True|'+\
				 'tmYLOn=False|'+\
				 'tmYUseRight=True|'+\
				 'vpXF=0|'+\
				 'vpWidthF=0.66|'+\
				 'vpHeightF=0.33|'+\
				 'tmYRLabelsOn=True|'+\
				 'tmXBLabelFontHeightF=0.018|'+\
				 'tmYLLabelFontHeightF=0.016|'+\
				 'lgLabelFontHeightF=0.018|'+\
				 #'pmLegendSide=Bottom|'+\
				 'pmLegendOrthogonalPosF=-0.32|'+\
				 'pmLegendParallelPosF=1.0|'+\
				 'tmXMajorGrid=True|'+\
				 'tmYMajorGrid=True|'+\
				 'tmXMajorGridLineDashPattern=2|'+\
				 'tmYMajorGridLineDashPattern=2|'+\
				 'xyLineThicknessF=8|'+\
				 'gsnLeftString='+variable+'|'+\
				 'gsnCenterString='+opts.simulation+' vs '+ref+'|'+\
				 'gsnRightString='+opts.season+'|'+\
				 'gsnStringFontHeightF='+str(stringFontHeight))
    thumbnail_size = 200
    if is3d(variable):
	    index+=open_line(varlongname(variable)+' ('+variable+')')+\
        	    cell("%.2g"%diff_avg,cfile(diff_fig))+\
		    cell("%.2g"%rmsd,cfile(diff_fig))+\
		    cell(simu,cfile(simu_fig),thumbnail=thumbnail_size,hover=False)+\
		    cell(ref,cfile(ref_fig),thumbnail=thumbnail_size,hover=False)+\
		    cell(text_diff,cfile(diff_fig),thumbnail=thumbnail_size,hover=False)
    	    close_line()
    else:
	    index+=open_line(varlongname(variable)+' ('+variable+')')+\
        	    cell("%.2g"%diff_avg,cfile(diff_fig))+\
		    cell("%.2g"%rmsd,cfile(diff_fig))+\
		    cell(simu,cfile(simu_fig),thumbnail=thumbnail_size,hover=False)+\
		   cell(ref,cfile(ref_fig),thumbnail=thumbnail_size,hover=False)+\
		    cell(text_diff,cfile(diff_fig),thumbnail=thumbnail_size,hover=False)+\
		    cell('zonal mean',cfile(zmean_fig),thumbnail=thumbnail_size,hover=False)
    	    close_line()
#
# Finalisons l'index html
index += close_table()
index += trailer()
out="index_example.html"
with open(out,"w") as filout : filout.write(index)
#



#
import os,os.path ; 
print("Attendez un bon peu : lancemement de firefox sur Ciclad....")
os.system("firefox file://"+os.path.abspath(os.path.curdir)+"/"+out+"&")




# ---------------------------------------------------------------------------------------- #
# -- Finalize the index by replacing the paths to the cache for the paths
# -- to the alternate directory
# -- Here we can work either on Ciclad or at TGCC
# -- On Ciclad we feed directly the cache located on the dods server
# -- and point at this web address.
# -- At TGCC we need to:
# --   - feed the cache on $SCRATCHDIR (set in your environment) and make a hard link in a target directory
# --     (alt_dir_name, based on the current working directory and subdir)
# --   - at the end of the atlas, we copy the target directory (alt_dir_name) on the $WORKDIR
# --     (work_alt_dir_name) before copying it on the dods with dods_cp
# --   - Eventually, we dods_cp the directory work_alt_dir_name on the /ccc/work/cont003/dods/public space
index += trailer()
import os
if alt_dir_name :
    #
    if onCiclad:
       outfile=cachedir+"/"+index_name
       with open(outfile,"w") as filout : filout.write(index)
       print(' -- ')
       print(' -- ')
       print(' -- ')
       print("index actually written as : "+outfile)
       print("may be seen at "+root_url+outfile.replace(cachedir,alt_dir_name))
    #
    if atTGCC:
       # -- Ecriture du fichier html dans le repertoire sur scratch
       outfile=alt_dir_name+"/"+index_name
       with open(outfile,"w") as filout : filout.write(index)
       print("index actually written as : "+outfile)
       # -- Copie du repertoire de resultat du scratch vers le work (avant copie sur le dods)
       if os.path.isdir(work_alt_dir_name):
          os.system('rm -rf '+work_alt_dir_name)
       cmd1 = 'cp -r '+alt_dir_name+' '+work_alt_dir_name.replace('/'+subdir,'')
       print cmd1
       os.system(cmd1)

       # -- dods_cp du repertoire copie sur le work
       cmd12 = 'rm -rf /ccc/work/cont003/dods/public/'+getuser()+'/'+subdir
       print cmd12
       os.system(cmd12)
       cmd2 = 'dods_cp '+work_alt_dir_name+' /ccc/work/cont003/dods/public/'+getuser()+'/'
       print cmd2
       os.system(cmd2)
       print(' -- ')
       print(' -- ')
       print(' -- ')
       print('Index available at : dods.extra.cea.fr/work/'+getuser()+'/'+subdir+'/'+index_name)
    #
else :
    with open(index_name,"w") as filout : filout.write(index)
    print("The atlas is ready as %s"%index_name)


