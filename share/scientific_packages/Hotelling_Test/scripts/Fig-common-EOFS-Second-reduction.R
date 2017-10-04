


# -- Launch the multiplot device ---------------------------------------------------------- #

neofpc=neof2
marpc=c(4,4,5,1)
marmap=c(4,5,5,2)

#outdir = paste("results/CommonEOFS-plots/Second-reduction/",var,"/",sep="") ; dir.create(outdir,showWarnings=FALSE)
#figname = paste("Common-EOF-2nd-reduction-",Test,"-",TestPeriod,"-",Experiment,"-ntest-",ntest,"-",Ref,"-",RefPeriod,"-nref-",nref,"-",var,"-neof",neofpc,"-",Regions[[region]]$shortname,".pdf",sep="")
#outdir = paste(hotelling_outputdir,"/CEOFs_plots/",sep="") ; dir.create(outdir,showWarnings=FALSE)
figname = InputTest[[Test]]$output_ceof2_figname

#pdf(paste(outdir,figname,sep=""),width=9,height=neofpc*(12/5))
pdf(figname,width=9,height=neofpc*(12/5))


layout(t(matrix(1:(2*neofpc),2,neofpc)))


dumref=c()
for (ref in names(REFFIELDS)){
     dumref=cbind(dumref,indiv.ref.proj2[[ref]])
}#end for ref
dumtest=c()
for (test in names(TESTFIELDS)){
     dumtest=cbind(dumtest,indiv.test.proj2[[test]])
}#end for test
ylim=range(c(P2.Ref,P2.Test,dumref,dumtest),na.rm=TRUE)


for (i in 1:neofpc){

# -- Explained variance: calculated in the main script ; ExpVar_model and ExpVar_RefMean

# -- Plot de l'EOF i
zmax=1
levels=seq(-zmax,zmax,by=zmax/10)
par(mar=marmap)
plot(C_eofs2[,i],type="l",xaxs="i",lwd=3,xlab="Time (months)",ylab="")
zero(1:length(C_eofs2[,i]))
mtext(paste("EOF",i," ",varlongname[[variable]],", 2nd Common EOFs (Ref.Mean & ",Test,")",sep=""),side=3,line=2.5,adj=0,cex=1.1)
mtext(paste(region," ; seasonal cycle",sep=""),side=3,line=1,adj=0,cex=0.9)


# -- Plot de la PC
par(mar=marpc)
xlab="Spaces"
ylab=paste("PC",i)
pctitre1=paste(Test," = ",round(ExpVar_Model2[i],digits=0),"%",sep="")
pctitre2=paste("Ref.Mean = ",round(ExpVar_Ref2[i],digits=0),"%",sep="")
plot(PP2.Ref[,i],type="l",lwd=3,xlab=xlab,ylab=ylab,main="",col="white",xaxt="n",ylim=ylim)

for (refnames in names(REFFIELDS)){
  lines(indiv.ref.proj2[[refnames]][,i],type="l",lwd=1.5,col="darkgrey")
}#end for refnames
lines(PP2.Ref[,i],type="l",lwd=3,col="black")

#if (length(TestFiles)>1){
#for (testnames in names(TESTFIELDS)){
#  lines(indiv.test.proj2[[testnames]][,i],type="l",lwd=1.5,col="skyblue")
#}#end for testnames
#}#end if
lines(PP2.Test[,i],type="l",lwd=3,col="dodgerblue")

zero(1:neof2)
axis(1,at=seq(1:neof2))
mtext(pctitre1,3,adj=1,line=2.25)
mtext(pctitre2,3,adj=1,line=1)
mtext(paste(ntest," members ; ",nref," ref.",sep=""),side=3,line=1,adj=0)

}#end for neofpc

dev.off()





