from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.core.paginator import Paginator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
import numpy as np
import io
import base64


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