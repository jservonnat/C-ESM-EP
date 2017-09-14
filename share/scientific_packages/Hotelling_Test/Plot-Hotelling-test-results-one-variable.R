

# ---------------------------------------------------------------------------------------------------------- #
# -- Ce script fait un test de Hotelling entre un ensemble de jeux de donnees de reference
# -- et une simulation, sur une zone pre-definie.
# -- Le test de Hotelling en pratique necessite de:
# --      - estimer un espace d'EOFs commun a la reference et au modele que l'on veut tester;
# --        pour une definition optimale de cet espace (pour qu'il explique le plus de variance possible
# --        du modele et de la ref), on va estimer une matrice de covariance commune a la ref et au modele ;
# --        si, par facilite , on estimait une matrice de covariance commune avec la moyenne des modeles
# --        et pas pour chaque modele, on perdra de la variance et le test ne sera pas optimal.
# --      - dans cet espace d'EOFs de la matrice de covariance commune, on projette le modele et la moyenne
# --        des refs sur les neof; on projette egalement chaque ref individuelle pour estimer la matrice de
# --        covariance d'erreurs S ; tous les champs projetes sur les neof EOF communes sont mis sous la
# --        forme suivante: les neof PCs sont mises les unes a la suite des autres pour former un vecteur,
# --        de longueur neof*12. La matrice de covariance d'erreur est donc de dimension n.indiv.ref/neof*12
# --      - La matrice de covariance d'erreur n'est pas inversible en l'etat. Pour l'inverser, on calcule
# --        ses EOFs; on inversera la matrice diagonale de valeurs propres, et on projettera les champs (deja
# --        projettes dans l'espace des EOFs communes) dans l'espace de ces EOFs de la matrice de covariance
# --        d'erreur. La figure Variance-explained-by-error-covariance-matrix.pdf montre comment les
# --        differents modeles et la moyenne des Refs se projettent dans ces EOFs.
# --      - On estime le parametre nu de la distribution de Fisher pour estimer la significativite du test
# --        a l'aide de la formule de Yao (1965)
# --      - on estime T2, son intervalle de confiance, ainsi que Ts2 (voir Braconnot & Frankignoul 1992)
# --        La figure HotellingDB-test-IPSL-models-vs-REF-mean-*.pdf resume les resultats du test. 
# -- 
# ---------------------------------------------------------------------------------------------------------- #


library("optparse")
library(rjson)

option_list = list(
   make_option(c("-j", "--test_json_files"), type="character", default="",
               help="Json file containing the description of the datasets that will be submitted to the test", metavar="character"),
   make_option(c("-n", "--figname"), type="character", default="None",
               help="Name of the figure; ", metavar="character"),
   make_option(c("-m", "--main_dir"), type="character", default="",
               help="Path to the main working directory", metavar="character"),
   make_option(c("-s", "--statistic"), type="character", default="T2",
               help="Hotelling statistic => T2 or Ts2", metavar="character")

   )

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)




# -- Source the useful scripts of functions -----------------------------------------------
main_dir = opt[['main_dir']]
if (main_dir==""){main_dir=getwd()}
Rsource=paste(main_dir,"/scripts/Rtools/",sep="")
source(paste(Rsource,"function.R",sep=""))
library(plotrix)


# --------------------------------------------------------------------------------------------------------------
# -- Bloc 1/ Que veut-on afficher?
# -- Le script fait un panel par variable (que l'on precise dans vars)
# --

# -- Toutes les cles suivantes sont disponibles et doivent etre renseignees ; si elles ne le sont pas,
# -- cela veut dire qu'on laisse le choix libre et que l'on recupere les resultats correspondants
# -- a toutes les valeurs possibles. SI ON NE RENSEIGNE PAS UNE CLE, IL FAUT LA COMMENTER DANS LE BLOC 3!!
# --> CLES:
# -- TestName ; var (boucle...) ; Experiment ; SimName ; Period ; CommonSpace
# -- neof1 ; neof2 ; RefName ; CommonGrid ; nref ; ntest

# ==============================================================================
# -- Si un argument est NULL, 
#CommonSpace="CCM"  # -> Soit CCM, soit CMR
#Period="198001-200512" # -- Period of the model
RefName="GBSB2015"
#CommonGrid="LMDZ4.0_9695"
#Activity="CMIP5"
SimName="r1i1p1"
#Experiment="amip"

# ==============================================================================

# ==============================================================================
# -- Which stat? Ts2 ou T2?
stat=opt[['statistic']]

# ==============================================================================
# -- Do we show the informations on the EOFS?
show.EOF=TRUE

# ==============================================================================


# ==============================================================================
# -- Some graphical parameters...
# --> If you want to modify the margins around the panels:
margins.one.panel=c(20,4,4,4)  # -- Bottom side, left, top, right
cex=1

# --> Dimensions of one panel in inches in the pdf figure
one_panel_width=2.5
one_panel_height=8

# --> If you don't want the labels between the panels
no.Ts2.label.between.panels=FALSE
no.EOF.label.between.panels=FALSE

# -- Do we want to sort the results?
sort.the.results=TRUE

# -- Highlight models
#highlights=list("IPSL-CM5A-LR"="blue",
#                "IPSL-CM5A-MR"="dodgerblue",
#		"IPSL-CM5B-LR"="purple",
#		"CNRM-CM5"="green")

highlights=list()
# ==============================================================================

# --
# -------------------------------------------------------------------------------------------------------------




# --------------------------------------------------------------------------------------------------------------
# -- Bloc 2/ Recuperation des resultats disponibles et scan de l'existant
InputRes = fromJSON(file=opt[['test_json_files']])

# -> InputRes is a R list which elements are the customnames of the tested datasets
ResForPlot = list()
for (testname in names(InputRes)){
  # -> Get the json file of the results for testname
  # ->
  res_json_file = InputRes[[testname]]$output_res_hotelling_json_file 
  print(paste('Getting json file = ',res_json_file))
  ResForPlot[[testname]] = fromJSON(file=res_json_file)
}#end for testname


variable = ResForPlot[[testname]]$description$variable

# ResForPlot[[testname]]$description
# --> Get the highlighted results that have a 'color' or 'R_color' argument
highlights = list()
for (testname in names(InputRes)){
  # -> Get the json file of the results for testname
  # ->
  if ('color' %in% names(InputRes[[testname]])){ highlights[[testname]] = InputRes[[testname]]$color }
  if ('R_color' %in% names(InputRes[[testname]])){ highlights[[testname]] = InputRes[[testname]]$R_color }

}#

# --
# -------------------------------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------------------------------
# -- Bloc 3/ Selection des resultats
# -- !! La boucle sur les variables demarre dans ce bloc et finit au bloc X.

dumylim=c()
xlabels=c()
for (testname in names(ResForPlot)){
     dum.xlabel=testname
     xlabels=c(xlabels,testname)
     dumylim=c(dumylim,ResForPlot[[testname]]$hotelling_res[[stat]]$conf_int)
}#end if

# --
# --------------------------------------------------------------------------------------------------------------

# On a besoin des ylim communes a toutes les variables => on doit faire la boucle
# On n'a pas forcement tous les modeles sur toutes les variables... donc on peut faire un xlabels par variable
# 


# --------------------------------------------------------------------------------------------------------------
# -- Bloc 4/ Ouverture du device graphique pour l'affichage
# -- Creation d'un nom de fichier adequat

print("Start the graphical device")
print("Name of the figure :")
figname=opt[['figname']]
if (figname=='None'){
figname = paste('results/figures/hotelling_statistic/',strsplit(strsplit(opt[['test_json_files']], 'test_files_')[[1]][2], '.json')[[1]][1],'_',stat,'_hotelling_statistic.pdf',sep='')
}
print(figname)
#figname = 

pdf(figname,width=12,height=11)

# --
# --------------------------------------------------------------------------------------------------------------






# --------------------------------------------------------------------------------------------------------------
# -- Bloc 5/ Affichage des resultats pour la variables variable
# -- !! La boucle sur les variables se termine dans ce bloc

print("Start the display")

# -- Parametres graphiques
par(mar=margins.one.panel,cex=cex)

source(paste(main_dir,"/scripts/graphical-parameters.R",sep=""))

    ylab=paste(stat,"statistic")

    # -- Tests available for this var?
    ntests=length(ResForPlot)

    # -- Demarrage du plot
    ylim=range(dumylim)
    plot(1:ntests,rep(0,ntests),type="p",col="white",xlab="",ylab="",main="",pch=16,cex=1.2,ylim=ylim,xaxt="n",xlim=c(0,ntests+1),xaxs="i")
    grid(nx=(ntests+1))

    # -- Loop on the tests
    T2=conf_int=threshold=explvar.model.neof1=explvar.model.neof2=explvar.refmean.neof1=explvar.refmean.neof2=c()
    for (testname in names(ResForPlot)){

         TMP=ResForPlot[[testname]]
         T2=c(T2,TMP$hotelling_res[[stat]]$statistic)
	 conf_int=cbind(conf_int,TMP$hotelling_res[[stat]]$conf_int)
	 threshold=c(threshold,TMP$hotelling_res[[stat]]$threshold_99)
	 #if (stat=="T2"){T2=log(T2) ; conf_int=log(conf_int) ; threshold=log(threshold)}


	 # -- Informations on the EOFs
	 if (show.EOF==TRUE){
	     explvar.model.neof1=c(explvar.model.neof1,round(TMP$hotelling_res$explvar.model.neof1,digits=1))
             explvar.model.neof2=c(explvar.model.neof2,round(TMP$hotelling_res$explvar.model.neof2,digits=1))
	     explvar.refmean.neof1=c(explvar.refmean.neof1,round(TMP$hotelling_res$explvar.refmean.neof1,digits=1))
	     explvar.refmean.neof2=c(explvar.refmean.neof2,round(TMP$hotelling_res$explvar.refmean.neof2,digits=1))
	 }#end if show.EOF
 
     }#end for test

     if (sort.the.results==TRUE){
         sorting=sort(T2,decreasing=FALSE,index.return=TRUE)$ix
	 T2=T2[sorting]
	 conf_int=conf_int[,sorting]
	 threshold=threshold[sorting]
	 if (show.EOF==TRUE){
	     explvar.model.neof1=explvar.model.neof1[sorting]
	     explvar.refmean.neof2=explvar.refmean.neof2[sorting]
	     explvar.model.neof1=explvar.model.neof1[sorting]
	     explvar.refmean.neof2=explvar.refmean.neof2[sorting]
	 }#end if show.eof
         xlabels=xlabels[sorting]
     }#end if sort.the.results



     # -- Affichage de l'intervalle de confiance
     for (i in 1:ntests){
          lines(rep(i,2),conf_int[,i],type="l",col="darkturquoise")
     }#end for
     
     # -- rajouts de points pour un affichage plus propre
     lines(1:ntests,T2,type="p",pch=16,cex=1.5)
     points(1:ntests,conf_int[1,],type="p",pch=16,col="darkgrey")
     points(1:ntests,conf_int[2,],type="p",pch=16,col="darkgrey")
     points(1:ntests,threshold,type="p",pch=22,col="red")
     
     # -- Informations on the EOFs
     if (show.EOF==TRUE){
         yscale=ylim[2]/100
         lines(1:ntests,yscale*explvar.model.neof1,type="b",col="blue")
         lines(1:ntests,yscale*explvar.model.neof2,type="b",col="blue",lty=2,cex=0.9)
         lines(1:ntests,yscale*explvar.refmean.neof1,type="b",col="black")
         lines(1:ntests,yscale*explvar.refmean.neof2,type="b",col="black",lty=2)
	 mtext(paste("NEOF1 =",TMP$description$neof1),side=3,adj=0,cex=0.9,line=1.25)
	 mtext(paste("NEOF2 =",TMP$description$neof2),side=3,adj=0,cex=0.9,line=0.5)
	 axis(4,at=seq(0,100,by=20)*yscale,labels=FALSE,cex=0.8)
         if (no.EOF.label.between.panels==FALSE){
             axis(4,at=seq(0,100,by=20)*yscale,tick=FALSE,labels=seq(0,100,by=20),cex=0.8)
             mtext("% explained variance",4,line=2)
             }else{
                   if (which(vars==variable)==length(vars)){
                        axis(4,at=seq(0,100,by=20)*yscale,tick=FALSE,labels=seq(0,100,by=20),cex=0.8)
                        mtext("% explained variance",4,line=2)
             }}#end if
         zero(0:(ntests+1),val=90*yscale,lty=3)
     }#end if show.EOF

     # -- ligne de zeros
     zero(0:(ntests+1))

     # -- axe des X
     display.xlabels=xlabels
     if (length(highlights)>=1){
     for (highlight in names(highlights)){
          model=highlight
          color=highlights[[highlight]]
	  which.model=which(xlabels==model)
	  display.xlabels[which.model]=NA
	  mtext(model,side=1,at=which.model,col=color,las=2,font=2,line=1)
	  points(which.model,T2[which.model],type="p",pch=16,cex=1.6,col=color)
     }#end for highlight
     }#end
     axis(1,at=1:ntests,labels=display.xlabels,las=2)

     # -- Label des Y
     mtext(ylab,2,line=2)

    # -- Titles - subtitles
    titre=paste("CMIP5",varlongname[[variable]])
    if (show.EOF==TRUE){
        mtext(titre,side=3,adj=0,cex=1.1,line=2.2,font=2)
	}else{
        mtext(titre,side=3,adj=0,cex=1.1,font=2,line=0.75)
    }#end if
    
    # -- Rajouter nref, ntest, nom de la ref, CCM, Period
    mtext(paste("Reference =",RefName),side=3,adj=1,cex=1.1,line=2)


# --
# --------------------------------------------------------------------------------------------------------------




# --------------------------------------------------------------------------------------------------------------
# -- Bloc 6/ fermeture du device graphique 
dev.off()
print("Done")

# --
# --------------------------------------------------------------------------------------------------------------

