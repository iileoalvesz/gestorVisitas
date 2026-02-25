from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Escola, Mediador, Visita, TurmaVisita, AnexoVisita, Evento


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Dados adicionais', {'fields': ('nome_exibicao', 'ativo')}),
    )


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ['nome_oficial', 'nome_usual', 'bloco_1', 'origem', 'ativo']
    list_filter = ['bloco_1', 'origem', 'ativo']
    search_fields = ['nome_oficial', 'nome_usual', 'diretor', 'mediador']


@admin.register(Mediador)
class MediadorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'escola_nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'escola_nome']


class TurmaInline(admin.TabularInline):
    model = TurmaVisita
    extra = 0


class AnexoInline(admin.TabularInline):
    model = AnexoVisita
    extra = 0


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['escola_nome', 'data', 'turno', 'mediador_nome', 'articulador_nome']
    list_filter = ['turno', 'data']
    search_fields = ['escola_nome', 'mediador_nome', 'articulador_nome']
    inlines = [TurmaInline, AnexoInline]


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'data', 'status', 'escola_nome', 'mediador_nome']
    list_filter = ['tipo', 'status', 'data']
    search_fields = ['titulo', 'escola_nome', 'mediador_nome']
