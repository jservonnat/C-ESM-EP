from climaf.api import *

def simu_name(simu):
    if type(simu) is dict:
        if 'product' in simu :
            return simu['product']
        elif simu.get('project',None) in ['IGCM_OUT']:
            return simu['simulation']
        elif simu.get('project',None) in [ 'CMIP6', 'CMIP5' ]:
            return simu['experiment']
        else :
            return simu['experiment']
    else:
        return simu

# A function for computing a map image filename based on some parameters
# that define its content. It mimics Mappers's convention
def mapper_map_filename(simu1, simu2, variable, season):
    # This is also an example of the interface for a function provided as
    # argument to cesmep_diagnostics.CM_atlas.plot_CM_atlas.section_2D(),
    rep = simu_name(simu1)
    if simu2 :
        rep += '_vs_' + simu_name(simu2)
    rep += '_' + variable + '_' + season
    return rep


# A function for computing a times_series image filename based on some
# parameters that define its content. It mimics Mappers's convention
def mapper_ts_filename(region, variable, frequency):
    abbrev = { 'yearly' : 'y', "annual_cycle" : 's' , "monthly" : 'm' }
    return variable + '_' + abbrev[frequency] + '_' + region


def annual_mean_space_average(dat):
    return space_average(ccdo(dat, operator='yearmean'))


def space_average_over_region(dat, region_number=None, regions_file=None,
                               contfrac = None, region_dimension = "reg",**kwargs):

    """Compute space average for a field represented by CliMAF object
    DAT, integrating over a region identified by REG_DIMENSION =
    REGION_NUMBER in file REGIONS_FILE, and only over its land part
    when CONTFRAC is not None and represents the continental fraction
    on the same grid of DAT (coded with 1s over the region and 0 or
    missing value elsewhere)
    
    If one of args related to the region is None, the whole domain is
    used
    The regions data is remapped to DAT's grid

    """
    
    # Contfrac : a CliMAF object representing the continental
    # fraction, ON THE SAME GRID AS DAT

    # Regions_file : holds variable reg_mask(reg,lat,lon), which has
    # value 1 in the region and 0 elsewhere
    # We assume that region masks are conservative re. land extent.
    
    # When called by diagnostics_ts, this function also receives
    # region's id as arg 'region' and region's (long) name as arg
    # 'region_name' 
    
    if contfrac is not None :
        contfrac = ccdo(contfrac, operator="-setctomiss,0")

    if regions_file is None or region_number is None :
        if contfrac is None:
            return ccdo(dat, operator="fldmean")
        else:
            return ccdo2(dat, contfrac, operator="fldmean -mul")
    else:
        regions = fds(regions_file, variable='reg_mask')
    
        # Create a region mask and remap it to data grid
        region_mask = cnckso(regions, operator="-d %s,%d"%(region_dimension,region_number))
        region_mask = regrid(region_mask, dat, option="remapnn")
        region_mask = ccdo(region_mask, operator="-setctomiss,0")
        
        if contfrac is not None:
            # Compute area weighted field mean of variable * cont.fraction area over the region
            varmean = ccdo3(dat, contfrac, region_mask, operator="fldmean -mul -mul")
            # Compute area weighted field mean of continental fraction over the region
            fracmean = ccdo2(contfrac, region_mask, operator="fldmean -mul")
            # Divide
            return ccdo2(varmean, fracmean, operator="div")
        else:
            return ccdo2(dat, region_mask, operator="fldmean -mul")
    

# ----------------------------------------------------------------------------
# Aliases for IGCM_OUT - should end up in CLiMAF
# ----------------------------------------------------------------------------
# From old definitions
#SS - à éclaircir - est-ce
calias("IGCM_OUT", 'tair', filenameVar='sechiba_history')
#calias("IGCM_OUT", 'tas', 't2m', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rsds', 'swdown', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rlds', 'lwdown', filenameVar='sechiba_history')
#calias('IGCM_OUT', 'et', 'evspsblveg', filenameVar='sechiba_history')
calias('IGCM_OUT', 'snw', 'snow', filenameVar='sechiba_history')
calias('IGCM_OUT', 'cLitter', filenameVar='stomate_ipcc_history')
calias('IGCM_OUT', 'npp', filenameVar='stomate_ipcc_history')
calias("IGCM_OUT", 'maxvegetfrac', filenameVar='sechiba_history')
calias("IGCM_OUT", 'CONTFRAC', filenameVar='cMisc')

#---------------------------------------------------------------------------
# From mapper.xml
calias("IGCM_OUT", 'alb_nir', filenameVar='sechiba_history')
calias("IGCM_OUT", 'alb_vis', filenameVar='sechiba_history')
calias('IGCM_OUT', 'rss', 'swnet', filenameVar='sechiba_history')
derive("IGCM_OUT", 'rsus',  'minus', 'rss', 'rsds')
calias('IGCM_OUT', 'rsds', 'swdown', filenameVar='sechiba_history')
derive("IGCM_OUT", 'albedo',  'divide', 'rsus', 'rsds')
calias("IGCM_OUT", 'cProduct', filenameVar='stomate_ipcc_history') # glob_coef="1E-12" glob_units="PgC"
calias("IGCM_OUT", 'cSoil',  filenameVar='stomate_ipcc_history') # glob_coef="1E-12" glob_units="PgC"
calias("IGCM_OUT", 'cVeg',  filenameVar='stomate_ipcc_history') # glob_coef="1E-12" glob_units="PgC"
calias("IGCM_OUT", 'drainage', filenameVar='sechiba_history')
calias("IGCM_OUT", 'evspsbl', 'evap', filenameVar='sechiba_history')
calias("IGCM_OUT", 'evspsblsoi', 'evapnu', filenameVar='sechiba_history')
calias('IGCM_OUT', 'hfls', 'fluxlat', filenameVar='sechiba_history')
calias('IGCM_OUT', 'hfss', 'fluxsens', filenameVar='sechiba_history')

#calias("IGCM_OUT", 'gpp_per_vegtype', 'gpp', scale=60*60*24*365/1000., units="kgC/m2/y", filenameVar='sechiba_history') #glob_coef="1E-12" glob_units="PgC/y"

# For simu FG2, there is a gpp time series in dir SBG (and also a GPP)
calias("IGCM_OUT", 'gpp_srf_per_vegtype', 'gpp', scale=60*60*24*365/1000., units="kgC/m2/y", filenameVar='sechiba_history') #glob_coef="1E-12" glob_units="PgC/y"
derive("IGCM_OUT", "gpp_srf", "ccdo" , 'gpp_srf_per_vegtype', operator='vertsum') 

calias("IGCM_OUT", 'gpp_sbg_per_vegtype', 'GPP', scale=365/1000., units="kgC/m2/y", filenameVar='stomate_history') #glob_coef="1E-12" glob_units="PgC/y"
calias("IGCM_OUT", 'VEGET_MAX', filenameVar='stomate_history')
derive("IGCM_OUT", "gpp_sbg", "ccdo2" , 'gpp_sbg_per_vegtype', 'VEGET_MAX', operator='vertsum -mul')

calias("IGCM_OUT", 'gpp', scale=60*60*24*365., units="kgC/m2/y", filenameVar='stomate_ipcc') #glob_coef="1E-12" glob_units="PgC/y"

calias("IGCM_OUT", 'max_vegetfrac', filenameVar='sechiba_history')

calias("IGCM_OUT", 'humrel_per_vegtype', 'humrel', filenameVar='sechiba_history')
derive("IGCM_OUT", "humrel", "ccdo2" , 'humrel_per_vegtype', 'maxvegetfrac', operator='vertsum -mul')

calias("IGCM_OUT", 'inter_per_vegtype', 'inter', filenameVar='sechiba_history', units="mm/d")
derive("IGCM_OUT", "inter", "ccdo" , 'inter_per_vegtype', operator='vertsum')

# Need to use upper case LAI because lai is per veg type in data files
calias("IGCM_OUT", 'lai_per_vegtype', 'lai', filenameVar='sechiba_history', units="m2/m2")
derive("IGCM_OUT", "LAI", "ccdo2" , 'lai_per_vegtype', 'maxvegetfrac', operator='vertsum -mul')

calias("IGCM_OUT", 'lai_sbg_per_vegtype', 'LAI', filenameVar='stomate_history')
derive("IGCM_OUT", "lai_sbg", "ccdo2" , 'lai_sbg_per_vegtype', 'VEGET_MAX', operator='vertsum -mul')

# Absent de ma simu test (FG2)
#calias("IGCM_OUT", 'LAI_MEAN_GS_per_vegtype', 'LAI_MEAN_GS', filenameVar='stomate_history')
#derive("IGCM_OUT", "LAI_MEAN_GS", "ccdo" , 'LAI_MEAN_GS_per_vegtype', operator='vertsum')

calias("IGCM_OUT", 'mrso', filenameVar='sechiba_history')
calias("IGCM_OUT", 'mrsos', filenameVar='sechiba_history')
calias("IGCM_OUT", 'nbp', scale=60*60*24*365, units="kgC/m2/y", filenameVar='stomate_history') # glob_coef="1E-12" glob_units="PgC/y"


calias("IGCM_OUT", 'ra', scale=60*60*24*365, units="kgC/m2/y", filenameVar='stomate_history') #glob_coef="1E-12" glob_units="PgC/y"
calias("IGCM_OUT", 'rh', scale=60*60*24*365, units="kgC/m2/y", filenameVar='stomate_history') #glob_coef="1E-12" glob_units="PgC/y"
calias("IGCM_OUT", 'runoff', filenameVar='sechiba_history')
calias("IGCM_OUT", 'snw', 'snow', filenameVar='sechiba_history')
calias("IGCM_OUT", 'rain', filenameVar='sechiba_history')
calias("IGCM_OUT", 'prsn', 'snowf', filenameVar='sechiba_history')
derive("IGCM_OUT", 'pr', 'ccdo2' , 'rain', 'prsn', operator='sum')
calias("IGCM_OUT", 'ts', 'temp_sol', filenameVar='sechiba_history')
# transpir
calias("IGCM_OUT", 'TWBR', scale=60*60*24, units="mm/d", filenameVar='sechiba_history')
#---------------------------------------------------------------------------


calias("IGCM_CMIP6", 'gpptot', 'gpp')


# Derived variables for IGCM_OUT, from an old version
# ----------------------------------------------------------------------------
# -- GPP on all PFTs
# #SS calias('IGCM_OUT', 'gpp', filenameVar='stomate_ipcc_history')
# calias("IGCM_OUT", 'cfracgpp', 'gpp', filenameVar='stomate_ipcc_history')
# calias("IGCM_OUT", 'GPP', 'gpp', scale=0.001, filenameVar='sechiba_history')
# cscript('select_veget_types', 'ncks ${selection} -v ${var} ${in} ${out}')
# calias("IGCM_OUT", 'Contfrac', filenameVar='sechiba_history')
# calias("IGCM_OUT", "CONTFRAC", filenameVar='landCoverFrac')
# #
# derive("IGCM_OUT", 'gpptot', 'divide', 'cfracgpp', 'Contfrac')
# # GPP * maxvegetfrac * Contfrac
# derive("IGCM_OUT", 'GPPmaxvegetfrac', 'multiply', 'GPP', 'maxvegetfrac')
# derive("IGCM_OUT", 'GPPmaxvegetfracContfrac', 'multiply', 'GPPmaxvegetfrac', 'Contfrac')

# # GPP treeFracPrimDec
# derive('IGCM_OUT', 'GPP3689', 'select_veget_types', 'GPPmaxvegetfracContfrac',
#        selection='-d veget,2 -d veget,5 -d veget,7 -d veget,8')
# derive("IGCM_OUT", 'GPP_treeFracPrimDec', 'ccdo',
#        'GPP3689', operator='vertsum -selname,GPP3689')

# # GPP treeFracPrimEver
# derive('IGCM_OUT', 'GPP2457', 'select_veget_types', 'GPPmaxvegetfracContfrac',
#        selection='-d veget,1 -d veget,3 -d veget,4 -d veget,6')
# derive("IGCM_OUT", 'GPP_treeFracPrimEver', 'ccdo',
#        'GPP2457', operator='vertsum -selname,GPP2457')

# # GPP c3PftFrac
# derive('IGCM_OUT', 'GPP1012', 'select_veget_types',
#        'GPPmaxvegetfracContfrac', selection='-d veget,9 -d veget,11')
# derive("IGCM_OUT", 'GPP_c3PftFrac', 'ccdo',
#        'GPP1012', operator='vertsum -selname,GPP1012')

# # GPP c4PftFrac" (PFTs 11, 13)
# derive('IGCM_OUT', 'GPP1113', 'select_veget_types',
#        'GPPmaxvegetfracContfrac', selection='-d veget,10 -d veget,12')
# derive("IGCM_OUT", 'GPP_c4PftFrac', 'ccdo',
#        'GPP1113', operator='vertsum -selname,GPP1113')

