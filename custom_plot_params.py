# -*- coding: iso-8859-1 -*-
# Created : S.Sénési - nov 2015
# Adapter : J.Servonnat - april 2016

dict_plot_params = {
       'pr' : {
              'default'  : { 'scale' : 86400. , 'color' : 'precip_11lev' , 'contours' : 1 },
            'full_field'   : {'colors':'0.5 1 2 3 4 6 8 10 12 14'  },
            'bias'        : {'color':'MPL_BrBG','colors': '-10 -8 -6 -4 -2 -1 -0.5 -0.2 0.2 0.5 1 2 4 6 8 10' },
            'model_model' : {'color':'precip_diff_12lev','colors': '-5 -2 -1 -0.5 -0.2 -0.1 0.1 0.2 0.5 1 2 5'},
        },
       'crest' : {
            #'full_field'   : {'colors':'-120 -110 -100 -90 -80 -70 -60 -50 -40 -30 -20 -10'  },
            'full_field' :{'min':-120,'max':0,'delta':5,'color':'MPL_viridis'},
            'bias'        : {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50' , 'color':'BlueWhiteOrangeRed' },
            'model_model' : {'min':-50,'max':50,'delta':5, 'color':'BlueWhiteOrangeRed'},
        },
       'cress' : {
            #'full_field'   : {'colors':'-120 -110 -100 -90 -80 -70 -60 -50 -40 -30 -20 -10'  },
            'full_field' :{'min':-120,'max':0,'delta':5,'color':'MPL_viridis'},
            'bias'        : {'colors': '-50 -40 -30 -20 -10 -5 -2 2 5 10 20 30 40 50' , 'color':'BlueWhiteOrangeRed' },
            'model_model' : {'min':-50,'max':50,'delta':5, 'color':'BlueWhiteOrangeRed'},
        },


}
