source(paste(main_dir,"/scripts/Rtools/Rpalettes.R",sep=""))
library(fields)
source(paste(main_dir,"/scripts/Rtools/function.R",sep=""))

"flip.plot"=
function(dat,lon,lat){
dim(dat)=c(length(lat),length(lon)) ; dat=t(dat)
dat
}



"quickmap2"=
function(DAT,period=NULL,flip=TRUE,levs=NULL,zmax=max(dat,na.rm=TRUE),int=NULL,pal=CORREL,posneg=FALSE,mar=c(4,5,4,2),cex=1,
         intlon=NULL,intlat=NULL,lonW=NULL,lonE=NULL,latS=NULL,latN=NULL,additionnals=c(),
	 UpperLeftTitle=NULL,LowerLeftTitle=NULL,UpperRightTitle=NULL,LowerRightTitle=NULL,no_legend=FALSE,
	 fun=NULL,inv=TRUE,fill.cont=FALSE,shift=NULL,help=FALSE){

if (help==TRUE){
print(" ### Available arguments ###")
print("levs = seq(binf,bsup,by=int) => levels of the color palette")
print("pal = CORREL  => color palette (see in Rpalette.R)")
print("UpperLeftTitle => character string for the upper left title ; file name by default")
print("LowerLeftTitle => character string for the lower left title ; variable name by default")
print("shift => add a scalar to the plotted field")
print("fill.cont = TRUE (FALSE by default) => add contours to the plot")
print("additionnals => additionnal layers to the plot (as in filled.contour3)")
print("no_legend (FALSE by default) => if set to true, avoid the key and allows for multiplot")
}


dat=DAT$dat
lon=DAT$lon
lat=DAT$lat
file=DAT$file


if (is.null(period) & is.null(fun)) fun="mean"

if (is.null(shift)==FALSE){dat=dat+shift}

if (is.null(LowerLeftTitle)) LowerLeftTitle=paste("Variable =",DAT$varname)
if (is.null(UpperLeftTitle)){dum=strsplit(file,"/") ; UpperLeftTitle=dum[[1]][length(dum[[1]])] }
if (is.null(LowerRightTitle)){
   if (is.null(period)){
     if (is.null(dim(dat))){
        LowerRightTitle="2D Field"
        }else{
        prd=paste(1,nrow(dat),sep=":")
        LowerRightTitle=paste(fun," ; Prd = ",prd,sep="")
     }#end is.null(dim(dat))
   }else{
      if (length(period)==1){LowerRightTitle=paste("Time Step =",period)
      }else{
      prd=paste(period[1],period[length(period)],sep=":")
      LowerRightTitle=paste(fun," ; Prd=",prd,sep="")
      }#end if (length(period)==1)
   }#end if is.null(period)
}#end if is.null(LowerRightTitle)



lon=sort(lon,decreasing=FALSE)
lat=sort(lat,decreasing=FALSE)
if (is.null(lonW)) lonW=round(lon[1],digits=-1)
if (is.null(lonE)) lonE=round(lon[length(lon)],digits=-1)
if (is.null(latS)) latS=round(lat[1],digits=-1)
if (is.null(latN)) latN=round(lat[length(lat)],digits=-1)
range.lon=lonE-lonW
if (is.null(intlon)){
if (range.lon<50){intlon=5}
if (range.lon>=50 & range.lon<150){intlon=10}
if (range.lon>=150){intlon=25}
}
range.lat=latN-latS
if (is.null(intlat)){
if (range.lat<50){intlat=5}
if (range.lat>=50 & range.lat<100){intlat=10}
if (range.lat>=100){intlat=20}
}


if (is.null(dim(dat))==FALSE){
time=1:nrow(dat)
if (is.null(period)){period=1:nrow(dat)
}else{
time=time[period]
dat=dat[period,]}
if (is.null(fun)==FALSE){dat=apply(dat,2,get(fun))}
}#end is.null(dim(dat))==FALSE


# -- rajouter le calcul sur variables saisonnieres

dumdat=flip.plot(dat,lon,lat)
if (inv==TRUE){dumdat=dumdat[,length(lat):1]}

source("/home/users/jservon/Evaluation/R_scripts/Rpalettes.R")
if (is.null(levs)){
if (posneg==TRUE){binf=-zmax ; bsup=zmax}else{binf=min(dumdat,na.rm=TRUE) ; bsup=max(dumdat,na.rm=TRUE)}
if (is.null(int)){if (posneg==TRUE){int=zmax/10}else{int=(max(dumdat,na.rm=TRUE)-min(dumdat,na.rm=TRUE))/20}}
levs=seq(binf,bsup,by=int)
}

dumdat=borne(dumdat,levs[1],levs[length(levs)])


library(maps)
land=map('world2',ylim=range(lat),xlim=range(lon),interior=FALSE,plot=FALSE)
par(mar=mar,cex=cex)

#dum.cont=list()
#if (fill.cont){dum.cont[["cont"]]=c()}else{dum.cont[["cont"]]=contour(lon,lat,dumdat,levels=levels,col="darkgrey",lwd=0.7,add=T,labels=NULL)}

if (no_legend==TRUE){
filled.contour3(lon,lat,dumdat,color.palette=pal,levels=levs,plot.axes=c(
		if (max(lon)>180){lines(land$x,land$y)}else{
		world(range(lon),range(lat),add=T)},
                if (fill.cont){contour(lon,lat,dumdat,levels=levs,col="darkgrey",lwd=0.7,add=T,labels=NULL)},
		axis(2,at=seq(latS,latN,by=intlat)),
	        axis(1,at=seq(lonW,lonE,by=intlon)),
	        mtext(UpperLeftTitle,side=3,line=2.5,adj=0,cex=1.2,font=2),
	        mtext(LowerLeftTitle,side=3,line=1,adj=0,cex=1),
		mtext(UpperRightTitle,line=1,adj=1),
	        mtext(LowerRightTitle,line=1,adj=1),
	        mtext("Longitude",side=1,line=2.5),mtext("Latitude",side=2,line=2.5,las=3),
		additionnals
                ))
}else{
filled.contour(lon,lat,dumdat,color.palette=pal,levels=levs,plot.axes=c(
		if (max(lon)>180){lines(land$x,land$y)}else{
		world(range(lon),range(lat),add=T)},
                if (fill.cont){contour(lon,lat,dumdat,levels=levs,col="darkgrey",lwd=0.7,add=T,labels=NULL)},
		axis(2,at=seq(latS,latN,by=intlat)),
		axis(1,at=seq(lonW,lonE,by=intlon)),
		mtext(UpperLeftTitle,side=3,line=2.5,adj=0,cex=1.2,font=2),
		mtext(LowerLeftTitle,side=3,line=1,adj=0,cex=1),
		mtext(UpperRightTitle,line=1,adj=1),
		mtext(LowerRightTitle,line=1,adj=1),
		mtext("Longitude",side=1,line=2.5),mtext("Latitude",side=2,line=2.5,las=3),
		additionnals
		))
}



}




"quickmap"=
function(lon,lat,dat,flip=TRUE,zmax=max(dat,na.rm=TRUE),int=NULL,pal=CORREL,posneg=FALSE,mar=c(4,5,4,2),cex=1,
         intlon=NULL,intlat=NULL,lonW=NULL,lonE=NULL,latS=NULL,latN=NULL,additionnals=c(),
	 UpperLeftTitle="",LowerLeftTitle="",UpperRightTitle="",LowerRightTitle="",no_legend=FALSE){

dumdat=flip.plot(dat,lon,lat)

lon=sort(lon,decreasing=FALSE)
lat=sort(lat,decreasing=FALSE)
if (is.null(lonW)) lonW=round(lon[1],digits=-1)
if (is.null(lonE)) lonE=round(lon[length(lon)],digits=-1)
if (is.null(latS)) latS=round(lat[1],digits=-1)
if (is.null(latN)) latN=round(lat[length(lat)],digits=-1)
range.lon=lonE-lonW
if (is.null(intlon)){
if (range.lon<50){intlon=5}
if (range.lon>=50 & range.lon<150){intlon=10}
if (range.lon>=150){intlon=25}
}
range.lat=latN-latS
if (is.null(intlat)){
if (range.lat<50){intlat=5}
if (range.lat>=50 & range.lat<100){intlat=10}
if (range.lat>=100){intlat=20}
}


source("/home/users/jservon/Evaluation/R_scripts/Rpalettes.R")
if (posneg==TRUE){binf=-zmax ; bsup=zmax}else{binf=min(dat) ; bsup=max(dat)}

if (is.null(int)){if (posneg==TRUE){int=zmax/10}else{int=(max(dat)-min(dat))/20}}
levels=seq(binf,bsup,by=int)

dumdat=borne(dumdat,binf,bsup)

library(maps)
land=map('world',ylim=range(lat),xlim=range(lon),interior=FALSE,plot=FALSE)
par(mar=mar,cex=cex)
if (no_legend==TRUE){
filled.contour3(lon,sort(lat,decreasing=FALSE),dumdat,color.palette=pal,levels=levels,plot.axes=c(
                contour(lon,lat,dumdat,levels=levels,col="darkgrey",lwd=0.7,add=T,labels=NULL),
#               lines(land$x,land$y),
                world(range(lon),range(lat),add=T),
		axis(2,at=seq(latS,latN,by=intlat)),
		axis(1,at=seq(lonW,lonE,by=intlon)),
		mtext(UpperLeftTitle,side=3,line=2.5,adj=0,cex=1.2,font=2),
		mtext(LowerLeftTitle,side=3,line=1,adj=0,cex=1),
		mtext(UpperRightTitle,line=1,adj=1),
		mtext(LowerRightTitle,line=1,adj=1),
		mtext("Longitude",side=1,line=2.5),mtext("Latitude",side=2,line=2.5,las=3),
		additionnals
		))
}else{
filled.contour(lon,sort(lat,decreasing=FALSE),dumdat,color.palette=pal,levels=levels,plot.axes=c(
               contour(lon,lat,dumdat,levels=levels,col="darkgrey",lwd=0.7,add=T,labels=NULL),
	       #               lines(land$x,land$y),
	       world(range(lon),range(lat),add=T),
	       axis(2,at=seq(latS,latN,by=intlat)),
	       axis(1,at=seq(lonW,lonE,by=intlon)),
	       mtext(UpperLeftTitle,side=3,line=2.5,adj=0,cex=1.2,font=2),
	       mtext(LowerLeftTitle,side=3,line=1,adj=0,cex=1),
	       mtext(UpperRightTitle,line=1,adj=1),
	       mtext(LowerRightTitle,line=1,adj=1),
	       mtext("Longitude",side=1,line=2.5),mtext("Latitude",side=2,line=2.5,las=3),
	       additionnals
	       ))

}

}









filled.contour3 <-
  function (x = seq(0, 1, length.out = nrow(z)),
            y = seq(0, 1, length.out = ncol(z)), z, xlim = range(x, finite = TRUE), 
	    ylim = range(y, finite = TRUE), zlim = range(z, finite = TRUE), 
	    levels = pretty(zlim, nlevels), nlevels = 20, color.palette = cm.colors, 
	    col = color.palette(length(levels) - 1), plot.title, plot.axes, 
	    key.title, key.axes, asp = NA, xaxs = "i", yaxs = "i", las = 1, 
	    axes = TRUE, frame.plot = axes,mar, ...) 
	    {
	    
	    # modification by Ian Taylor of the filled.contour function
	    # to remove the key and facilitate overplotting with contour()
	    # further modified by Carey McGilliard and Bridget Ferris
	    # to allow multiple plots on one page

            if (missing(z)) {
	    if (!missing(x)) {
	    if (is.list(x)) {
	    z <- x$z
	    y <- x$y
	    x <- x$x
	    }else {
	    z <- x
	    x <- seq.int(0, 1, length.out = nrow(z))
	    }
	    }
	    else stop("no 'z' matrix specified")
	    }
	    else if (is.list(x)) {
	    y <- x$y
	    x <- x$x
	    }
	    if (any(diff(x) <= 0) || any(diff(y) <= 0)) 
	    stop("increasing 'x' and 'y' values expected")
	    # mar.orig <- (par.orig <- par(c("mar", "las", "mfrow")))$mar
	    # on.exit(par(par.orig))
	    # w <- (3 + mar.orig[2]) * par("csi") * 2.54
	    # par(las = las)
	    # mar <- mar.orig
	    plot.new()
	    # par(mar=mar)
	    plot.window(xlim, ylim, "", xaxs = xaxs, yaxs = yaxs, asp = asp)
	    if (!is.matrix(z) || nrow(z) <= 1 || ncol(z) <= 1) 
	    stop("no proper 'z' matrix specified")
	    if (!is.double(z)) 
	    storage.mode(z) <- "double"
	    #.Internal(filledcontour(as.double(x), as.double(y), z, as.double(levels), 
	    #col = col))
            .filled.contour(as.double(x), as.double(y), z, as.double(levels),
            col = col)
	    if (missing(plot.axes)) {
	    if (axes) {
	    title(main = "", xlab = "", ylab = "")
	    Axis(x, side = 1)
	    Axis(y, side = 2)
	    }
	    }
	    else plot.axes
	    if (frame.plot) 
	    box()
	    if (missing(plot.title)) 
	    title(...)
	    else plot.title
	    invisible()
}

#}


filled.legend <-
  function (x = seq(0, 1, length.out = nrow(z)), y = seq(0, 1, 
            length.out = ncol(z)), z, xlim = range(x, finite = TRUE), 
	    ylim = range(y, finite = TRUE), zlim = range(z, finite = TRUE), 
	    levels = pretty(zlim, nlevels), nlevels = 20, color.palette = cm.colors, 
	    col = color.palette(length(levels) - 1), plot.title, plot.axes, 
	    key.title, key.axes, asp = NA, xaxs = "i", yaxs = "i", las = 1, 
	    axes = TRUE, frame.plot = axes, ...) 
	    {
	    # modification of filled.contour by Carey McGilliard and Bridget Ferris
	    # designed to just plot the legend
	    if (missing(z)) {
	    if (!missing(x)) {
	    if (is.list(x)) {
	    z <- x$z
	    y <- x$y
	    x <- x$x
	    }
	    else {
	    z <- x
	    x <- seq.int(0, 1, length.out = nrow(z))
	    }
	    }
	    else stop("no 'z' matrix specified")
	    }
	    else if (is.list(x)) {
	    y <- x$y
	    x <- x$x
	    }
	    if (any(diff(x) <= 0) || any(diff(y) <= 0)) 
	    stop("increasing 'x' and 'y' values expected")
	    #  mar.orig <- (par.orig <- par(c("mar", "las", "mfrow")))$mar
	    #  on.exit(par(par.orig))
	    #  w <- (3 + mar.orig[2L]) * par("csi") * 2.54
	    #layout(matrix(c(2, 1), ncol = 2L), widths = c(1, lcm(w)))
	    #  par(las = las)
	    #  mar <- mar.orig
	    #  mar[4L] <- mar[2L]
	    #  mar[2L] <- 1
	    #  par(mar = mar)
	    # plot.new()
	    plot.window(xlim = c(0, 1), ylim = range(levels), xaxs = "i", 
	    yaxs = "i")
	    rect(0, levels[-length(levels)], 1, levels[-1L], col = col)
	    if (missing(key.axes)) {
	    if (axes) 
	    axis(4)
	    }
	    else key.axes
	    box()
}








