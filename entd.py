# streamlit run test.py # en se plaçant dans le répertoire contenant test.py en ligne de commande.
# https://docs.streamlit.io/

import streamlit as st
import pandas as pd
import pandas as pd
import numpy as np
#pd.options.plotting.backend = "plotly"
import plotly.express as px
#from scipy.stats import chi2_contingency


# In[2]:


st.write(
    "**Exploitation graphique : enquête sur la mobilité des français - 2019**"
)
st.write(
   "Mobilité locale, trajets de moins de 80 km. Exploitation : YTAC - Yves Tresson - Août 2024"
)

st.html(
    "<a href=https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019>Source : ENTD 2019</a>"
)

st.write(
   "Attention : la représentativité régionale n'est pas garantie par l'enquête. Toute sélection sur ce thème est donc à examiner avec circonspection, d'autant plus avec un choix de statut ou d'aire d'attraction. De façon générale, un petit échantillon ne sera pas significatif."
)
# In[3]:


df_deploc=pd.read_csv("k_deploc_public.csv",
                      sep=';',decimal='.',encoding='latin_1',
                     dtype={'CATCOM_AA_ORI':'Int64','CATCOM_AA_DES':'Int64',
                            'MMOTIFDACC':'str','MMOY2S':'str','MTITR1S':'str',
                            'MTITR2S':'str','MTITR3S':'str','MVEHEXT':'str'})
pd.options.mode.chained_assignment = None
#Rajout de POND_vk
df_deploc["POND_vk"]=df_deploc["POND_JOUR"]*df_deploc['MDISTTOT_fin']
#Rajout de POND_temps
df_deploc["POND_temps"]=df_deploc["POND_JOUR"]*df_deploc['DUREE']
# Segmentation de CAT_COM - Origine
df_deploc["CATCOM_AA_ORI"].fillna(99,inplace=True)
df_deploc.loc[:,"AA_ORI_CAT"]=pd.cut(df_deploc.loc[:,"CATCOM_AA_ORI"],[0,15,25,40,120],
                                     labels=["Pôle","Couronne","Hors attraction des villes","Autres"],right=True)
# Destination
df_deploc["CATCOM_AA_DES"].fillna(99,inplace=True)
df_deploc.loc[:,"AA_DES_CAT"]=pd.cut(df_deploc.loc[:,"CATCOM_AA_DES"],[0,15,25,40,120],
                                     labels=["Pôle","Couronne","Hors attraction des villes","Autres"],right=True)
# Segmentation de la distance : le graphe cumulatif indique les bornes pour une séparation en 4 zones : 0, 10, 20, 40 et plus
df_deploc.loc[:,"DIST_CAT"]=pd.cut(df_deploc.loc[:,"MDISTTOT_fin"],[0,10,20,40,10000],
                                     labels=["Moins de 10 km","10-20 km","20-40 km","Plus de 40 km"],right=True)
# Segmentation du motif
df_deploc.loc[:,"MOTIF_CAT"]=pd.cut(df_deploc.loc[:,"MMOTIFDES"].fillna(10),[0,2,3,5,7,9,10,1000],
                                     labels=["Retours","Achats","Soins-démarches",
                                             "Visites-accompagnement","Loisirs-vacances","Professionnel","N-D"],right=True)
df_deploc["MOTIF_CAT2"]=df_deploc["MOTIF_CAT"].astype(str)
# Segmentation du mode
df_deploc.loc[:,"MODE_CAT"]=pd.cut(df_deploc.loc[:,"mtp"].fillna(10),[0,2,3.1,4,8,1000],
                                     labels=["Mode doux","Voiture-conducteur","Voiture-passager ou autre",
                                             "Transport en commun","Autre"],right=True)
df_deploc["MODE_CAT2"]=df_deploc["MODE_CAT"].astype(str)

#Création d'une catégorie de destination particulière
# Cas où la commune de départ est la même que celle d'arrivée
df_deploc["AA_DES_CAT_2"]=df_deploc["CATCOM_AA_DES"]//10
df_deploc["AA_DES_CAT_2"][df_deploc["MEMDESCOM"]==1]=4
#Cas où la commune d'arrivée est une commune centre mais n'est pas dans la même aire d'attraction que la commune de départ
df_deploc["AA_DES_CAT_2"][(df_deploc["MEMDESAA"]==0) & (df_deploc["AA_DES_CAT"]=="Pôle")]=5
#Cas où la commune d'arrivée n'est pas une commune centre et n'est pas dans la même aire d'attraction que la commune de départ
df_deploc["AA_DES_CAT_2"][(df_deploc["MEMDESAA"]==0) & (df_deploc["AA_DES_CAT"]!="Pôle")]=6
df_deploc["AA_DES_CAT_2"].fillna(9,inplace=True)
df_deploc.loc[:,"AA_DES_CAT_3"]=pd.cut(df_deploc.loc[:,"AA_DES_CAT_2"],[0,1,2,3,4,5,6,120],
                                     labels=["Pôle","Couronne","Hors attraction des villes",
                     "Même commune","Pôle autre aire", "Reste autre aire","Autres"],right=True).astype(str)
#
#Intégration de données d'autres tables
df_tcm_men=pd.read_csv("tcm_men_public.csv",
                      sep=';',decimal='.',encoding='latin_1',
                     dtype={'CATCOM_AA_ORI':'Int64','CATCOM_AA_DES':'Int64',                         'DEP_RES':'str','NUTS_res':'str','TUU2017_RES':'str','TAA2017_RES':'str',
                            'CATCOM_AA_RES':'Int64'})
df_tcm_men=df_tcm_men.rename(columns={"ident_men":"IDENT_MEN"})
df_deploc=df_deploc.merge(df_tcm_men,how="left",on=["IDENT_MEN"])
df_ind=pd.read_csv("k_individu_public.csv",usecols=[0,1,3],sep=';',decimal='.',encoding='latin_1')
df_deploc=df_deploc.merge(df_ind,how="left",on=["IDENT_IND"])
pd.options.mode.chained_assignment = None

# Sélection sur semaine, déplacements locaux de moins de 80 km
df_deploc_2=df_deploc.query("mobloc==1 and MDISTTOT_fin<=80")

#Sélection des jours concernés par les déplacements
jours=st.multiselect(
        "Choisir le jour", ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'], ['lundi','mardi','mercredi','jeudi','vendredi'],)
df_deploc_2=df_deploc_2.loc[df_deploc_2["MDATE_jour"].isin(jours)]

#Sélection du motif
motif_texte="Tous motifs hors retours" 
motif_texte=st.selectbox("Motif (attention aux retours) :",["Tous motifs hors retours","Tous motifs","Retours","Achats","Soins-démarches",
                                             "Visites-accompagnement","Loisirs-vacances","Professionnel","N-D"])
if motif_texte=="Tous motifs hors retours" : df_deploc_2=df_deploc_2.query("MMOTIFDES>=2")
else :
    if motif_texte!="Tous motifs" : df_deploc_2=df_deploc_2[df_deploc_2['MOTIF_CAT'].str.contains(motif_texte)==True]	                                             

#Niveau national fixé après la sélection des jours et des motifs sous forme de df_deploc_3
df_deploc_3=df_deploc_2

st.write(
    "Les jours et motifs sélectionnés serviront pour les deux niveaux comparés : national et sélection"
)

#Sélection de la région par streamlit
region_name=st.selectbox("Choisir une région :",["France entière","Auvergne - Rhône Alpes","Bourgogne - Franche Comté","Bretagne",
                                            "Centre - Val de Loire","Corse","Grand Est","Hauts de France","Ile de France","Normandie","Nouvelle Aquitaine","Occitanie","Pays de la Loire","Sud"])
region="FR"
if region_name == "France entière" : region = "FR"
if region_name == "Auvergne - Rhône Alpes" : region = "FRK"
if region_name == "Bourgogne - Franche Comté" : region = "FRC"
if region_name == "Bretagne" : region = "FRH"
if region_name == "Centre - Val de Loire" : region = "FRB"
if region_name == "Corse" : region = "FRM"
if region_name == "Grand Est" : region = "FRF"
if region_name == "Hauts de France" : region = "FRE"
if region_name == "Ile de France" : region = "FR1"
if region_name == "Normandie" : region = "FRD"
if region_name == "Nouvelle Aquitaine" : region = "FRI"
if region_name == "Occitanie" : region = "FRJ"
if region_name == "Pays de la Loire" : region = "FRG"
if region_name == "Sud" : region = "FRL"
df_deploc_2=df_deploc_2[df_deploc_2["NUTS_res"].str.contains(region)==True]

#Sélection du statut de la commune
statut_texte=st.selectbox("Statut de la commune de résidence (ensemble par défaut)",["Ensemble","Hors unité urbaine","Ville-centre","Banlieue","Ville isolée"])
statut_com="FR"
if statut_texte=="Hors unité urbaine" : statut_com="H"
if statut_texte=="Ville-centre" : statut_com="C"
if statut_texte=="Banlieue" : statut_com="B"
if statut_texte=="Ville isolée" : statut_com="I"
if statut_com!="FR" :
   df_deploc_2=df_deploc_2[df_deploc_2['STATUTCOM_UU_RES'].str.contains(statut_com)==True]
#Sélection de la tranche d'aire d'attraction
taa_texte=st.selectbox("Tranche d'aire d'attraction des villes (commune de résidence)",["Ensemble","Commune hors attraction des villes","Aire de moins de 50 000 habitants",
		"Aire de 50 000 à moins de 200 000 habitants","Aire de 200 000 à moins de 700 000 habitants","Aire de 700 000 habitants ou plus (hors Paris)","Aire de Paris"])
taa="FR"
if taa_texte=="Commune hors attraction des villes" : taa="0"
if taa_texte=="Aire de moins de 50 000 habitants" : taa="1"
if taa_texte=="Aire de 50 000 à moins de 200 000 habitants" : taa="2"
if taa_texte=="Aire de 200 000 à moins de 700 000 habitants" : taa="3"
if taa_texte=="Aire de 700 000 habitants ou plus (hors Paris)" : taa="4"
if taa_texte=="Aire de Paris" : taa="5"
if taa!="FR" :
   df_deploc_2=df_deploc_2[df_deploc_2['TAA2017_RES'].str.contains(taa)==True]

import plotly.graph_objects as go

#Graphique sur les modes et la distance de déplacement avec comparaison sélection et national
Titre3='Km par voyageur suivant la distance du déplacement et le mode principal'+'<br><sup>'+\
       "Source ENTD 2019 - Mobilité locale moins de 80 km - Graphique YT"+'</sup><br><sup>'
df_deploc_3["y"]=df_deploc_3["POND_vk"]/sum(df_deploc_3["pond_indC"]) #niveau national
df_3_sum=df_deploc_3.loc[:,("DIST_CAT","MODE_CAT2","y")].groupby(["DIST_CAT","MODE_CAT2"],observed=True).sum()
df_3_sum=df_3_sum.reset_index()
df_3_sum["Niveau"]="National" 
df_deploc_2["y"]=df_deploc_2["POND_vk"]/sum(df_deploc_2["pond_indC"]) #Niveau sélectionné
df_2_sum=pd.pivot_table(df_deploc_2.loc[:,("DIST_CAT","MODE_CAT2","y")], index=["DIST_CAT","MODE_CAT2"], values="y", 
                                aggfunc="sum",margins=False)
df_2_sum=df_2_sum.reset_index() #remet sous forme de dataframe avec 3 colonnes.
df_2_sum["Niveau"]="Sélection"   
df_sum=pd.concat([df_3_sum,df_2_sum], ignore_index=True) # rassemble les 2 niveaux    
fig3 = px.bar(df_sum,x="DIST_CAT",
              y="y",
              title=Titre3,
             color="MODE_CAT2",
             facet_col="Niveau",
              labels={"DIST_CAT":"Distance du déplacement"},
             category_orders={"DIST_CAT": ["Moins de 10 km","10-20 km","20-40 km","Plus de 40 km"],
                             "MODE_CAT2":["Mode doux","Transport en commun",
                                          "Voiture-passager ou autre","Voiture-conducteur","Autre"]},
            color_discrete_sequence=["green", "blue", "goldenrod", "red", "magenta"]
             )
fig3.update_layout(yaxis_title="Km par voyageur")
fig3.update_layout(legend_title="Mode de transport principal")
st.plotly_chart(fig3)

#Graphique sur les motifs et la distance de déplacement avec comparaison sélection et national
Titre4='Km par voyageur suivant la distance du déplacement et le motif'+'<br><sup>'+\
       "Source ENTD 2019 - Mobilité locale moins de 80 km - Graphique YT"+'</sup><br><sup>'
df_3_sum2=df_deploc_3.loc[:,("DIST_CAT","MOTIF_CAT2","y")].groupby(["DIST_CAT","MOTIF_CAT2"],observed=True).sum()
df_3_sum2=df_3_sum2.reset_index()
df_3_sum2["Niveau"]="National" 
df_2_sum2=pd.pivot_table(df_deploc_2.loc[:,("DIST_CAT","MOTIF_CAT2","y")], index=["DIST_CAT","MOTIF_CAT2"], values="y", 
                                aggfunc="sum",margins=False)
df_2_sum2=df_2_sum2.reset_index() #remet sous forme de dataframe avec 3 colonnes.
df_2_sum2["Niveau"]="Sélection"  
df_sum2=pd.concat([df_3_sum2,df_2_sum2], ignore_index=True) 
fig4 = px.histogram(df_sum2, x="DIST_CAT", 
              y="y", 
              title=Titre4,
             color="MOTIF_CAT2",
             facet_col="Niveau",
              labels={"DIST_CAT":"Distance du déplacement"},
             category_orders={"DIST_CAT": ["Moins de 10 km","10-20 km","20-40 km","Plus de 40 km"],
                             "MOTIF_CAT2":["Achats","Soins-démarches","Visites-accompagnement","Loisirs-vacances","Professionnel"]}
             )
fig4.update_layout(yaxis_title="Km par voyageur")
fig4.update_layout(legend_title="Motif")
st.plotly_chart(fig4)

#Graphique sur la distance
df_deploc_2["Voyageurs-km"]=df_deploc_2["POND_vk"]
df_deploc_2["Nbre_deplacements"]=df_deploc_2["POND_JOUR"]
Titre2='Cumul suivant la distance du déplacement - Sélection'+'<br><sup>'+\
       "Source ENTD 2019 - Mobilité locale moins de 80 km - Graphique YT"+'</sup><br><sup>'
fig2 = px.ecdf(df_deploc_2, x="MDISTTOT_fin", 
              y=["Voyageurs-km","Nbre_deplacements"], 
              title=Titre2,
              labels={"MDISTTOT_fin":"Distance du déplacement","POND_vk":"Voyageurs-km"},
             )
fig2.update_layout(yaxis_title=None)
fig2.update_layout(legend_title_text="Variable")
fig2.update_xaxes(range=[0, 80])
fig2.update_yaxes(range=[0, 1])
#fig2.add_annotation(x=30, y=0.98,
#            text="Un AR par semaine",
#            showarrow=False,
#            arrowhead=1)
fig2.add_vline(x=20,line_width=1, line_dash="dash", line_color="green")
st.plotly_chart(fig2)

# Elaboration du graphique sankey
df_sankey=df_deploc_2.groupby(["AA_ORI_CAT","AA_DES_CAT_2"],dropna=False, observed=True)["POND_vk"].sum().reset_index()
df_sankey.columns = ['source','target','value']
#df_sankey.fillna(99.0,inplace=True)
df_sankey["value"]=df_sankey["value"]/1000000
mapping_dict = {"Pôle" : 0,"Couronne" : 1,"Hors attraction des villes" : 2,"Autres" : 3}
mapping_dict2 = {1 : 4, 2 : 5, 3 : 6, 4 : 7, 5 : 8, 6 :9 , 9 : 10}
                     #"Pôle autre aire" : 8, "Reste autre aire" : 9}
df_sankey['source'] = df_sankey['source'].map(mapping_dict)
df_sankey['target'] = df_sankey['target'].map(mapping_dict2)
links_dict = df_sankey.to_dict(orient='list')
    
fig = go.Figure(data=[go.Sankey(
        valuesuffix = " Millions vk",
        node = dict(
            pad = 15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label = ["Pôle","Couronne","Hors attraction des villes","Autres",
                    "Pôle","Couronne","Hors attraction des villes",
                     "Même commune","Pôle autre aire", "Reste autre aire","Autres"],
            color='green'
        ),
        link = dict(
            source= links_dict['source'],
            target = links_dict['target'],
            value = links_dict['value']
        )

    )
    ])
Texte1="Flux entre types de communes - Sélection (vk)"
Texte2="Source ENTD 2019 - Mobilité locale moins de 80 km - Graphique YT"
Texte3="Millions de voyageurs-km"
fig.update_layout(title=Texte1+'<br><sup>'+Texte2+'</sup><br><sup>'+Texte3+'</sup>')
st.plotly_chart(fig)

#Dataframes de rendu
data_tempo=[["National",sum(df_deploc_3["POND_vk"]),sum(df_deploc_3["pond_indC"])],["Sélection",sum(df_deploc_2["POND_vk"]),sum(df_deploc_2["pond_indC"])]]
df_tempo=pd.DataFrame(data=data_tempo,columns=["Niveau","Somme des voyageurs-km","Nombre d'individus"])
df_tempo["Parcours moyen"]=df_tempo["Somme des voyageurs-km"]/df_tempo["Nombre d'individus"]
st.write(
   "Tableau des poids respectifs en termes de voyageurs-km et d'individus. Attention : plus la sélection est petite, moins les résultats sont fiables"
)
st.dataframe(df_tempo,column_config={"Somme des voyageurs-km":st.column_config.NumberColumn(format="%0.0f"),
				"Nombre d'individus":st.column_config.NumberColumn(format="%0.0f"),
				"Parcours moyen":st.column_config.NumberColumn(format="%0.2f")},hide_index=True)
st.write(
   "Tableau des résultats : catégories de distance et modes de déplacements."
)
st.dataframe(df_sum,column_config={"y":st.column_config.NumberColumn("km/voyageur",format="%0.2f")},hide_index=True)

st.write(
   "Tableau des résultats : catégories de distance et motifs de déplacements."
)
st.dataframe(df_sum2,column_config={"y":st.column_config.NumberColumn("km/voyageur",format="%0.2f")},hide_index=True)



