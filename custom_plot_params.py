# -*- coding: iso-8859-1 -*-
# Created : S.Sénési - nov 2015
# Adapter : J.Servonnat - april 2016

dict_plot_params = {
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





}

