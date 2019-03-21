import pymongo
import pandas


def SelectFromDictionnary(df,Keys):
    # -- First, separate the 'normal' keys and the dictionnaries
    df1 = df
    RegularKeys=[]
    DictionnaryKeys=[]
    if len(Keys.keys())!=0:
        for K in Keys.keys():
            if K not in df1.keys():
                DictionnaryKeys.append(K)
            else:
                RegularKeys.append(K)
        import pandas
        for K in RegularKeys:
            print K
            df1 = df1[df1[K].str.match(Keys[K])]
        if len(DictionnaryKeys) != 0:
            for K in DictionnaryKeys:
                df2 = df
                for LK in Keys[K].keys():
                    df2 = df2[df2[LK].str.match(Keys[K][LK])]
            newdf = pandas.concat([df1,df2])
        else:
            newdf = df1
    else:
        newdf = df1
    return newdf



def GPMultiRegions(df,
                   MetricName='rms_xy', 
                   seas = ['djf','mam','jja','son'],
                   Regions=None,
                   removePattern = None,
                   NumexpSelection={}, NumexpExclusion={}, RefSelection={}, RefExclusion={},
                   Columns=['Metric','Region','Seas','variable'],
                   Index=['simulationActivity','simulationInstitute','simulationModel','simulationExperiment',
                          'simulationName','simulationPeriod','simulationLogin'],
                   displayTestOnly=True, SortBy=None,
                   Normalization=None, ByColumnsOrRows='Columns' , MaxValue=None, ForceAggregation=False):
    

    # -- Selection des regions
    if not Regions:
        Regions=['']
    
    NewKeys=['Metric','Region','Seas','Result']
    
    # From this, we reformat the records
    import numpy as np
    SelectedKeys=[]
    for key in df.keys():
        d=np.array(df[key])[0]
        if isinstance(d,float)==False:
            SelectedKeys.append(key)
    for k in NewKeys:
        SelectedKeys.append(k)
    CustomKeys = SelectedKeys

    # ... and what are the regions available for the different seasons?
    Metrics=[]
    for s in seas:
        for reg in Regions:
            for k in df.keys():
                if MetricName+'_' in k and s in k and reg in k:
                    Metrics.append(k.encode('ascii'))

    if removePattern is not None:
        for m in Metrics:
            if removePattern in m:
                Metrics.remove(m)

    # REFORMAT THE DATAFRAME
    rec={}
    for k in CustomKeys:
        rec[k]=[]

    for Metric in Metrics:
        for m in df[Metric].index:
            dum = str.split(Metric,'_')
            rec['Metric'].append(dum[0]+'_'+dum[1])
            rec['Result'].append(df[Metric][m])
            rec['Region'].append(dum[-1])
            rec['Seas'].append(dum[2])

            for k in CustomKeys:
                if k not in NewKeys:
                    rec[k].append(df[k][m])

    ndf = pandas.DataFrame(data=rec)
    
    # --> From here it is like the GlecklerPlot function
    
    refsimulations = testsimulations = ndf
    
    refsimulations = SelectFromDictionnary(refsimulations,RefSelection)
    for K in RefSelection.keys():
        testsimulations = testsimulations.drop(testsimulations.index[testsimulations[K].str.match(RefSelection[K])])
    for K in RefExclusion.keys():
        refsimulations = refsimulations.drop(refsimulations.index[refsimulations[K].str.match(RefExclusion[K])])
    
    testsimulations = SelectFromDictionnary(testsimulations,NumexpSelection)
    for K in NumexpExclusion.keys():
        testsimulations = testsimulations.drop(testsimulations.index[testsimulations[K].str.match(NumexpExclusion[K])])
    
    Values='Result'
    
    ###### START CHECKING FOR MULTIPLE HITS ###########################################
    # 1/ We get the fields with multiple values
    import numpy as np
    
    allFieldsWithMultipleValues=[]
    for key in ndf.keys():
        d=np.array(ndf[key])[0]
        if len(ndf[key].unique()) > 1:
            if isinstance(d,float)==False:
                allFieldsWithMultipleValues.append(key)
    
    FieldsWithMultipleValues=[]
    Exclude=['simulationInputClimatologyFileCheckSum','simulationTrackingID','referenceFileCheckSum','referenceFilename','simulationInputClimatologyFileName','referenceTrackingDate','simulationCreationDate']
    
    for K in allFieldsWithMultipleValues:
        if K not in Exclude:
            if len(ndf[K].unique())>1:
                FieldsWithMultipleValues.append(K)
    
    WorkingColumns=[]
    WorkingIndex=[]
    
    for K in Columns:
        if K in FieldsWithMultipleValues:
            WorkingColumns.append(K)
    
    for K in Index:
        if K in FieldsWithMultipleValues:
            WorkingIndex.append(K)
    
    NumberOfHits=pandas.pivot_table(ndf, values=Values, 
                                columns=WorkingColumns, 
                                index=WorkingIndex, 
                                aggfunc=np.size)
    
    gtone = NumberOfHits.values[np.where(NumberOfHits.values > 1)]
    
    if len(gtone) and ForceAggregation==False:
        print "### Multiple results by square ; Need to add elements in columns or rows"
        print "Elements available for rows and columns ="
        print FieldsWithMultipleValues
        print ''
        print "### => Tip : Run the MG.plot() function without filling Columns and Index"
        print "###          to have the full description of the rows and columns"
        print ""
        print "Number of results in each square"
        return NumberOfHits
    ###### END CHECKING FOR MULTIPLE HITS #####################################################
    
    
    # -> Table that will be displayed
    score = pandas.pivot_table(testsimulations, values=Values, 
                                columns=WorkingColumns, 
                                index=WorkingIndex, 
                                aggfunc=np.mean)
    
    # -> Reference simulations against which the results will be normalized
    scoreRefSimulations = pandas.pivot_table(refsimulations, values=Values, 
                                columns=WorkingColumns, 
                                index=WorkingIndex, 
                                aggfunc=np.mean)

    #dumscore=score
    
    Normalization='NormByMean'
    if (Normalization=='NormByMean' and ByColumnsOrRows=='Columns'):
            score = 100*((score-scoreRefSimulations.mean(axis=0))/scoreRefSimulations.mean(axis=0))
            scoreRefSimulations = 100*((scoreRefSimulations-scoreRefSimulations.mean(axis=0))/scoreRefSimulations.mean(axis=0))
            print '# --- Display normalized results ; by column ;'
            print '#   -> Centered and normalized by mean'
            print '#   -> The results are represented in %'
            print '#   -> The value 50 means that the metric value is 50% higher'
            print '#      than the average '+MetricName+' of the reference simulations'

    MaxValue = 50
    MinValue = -MaxValue
    
    
    # Maximum value
    print 'MaxValue:',MaxValue
    print 'MinValue:',MinValue
    
    # -- Concatenate the results for the tested numerical experiments and the set of reference simulations
    if len(refsimulations)!=len(df) and displayTestOnly==False:
        score = pandas.concat([score,scoreRefSimulations])
    
    # -- Add a column on the right with the mean of the scores of the whole rows
    score['Mean']=score.mean(axis=1)
    
    # -- Sort the results for a given column...
    if SortBy!=None:
        if SortBy!='Mean':
            if isinstance(SortBy,list)==False:
                SortBy=[SortBy]
            tmp = ['']*(len(WorkingColumns)+1)
            # Name of the metric
            tmp[0]=Values[0]
            # Si on a mis que le nom de la variable mais qu'on a pas precise le reste,
            # on met des valeurs par defaut
            if len(SortBy)==1 and len(WorkingColumns)>1:
                print '== Sorted '+SortBy[0]+' by default:'
                for K in WorkingColumns:
                    #if K=='Metric':
                    #    tmp[(WorkingColumns.index(K)+1)]=SortBy[0]
                    if K=='variable':
                        tmp[(WorkingColumns.index(K)+1)]=SortBy[0]
                    if K=='referenceType':
                        print 'referenceType = default'
                        tmp[(WorkingColumns.index(K)+1)]='default'
                    if K=='maskingRegion':
                        print 'maskingRegion = global'
                        tmp[(WorkingColumns.index(K)+1)]='global'
                    if K=='referenceName':
                        tmp1 = df[ df['variable'].str.match(SortBy[0]) ]
                        tmp2 = tmp1[ tmp1['referenceType'].str.match('default')]
                        tmp[(WorkingColumns.index(K)+1)]=tmp2['referenceName'].unique()[0]
                        print 'referenceName = '+tmp2['referenceName'].unique()[0]
                print 'Follow the keys:', WorkingColumns
                print 'to specify your own sorting'
            else:
                tmp[(WorkingColumns.index('variable')+1):]=SortBy
            
        else:
            tmp=['']*(len(WorkingColumns)+1)
            tmp[0]=SortBy
        Sort=[tuple(tmp)]
        if len(tmp)<(len(WorkingColumns)+1):
            print '### Must pass more elements to SortBy'
            print '### Available keys:', WorkingColumns[WorkingColumns.index('variable'):]
            print '### Tip: run the function without SortBy to see which set of values are available'
            print '### Example: SortBy=["tas","ERA40"]'
            return 'Sort =',Sort
        else:
            print 'Sort by',SortBy
            score = score.sort(columns=Sort)
    
    #score=dumscore
    # --- Display features
    # Make the color palette
    import matplotlib
    
    cdict1 = {'red':  ((0.0, 0.0, 0.0),
                       (0.5, 1.0, 1.0),
                       (1.0, 1.0, 1.0)),
    
             'green': ((0.0, 0.0, 0.0),
                       (0.5, 1.0, 1.0),
                       (1.0, 0.0, 0.0)),
    
             'blue':  ((0.0, 1.0, 1.0),
                       (0.5, 1.0, 1.0),
                       (1.0, 0.0, 0.0))
            }
    
    mycmap = matplotlib.colors.LinearSegmentedColormap('BlueWhiteRed', cdict1)
    norm = matplotlib.colors.Normalize(vmin=MinValue, vmax=MaxValue) # the color maps work for [0, 1]
    
    def cmap2rgb(value):
        c1=mycmap(norm(value))[0:3]
        c2=np.multiply(c1,255)
        return str(tuple(c2.astype(int)))
    
    from bs4 import BeautifulSoup
    
    scorehtmlsoup = BeautifulSoup(score.to_html())
    
    import math
    
    for tag in scorehtmlsoup.findAll('td') :
        v=tag.getText()
        if math.isnan(float(v))==False :
            tag['style'] = "font-family: monospace; font-size:10px; text-align: center; background-color:rgb"+cmap2rgb(float(v))
            tag.string="%+.1f" % float(v)
        else :
            tag['style'] = "background-color:#DDDDDD"
            tag.string=""
    
    for tag in scorehtmlsoup.findAll('th') :
        tag['style'] = "width: 100px;"
    
    # ColorBar
    a = ['<td>'+str(i)+'</td>' for i in np.linspace(MinValue,MaxValue,21)]
    colorbarhtml='''
    <table border="1">
    <tbody>
    <tr>
    ''' + '\n'.join(a) + '''
    </tr>
    </tbody>
    </table>
    '''
    
    colorbarhtmlsoup = BeautifulSoup(colorbarhtml)
    
    for tag in colorbarhtmlsoup.findAll('td') :
        v=tag.getText()
        if math.isnan(float(v))==False:
            tag['style'] = "font-family: monospace; font-size:10px; text-align: center; background-color:rgb"+cmap2rgb(float(v))
            tag.string="%+.2f" % float(v)
        else :
            tag['style'] = "background-color:#DDDDDD"
            tag.string=""
    
    # Display with the colors
    from IPython.display import display, HTML, display_html
    display(HTML(str(colorbarhtmlsoup)))
    display(HTML(str(scorehtmlsoup)))
    display(HTML(str(colorbarhtmlsoup)))




def ConnectionToIPSLMongoDBCollection(CollectionName='lmdz_pcmdi'):
    connection = pymongo.Connection('prodiguer-test-db.private.ipsl.fr', 27017)
    db = connection['metrics']
    print "Available collections:"
    print db.collection_names()

    # Working on collection CollectionName
    c = db[CollectionName]
    print "---"
    print "Working on collection:",CollectionName
    print "%d reccords" %c.count()

    df = pandas.DataFrame.from_records(c.find())
    df = df.convert_objects(convert_numeric=True)
    del df['_id']

    return(df)


def ConnectionToIPSLMongoDBSecured(MongoDatabase='172.20.179.73',
                                   user='external-db-mongo-exploitation',
                                   passwd = 'C0l1br1!',
                                   CollectionName='lmdz_pcmdi', ConvertNoneToString=True):

    uri = 'mongodb://'+user+':'+passwd+'@'+MongoDatabase+'/metrics?authMechanism=MONGODB-CR'
    client = pymongo.MongoClient(uri)

    db = client.metrics
    print "Available collections:"
    print db.collection_names()

    # Working on collection CollectionName
    c = db[CollectionName]
    print "---"
    print "Working on collection:",CollectionName
    print "%d reccords" %c.count()

    df = pandas.DataFrame.from_records(c.find())
    if ConvertNoneToString:
        df2 = df.replace([None],'--')
    else:
        df2 = df
    df = df2.convert_objects(convert_numeric=True)
    del df['_id']

    return(df)



def FirstSelection(df,WhichMetrics={}, WhichNumericalExperiment={}):
    df2 = df
    for K in WhichMetrics.keys():
        df2 = df2[ df2[K].str.match(WhichMetrics[K])]
    for K in WhichNumericalExperiment.keys():
        df2 = df2[ df2[K].str.match(WhichNumericalExperiment[K])]
    print "Nombre d'enregistrements: %d" % (len(df))
    print "Nombre d'enregistrements apres selection: %d" % (len(df2))
    return(df2)








def GlecklerPlot(df,MetricName='rms_xyt', dataType='ann', Region='GLB', displayTestOnly=True, SortBy=None,
    		 NumexpSelection={}, NumexpExclusion={}, RefSelection={}, RefExclusion={},
    		 Columns=['variable','referenceType','referenceName','maskingRegion'],
                 Index=['simulationActivity','simulationInstitute','simulationModel','simulationExperiment',
		        'simulationName','simulationPeriod','simulationLogin'],
    		 Normalization=None, ByColumnsOrRows='Columns' , MaxValue=None, ForceAggregation=False,html_pathandfilename=None,
                ndigits=".2f", cellWidth="100px", displayMeanOverReference=True):
    
    
    import pandas
    
    #testsimulations = pandas.DataFrame(data=df)
    testsimulations = SelectFromDictionnary(pandas.DataFrame(data=df),NumexpSelection)
    for K in NumexpExclusion.keys():
        testsimulations = testsimulations.drop(testsimulations.index[testsimulations[K].str.match(NumexpExclusion[K])])
    if not RefSelection:
        refsimulations = testsimulations
    else:
        refsimulations = SelectFromDictionnary(pandas.DataFrame(data=df),RefSelection)
        #for K in RefSelection.keys():
        #    testsimulations = testsimulations.drop(testsimulations.index[testsimulations[K].str.match(RefSelection[K])])

    for K in RefExclusion.keys():
        refsimulations = refsimulations.drop(refsimulations.index[refsimulations[K].str.match(RefExclusion[K])])
    
    import numpy as np
    
    if (MetricName not in ['rms_xyt','rms_xy','bias_xy','cor_xy','cor_xyt']):
        print '# => MetricName '+MetricName+' not available'
        print '# => Choose among:'
        print '#     - rms_xyt + ann'
        print '#     - rms_xy + ann|djf|mam|jja|son'
        print '#     - bias_xy + ann|djf|mam|jja|son'
        print '#     - cor_xy + djf|mam|jja|son'
        print '#     - cor_xyt + ann'

     
    if (MetricName=='rms_xyt' and dataType!='ann'):
        print 'rms_xyt only available for ann (annual cycle)'
        print 'For '+dataType+' use MetricName="rms_xy"'
        return 1
    
    Values=[MetricName+'_'+dataType+'_'+Region]
    
    ###### START CHECKING FOR MULTIPLE HITS ###########################################
    # 1/ We get the fields with multiple values
    import numpy as np
    
    allFieldsWithMultipleValues=[]
    for key in df.keys():
        d=np.array(df[key])[0]
        if len(df[key].unique()) > 1:
            if isinstance(d,float)==False:
                allFieldsWithMultipleValues.append(key)
    
    FieldsWithMultipleValues=[]
    Exclude=['simulationInputClimatologyFileCheckSum','simulationTrackingID','referenceFileCheckSum','referenceFilename','simulationInputClimatologyFileName','referenceTrackingDate','simulationCreationDate']
    
    for K in allFieldsWithMultipleValues:
        if K not in Exclude:
            if len(df[K].unique())>1:
                FieldsWithMultipleValues.append(K)
    
    WorkingColumns=[]
    WorkingIndex=[]
    
    for K in Columns:
        if K in FieldsWithMultipleValues:
            WorkingColumns.append(K)
    
    for K in Index:
        if K in FieldsWithMultipleValues:
            WorkingIndex.append(K)

    NumberOfHits=pandas.pivot_table(df, values=[MetricName+'_'+dataType+'_'+Region], 
                                columns=WorkingColumns, 
                                index=WorkingIndex, 
                                aggfunc=np.size)
    
    gtone = NumberOfHits.values[np.where(NumberOfHits.values > 1)]
    
    if len(gtone) and ForceAggregation==False:
        print "### Multiple results by square ; Need to add elements in columns or rows"
        print "Elements available for rows and columns ="
        print FieldsWithMultipleValues
        print ''
        print "### => Tip : Run the MG.plot() function without filling Columns and Index"
        print "###          to have the full description of the rows and columns"
        print ""
        print "Number of results in each square"
        return NumberOfHits
    ###### END CHECKING FOR MULTIPLE HITS #####################################################
    
    
    # -> Table that will be displayed
    #score = pandas.pivot_table(df, values=Values,
    score = pandas.pivot_table(testsimulations, values=Values, 
                                columns=WorkingColumns, 
                                index=WorkingIndex, 
                                aggfunc=np.mean)
    
    # -> Reference simulations against which the results will be normalized
    scoreRefSimulations = pandas.pivot_table(refsimulations, values=Values, 
                                columns=WorkingColumns, 
                                index=WorkingIndex, 
                                aggfunc=np.mean)
    
    if (MetricName in ['bias_xy','rms_xy','rms_xyt','cor_xyt','cor_xy','mae_xy']): 
        if (Normalization=='NormByStandardDeviation' and ByColumnsOrRows=='Columns'):
            refscore = scoreRefSimulations.std(axis=0)
            score = (score-scoreRefSimulations.mean(axis=0))/refscore
            scoreRefSimulations = (scoreRefSimulations-scoreRefSimulations.mean(axis=0))/scoreRefSimulations.std(axis=0)
            print '# --- Display normalized results ; by column ;'
            print '#   -> Centered and normalized by standard deviation'
            print '#   -> The results are represented in *std'
            print '#   -> The value 2 means that the metric value is 50% higher'
            print '#      than the average '+MetricName+' of the reference simulations'
            if MaxValue==None:
                MaxValue = 3
            MinValue = -MaxValue
        
        if (Normalization=='NormByMean' and ByColumnsOrRows=='Columns'):
            refscore = scoreRefSimulations.mean(axis=0)
            score = 100*((score-scoreRefSimulations.mean(axis=0))/refscore)
            scoreRefSimulations = 100*((scoreRefSimulations-scoreRefSimulations.mean(axis=0))/scoreRefSimulations.mean(axis=0))
            print '# --- Display normalized results ; by column ;'
            print '#   -> Centered and normalized by mean'
            print '#   -> The results are represented in %'
            print '#   -> The value 50 means that the metric value is 50% higher'
            print '#      than the average '+MetricName+' of the reference simulations'
            if MaxValue==None:
                MaxValue = 50
            MinValue = -MaxValue
    
    # -- Concatenate the results for the tested numerical experiments and the set of reference simulations
    if len(refsimulations)!=len(df) and displayTestOnly==False:
        score = pandas.concat([score,scoreRefSimulations])
    
    # -- Add a column on the right with the mean of the scores of the whole rows
    score['Mean']=score.mean(axis=1)
    
    # -- Sort the results for a given column...
    if SortBy!=None:
        if SortBy!='Mean':
            if isinstance(SortBy,list)==False:
                SortBy=[SortBy]
            tmp = ['']*(len(WorkingColumns)+1)
            # Name of the metric
            tmp[0]=Values[0]
            # Si on a mis que le nom de la variable mais qu'on a pas precise le reste,
            # on met des valeurs par defaut
            if len(SortBy)==1 and len(WorkingColumns)>1:
                print '== Sorted '+SortBy[0]+' by default:'
                for K in WorkingColumns:
                    if K=='variable':
                        tmp[(WorkingColumns.index(K)+1)]=SortBy[0]
                    if K=='referenceType':
                        print 'referenceType = default'
                        tmp[(WorkingColumns.index(K)+1)]='default'
                    if K=='maskingRegion':
                        print 'maskingRegion = global'
                        tmp[(WorkingColumns.index(K)+1)]='global'
                    if K=='referenceName':
                        tmp1 = df[ df['variable'].str.match(SortBy[0]) ]
                        tmp2 = tmp1[ tmp1['referenceType'].str.match('default')]
                        tmp[(WorkingColumns.index(K)+1)]=tmp2['referenceName'].unique()[0]
                        print 'referenceName = '+tmp2['referenceName'].unique()[0]
                print 'Follow the keys:', WorkingColumns
                print 'to specify your own sorting'
            else:
                tmp[(WorkingColumns.index('variable')+1):]=SortBy
            
        else:
            tmp=['']*(len(WorkingColumns)+1)
            tmp[0]=SortBy
        Sort=[tuple(tmp)]
        if len(tmp)<(len(WorkingColumns)+1):
            print '### Must pass more elements to SortBy'
            print '### Available keys:', WorkingColumns[WorkingColumns.index('variable'):]
            print '### Tip: run the function without SortBy to see which set of values are available'
            print '### Example: SortBy=["tas","ERA40"]'
            return 'Sort =',Sort
        else:
            print 'Sort by',SortBy
            score = score.sort(columns=Sort)
    
    from bs4 import BeautifulSoup

    # -- Add the values of the reference
    #if Normalization:
    #tmprefscore = refscore.to_frame().transpose()
    #refscorehtmlsoup = BeautifulSoup(tmprefscore.to_html())
    scorehtmlsoup = BeautifulSoup(score.to_html())
    import math
    nd="%+"+ndigits

    for tag in scorehtmlsoup.findAll('td') :
        v=tag.getText()
        if v=='Na':
           tag['style'] = "background-color:#DDDDDD"
           tag.string=""
        else:
           if math.isnan(float(v))==False :
              tag['style'] = "font-family: monospace; font-size:10px; text-align: center"
              tag.string=nd % float(v)
              #tag.string="%+.5f" % float(v)
           else :
              tag['style'] = "background-color:#DDDDDD"
              tag.string=""


    if Normalization:
        tmprefscore = refscore.to_frame().transpose()
        refscorehtmlsoup = BeautifulSoup(tmprefscore.to_html())
        #
        # --- Display features
        # Make the color palette
        import matplotlib

        cdict1 = {'red':  ((0.0, 0.0, 0.0),
                           (0.5, 1.0, 1.0),
                           (1.0, 1.0, 1.0)),

                 'green': ((0.0, 0.0, 0.0),
                           (0.5, 1.0, 1.0),
                           (1.0, 0.0, 0.0)),

                 'blue':  ((0.0, 1.0, 1.0),
                           (0.5, 1.0, 1.0),
                           (1.0, 0.0, 0.0))
                }
        cdict2 = {'red':  ((0.0, 1.0, 1.0),
                           (0.5, 1.0, 1.0),
                           (1.0, 0.0, 0.0)),

                 'green': ((0.0, 0.0, 0.0),
                           (0.5, 1.0, 1.0),
                           (1.0, 0.0, 0.0)),

                 'blue':  ((0.0, 0.0, 0.0),
                           (0.5, 1.0, 1.0),
                           (1.0, 1.0, 1.0))
                }

        #
        if 'cor' in MetricName: 
            mycmap = matplotlib.colors.LinearSegmentedColormap('RedWhiteBlue', cdict2)
        else:
            mycmap = matplotlib.colors.LinearSegmentedColormap('BlueWhiteRed', cdict1)

        norm = matplotlib.colors.Normalize(vmin=MinValue, vmax=MaxValue) # the color maps work for [0, 1]

        def cmap2rgb(value):
            c1=mycmap(norm(value))[0:3]
            c2=np.multiply(c1,255)
            return str(tuple(c2.astype(int)))

        scorehtmlsoup = BeautifulSoup(score.to_html())
        

        for tag in scorehtmlsoup.findAll('td') :
            v=tag.getText()
            if math.isnan(float(v))==False :
                tag['style'] = "font-family: monospace; font-size:10px; text-align: center; background-color:rgb"+cmap2rgb(float(v))
                tag.string=nd % float(v)
                #tag.string="%+"+ndigits % float(v)
            else :
                tag['style'] = "background-color:#DDDDDD"
                tag.string=""

        for tag in scorehtmlsoup.findAll('th') :
            tag['style'] = "width: "+cellWidth+";"

        # ColorBar
        a = ['<td>'+str(i)+'</td>' for i in np.linspace(MinValue,MaxValue,21)]
        colorbarhtml='''
        <table border="1">
        <tbody>
        <tr>
        ''' + '\n'.join(a) + '''
        </tr>
        </tbody>
        </table>
        '''

        colorbarhtmlsoup = BeautifulSoup(colorbarhtml)

        for tag in colorbarhtmlsoup.findAll('td') :
            v=tag.getText()
            if math.isnan(float(v))==False:
                tag['style'] = "font-family: monospace; font-size:10px; text-align: center; background-color:rgb"+cmap2rgb(float(v))
                #tag.string="%+.2f" % float(v)
                tag.string=nd % float(v)
            else :
                tag['style'] = "background-color:#DDDDDD"
                tag.string=""
        # End if Normalization==None
        #
        textrefscore='Mean values over the reference simulations of the statistics (used to normalize per column)'
        # Display with the colors
        if html_pathandfilename:
            #return scorehtmlsoup
            Html_file= open(html_pathandfilename,"w")
            Html_file.write(str(scorehtmlsoup)+'\
                            <br/>\
                            '+str(colorbarhtmlsoup))
            #Html_file.write(str(scorehtmlsoup)+'\
            #                <br/>\
            #                '+str(colorbarhtmlsoup))
            if displayMeanOverReference:
               Html_file.write(str('<br/>'))
               Html_file.write(textrefscore)
               Html_file.write(str(refscorehtmlsoup))
            Html_file.close()
        else:
            from IPython.display import display, HTML, display_html
            display(HTML(str(colorbarhtmlsoup)))
            display(HTML(str(scorehtmlsoup)))
            display(HTML(str(colorbarhtmlsoup)))
            if displayMeanOverReference:
               display(HTML(' '))
               display(HTML(textrefscore))
               display(HTML(str(refscorehtmlsoup)))
    else:
        textrefscore='Mean values over the reference simulations of the statistics (used to normalize per column)'
        # if Normalization == None
        if html_pathandfilename:
            #return scorehtmlsoup
            Html_file= open(html_pathandfilename,"w")
            Html_file.write(str(scorehtmlsoup))
            if displayMeanOverReference:
               Html_file.write(' ')
               #Html_file.write(textrefscore)
               #Html_file.write(str(refscorehtmlsoup))
            Html_file.close()
        else:
            from IPython.display import display, HTML, display_html
            display(HTML(str(scorehtmlsoup)))
            if displayMeanOverReference:
               display(HTML(' '))
               #display(HTML(textrefscore))
               #display(HTML(str(refscorehtmlsoup)))

        



