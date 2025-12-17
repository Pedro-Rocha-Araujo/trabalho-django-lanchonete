from django.contrib import admin
from django.urls import path
from app_lanchonete import views

urlpatterns = [
    path('',views.home, name='home'),

    path('menu_clientes/', views.menu_clientes, name='menu_clientes'),
    path('menu_funcionarios/', views.menu_funcionarios, name='menu_funcionarios'),
    path('menu_lanches/', views.menu_lanches, name='menu_lanches'),
    path('menu_pedido/', views.menu_pedidos, name='menu_pedidos'),

    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('cadastrar_funcionario/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('cadastrar_lanche/', views.cadastrar_lanche, name='cadastrar_lanche'),
    path('cadastrar_pedido/', views.cadastrar_pedido, name='cadastrar_pedido'),

    path('clientes_cadastrados/', views.clientes_cadastrados, name='clientes_cadastrados'),
    path('funcionarios_cadastrados/', views.funcionarios_cadastrados, name='funcionarios_cadastrados'),
    path('lanches_cadastrados/', views.lanches_cadastrados, name='lanches_cadastrados'),
    path('pedidos_cadastrados/', views.pedidos_cadastrados, name='pedidos_cadastrados'),

    path("pedido/pagar/<int:pedido_id>/", views.marcar_pago, name="marcar_pago"),

]
