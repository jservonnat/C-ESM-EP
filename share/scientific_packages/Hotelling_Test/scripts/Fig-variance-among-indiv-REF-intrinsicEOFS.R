

# -- Launch the multiplot device ---------------------------------------------------------- #

source(paste(main_dir,"scripts/Rtools/filled.contour3.R",sep="/"))

marmap=c(4,5,4,1)

if (neof1==3){
plotheight=12/5
}
if (neof1==2){
plotheight=12/4
}


outdir = paste(main_dir,"/results/CommonEOFS-plots/First-reduction/",var,"/",sep="") ; dir.create(outdir,showWarnings=FALSE)
figname = paste("Variance-among-indivref-",Ref,"-",RefPeriod,"-nref-",nref,"-",var,"-neof",neof1,"-",Regions[[region]]$shortname,".pdf",sep="")


pdf(paste(outdir,figname,sep=""),width=9,height=neof1*plotheight)

layout(matrix(1:neof1,neof1,1))

for (i in 1:neof1){

# -- On recupere l'EOF et la PC
CEOF=C_eofs1[,i]
eofs=c()
expvar=c()
for (ref in names(REFFIELDS)){
  dumeof=REFFIELDS[[ref]]$EOF$rotation[,i]
  test=sum(CEOF*dumeof) ; if (test<0){dumeof=-dumeof}
  eofs=rbind(eofs,dumeof)
  tmp.expvar=100*(REFFIELDS[[ref]]$EOF$sd[i]/sum(REFFIELDS[[ref]]$EOF$sd))
  expvar=c(expvar,tmp.expvar)
}#end for ref
expvar=round(expvar,digits=1)

variance.eof=apply(eofs,2,sd)^2


#REFEOF=EOF.MeanRef$rotation[,i]
#REF.ExpVar=100*(EOF.MeanRef$sd^2)/sum(EOF.MeanRef$sd^2)

# -- Explained variance: calculated in the main script ; ExpVar_Model and ExpVar_RefMean

# -- On remet les valeurs des eofs sur une matrice qui contient les continents (une matrice de taille lon*lat)
var.tmp=BlankField ; var.tmp[NoNA]=variance.eof

# -- On remet la matrice dans la dimensions lon/lat 
var.plot=var.tmp ; dim(var.plot)=c(length(lat),length(lon)) ; var.plot=t(var.plot)


# -- Plot de l'EOF i
source("scripts/Rpalettes.R")
pal=CORREL


zmax=0.001


levels=seq(-zmax,zmax,by=zmax/10)
library(maps)
land=map('world2',ylim=range(lat),xlim=range(lon),interior=FALSE,plot=FALSE)
par(mar=marmap)
var.plot=borne(var.plot,-zmax,zmax)
if (lat[2]<lat[1]){plat=sort(lat,decreasing=FALSE) ; var.plot=var.plot[,length(lat):1]}else{plat=lat}
if (lon[2]<lon[1]){plon=sort(lon,decreasing=FALSE) ; var.plot=var.plot[length(lon):1,]}else{plon=lon}

filled.contour3(plon,plat,var.plot,color.palette=pal,levels=levels,plot.axes=c(
              contour(plon,plat,var.plot,levels=levels,col="darkgrey",lwd=0.7,add=T,labels=NULL),
	      lines(land$x,land$y),
	      lines(plon,rep(0,length(plon)),type="l",lty=2),
	      axis(2,at=seq(latS,latN,by=10)),
	      axis(1,at=seq(0,180,by=30)),
	      axis(1,at=seq(210,360,by=30),labels=seq(-150,0,by=30)),
              mtext(paste("Variance among EOFs of indiv. ref., EOF",i,", ",varlongname[[var]]," (",Ref,")",sep=""),side=3,line=2.5,adj=0,cex=1.2),
	      mtext(paste(region," ; seasonal cycle",sep=""),side=3,line=1,adj=0,cex=1),
              mtext(paste("EOF",i," = (",min(expvar)," ; ",max(expvar),")%",sep=""),side=3,line=1,adj=1),
	      mtext("Longitude",side=1,line=2.5),mtext("Latitude",side=2,line=2.5,las=3),
              mtext(paste(nref," ref.",sep=""),side=3,line=2.5,adj=1)
	      ))


}#end for neof1

dev.off()





