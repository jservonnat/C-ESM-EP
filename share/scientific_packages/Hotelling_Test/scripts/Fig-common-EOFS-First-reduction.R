# -- Launch the multiplot device ---------------------------------------------------------- #

source(paste(main_dir,"scripts/Rtools/filled.contour3.R",sep="/"))

neofpc=neof1
marpc=c(4,2,4,1)
marmap=c(4,5,4,1)


figname = InputTest[[Test]]$output_ceof1_figname
print(figname)
pdf(figname,width=12,height=neofpc*(12/5))

layout(t(matrix(1:(3*neofpc),3,neofpc)),widths=c(4,1,1))

dumref=c()
for (ref in names(REFFIELDS)){
     dumref=cbind(dumref,indiv.ref.proj[[ref]])
}#end for ref
dumtest=c()
for (test in names(TESTFIELDS)){
     dumtest=cbind(dumtest,indiv.test.proj[[test]])
}#end for test


dumylim=range(cbind(P1.Ref,P1.Test,dumref,dumtest),na.rm=TRUE)


for (i in 1:neofpc){

# -- On recupere l'EOF et la PC
dum.eof=C_eofs1[,i]
dum.pc.ref=P1.Ref[,i]
dum.pc.test=P1.Test[,i]

# -- Explained variance: calculated in the main script ; ExpVar_Model and ExpVar_RefMean

# -- On remet les valeurs des eofs sur une matrice qui contient les continents (une matrice de taille lon*lat)
eof.ref.tmp=BlankField ; eof.ref.tmp[NoNA]=dum.eof

# -- On remet la matrice dans la dimensions lon/lat 
tmp.eof=eof.ref.tmp ; dim(tmp.eof)=c(length(lat),length(lon)) ; tmp.eof=t(tmp.eof)


# -- Plot de l'EOF i
source(paste(main_dir,"scripts/Rtools/Rpalettes.R",sep="/"))
source(paste(main_dir,"scripts/graphical-parameters.R",sep="/"))
pal=CORREL


zmax=0.1


levels=seq(-zmax,zmax,by=zmax/10)
library(maps)
land=map('world2',ylim=range(lat),xlim=range(lon),interior=FALSE,plot=FALSE)
par(mar=marmap)
tmp.eof=borne(tmp.eof,-zmax,zmax)
if (lat[2]<lat[1]){plat=sort(lat,decreasing=FALSE) ; tmp.eof=tmp.eof[,length(lat):1]}else{plat=lat}
if (lon[2]<lon[1]){plon=sort(lon,decreasing=FALSE) ; tmp.eof=tmp.eof[length(lon):1,]}else{plon=lon}

dumcex = 0.9

filled.contour3(plon,plat,tmp.eof,color.palette=pal,levels=levels,plot.axes=c(
              contour(plon,plat,tmp.eof,levels=levels,col="darkgrey",lwd=0.7,add=T,labels=NULL),
	      lines(land$x,land$y),
	      lines(plon,rep(0,length(plon)),type="l",lty=2),
	      axis(2,at=seq(latS,latN,by=10)),
	      axis(1,at=seq(0,180,by=30)),
	      axis(1,at=seq(210,360,by=30),labels=seq(-150,0,by=30)),
              mtext(paste("Common EOF",i," ",varlongname[[variable]],": ",Test," and Ref. Mean",sep=""),side=3,line=2.5,adj=0,cex=1.2*dumcex),
              mtext(paste("Variance expl. by EOF ",i," : Ref.Mean = ",round(ExpVar_RefMean[i],digits=1),"% ; ",Test," = ",round(ExpVar_Model[i],digits=1),"%",sep=""),side=3,line=1,adj=0,cex=1*dumcex),
	      mtext("Longitude",side=1,line=2.5),mtext("Latitude",side=2,line=2.5,las=3)
	      ))


# -- Plot des projections des refs et des tests sur l'EOF i
lwdindivref=1
lwdtest=3

par(mar=marpc)
xlab="Months"
ylab=paste("PC",i)
titre=paste("Proj. on C.EOF",i)
# -- On construit un vecteur dum avec toutes les PCs a afficher pour connaitre les limites du plot
x=1:length(P1.Ref[,i])
plot(x,rep(NA,length(x)),type="l",lwd=3,xlab=xlab,ylab=ylab,main="",col="white",ylim=dumylim,xaxs="i",xaxt="n")
grid()
for (refnames in names(REFFIELDS)){
  lines(x,indiv.ref.proj[[refnames]][,i],type="l",lwd=1,col="darkgrey")
}#end for refnames
lines(x,P1.Ref[,i],type="l",lwd=3,col="black")
axis(1,at=1:12,labels=c('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'),las=2)

lines(x,P1.Test[,i],type="l",lwd=3,col="dodgerblue")
zero(x)
mtext(titre,3,line=1,adj=0)



# -- Plot des PCs des EOFs intrinseques
par(mar=marpc)
titre=paste("Intrinsic PC",i)
# -- Demarrage du plot
plot(x,rep(NA,length(x)),type="l",lwd=3,xlab=xlab,ylab=ylab,main="",col="white",ylim=dumylim,xaxs="i",xaxt="n")
grid()
axis(1,at=1:12,labels=c('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'),las=2)
for (ref in names(REFFIELDS)){
  pc=REFFIELDS[[ref]]$EOF$x[,i] ; eof=REFFIELDS[[ref]]$EOF$rotation[,i]
  test=sum(eof*C_eofs1[,i]) ; if (test<0){pc=-pc}
  lines(x,pc,type="l",lwd=1,col="darkgrey")
}#end for refnames
pc=EOF.MeanRef$x[,i] ; eof=EOF.MeanRef$rotation[,i]
test=sum(eof*C_eofs1[,i]) ; if (test<0){pc=-pc}
lines(x,pc,type="l",lwd=3,col="black")

pc=EOF.MeanTest$x[,i] ; eof=EOF.MeanTest$rotation[,i]
test=sum(eof*C_eofs1[,i]) ; if (test<0){pc=-pc}
lines(x,pc,type="l",lwd=3,col="dodgerblue")
zero(x)
mtext(titre,3,line=1,adj=0)

}#end for neofpc

dev.off()





