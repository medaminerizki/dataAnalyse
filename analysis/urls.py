from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'), 
    path('menu/', views.menu, name='menu'),  
    path('view_data/', views.view_data, name='view_data'),  
    path('choose_graphic/', views.choose_graphic, name='choose_graphic'), 
    path('choose_columns/', views.choose_columns, name='choose_columns'),
    path('graph_result/', views.graph_result, name='graph_result'),
]
