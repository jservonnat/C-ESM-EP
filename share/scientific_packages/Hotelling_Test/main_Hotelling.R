
# -- Get the arguments
# -- -> name of the json file TestFiles.json
# -- -> variables
# -- -> experiment = historical or amip

#!/usr/bin/env Rscript
library("optparse")
library(rjson)
 
option_list = list(
   make_option(c("-f", "--test_json_file"), type="character", default="pouet",
               help="Json file containing the description of the datasets that will be submitted to the test", metavar="character"),
   make_option(c("-r", "--reference_json_file"), type="character", default="pouet",
               help="Json file containing the descriptions (path and names) to the observational references used in GB2015", metavar="character"),
   make_option(c("-o", "--hotelling_outputdir"), type="character", default="results/",
               help="Path to the output directory", metavar="character"),
   make_option(c("-m", "--main_dir"), type="character", default="",
               help="Path to the main working directory", metavar="character")

   )
				       
opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

# ======================================================================================================================== #
# -- HEADER

# -- Define the input files (you can have several txt files as input ; will make a loop)
test_json_file = opt[['test_json_file']]

reference_json_file = opt[['reference_json_file']]

hotelling_outputdir = opt[['hotelling_outputdir']]


# -- Variable
dum = strsplit(reference_json_file,'_')[[1]]
print(dum)
print(strsplit(dum[length(dum)], '.json'))
variable = strsplit(dum[length(dum)], '.json')[[1]]
print(paste("Working on variable",variable))
print(variable)

# -- Define the region of interest (see Regions-def.R)
region = "Tropical oceans"

# --> Which common space for the Hotelling test?
# ==> Common EOFs or EOFs of the mean of the reference?
CommonSpace = "CCM" # 2 possible values: CCM (Common Covariance Matrix) or CMR (Covariance Matrix of the Reference mean)

# -- 
# ======================================================================================================================== #


main_dir = opt[['main_dir']]
if (main_dir==""){main_dir=getwd()}

# -- On source les scripts de fonctions utiles
Rsource=paste(main_dir,"/scripts/Rtools/",sep="")
print(paste(Rsource,"netcdf-with-R_v2.R",sep=""))
source(paste(Rsource,"netcdf-with-R_v2.R",sep=""))
source(paste(Rsource,"filled.contour3.R",sep=""))
source(paste(Rsource,"function.R",sep=""))


# -- Selection of the working area -------------------------------------------------------- #
source(paste(main_dir,"/scripts/Regions-def.R",sep=""))
lonW=Regions[[region]]$lonW
lonE=Regions[[region]]$lonE
latS=Regions[[region]]$latS
latN=Regions[[region]]$latN



# !!!! START !!!!

# -- REF
print(reference_json_file)
InputRefs = fromJSON(file=reference_json_file)

REFFIELDS = list()
for (refname in names(InputRefs)){
     print(refname)
     tmp = get.nc2(InputRefs[[refname]]$file,varname=variable,region=c(lonW,lonE,latS,latN))
     dum = tmp$dat
     dum[dum<=-999]=NA ; REFFIELDS[[refname]]$dat = dum
     if (refname == names(InputRefs)[1]){ MeanRef = dum }else{ MeanRef = MeanRef + dum } # -> Initialize MeanRef
}#end for RefFile

# -- Get the longitudes and latitudes of the last reference (they are all regridded on a common grid)
lon=tmp$lon
lat=tmp$lat

BlankField = MeanRef[1,] * NA
test.plot = tmp ; test.plot$dat = test.plot$dat*NA

# -> And calculate the mean of the references (MeanRef is the sum of all the individual references
# -> We divide MeanRef by the number of individual references to obtain the mean of the references
MeanRef = MeanRef / length(InputRefs)
#plot = test.plot ; plot$dat = apply(MeanRef,2,na.rm=TRUE) ; quickmap2(plot)

    
TestForNA = MeanRef
# -- We now want to remove all the remaining NAs ; we select all the non-NA grid cells
# -- that are common to all the files (both ref and test) and we apply the mask
test = apply(TestForNA,2,mean) #* mask
NoNA = which(is.na(test)==FALSE)
# --> We select the non-NA grid cells on all the refs, the MeanRef and the tests
# --> We also estimate the intrinsic EOFs of the datasets
# 1/ For the area of the grid cells, so we can calculate the weights
latpond = cos(rep(lat,length(lon))*pi/180)[NoNA]
weights = latpond/sum(latpond)
scale=1/sqrt(weights)


# !!!!!!!! STOP HERE => A cause du NONA!!! 
# 2/ For the MeanRef and the MeanTest
WMeanRef = MeanRef[,NoNA]
EOF.MeanRef = prcomp(WMeanRef,scale=scale)


# 3/ For the individual ref
for (ref in names(REFFIELDS)){
     print(paste("Computing EOFs for",ref))
     REFFIELDS[[ref]]$wdat = REFFIELDS[[ref]]$dat[,NoNA]
     REFFIELDS[[ref]]$EOF = prcomp(REFFIELDS[[ref]]$wdat,scale=scale)
}#end for ref



# -- TEST
# -- On charge la liste des fichiers tests ; si les noms de fichiers contiennent le nom de variable, il correspondra
# -- automatiquement avec var. Sinon (plusieurs variables dans le meme fichier), le script ira chercher la variable dans le fichier unique.
InputTest = fromJSON(file=test_json_file)

for (testname in names(InputTest)){

    TESTFIELDS = list()
    print(testname)
    if (InputTest[[testname]]$compute_hotelling=='TRUE'){
       dum=get.nc2(InputTest[[testname]]$file,varname=variable,region=c(lonW,lonE,latS,latN))$dat
       TESTFIELDS[[testname]]$dat = dum
       MeanTest = dum
       #plot = test.plot ; plot$dat = apply(MeanTest,2,na.rm=TRUE) ; quickmap2(plot)

       # 2/ For the MeanRef and the MeanTest
       WMeanRef = MeanRef[,NoNA]
       EOF.MeanRef = prcomp(WMeanRef,scale=scale)
       #plot = test.plot ; plot$dat[NoNA] = apply(MeanRef,2,na.rm=TRUE) ; quickmap2(plot)
       WMeanTest = MeanTest[,NoNA]
       EOF.MeanTest = prcomp(WMeanTest,scale=scale)
       #plot = test.plot ; plot$dat[NoNA] = apply(MeanTest,2,na.rm=TRUE) ; quickmap2(plot)

       # 4/ For the test files
       TESTFIELDS[[testname]]$wdat = TESTFIELDS[[testname]]$dat[,NoNA]
       TESTFIELDS[[testname]]$EOF = prcomp(TESTFIELDS[[testname]]$wdat,scale=scale)

       # -- Run the Hotelling script
       # --> The Hotelling script needs REFFIELDS$wdat and MeanRef, TESTFIELDS$wdat and the weights to calculate the statistics.
       # --> It also needs lon and lat, and BlankField to plot the EOF maps
       print(paste('source(Hotelling_routine.R) for',testname,'for variable',variable))
       source(paste(main_dir,"Hotelling_routine.R",sep="/"))
    }else{
       print(paste('Results already available:',InputTest[[testname]]$output_res_hotelling_json_file))
    }#
}#end for ListOfTestFiles



