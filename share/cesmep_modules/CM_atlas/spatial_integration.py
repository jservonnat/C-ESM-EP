import os
from six import string_types
from climaf.api import *

def average_over_region(dat, region_number=None, regions_file=None,
                               contfrac = None, region_dimension = "reg",
                              fldmean = "fldmean", **kwargs):

    """Compute space average (or sum) for a field represented by CliMAF object
    DAT, integrating over a region identified by REG_DIMENSION =
    REGION_NUMBER in file REGIONS_FILE, and only over its land part
    when CONTFRAC is not None and represents the continental fraction
    on the same grid of DAT (coded with 1s over the region and 0 or
    missing value elsewhere)

    Default is a space average. In order to get a space integral, just
    call with fldmean = "fldint" 
    
    If one of the args related to the region is None, the whole domain
    is used

    The REGIONS_FILE structure (with vars reg_mask, reg_id, reg_label)
    is examplified by <main_cesmep_path>/data/regs_360720.nc on spirit
    It looks like region files in Mapper, except that you must add
    attributes standard_name and units to lat & lon
    
    The regions data is remapped to DAT's grid using nearest neighbour

    CONTFRAC must be either a CliMAF object representing, or a file
    providing, the continental fraction, ON THE SAME GRID AS DAT

    """
    
    # Regions_file : holds variable reg_mask(reg,lat,lon), which has
    # value 1 in the region and 0 elsewhere
    # We assume that region masks are conservative re. land extent.
    
    # When called by diagnostics_ts, this function also receives
    # region's id as arg 'region' and region's (long) name as arg
    # 'region_name' (through kwargs)
    
    if contfrac is not None :
        if isinstance(contfrac, string_types) and os.path.exists(contfrac):
            contfrac = fds(contfrac)
        contfrac = ccdo(contfrac, operator="-setctomiss,0")

    if regions_file is None or region_number is None :
        if contfrac is None:
            return ccdo(dat, operator=fldmean)
        else:
            return ccdo2(dat, contfrac, operator=fldmean+" -mul")
    else:
        regions = fds(regions_file, variable='reg_mask')
    
        # Create a region mask and remap it to data grid
        region_mask = cnckso(regions, operator="-d %s,%d"%\
                             (region_dimension,region_number))
        region_mask = regrid(region_mask, dat, option="remapnn")
        region_mask = ccdo(region_mask, operator="-setctomiss,0")
        
        if contfrac is not None:
            # Compute area weighted field integral of variable *
            # cont.fraction area over the region
            var_integral = ccdo3(dat, contfrac, region_mask, \
                                 operator="fldint -mul -mul")
            if fldmean == "fldint":
                return var_integral            
            elif fldmean == "fldmean":
                # Compute area weighted field integral of continental
                # fraction over the region
                frac_integral = ccdo2(contfrac, region_mask, operator="fldint -mul")
                # Divide
                return ccdo2(var_integral, frac_integral, operator="div")
        else:
            return ccdo2(dat, region_mask, operator=fldmean+" -mul")
    

def integral_over_region(dat, region_number=None, regions_file=None,
                              contfrac = None, region_dimension = "reg", **kwargs):
    """ See comments of space_average_over_region""" 
    return average_over_region(dat, region_number=region_number,
                                     regions_file=regions_file, contfrac=contfrac,
                                     region_dimension=region_dimension,
                                     fldmean="fldint" , **kwargs)
