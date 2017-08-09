# -- Set default values for the variables
# -----------------------------------------------------------------------------------
verbose = 'critical'
clean_cache='False'
safe_mode = True

season = 'ANM'
region = 'GLOB'
domain = {}

custom_obs_dict = dict()

do_atlas_explorer = False
atlas_explorer_climato_variables=None
do_atmos_maps = False
remapping = True
do_ocean_2D_maps = False
do_biogeochemistry_2D_maps = False
do_land_surface_maps = False
do_seaice_maps = False
do_seaice_annual_cycle = False
sea_ice_diags = None
do_MLD_maps = False
do_TS_MOC = False
llats = None
MLD_diags = None
do_curl_maps = False
curl_diags=None
do_GLB_SFlux_maps = False
do_Tropics_SFlux_maps = False
do_ENSO_CLIVAR = False
do_Monsoons_pr_anncyc = False
monsoon_precip_regions = None

add_line_of_climato_plots = False

style_file = None
add_product_in_title = True
hover = False
add_compareCompanion = True

do_ATLAS_TIMESERIES_SPATIAL_INDEXES = False
do_ATLAS_VERTICAL_PROFILES = False
do_ATLAS_DRIFT_PROFILES = False
do_ATLAS_MOC_DIAGS = False
do_ATLAS_ZONALMEAN_SLICES = False
y='lin'

do_ORCHIDEE_Energy_Budget_climobs_bias_modelmodeldiff_maps = False
do_ORCHIDEE_Energy_Budget_climobs_bias_maps = False
do_ORCHIDEE_Energy_Budget_climrefmodel_modelmodeldiff_maps = False
do_ORCHIDEE_Energy_Budget_diff_with_ref_maps = False
do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps = False
do_ORCHIDEE_Water_Budget_climobs_bias_maps = False
do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps = False
do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps = False
do_ORCHIDEE_Carbon_Budget_climobs_bias_maps = False
do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps = False

thumbnail_size="300*175"
thumbnail_polar_size="250*250"
thumbnail_size_3d="250*250"
thumbsize_zonalmean='450*250'
thumbsize_TS='450*250'
thumbsize_MOC_slice="475*250"
thumbsize_MAXMOC_profile="325*250"
thumbsize_MOC_TS="325*250"
thumbsize_VertProf="250*250"
thumbnail_ENSO_size="400*175"
thumbnail_ENSO_ts_size="400*175"

