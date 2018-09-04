library(optparse)
library(rjson)

option_list = list(
   make_option(c("-j", "--metrics_json_file"), type="character", default="",
               help="Json file containing the results to be plotted", metavar="character"),
   make_option(c("-n", "--figname"), type="character", default="None",
               help="Name of the figure; ", metavar="character"),
   make_option(c("-m", "--main_dir"), type="character", default="",
               help="Path to the main working directory", metavar="character"),
   make_option(c("-r", "--region"), type="character", default="",
               help="Name of the region to be plotted", metavar="character") 
    )

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)


metrics_json_file = opt[['metrics_json_file']]

region = opt[['region']]


results = fromJSON(file=metrics_json_file)

variable = results$variable$variable
varlongname = results$variable$varlongname


obs_reference           = c()
obs_reference_names     = c()
reference_dataset       = c()
reference_dataset_names = c()
test_dataset            = c()
test_dataset_names      = c()
test_dataset_colors     = c()


for (tmp in names(results)){
    if (tmp!='json_structure' & tmp!='variable'){
        print(tmp)
        print(results[[tmp]]$dataset_dict$dataset_type)
        # -- Get the obs_reference tagged results
        if (results[[tmp]]$dataset_dict$dataset_type=='obs_reference'){
           if (results[[tmp]]$results[[region]]$rawvalue!='NA'){          
            obs_reference = c(obs_reference, as.numeric(results[[tmp]]$results[[region]]$rawvalue))
            obs_reference_names = c(obs_reference_names, tmp)
           }#end if
        }#
        # -- Get the reference_dataset tagged results
        if (results[[tmp]]$dataset_dict$dataset_type=='reference_dataset'){
           if (results[[tmp]]$results[[region]]$rawvalue!='NA'){
            reference_dataset = c(reference_dataset, as.numeric(results[[tmp]]$results[[region]]$rawvalue))
            reference_dataset_names = c(reference_dataset_names, tmp)
           }#end if
        }#
        # -- Get the test_dataset tagged results
        if (results[[tmp]]$dataset_dict$dataset_type=='test_dataset'){
           if (results[[tmp]]$results[[region]]$rawvalue!='NA'){
            test_dataset = c(test_dataset, as.numeric(results[[tmp]]$results[[region]]$rawvalue))
            test_dataset_names = c(test_dataset_names, tmp)
            print('names(results[[tmp]]$dataset_dict) = ')
            print(names(results[[tmp]]$dataset_dict))
            if ('color' %in% names(results[[tmp]]$dataset_dict)){ color = results[[tmp]]$dataset_dict$color }
            if ('R_color' %in% names(results[[tmp]]$dataset_dict)){ color = results[[tmp]]$dataset_dict$R_color }
            test_dataset_colors = c(test_dataset_colors, color)
           }#end if
        }#
        
    }#end if tmp!='json_structure'
    
}#end for tmp


# -- Do the plot
ylim = range(c(obs_reference,reference_dataset,test_dataset),na.rm=TRUE)
print("c(obs_reference,reference_dataset,test_dataset)")
print(c(obs_reference,reference_dataset,test_dataset))
print("ylim = ")
print(ylim)

tmp_datasets4plot=c(reference_dataset,test_dataset)
tmp_names4plot=c(reference_dataset_names,test_dataset_names)
tmp_test_dataset_colors = c(rep('black',length(reference_dataset_names)),test_dataset_colors)
tmp_pcex = c(rep(1,length(reference_dataset_names)), rep(1.5,length(reference_dataset_names)))

dumsort = sort(tmp_datasets4plot, decreasing=TRUE, index.return=TRUE)
datasets4plot = dumsort$x
names4plot = tmp_names4plot[dumsort$ix]
sorted_colors = tmp_test_dataset_colors[dumsort$ix]
sorted_pcex = tmp_pcex[dumsort$ix]


figname = opt[['figname']]
png(figname,width=900,height=750)

# -- Test plot 2
par(mar=c(20,5,4,1))
nitems = 1+length(datasets4plot)
ylab='SST raw value'
plot(1:nitems,rep(NA,nitems),ylim=ylim,xaxt='n',xlab="",ylab=ylab,cex=1.1,cex.lab=1.75,cex.axis=1.2,xlim=c(2,nitems-1))
mtext(paste(gsub('_',' ',region),"- space average"),side=3,adj=0,cex=3, font=1,line=0.75)
mtext("annual mean",side=3,adj=1,cex=3, font=1,line=0.75)

grid()
abline(v=1:nitems,lty=2,col="darkgrey")
abline(h=obs_reference)
vertadj=0.04 
for (i in 1:length(obs_reference_names)){
  if (obs_reference_names[i] %in% c('UKMETOFFICE-HadISST-v1-1_198002-200501','NOAA-OISST-v2_198202-201201')){
     text(nitems,obs_reference[i]+vertadj,obs_reference_names[i], adj=1, cex=1.2)
  }else{
     text(1,obs_reference[i]+vertadj,obs_reference_names[i], adj=0, cex=1.2)
  }
}
axis(1,at=1:nitems,labels=FALSE)
for (i in 1:length(datasets4plot)){
    #if (sorted_colors[i]=='black'){
    if (names4plot[i] %in% reference_dataset_names){
       lines(i,datasets4plot[i],type="p", col=sorted_colors[i], pch=16, cex=1.5*sorted_pcex[i])
       mtext(names4plot[i],side=1,at=i,col=sorted_colors[i],las=2,line=1,font=1 )
    }else{
       lines(i,datasets4plot[i],type="p", col=sorted_colors[i], pch=16, cex=1.5*sorted_pcex[i])
       mtext(names4plot[i],side=1,at=i,col=sorted_colors[i],las=2,line=1,font=2 )
       lines(i,datasets4plot[i],type="p", col=sorted_colors[i], pch=0, cex=2.5*sorted_pcex[i])
    }
}#


dev.off()


