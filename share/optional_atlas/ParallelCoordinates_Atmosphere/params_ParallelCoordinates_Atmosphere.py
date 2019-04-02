# ------------------------------------------------------------------------------------------ \
# --                                                                                        - \
# --                                                                                         - \
# --      User Interface for:                                                                 - \
# --                                                                                           - \
# --          CliMAF Earth System Model Evaluation Platform                                     - \
# --             - component: ParallelCoordinates_Atmosphere                                     - |
# --                                                                                             - |
# --      Developed within the ANR Convergence Project                                           - |
# --      CNRM GAME, IPSL, CERFACS                                                               - |
# --      Contributions from CNRM, LMD, LSCE, NEMO Group, ORCHIDEE team.                         - |
# --      Based on CliMAF: WP5 ANR Convergence, S. Senesi (CNRM) and J. Servonnat (LSCE - IPSL)  - |
# --                                                                                             - |
# --      J. Servonnat, S. Senesi, L. Vignon, MP. Moine, O. Marti, E. Sanchez, F. Hourdin,       - |
# --      I. Musat, M. Chevallier, J. Mignot, M. Van Coppenolle, J. Deshayes, R. Msadek,         - |
# --      P. Peylin, N. Vuichard, J. Ghattas, F. Maignan, A. Ducharne, P. Cadule,                - |
# --      P. Brockmann, C. Rousset                                                               - |
# --                                                                                             - |
# --      Contact: jerome.servonnat@lsce.ipsl.fr                                                 - |
# --                                                                                             - |
# --                                                                                            - /
# --                                                                                           - /
# --------------------------------------------------------------------------------------------- /


# -- Parameter file for the parallel coordinates html page created by:
# --    - running the PCMDI Metrics Package (PMP) on the datasets defined in datasets_setup.py
# --    - building the html page with climaf.html
# --    - do the plots with the script parallel_coordinates.R

safe_mode=True


# -- Import modules
from climaf.site_settings import atTGCC, onCiclad
import os, copy, subprocess, shlex
from datetime import datetime
from shutil import copyfile
from getpass import getuser

# -- Get the parameters that the atlas takes as arguments
# -----------------------------------------------------------------------------------
datasets_setup         = "datasets_setup.py"
image_size             = None
legend_ratio           = None
sort                   = 'TRUE'
# -- Colors for the CMIP5 highlighted models ; provide either a list of strings (same length as CMIP5_highlights)
# -- or a list of dictionaries (with only a subset of models)
# --   For CMIP5_highlights = ['IPSL-CM5A-LR','IPSL-CM5A-MR','CNRM-CM5']
# --   => CMIP5_colors = ['red', 'blue', 'orange']
# --   => CMIP5_colors = [dict(model='IPSL-CM5A-MR',color='red'), dict(model='IPSL-CM5A-LR',color='green')]
# --      -> the models that were not attributed a color will be assigned a default color
#CMIP5_colors                 = ['blue','navyblue','darkturquoise','green2']
# -- Set the CMIP5 models you want to highlight
CMIP5_highlights             = [dict(model='IPSL-CM5A-MR',color='black'),
                               ]
# -- Show only the highlighted simulations/models in the legend
highlights_only        = "FALSE"
# -- Do you want to use the first model of the highlights list to sort the results? If yes, set to "TRUE"
# -- If you rather want to use the first simulation specified in datasets_setup, set to "FALSE"
CMIP5_highlights_first       = True

lwd_background         = 2
lwd_highlights         = 6
# -- Check the R colors here: http://www.stat.columbia.edu/~tzheng/files/Rcolor.pdf
#colorpalette = ['dodgerblue3','orangered','mediumseagreen','firebrick3','yellow1','royalblue','deepskyblue','violetred2','mediumturquoise','cadetblue']
colorpalette = ['dodgerblue3','orangered','green2','yellow3','navyblue','darkturquoise','mediumseagreen','firebrick3','violetred2','antiquewhite3','darkgoldenrod3','coral3','lightsalmon1','lightslateblue','darkgreen','darkkhaki','darkorchid4','darksalmon','deepink2','lightblue4']
root_outpath           = None # -- For the links to the climatologies
force_compute_metrics  = False
reference              = None # -- defaultReference, alternate1...
template_paramfile_dir = '/home/jservon/Evaluation/PCMDI-MP/template_param_file'
rm_tmp_paramfie        = True
obs_data_path          = '/data/jservon/Evaluation/ReferenceDatasets/PMP_obs/obs'
outfigdir              = None
ref_parallel_coordinates = 'CMIP5'
if ref_parallel_coordinates=='CMIP5':
   reference_data_path = '/data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-historical/03Nov2016'
if ref_parallel_coordinates=='AMIP':
   reference_data_path = '/data/jservon/Evaluation/metrics_results/CMIP_metrics_results/CMIP5_20161103/cmip5clims_metrics_package-amip/03Nov2016'

metrics_table = 'Atmosphere'
vars = None
parallel_coordinates_script = '/home/jservon/Evaluation/PCMDI-MP/R_script/parallel_coordinates.R'

do_four_seasons_parcor=False

# -- Set the sections of metrics you want
metrics_sections = [
       dict(statistic=['rms_xyt','rmsc_xy','bias_xy','cor_xy'],
            region=['global'],#'land','ocean'],
            season=['ann'],
            section_name='Global, land, ocean on annual cycle and annual mean (rms_xyt, rmsc_xyt, bias_xy and cor_xy)'),
       dict(statistic=['rms_xy','rmsc_xy','bias_xy','cor_xy'],
            region=['NHEX', 'TROPICS', 'SHEX'],
            season=['ann','djf','mam','jja','son'],
            section_name='NHEX (90N-20N), TROPICS (20N-20S), and SHEX (20S-90S), annual and seasonal means (rms_xy, rmsc_xy, bias_xy and cor_xy)'),
    ]


atlas_head_title = 'Parallel Coordinates - PMP PCMDI'

style_file = '/share/fp_template/cesmep_atlas_style_css'
i=1
while not os.path.isfile(os.getcwd()+style_file):
    print i
    style_file = '/..'+style_file
    if i==3:
       break
    i=i+1
style_file = os.getcwd()+style_file

index_filename_root = 'ParallelCoordinates_Atmosphere'


