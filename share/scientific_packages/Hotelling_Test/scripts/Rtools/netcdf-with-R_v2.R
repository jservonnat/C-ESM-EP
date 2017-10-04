

# --------------------------------------------------------------------------------------- #
# -- Load the "ncdf" package needed to work with netcdf files in R                     -- #

library(ncdf)


# --------------------------------------------------------------------------------------- #
# -- time.axis()                                                                       -- #
# -- Generates a time axis with the years, months and days





# -- Rajouter un lonflip dans get.nc2

# -- Rajouter l'affichage de 0 a 360 dans quickmap2








# --------------------------------------------------------------------------------------- #
# -- get.nc2()                                                                          -- #
# -- For an object-oriented use of the netcdf files.

"get.nc2"=
function(file,varname=NULL,region=NULL,period=NULL,time.axis=NULL,ndims=NULL,transpose=TRUE,dimnames=NULL,reshape=TRUE,shift=NULL,PacificCentered=NULL){

   # ------------------------------------------------------------------------------------------------------------------------------------------ #
   # --> This function works in X steps :                                                                                                    -- #
   # -->      - 1/ Get the name of the variable                                                                                              -- #
   # -->      - 2/ Get the dimensions of the file and creates the matrix that will receive the dataset                                       -- #
   # -->      - 3/ Extract the dataset                                                                                                       -- #
   # -->      - 4/ Depending on the dimensions of the dataset, put the dataset in a convenient format (grid points in one dimension)         -- #
   # -->      - 5/ Finalize the extraction (call the dataset at last line)                                                                   -- #
   # -->                                                                                                                                     -- #
   # -->        => Implementer la possibilite de selectionner une zone ou une periode                                                        -- #
   # -->                                                                                                                                     FALSE
   # ------------------------------------------------------------------------------------------------------------------------------------------ #

   # -- Open a list that will receive the results
   RES=list()
   RES$file=file

   # -- Open the netcdf file
   nc=open.ncdf(file)



   # -- 1/ If there is only one variable in the file, there is no need to precise it ------------------------------------------------------------

   if (is.null(varname)==TRUE){
     if (length(nc$var)==1){varname=names(nc$var)}else{print("Multiple variables = please select one") ; print(names(nc$var)) ; stop()}
   }#end if

      # --> Stockage dans RES
      RES$varname=varname


   # -- 2/ Get the dimensions of the variable (number and names) ---------------------------------------------------------------------------------
   
   # -> Check the size of the dataset
   dumvarsize=nc$var[[varname]]$varsize
   RES$varsize=dumvarsize

   # -> Get the number of dimensions
   if (is.null(ndims)==TRUE){ndims=length(nc$var[[varname]]$dim)}#end if is.null(ndims)
   print(paste("ndims =",ndims))

   # -> Get the dimensions names (dimnames)
   if (is.null(dimnames)==TRUE){dimnames=names(nc$dim)} # !!!! WARNING !!! nc$vars$varname$dim
   dimnames=dimnames[nc$var[[varname]]$dimids]
   RES$dimnames=dimnames


   # -- If we do not ask for a particular region
   start=rep(1,ndims)
   count=rep(-1,ndims)
   
   
   # --> Get the longitudes and latitudes
   lon=get.dim(nc,"lon")
   lat=get.dim(nc,"lat")
   if (is.null(lon)==FALSE) RES$lon=lon
   if (is.null(lat)==FALSE) RES$lat=lat

   nload=1
   if (is.null(region)==FALSE){

   # -- If we ask for a given lon/lat region, defined as region=c(lonW,lonE,latS,latN)
   # -- Works for 3D file (lon,lat,time), but not for a 4D file (including depth or altitude)
   lonW=region[1] ; lonE=region[2] ; latS=region[3] ; latN=region[4]


       # -- Traitement des latitudes
       if (lat[2]>lat[1]){#then lat is sorted in increasing order
         if (latS<min(lat)){first.lat=1}else{first.lat=max(which(lat<=latS))}
         if (latN>max(lat)){end.lat=length(lat)}else{end.lat=min(which(lat>=latN))}
       }else{#then lat is sorted in decreasing order
         if (latN>max(lat)){first.lat=1}else{first.lat=max(which(lat>=latN))}
         if (latS<min(lat)){end.lat=length(lat)}else{end.lat=min(which(lat<=latS))}
       }#end if
       length.lat=end.lat-first.lat+1

       start[2]=first.lat
       count[2]=length.lat
       lat=lat[first.lat:end.lat]



       int=lon[2]-lon[1]

       if (lonW>=(lon[length(lon)])){
       lon=lon+360
       print("lonW > 180")}

       # -- Case 1/ the region lies inside the intervalle of the original longitudes
       if (lonW>=(lon[1]-int) & lonE<=(lon[length(lon)]+int)){
       nload=1 # Va-t-on charger le dataset en une ou deux fois (en nload fois)?


       # --> Select the longitudes and latitudes
       if (lonW<min(lon)){first.lon=1}else{first.lon=max(which(lon<=lonW))}
       if (lonE>max(lon)){end.lon=length(lon)}else{end.lon=min(which(lon>=lonE))}
       length.lon=end.lon-first.lon+1

       # -- Define the start and count
       start[1]=first.lon
       count[1]=length.lon

       lon=lon[first.lon:end.lon]
       }# end case 1


       # -- Case 2/ The longitudes of the file span from 0 to 360, and we ask for a domain with longitudes between -180 and 180
       if (lonW<(lon[1]-int)){

       nload=2 # On chargera le dataset en deux parties
       start1=start ; count1=count # Partie Ouest (qui deviendra la partie Est)
       start1[1]=1 ; count1[1]=max(which(lon<=lonE))

       lon[which(lon>180)]=lon[which(lon>180)]-360
       start2=start ; count2=count # Partie Est (qui deviendra la partie Ouest)
       start2[1]=min(which(lon>=lonW & lon<0)) ; count2[1]=-1
       # faire le nouveau vecteur de longitudes correspondant
       dumlon=sort(lon,decreasing=FALSE)
       lon=dumlon[which(dumlon>=lonW & dumlon<=lonE)]
       }#end case 2


       # -- Case 3/ The longitudes of the file span from -180 to 180, and we ask for a domain with longitudes between 0 and 360
       if (lonE>(lon[length(lon)]+int) & lonW<(lon[length(lon)])){
       nload=2 # On chargera le dataset en deux parties
       start1=start ; count1=count
       start2=start ; count2=count
       start2[1]=min(which(lon>=lonW)) ; count2[1]=-1
       lon[which(lon<0)]=lon[which(lon<0)]+360
       start1[1]=1 ; count1[1]=max(which(lon<=lonE & lon>lon[1]))

       dumlon=sort(lon,decreasing=FALSE)
       lon=dumlon[which(dumlon>=lonW & dumlon<=lonE)]

       }#end case 3




   }#end if is.null(region)

       RES$lon=lon
       RES$lat=lat


   # --> Get the time axis
   if (is.null(time.axis) & (any(dimnames=="time") | any(dimnames=="time_counter") | any(dimnames=="TIME"))){
   dumtime=get.dim(nc,"time")
   time=dumtime
   }#end if

   if (is.null(period)==FALSE){

     prd=which(time.axis$years>=period[1] & time.axis$years<=period[2])
     time=list()
     for (dum in names(time.axis)){
     time[[dum]]=time.axis[[dum]][prd]
     }#end for

     start[3]=prd[1]
     count[3]=length(prd)

   }#end if

   RES$time=time


   # -> Get the size of the dataset
   # -- Which Axes?
   Tnames=c("t","T","time","time_counter","TIME_COUNTER","TIME","TMEANSC")
   dumx=c() ; dumy=c() ; dumz=c() ; dumt=c()
   for (l in 1:length(nc$dim)){
        dumt=c(dumt,(any(Tnames == dimnames[l])))
   }#end for l

   # -- Names of the axes
   ntname=dimnames[which(dumt==TRUE)]

   # -- Print what was found
   print(paste("The variable",varname,"is defined on =",paste(dumvarsize,dimnames)))

     # => From here, we have the dimensions of the variable varname nx, ny, nz and nt
     # => and also start and count



   # -- 3/ Extract the dataset ---------------------------------------------------------------------------------------------------------------------

   if (nload==1){
   dum.dat=get.var.ncdf(nc,nc$var[[varname]],start=start,count=count)
   }
   if (nload==2){
   dum.dat1=get.var.ncdf(nc,nc$var[[varname]],start=start1,count=count1)
   dum.dat2=get.var.ncdf(nc,nc$var[[varname]],start=start2,count=count2)
   dum.dat=array(data=NA,c(length(RES$lon),length(RES$lat),length(RES$time)))
   #print(dim(dum.dat))
   #print(dim(dum.dat1))
   #print(dim(dum.dat2))
   dum.dat[1:nrow(dum.dat2),,]=dum.dat2
   dum.dat[(nrow(dum.dat2)+1):(nrow(dum.dat2)+nrow(dum.dat1)),,]=dum.dat1
   }
   close.ncdf(nc)

   # !!! The number of dimensions associated with the variable in the dataset is not always the number of useful dimensions
   # !!! For example, if the file has been prepocessed, and that the variable has been selected from only one vertical level, or one longitude,
   # !!! the dimensions of the final object are not the same as the dimensions mentioned in the netcdf file.
   # !!! We thus eliminate the dimension of length = 1
   varsize=dumvarsize[dumvarsize!=1]
   if (length(varsize)!=length(dumvarsize)){
   dimnames=names(nc$dim)[nc$var[[varname]]$dimids][dumvarsize!=1]
   ndims=length(dimnames)
   print("Useful dimensions are =")
   print(paste(dimnames))
   }

   if (is.null(PacificCentered)==FALSE){
   if (PacificCentered==FALSE){
   # on veut des longitudes de -180 a 180
      if (max(lon)>180){
         dum=dum.dat
	 indsup180=which(lon>180)
	 indinf180=which(lon<=180)
	 dum[1:length(indsup180),,]=dum.dat[indsup180,,]
	 dum[(length(indsup180)+1):length(lon),,]=dum.dat[indinf180,,]
	 lon[lon>180]=lon[lon>180]-360
	 RES$lon=sort(lon,decreasing=FALSE)
	 dum.dat=dum
      }#end if max(lon)>180

   }
   if (PacificCentered==TRUE){
   # on veut des longitudes de 0 a 360

   }
   }#end if is.null(PacificCentered)


   # -- 4/ Put the dataset in the convenient format ------------------------------------------------------------------------------------------------

   if (reshape==FALSE){
   DAT=dum.dat
   }else{


      # -> Case 1 = one dimension dataset
      if (ndims==0 | ndims==1){DAT=dum.dat}


      # -> Case 2 = two dimension dataset
      if (ndims==2){

        # If the dataset is XT or YT or ZT, we do not need to change its form
        if (any(dimnames==ntname)==TRUE){
         DAT=dum.dat
        }else{
        # If the dataset is XY, XZ, or YZ, we want to put all the grid points in one array
	 dim.dum.dat=dim(dum.dat) ; non.null.dim=dim.dum.dat[dim.dum.dat!=1]
	 dim(dum.dat)=c(non.null.dim[1],non.null.dim[2])
         if (transpose==TRUE){dum.dat=t(dum.dat)}
         dim(dum.dat)=NULL
         DAT=dum.dat 
        }#end if & else

      }#end if ndims==2
   


      # -> Case 3 = three dimension dataset
      if (ndims==3){
      
         # We consider here that the time dimension must be the last one listed in wdim.
         # Otherwise, the last dimension is the vertical.
         # We want a dataset with the grid points in one dimension => XY, XZ, YZ ; the third dimension is either vertical or time
         # We thus consider that the dataset is NX,NY,NT:
         #   - NX being either x or y
         #   - NY being either y or z
         #   - NT being either z or t

           NX=nc$dim[[dimnames[1]]]$len
       	   NY=nc$dim[[dimnames[2]]]$len
	   NT=nc$dim[[dimnames[3]]]$len
           
	   if (is.null(region)==FALSE){NX=length(lon) ; NY=length(lat)}
           if (is.null(period)==FALSE){NAT=length(time$years)}

           # We have dim=c(NX,NY,NT) and we want dim=c(NT,NX*NY)
           dat = dum.dat*NA; dim(dat) <- c(NT,NY,NX)
           for (i in 1:NT){
	   dat[i,,] <- t(as.matrix(dum.dat[,,i]))
	   }#end for i
           # On prefere les tableaux a deux dimensions
           dim(dat)=c(NT,NX*NY)
	   DAT=dat

      }#end if ndims==3
   
   
      # -> Case 4 = four dimension dataset
      if (ndims==4){

          NX=nc$dim[[dimnames[1]]]$len
          NY=nc$dim[[dimnames[2]]]$len
          NZ=nc$dim[[dimnames[3]]]$len
          NT=nc$dim[[dimnames[4]]]$len
       
          DAT=dum.dat*NA
          dim(DAT)=c(NT,NZ,NX*NY)

          # We have dim=c(NX,NY,NZ,NT) and we want dim=c(NT,NZ,NX*NY)
          for (z in 1:NZ){
          dum=dum.dat[,,z,]
          tmp=dum*NA ; dim(tmp) <- c(NT,NY,NX)
            for (t in 1:NT){
	    tmp[t,,] <- t(as.matrix(dum[,,t]))
	    }#end for t
          dim(tmp)=c(NT,NX*NY)
          DAT[,z,]=tmp
          }#end for z

      }#end if ndims==4

  }#end if reshape==FALSE



   # -- 5/ Finalize the extraction -----------------------------------------------------------------------------------------------------------------

   # -> Change spval for NA
   DAT[which(DAT>10^30)]=NA

   # -> Call the dataset
   DAT

   # -- Add a shift
   if (is.null(shift)==FALSE) DAT=DAT+shift


   RES$dat=DAT

   RES


}#end def get.nc









# --------------------------------------------------------------------------------------- #
# -- get.dim()                                                                         -- #

"get.dim"=
function(nc,dimname,varname=NULL){

# L'interet de cette fonction est de recuperer systematiquement la variable qui correspond a une dimension classique, comme la latitude
# Au final, je veux 

dimnames=names(nc$dim)
if (is.null(varname)==FALSE){
dimnames=dimnames[nc$var[[varname]]$dimids]
}#end if


if (dimname=="x" | dimname=="longitude" | dimname=="lon" | dimname=="LON" | dimname=="X"){
   names=c("x","X","lon","long","longitude","LON","LONGITUDE","Lon","Longitude")
   dum=c()
   for (l in 1:length(dimnames)){
     dum=c(dum,(any(names == dimnames[l])))
   }#end for l
   nyname=dimnames[which(dum==TRUE)]
   print(paste("Real dimension name =",nyname))
   vals=nc$dim[[nyname]]$vals
}#end if

if (dimname=="lat" | dimname=="latitude" | dimname=="y" | dimname=="Y" | dimname=="LAT"){
   names=c("y","Y","lat","lati","latitude","LAT","LATITUDE","Lat","Latitude")
   dum=c()
   for (l in 1:length(dimnames)){
     dum=c(dum,(any(names == dimnames[l])))
   }#end for l
   nyname=dimnames[which(dum==TRUE)]
   print(paste("Real dimension name =",nyname))
   vals=nc$dim[[nyname]]$vals
}#end if

if (dimname=="z" | dimname=="vertical" | dimname=="levels" | dimname=="depth" | dimname=="deptht" ){
   names=c("z","Z","presnivs","deptht","depth","depthw","pressure","lev","level","levels","DEPTH",
           "sigma","sigma0","sigma1","sigma2","sigma3","sigma4","SIGMA","AXSIGMA","axsigma")
   dum=c()
   for (l in 1:length(dimnames)){
    dum=c(dum,(any(names == dimnames[l])))
   }#end for l
   nyname=dimnames[which(dum==TRUE)]
   print(paste("Real dimension name =",nyname))
   vals=nc$dim[[nyname]]$vals
}#end if


if (dimname=="t" | dimname=="time" | dimname=="time_counter" | dimname=="time"){
   names=c("t","T","time","time_counter","TIME_COUNTER","TIME","TMEANSC")
   dum=c()
   for (l in 1:length(dimnames)){
    dum=c(dum,(any(names == dimnames[l])))
   }#end for l
   nyname=dimnames[which(dum==TRUE)]
   print(paste("Real dimension name =",nyname))
   vals=nc$dim[[nyname]]$vals
}#end if

vals

}#end def get.dim



