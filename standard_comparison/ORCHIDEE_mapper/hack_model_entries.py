# This is an example of a function that allows to modify the dataset's
# definition used by C-ESM-EP, i.e. the entries defined in list
# 'models' of datasets_setup.py, and in list Wmodels of
# datasets_setup_available_period_set.py.

# Such a function is applied to each of this entries, just after their
# are loaded in C-ESM-EP main program. This, provided it can be
# imported from a module named hack_model_entries.

# Locating such a module in a component directory allows to limit the
# changes to the desired component

# Note: at the stage of applying that function, the parameters file
# and the diagnostic file have not yet been executed by C-ESM-EP main



# Here, for diagnostic ORCHIDEE_mapper, and when the run is
# configured by libIGCM, we change key OUT, if present, to
# systematically use value 'Output'.

# This is needed because not all geophysical variables needed by this
# diag are actually available in OUT Analyse (while this is not the
# case for other diags)

try :
    import libIGCM_settings
except:
    def hack_model_entry(model):
        pass
else:
    def hack_model_entry(model):
        #
        if 'OUT' in model :
            model['OUT'] = 'Output'
            model['frequency'] = 'monthly'
