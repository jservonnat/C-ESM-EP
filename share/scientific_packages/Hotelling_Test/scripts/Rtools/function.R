
   ### fonctions usuelles pour realiser differentes operations pratiques ###
   ### borne() = permet de borner les donnees pour l'affichage (pas de   ###
   ### valeurs sup ou inf aux bornes du graph)                           ###
   ### which.image.cont() = attribue une palette de couleur en fonction  ###
   ### des bornes sup et inf                                             ###
   ### indice.point() = donne l'indice d'un point(long,lati) dans la     ###
   ### matrice de donnees, connaissant list.lon et list.lat              ###
   ### indice.zone() = sort un vecteur comportant les indices des points ###
   ### d'une zone carree definie par ses coordonnees loninf,lonsup,...   ###
   ### spatial.t.test() = sort un vecteur de longueur egale au nombre de ###
   ### points de grille de la zone etudiee. Le vecteur test.res contient ###
   ### des 0 lorsque la difference de moyennes n'est pas significative,  ###
   ### 1 dans le cas contraire.                                          ###




"ri"=
function(model,obs){
# -- RI = reliability index
# -- model and obs are time series
RI=exp(sqrt((1/length(obs))*sum(log(obs/model)^2)))
RI
}


"ae"=
function(model,obs){
# -- AE = average error
# -- model and obs are time series
AE=mean(model-obs)
AE
}

"aae"=
function(model,obs){
# -- AE = average absolute error
# -- model and obs are time series
AAE=mean(abs(model-obs))
AAE
}



"mef"=
function(model,obs){
# -- MEF = modelling efficiency
# -- model and obs are time series
errors=sum((model-obs)^2,na.rm=TRUE)
obs_sqdev=sum((obs-mean(obs,na.rm=TRUE))^2,na.rm=TRUE)
mef_score=(obs_sqdev-errors)/obs_sqdev
mef_score
}

"rmse"=
function(dat1,dat2,area=NULL){

if (is.null(dim(dat1))==TRUE | length(dim(dat1))==1){
if (is.null(area)==TRUE){
area=rep(1,length(dat1))}else{area=area}#end if & else
area[which(is.na(dat1)==TRUE | is.na(dat2)==TRUE)]=NA
rmse=sqrt(sum(((dat1-dat2)^2)*area,na.rm=TRUE)/sum(area,na.rm=TRUE))
}else{
if (is.null(area)==TRUE){
area=rep(1,ncol(dat1))}else{area=area}#end if & else
area[which(is.na(dat1[1,])==TRUE | is.na(dat2[1,])==TRUE)]=NA
sqdiff=(dat1-dat2)^2
wdiff=t(t(sqdiff)*area)
ts=apply(wdiff,1,sum,na.rm=TRUE)
rmse=sqrt(ts/sum(area,na.rm=TRUE))
}

rmse
}











"init.table"=
function(nr,nc,martab=c(0,0,0,0),lwd=1){
par(mar=martab)
image(seq(0,nc,length=10),seq(0,nr,length=10),matrix(data=0,10,10),bty="n",xaxt="n",yaxt="n",xlab="",ylab="",col="white")
segments(0,(nr-1),nc,lwd=lwd)
}

"fill.table"=
function(i,j,nr,text,cex=1,poscol=0.5,posrow=0.5){
# familiy for the font
col=(j-poscol)
row=(nr-i+posrow)
text(col,row,text,cex=cex)
}




"explvar.eof"=
function(pc.dat,n){
dum=((pc.dat$sdev[n]^2)/sum((pc.dat$sdev^2)))*100
dum
}



"GreenW_centered"=
function(dat,lon,lat,lonresol=2.5,zero=0,EAST=180,WEST=(EAST+lonresol)){
W=indice.zone(lon,lat,WEST,lon[length(lon)],lat[length(lat)],lat[1])
E=indice.zone(lon,lat,zero,EAST,lat[length(lat)],lat[1])

if (is.null(dim(dat))==TRUE){
dum=c(dat[W$ind],dat[E$ind])
dim(dum)=c(length(lat),length(lon)) ; dum=dum[length(lat):1,] ; dim(dum)=NULL
DAT=dum
}else{
DAT=c()
for (i in 1:nrow(dat)){
dum=c(dat[i,W$ind],dat[i,E$ind])
dim(dum)=c(length(lat),length(lon)) ; dum=dum[length(lat):1,] ; dim(dum)=NULL
DAT=rbind(DAT,dum)
}}#end for i and else
LIST=list("dat"=DAT,"lon"=c(W$lon-360,E$lon))
}




"pourc_earth_lmdz9672"=
function(dat,thres="NO"){
areanc=open.ncdf("/home/e2c2/jservon/ESCARSEL/LMDZ9672_grid_AREA.nc")
varnc=areanc$var$aire
area=get.var.ncdf(areanc,varnc)
area=t(area)
dim(area)=NULL
close.ncdf(areanc)

if (thres!="NO"){ind=which(is.na(dat)==TRUE | dat<thres)}
else{ind=which(is.na(dat)==TRUE)}
pourc=round((sum(area[ind])/sum(area))*100,digits=0)

pourc

}#end def




"plot.table"=
function(table,rownames,colnames,w.adj=0,h.adj=0,cex1=1,cex2=1,rnames=1,cnames=1,wcol=1,hrow=1){

mar=c(h.adj,w.adj,h.adj,w.adj)
nrow=nrow(table)+1
ncol=ncol(table)+1
nelts=nrow*ncol
layout(matrix(1:nelts,nrow,ncol),widths=c(rnames,rep(wcol,nrow-1)),heights=c(cnames,rep(hrow,ncol-1)))

table=cbind(rownames,table)
table=rbind(colnames,table)

xlim=c(0,1)
for (j in 1:ncol(table)){for (i in 1:nrow(table)){
par(mar=mar)
if (i==1 | j==1){par(cex=cex1);par(font=2)}else{par(cex=cex2);par(font=1)}
plot(rep(NA,2),bty="n",xaxt="n",yaxt="n",xlim=xlim,ylim=xlim,xlab="",ylab="")
text(0.5,0.5,as.character(table[i,j]))
}}
}#end def plot.table




"smth.spline.noNA"=
function(dat,spar=10,df=0){
indices=1:length(dat)
res=array(data=NA,length(dat))
dum=which(is.finite(dat)==TRUE)
if (spar!=10){res[dum]=smooth.spline(dat[dum],spar=spar)$y}
if (df!=0){res[dum]=smooth.spline(dat[dum],df=df)$y}
res
}



"pl"=
function(dat,col="black",lwd=1){
if (col=="b"){col="blue"}
if (col=="r"){col="red"}
if (col=="g"){col="green"}
plot(dat,type="l",col=col,lwd=lwd)
}



"li"=
function(dat,col="black",lwd=1){
if (col=="b"){col="blue"}
if (col=="r"){col="red"}
if (col=="g"){col="green"}
lines(dat,type="l",col=col,lwd=lwd)
}



"SE"=
function(data,model){
# data is the array of observed data
# model is the array of modeled data
E=(model-data)^2
E
}


"rednoisepar"=
function(dat){
nsteps=length(dat)
a=cov(dat[1:(nsteps-1)],dat[2:nsteps],use="pairwise.complete.obs")/var(dat,na.rm=TRUE)
sigmasq=var(dat,na.rm=TRUE)*(1-a^2)
par=list("a"=a,"sigmasq"=sigmasq)
par
}


"rednoise"=
function(nsteps,a,sigma){
X=array(data=0,nsteps)
b=sqrt(sigma)*rnorm(nsteps-1)
X[1]=b[1]
for (i in 1:(nsteps-1)){X[i+1]=a*X[i]+b[i]}
X=X-mean(X)
X
}#end def


"summary.test"=
function(stat,proba=99.5){

dumcoefcards=c()
dumprobatsup=c()

for (i in 1:length(stat)){
dumproba=100-((stat[[i]][[4]][8])*100)
dumcoef=stat[[i]][[4]][2]
dumcoefcards=c(dumcoefcards,dumcoef)
dumprobatsup=c(dumprobatsup,dumproba)
}#end for i

coefs=list()
coefs$tstd=dumcoefcards
coefs$tstd[which(dumprobatsup<proba)]=NA
coefs$vals=dumcoefcards
coefs$proba=dumprobatsup

coefs

}#end def 





"zero"=
function(time,lty=2,lwd=1,col="black",val=0){
lines(time,rep(val,length(time)),type="l",lty=lty,lwd=lwd,col=col)}

"anom"=
function(dat,time=NULL,begref=NULL,endref=NULL){
if (is.null(time)==TRUE){anom=dat-mean(dat,na.rm=TRUE)}else{
anom=dat-mean(dat[which(time==begref):which(time==endref)],na.rm=TRUE)}
anom
}#end def anom



"linreg"=
function(x,y,weights=NULL){
if (is.null(weights)){param=lm(y~x)}else{param=lm(y~x,weights=weights)}
droite=list()
droite[["vals"]]=param$coefficients[2]*x + param$coefficients[1]
droite[["coefs"]]=param$coefficients
droite
}#end def linreg


"detrend"=
function(x,method="lin",dof=length(x)/20){
if (method=="lin"){
detr=x-linreg(1:length(x),x)$vals
}
if (method=="spline"){
detr=x-smth.spline.noNA(x,df=dof)$y
}
detr
}#end def detrend





"PDF"=
function(dat,nsteps=100,plot="TRUE",xlab="Values",spar=0.5){
lims=range(dat,na.rm=TRUE)
step=(lims[2]-lims[1])/nsteps
lgth=length(dat)

  dens=c()
  vals=c()
  for (i in 1:nsteps){
  inf=lims[1]+step*(i-1)
  sup=lims[1]+step*i
  dumdens=length(which(dat>inf & dat<sup))/lgth
  dens=c(dens,dumdens)

  dumvals=(lims[1]+step/2)+step*(i-1)
  vals=c(vals,dumvals)
  }#end for i

# Smoothing the density values
dens=smooth.spline(dens,spar=spar)$y


  # Display the PDF
  if (plot=="TRUE"){
  plot(vals,dens,type="l",xlab=xlab,ylab="Density",main="Probability Density Function")
  }else{
  res=list()
  res$dens=dens
  res$vals=vals
  res
  }#end if & else

}#end def PDF



"which.quantile"=
function(dat,value){
test=PDF(dat,nsteps=500,plot="FALSE")
cumul=0
for (i in 2:length(test$dens)){
cumul=c(cumul,sum(test$dens[1:i])/sum(test$dens))}#end for i
quant=cumul[which(abs(test$vals-value)==min(abs(test$vals-value)))]
round(quant,digits=3)*100
}#end def





# -- Replace the NA by a the mean of its two first neighbours
"fillNA"=
function(dat){
ind=which(is.finite(dat)==FALSE)
for (i in 1:length(ind)){
dat[ind[i]]=mean(c(dat[ind[i]-1],dat[ind[i]+1]))
}#end for i
dat
}# end def fillNA




# -- Smooth the TS with a Hamming window
"rollhamm"=
function(dat,window,p=2,time=1:length(dat)){
# Window width = must be a odd number
nyr=length(dat)
whamm=0.54 - 0.46*cos(((2*pi*(1:window)))/(window+1))

res=c()
for (i in 1:(nyr-window+1)){
dum=sum(dat[i:(i+window-1)]*whamm)/sum(whamm)
res=c(res,dum)
}#end for i

res=c(rep(NA,((window-1)/2)),res,rep(NA,((window-1)/2)))

if (p==1){
plot(time,dat,type="l",main="Black = yearly dataset
Red = Smoothed with the Hamming filter")
lines(time,res,type="l",col="red",lwd=2)
}else{
res
}#end if & else

}#end def rollhamm




# -- Smooth the TS with a Gaussian window
"rollgaussian"=
function(dat,window,p=2,time=1:length(dat),sigma=0.5){
# Window width = must be a odd number
nyr=length(dat)
n=0:(window-1)
N=window
gauss=exp(-0.5*((n-(N-1)/2)/(sigma*(N-1)/2))^2)

res=c()
for (i in 1:(nyr-window+1)){
dum=sum(dat[i:(i+window-1)]*gauss)/sum(gauss)
res=c(res,dum)
}#end for i

res=c(rep(NA,((window-1)/2)),res,rep(NA,((window-1)/2)))

if (p==1){
plot(time,dat,type="l",main="Black = yearly dataset
Red = Smoothed with the Gaussian filter")
lines(time,res,type="l",col="red",lwd=2)
}else{
res
}#end if & else

}#end def rollhamm



# -- Smooth the TS with a Gaussian window
"lanczos"=
function(dat,window,p=2,time=1:length(dat)){
# Window width = must be a odd number
"sinc"=function(x){sin(pi*x)/(pi*x)}

nyr=length(dat)
n=0:(window-1)
N=window
lanczoswin=sinc((2*n/(N-1))-1)

res=c()
for (i in 1:(nyr-window+1)){
dum=sum(dat[i:(i+window-1)]*lanczoswin)/sum(lanczoswin)
res=c(res,dum)
}#end for i

res=c(rep(NA,((window-1)/2)),res,rep(NA,((window-1)/2)))

if (p==1){
plot(time,dat,type="l",main="Black = yearly dataset
Red = Smoothed with the Lanczos window filter")
lines(time,res,type="l",col="red",lwd=2)
}else{
res
}#end if & else

}#end def rollhamm







# -- Smooth the TS with a Hamming window
"rollscore"=
function(dat1,dat2,window,time=1:length(dat1),level=95){
# Window width = must be a odd number
nyr=length(dat1)

dumres=list()

rescor=c()
signif90=c()
signif95=c()
signif99=c()
resmef=c()
resftest=c()

signif90=c()
signif95=c()
signif99=c()

for (i in 1:(nyr-window+1)){
tmpts1=dat1[i:(i+window-1)]
tmpts2=dat2[i:(i+window-1)]
dum=cor.test.ess(tmpts1,tmpts2)
dummef=mef(tmpts1,tmpts2)
dumftest=F.test(tmpts1,tmpts2,dum$Neff)

resftest=c(resftest,dumftest)
resmef=c(resmef,dummef)
rescor=c(rescor,dum$cor)
signif90=c(signif90,dum$signif90)
signif95=c(signif95,dum$signif95)
signif99=c(signif99,dum$signif99)

}#end for i

signif90=c(rep(NA,((window-1)/2)),signif90,rep(NA,((window-1)/2)))
signif95=c(rep(NA,((window-1)/2)),signif95,rep(NA,((window-1)/2)))
signif99=c(rep(NA,((window-1)/2)),signif99,rep(NA,((window-1)/2)))

dumres$signif90=signif90
dumres$signif95=signif95
dumres$signif99=signif99

rescor=c(rep(NA,((window-1)/2)),rescor,rep(NA,((window-1)/2)))
resmef=c(rep(NA,((window-1)/2)),resmef,rep(NA,((window-1)/2)))
resftest=c(rep(NA,((window-1)/2)),resftest,rep(NA,((window-1)/2)))


dumres$coef=rescor
dumres$mef=resmef
dumres$ftest=resftest


dumres$time=time
dumres

}#end def rollscore






# -- Performs an autocorrelation to measure the memory of the TS
"autocor"=
function(dat,lags=round((length(dat)/4),digits=0),p=TRUE,ylim="def"){
res=c()
test=c()
for (i in 1:lags){
dumres=cor.test(dat[1:(length(dat)-i)],dat[(i+1):length(dat)],na.omit=TRUE)
if (dumres[[3]]<0.001){
test=c(test,round(dumres[[4]],digits=6))
}else{
test=c(test,NA)
}#end if & else
res=c(res,round(dumres[[4]],digits=6))
}#end for i


if (p==TRUE){
if (ylim=="def"){ylims=c(min(res,na.rm=TRUE),max(res,na.rm=TRUE))}else{ylims=c(0,1)}
plot(1:lags,res,type="l",xlab="Lags",ylab="Autocorr. Coef",ylim=ylims)
lines(1:lags,test,type="p",col="blue",lwd=2)
zero(1:lags)
}else{
dum=list("res"=res,"test"=test)
dum}#end if & else

}#end def autocor



"lagcor"=
function(dat1,dat2,lags=round((length(dat1)/4),digits=0),p=TRUE,ylim=c(0,1)){
# !!! dat1 leads dat2
res=c()
for (i in -lags:lags){
if (i<0){dumres=cor(dat2[1:(length(dat1)-abs(i))],dat1[(abs(i)+1):length(dat1)],use="pairwise.complete.obs")}
if (i>=0){dumres=cor(dat1[1:(length(dat1)-i)],dat2[(i+1):length(dat1)],use="pairwise.complete.obs")}
res=c(res,round(dumres,digits=6))
}#end for i

if (p==TRUE){
plot(-lags:lags,res,type="l",xlab="Lags",ylab="Corr. Coef",ylim=ylim)
}else{
dum=list()
dum$lags=-lags:lags
dum$coef=res
dum
}#end if & else

}#end def autocor



"laglinreg"=
function(dat1,dat2,lagst=0,lags=round((length(dat1)/4),digits=0),p="TRUE",ylim=c(0,1)){
# !!! dat2 is a function of dat1
# !!! lag > 0 : dat1 leads dat2
# !!! lag < 0 : dat2 leads dat1
reg=c()
std=c()
for (i in lagst:lags){

    if (i>=0){
    x=dat1[1:(length(dat1)-i)]
    y=dat2[(i+1):length(dat1)]}

    if (i<0){
    x=dat1[(-i+1):length(dat1)]
    y=dat2[1:(length(dat1)+i)]}

dumreg=summary(lm(y~x))

if (dumreg$coefficients[[8]]<0.001){
reg=c(reg,round(dumreg$coefficients[[2]],digits=6))
std=c(std,round(dumreg$coefficients[[4]],digits=6))

}else{
reg=c(reg,NA)
}#end if & else
}#end for i

if (p=="TRUE"){
plot(lagst:lags,reg,type="l",xlab="Lags",ylab="Regr. Coef",ylim=ylim)
}else{
reg=list("coef"=reg,"std"=std);reg}#end if & else

}#end def autocor



"mvlaglinreg"=
function(dat1,dat2,lagst=0,lags=round((length(dat1)/4),digits=0),p="TRUE",ylim=c(0,1)){
# !!! dat2 is a function of dat1
# !!! lag > 0 : dat1 leads dat2
# !!! lag < 0 : dat2 leads dat1
reg1=c()
std1=c()
reg2=c()
std2=c()

for (i in lagst:lags){

if (i>=0){
x1=dat1[[1]][1:(length(dat1[[1]])-i)]
x2=dat1[[2]][1:(length(dat1[[1]])-i)]
y=dat2[(i+1):length(dat1[[1]])]}

if (i<0){
x1=dat1[[1]][(-i+1):length(dat1[[1]])]
x2=dat1[[2]][(-i+1):length(dat1[[1]])]
y=dat2[1:(length(dat1[[1]])+i)]}

dumreg=summary(lm(y~x1*x2))

if (dumreg$coefficients[[14]]<0.001){
reg1=c(reg1,round(dumreg$coefficients[[2]],digits=6))
std1=c(std1,round(dumreg$coefficients[[6]],digits=6))
}else{
reg1=c(reg1,NA)
std1=c(std1,NA)
}#end if & else

if (dumreg$coefficients[[15]]<0.001){
reg2=c(reg2,round(dumreg$coefficients[[3]],digits=6))
std2=c(std2,round(dumreg$coefficients[[7]],digits=6))
}else{
reg2=c(reg2,NA)
std2=c(std2,NA)
}#end if & else

}#end for i

reg=list("C1"=reg1,"std1"=std1,"C2"=reg2,"std2"=std2)
reg
}#end def autocor




# -- Autocorrelation with bootstrap
"bootautocor"=
function(dat,lags=length(dat)/2,nsim=100,nelts=round((length(dat)/10),digits=0),p="TRUE"){

  # - Preliminaires
nyears=length(dat)

  # - Bootstrap
boots=c()
for (i in 1:nsim){
ind=sample(1:nyears,nelts)
dumdat=dat
dumdat[ind]=NA
dumboot=autocor(dumdat,lags=lags,p="FALSE")
boots=rbind(boots,dumboot)
}#end for i

  # - Confidence interval
confint=apply(boots,2,sd,na.rm=TRUE)

  # - Reference
ref=apply(boots,2,mean,na.rm=TRUE)

  # - Display
dum=c(ref+confint,ref-confint)
ymax=max(dum,na.rm=TRUE)
ymin=min(dum[which(dum>0)],na.rm=TRUE)

if (p=="TRUE"){
plot(1:lags,ref,type="l",lwd=2,ylim=c(ymin,ymax),xlab="Lags",ylab="Autocorr. Coef",main=paste("Black line = Autocorrelation
Dashed blue lines = conf. int (2 SD, Bootstrap)
TS length = ",nyears," ; Replaced elts = ",nelts," ; BootS sim. = ",nsim,sep=""))
lines(1:lags,ref+confint,type="l",lty=2,col="blue")
lines(1:lags,ref-confint,type="l",lty=2,col="blue")
}else{
ref
}

}#end def bootautocor








# -- Autocorrelation with bootstrap
"bootlagcor"=
function(dat1,dat2,lags,nsim=100,nelts=round((length(dat1)/10),digits=0),p="TRUE"){

# - Preliminaires
nyears=length(dat1)

# - Bootstrap
boots=c()
for (i in 1:nsim){
ind=sample(1:nyears,nelts)
dumdat1=dat1
dumdat1[ind]=NA
dumboot=lagcor(dumdat1,dat2,lags=lags,p="FALSE")
boots=rbind(boots,dumboot)
}#end for i

# - Confidence interval
confint=apply(boots,2,sd,na.rm=TRUE)

# - Reference
ref=apply(boots,2,mean,na.rm=TRUE)

# - Display
dum=c(ref+confint,ref-confint)
ymax=max(dum,na.rm=TRUE)
ymin=min(dum[which(dum>0)],na.rm=TRUE)

plot(0:lags,ref,type="l",lwd=2,ylim=c(ymin,ymax),xlab="Lags",ylab="Corr. Coef",main=paste("Black line = Lagged correlation
Dashed blue lines = conf. int (2 SD, Bootstrap)
TS length = ",nyears," ; Replaced elts = ",nelts," ; BootS sim. = ",nsim,sep=""))
lines(0:lags,ref+confint,type="l",lty=2,col="blue")
lines(0:lags,ref-confint,type="l",lty=2,col="blue")

}#end def bootautocor


# -- Lagged linear regression with bootstrap
"bootlaglinreg"=
function(dat1,dat2,lags,nsim=100,nelts=round((length(dat1)/10),digits=0),p="TRUE"){
# !!! dat1 leads dat2

# - Preliminaires
nyears=length(dat1)

# - Bootstrap
boots=c()
for (i in 1:nsim){
ind=sample(1:nyears,nelts)
dumdat1=dat1
dumdat1[ind]=NA
dumboot=laglinreg(dumdat1,dat2,lags=lags,p="FALSE")
boots=rbind(boots,dumboot)
}#end for i

# - Confidence interval
confint=apply(boots,2,sd,na.rm=TRUE)

# - Reference
ref=apply(boots,2,mean,na.rm=TRUE)

# - Display
dum=c(ref+confint,ref-confint)
ymax=max(dum,na.rm=TRUE)
ymin=min(dum[which(dum>0)],na.rm=TRUE)

plot(0:lags,ref,type="l",lwd=2,ylim=c(ymin,ymax),xlab="Lags",ylab="Regr. Coef",main=paste("Black line = Lagged lin. Regression
Dashed blue lines = conf. int (2 SD, Bootstrap)
TS length = ",nyears," ; Replaced elts = ",nelts," ; BootS sim. = ",nsim,sep=""))
lines(0:lags,ref+confint,type="l",lty=2,col="blue")
lines(0:lags,ref-confint,type="l",lty=2,col="blue")

}#end def bootautocor







# - Samples a ts every step to perform a correlation with the good
# - number of degrees of freedom
"sampcor"=
function(dat,step=10){
samp=c()
nsteps=round(length(dat)/step,digits=0)
dumstep=0
for (i in 1:nsteps){
dumsamp=dat[1+dumstep]
dumstep=i*step
samp=c(samp,dumsamp)
}#end for
samp
}#end def sampcor




# - Draws a shaded area
"plotshaded"=
function(time,errinf,errsup,color,density=NULL){
#errinf=sdmanncpscruinf
#errsup=sdmanncpscrusup
newtime=time[which(is.finite(errinf)==TRUE)]
deb=which(time==newtime[1])
fin=which(time==newtime[length(newtime)])
x=c(time[deb:fin],time[fin],time[fin:deb],time[deb])
y=c(errinf[deb:fin],errsup[fin],errsup[fin:deb],errinf[deb])
polygon(x,y,col=color,border=NA,density=density)
}#end def plotshaded





# - Performs a surface grid cell weighted average
"wa"=
function(dat,lon,lat,mask=rep(1,ncol(dat))){
 # - List of the latitudes
list.lat=rep(lat,length(lon))
 # - Weights per grid cell taking into account the mask
pond=cos(list.lat*pi/180)*mask


if (length(dim(dat))==2){
# - Ponded field
pdd=t(pond*t(dat))
# - Ponded time serie
dum=apply(pdd,1,sum,na.rm=TRUE)/sum(pond,na.rm=TRUE)
}else{
pdd=pond*dat
dum=sum(pdd,na.rm=TRUE)/sum(pond,na.rm=TRUE)
}#end if & else
dum
}#end def wa



# - Performs a surface grid cell weighted average
"wa.area"=
function(dat,area,mask=1){

if (length(mask)==1){
if (length(dim(dat))==2){mask=rep(1,ncol(dat))}else{mask=rep(1,length(dat))}
}

 # - Weights per grid cell taking into account the mask
pond=area*mask


if (length(dim(dat))==2){
# - Ponded field
pdd=t(pond*t(dat))
# - Ponded time serie
dum=apply(pdd,1,sum,na.rm=TRUE)/sum(pond,na.rm=TRUE)
}else{
pdd=pond*dat
dum=sum(pdd,na.rm=TRUE)/sum(pond,na.rm=TRUE)
}#end if & else
dum
}#end def wa


# -- Variance ponderee
weighted.var <- function(x, w, na.rm = FALSE) {
    if (na.rm) {
        w <- w[i <- !is.na(x)]
        x <- x[i]
    }
    sum.w <- sum(w)
    sum.w2 <- sum(w^2)
    mean.w <- sum(x * w) / sum(w)
    (sum.w / (sum.w^2 - sum.w2)) * sum(w * (x - mean.w)^2, na.rm =
na.rm)
}


# -- Variance ponderer = Deuxieme methode
weighted.var2 <- function(x, w, na.rm = FALSE) {
    if (na.rm) {
        w <- w[i <- !is.na(x)]
        x <- x[i]
    }
    sum.w <- sum(w)
    (sum(w*x^2) * sum.w - sum(w*x)^2) / (sum.w^2 - sum(w^2))
} 




"mnmean"=
function(dat,DATA="MO",m1,m2,nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.mn=c()

if(length(dim(dat))==0 | length(dim(dat))==1){
for (yr in 1:nyear){
ind=which(time==yr & month==m1)
dum=mean(dat[ind:(ind+(m2-m1))],na.rm=TRUE)
dat.mn=c(dat.mn,dum)}}#end if and for


if(length(dim(dat))==2){
for (yr in 1:nyear){
ind=which(time==yr & month==1) ; print(ind:(ind+(m2-m1)))
dum=apply(dat[ind:(ind+(m2-m1)),],2,mean,na.rm=TRUE)
dat.mn=rbind(dat.mn,dum)}}#end if and for

dat.mn
}#end def daily.anmean





"mnmean.par"=
function(dat,DATA="MO",m1,m2,nyear,nproc=5,do_print=FALSE){
library(doMC)
registerDoMC(nproc)
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.mn=c()

if(length(dim(dat))==0 | length(dim(dat))==1){
for (yr in 1:nyear){
ind=which(time==yr & month==m1)
dum=mean(dat[ind:(ind+(m2-m1))],na.rm=TRUE)
dat.mn=c(dat.mn,dum)}}#end if and for


if(length(dim(dat))==2){
dat.mn=matrix(data=NA,nyear,ncol(dat))
nona=which(is.na(apply(dat,2,mean))==FALSE)
dat.tmp = foreach (yr=1:nyear,.combine=rbind,.inorder=TRUE) %dopar% { if (do_print==TRUE){print(yr)}
ind=which(time==yr & month==m1)
apply(dat[ind:(ind+(m2-m1)),nona],2,mean,na.rm=TRUE)}
dat.mn[,nona]=dat.tmp
}#end if and for

dat.mn

}#end def daily.anmean








# - Plots a weighted averaged ts of choosen area, taking into account a mask
"plot.zone"=
function(time=1:nrow(dat),dat,lon,lat,lonW,lonE,latS,latN,mask=rep(1,ncol(dat))){
titre=paste(lonE,"/",lonW,"degE  ",latS,"/",latN,"degN",sep="")
p=indice.zone(lon,lat,lonE,lonW,latS,latN)
ts=wa(dat[,p$ind.zone],p$lon,p$lat,mask[p$ind.zone])
plot(time,ts,type="l",bty="n",main=titre)
}#end def plot.zone



"ph"=
function(){
print("
lonE=
lonW=
latS=
latN=
time=
plot.zone(time,dat,lon,lat,lonW,lonE,latS,latN)
")
}


"funTS"=
function(time,TS,beg,end){
# Works with yearly datasets
if (time[1]>beg){
addeb=rep(NA,(time[1]-beg))
deb=1
}else{
addeb=NULL
deb=which(time==beg)
}#end if & else

if (time[length(time)]<end){
adfin=rep(NA,(end-time[length(time)]))
fin=length(time)
}else{
adfin=NULL
fin=which(time==end)
}#end if & else

ts=TS[deb:fin]
if (length(addeb)>0){ts=c(addeb,ts)}
if (length(adfin)>0){ts=c(ts,adfin)}

ts

}#end def funTS



"anmean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
time=rep(1:nyear,each=lgthyr)
dat.yr=c()
if(length(dim(dat))==0){
for (yr in 1:nyear){
dum=mean(dat[which(time==yr)],na.rm=TRUE)
dat.yr=c(dat.yr,dum)}}#end if and for
if(length(dim(dat))==1){
for (yr in 1:nyear){
dum=mean(dat[which(time==yr)],na.rm=TRUE)
dat.yr=c(dat.yr,dum)}}#end if and for
if(length(dim(dat))==2){
for (yr in 1:nyear){
dum=apply(dat[which(time==yr),],2,mean,na.rm=TRUE)
dat.yr=rbind(dat.yr,dum)}}#end if and for

dat.yr
}#end def daily.anmean


"winmean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.win=c()

if(length(dim(dat))==0){
for (yr in 2:(nyear-1)){
ind=which(time==(yr-1) & (month==12))
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==1){
for (yr in 2:(nyear-1)){
ind=which(time==(yr-1) & (month==12))
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==2){
for (yr in 2:(nyear-1)){
ind=which(time==(yr-1) & (month==12))
dum=apply(dat[ind:(ind+2),],2,mean,na.rm=TRUE)
dat.win=rbind(dat.win,dum)}}#end if and for

dat.win
}#end def daily.anmean


"ndjfmamean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.win=c()

if(length(dim(dat))==0){
for (yr in 2:(nyear-1)){
ind=which(time==(yr-1) & (month==11))
dum=mean(dat[ind:(ind+5)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==1){
for (yr in 2:(nyear-1)){
ind=which(time==(yr-1) & (month==11))
dum=mean(dat[ind:(ind+5)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==2){
for (yr in 2:(nyear-1)){
ind=which(time==(yr-1) & (month==11))
dum=apply(dat[ind:(ind+5),],2,mean,na.rm=TRUE)
dat.win=rbind(dat.win,dum)}}#end if and for

dat.win
}#end def daily.anmean





"summean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.win=c()

if(length(dim(dat))==0){
for (yr in 1:nyear){
ind=which(time==yr & month==6)
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==1){
for (yr in 1:nyear){
ind=which(time==yr & month==6)
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==2){
for (yr in 1:nyear){
ind=which(time==yr & month==6)
dum=apply(dat[ind:(ind+2),],2,mean,na.rm=TRUE)
dat.win=rbind(dat.win,dum)}}#end if and for

dat.win
}#end def daily.anmean


"sprmean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.win=c()

if(length(dim(dat))==0){
for (yr in 1:nyear){
ind=which(time==yr & month==3)
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==1){
for (yr in 1:nyear){
ind=which(time==yr & month==3)
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==2){
for (yr in 1:nyear){
ind=which(time==yr & month==3)
dum=apply(dat[ind:(ind+2),],2,mean,na.rm=TRUE)
dat.win=rbind(dat.win,dum)}}#end if and for

dat.win
}#end def daily.anmean


"autmean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.win=c()

if(length(dim(dat))==0){
for (yr in 1:nyear){
ind=which(time==yr & month==9)
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==1){
for (yr in 1:nyear){
ind=which(time==yr & month==9)
dum=mean(dat[ind:(ind+2)],na.rm=TRUE)
dat.win=c(dat.win,dum)}}#end if and for

if(length(dim(dat))==2){
for (yr in 1:nyear){
ind=which(time==yr & month==9)
dum=apply(dat[ind:(ind+2),],2,mean,na.rm=TRUE)
dat.win=rbind(dat.win,dum)}}#end if and for

dat.win
}#end def daily.anmean



"ASmean"=
function(dat,DATA="MO",nyear){
if(DATA=="MO"){lgthyr=12}
if(DATA=="DA"){lgthyr=360}
month=rep(1:12,length=nyear*12)
time=rep(1:nyear,each=lgthyr)

dat.AS=c()

if(length(dim(dat))==0){
for (yr in 1:nyear){
ind=which(time==yr & month==4)
dum=mean(dat[ind:(ind+5)],na.rm=TRUE)
dat.AS=c(dat.AS,dum)}}#end if and for

if(length(dim(dat))==1){
for (yr in 1:nyear){
ind=which(time==yr & month==4)
dum=mean(dat[ind:(ind+5)],na.rm=TRUE)
dat.AS=c(dat.AS,dum)}}#end if and for

if(length(dim(dat))==2){
for (yr in 1:nyear){
ind=which(time==yr & month==4)
dum=apply(dat[ind:(ind+5),],2,mean,na.rm=TRUE)
dat.AS=rbind(dat.AS,dum)}}#end if and for

dat.AS
}#end def daily.anmean



"smth.rollmean"=
function(dat,DATA="YR",window){
# the window parameter is in years !!!
# Must be impair
dum=rep(NA,length(dat))
if(length(which(is.finite(dat)=="FALSE"))==length(dat)){
# DO NOTHING
}else{
if(DATA=="YR"){base=1}#end if
if(DATA=="MO"){base=12}#end if
if(DATA=="WIN"){base=90}#end if

ind=which(is.finite(dat)=="TRUE")
dum[ind]=c(rep(NA,((window-1)/2)*base),rollmean(dat[ind],window*base),rep(NA,((window-1)/2))*base)
}#end if & else
dum

}#end def smth.rollmean



"over.thres"=
function(dat,DATA="YR",thres,window){
#print("!!!the window parameter is in years !!!")
# window must be impair
dum=rep(NA,length(dat))
if(length(which(is.finite(dat)=="FALSE"))==length(dat)){
# DO NOTHING
}else{
if(DATA=="YR"){base=1}#end if
if(DATA=="MO"){base=12}#end if
if(DATA=="DA"){base=360}#end if
if(DATA=="SEAS_DA"){base=90}#end if
if(DATA=="SEAS_MO"){base=3}#end if

ind=which(is.finite(dat)=="TRUE")

noccur=c()
for (i in (ind[1]:(ind[length(ind)]-(window-1)*base))){
dumind=i:(i+(window-1)*base)
dumnoccur=length(which(dat[dumind]>thres))
noccur=c(noccur,dumnoccur)
}#end for i

dum[ind]=c(rep(NA,((window-1)/2)*base),noccur,rep(NA,((window-1)/2)*base))

}#end if & else
dum




}#end def over.thres

"under.thres"=
function(dat,DATA="YR",thres,window){
#print("!!!the window parameter is in years !!!")
dum=rep(NA,length(dat))
if(length(which(is.finite(dat)=="FALSE"))==length(dat)){
# DO NOTHING
}else{
if(DATA=="YR"){base=1}#end if
if(DATA=="MO"){base=12}#end if
if(DATA=="DA"){base=360}#end if
if(DATA=="SEAS_DA"){base=90}#end if
if(DATA=="SEAS_MO"){base=3}#end if

ind=which(is.finite(dat)=="TRUE")

noccur=c()
for (i in (ind[1]:(ind[length(ind)]-(window-1)*base))){
dumind=i:(i+(window-1)*base)
dumnoccur=length(which(dat[dumind]<thres))
noccur=c(noccur,dumnoccur)
}#end for i

dum[ind]=c(rep(NA,((window-1)/2)*base),noccur,rep(NA,((window-1)/2)*base))

}#end if & else
dum

}#end def over.thres



"smth.rollsd"=
function(dat,DATA="YR",window){
# the window parameter is in years !!!
if(DATA=="YR"){base=1}#end if
if(DATA=="MO"){base=12}#end if

datsd=array(data=NA,length(dat))

win=window*base/2
ind=which(dat!="NA")
ind=ind[win:(length(which(dat!="NA"))-win)]

dumsd=c()
for (i in ind){
dum=sd(dat[(i-(win-1)):(i+win)],na.rm=TRUE)
dumsd=c(dumsd,dum)
}#end for i
datsd[ind]=smooth.spline(dumsd[which(dumsd!="NA")],spar=0.1)$y
datsd
}#end def smth.rollsd




"borne"=
function(champ,liminf,limsup){
         champ[which(champ>limsup)]=limsup
         champ[which(champ<liminf)]=liminf
champ
}#end def borne



"indice.point" =
function(lon,lat,lonp,latp){
  nearest.lon=abs(lon-lonp)
  nearest.lat=abs(lat-latp)
  nlon=lon[which(nearest.lon==min(nearest.lon))]
  nlat=lat[which(nearest.lat==min(nearest.lat))]
  list.lat=rep(lat,length(lon))
  list.lon=rep(lon,each=length(lat))
  indice=which(list.lon==nlon & list.lat==nlat)
  indice
}# end def indice.point






"indice.zone" =
function(lon,lat,loninf,lonsup,latinf,latsup){
#print("Warning!!! Latitudes have to be sorted from North to South")

  # Creation de list.lon et list.lat
  list.lat=rep(lat,length(lon))
  list.lon=rep(lon,each=length(lat))

  #extraction des valeurs de lon et lat les plus proches des loninf,lonsup...
  if (length(which(lon==loninf))==1){lonW=which(lon==loninf)}else{
  nearest.loninf=abs(lon-loninf)
  loninf=lon[which(nearest.loninf==min(nearest.loninf))]
  ind1=which(nearest.loninf==sort(nearest.loninf)[1])
  ind2=which(nearest.loninf==sort(nearest.loninf)[2])
  lonW=min(c(ind1,ind2))}

  if (length(which(lon==lonsup))==1){lonE=which(lon==lonsup)}else{
  nearest.lonsup=abs(lon-lonsup)
  lonsup=lon[which(nearest.lonsup==min(nearest.lonsup))]
  ind3=which(nearest.lonsup==sort(nearest.lonsup)[1])
  ind4=which(nearest.lonsup==sort(nearest.lonsup)[2])
  lonE=max(c(ind3,ind4))}

  if (length(which(lat==latinf))==1){latN=which(lat==latinf)}else{
  nearest.latinf=abs(lat-latinf)
  latinf=lat[which(nearest.latinf==min(nearest.latinf))]
  ind5=which(nearest.latinf==sort(nearest.latinf)[1])
  ind6=which(nearest.latinf==sort(nearest.latinf)[2])
  latN=max(c(ind5,ind6))}

  if (length(which(lat==latsup))==1){latS=which(lat==latsup)}else{
  nearest.latsup=abs(lat-latsup)
  latsup=lat[which(nearest.latsup==min(nearest.latsup))]
  ind7=which(nearest.latsup==sort(nearest.latsup)[1])
  ind8=which(nearest.latsup==sort(nearest.latsup)[2])
  latS=min(c(ind7,ind8))}
  
  # recuperation des longitudes et latitudes (dans lon et lat) comprises entre
  # les bornes sup et inf
  ilon=lon[lonW:lonE]
  jlat=lat[latN:latS]
  l.ilon=length(ilon)
  l.jlat=length(jlat)
  ind.zone=array(data=0,l.ilon*l.jlat)

  # recuperation des indices des points qui appartiennent a la zone
  for (i in 1:l.ilon){
   for (j in 1:l.jlat){
     ind.zone[j+(l.jlat*(i-1))]=which(list.lon==ilon[i] & list.lat==jlat[j])
   }#end for j
  }#enf for i
ind.zone=list("ind.zone"=ind.zone,"lon"=ilon,"lat"=jlat)
ind.zone
}# end def indice.zone


"indice.zone.v2" =
function(lon,lat,lonW,lonE,latS,latN){
#print("Warning!!! Latitudes have to be sorted from North to South")

  # Creation de list.lon et list.lat
  list.lat=rep(lat,length(lon))
  list.lon=rep(lon,each=length(lat))

  if (lonW>lonE){
  ind=which((list.lon<=lonE | list.lon>=lonW) & list.lat>=latS & list.lat<=latN)
  new.lon=which(lon<=lonE | lon>=lonW)
  new.lat=which(lat>=latS & lat<=latN)
  }else{
  ind=which(list.lon<=lonE & list.lon>=lonW & list.lat>=latS & list.lat<=latN)
  new.lon=which(lon<=lonE & lon>=lonW)
  new.lat=which(lat>=latS & lat<=latN)
  }#end

ind.zone=list("ind.zone"=ind,"lon"=new.lon,"lat"=new.lat)

ind.zone

}# end def indice.zone










"indice.zonal" =
function(lat,presnivs,latinf,latsup,presnivsinf,presnivssup){
#print("Warning!!! Latitudes have to be sorted from North to South")

  # Creation de list.lat et list.presnivs
  list.presnivs=rep(presnivs,length(lat))
  list.lat=rep(lat,each=length(presnivs))

  #extraction des valeurs de lat et presnivs les plus proches des latinf,latsup...
  if (length(which(trunc(lat)==latinf))==1){latS=which(trunc(lat)==latinf)}else{
  nearest.latinf=abs(lat-latinf)
  latS=which(nearest.latinf==min(nearest.latinf))}#

  #extraction des valeurs de lat et presnivs les plus proches des latinf,latsup...
  if (length(which(trunc(lat)==latsup))==1){latN=which(trunc(lat)==latsup)}else{
  nearest.latsup=abs(lat-latsup)
  latN=which(nearest.latsup==min(nearest.latsup))}#




  #extraction des valeurs de lat et presnivs les plus proches des latinf,latsup...
  if (length(which(trunc(presnivs)==presnivsinf))==1){presnivsL=which(trunc(presnivs)==presnivsinf)}else{
  nearest.presnivsinf=abs(presnivs-presnivsinf)
  presnivsL=which(nearest.presnivsinf==min(nearest.presnivsinf))}#

  #extraction des valeurs de lat et presnivs les plus proches des latinf,latsup...
  if (length(which(trunc(presnivs)==presnivssup))==1){presnivsH=which(trunc(presnivs)==presnivssup)}else{
  nearest.presnivssup=abs(presnivs-presnivssup)
  presnivsH=which(nearest.presnivssup==min(nearest.presnivssup))}#


  
  # recuperation des latgitudes et presnivsitudes (dans lat et presnivs) comprises entre
  # les bornes sup et inf
  ilat=lat[latN:latS]
  jpresnivs=presnivs[presnivsL:presnivsH]
  l.ilat=length(ilat)
  l.jpresnivs=length(jpresnivs)
  ind.zone=array(data=0,l.ilat*l.jpresnivs)

  # recuperation des indices des points qui appartiennent a la zone
  for (i in 1:l.ilat){
   for (j in 1:l.jpresnivs){
     ind.zone[j+(l.jpresnivs*(i-1))]=which(list.lat==ilat[i] & list.presnivs==jpresnivs[j])
   }#end for j
  }#enf for i
ind.zone=list("ind.zone"=ind.zone[length(ind.zone):1],"lat"=ilat,"presnivs"=jpresnivs)
ind.zone
}# end def indice.zone




"lat.time.plot"=
function(time,latF,champ,titre="",Ichange=numeric(0),
         zlev=seq(min(champ,na.rm=TRUE),max(champ,na.rm=TRUE),length=22),
         transpose=FALSE,mar=c(5,5,5,6),legend=TRUE,xlab="Years",
         ylab="Latitude")
{
ldpal=colorRampPalette(c("blue", "white"),space = "Lab")
ldpal2=colorRampPalette(c("black", "turquoise", "white"),space = "Lab")
hdpal=colorRampPalette(c("white", "yellow", "red", "black"),space = "Lab")
hdpal2=colorRampPalette(c("white", "yellow", "green", "darkblue"),space = "Lab")
pnpal=colorRampPalette(c("navyblue","blue","white","red","black"),space = "Lab")

col10=rainbow(length(zlev)-1,start=0,end=2/6)
#par( mar=c(10,5,5,5))
par(mar=mar)
if(length(Ichange)>0) champ[Ichange]=1
if (transpose)
  dum=t(matrix(champ,length(latF),length(time)))
else
  dum=matrix(champ,length(time),length(latF))
latF.sort=sort(latF,index.return=TRUE)
image(time,sort(latF),dum[,latF.sort$ix],col=pnpal(21),
       xlab=xlab,ylab=ylab,main=titre,breaks=zlev)
if(legend) image.plot(dum[,length(latF):1],col=pnpal(21)
      , legend.only=TRUE,zlim=range(zlev))
}





"image.zonmean"=
function(lat,presnivs,dat,zlim=c(min(dat,na.rm=TRUE),max(dat,na.rm=TRUE)),int=(zlim[2]-zlim[1])/20,colpal=BR,yaxis=round(c(min(presnivs),max(presnivs),(max(presnivs)-min(presnivs))/5),digits=0),legend=TRUE,titre="",mar=c(5,5,5,6),xlab="Latitude",ylab="Pressure (mb)",cex=1,legend.width=1.2,smallplot=NULL,select=FALSE){
source("~/Rtools/Rpalettes.R")
dum=dat ; dim(dum)=c(length(presnivs),length(lat)) ; dum=t(dum)
par(mar=mar)
par(cex=cex)
if (select==FALSE){
zlev=seq(zlim[1],zlim[2],int)
image(sort(lat),sort(-presnivs),dum[,length(presnivs):1],yaxt="n",col=colpal(length(zlev)-1),xlab=xlab,ylab=ylab,main=titre,breaks=zlev)
}else{
image(sort(lat),sort(-presnivs),dum,yaxt="n",col=colpal(21),xlab=xlab,ylab=ylab,main=titre,breaks=zlev)
}#end if & else

axis(2,at=seq(-yaxis[2],-yaxis[1],by=yaxis[3]),labels=sort(seq(yaxis[1],yaxis[2],by=yaxis[3]),decreasing=TRUE))
if(legend==TRUE){image.plot(dum,col=colpal(length(zlev)-1),legend.only=TRUE,zlim=zlim,legend.width=legend.width,smallplot=smallplot)}
#,length(presnivs):1 ; length(lat):1
}

"add.legend"=
function(dat,zlim=c(min(dat,na.rm=TRUE),max(dat,na.rm=TRUE)),int=(zlim[2]-zlim[1])/20,colpal=BR,legend.width=1.2){
image.plot(dat,col=colpal(length(seq(zlim[1],zlim[2],by=int))-1),legend.only=TRUE,zlim=zlim,legend.width=legend.width,smallplot=NULL)
}




"contour.zonmean"=
function(lat,presnivs,dat,col="black",lty=1,lwd=1,labs=TRUE,nlevels="all",levels="all",select=FALSE){
dum=dat ; dim(dum)=c(length(presnivs),length(lat)) ; dum=t(dum)
if (select==FALSE){
if (nlevels=="all" & levels=="all"){
contour(sort(lat),sort(-presnivs),dum[,length(presnivs):1],add=TRUE,col=col,lty=lty,lwd=lwd,drawlabels=labs)}else{
contour(sort(lat),sort(-presnivs),dum[,length(presnivs):1],add=TRUE,col=col,lty=lty,lwd=lwd,nlevels=nlevels,levels=levels,drawlabels=labs)}
}else{
if (nlevels=="all" & levels=="all"){
contour(sort(lat),sort(-presnivs),dum,add=TRUE,col=col,lty=lty,lwd=lwd,drawlabels=labs)}else{
contour(sort(lat),sort(-presnivs),dum[,length(presnivs):1],add=TRUE,col=col,lty=lty,lwd=lwd,nlevels=nlevels,levels=levels,drawlabels=labs)}
}#end if
}





"savenc"=
function(VALS,DIMS,ncname,outdir,units="",longname="",world=FALSE,scal=list(),scalinfos="",scalunits="",timeunits="",transpose=TRUE,multivar=FALSE){

   varnc=list()
   scalar=list()

   if (multivar==FALSE){
   nvars=1
   }else{
   nvars=length(VALS)
   }#end if multivar


   for (z in 1:nvars){
   if (multivar==FALSE){
   vals=VALS
   dims=DIMS
   }else{
   vals=VALS[[z]]
   dims=DIMS[[z]]
   }#end if multivar
 

    # L'option world permet un affichage centre sur le 0 avec grads -

    # vals est une liste des variables lon*lat a mettre dans --------
    # le fichier  ---------------------------------------------------
    varname=names(vals)
    scaname=names(scal)

 
    dim.list=list()
    for (d in 1:length(dims)){
    DIMNAMES=names(dims)[d]
    if (DIMNAMES=="lon"){
       if (world==FALSE){long=dims$lon}else{long=dims$lon[2:length(dims$lon)]}
       if (lon[1]>=0 & world==TRUE){long=long-180}
    D=dim.def.ncdf("lon","degrees_east",long,create_dimvar=TRUE)}

    if (DIMNAMES=="lat"){
    D=dim.def.ncdf("lat","degrees_north",dims$lat,create_dimvar=TRUE)}

    if (DIMNAMES=="x"){
    D=dim.def.ncdf("x","",dims$x,create_dimvar=TRUE)}

    if (DIMNAMES=="y"){
    D=dim.def.ncdf("y","",dims$y,create_dimvar=TRUE)}

    if (DIMNAMES=="deptht"){
    D=dim.def.ncdf("deptht","meters",dims$deptht,create_dimvar=TRUE)}

    if (DIMNAMES=="depth"){
    D=dim.def.ncdf("depth","meters",dims$depth,create_dimvar=TRUE)}

    if (DIMNAMES=="depthw"){
    D=dim.def.ncdf("depthw","meters",dims$depthw,create_dimvar=TRUE)}

    if (DIMNAMES=="AXSIGMA"){
    D=dim.def.ncdf("AXSIGMA","Sigma",dims$AXSIGMA,create_dimvar=TRUE)}

    if (DIMNAMES=="levels"){
    D=dim.def.ncdf("levels","pressure_mb",dims$levels,create_dimvar=TRUE)}

    if (DIMNAMES=="time"){
    D=dim.def.ncdf("time",timeunits,dims$time,unlim=TRUE,create_dimvar=TRUE)}

    if (DIMNAMES=="lags"){
    D=dim.def.ncdf("lags",timeunits,dims$lags,unlim=TRUE,create_dimvar=TRUE)}

    if (DIMNAMES=="time_counter"){
    D=dim.def.ncdf("time_counter",timeunits,dims$time,unlim=TRUE,create_dimvar=TRUE)}

    dim.list[[d]]=D
    }#end for d

# - Boucle sur les matrices lon*lat
for (i in 1:length(vals)){
    # Definition de la variable -------------------------------------
    if (is.list(longname)==FALSE){
    varnc[[varname[i]]]=var.def.ncdf(varname[i],units=units,dim.list,
                       missval=2*10^30,longname="")
    }else{
    varnc[[varname[i]]]=var.def.ncdf(varname[i],units=units[[varname[i]]],dim.list,
                       missval=2*10^30,longname=longname[[varname[i]]])}
}#end i

}#end for z


    # Ouverture du fichier netcdf -----------------------------------
    ncnew=create.ncdf(paste(outdir,ncname,sep=""),varnc)


   for (z in 1:nvars){
   if (multivar==FALSE){
   vals=VALS
   dims=DIMS
   }else{
   vals=VALS[[z]]
   dims=dim.list=DIMS[[z]]
   }#end if multivar
 
    varname=names(vals)

# - Boucle sur les matrices lon*lat
for (i in 1:length(vals)){

    mat=vals[[varname[i]]]

    # Serie temporelle
    if (length(dims)==1){
    mat[which(is.finite(mat)==FALSE)]=2*10^30
    put.var.ncdf(ncnew,varname[i],mat,start=NA,count=length(mat))
    }#end if (length(dims)==1)

    # Lat-temps / profondeur-temps
    if (length(dims)==2){
    lenD1=length(dims[[names(dims)[1]]])
    lenD2=length(dims[[names(dims)[2]]])
    if (transpose==TRUE){
    dim(mat)=c(lenD2,lenD1)
    mat=t(mat)}
    mat[which(is.finite(mat)==FALSE)]=2*10^30
    put.var.ncdf(ncnew,varname[i],mat,start=NA,count=dim(mat))
    }#end if (length(dims)==2)

    # Lon/lat/temps
    if (length(dims)==3){
    lenD1=length(dims[[names(dims)[1]]])
    lenD2=length(dims[[names(dims)[2]]])
    lenD3=length(dims[[names(dims)[3]]])

    dum=t(vals[[varname[i]]])
    dim(dum)=c(lenD2,lenD1,lenD3)
    mat=rep(0,length(dum))
    dim(mat)=c(lenD1,lenD2,lenD3)
    for (w in 1:nrow(vals[[varname[i]]])){
    mat[,,w]=t(dum[,,w])
    }#end for y
    mat[which(is.finite(mat)=="FALSE")]=2*10^30
    put.var.ncdf(ncnew,varname[i],mat,start=NA,count=dim(mat))
    }#end if (length(dims)==3)
    # Lon/lat/depth/time


    # Lon/lat/depth/temps
    if (length(dims)==4){
    lenD1=length(dims[[names(dims)[1]]])
    lenD2=length(dims[[names(dims)[2]]])
    lenD3=length(dims[[names(dims)[3]]])
    lenD4=length(dims[[names(dims)[4]]])

    Mmat=rep(NA,lenD4*lenD3*lenD2*lenD1)
    dim(Mmat)=c(lenD1,lenD2,lenD3,lenD4)
    for (k in 1:lenD3){
    dum=t(vals[[varname[i]]][,k,])
    dim(dum)=c(lenD2,lenD1,lenD4)
    mat=rep(0,length(dum))
    dim(mat)=c(lenD1,lenD2,lenD4)
    for (w in 1:lenD4){
    mat[,,w]=t(dum[,,w])
    }#end for w
    Mmat[,,k,]=mat
    }#end for k
    Mmat[which(is.finite(Mmat)==FALSE)]=2*10^30
    put.var.ncdf(ncnew,varname[i],Mmat,start=NA,count=dim(Mmat))
    }#end if (length(dims)==4)

}#end i


}#end for z (multivar)


  # - Fermeture du fichier netcdf
    close.ncdf(ncnew)

}# end def savenc




