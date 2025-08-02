# Module for generating an html page 'a la Mapper', based on companion
# script mapper.js. It provides 2 functions for generating filenames
# for maps and timeseries images, compatible with mapper.js conventions

def mapper_simu_name(simu):
    if type(simu) is dict:
        if 'customname' in simu :
            return simu['customname']
        elif 'product' in simu :
            return simu['product']
        elif simu.get('project',None) in ['IGCM_OUT']:
            return simu['simulation']
        elif simu.get('project',None) in [ 'CMIP6', 'CMIP5' ]:
            return simu['experiment']
        else :
            return simu['experiment']
    else:
        return simu

# A function for computing a map image filename based on some parameters
# that define its content. It mimics Mappers's convention. Returned value
# has no extension
def mapper_map_filename(simu1, simu2, variable, season):
    # This is also an example of the interface for a function provided as
    # argument to cesmep_diagnostics.CM_atlas.plot_CM_atlas.section_2D(),
    rep = mapper_simu_name(simu1)
    if simu2 :
        rep += '_vs_' + mapper_simu_name(simu2)
    rep += '_' + variable + '_' + season.lower()
    return rep


# A function for computing a times_series image filename based on some
# parameters that define its content. It mimics Mappers's convention
# Returned value has no extension
def mapper_ts_filename(region, variable, frequency):
    abbrev = { 'yearly' : 'y', "annual_cycle" : 's' , "monthly" : 'm' }
    return variable + '_' + abbrev[frequency] + '_' + region


def build_mapper_page(models, variables_setup, case_toggles, seasons, ts_frequencies,
                      ts_regions, ts_regions_file,  custom_obs_dict,
                      variables_specifics, title ):
    # We want to build a page like that :
    
    # <html>
    # <head>
    # <title>CESMEP</title>
    # <script type="text/javascript">
    
    # let sims = ["FGH.ORC22v8514", "FGH.ORC3v8120", "FGH.ORC4v8828.A", "FGH.ORC4v8828.B"];
    # let types = ["map", "ts"];
    # let map_freqs = ["ye", "3m"];
    # let ts_freqs = ["ye", "mo", "se"];
    # let mods = ["map", "vsobs", "vs0"];
    # let regs = ["g", "n", "t", "s", "amnbo", "amnte", "amstr", "amste", "eu", "afn", "afs", "asbo", "aste", "astr", "auzea"];
    # let vars = { "energy" : ["alb_nir", "fluxlat", "fluxsens"],
    #              "water" : ["mrso", "transpir", "evap"],
    #              "carbon" : ["gpp", "nbp", "lai"] };
    # let obs = {"alb_nir" : "modis",
    #            "fluxlat" : ["jung","jung"],
    #            "fluxsens" : "jung"};
    # let labels = { 
    #                "map" : "Maps",
    #                "ts" : "Time-Series",
    #                "sim" : "Simulations",
    #                "var" : "Variables",
    #                "freq" : "Frequencies",
    #                "mod" : "Modes",
    #                "reg" : "Regions",
    #                "energy" : "Energy Budget",
    #                ...
    #                "ye" : "Yearly",
    #                "3m" : "3-monthly",
    #                "mo" : "Monthly",
    #                "se" : "Seasonal Cycle",
    #                "g" : "Global Land",
    #                "n" : "Northern Land",
    #                 ...
    #                // variable long-names
    #                "alb_nir" : "Albedo Near Infrared",
    #                ...
    #                "lai" : "Leaf Area Index"};
    # </script>
    # <script src="mapper.js"></script> 
    # <link rel="stylesheet" href="interf.css">
    
    # </head>
    
    # <body onload="makeInterf(); makeTable();">
    # <p>C-ESM-EP comparison</p>
    # <div id="interf"></div>
    # <div id="table"></div>
    # </body>
    
    # </html>
    
    def plist(name, liste, trans=None, crlf=False):
        """
        Returns the javascript syntax for declaring list (or dict) LISTE.
        If CRLF is True , a newline is inserted between elements
        If NAME is not None, the returned construct begins with
        "let name = " and ends with ";"
        TRANS is a function or a dict for translating the values in LIST
        """
        dico = type(liste) is dict
        #
        if dico : begin,end = "{","}"
        else:         begin,end = "[","]"
        #
        rep = ""
        if name is not None : rep += f"let {name} = "
        rep += begin
        if crlf : rep += "\n"
        for el in liste :
            quote = '"'
            if crlf : rep += "  "
            if dico :
                rep += ' "%s" :'%el
                v = liste[el]
                if type(v) is list:
                    v = plist(None, v, trans=trans)
                    quote=''
            else:
                v = el
            if trans is None :
                rep += ' %s%s%s,'%(quote,v,quote)
            elif type(trans) is dict :
                if v in trans:
                    rep += ' %s%s%s,'%(quote,trans[v],quote)
                else:
                    rep += ' %s%s%s,'%(quote,v,quote)
            else:
                rep += ' %s%s%s,'%(quote,trans(v),quote)
            if crlf : rep += "\n"
        rep += end 
        if name is not None : rep += ";\n"
        if crlf : rep += "\n"
        return rep

    translate = {
        'yearly' : 'ye',
        'monthly' : 'mo',
        'annual_cycle' : 'se',
        'maps' : "map",
        'anomalies' : "vsobs",
        'diffs' : "vs0",
        }
    page = '<html>\n<head>\n<title>CESMEP</title>\n<script type="text/javascript">\n'
    page += 'let pngPath = "./";\n'
    page += plist("sims", models, mapper_simu_name)

    page += 'let types = ['
    if any([ case_toggles[k] for k in ['maps', 'anomalies', 'diffs' ]]):
           page += '"map", '
    if case_toggles['time_series']:
           page += '"ts", '
    page += '];\n'

    oseasons = []
    if 'ANM' in seasons : oseasons.append('ye')
    if len([ s for s in seasons if s != 'ANM' ]) > 1 : oseasons.append('3m')
    oseasons.extend([ s.lower() for s in seasons if s != 'ANM' ])
    page += plist("map_freqs", oseasons)
    
    page += plist("ts_freqs", ts_frequencies, translate)
    mods = [mod for mod in case_toggles if case_toggles[mod] and mod != "time_series"]
    if 'diffs' in mods and len(models) < 2 :
        mods.remove('diffs')
    page += plist("mods", mods, translate)
    page += plist("regs", ts_regions, translate)
    page += plist("vars", { category: entry['variables'] for category,entry in variables_setup.items()}, crlf=True)
    # Must build obs_dict
    obs_dict = { variable : custom_obs_dict[variable]['product'] for variable in custom_obs_dict \
                 if any([ (variable in entry['variables']) for entry in variables_setup.values() ]) }
    page += plist("obs", obs_dict, crlf=True)
    labels = { 
        "map" : "Maps",
        "ts" : "Time-Series",
        "sim" : "Simulations",
        "var" : "Variables",
        "freq" : "Frequencies",
        "mod" : "Modes",
        "reg" : "Regions",
        "ye" : "Yearly",
        "3m" : "3-monthly",
        "mo" : "Monthly",
        "se" : "Seasonal Cycle",
        # next entries should be derived from regions_file and reg_ts
        "g" : "Global Land",
        "n" : "Northern Land",
        "t" : "Tropical Land",
        "s" : "Southern Land",
        "amnbo" : "Boreal North America",
        "amnte" : "Temperate North America",
        "amstr" : "Tropical South America",
        "amste" : "Temperate South America",
        "eu" : "Europe",
        "asbo" : "Boreal Asia",
        "aste" : "Temperate Asia",
        "astr" : "Tropical Asia",
        "afn" : "North Africa",
        "afs" : "South Africa",
        "auzea" : "Australia & New Zealand",
    }
    for category in variables_setup : labels[category] = category
    for category in variables_setup :
        for variable in variables_setup[category]['variables']:
            labels[variable] = variables_specifics[variable]["longname"]
    page += plist("labels", labels, crlf=True)

    page += '</script>\n<script src="mapper.js"></script>\n'
    page += '<link rel="stylesheet" href="mapper.css">\n'
    page += '\n</head>\n\n<body onload="makeInterf(); makeTable();">\n'
    page += '<h1>%s</h1>\n'%title
    page += '<div id="interf"></div>\n<div id="table"></div>\n'
    page += '<div id="overlay"><img id="zoomedImage" src=""></div>\n'
    page += '</body>\n</html>\n'

    return page
