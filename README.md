# Schéma de principe 
    modèlisation > API_MLflow > Interrogation par DashBoard Streamlit
    Dépôt fichiers sur Github > Déploiement Automatique sur Heroku à chaque $ git push -u origin main

# Fichiers d'initialisation (heroku et Streamlit)
    runtime.txt, version de python à utiliser
    requirements.txt, liste des librairies python dont heroku a besoin pour réaliser la build de l'application
    script.sh, contient les 2 processus à lancer dans le même dynos heroku (serveur d'API MLflow et serveur Streamlit)
    Procfile, processus web dynos à lancer après la build (lance le shell script.sh)
    setup.sh, paramètrage général de Streamlit

# Fichiers de l'application (dans le sous-dossier Livrables)
    scoring_client.ipynb, notebook d'analyse de création du modèle de prédiction
    api_MLflow.ipynb, notebook de création du modèle MLFlow / API ; génère le dossier mlflow_model
    dashboard.py, interface Web réalisée avec Streamlit pour saisie des paramètres et interrogation de l'API MLflow
    pipeline_scoring.joblib et signature_Mlflow.joblib, objets sérialisés

# Dépôt Github des fichiers de l'application
    https://github.com/EricLaur73/Projet-7/

# Déploiement de l'application avec HEROKU 
    test en mode local d'heroku
        - Dans un terminal bash lancer l'application avec : $ heroku local
        - Puis cliquer sur le lien du serveur Streamlit

    en mode cloud, tous les fichiers sont automatiquement déployés sur heroku à chaque mise à jour du dépôt Github
        - lien application : https://scorecredit.herokuapp.com/ 