#!/usr/bin/env Rscript
## PARALLEL COORDINATES WITH R
## Contact: jerome.servonnat@lsce.ipsl.fr
## Started at PCMDI, 09-2016, finished at IPSL 04-2017
## -----------------------------------------------------


#parallel_coordinates_pmp_parser.py --line_widths 5,5,5 --statistic bias_xy --season ann --reference_data_path /data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-historical/03Nov2016 --test_data_path /data/jservon/PMP_OUT/metrics_results/2017-02-13/raw/IGCM_OUT_fabric_IPSLCM6_experiment_not_defined_CM605-LR-piCtrl-01_2330_2339_LMDZ_PCMDI --customname CM605-LR-piCtrl-01 --colors orangered,green,navy --highlights IPSL-CM5A-LR,CNRM-CM5,CM605-LR-piCtrl-01 --sort True --figname bias_parallel_coordinates.png --region global


#Rscript parallel_coordinates.R --test_data_path /data/jservon/PMP_OUT/metrics_results/2017-02-13/raw/IGCM_OUT_fabric_IPSLCM6_experiment_not_defined_CM605-LR-piCtrl-01_2330_2339_LMDZ_PCMDI --reference_data_path /data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-historical/03Nov2016 --statistic bias_xy --region TROPICS

# -- Rajouter:
#  1. Highlights : ok; manque affichage uniquement des highlights= Ok
#  2. Tri des colonnes pour une simu ref = OK
#  3. Affichage bias = OK
#  4. Utilisation des customnames pour les simus tests / passer plusieurs simus tests
#  5. Utilisation des customcolors = OK

#options(show.error.locations = TRUE)
options(error=traceback)


# -- Command line options
# ---------------------------------------------------------------------------------------------------------
library(optparse)

option_list = list(
  make_option(c("--reference_data_path"), type="character", default=NULL,
              help="Path to the reference data", metavar="character"),
  make_option(c("--test_data_path"), type="character", default="",
              help="Path to the test data (separated with , if you want to provide multiple tests)", metavar="character"),
  make_option(c("--customnames"), type="character", default=NULL,
              help="Customnames that will be used in the plot (same order as the tests)", metavar="character"),
  make_option(c("--highlights"), type="character", default=NULL,
              help="Numerical experiments that will be highlighted (the others are in grey in the background)", metavar="character"),
  make_option(c("--colors"), type="character", default=NULL,
              help="Colors (same order as the tests)", metavar="character"),
  make_option(c("--figname"), type="character", default="out.png",
              help="Name of the figure (.png)", metavar="character"),
  make_option(c("--reference"), type="character", default="defaultReference", help="Reference used to comute the metric",
              metavar="character"),
  make_option(c("-s","--statistic"), type="character", default="rms_xyt",
              help="Statistic", metavar="character"),
  make_option(c("--region"), type="character", default="global", help="Region", metavar="character"),
  make_option(c("--season"), type="character", default="ann", help="Season", metavar="character"),
  make_option(c("--sort"), type="character", default="TRUE", help="Sort the columns with the first experiment of the highlights list", metavar="character"),
  make_option(c("--highlights_only"), type="character", default="FALSE", help="Specify if you want to see only the highlighted models in the legend (TRUE or FALSE)", metavar="character"),
  make_option(c("--lwd_background"), type="character", default="2", help="Line Width for background", metavar="character"),
  make_option(c("--lwd_highlights"), type="character", default="6", help="Line Width for highlighted experiments", metavar="character"),
  make_option(c("--image_size"), type="character", default=NULL, help="Size of the PNG image width*height (ex: 1000*600)", metavar="character"),
  make_option(c("--legend_ratio"), type="character", default=NULL, help="Ratio of the width of the image used for the legend", metavar="character")

); 

# -- Read the arguments
opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

for (i in 1:length(opt)){
     arg = names(opt)[i]
     print(paste("Argument",arg,"="))
     print(opt[[arg]])
}


# -- Get the values of the arguments
# ---------------------------------------------------------------------------------------------------------

reference = opt$reference
region    = opt$region
statistic = opt$statistic
season    = opt$season
highlights = opt$highlights
highlights_only = opt$highlights_only
lwd_background = opt$lwd_background
lwd_highlights = opt$lwd_highlights
colors = opt$colors
image_size = opt$image_size
figname = opt$figname
legend_ratio = opt$legend_ratio
customnames = opt$customnames
sort = opt$sort


# -- Function to get the metrics results from a json file
# ---------------------------------------------------------------------------------------------------------
getValuesFromJsonFile = function(json_file, reference='defaultReference', statistic='rms_xyt',
                                 region='global', season='ann', customname=NULL){
  res_matrix = c()
  library(rjson)
  json_data = fromJSON(file=json_file)
  var = json_data$Variable
  if (var$id=='ua' | var$id=='va' | var$id=='ta' | var$id=='hur' | var$id=='hus' | var$id=='zg'){
     variable = paste(var$id,'_',as.character(var$level/100),sep='')
  }else if (var$id=='to' | var$id=='so' | var$id=='thetao'){
     variable = paste(var$id,'_',as.character(var$level),sep='')
  }else{
     variable = var$id
  }
  if (json_data$json_version==3){
     for (model in names(json_data$RESULTS)){
       for (sim in names(json_data$RESULTS[[model]][[reference]])){
          if (sim!='source'){
             if (length(names(json_data$RESULTS))>1){
                name = model
             }else{
                name = sim
                if (is.null(customname)==FALSE){name = customname}
             }
             res = json_data$RESULTS[[model]][[reference]][[sim]][[region]][[statistic]][[season]]
             res_row = c(name, variable, res)
             res_matrix = rbind(res_matrix, res_row)
          }# end if sim
       }#end for sim
     }#end for model
  }#end json_version==3

  return(res_matrix)

}



# -- Retrieve the results from the json files
# ---------------------------------------------------------------------------------------------------------
RES = c()

print("Reference files = ")
reference_data_path = opt$reference_data_path
print(reference_data_path)
reference_files = dir(path=reference_data_path, pattern="*.json$")

# -- Get the results in the reference files
for (reference_file in reference_files){
  json_file = paste(reference_data_path,reference_file,sep='/')
  RES = rbind( RES, getValuesFromJsonFile(json_file, reference=reference,
                                          region=region, statistic=statistic, season=season))
}#end for reference_file

if (dim(RES)[2]==2){print(paste("The requested metric is not available in",reference_data_path))}

# -- Get the results from the test files
print("Test files = ")
test_data_paths = strsplit(opt$test_data_path,',')[[1]]
print(test_data_paths)
if (is.null(customnames)==FALSE){
  customnames = strsplit(customnames,',')[[1]]
}#
for (test_data_path in test_data_paths){
  test_files = dir(path=test_data_path, pattern="*.json$")
  print(test_files)
  if (is.null(customnames)==FALSE){
     customname = customnames[which(test_data_paths==test_data_path)]
  }else{ customname=NULL }

  # -- Get the variable
  for (test_file in test_files){
    json_file = paste(test_data_path,test_file,sep='/')
    RES = rbind( RES, getValuesFromJsonFile(json_file, reference=reference,
                                            region=region, statistic=statistic, season=season, customname=customname) )
  }#end for test_file
  
  if (dim(RES)[2]==2){print(paste("The requested metric is not available in",test_data_path))}
}#

# -- Reshape the matrix :
# --   - columns = variables
# --   - rows = simulations
# ---------------------------------------------------------------------------------------------------------
reshaped_RES = c()
variables = unique(RES[,2])
simnames = sort(unique(RES[,1]))
for (variable in variables){
   dumresvar = c()
   for (simname in sort(simnames)){
      ind = which(RES[,2]==variable & RES[,1]==simname)
      if (length(ind)>1){print("WARNING !!!!!!!!"); print(ind) ; print(simname); break()}
      if (length(ind)==0){
         dumres = NA
      }else{
         dumres = as.numeric(RES[ind,3])
      }#
      dumresvar = c(dumresvar, dumres)
   }#end for elt
   reshaped_RES = cbind(reshaped_RES,dumresvar)
}



# -- Reorder the simulations = highlighted simulations at the end
# ---------------------------------------------------------------------------------------------------------
if (is.null(highlights)==FALSE){
  avail_highlights = c()
  highlights = strsplit(highlights,',')[[1]]
  reordered_simnames = c()
  tmp_HL_sims = c()
   # We select the highlighted numerical experiments
   for (HL_sim in highlights){
       indsim = which(simnames==HL_sim)
       if (length(indsim)>0){
           tmp_HL_sims = rbind(tmp_HL_sims, reshaped_RES[indsim,])
           reordered_simnames = c(reordered_simnames, HL_sim)
           avail_highlights = c()
       }
   }#
   # And we add the other ones
   for (indsim in 1:nrow(reshaped_RES)){
       if (is.element(simnames[indsim], highlights)==FALSE){
          tmp_HL_sims = rbind(reshaped_RES[indsim,], tmp_HL_sims)
          reordered_simnames = c(simnames[indsim], reordered_simnames)
       }#
   }#

reshaped_RES = tmp_HL_sims
simnames = reordered_simnames

}#end if


# -- Buidling the parallel coordinates and (most important) the scaling and the axes 
# ---------------------------------------------------------------------------------------------------------

# -- Typical number of ticks on a vertical axis (can be upt to spacing + 3)
spacing = 10

# -- Set the optimal spacings between the ticks of the vertical axes
maxfactor = 20
minscale = 0.0000000000001
dum = c(1,2,5)
spacingscale = c()
for (factor in 0:maxfactor){
     spacingscale = c(spacingscale, dum*minscale*10^factor)
}

# -- The 'axes' list will receive the scaled vertical axes:
# --> axes[[metric]]$newaxis is the values of the vertical axis on the 'true' range of values
# --> valnewaxis is the vector of values of the ticks on the [0,1] range (scaled)
axes = list()

# ----->
# -- Loop on the metrix to scale them on a [0,1] range of values and build nice vertical axes
# ----->

scaledat = reshaped_RES
nmetrix = ncol(reshaped_RES)
nsim = nrow(reshaped_RES)
ok_variables = c()
ok_scaledat = c()
ok_ind = 1
for (metric in 1:length(variables)){
     print("variable")
     print(variables[metric])
     # -- Working on one metric (or one metriciable)
     metricdat = reshaped_RES[,metric]
     # -- Min and max of the values
     minmetric = min(metricdat, na.rm=TRUE)
     maxmetric = max(metricdat, na.rm=TRUE)
     #
     if (minmetric!=maxmetric){
       # -- Si on travaille sur des valeurs de biais, on veut la ligne de zeros horizontale au milieu du plot
       if (grepl('bias',statistic)){
          dummax = max(c(abs(minmetric),abs(maxmetric)))
          minmetric = -dummax
          maxmetric = dummax
       }#
       print(paste("We work on variable",variables[metric]))
       ok_variables = c(ok_variables, variables[metric])
       # -- Create a new axis: find the correct spacing and range of values
       # -> We first seek for the value withing spacingscale (the optimal spacing values)
       #    that is the closest to the actual 'true' spacing (range of values / number of ticks - 1)
       tmpspacescale = ( maxmetric - minmetric ) / spacing
       dumspacingscale = spacingscale[ abs(spacingscale-tmpspacescale) == min(abs(spacingscale-tmpspacescale)) ]
       # -- Then, we create a vector of values separated by 'dumspacingscale'
       if (minmetric>(-1) & minmetric<0){
          startval = -1
       #}else if(minmetric>0 & minmetric<1) {
       #   startval = 0
       }else{
          #startval = round(minmetric,0)
          startval = trunc(minmetric,0)
       }#
       values = seq(startval,maxmetric,dumspacingscale)
       if (grepl('bias',statistic)){
          posvalues = seq(0,maxmetric,dumspacingscale)
          values = c(posvalues[length(posvalues):1],posvalues)
       }#
       # -- We extract the range of values that cover the range of values of the metric
       minaxeval = values[abs(values - minmetric)==min(abs(values - minmetric))]
       maxaxeval = values[abs(values - maxmetric)==min(abs(values - maxmetric))]
       if (grepl('bias',statistic)){
          dummax = max(c(abs(minaxeval),abs(maxaxeval)))
          minaxeval = -dummax
          maxaxeval = dummax
       }#       
       newaxis = values[values>=(minaxeval-dumspacingscale) & values<=(maxaxeval+dumspacingscale)]
       # ... and complete the axis if needed (at both ends)
       while (newaxis[1]>minmetric){ newaxis = c(newaxis[1]-dumspacingscale, newaxis) }
       while (newaxis[length(newaxis)]<maxmetric){ newaxis = c(newaxis, newaxis[length(newaxis)]+dumspacingscale) }
       #
       # -- Scaling of the axis
       # -- We put the minimum value to zero (offset)
       offset = newaxis[1]
       zerometric = metricdat - offset
       # -- And put the max to 1 (scale)
       scale = newaxis[length(newaxis)] - offset
       scalemetric = zerometric / scale
       scaledat[,metric] = scalemetric
       ok_scaledat = cbind(ok_scaledat, scalemetric)
       # -- On trouve les valeurs que va prendre le newaxis dans l'axe 0:1
       valnewaxis = (newaxis - offset) / scale
       axes[[variables[metric]]][["newaxis"]]    = newaxis
       axes[[variables[metric]]][["valnewaxis"]] = valnewaxis
       ok_ind = ok_ind+1
     }#
}#end for metric



# -- Impose a minimum percentage of available results for display (otherwise remove the variable)
# ---------------------------------------------------------------------------------------------------------
ind_percentage_variables = c()
nsim = nrow(ok_scaledat)
thres_avail_res = 50
for (i in 1:ncol(ok_scaledat)){
    nsim_ok = length(which(is.na(ok_scaledat[,i])==FALSE))
    if ((nsim_ok/nsim)>(thres_avail_res/100)){
       ind_percentage_variables = c(ind_percentage_variables, i)
    }#
}#end for
ok_variables = ok_variables[ind_percentage_variables]
ok_scaledat = ok_scaledat[,ind_percentage_variables]


# -- Impose that all highlights are available
# ---------------------------------------------------------------------------------------------------------
if (0){
# -- Imposer que les highlights soient tous dispos
ind_okhl_variables = c()
ind_highlights = simnames %in% highlights
for (i in 1:ncol(ok_scaledat)){
    res_highlights = ok_scaledat[ind_highlights,i]
    if ( length(which(is.na(res_highlights)==FALSE))==length(res_highlights) ){
       ind_okhl_variables = c(ind_okhl_variables, i)
    }#end if
}#end for
ok_variables = ok_variables[ind_okhl_variables]
ok_scaledat = ok_scaledat[,ind_okhl_variables]
}

# -- Check that all simulations still have results (particularly the highlights)
# ---------------------------------------------------------------------------------------
ok_simnames = c()
ok_res = c()
ok_highlights = c()
for (i in 1:nrow(ok_scaledat)){
  simname = simnames[i]
  res_sim = ok_scaledat[i,]
  if (length(is.na(res_sim)==FALSE)>0){
     # -- Keep only the sim names that have values
     ok_simnames = c(ok_simnames, simname)
     ok_res = rbind(ok_res, res_sim)
     if (simname %in% highlights){
        ok_highlights = c(ok_highlights, simname)
     }#end if
  }#end if
}#end for i
simnames = ok_simnames
ok_scaledat = ok_res



# -- Sort the columns ascending order (as a function of the position of the ref. simulation on the axis)
# ---------------------------------------------------------------------------------------------------------
if (sort=="TRUE"){
   refsim = ok_highlights[1]
   indrefsim = which(simnames==refsim)
   sorted = order(ok_scaledat[indrefsim,])
   sorted_scaledat=ok_scaledat[,sorted]
   sorted_variables = ok_variables[sorted]

   ok_scaledat = sorted_scaledat
   ok_variables = sorted_variables   
}

# On veut que les couleurs attribuees a une simu ne changent pas d'un plot a l'autre
# --> On construit la palette sur 'highlights', on affiche seulement ce qui manque


missing_variables = paste(subset(variables, !(variables %in% ok_variables)), collapse=', ')


scaledat = ok_scaledat

# -- Graphical parameter
# ---------------------------------------------------------------------------------------------------------
lwd=3
type="b"
CORREL2=colorRampPalette(c("black","gray80","darkturquoise","navyblue","blue","skyblue","green","yellow","red","darkred","deeppink"),space = "Lab")
CORREL2=colorRampPalette(c("navyblue","blue","skyblue","green","yellow","red"),space = "Lab")
palcolors = CORREL2(nsim)
SHADES = colorRampPalette(c("black","gray60"),space = "Lab")

# -- Highlighting the selected simulations
if (is.null(highlights)==FALSE){
  HL_colors = CORREL2(length(highlights))
  # -- If we provided some colors for the highlighted simulations, we use them
  if (is.null(colors)==FALSE){
     colors = strsplit(colors,',')[[1]]
     HL_colors[1:length(colors)] = colors
  }#
  
  ok_HL_colors = colors[highlights %in% ok_highlights]
  w_colors = c(rep('gray70',length(simnames)-length(ok_highlights)), ok_HL_colors)
  lwds = c(rep(lwd_background,length(simnames)-length(ok_highlights)), rep(lwd_highlights, length(ok_highlights)))
}#end if

colors=w_colors

# ----------------- #
# -- DO THE PLOT -- #
# ----------------- #

# -- Name of the image ------------------------------------------------------------------
if (is.null(figname)){
   figname = paste(statistic,season,region,"parallel_coordinates_with_R.png",sep='_')
}

# -- Multiplot layout (Left panel for the plot and right panel for the legend) ----------
if (highlights_only=="TRUE"){
  width=1000
  height=600
  layout_width = c(2,0.8)
}else{
  width=1300
  height=600
  layout_width = c(2,1.5)
}#
if (is.null(image_size)==FALSE) {
  dum = strsplit(image_size, '*')[[1]]
  width = dum[1]
  height = dum[2]
}#
if (is.null(legend_ratio)==FALSE) {
  dum = as.numeric(legend_ratio)
  layout_width = c((1/dum - 1), 1)
}#

# -- Start the plot device
png(figname, width=width, height=height)
layout(matrix(1:2,1,2), width=layout_width)


# -- Setup margins
lower_margin=7
par(mar=c(lower_margin,5,7,0))

# -- Start the plot with the first simulation...
plot(1:ncol(scaledat),scaledat[1,],type=type,lwd=lwd,col=colors[1],
     xaxs="i",yaxs="i",ylim=c(0,1),bty="n",xaxt="n",yaxt="n",xlab="",ylab="")
if (grepl('bias',statistic)){ abline(h=0.5) }
# -- ... and add the others
for (i in 2:nrow(scaledat)){
  lines(1:ncol(scaledat),scaledat[i,],type=type,lwd=lwds[i],col=colors[i])
}

# -- Superimpose the parallel axes
for (metric in ok_variables){
   axis(2,at=axes[[metric]][["valnewaxis"]],
        labels=axes[[metric]][["newaxis"]],pos=which(ok_variables==metric), lwd=1.5,cex.axis=1.2)}

# -- Add the names of the metrix at the bottom of the plot
axis(1,at=1:ncol(scaledat),labels=ok_variables, las=2, tick=FALSE, font=2,cex.axis=1.2)

# -- Title
titre = paste("Parallel coordinates - ",statistic,season,region)
mtext(titre,side=3,line=2,adj=0,cex=2.1,font=2)

# -- And end with the legend
plot(0:1,0:1,col="white",bty="n",xaxt="n",yaxt="n",xlab="",ylab="")
par(mar=c(1,0,1,0))
if (highlights_only=="TRUE" & is.null(highlights)==FALSE){
  selection = (length(simnames)-length(ok_highlights)+1):length(simnames)
  legend_ncol = 1
  xleg=-0.3
}else{
  selection = 1:length(simnames)
  legend_ncol = 2
  xleg=-0.1
}
for (i in 1:nrow(scaledat)){
  print(paste("Dataset =",simnames[selection[i]],colors[i]))
  print(scaledat[i,])
}

selection = selection[length(selection):1]
print("simnames[selection]")
print(simnames[selection])
legend(xleg,1.05,legend=simnames[selection],col=colors[selection],ncol=legend_ncol,lwd=lwds[selection], bty="n",cex=1.3)
text(-0.1,0,paste("missing variables = ",missing_variables,sep=''),adj=0)

# -- Close the device
dev.off()


