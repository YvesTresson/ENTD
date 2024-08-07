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
    "Exploitation graphique : enquête sur la mobilité des français - 2019"
)
st.write(
   "Mobilité locale, trajets de moins de 80 km"
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
pd.options.mode.chained_assignment = None
# Sélection sur semaine, déplacements locaux de moins de 80 km et motifs aller
region=st.text_input("Quel code NUTS de région ? (FR pour l'ensemble)","FR")
tuu=st.text_input("Quel tranche d'unité urbaine ? (De 0 à 8 pour Paris, FR pour l'ensemble)","FR")
taa=st.text_input("Quel tranche d'aire d'attraction ? (De 0 à 5 pour Paris, FR pour l'ensemble)","FR")
df_deploc_2=df_deploc.query("mobloc==1 and MMOTIFDES>=2 and MDISTTOT_fin<=80 ")
df_deploc_2=df_deploc_2[df_deploc_2["NUTS_res"].str.contains(region)==True]
if tuu!="FR" :
   df_deploc_2=df_deploc_2[df_deploc_2['TUU2017_RES'].str.contains(tuu)==True]
if taa!="FR" :
   df_deploc_2=df_deploc_2[df_deploc_2['TAA2017_RES'].str.contains(taa)==True]
jours=st.multiselect(
        "Choisir le jour", ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'], ['lundi','mardi','mercredi','jeudi','vendredi'],)
df_deploc_2=df_deploc_2.loc[df_deploc_2["MDATE_jour"].isin(jours)]
df_sankey=df_deploc_2.groupby(["AA_ORI_CAT","AA_DES_CAT_2"],dropna=False, observed=True)["POND_vk"].sum().reset_index()
df_sankey.columns = ['source','target','value']
#df_sankey.fillna(99.0,inplace=True)
df_sankey["value"]=df_sankey["value"]/5000000
    #print(sum(df_sankey["value"]))
    #print(df_sankey)
    #links_dict = df_sankey.to_dict(orient='list')
mapping_dict = {"Pôle" : 0,"Couronne" : 1,"Hors attraction des villes" : 2,"Autres" : 3}
mapping_dict2 = {1 : 4, 2 : 5, 3 : 6, 4 : 7, 5 : 8, 6 :9 , 9 : 10}
                     #"Pôle autre aire" : 8, "Reste autre aire" : 9}
df_sankey['source'] = df_sankey['source'].map(mapping_dict)
df_sankey['target'] = df_sankey['target'].map(mapping_dict2)
links_dict = df_sankey.to_dict(orient='list')
    
# Elaboration du graphique
import plotly.graph_objects as go

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
Texte1="Flux entre types de communes - Aller (vk)"
Texte2="Source ENTD 2019 - Mobilité locale moins de 80 km - Graphique YT"
Texte3="Millions de voyageurs-km"
fig.update_layout(title=Texte1+'<br><sup>'+Texte2+'</sup><br><sup>'+Texte3+'</sup>')
st.plotly_chart(fig)









