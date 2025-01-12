# Projet Django d'analyse de données Excel

## Description
Ce projet Django permet d'importer un fichier Excel CSV, d'analyser les données et de les visualiser sous forme de différents graphiques.

## Captures d'écran
Voici les captures d'écran du projet :

### Accueil
![Accueil](screenshots/home.png)
### Menu
![Menu](screenshots/menu.png)
### Sélection de graphique
![Sélection de graphique](screenshots/graph_select.png)
### Sélection de Loi de probabilité
![Sélection de loi](screenshots/menu_probas.png)
### Sélection du test d'hypothèse
![Sélection de test](screenshots/menu_tests.png)


## Fonctionnalités
- Importation d'un fichier Excel CSV
- Analyse des données
- Visualisation des données sous forme de :
  - Histogramme ![Histogramme](screenshots/histogram.png)
  - Diagramme en barres ![Barplot](screenshots/barplot.png)
  - Diagramme en boîtes ![Boxplot](screenshots/boxplot.png)
  - Diagramme circulaire ![Piechart](screenshots/piechart.png)
  - Nuage de points ![Scatterplot](screenshots/scatterplot.png)
  - Carte de chaleur ![Heatmap](screenshots/heatmap.png)
  - Graphique à noyau de densité ![KDE](screenshots/kde.png)
- Calcul des probabilités
  - Loi de Bernoulli ![Bernoulli](screenshots/bernoulli.png)
  - Loi binomiale ![Binomiale](screenshots/binomiale.png)
  - Loi uniforme ![Uniforme](screenshots/uniforme.png)
  - Loi de Poisson ![Poisson](screenshots/poisson.png)
  - Loi Normale ![Normale](screenshots/normale.png)
  - Loi exponentielle ![Expon](screenshots/expon.png)
-Tests des hypothèses
  - Z-test ![Z-test](screenshots/ztest.png)
  - T-test ![T-test](screenshots/ttest.png)


## Installation
1. Clonez le dépôt Git :
git clone https://github.com/medaminerizki/dataAnalyse.git

Copy
2. Créez et activez un environnement virtuel :
python -m venv env
source env/bin/activate

Copy
3. Installez les dépendances :
pip install -r requirements.txt

Copy
4. Lancez le serveur de développement :
python manage.py runserver

Copy
5. Accédez à l'application dans votre navigateur à l'adresse `http://127.0.0.1:8000/`.

## Utilisation
1. Cliquez sur le bouton "Importer un fichier Excel" pour sélectionner le fichier CSV à analyser.
2. Une fois le fichier importé, les différents graphiques seront générés et affichés sur la page.
3. Vous pouvez interagir avec les graphiques pour explorer davantage les données.


## Auteurs
Mohamed Amine RIZKI  
Yahya SERNANE
