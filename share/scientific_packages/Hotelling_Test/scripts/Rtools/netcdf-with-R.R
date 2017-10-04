

# --------------------------------------------------------------------------------------- #
# -- Load the "ncdf" package needed to work with netcdf files in R                     -- #

library(ncdf)



# --------------------------------------------------------------------------------------- #
# -- get.nc()                                                                          -- #

"get.nc"=
function(nc,varname=NULL,dimnames=NULL,ndims=NULL,start=NULL,count=NULL,reshape=TRUE,transpose=TRUE){

   # ------------------------------------------------------------------------------------------------------------------------------------------ #
   # --> This function works in X steps :                                                                                                    -- #
   # -->      - 1/ Get the name of the variable                                                                                              -- #
   # -->      - 2/ Get the dimensions of the file and creates the matrix that will receive the dataset                                       -- #
   # -->      - 3/ Extract the dataset                                                                                                       -- #
   # -->      - 4/ Depending on the dimensions of the dataset, put the dataset in a convenient format (grid points in one dimension)         -- #
   # -->      - 5/ Finalize the extraction (call the dataset at last line)                                                                   -- #
   # -->                                                                                                                                     -- #
   # -->        => Implementer la possibilite de selectionner une zone ou une periode                                                        -- #
   # -->                                                                                                                                     -- #
   # ------------------------------------------------------------------------------------------------------------------------------------------ #


   # -- 1/ If there is only one variable in the file, there is no need to precise it ------------------------------------------------------------

   if (is.null(varname)==TRUE){
     if (length(nc$var)==1){varname=names(nc$var)}else{print("Multiple variables = please select one") ; print(names(nc$var)) ; stop()}
   }#end if



   # -- 2/ Get the dimensions of the variable (number and names) ---------------------------------------------------------------------------------
   
   # -> Check the size of the dataset
   dumvarsize=nc$var[[varname]]$varsize

   # -> Get the dimensions names (dimnames)
   if (is.null(dimnames)==TRUE){dimnames=names(nc$dim)} # !!!! WARNING !!! nc$vars$varname$dim
   dimnames=dimnames[nc$var[[varname]]$dimids]

   # -> Get the number of dimensions
   if (is.null(ndims)==TRUE){ndims=length(nc$var[[varname]]$dim)}#end if is.null(ndims)
   print(paste("ndims =",ndims))

   # -> Select a given area or period?
   if (is.null(start)==TRUE){start=rep(1,ndims)}#end if is.null(start)
   if (is.null(count)==TRUE){count=rep(-1,ndims)}#end if is.null(count)

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

   dum.dat=get.var.ncdf(nc,nc$var[[varname]],start=start,count=count)


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



