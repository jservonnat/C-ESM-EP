from climaf.api import cscript, derive, calias
from CM_atlas.spatial_integration import average_over_region, integral_over_region

# ----------------------------------------------------------------------------
# All settings for Orchidee variables 'a la MAPPER', and a function to map
# that to C-ESM-EP data structures for component 'maps_and_ts'
# ----------------------------------------------------------------------------
# Also includes definitions of aliases for observation references

orchidee_variables = {    
    "alb_nir" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "", "longname": "Albedo Near Infrared" },
    "alb_vis" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "", "longname": "Albedo Visible" },
    "albedo" : { "formula": "see derive" , "DIR":"SRF", "units": "" , "longname": "Albedo" },
    
    "swnet" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "W/m**2" , "longname": "Surface Net Shortwave Radiation" },
    "swdown" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "W/m**2" , "longname": "Surface Down Shortwave Radiation" },
    "cProduct" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "units": "kgC/m2", "global_sum_scale" : ("1E-12" , "PgC"),  "longname": "Carbon in Products of Land Use Change" },
    "cSoil" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "units": "kgC/m2", "global_sum_scale" : ("1E-12" , "PgC"), "longname": "Carbon in Soil Pool" },
    "cVeg" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "units": "kgC/m2", "global_sum_scale" : ("1E-12" , "PgC"), "longname": "Carbon in Vegetation" },
    "cLitter" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "units": "kgC/m2", "global_sum_scale" : ("1E-12" , "PgC"), "longname": "Carbon in Litter Pool" },
    "fLitterSoil" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "units": "kgC/m2/s", "longname": "Total Carbon Flux from Litter to Soil" },
    "fLuc" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "CO2 Flux to Atm from Land Use Change" },
    "fHarvest" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "CO2 Flux to Atm from Crop Harvesting" },
    "fWoodharvest" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "CO2 Flux to Atm from Wood Harvesting" },
    
    "precip" : { "formula": "see derive", "DIR":"SRF", "units": "mm/d" , "bounds": "0,0.1,0.5,1,2,3,5,8,10,15,20" , "longname": "Precipitation" },
    "drainage" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "longname": "Deep Drainage" },
    "evap" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "longname": "Evapotranspiration" },
    "evapnu" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "longname": "Bare Soil Evaporation" },
    "fluxlat" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "W/m2" , "longname": "Latent Heat Flux" },
    "fluxsens" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "W/m2" , "longname": "Sensible Heat Flux" },
    
    "read_gpp" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "fileVar": "gpp", "coef": "60*60*24*365/1000", "units": "kgC/m2/y" },
    "gpp" : {  "formula": "see derive", "DIR":"SRF", "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Gross Primary Production" },
    "gpp_srf" : { "formula": "see derive", "DIR":"SRF", "filenameVar":"sechiba_history", "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Gross Primary Production" },
    "GPP" : { "DIR":"SBG", "filenameVar":"stomate_history", "coef": "365/1000." , "units": "kgC/m2/y", },
    "gpp_sbg" : { "formula": "see derive", "DIR":"SBG", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Gross Primary Production" },
    "VEGET_MAX" : { "DIR":"SBG", "filenameVar":"stomate_history", },
    "gpp_ipcc" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "fileVar": "gpp", "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Gross Primary Production" },
    
    "read_humrel" : { "DIR":"SRF", "filenameVar":"sechiba_history", "fileVar":"humrel", "units": "" , "longname": "humrel as read" },
    "humrel" : { "formula": "see derive" , "DIR":"SRF", "filenameVar":"sechiba_history","units": "" , "longname": "Soil Moisture Stress for Transpiration" },
    "maxvegetfrac" : { "DIR":"SRF", "filenameVar":"sechiba_history", "units": "" , "longname": "Max Vegetation Fraction" },
    "read_inter" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "fileVar":"inter", "units": "mm/d" , "longname": "Interception Loss per Veg Type" },
    "inter" : {  "formula": "see derive" , "DIR":"SRF", "units": "mm/d" , "longname": "Interception Loss" , "filenameVar":"sechiba_history"},
    "read_lai" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "fileVar":"lai", "units": "m2/m2" , "longname": "Leaf Area Index per Vegetation Type" },
    "lai" : { "formula": "see derive" , "DIR":"SRF", "units": "m2/m2" , "longname": "Leaf Area Index" },
    "LAI_MEAN" : { "DIR":"SBG", "filenameVar":"stomate_history", "units": "m2/m2" , "longname": "Leaf Area Index per vegtype" },
    "lai_sbg" : { "formula": "see derive" , "DIR":"SBG", "units": "m2/m2" , "longname": "Leaf Area Index" },
    "read_LAI_MEAN_GS" : { "DIR":"SBG", "filenameVar":"stomate_history", "fileVar" : "LAI_MEAN_GS"  , "units": "m2/m2" , "longname": "Seasonal Mean Leaf Area Index per Vegtype" },
    "LAI_MEAN_GS" : { "formula": "see derive" , "DIR":"SBG", "units": "m2/m2" , "longname": "Seasonal Mean Leaf Area Index" },
    

    "lwdown" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "W/m2" , "longname": "LW Radiation" },
    "mrso" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "kg/m2" , "longname": "Total Soil Moisture" },
    "mrsos" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "kg/m2" , "longname": "Moisture in Top 10 cm" },
    
    "nbp" : { "fileVar" : "nbp_c", "OUT" : "*", "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Net Biospheric Production" },
    "npp" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Net Primary Production" },
    "rain" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "bounds": "0,0.1,0.5,1,2,3,5,8,10,15,20" , "longname": "Rain Fall" },
    "snowf" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "bounds": "0,0.1,0.5,1,2,3,5,8,10,15,20" , "longname": "Snow Precipitation" },
    "ra" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Autotrophic Respiration" },
    "rh" : { "DIR":"SBG", "filenameVar":"stomate_ipcc_history",  "coef": "60*60*24*365" , "units": "kgC/m2/y", "global_sum_scale" : ("1E-12" , "PgC/y"), "longname": "Heterotrophic Respiration" },
    
    "runoff" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "longname": "Surface Runoff" },
    "snow" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "kg/m2" , "bounds": "0,25,50,75,100,200,300,400,500,750,1000" , "longname": "Snow Mass" },
    "snowf" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "bounds": "0,0.1,0.5,1,2,3,5,8,10,15,20" , "longname": "Snow Fall" },
    "swdown" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "W/m2" , "longname": "SW Radiation" },
    "t2m" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "offset": "-273.15" , "units": "degC" , "longname": "Air Temperature at 2m" },
    "tair" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "offset": "-273.15" , "units": "degC" , "longname": "Air Temperature" },
    "temp_sol" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "degC" , "longname": "Surface Temperature" },
    
    "read_transpir" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "fileVar": "transpir", "units": "mm/d" , "longname": "Transpiration per vegtype" },
    "transpir" : { "formula": "see derive", "DIR":"SRF", "units": "mm/d" , "longname": "Transpiration" },
    
    "twbr" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "fileVar": "TWBR", "coef": "60*60*24" , "units": "mm/d" , "longname": "Total Water Budget Residu" },
    "precisol" : { "DIR":"SRF", "filenameVar":"sechiba_history",  "units": "mm/d" , "longname": "precisol" },
    
    
    # Atmospheric forcing input variables 
    "Tair" : { "offset": "-273.15" , "units": "degC" , "maplim": "-30,30" , "longname": "Air Temperature" },
    "PSurf" : { "coef": "1E-3" , "units": "kPa" , "maplim": "50,100" , "longname": "Pressure" },
    "Qair" : { "coef": "1E3" , "units": "mg/g" , "maplim": "0,20" , "longname": "Air Specific Humidity" },
    "Rainf" : { "coef": "60*60*24" , "units": "mm/d" , "bounds": "0,0.1,0.5,1,2,3,5,8,10,15,20" , "longname": "Rainfall" },
    "Snowf" : { "coef": "60*60*24" , "units": "mm/d" , "bounds": "0,0.1,0.5,1,2,3,4,5,6,7,8" , "longname": "Snowfall" },
    "SWdown" : { "units": "W/m2" , "maplim": "50,300" , "longname": "Incoming Shortwave Radiation" },
    "LWdown" : {  "units": "W/m2" , "maplim": "100,400" , "longname": "Incoming Longwave Radiation" },
    
    # Ratio-derived variables 
    "ratio_ep" : { "ratio": "evap/precip" , "units": "" , "maplim": "0,2" , "diflim": "1" , "ratio_threshold": "1E-3" , "longname": "Evapotranspiration-Precipitation Ratio" },
    "ratio_gt" : { "ratio": "gpp_srf/transpir" , "units": "" , "maplim": "0,1" , "ratio_threshold": "1E-3" , "longname": "GPP-Transpiration Ratio" },
    "ratio_ie" : { "ratio": "inter/evap" , "units": "" , "maplim": "0,1" , "ratio_threshold": "1E-3" , "longname": "Interception-Evapotranspiration Ratio" },
    "ratio_lf" : { "ratio": "cLitter/fLitterSoil" , "units": "y" , "ratio_threshold": "1E-3" , "longname": "cLitter-fLitterSoil Ratio" },
    "ratio_ng" : { "ratio": [ ("npp",{}), ("gpp_srf",{"DIR":"SRF"})] , "units": "" , "maplim": "0,1" , "ratio_threshold": "1E-8" , "longname": "NPP-GPP Ratio" },
    "ratio_te" : { "ratio": "transpir/evap" , "units": "" , "maplim": "0,1" , "ratio_threshold": "1E-3" , "longname": "Transpiration-Evapotranspiration Ratio" },
    "ratio_tr" : { "ratio": "precisol/rain" , "units": "" , "maplim": "0.5,1.5" , "diflim": "0.25" , "ratio_threshold": "1E-3" , "longname": "Throughfall-Rain Ratio" },
    "ratio_vn" : { "ratio": "cVeg/npp" , "units": "y" , "ratio_threshold": "1E-3" , "longname": "cVeg-NPP Ratio" },    

}

def declare_orchidee_alias_for_observations():
    # Explain how Orchidee variable names map to observation's variable names
    # (for those obs data handled by project 'ref_climatos')
    calias("ref_climatos", "alb_vis","albvis")         
    calias("ref_climatos", "alb_nir","albnir")
    calias("ref_climatos", "LAI","lai")
    calias("ref_climatos", "lwdown","rlds")
    calias("ref_climatos", "swdown","rsds")
    calias("ref_climatos", "albedo","alb")
    calias("ref_climatos", "temp_sol","ts")
    
# Can define specific reference observations, on a per-variable basis.
# This will complement root custom_obs_dict
orchidee_custom_obs_dict = dict(
    #fluxlat  = dict(project='ref_climatos', product='EnsembleLEcor', frequency='annual_cycle'),
)


def init_orchidee_variables(variables_setup, plots_setup, time_series_setup,
                            variables_specifics, special_project_specs):

    # For variables in variables_setup, update variables_specifics,
    # special_project_specs, plots_setup and time_series_setup with
    # content of orchidee_variables.

    # Also let CliMAF know about some units, scaling,
    # filenames... using calias, and know about formulas using derive

    #calias("IGCM_OUT", 'CONTFRAC',  filenameVar='stomate_history')
    
    # Declare all variables to CliMAF, 
    for variable,defs in orchidee_variables.items():
        if "formula" not in defs:
            calias("IGCM_OUT", variable=variable, fileVariable = defs.get("fileVar",None),
                   scale = eval(defs.get("coef","1.0")), offset = eval(defs.get("offset", "0.")),
                   units = defs.get("units", None), filenameVar = defs.get("filenameVar",None) )
    
    # Variables defined by formulas
    derive("IGCM_OUT", 'precip',  'ccdo2', 'snowf', 'rain', operator='add')
    cscript("compute_albedo", "cdo mulc,-1. -subc,1 -div ${in_1} ${in_2} ${out}", _var="albedo")
    derive("IGCM_OUT", 'albedo',  'compute_albedo', 'swnet', 'swdown')
    derive("IGCM_OUT", "gpp", "ccdo", "read_gpp", operator="vertsum")
    derive("IGCM_OUT", "gpp_srf", "ccdo", "read_gpp", operator="vertsum")
    derive("IGCM_OUT", "GPP", "ccdo2", "read_gpp", "VEGET_MAX", operator="vertsum -mul")
    derive("IGCM_OUT", "humrel", "ccdo2", "read_humrel", "maxvegetfrac", operator="vertsum -mul")
    derive("IGCM_OUT", "inter", "ccdo", "read_inter", operator="vertsum")
    derive("IGCM_OUT", "lai", "ccdo2", "read_lai", "maxvegetfrac", operator="vertsum -mul")
    derive("IGCM_OUT", "lai_sbg", "ccdo2", "LAI_MEAN", "VEGET_MAX", operator="vertsum -mul")
    derive("IGCM_OUT", "LAI_MEAN_GS", "ccdo2", "read_LAI_MEAN_GS", "VEGET_MAX", operator="vertsum -mul")
    derive("IGCM_OUT", "transpir", "ccdo", "read_transpir", operator="vertsum")

    for category,specs in variables_setup.items():
        for variable in specs['variables'].copy():
            if variable not in orchidee_variables: 
                print("!! Cannot process un-documented variable %s"%variable)
                specs['variables'].remove(variable)
                continue
            #
            defs=orchidee_variables[variable]
            #
            special_project_specs.setdefault(variable,{"IGCM_OUT":{}})
            for key in [ "DIR", "OUT" ]:
                if key in defs:
                    special_project_specs[variable]["IGCM_OUT"][key]=defs[key]
            #
            variables_specifics.setdefault(variable,{})
            for key in ["global_sum_scale", "longname", "ratio", "ratio_threshold","units" ]:
                if key in defs:
                    variables_specifics[variable][key] = defs[key]
            #
            plots_setup.setdefault(variable,{})
            if "bounds" in defs:
                plots_setup[variable].update(colors=defs["bounds"].replace(","," "))
            if "maplim" in defs:
                min,max = defs["maplim"].split(",")
                plots_setup[variable]["min"] = float(min)
                plots_setup[variable]["max"] = float(max)
                plots_setup[variable]["delta"] = (float(max) - float(min)) / 20.
            #
            time_series_setup.setdefault(variable,{"contfrac" : "nc"})
            if "global_sum_scale" in defs :
                time_series_setup[variable].update({"operation": integral_over_region})
                display_units = defs["global_sum_scale"][1]
            else:
                time_series_setup[variable].update({"operation": average_over_region})
                display_units = defs["units"]
            time_series_setup[variable]["ylabel"] = defs["longname"] + " [ %s ]"%display_units
            #
            if "ratio" in defs :
                ratio_specs = defs['ratio']
                if type(ratio_specs) is str:
                    # e.g. "evap/precip"
                    numerator = ratio_specs.split('/')[0]
                elif type(ratio_specs) is list:
                    # e.g. [ ("npp",{}), ("gpp_srf",{"DIR":"SRF"})] 
                    numerator = ratio_specs[0][0]
                else:
                    raise ValueError("Cannot interpret field ratio :" + repr(ratio))
                if numerator not in orchidee_variables:
                    print("!! Ratio numerator for %s (%s) is not documented"%(variable,numerator))
                    specs['variables'].remove(variable)
                else:
                    variables_specifics[variable]["filenameVar"]=\
                        orchidee_variables[numerator].get("filenameVar","*")
                    for key in [ "DIR", "OUT" ]:
                        if key in orchidee_variables[numerator]:
                            special_project_specs[variable]["IGCM_OUT"][key]= \
                                orchidee_variables[numerator][key]

