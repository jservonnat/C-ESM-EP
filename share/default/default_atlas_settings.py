# -- Set default values for the variables
# -----------------------------------------------------------------------------------
verbose = 'critical'
clean_cache='False'
safe_mode = True
routine_cache_cleaning = False


season = 'ANM'
region = 'GLOB'
domain = {}

custom_obs_dict = dict()

reference_models=[]
period_manager_test_variable = None
apply_period_manager_once_for_all_diags = False
do_SST_for_tuning = False
do_atlas_explorer = False
do_parallel_atlas_explorer = False
do_parallel = False
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
do_Hotelling_Test = False
do_Tropics_SFlux_maps = False
do_ENSO_CLIVAR = False
do_ENSO_CLIVAR_sstanino3_timeseries = False
do_ENSO_CLIVAR_SSTA_std_maps = False
do_ENSO_CLIVAR_pr_climatology_maps = False
do_ENSO_CLIVAR_tauu_climatology_maps = False
do_ENSO_CLIVAR_linearRegression_dtauu_dsstanino3_maps = False
do_ENSO_CLIVAR_linearRegression_drsds_dsstanino3_maps = False
do_ENSO_CLIVAR_SSTA_annualcycles = False
do_ENSO_CLIVAR_longitudinal_profile_tauu = False
do_Monsoons_pr_anncyc = False
monsoon_precip_regions = None
do_mse_otorres_maps = False
do_mse_otorres_diff_maps = False
do_my_own_script_diag = False
do_my_own_climaf_diag = False
do_annual_cycle_precip = False
add_line_of_climato_plots = False
do_plot_raw_climatologies = False
do_zonal_profiles_explorer = False
do_main_time_series = False
style_file = None
add_product_in_title = True
hover = False
add_compareCompanion = True
add_period_to_simname=True
do_four_seasons_parcor=False

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
do_ORCHIDEE_Energy_Budget_climatology_maps = False
do_ORCHIDEE_Water_Budget_climobs_bias_modelmodeldiff_maps = False
do_ORCHIDEE_Water_Budget_climobs_bias_maps = False
do_ORCHIDEE_Water_Budget_climrefmodel_modelmodeldiff_maps = False
do_ORCHIDEE_Water_Budget_climatology_maps = False
do_ORCHIDEE_Carbon_Budget_climobs_bias_modelmodeldiff_maps = False
do_ORCHIDEE_Carbon_Budget_climobs_bias_maps = False
do_ORCHIDEE_Carbon_Budget_climrefmodel_modelmodeldiff_maps = False
do_ORCHIDEE_Carbon_Budget_climatology_maps = False

thumbnail_size=None
thumbnail_size_global="300*175"
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
thumbnail_monsoon_pr_anncyc_size = '375*600'

