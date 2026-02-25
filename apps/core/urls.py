from django.urls import path
from . import views

urlpatterns = [
    # Autenticacao
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('health', views.health_check, name='health'),

    # Paginas
    path('', views.index, name='index'),
    path('escolas', views.escolas_view, name='escolas'),
    path('visitas', views.visitas_view, name='visitas'),
    path('visitas/nova', views.nova_visita_view, name='nova_visita'),
    path('visitas/<int:visita_id>', views.detalhes_visita_view, name='detalhes_visita'),
    path('distancias', views.distancias_view, name='distancias'),
    path('relatorios', views.relatorios_view, name='relatorios'),
    path('mapa', views.mapa_view, name='mapa'),
    path('agenda', views.agenda_view, name='agenda'),
    path('agenda/<str:data>', views.agenda_view, name='agenda_data'),
    path('mediadores', views.mediadores_view, name='mediadores'),

    # API - Escolas
    path('api/escolas', views.api_escolas, name='api_escolas'),
    path('api/escolas/geocodificar', views.api_geocodificar_escolas, name='api_geocodificar_escolas'),
    path('api/escolas/<int:escola_id>', views.api_escola_detail, name='api_escola_detail'),
    path('api/escolas/<int:escola_id>/proximas', views.api_escolas_proximas, name='api_escolas_proximas'),

    # API - Visitas
    path('api/visitas', views.api_visitas, name='api_visitas'),
    path('api/visitas/<int:visita_id>', views.api_visita_detail, name='api_visita_detail'),

    # API - Distancias
    path('api/distancia', views.api_calcular_distancia, name='api_distancia'),

    # API - Estatisticas
    path('api/estatisticas', views.api_estatisticas, name='api_estatisticas'),

    # API - Relatorios
    path('api/relatorios/consolidado', views.api_relatorio_consolidado, name='api_relatorio_consolidado'),
    path('api/relatorios/folha-oficinas', views.api_folha_oficinas, name='api_folha_oficinas'),

    # API - Agenda
    path('api/agenda/semana', views.api_agenda_semana, name='api_agenda_semana'),
    path('api/agenda/mes', views.api_agenda_mes, name='api_agenda_mes'),
    path('api/agenda/mes/estatisticas', views.api_agenda_mes_stats, name='api_agenda_mes_stats'),
    path('api/agenda/eventos', views.api_eventos, name='api_eventos'),
    path('api/agenda/eventos/executar-visita', views.api_executar_visita, name='api_executar_visita'),
    path('api/agenda/eventos/<str:evento_id>', views.api_evento_detail, name='api_evento_detail'),
    path('api/agenda/eventos/<str:evento_id>/mover', views.api_mover_evento, name='api_mover_evento'),
    path('api/agenda/eventos/<str:evento_id>/executar', views.api_executar_evento, name='api_executar_evento'),
    path('api/agenda/eventos/<str:evento_id>/cancelar', views.api_cancelar_evento, name='api_cancelar_evento'),
    path('api/agenda/eventos/<str:evento_id>/duplicar', views.api_duplicar_evento, name='api_duplicar_evento'),

    # API - Mediadores
    path('api/mediadores', views.api_mediadores, name='api_mediadores'),
    path('api/mediadores/<int:mediador_id>', views.api_mediador_detail, name='api_mediador_detail'),
]
