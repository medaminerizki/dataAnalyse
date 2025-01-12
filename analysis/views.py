from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.core.paginator import Paginator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
import numpy as np
from io import BytesIO
import io
import base64
from django import forms
from scipy.stats import bernoulli, binom, uniform, poisson, norm, expon, t
from .forms import ProbabilityForm



def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        try:
            df = pd.read_csv(file)  # lire le fichier CSV
        except Exception:
            return render(request, 'analysis/upload.html', {'error': 'Format du fichier invalide.'})

        # enregistrer le DataFrame dans la session sous forme JSON
        request.session['dataframe'] = df.to_json()

        return redirect('menu')  

    return render(request, 'analysis/upload.html')


def menu(request):
    if 'dataframe' not in request.session:
        return redirect('upload_file') 

    return render(request, 'analysis/menu.html')


# Table avec pagination
def view_data(request):
    if 'dataframe' not in request.session:
        return redirect('upload_file') 

    df = pd.read_json(request.session['dataframe'])

    # Paginations 10 lignes par page
    paginator = Paginator(df.values, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data_table = pd.DataFrame(page_obj.object_list, columns=df.columns).to_html(classes='data', header=True, index=False)

    return render(request, 'analysis/view_data.html', {
        'data_table': data_table,
        'page_obj': page_obj,
    })


def choose_graphic(request):
    return render(request, 'analysis/choose_graphic.html')


def choose_columns(request):
    graph_type = request.GET.get('graph_type', None)


    if 'dataframe' not in request.session:
        return redirect('upload_file')  # rediriger vers la page de téléchargement du fichier

    df = pd.read_json(request.session['dataframe'])

    # Initialiser une variable pour les colonnes à afficher
    columns = df.columns.tolist()

    x_columns = []
    y_columns = []
    display_x = True
    display_y = True
    default_x_column = None
    default_y_column = None

    if graph_type == 'line' or graph_type == 'scatter':

        x_columns = [col for col in columns if df[col].dtype in ['int64', 'float64']]  # Quantitative 
        y_columns = x_columns  # y peuvent aussi être des colonnes quantitatives

    elif graph_type == 'boxplot':
        
        x_columns = [col for col in columns if df[col].dtype in ['int64', 'float64']]
        display_y = False 

    elif graph_type == 'violin':
        x_columns = [col for col in columns if df[col].dtype == 'object']  # Catégorique
        y_columns = [col for col in columns if df[col].dtype in ['int64', 'float64']]  # Quantitative
    elif graph_type == 'histogram':

        x_columns = columns
        y_columns = [col for col in columns if df[col].dtype in ['int64', 'float64']]  # Quantitative

    elif graph_type == 'pie chart':

        x_columns = [col for col in columns if df[col].dtype == 'object']  # Catégorique
        display_y = False

    elif graph_type == 'kde':
        
        x_columns = [col for col in columns if df[col].dtype in ['int64', 'float64']]  # Quantitative
        display_y = False  

    elif graph_type == 'bar':
        x_columns = [col for col in columns if df[col].dtype == 'object']  # Catégorique
        y_columns = [col for col in columns if df[col].dtype in ['int64', 'float64']]  # Quantitative

    else:
        
        x_columns = columns
        y_columns = columns


    if x_columns:
        default_x_column = x_columns[0]  # Valeur par défaut pour x_column
    if y_columns:
        default_y_column = y_columns[0]  # Valeur par défaut pour y_column

    return render(request, 'analysis/choose_columns.html', {
        'x_columns': x_columns,
        'y_columns': y_columns,
        'graph_type': graph_type,
        'display_x': display_x,
        'display_y': display_y,
        'default_x_column': default_x_column,
        'default_y_column': default_y_column,
    })


def graph_result(request):
    graph_type = request.POST.get('graph_type') 
    x_column = request.POST.get('x_column')
    y_column = request.POST.get('y_column')

    df = pd.read_json(request.session['dataframe'])

    fig, ax = plt.subplots(figsize=(8, 6))  

    if graph_type == 'line':

        ax.plot(df[x_column], df[y_column], label=f'{x_column} vs {y_column}')
        ax.set_title(f'Graphique linéaire de {x_column} vs {y_column}')
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
    
    elif graph_type == 'scatter':

        ax.scatter(df[x_column], df[y_column], label=f'{x_column} vs {y_column}')
        ax.set_title(f'Nuage de points de {x_column} vs {y_column}')
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)

    elif graph_type == 'boxplot':

        sns.boxplot(x=df[x_column], ax=ax)
        ax.set_title(f'Boxplot de {x_column}')
    
    elif graph_type == 'violin':

        sns.violinplot(x=df[x_column], y=df[y_column], ax=ax)
        ax.set_title(f'Violin plot de {x_column} vs {y_column}')
    
    elif graph_type == 'histogram':

        ax.hist(df[x_column], bins=20, color='skyblue', edgecolor='black')
        ax.set_title(f'Histogramme de {x_column}')
        ax.set_xlabel(x_column)
        ax.set_ylabel('Fréquence')

    elif graph_type == 'pie chart':
        
        if x_column in df.columns:
            
            if df[x_column].dtype == 'object' or df[x_column].dtype.name == 'category':
               
                pie_data = df[x_column].value_counts()

                ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
                ax.set_title(f'Pie chart de {x_column}')
                ax.axis('equal')  # pour avoir un cercle parfait
            else:

                return render(request, 'analysis/graph_result.html', {'error_message': 'La colonne doit être catégorique pour un Pie chart.'})
        else:

            return render(request, 'analysis/graph_result.html', {'error_message': f'La colonne {x_column} n\'existe pas dans le DataFrame.'})


    elif graph_type == 'bar':
        
        sns.barplot(x=df[x_column], y=df[y_column], ax=ax)
        ax.set_title(f'Bar plot de {x_column} vs {y_column}')
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
    
    elif graph_type == 'heatmap':
        
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

        
        if x_column in numeric_columns and y_column in numeric_columns:
            # corrélation entre les deux colonnes
            correlation_matrix = df[[x_column, y_column]].corr()
            
            sns.heatmap(correlation_matrix, annot=True, cmap="YlGnBu", ax=ax)
            ax.set_title(f'Heatmap de corrélation de {x_column} vs {y_column}')
        
        else:
            
            heatmap_data = df.pivot_table(index=x_column, columns=y_column, aggfunc='size', fill_value=0)
            sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", ax=ax)
            ax.set_title(f'Heatmap de {x_column} vs {y_column} (comptage)')




    elif graph_type == 'kde':
        sns.kdeplot(df[x_column], ax=ax, shade=True, color='blue')
        ax.set_title(f'KDE plot de {x_column}')
    
    else:
        return redirect('menu')  

    # image du graphique dans un format base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    
    return render(request, 'analysis/graph_result.html', {'image_base64': image_base64})

def probability_menu(request):
    return render(request, 'analysis/probability_menu.html')

def tests_menu(request):
    return render(request, 'analysis/tests_menu.html')

def bernoulli_form(request):
    graph = None
    if request.method == "POST":
        p = float(request.POST.get('p'))  # probabilité de succès
        
        # Génération des valeurs de X (0 ou 1)
        x = [0, 1]
        y = bernoulli.pmf(x, p)
        
        # Création du graphique
        fig, ax = plt.subplots()
        ax.bar(x, y, color='green', alpha=0.7)
        ax.set_title(f'Distribution de Bernoulli\n(p={p})')
        ax.set_xlabel('Valeur')
        ax.set_ylabel('Probabilité')
        
        # Sauvegarde du graphique dans un buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # Conversion en base64 pour affichage dans le template
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'analysis/bernoulli_form.html', {'graph': graph})

def binomial_form(request):
    graph = None
    if request.method == "POST":
        n = int(request.POST.get('n'))  # Nombre d'essais
        p = float(request.POST.get('p'))  # Probabilité de succès
        
        # Calcul des probabilités binomiales
        x = np.arange(0, n + 1)
        y = binom.pmf(x, n, p)
        
        # Création du graphique
        fig, ax = plt.subplots()
        
        # Dessiner les barres
        ax.bar(x, y, color='green', alpha=0.7, label="PMF - Barres")
        
        # Dessiner la courbe (fonction de masse de probabilité)
        ax.plot(x, y, color='red', marker='o', label="Courbe")
        
        # Ajouter un titre et des labels
        ax.set_title(f'Distribution Binomiale\n(n={n}, p={p})')
        ax.set_xlabel('Nombre de succès')
        ax.set_ylabel('Probabilité')
        
        # Ajouter une légende
        ax.legend()

        # Sauvegarde du graphique dans un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # Conversion en base64 pour affichage dans le template
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'analysis/binomial_form.html', {'graph': graph})

def uniform_form(request):
    graph = None
    if request.method == "POST":
        # Récupération des bornes a et b depuis le formulaire
        a = float(request.POST.get('a'))  # Borne inférieure
        b = float(request.POST.get('b'))  # Borne supérieure
        
        # Densité théorique
        x = np.linspace(a - 1, b + 1, 500)
        density = np.where((x >= a) & (x <= b), 1 / (b - a), 0)
        
        # Simulation de valeurs aléatoires
        n_samples = 1000
        random_values = np.random.uniform(a, b, n_samples)

        # Création du graphique
        fig, ax = plt.subplots(figsize=(10, 6))

        # Affichage de la densité théorique (ligne bleue)
        ax.plot(x, density, label=f'Densité théorique (a={a}, b={b})', color='blue', lw=2)

        # Affichage de l'histogramme des valeurs simulées (en orange)
        ax.hist(random_values, bins=30, density=True, alpha=0.5, color='green', label='Histogramme des données simulées')

        # Personnalisation du graphique
        ax.set_title("Loi Uniforme Continue", fontsize=16)
        ax.set_xlabel("x", fontsize=14)
        ax.set_ylabel("Densité de probabilité", fontsize=14)

        # Affichage des bornes a et b (lignes verticales)
        ax.axvline(a, color='red', linestyle='--', label=f'Borne a = {a}')
        ax.axvline(b, color='red', linestyle='--', label=f'Borne b = {b}')
        
        # Ajouter la légende et la grille
        ax.legend(fontsize=12)
        ax.grid(alpha=0.3)
        
        # Sauvegarde du graphique dans un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # Conversion en base64 pour affichage dans le template
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'analysis/uniform_form.html', {'graph': graph})


def poisson_form(request):
    graph = None
    if request.method == "POST":
        mu = float(request.POST.get('mu'))  # Moyenne
        
        # Calcul des probabilités de Poisson
        x = np.arange(0, int(mu * 3) + 1)  # Étendre l'intervalle x
        y = poisson.pmf(x, mu)
        
        # Création du graphique
        fig, ax = plt.subplots()
        
        # Affichage des barres (discrètes)
        ax.bar(x, y, color='green', alpha=0.7, label=f'λ={mu}')
        
        # Ajout de la courbe (continue) sur le même graphique
        ax.plot(x, y, color='blue', alpha=0.8, linewidth=2, label='Courbe de probabilité')
        
        ax.set_title(f'Distribution de Poisson\n(λ={mu})')
        ax.set_xlabel('Nombre d\'événements')
        ax.set_ylabel('Probabilité')
        
        # Ajouter la légende
        ax.legend()
        
        # Sauvegarde du graphique dans un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # Conversion en base64 pour affichage dans le template
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'analysis/poisson_form.html', {'graph': graph})

def normal_form(request):
    graph = None
    if request.method == "POST":
        mu = float(request.POST.get('mu'))  # Moyenne
        sigma = float(request.POST.get('sigma'))  # Écart-type
        
        # Génération des valeurs pour la courbe normale
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        y = norm.pdf(x, mu, sigma)
        
        # Création du graphique
        fig, ax = plt.subplots()
        ax.plot(x, y, color='green', alpha=0.7)
        ax.fill_between(x, y, color='green', alpha=0.3)
        ax.set_title(f'Distribution Normale\n(μ={mu}, σ={sigma})')
        ax.set_xlabel('Valeur')
        ax.set_ylabel('Densité de probabilité')
        
        # Sauvegarde du graphique dans un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # Conversion en base64 pour affichage dans le template
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'analysis/normal_form.html', {'graph': graph})

def exponential_form(request):
    graph = None
    if request.method == "POST":
        lambda_ = float(request.POST.get('lambda'))  # Taux de l'événement
        
        # Génération des valeurs pour la fonction exponentielle
        x = np.linspace(0, 10, 1000)
        y = expon.pdf(x, scale=1/lambda_)
        
        # Création du graphique
        fig, ax = plt.subplots()
        ax.plot(x, y, color='green', alpha=0.7)
        ax.fill_between(x, y, color='green', alpha=0.3)
        ax.set_title(f'Distribution Exponentielle\n(λ={lambda_})')
        ax.set_xlabel('Temps')
        ax.set_ylabel('Densité de probabilité')
        
        # Sauvegarde du graphique dans un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        
        # Conversion en base64 pour affichage dans le template
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render(request, 'analysis/exponential_form.html', {'graph': graph})

def z_test_view(request):
    result = None
    decision = None

    if request.method == "POST":
        # Get inputs from the form
        population_mean = float(request.POST.get("population_mean"))
        sample_mean = float(request.POST.get("sample_mean"))
        sample_std = float(request.POST.get("sample_std"))
        sample_size = int(request.POST.get("sample_size"))
        alpha = float(request.POST.get("alpha"))

        # Calculate Z score
        z_score = (sample_mean - population_mean) / (sample_std / np.sqrt(sample_size))

        # Calculate p-value
        p_value = 2 * (1 - norm.cdf(abs(z_score)))

        # Decision
        if p_value < alpha:
            decision = "Rejet de l'hypothèse nulle (H₀)."
        else:
            decision = "Non-rejet de l'hypothèse nulle (H₀)."

        result = {
            "z_score": z_score,
            "p_value": p_value,
            "decision": decision,
        }

    return render(request, "analysis/z_test.html", {"result": result})

def t_test_view(request):
    result = None
    decision = None

    if request.method == "POST":
        # Get inputs from the form
        population_mean = float(request.POST.get("population_mean"))
        sample_mean = float(request.POST.get("sample_mean"))
        sample_std = float(request.POST.get("sample_std"))
        sample_size = int(request.POST.get("sample_size"))
        alpha = float(request.POST.get("alpha"))

        # Degrees of freedom
        df = sample_size - 1

        # Calculate T score
        t_score = (sample_mean - population_mean) / (sample_std / np.sqrt(sample_size))

        # Calculate p-value
        p_value = 2 * (1 - t.cdf(abs(t_score), df))

        # Decision
        if p_value < alpha:
            decision = "Rejet de l'hypothèse nulle (H₀)."
        else:
            decision = "Non-rejet de l'hypothèse nulle (H₀)."

        result = {
            "t_score": t_score,
            "p_value": p_value,
            "decision": decision,
        }

    return render(request, "analysis/t_test.html", {"result": result})