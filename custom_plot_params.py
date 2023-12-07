# -*- coding: iso-8859-1 -*-
# Created : S.Sénési - nov 2015
# Adapter : J.Servonnat - april 2016

from climaf.utils import ranges_to_string

dict_plot_params = {
    'evap': {
        'default': {'color': 'precip3_16lev', 'units': '', 'scale': 86400},
        'full_field': {'colors': '0 0.1 0.5 1 2 3 4 5 6 7 8 9 10'},
        'bias': {'min': -1, 'max': 1, 'delta': 0.01, 'color': 'BlueWhiteOrangeRed'},
        'model_model': {'min': -0.7, 'max': 0.7, 'delta': 0.05, 'color': 'BlueWhiteOrangeRed'},

    },
    'pr': {
        'default': {'scale': 86400., 'color': 'precip_11lev', 'contours': 1},
        'full_field': {'colors': '0.5 1 2 3 4 6 8 10 12 14'},
        'bias': {'color': 'MPL_BrBG', 'colors': '-10 -8 -6 -4 -2 -1 -0.5 -0.2 0.2 0.5 1 2 4 6 8 10'},
        'model_model': {'color': 'precip_diff_12lev', 'colors': '-5 -2 -1 -0.5 -0.2 -0.1 0.1 0.2 0.5 1 2 5'},
    },
    'prw': {
        'default': {'color': 'precip_11lev', 'contours': 1},
        'full_field': {'min': 0, 'max': 55, 'delta': 5},
        'bias': {'color': 'MPL_BrBG', 'min': -55, 'max': 55, 'delta': 5},
        'model_model': {'color': 'precip_diff_12lev', 'colors': '-5 -2 -1 -0.5 -0.2 -0.1 0.1 0.2 0.5 1 2 5'},
    },
    'crest': {
        # 'full_field': {'colors': '-120 -110 -100 -90 -80 -70 -60 -50 -40 -30 -20 -10'},
        'full_field': {'min': -120, 'max': 0, 'delta': 5, 'color': 'MPL_viridis'},
        'bias': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50', 'color': 'BlueWhiteOrangeRed'},
        'model_model': {'min': -50, 'max': 50, 'delta': 5, 'color': 'BlueWhiteOrangeRed'},
    },
    'cress': {
        # 'full_field': {'colors': '-120 -110 -100 -90 -80 -70 -60 -50 -40 -30 -20 -10'},
        'full_field': {'min': -120, 'max': 0, 'delta': 5, 'color': 'MPL_viridis'},
        'bias': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50', 'color': 'BlueWhiteOrangeRed'},
        'model_model': {'min': -50, 'max': 50, 'delta': 5, 'color': 'BlueWhiteOrangeRed'},
    },
    'rltcre': {
        'full_field': {'colors': '-100 -90 -80 -70 -60 -50 -40 -30 -20 -10 0 10 20 30 40 50 60 70 80 90 100'},
        'bias': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50', 'color': 'BlueWhiteOrangeRed'},
        'model_model': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50'},
    },
    'rstcre': {
        'full_field': {'colors': '-100 -90 -80 -70 -60 -50 -40 -30 -20 -10 0 10 20 30 40 50 60 70 80 90 100'},
        'bias': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50', 'color': 'BlueWhiteOrangeRed'},
        'model_model': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50'},
    },
    'hfls': {
        'default': {},
        'full_field': {'colors': '0 20 40 60 80 100 120 140 160 180 200', 'color': 'WhiteBlueGreenYellowRed'},
        'bias': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 15 25 35 45 55', 'color': 'BlueWhiteOrangeRed'},
        'model_model': {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 15 25 35 45 55'},
    },

    'gpp': {
        'default': {'color': 'precip3_16lev'}
    },
    # 'mrro': {'full_field': dict(colors='0 0.1 0.25 0.5 0.75 1 2 5')},
    # 'mrros': {'full_field': dict(colors='0 0.1 0.25 0.5 0.75 1 2 5')},

    # Next two entries in order to fix a typo in CLiMAF V3.0, for the 'full_field' entries
    'ta700': {
        'default': {'units': 'degC', 'color': 'BlueWhiteOrangeRed', 'offset': -273.15},
        'full_field': {'colors': ranges_to_string(ranges=[[-40, 0, 10], [0, 25, 5]])},
        'bias': {'min': -5, 'max': 5, 'delta': 1, 'offset': 0},
        'model_model': {'min': -10, 'max': 10, 'delta': 1, 'offset': 0}}
    'ta500': {
        'default': {'units': 'degC', 'color': 'BlueWhiteOrangeRed', 'offset': -273.15},
        'full_field': {'colors': ranges_to_string(ranges=[[-40, 0, 10], [0, 25, 5]])},
        'bias': {'min': -5, 'max': 5, 'delta': 1, 'offset': 0},
        'model_model': {'min': -10, 'max': 10, 'delta': 1, 'offset': 0}}





}
