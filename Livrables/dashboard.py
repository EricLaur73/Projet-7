import pandas as pd
import numpy as np
import plotly.graph_objects as go

from datetime import datetime,timedelta, date
from PIL import Image
import streamlit as st # pour créer le formulaire
import requests # pour interroger l'API

# Pour interroger l'API
def request_prediction(model_uri, data_json):
    headers = {"Content-Type": "application/json"}
    response = requests.request(method='POST', headers=headers, url=model_uri, json=data_json)

    if response.status_code != 200:
        raise Exception(
            "Request failed with status {}, {}".format(response.status_code, response.text))

    return response.json()

# Pour préparer les données au format JSON et lancer une simulation
def simulation (parametres) :

        # Construction des données format JSON
        data=list(parametres.iloc[0])
        data_json = {"columns": list(parametres.columns), "data": [data]}

        # Interrogation de l'API MLflow
        pred = None
        pred = request_prediction(MLFLOW_URI, data_json)[0]

        return pred

# Savoir si session locale ou heroku
import socket
hostname=socket.gethostname()

# Chemin de l'application (MORPHEUS c'est nom de mon PC en local)
if hostname=="MORPHEUS":
    path_application="D:/Formation_Data_Scientist/Projets/Projet 7" # en local
else: 
    path_application="." # sur Heroku

# Adresse Serveur/Port API MLflow
MLFLOW_URI = 'http://127.0.0.1:5000/invocations'

# Features du modèle
features=[
'FLAG_OWN_CAR',
'FLAG_OWN_REALTY',
'CNT_CHILDREN',
'AMT_INCOME_TOTAL',
'AMT_CREDIT',
'AMT_ANNUITY',
'AMT_GOODS_PRICE',
'NAME_EDUCATION_TYPE',
'NAME_FAMILY_STATUS',
'DAYS_BIRTH',
'EXT_SOURCE_1',
'EXT_SOURCE_2',
'EXT_SOURCE_3',
]

# Importer les échantillons
echantillon = pd.read_csv(path_application+'/Livrables/data/echantillon.csv',sep=',',encoding='utf-8')
echantillon_test = pd.read_csv(path_application+'/Livrables/data/echantillon_test.csv',sep=',',encoding='utf-8')

# Générer les choix possibles pour les features de type classes
plage_valeur={}
for feature in features:
    if echantillon[feature].dtypes=='object':
        plage_valeur[feature]=np.sort((echantillon[feature].unique()))

def main():

    st.title('Scoring crédit')
    st.markdown('_Evaluation de difficultés de remboursement en fonction du profil du client_')

    image=Image.open(path_application + '/Livrables/image_scoring.jpg')
    st.image(image, use_column_width='always')

    # Choix d'un client à partir de la base test

    st.markdown("### 1. Choix d'un client de la base de données")
    choix_iDClient=st.select_slider('Identifiant du client',options=echantillon_test['SK_ID_CURR'])
    param_choixClient=echantillon_test[echantillon_test['SK_ID_CURR']==choix_iDClient].to_dict(orient='records')[0]
    param_naissance_choixClient=(date.today()+timedelta(days=param_choixClient['DAYS_BIRTH'])).strftime("%d/%m/%Y") # conversion en date de naissance
  
    # Paramètres du client 

    st.markdown("### 2. Paramètres du client")
    st.markdown("_modification possible avant simulation_")

    param={}
    col1, col2= st.columns(2)

    with col1 :
        param[features[0]] = st.radio("2.1 Est propriétaire d'une voiture ?",plage_valeur[features[0]], index=int(np.where(plage_valeur[features[0]]==param_choixClient[features[0]])[0]))
        param[features[1]] = st.radio("2.2 Est propriétaire d'une maison ou d'un appartement?",plage_valeur[features[1]], index=int(np.where(plage_valeur[features[1]]==param_choixClient[features[1]])[0]))
        param[features[2]] = float(st.slider("2.3 Nombre d'enfants ?", 0, 20, step=1, value=param_choixClient[features[2]]))
        param[features[3]] = st.number_input("2.4 Niveau de revenu total annuel ?",min_value=0.,step=1000., value=float(param_choixClient[features[3]]))
        param[features[4]] = st.number_input("2.5 Valeur total du crédit ?",min_value=0.,step=1000.,value=float(param_choixClient[features[4]]))
        param[features[5]] = st.number_input("2.6 Annuité du crédit ?",min_value=0.,step=1000.,value=float(param_choixClient[features[5]]))
        param[features[6]] = st.number_input("2.7 Valeur du bien pour lequel le crédit est souscrit ?",min_value=0.,step=1000.,value=float(param_choixClient[features[6]]))

    with col2 :
        param[features[7]] = st.radio("2.8 Niveau d'études ?", plage_valeur[features[7]], index=int(np.where(plage_valeur[features[7]]==param_choixClient[features[7]])[0]))
        param[features[8]] = st.radio("2.9 Status familial ?", plage_valeur[features[8]], index=int(np.where(plage_valeur[features[8]]==param_choixClient[features[8]])[0]))
        param[features[9]] = float((datetime.strptime(st.text_input("2.10 Date de naissance en format JJ/MM/AAAA ?",value=param_naissance_choixClient), "%d/%m/%Y")-datetime.today()).days) # conversion date en jours écoulés
        age=int(round(np.abs(param[features[9]])/365,0))
        st.write(f'Age : {age} ans')
        param[features[10]] = st.slider("2.11 Paramètre source externe 1 ?", 0., 1., step=0.01, value=float(param_choixClient[features[10]]))
        param[features[11]] = st.slider("2.12 Paramètre source externe 2 ?", 0., 1., step=0.01, value=float(param_choixClient[features[11]]))
        param[features[12]] = st.slider("2.13 Paramètre source externe 3 ?", 0., 1., step=0.01, value=float(param_choixClient[features[12]]))

    # Paramètres calculés 

    st.markdown("### 3. Indicateurs calculés")

    endettement = param[features[5]] / param[features[3]] # calcul de l'endettement
    duree_credit = param[features[4]] / param[features[5]] # calcul durée du credit

    st.text(f'3.1 Endettement : {endettement:.0%}')
    st.text(f'3.2 Durée du remboursement : {duree_credit:.1f} année(s)')

    # Enregistrement des paramètres dans un dataframe parametres

    parametres=pd.DataFrame(columns=param.keys(),data=[param.values()])

    # Positionnement 

    st.markdown("### 4. Positionnement client")
    st.markdown("_Client sélectionné en rouge, groupe avec crédit accordé en bleu_")

    echantillon_0 = echantillon[echantillon['TARGET']==0] # Sélection du  groupe de client avec crédits accordés

    col3, col4 = st.columns(2)

    # Graphique 1 : RADAR

    features_1 = [
        'EXT_SOURCE_1',
        'EXT_SOURCE_2',
        'EXT_SOURCE_3',
        ]
    indicateurs_1= echantillon_0[features_1].mean()
    position_client_1=np.abs(parametres[features_1].iloc[0])
    fig1=go.Figure()
    fig1.add_trace(go.Scatterpolar(r=indicateurs_1, theta=features_1,fill="toself",name='Moy. groupe'))
    fig1.add_trace(go.Scatterpolar(r=position_client_1, theta=features_1,fill="toself",name='Client'))
    fig1.update_layout(autosize=False)

    with col3 :
        st.plotly_chart(fig1,use_container_width=True)

    # Graphique 2 : Endettement
      
    endettement_0=(echantillon_0['AMT_ANNUITY']/echantillon_0['AMT_INCOME_TOTAL'])*100
    fig2=go.Figure()
    fig2.add_trace(go.Box(y=endettement_0, boxpoints=False, name='Endettement%'))
    fig2.add_trace(go.Box(y=[endettement*100],name='Endettement%'))
    fig2.update_layout(autosize=False)
    
    with col4 :
        st.plotly_chart(fig2,use_container_width=True)
    

    # Simulation 

    st.markdown("### 5. Simulation")

    simulation_btn = st.button('GO !')

    if simulation_btn :
        
        if simulation(parametres)==0 :
            st.header(f'PRÊT accordé :-)')
        else :
            st.header(f'/!\ Désolé : PRÊT refusé :-(')

if __name__ == '__main__': main()

# Dans un terminal bash, lancer le dashboard avec :  
# $ streamlit run ./Livrables/dashboard.py