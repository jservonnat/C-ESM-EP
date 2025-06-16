import matplotlib.pyplot as plt
import xarray as xr

# A convenience function that will soon be available in CliMAF
#-------------------------------------------------------------
def cxr(cobj):
    """ Returns an Xarray representing Climaf object COBJ """
    with xr.open_dataset(cfile(cobj)) as f:
        return f[cobj.variable]
    
# Declaring script get_sistemp to CliMAF
#---------------------------------------------
#path = '/home/ssenesi/IPSL_2025/kenza/'
path = '/home/jdeshayes/TOOLS/C-ESM-EP/C-ESM-EP-dev/git/JD_compares_SI3_Kenza/ICEseas/'
# Le script d'origine a ét modifié pour sortir deux fichiers netcdf.
# On choisit de décrire une sortie principale 'out' pour la simu et de nommer 'obs' 
# les données de sortie relatives aux obs
cscript('sistemp_cycle', 
#        "python " + path + "get_sistemp.py ${hemisphere} ${in_1} ${in_2} ${out} ${out_obs}", 
#        "python " + path + "get_sistemp_2_inputs.py ${hemisphere} ${in_1} ${in_2} ${out} ${out_obs}", 
        "python " + path + "get_sistemp_2_inputs.py ${hemisphere} ${in_1} ${in_2} ${out}", 
        _var="sea_ice_stemp_model")
#        obs_var="sea_ice_stemp_obs")
#---------------------------------------------

# We could also have a script that directly returns the plot
#---------------------------------------------
# cscript('plot_cycle',' toto.py ${in} ${out} ${title}', format='png')
# figure_file = plot_cycle(cycle,cycle.obs,title="")
       


# Handling html matters
if atlas_head_title is None :
    atlas_head_title = "ICE seasonal diagnostics"
index = header(atlas_head_title, style_file=style_file)
index += section("My own CliMAF diagnostic", level=4)
figure_size = thumbnail_size_global # defined in share/default/default_atlas_settings.py
index += open_table()  
index += line(['Diag #1 = amplitude of the annual cycle'])

Wmodels = copy.deepcopy(models) # `models` is usually set by datasets_setup.py
print(Wmodels)

my_own_climaf_diag_variables = ['sistem', 'siconc']

for variable in my_own_climaf_diag_variables: #["sistem"]:
    #
    index += open_line()  # the figures for all models will lay on a single line
    for model in Wmodels:
        #
        wmodel = model.copy()  # - avoid modifying the original dictionary
        wmodel["variable"] = variable
        wmodel = get_period_manager(wmodel, diag='clim')
        wmodel.pop('variable')
        #
        # Get the dataset and compute the requested diag
        #if variable == 'sistem':
            #var_group = 'siconc,sistem'
            # Next command has two effects :
            #   - tell that some variable has to be found in a file
            #     having 'icemod' at the location devoted to the variable name
            #   - tell that 'icemod' can be used to provide a GROUP of variables
         var_group = 'siconc'
         calias("IGCM_OUT", var_group, filenameVar="icemod")
            dat1 = ds(variable = var_group, **wmodel)
            var_group = 'sistem'
            calias("IGCM_OUT", var_group, filenameVar="icemod")
            dat2 = ds(variable = var_group, **wmodel)
            cycle = sistemp_cycle(dat1,dat2, hemisphere='n')
            
        else:
            # No other variable yet implemented
            continue
        #
        # -- Plot the amplitude of the annual cycles
        fig,_ = plt.subplots()

        cxr(cycle).plot()
        # An equivalent to above :
        # file_simu = cfile(cycle)
        # f= xr.open_dataset(file_simu)
        # simu_xr = file_simu[cycle.variable]
        # simu_xr.plot()
        
#        cxr(cycle.obs).plot()

        figure_file = "%s_%s_%s.png"%(variable,wmodel["simulation"], wmodel["period"])
        fig.savefig(fname=figure_file)
        #
        # ==> -- Add the plot to the figures line
        index += cell("", figure_file, thumbnail=figure_size, hover=False, **alternative_dir)
index += close_line()  # One line for all models and a single variable
#
# ==> -- Close the table before possibly adding a section
index += close_table()


