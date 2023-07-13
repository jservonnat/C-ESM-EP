#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Defining locations and rendering for C-ESM-EP atlas
# SS - August 2018

# -- Python 2 <-> 3 compatibility ---------------------------------------------------------
from __future__ import unicode_literals, print_function, absolute_import, division

import getpass
import os

# Identify on which system we are running, generally using a CliMAF module

# On TGCC and IDRIS , we wish to avoid having to use CliMAF in this
# utility script, because CliMAF is available through a docker container,
# and we would like to avoid using this slightly heavy procedure
# when executing this script
if os.path.exists('/ccc') and not(os.path.exists('/data')):
    atCNRM = onCiclad = onSpirit = atCerfacs = False
    atTGCC = atIPSL = True
elif os.path.exists('/gpfsdswork'):
    atCNRM = onCiclad = onSpirit = atCerfacs = atTGCC = False
    atIDRIS = atIPSL = True

else:
    from env.site_settings import atCNRM, onCiclad, onSpirit, atTGCC, atCerfacs, atIDRIS

username = getpass.getuser()

# -- path_to_cesmep_output_rootdir is the location of the root output directory
# -- where we store all the C-ESM-EP comparisons
# path_to_cesmep_output_rootdir = '/prodigfs/ipslfs/dods/'+username
#
# -- Path that follows root_url to access path_to_cesmep_output_rootdir from a web page
# root_url_to_cesmep_outputs = "https://vesg.ipsl.upmc.fr/thredds/fileServer/IPSLFS/"+username
#
# -- At TGCC you can have a different path to access the data that are visible from the web
#    than the path where you actually stored your data (ex: path to thredds )
# -- Can be equal to path_to_cesmep_output_rootdir (simply set to None)
# path_to_cesmep_output_rootdir_on_web_server = None


if atCNRM:
    # Climaf Cache location - used for launching batch jobs in run_C-ESM-EP.py
    # This could be a location shared among users.
    # This can also be a location visible only from compute cluster (aneto)
    climaf_cache = '/cnrm/est/USERS/' + username + '/NO_SAVE/CESMEP_climaf_cache'

    # Root on file system for atlas.
    # If using http for rendering, this should be somehow visible by the http server
    # This value is used as 'pathwebspace' in run_C-ESM-EP.py
    # It will be complemented with 'C-ESM-EP/'
    # This location can be shared among users, as username will be added at end of data path
    path_to_cesmep_output_rootdir = '/cnrm/est/USERS/' + username + '/NO_SAVE/'

    # Describe the rendering method; if it is http, must match the workspace and the adress for http server
    # For now, at CNRM, we do not use http:// but file:// for atlas rendering
    root_url_to_cesmep_outputs = 'file://'+path_to_cesmep_output_rootdir
    #
    path_to_cesmep_output_rootdir_on_web_server = None

# -- Ciclad
if onCiclad:
    # -- path_to_cesmep_output_rootdir is the location of the root output directory
    # -- where we store all the C-ESM-EP comparisons
    path_to_cesmep_output_rootdir = '/thredds/ipsl/'+username
    # --
    # -- Path that follows root_url to access path_to_cesmep_output_rootdir from a web page
    root_url_to_cesmep_outputs = "https://vesg.ipsl.upmc.fr/thredds/fileServer/IPSLFS/"+username

    # -- At TGCC you can have a different path to access the data that are visible from the web
    #    than the path where you actually stored your data (ex: path to thredds )
    # -- Can be equal to store_atlas_results_dir, but at TGCC
    path_to_cesmep_output_rootdir_on_web_server = None
    #
    climaf_cache = '/scratchu/' + username + '/atlas_explorer'

# -- Spirit
if onSpirit:
    # -- path_to_cesmep_output_rootdir is the location of the root output directory
    # -- where we generate all the C-ESM-EP comparisons (later moved to thredds)
    path_to_cesmep_output_rootdir = '/scratchu/' + \
        username  # Pour résultats des comparaisons
    #
    # -- path
    path_to_cesmep_output_rootdir_on_web_server = '/thredds/ipsl/' + \
        username  # pour index général
    # --
    # -- Path that follows root_url to access path_to_cesmep_output_rootdir from a web page
    root_url_to_cesmep_outputs = "https://thredds-su.ipsl.fr/thredds/fileServer/ipsl_thredds/"+username
    climaf_cache = '/scratchu/' + username + '/atlas_explorer'


# -- TGCC
if atTGCC:
    # Components outputs will be temporarily on scratchdir, and
    # ultimately copied on workdir, with a hard link on the thredds
    # (using thredds_cp)
    scratch = os.getenv("CCCSCRATCHDIR")
    path_to_cesmep_output_rootdir = scratch

    work = os.getenv("CCCWORKDIR")
    # Should be the project label, e.g. gencmip6, gen0826
    project = str(work.split("/")[4])
    thredds = work.replace('/'+project+'/', '/thredds/')
    path_to_cesmep_output_rootdir_on_web_server = thredds
    root_url_to_cesmep_outputs = 'https://thredds-su.ipsl.fr/thredds/fileServer/' +\
        'tgcc_thredds/work/' + username

    climaf_cache = scratch + '/cache_atlas_explorer'

# -- IDRIS
if atIDRIS:
    # Components outputs will be temporarily on scratchdir, and
    # ultimately copied on workdir, with a hard link on the thredds
    # (using thredds_cp)
    scratch = os.getenv("SCRATCH")
    path_to_cesmep_output_rootdir = scratch
    # thredds_cp requires relative target paths
    path_to_cesmep_output_rootdir_on_web_server = "." 
    root_url_to_cesmep_outputs = 'https://thredds-su.ipsl.fr/thredds/fileServer/' +\
        'idris_thredds/work/' + username
    climaf_cache = scratch + '/cache_atlas_explorer'


# At Cerfacs
if atCerfacs:
    # On scylla
    if os.path.exists('/data/scratch/globc'):
        # Climaf Cache location - used for launching batch jobs in run_C-ESM-EP.py
        # This could be a location shared among users.
        # This can also be a location visible only from compute cluster (aneto)
        climaf_cache = '/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/CESMEP_climaf_cache'

        # Root on file system for atlas.
        # If using http for rendering, this should be somehow visible by the http server
        # This value is used as 'pathwebspace' in run_C-ESM-EP.py
        # It will be complemented with 'C-ESM-EP/'
        # This location can be shared among users, as username will be added at end of data path
        path_to_cesmep_output_rootdir = '/data/scratch/globc/dcom/CMIP6_TOOLS/C-ESM-EP/CESMEP_html'

        # Describe the rendering method; if it is http, must match the workspace and the adress for http server
        # For now we do not use http:// but file:// for atlas rendering
        root_url_to_cesmep_outputs = 'http://cerfacs.fr/giec6/C-ESM-EP/CESMEP_html/'
        #
        path_to_cesmep_output_rootdir_on_web_server = None

    elif os.path.exists('/scratch/globc'):
        # Climaf Cache location - used for launching batch jobs in run_C-ESM-EP.py
        # This could be a location shared among users.
        # This can also be a location visible only from compute cluster (aneto)
        climaf_cache = '/scratch/globc/' + username + '/C-ESM-EP/CESMEP_climaf_cache'

        # Root on file system for atlas.
        # If using http for rendering, this should be somehow visible by the http server
        # This value is used as 'pathwebspace' in run_C-ESM-EP.py
        # It will be complemented with 'C-ESM-EP/'
        # This location can be shared among users, as username will be added at end of data path
        path_to_cesmep_output_rootdir = '/scratch/globc/' + \
            username + '/C-ESM-EP/CESMEP_html'

        # Describe the rendering method; if it is http, must match the workspace and the adress for http server
        # For now we do not use http:// but file:// for atlas rendering
        root_url_to_cesmep_outputs = 'file://'+path_to_cesmep_output_rootdir
        #
        path_to_cesmep_output_rootdir_on_web_server = None


# Override climaf_cache with env variable CESMEP_CLIMAF_CACHE if (really) set
cesmep_climaf_cache = os.getenv("CESMEP_CLIMAF_CACHE", "")
if cesmep_climaf_cache != "":
    climaf_cache = cesmep_climaf_cache
