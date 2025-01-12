from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'), 
    path('menu/', views.menu, name='menu'),  
    path('view_data/', views.view_data, name='view_data'),  
    path('choose_graphic/', views.choose_graphic, name='choose_graphic'), 
    path('choose_columns/', views.choose_columns, name='choose_columns'),
    path('graph_result/', views.graph_result, name='graph_result'),
    path('probability_menu/', views.probability_menu, name='probability_menu'),
    path('bernoulli/', views.bernoulli_form, name='bernoulli_form'),
    path('binomial/', views.binomial_form, name='binomial_form'),
    path('uniform/', views.uniform_form, name='uniform_form'),
    path('poisson/', views.poisson_form, name='poisson_form'),
    path('normal/', views.normal_form, name='normal_form'),
    path('exponential/', views.exponential_form, name='exponential_form'),
    path('tests_menu/',views.tests_menu, name='tests_menu'),
    path('z_test/',views.z_test_view, name='z_test'),
    path('t_test/',views.t_test_view, name='t_test')
    
]
