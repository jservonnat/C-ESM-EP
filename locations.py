# Defining locations and rendering for C-ESM-EP atlas 
# SS - August 2018

import getpass, os.path
username=getpass.getuser()

if os.path.exists('/cnrm'):  
    # Climaf Cache location - used for launching batch jobs in run_C-ESM-EP.py
    # This could be a location shared among users.
    # This can also be a location visible only from compute cluster (aneto)
    climaf_cache='/cnrm/est/USERS/'+username+'/NO_SAVE/CESMEP_climaf_cache'

    # Root on file system for atlas.
    # If using http for rendering, this should be somehow visible by the http server
    # This location can be shared among users, as username will be added at end of data path
    # This value is used as 'pathwebspace' in run_C-ESM-EP.py
    # It will be complemented with 'C-ESM-EP/'
    workspace='/cnrm/est/USERS/'+username+'/NO_SAVE/'
    
    # Describe the rendering method; if it is http, must match the workspace and the adress for http server
    # For now, at CNRM, we do not use http:// but file:// for atlas rendering 
    root_url = 'file://'
    pathwebspace=workspace  # used as 'alt_dir_name' in main_C-ESM-EP.py, for building the full URL
    base_url = root_url+pathwebspace
    
    
