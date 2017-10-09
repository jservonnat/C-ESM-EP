"""
- Fonction closest : trouve dans collection la valeur la plus proche de num
- Fonction which : utilise la fonction closest pour renvoyer l indice correspondant a cette valeur
	Par exemple si on veut la valeur de x a 250E mais que cette longitude n existe pas sur la grille, x[which(lon,250)] donnera la valeur de x en 251.21 (qui est un point de la grille)
- Fonctions whichInf et whichSup sont a utiliser pour selectionner une region (whichInf pour la borne inferieure et whichSup pour la borne superieure) : par rapport a which, elles permettent d imposer que la longitude (ou la latitude) la plus proche de celle ou on veut couper soit a l interieur de la region que l on veut selectionner

 Fonctions qui necessitent d importer numpy (as np)
"""


def closest(collection,num):
	return min(collection,key=lambda x:abs(x-num))

def which(collection,num):
	return np.where(collection==closest(collection,num))[0][0]

def whichInf(collection,num):
	i_closest = np.where(collection==closest(collection,num))[0][0]
	if closest(collection,num) < num :
		return i_closest+1
	else:
		return i_closest

def whichSup(collection,num):
	i_closest = np.where(collection==closest(collection,num))[0][0]
	if closest(collection,num) > num :
		return i_closest
	else:
		return i_closest+1




#Script qui trace les cartes montrant la divergence du transport energetique atmsospherique totale(CpT+gz+Lq) integre verticalement (Reprise du script de marion !!!!)

import netCDF4 as nc
import matplotlib
matplotlib.use('agg')
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from pylab import *

from windspharm.standard import VectorWind
from windspharm.tools import prep_data, recover_data, order_latdim



#-------------   Récupération des arguments et des variables -----------------------

ref       = sys.argv[1]        # uE REF
ref2      = sys.argv[2]        # vE REF
ref3      = sys.argv[3]        # uE simu
ref4      = sys.argv[4]        # vE simu
ref5      = sys.argv[5]        # aire 
ref6      = sys.argv[6]        # pourc_ter
title     = sys.argv[7]        # title REF
widthu    = sys.argv[8]        # width arrows
colormap  = sys.argv[9]       # colormap
dxx       = sys.argv[10]       # dx arrows
dyy       = sys.argv[11]       # dy arrows
scal      = sys.argv[12]       # scale arrows
vma       = sys.argv[13]       # val max colormap
vmi       = sys.argv[14]       # val min colorbar
masku     = sys.argv[15]       # mask to pourc_ter
name      = sys.argv[16]       # title of fig

widt     = float(widthu)
dxxx     = float(dxx)
dyyy     = float(dyy)
scales   = float(scal)
valma    = float(vma)
valmi    = float(vmi)

#--------------------------------------------------------------------------------------
"""""""""""""""""""""""""""""""""""""""""""""""""""

                       DONNEE

"""""""""""""""""""""""""""""""""""""""""""""""""""

#---------------      Fichier Initial contenant toute les variables   -----------------------
#file_ini=nc.Dataset('/home/users/otorres/TEST_PYTHON/DRAGNOCE_19200101_19591230_Monthmean.nc')



#---------------                 Extraction de la variable VE               -----------------------
file_ini=nc.Dataset(ref)

lon_var=file_ini.variables['lon'][:]

lat_var=file_ini.variables['lat'][:]

UE_pin_o = file_ini.variables['ue'][:,:]
UE_pin_W = UE_pin_o[:,:,:which(lon_var,0)]
UE_pin_E = UE_pin_o[:,:,which(lon_var,0):]
UE_mean_pin = np.concatenate((UE_pin_E,UE_pin_W),axis=2)
file_ini.close()


#-------------       longitudes de -180 a 180 donc on remet de 0 a 360      -----------------
lonsW_o=lon_var[:which(lon_var,0)]                                                     # on isole la partie ouest (de -180 a 0)
lonsW = r_[lonsW_o[np.where(lonsW_o >=0)],180+(180+lonsW_o[np.where(lonsW_o <0)])]       # ici on transforme toutes les valeurs negatives en valeurs qui suivent 180
#lonsW = r_[lonsW_o[np.where(lonsW_o >=0)],180+(180+lonsW_o[np.where(lonsW_o <0)])]          # ici on transforme toutes les valeurs negatives en valeurs qui suivent 180
lonsE=lon_var[which(lon_var,0):]                                                       #  on isole la partie est (de 0 a 180)
lons=np.concatenate((lonsE,lonsW))                                                        # on les concatene

#---------------      latitudes de 90 a -90 donc on remet de -90 a 90       -----------------------

lats = lat_var[:]


file_ini=nc.Dataset(ref2)
VE_pin_o = file_ini.variables['ve'][:,:]
VE_pin_W = VE_pin_o[:,:,:which(lon_var,0)]
VE_pin_E = VE_pin_o[:,:,which(lon_var,0):]
VE_mean_pin = np.concatenate((VE_pin_E,VE_pin_W),axis=2)
file_ini.close()

#---------------                Extraction de la variable AIRE              -----------------------
file_ini=nc.Dataset(ref5)
areA = file_ini.variables['aire'][:,:]
file_ini.close()

#---------------            Extraction de la variable pourc_ter             -----------------------
file_ini=nc.Dataset(ref6)
pourcter_o = file_ini.variables['pourc_ter'][:,:]
pourcter_W = pourcter_o[:,:which(lon_var,0)]
pourcter_E = pourcter_o[:,which(lon_var,0):]
pourcter = np.concatenate((pourcter_E,pourcter_W),axis=1)
file_ini.close()


"""""""""""""""""""""""""""""""""""""""""""""""""""

                       ANALYSES

"""""""""""""""""""""""""""""""""""""""""""""""""""

#---------------     Calcul du potentiel de vitesses et de son gradient     -----------------------
#---------    = partie divergente du champ = partie par laquelle se fait l export   ---------------

#---------------                           MOYENNE                          -----------------------
#---          The standard interface requires that latitude and longitude be the leading       ----
#---           dimensions of the input wind components, and that wind components must be       ----
#---              either 2D or 3D arrays. The data read in is 3D and has latitude and          ----
#---                               longitude as the last dimensions.                           ----
#---         It is also required that the latitude dimension is north-to-south. Again the      ----
#---                               bundled tools make this easy.                               ----

lats_r, uwnd, vwnd = order_latdim(lats,UE_mean_pin,VE_mean_pin)

#- Create a VectorWind instance to handle the computation of streamfunction and velocity potential-

w = VectorWind(uwnd, vwnd)

#---                          fonction de courant (sf ; streamfunction)                        ----
#---                          potentiel de vitesse (vp ; velocity potential)                   ----

sf, vp = w.sfvp()

#---             partie divergente du champ = gradient du potentiel de vitesses                ----

grad_vp = w.irrotationalcomponent()

#---     on masque les continents parce que les valeurs sur les continents sont trop fortes    ----

pourcter_ma = ma.array(pourcter,mask=pourcter>0.1)

#---   attention on a re-inverse les latitudes pour pouvoir utiliser VectorWind pour calculer  ----
#---                le potentiel de vitesse. Donc il faut que le masque colle bien             ----

grad_vp_x_ma = ma.array(grad_vp[0],mask=pourcter_ma.mask[::1,:]) 
grad_vp_y_ma = ma.array(grad_vp[1],mask=pourcter_ma.mask[::1,:])

#---                                   si on ne masque pas                                     ----

grad_vp_x = grad_vp[0]
grad_vp_y = grad_vp[1]

#---              integration meridienne de la composante zonale avec les continents           ----
#---             et integration zonale de la composante meridienne avec les continents         ----

dy_o = (lats_r[1]-lats_r[2])*(3.14159/180.)*6371000
dy = np.zeros(shape(areA[:,:]))+dy_o 
dx = areA[:,:] / dy

aire_mer = np.sum(areA[5:-5,:]*dy[5:-5,:],axis=0)
aire_zon  = np.sum(areA[:,:]*dx[:,:],axis=1)

grad_vp_x_me = np.sum(grad_vp_x[5:-5,:]*dy[5:-5,:],axis=0)
grad_vp_y_zo = np.sum(grad_vp_y[:,:]*dx[:,:],axis=1)

grad_vp_x_mer = grad_vp_x_me/aire_mer
grad_vp_y_zon = grad_vp_y_zo/aire_zon



"""""""""""""""""""""""""""""""""""""""""""""""""""

            DONNEE  POUR NOCE

"""""""""""""""""""""""""""""""""""""""""""""""""""

#---------------                 Extraction de la variable VE               -----------------------
file_ini=nc.Dataset(ref3)

UE_pin_o = file_ini.variables['ue'][:,:]
UE_pin_W = UE_pin_o[:,:,:which(lon_var,0)]
UE_pin_E = UE_pin_o[:,:,which(lon_var,0):]
UE_mean_noce = np.concatenate((UE_pin_E,UE_pin_W),axis=2)
file_ini.close()


file_ini=nc.Dataset(ref4)
VE_pin_o = file_ini.variables['ve'][:,:]
VE_pin_W = VE_pin_o[:,:,:which(lon_var,0)]
VE_pin_E = VE_pin_o[:,:,which(lon_var,0):]
VE_mean_noce = np.concatenate((VE_pin_E,VE_pin_W),axis=2)
file_ini.close()

"""""""""""""""""""""""""""""""""""""""""""""""""""

                       ANALYSES

"""""""""""""""""""""""""""""""""""""""""""""""""""

#---------------     Calcul du potentiel de vitesses et de son gradient     -----------------------
#---------    = partie divergente du champ = partie par laquelle se fait l export   ---------------

#---------------                           MOYENNE                          -----------------------
#---          The standard interface requires that latitude and longitude be the leading       ----
#---           dimensions of the input wind components, and that wind components must be       ----
#---              either 2D or 3D arrays. The data read in is 3D and has latitude and          ----
#---                               longitude as the last dimensions.                           ----
#---         It is also required that the latitude dimension is north-to-south. Again the      ----
#---                               bundled tools make this easy.                               ----

lats_r_noce, uwnd_noce, vwnd_noce = order_latdim(lats,UE_mean_noce,VE_mean_noce)

#- Create a VectorWind instance to handle the computation of streamfunction and velocity potential-

w_noce = VectorWind(uwnd_noce, vwnd_noce)

#---                          fonction de courant (sf ; streamfunction)                        ----
#---                          potentiel de vitesse (vp ; velocity potential)                   ----

sf_noce, vp_noce = w_noce.sfvp()

#---             partie divergente du champ = gradient du potentiel de vitesses                ----

grad_vp_noce = w_noce.irrotationalcomponent()

#---     on masque les continents parce que les valeurs sur les continents sont trop fortes    ----

pourcter_ma_noce = ma.array(pourcter,mask=pourcter>0.1)

#---   attention on a re-inverse les latitudes pour pouvoir utiliser VectorWind pour calculer  ----
#---                le potentiel de vitesse. Donc il faut que le masque colle bien             ----

grad_vp_x_ma_noce = ma.array(grad_vp_noce[0],mask=pourcter_ma_noce.mask[::1,:]) 
grad_vp_y_ma_noce = ma.array(grad_vp_noce[1],mask=pourcter_ma_noce.mask[::1,:])

#---                                   si on ne masque pas                                     ----

grad_vp_x_noce = grad_vp_noce[0]
grad_vp_y_noce = grad_vp_noce[1]

#---              integration meridienne de la composante zonale avec les continents           ----
#---             et integration zonale de la composante meridienne avec les continents         ----

dy_o_noce = (lats_r_noce[1]-lats_r_noce[2])*(3.14159/180.)*6371000
dy_noce = np.zeros(shape(areA[:,:]))+dy_o_noce 
dx_noce = areA[:,:] / dy_noce

grad_vp_x_mer_noce = np.sum(grad_vp_x_noce[5:-5,:]*dy_noce[5:-5,:],axis=0)
grad_vp_y_zon_noce = np.sum(grad_vp_y_noce[:,:]*dx_noce[:,:],axis=1)


"""""""""""""""""""""""""""""""""""""""""""""""""""

                      FIGURES

"""""""""""""""""""""""""""""""""""""""""""""""""""
couleurs = {'gris': [[0.72,0.72,0.72], 'light_black']}

matplotlib.rcParams.update({'font.size': 20})

m = Basemap(projection='cyl',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=lons.min(),urcrnrlon=lons.max(),resolution='c',fix_aspect=True)
#m = Basemap(projection='cyl',llcrnrlat=-80,urcrnrlat=80,resolution='c',fix_aspect=True)
parallels = np.arange(-80,81,20.)
meridians = np.arange(0.,360.,60.)

# echelle des fleches (plus elle est grande, plus fleches petites)
width = widt
# dx sur lequel tracer les vents
dX = dxxx
dY = dyyy # (1 sur 5 en latitudes)


############## MOYENNE

# attention important, ce plot fait une colorbar comme dans ferret avec -inf et inf ! (le extend="both" dans le plot est la cle)
# on definit les limites qu on veut pour la colorbar :
scale = scales
cm_div_1 = plt.get_cmap('Spectral_r')
cm_div_2 = plt.get_cmap(colormap)
vmax_div = valma
vmin_div = valmi
levels_div=MaxNLocator(nbins=17).bin_boundaries(vmin_div,vmax_div)


X = lons
Y = lats_r[2:-2]
U = grad_vp_x_ma_noce[2:-2,:]-grad_vp_x_ma[2:-2,:]
V = grad_vp_y_ma_noce[2:-2,:]-grad_vp_y_ma[2:-2,:]
Z = vp_noce[2:-2,:]-vp[2:-2,:]


############## MOYENNE V2

fig, ax = plt.subplots(1,figsize=(15,8))
subplots_adjust(left=0.08,wspace=0.48,hspace=0.32)

##############  MOYENNE

m.drawcoastlines()
#m.fillcontinents()
m.drawparallels(parallels,labels=[1,0,0,0],fontsize=20,linewidth=0.2)
m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=20,linewidth=0.2)


plot_div = plt.contourf(X,Y,Z,cmap=cm_div_2,levels=levels_div,extend="both")
Q2=quiver(X[::dX],Y[::dY],U[::dY,::dX],V[::dY,::dX],width=width,scale=scale)
qk2 = quiverkey(Q2,0.75,1.04,2*1e8, r'$2*10^{8} W/m$', labelpos='E', fontproperties={'weight': 'bold','size': '24'})

plt.title('MSE export '+'('+title+')', fontsize=32) 
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)


#plt.title('MSE export, annual mean \n DRAGALL')
# place colorbar
box = ax.get_position()
pad, thick = 0.02, 0.01
cax = fig.add_axes([box.xmax + pad, box.ymin, thick, box.height])
cbar = fig.colorbar(plot_div, cax=cax)
cbar.ax.set_ylabel('W', fontsize=26)
cbar.ax.tick_params(labelsize=26)

plt.savefig(name, bbox_inches='tight')


