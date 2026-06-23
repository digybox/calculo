from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_cliente, name='cliente'),
    path('dashboard/', views.dashboard_admin, name='dashboard'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
]