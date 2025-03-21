# Created by L. Coquart 09/2019 to use ERA5 reanalysis

custom_obs_dict = {
        'tas':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'pr':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        # Ne donne pas de bons resultats sur Atmosphere_Surface
        #'hfls':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        #'hfss':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'psl':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'uas':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'vas':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        # Ne donne pas de bons resultats sur Atmosphere_Surface
        #'rlut':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ua850':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'va850':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ta850':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'hur850':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'hus850':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1980-2018', obs_type='reanalysis', table='Amon'),
        'ua500':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'va500':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ta500':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'hur500':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        #'hus500':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'zg500':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ua200':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'va200':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ta200':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'hur200':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        #'hus200':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ua':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'va':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'ta':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'hur':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'hus':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        'zg':dict(project='ref_era5cerfacs', frequency='monthly', product='ERA5', period='1979-2018', obs_type='reanalysis', table='Amon'),
        }


