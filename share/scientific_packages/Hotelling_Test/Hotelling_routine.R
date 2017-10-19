
# ---------------------------------------------------------------------------------------------------------- #
# -- Ce script fait un test de Hotelling entre un ensemble de jeux de donnees de reference
# -- et une simulation, sur une zone pre-definie.
# -- Le test de Hotelling en pratique necessite de:
# --      - estimer un espace d'EOFs commun a la reference et au modele que l'on veut tester;
# --        pour une definition optimale de cet espace (pour qu'il explique le plus de variance possible
# --        du modele et de la ref), on va estimer une matrice de covariance commune a la ref et au modele ;
# --        si, par facilite , on estimait une matrice de covariance commune avec la moyenne des modeles
# --        et pas pour chaque modele, on perdra de la variance et le test ne sera pas optimal.
# --      - dans cet espace d'EOFs de la matrice de covariance commune, on projette le modele et la moyenne
# --        des refs sur les neof; on projette egalement chaque ref individuelle pour estimer la matrice de
# --        covariance d'erreurs S ; tous les champs projetes sur les neof EOF communes sont mis sous la
# --        forme suivante: les neof PCs sont mises les unes a la suite des autres pour former un vecteur,
# --        de longueur neof*12. La matrice de covariance d'erreur est donc de dimension n.indiv.ref/neof*12
# --      - La matrice de covariance d'erreur n'est pas inversible en l'etat. Pour l'inverser, on calcule
# --        ses EOFs; on inversera la matrice diagonale de valeurs propres, et on projettera les champs (deja
# --        projettes dans l'espace des EOFs communes) dans l'espace de ces EOFs de la matrice de covariance
# --        d'erreur. La figure Variance-explained-by-error-covariance-matrix.pdf montre comment les
# --        differents modeles et la moyenne des Refs se projettent dans ces EOFs.
# --      - On estime le parametre nu de la distribution de Fisher pour estimer la significativite du test
# --        a l'aide de la formule de Yao (1965)
# --      - on estime T2, son intervalle de confiance, ainsi que Ts2 (voir Braconnot & Frankignoul 1992)
# --        La figure Hotelling-test-IPSL-models-vs-REF-mean-*.pdf resume les resultats du test. 
# -- 
# ---------------------------------------------------------------------------------------------------------- #

Test=testname
nref=length(REFFIELDS)
ntest=length(TESTFIELDS)

# ---------------------------------------------------------------------------------------------------------- #
# -- Preliminaire 1
# -- On impoTest=testnamese le nombre d'EOFs (neof) de la matrice de covariance commune que l'on veut garder =>
# -- => cf le script d'etude de la matrice de covariance commune et les deux figures produites:
# --    - le script: Common-covariance-matrix-study.R
# --    - les figures: Explained-variance-indivmodel-vs-CCM-modelmean.pdf et Explained-variance-indivmodel-vs-CCM-indivmodels.pdf
# -- neof1 et neof2 sont les nombres d'EOFs des matrices de covariance commune de la 1ere et 2nd reduction

    if (variable == "ts"){ neof1=2 ; neof2=2 }
    if (variable == "hfls"){ neof1=3 ; neof2=3 }
    if (variable == "hfss"){ neof1=2 ; neof2=2 }
    if (variable == "tauu"){ neof1=2 ; neof2=2 }
    if (variable == "tauv"){ neof1=2 ; neof2=2 }
    if (variable == "wind10m"){ neof1=2 ; neof2=2 }
    if (variable == "q2m"){ neof1=2 ; neof2=2 }
    if (variable == "deltaT2m"){ neof1=2 ; neof2=2 }

    do_figures_common_eof=TRUE
    weighting=TRUE


    # -- Test and Ref are the names of the simulations to be tested and the reference used
    TestPeriod=InputTest[[Test]]$period
    #RefPeriod=InputRef[[Ref]]$period
    experiment=InputTest[[Test]]$Experiment

# ---------------------------------------------------------------------------------------------------------- #
# -- Preliminaire 2
# -- On va declarer une liste Hotelling dans laquelle on va stocker les resultats des analyses

    # -- 7.1/ On declare la liste Hotelling 
    Hotelling=list()



# ---------------------------------------------------------------------------------------------------------- #
# -- !!! Debut du test !!! 
# -- On commence par faire une boucle sur les differentes versions de modele,
# -- on recupere le champ du modele sur la zone d'etude, on calcule ses anomalies et on le pondere.
    if (weighting==TRUE){dumweights=weights}else{dumweights=(weights*0)+1}


# ---------------------------------------------------------------------------------------------------------- #
# -- 1/ Calcul de la matrice de covariance commune model - ref

     # -- 1.1/ Matrice de covariance CMM du modele
     # - Ponderation des anomalies
     Manom=t(t(WMeanTest)-apply(WMeanTest,2,mean)) # -- Manom  = anomalies de la moyenne du modele
     WManom=t(t(Manom)*sqrt(dumweights))  # -- WManom = anomalies ponderees
     CMM=(t(WManom)%*%WManom)/(nrow(WManom)-1)  # -- CMM = matrice de covariance du modele

     # -- 1.2/ Matrice de covariance CMR de la moyenne des references
     # - Ponderation des anomalies
     Ranom=t(t(WMeanRef)-apply(WMeanRef,2,mean)) # -- Ranom = anomalies de la ref (deja calculees dans Common-EOF-analysis.R)
     WRanom=t(t(Ranom)*sqrt(dumweights)) # -- anomalies ponderees
     CMR=(t(WRanom)%*%WRanom)/(nrow(WRanom)-1) # -- CMR = matrice de covariance de la moyenne des ref

     # -- Somme des matrices de covariance du modele et des obs (CCM, pour Common Covariance Matrix)
     library(psych)
     if (CommonSpace == "CCM"){ CCM=CMM/tr(CMM) + CMR/tr(CMR) }
     if (CommonSpace == "CMR"){ CCM=CMR/tr(CMR) }

# ---------------------------------------------------------------------------------------------------------- #
# -- 2/ Calcul des EOFs communes sur la matrice de covariance commune CCM

     # -- Decomposition valeurs/vecteurs propres
     print("Processing eigen vectors first reduction")
     eig=eigen(CCM)
     print("Done")

     C_eofs1=eig$vectors[,1:neof1]
     C_lambda=eig$values[1:neof1]



# ---------------------------------------------------------------------------------------------------------- #
# -- 2.bis/ Calcul des % de variance de la moyenne des ref et du modele
# --        explique par les EOFs communes:
# --             - la diagonale de la matrice egale a: t(C_eofs) %*% CMM %*% C_eofs contient la projection
# --               de CMM sur les C_eofs, autrement dit la variance expliquee par les C_eofs;
# --             - si on veut le % de la variance du modele explique par les C_eofs, on normalise par la
# --               trace de CMM, soit la variance du modele.

     tmpeof=eig$vectors[,1:20]
     ExpVar_Model=100*diag(t(tmpeof)%*%CMM%*%tmpeof)/tr(CMM)
     ExpVar_RefMean=100*diag(t(tmpeof)%*%CMR%*%tmpeof)/tr(CMR)


# ---------------------------------------------------------------------------------------------------------- #
# -- On a maintenant les EOFs communes. Elles nous fournissent l'espace dans lequel on va pouvoir estimer
# -- la matrice de covariance d'erreurs (S) pour le test de Hotelling.
# -- Le nombre d'EOFs communes que nous avons choisi nous donne le nombre de dof spatiaux pour le test.
# ---------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------------------------------------------------------- #
# -- 3/ On va estimer la matrice de covariance d'erreur D des observations (references).
# -- Les erreurs sont les ecarts entre chaque reference individuelle et la moyenne des references.
# -- Methodo:
# --     - on projette les champs BRUTS ponderes sur les EOFs communes
# --     - pour la moyenne des references et pour les references individuelles
# --     - et on calcule les ecarts comme la difference entre les references individuelles et la moy. des ref
# --     - La projection d'une ref sur les EOFs communes donne une matrice (ntime,neof), avec ntime le
# --       nombre de pas de temps (12 si c'est un cycle saisonnier). Les colonnes sont en fait les PCs des
# --       refs individuelles dans l'espace des EOFs communes.
# --     - Pour calculer la matrice de covariance d'erreur, on fait une boucle sur les ref;
# --       et on accumule en lignes les ref individuelles projettees sur les EOFs communes, que l'on
# --       aura prealablement transformes en vecteurs.
# --       On obtient une matrice indiv.errors (nref,ntime*neof) d'erreurs, a partir de laquelle on pourra  
# --       calculer la matrice de covariance d'erreur.


     # -- 3.1/ On projette la moyenne des ref sur les EOFs communes, apres ponderation de la moyenne
     P1.Ref=WRanom%*%C_eofs1

     # -- 3.1/ On projette la moyenne des ref sur les EOFs communes, apres ponderation de la moyenne
     P1.Test=WManom%*%C_eofs1

     # -- Deuxieme reduction (EOFs/PCs)
     # -- On calcule  
     CMR2 = (P1.Ref%*%t(P1.Ref))/(nrow(P1.Ref)-1)
     CMM2 = (P1.Test%*%t(P1.Test))/(nrow(P1.Test)-1)

     # -- Deuxieme matrice de covariance commune
     if (CommonSpace == "CCM"){ CCM2 = CMR2/tr(CMR2) + CMM2/tr(CMM2) }
     if (CommonSpace == "CMR"){ CCM2 = CMR2/tr(CMR2) }

     # -- Deuxiemes EOFs communes
     eig2=eigen(CCM2)


     # -- Combien d'EOFs conserve-t-on?
     C_lambda2=eig2$values[1:neof2]
     C_eofs2=eig2$vectors[,1:neof2]

     # -- Deuxieme projection de la ref et de la simulation sur les EOFs communes 2
     PP2.Ref=t(P1.Ref)%*%C_eofs2
     PP2.Test=t(P1.Test)%*%C_eofs2
     P2.Ref=PP2.Ref ; P2.Test=PP2.Test
     # --> On garde PP2.Ref et PP2.Test avec les EOFs en colonnes (pour faire les figures ; voir scripts/Fig-common-EOFS-Second-reduction.R)


     dim(P2.Ref)=dim(P2.Test)=NULL

     tmpeof2=eig2$vectors
     ExpVar_Model2=100*diag(t(tmpeof2)%*%CMM2%*%tmpeof2)/tr(CMM)
     ExpVar_Ref2=100*diag(t(tmpeof2)%*%CMR2%*%tmpeof2)/tr(CMR)
     #EXPVARModel=c(EXPVARModel,sum(ExpVar_Model2))
     #EXPVARRefMean=c(EXPVARRefMean,sum(ExpVar_Ref2))

     # -- 3.2/ On va maintenant faire une boucle sur les refs, a l'interieur de laquelle on
     # -- projetera les Ref individuelles (champs bruts, pas les anomalies) ponderees sur les EOFS communes.
     # -- On initialise l'objet indiv.errors qui va recevoir les erreurs associees a chaque ref individuelles
     # -- en ligne.

     indiv.ref.errors=c()

     indiv.ref.proj=list()
     indiv.ref.proj2=list()
     # -- Boucle sur les ref.
     for (refnames in names(REFFIELDS)){

        print(refnames)

        # -- On recupere le jeu de ref individuel refnames, sur la zone w.indices
        dumdat=REFFIELDS[[refnames]]$wdat
	####plot = test.plot ; plot$dat[NoNA] = apply(dumdat,2,mean) ; quickmap2(plot)
        dumdat=t(t(dumdat)-apply(dumdat,2,mean))
        Wdumdat=t(t(dumdat)*sqrt(dumweights))

        # -- Pour obtenir les PC, on projette le champ brut pondere sur les EOFs communes
        proj=Wdumdat%*%C_eofs1
        proj2=t(proj)%*%C_eofs2
        CMIR=(t(Wdumdat)%*%Wdumdat)/(nrow(Wdumdat)-1) # -- CMR = matrice de covariance de la moyenne des ref
        CMIR2 = (proj%*%t(proj))/(nrow(proj)-1)
        ExpVar_RefIndiv2=100*diag(t(C_eofs2)%*%CMIR2%*%C_eofs2)/tr(CMIR)
        #EXPVARRefIndiv=c(EXPVARRefIndiv,sum(ExpVar_RefIndiv2))

        indiv.ref.proj[[refnames]]=proj
	indiv.ref.proj2[[refnames]]=proj2

        # -- On calcule l'ecart a la moyenne des refs
        dim(proj2)=NULL
        dum.error=proj2-P2.Ref
	
        # -- On rajoute les erreurs comme une ligne supplementaire a indiv.errors
        indiv.ref.errors=rbind(indiv.ref.errors,dum.error)

     }#end for refnames




     # -- 3.3/ On va maintenant faire une boucle sur les fichiers tests individuels, a l'interieur de laquelle on
     # -- projetera les tests individuels (champs bruts, pas les anomalies) sur les EOFS communes.
     # -- On initialise l'objet indiv.test.errors qui va recevoir les erreurs associees a chaque test individuel
     # -- en ligne.


     indiv.test.errors=c()

     indiv.test.proj=list()
     indiv.test.proj2=list()
     
     # -- Boucle sur les test.
     for (testnames in names(TESTFIELDS)){

        print(testnames)

        # -- On recupere le jeu de test individuel testnames, sur la zone w.indices
        dumdat=TESTFIELDS[[testnames]]$wdat
        dumdat=t(t(dumdat)-apply(dumdat,2,mean))
        Wdumdat=t(t(dumdat)*sqrt(dumweights))

        # -- Pour obtenir les PC, on projette le champ brut pondere sur les EOFs communes
        proj=Wdumdat%*%C_eofs1
        proj2=t(proj)%*%C_eofs2

        indiv.test.proj[[testnames]]=proj
        indiv.test.proj2[[testnames]]=proj2

        dim(proj2)=NULL

        # -- On calcule l'ecart a la moyenne des tests
        dum.error=proj2-P2.Test

        # -- On rajoute les erreurs comme une ligne supplementaire a indiv.errors
        indiv.test.errors=rbind(indiv.test.errors,dum.error)

     }#end for testnames




if (do_figures_common_eof==TRUE){

     # !!! Inserer le nom du modele!!!
# ---------------------------------------------------------------------------------------------------------- #
# -- Intermediaire/ On fait la figure des 5 premieres EOF communes (premiere reduction = cartes)
     print("Do figure common EOFs 1st reduction")
     source(paste(main_dir,"scripts/Fig-common-EOFS-First-reduction.R",sep="/"))
     # Output = paste(hotelling_outputdir,'CEOFs_plots/',sep='')
# ---------------------------------------------------------------------------------------------------------- #
# -- Intermediaire/ On fait la figure de la variance entre les EOFs des ref individuelles
     #print("Do figure variance among EOFs of the individual ref")
     #source(paste(main_dir,"scripts/Fig-variance-among-indiv-REF-intrinsicEOFS.R",sep="/"))

# ---------------------------------------------------------------------------------------------------------- #
# -- Intermediaire/ On fait la figure des EOF de la deuxieme reduction (EOF=temporal)
     #print("Do figure common EOFs 2nd reduction")
     #source(paste(main_dir,"scripts/Fig-common-EOFS-Second-reduction.R",sep="/"))
}







# ---------------------------------------------------------------------------------------------------------- #
# -- 4/ On va maintenant estimer la matrice de covariance d'erreur D des observations (references).
     D=(t(indiv.ref.errors)%*%indiv.ref.errors)/(nrow(indiv.ref.errors)-1)

# ---------------------------------------------------------------------------------------------------------- #
# -- 5/ Puis, on estime la matrice de covariance d'erreur du modele ;
# --    Si on a une seule realisation, on considere qu'on ne connait pas la matrice de covariance
# --    d'erreur du modele, et qu'on ne peut pas l'estimer. Dans ce cas, M = 0
     if (ntest>1){
     M=(t(indiv.test.errors)%*%indiv.test.errors)/(nrow(indiv.test.errors)-1)
     }else{
     M=D*0
     }#end


# ---------------------------------------------------------------------------------------------------------- #
# -- 6/ La matrice de covariance d'erreur S est la somme de D et M
     S = D + M

# ---------------------------------------------------------------------------------------------------------- #
# -- 6/ Calcul de l'inverse de S
     inv_S=solve(S)

# ---------------------------------------------------------------------------------------------------------- #
# -- 7/ Calcul de la statistique T2 de Hotelling
# -- Etant donne que la matrice de covariance d'erreur n'est inversible que dans l'espace de ses EOFs,
# -- on va estimer les differences de moyenne (model - ref_mean) dans l'espace de ces EOFs

         print("Start Hotelling test")
         # -- On calcule la difference entre le modele et la moyenne des ref
         diff=P2.Test-P2.Ref
         dim(diff)=c(length(diff),1)
         
	 # -- Estimation de la statistique T2
	 dumT2 = t(diff) %*% inv_S %*% diff
	 print("T2")
	 print(dumT2)

         # -- Premier parametre de la loi F = mu (K dans Wilks)=> Nombre de dof totaux = mu = neof1*neof2
	 mu=neof1*neof2
         print(paste("mu =",mu))
	 # -- Deuxieme parametre de la loi F = nu (n-1 dans Wilks)
	 # -- nu estime d'apres Yao (1965)
	 n=nrow(indiv.ref.errors)
	 if (ntest>1){ MM = M }else{ MM = S }
         nu = 1 / ( (1/(n-1)) * ( ( t(diff) %*%  inv_S %*% (MM/nrow(indiv.ref.errors)) %*% inv_S %*% diff ) / dumT2 )^2 )
         print(paste("nu =",nu))

         # -- L'hypothese nulle du test de Hotelling est rejetee au niveau de significativite alpha 
	 # -- si T2 > [(nu-mu+1)/(mu*nu)] * F(1-alpha) , avec F = F(mu,nu-mu+1)
	 # -- On va donc chercher le quantile de F qui correspond a la valeur de T2:
	 # -- F(1-alpha) = T2 * [(mu*nu)/(nu-mu+1)]
	 Fvalue = dumT2 * ((mu*nu)/(nu-mu+1))
         probFvalue=pf(Fvalue,mu,nu-mu+1)
	 p_value=1-probFvalue

	 # -- T2 suit une loi de chi2, a mu degres de liberte et parametre de non-centralite L (T2 etant le meilleur estimateur de L)
	 # -- On estime l'intervalle de confiance a 95% de T2, on estime les quantiles 2.5 et 97.5 de T2
	 T2_conf_int=qchisq(c(0.025,0.975),mu,ncp=dumT2)

         # -- Valeur critique de T2 a 95% et a 99%
	 T2_crit_95_chisq=qchisq(0.95,mu)
	 T2_crit_99_chisq=qchisq(0.99,mu)
         T2_crit_95_F=(mu*nu/(nu-mu+1))*qf(0.95,mu,nu-mu+1)
	 T2_crit_99_F=(mu*nu/(nu-mu+1))*qf(0.99,mu,nu-mu+1)


         # -- Intervalle de confiance de T2 
	 # -- T2 suit une loi de chi2, a mu degres de liberte et parametre de non-centralite L (T2 etant le meilleur estimateur de L)
	 # -- Cette loi a pour moyenne mu+L, et variance 2(mu+2L)
	 # -- Soit V = (chi2_mu(L) - (L+mu)) / sqrt(2(mu+2L)) ; V suit une loi normale unitaire (moyenne 0, variance unitaire)
         # -- Suivant cela, la variable Ts2 = T2 / sqrt(2(mu+2L)) suit une loi ~ chi2_mu(L)/sqrt(2(mu+2L)),
	 # -- equivalente a une loi normale de moyenne mu+L/sqrt(2(mu+2L)), et de variance unitaire.
	 # -- L'intervalle de confiance a 95% de la statistique Ts2 est donc donne par [(Ts2-1.96*1);(Ts2+1.96*1)]
         # -- Test
	 varT2 = 2 * ( mu + 2*dumT2 )
	 Ts2 = dumT2 / sqrt(varT2)
	 print(paste("Ts2 =",Ts2))
	 Ts2_conf_int = Ts2 + ( c(-1.96,1.96) )

         print("Hotelling Done")


         # -- Stockage des resultats
         Hotelling$description=list()
         #Hotelling$C_EOFS=list("C_EOF1"=list(),"C_EOF2"=list())
         Hotelling$hotelling_res=list("T2"=list(),"Ts2"=list())

         # -- Description du test qui va etre fait: nom de la simulation, variable, neof1, neof2
         Hotelling$description$TestName=Test
         Hotelling$description$variable=variable
         Hotelling$description$neof1=neof1
         Hotelling$description$neof2=neof2
         Hotelling$description$TestPeriod=TestPeriod
	 Hotelling$description$Activity=InputTest[[Test]]$Activity
	 Hotelling$description$experiment=InputTest[[Test]]$Experiment
	 Hotelling$description$simulation=InputTest[[Test]]$SimName
	 Hotelling$description$nref=nref
	 Hotelling$description$ntest=ntest
	 Hotelling$description$CommonSpace=CommonSpace


         # -- Stockage des resultats
         #Hotelling$C_EOFS$C_EOF1$eofs=C_eofs1
         #Hotelling$C_EOFS$C_EOF1$expvar_model=ExpVar_Model
         #Hotelling$C_EOFS$C_EOF1$expvar_refmean=ExpVar_RefMean
         #Hotelling$C_EOFS$C_EOF1$P1.Ref=P1.Ref
         #Hotelling$C_EOFS$C_EOF1$P1.Test=P1.Test

         #Hotelling$C_EOFS$C_EOF2$eofs=C_eofs2

         #Hotelling$C_EOFS$C_EOF2$P2.Ref=P2.Ref
         #Hotelling$C_EOFS$C_EOF2$P2.Test=P2.Test

         #Hotelling$C_EOFS$C_EOF2$expvar_model=ExpVar_Model2
         #Hotelling$C_EOFS$C_EOF2$expvar_refmean=ExpVar_Ref2

         Hotelling$hotelling_res$explvar.model.neof1=sum(ExpVar_Model[1:neof1])
	 Hotelling$hotelling_res$explvar.model.neof2=sum(ExpVar_Model2[1:neof2])
	 Hotelling$hotelling_res$explvar.refmean.neof1=sum(ExpVar_RefMean[1:neof1])
	 Hotelling$hotelling_res$explvar.refmean.neof2=sum(ExpVar_Ref2[1:neof2])
         Hotelling$hotelling_res$S=S
         Hotelling$hotelling_res$inv_S=inv_S
         Hotelling$hotelling_res$diff=diff
         Hotelling$hotelling_res$T2$statistic=dumT2
         Hotelling$hotelling_res$T2$mu=mu
	 Hotelling$hotelling_res$T2$nu=nu
	 Hotelling$hotelling_res$T2$p_value=p_value
	 Hotelling$hotelling_res$T2$conf_int=T2_conf_int
         Hotelling$hotelling_res$T2$threshold_95=T2_crit_95_F
	 Hotelling$hotelling_res$T2$threshold_99=T2_crit_99_F
         Hotelling$hotelling_res$Ts2$statistic=Ts2
         Hotelling$hotelling_res$Ts2$conf_int=Ts2_conf_int
         Hotelling$hotelling_res$Ts2$threshold_95=T2_crit_95_F/sqrt(varT2)
         Hotelling$hotelling_res$Ts2$threshold_99=T2_crit_99_F/sqrt(varT2)
	 Hotelling$hotelling_res$files=InputTest[[Test]]$files


# -- On a finit le test de Hotelling pour "Test" (dans la liste InputTest definie dans InputTest.R)
# ---------------------------------------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------------------------------------- #
# -- 8/ Sauvegarde des resultats

# -- 8.2/ Le fichier qu'on va charger, avec les resultats des precedents calculs (avec d'autres modeles, d'autres variables...)
# --      contient un objet "Hotelling" => on mets donc les resultats que l'on vient de calculer dans un objet TMP
# --      (car l'objet Hotelling sera ecrase au chargement du fichier "all results".
library(rjson)
# -- Creation du repertoire d'output si il n'existe pas
if ('output_res_hotelling_json_file' %in% names(InputTest[[Test]])){
  results_file = InputTest[[Test]]$output_res_hotelling_json_file
}else{
  results_file=paste(hotelling_outputdir,"results_json_files/Res-Hotelling_",InputTest[[Test]]$dataset_name_in_filename,"-",variable,".json",sep="")
}#
# -- Get the path to create it if necessary
dum = strsplit(results_file,'/')[[1]]
results_outdir = dum[1]
for (elt in dum[2:(length(dum)-1)]){results_outdir=paste(results_outdir,elt,sep='/')}
print(results_outdir)
dir.create(results_outdir,showWarnings=FALSE)

# -- Save the file
print(paste("==> Saving",results_file))
write(toJSON(Hotelling), file=results_file)
print(paste("==> Hotelling test done for",testname,variable))
