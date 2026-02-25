"""
Views Django - Sistema de Gestão de Visitas às Escolas
"""
import json
import os
import shutil
from datetime import datetime, timedelta, date
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.conf import settings
from werkzeug.utils import secure_filename

from .models import Escola, Mediador, Visita, TurmaVisita, AnexoVisita, Evento, Usuario
from distancias import CalculadorDistancias
from relatorios import GeradorRelatorios
from escolas import GerenciadorEscolas as _GerEscolas  # só para geocoding

calculador_distancias = CalculadorDistancias()
gerador_relatorios = GeradorRelatorios()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _bloco1_or_manual_qs():
    from django.db.models import Q
    return Escola.objects.filter(ativo=True).filter(
        Q(bloco_1=True) | Q(origem='manual')
    ).order_by('nome_oficial')


def _obter_coords_escola(escola_obj):
    """Geocodifica uma escola usando o módulo escolas.py"""
    escola_dict = escola_obj.to_dict()
    ge = _GerEscolas.__new__(_GerEscolas)
    ge.escolas = []
    coords = ge.obter_coordenadas(escola_dict)
    if coords:
        escola_obj.latitude = coords[0]
        escola_obj.longitude = coords[1]
        escola_obj.save(update_fields=['latitude', 'longitude'])
        return True
    return False


# ==================== AUTENTICACAO ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        senha = request.POST.get('password', '')
        lembrar = request.POST.get('lembrar') == 'on'

        user = authenticate(request, username=username, password=senha)
        if user and user.ativo:
            login(request, user)
            if not lembrar:
                request.session.set_expiry(0)
            next_page = request.GET.get('next', '/')
            return redirect(next_page)
        else:
            error = 'Usuário ou senha inválidos.'

    return render(request, 'login.html', {'error': error})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def health_check(request):
    return JsonResponse({'status': 'ok'})


# ==================== PÁGINAS ====================

@login_required
def index(request):
    from django.db.models import Count
    total_escolas = Escola.objects.filter(bloco_1=True, ativo=True).count()
    total_visitas = Visita.objects.count()
    escolas_visitadas_ids = Visita.objects.values_list('escola_id', flat=True).distinct()
    total_escolas_visitadas = len(set(escolas_visitadas_ids))
    escolas_sem_visita = total_escolas - total_escolas_visitadas

    escola_mais = (
        Visita.objects.values('escola_nome')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )

    stats = {
        'total_visitas': total_visitas,
        'total_escolas_visitadas': total_escolas_visitadas,
        'escola_mais_visitada': escola_mais['escola_nome'] if escola_mais else None,
        'max_visitas_escola': escola_mais['total'] if escola_mais else 0,
        'visitas_por_escola': {},
        'visitas_por_mes': {},
    }

    return render(request, 'index.html', {
        'stats': stats,
        'total_escolas': total_escolas,
        'escolas_sem_visita': max(0, escolas_sem_visita),
    })


@login_required
def escolas_view(request):
    escolas = list(_bloco1_or_manual_qs())
    return render(request, 'escolas.html', {'escolas': escolas})


@login_required
def visitas_view(request):
    visitas = list(Visita.objects.prefetch_related('turmas', 'anexos').order_by('-data'))
    return render(request, 'visitas.html', {'visitas': visitas})


@login_required
def nova_visita_view(request):
    escolas = list(_bloco1_or_manual_qs())
    return render(request, 'nova_visita.html', {'escolas': escolas})


@login_required
def detalhes_visita_view(request, visita_id):
    visita = get_object_or_404(Visita.objects.prefetch_related('turmas', 'anexos'), pk=visita_id)
    return render(request, 'detalhes_visita.html', {'visita': visita})


@login_required
def distancias_view(request):
    escolas = list(Escola.objects.filter(bloco_1=True, ativo=True).order_by('nome_oficial'))
    return render(request, 'distancias.html', {'escolas': escolas})


@login_required
def relatorios_view(request):
    return render(request, 'relatorios.html')


@login_required
def mapa_view(request):
    escolas = list(
        Escola.objects.filter(bloco_1=True, ativo=True)
        .exclude(latitude=None).exclude(longitude=None)
        .order_by('nome_oficial')
    )
    escolas_com_coords = [e.to_dict() for e in escolas]
    return render(request, 'mapa.html', {'escolas': escolas_com_coords})


@login_required
def agenda_view(request, data=None):
    escolas = list(_bloco1_or_manual_qs())
    return render(request, 'agenda.html', {'escolas': escolas})


# ==================== API - ESCOLAS ====================

@login_required
def api_escolas(request):
    if request.method == 'GET':
        escolas = _bloco1_or_manual_qs()
        return JsonResponse([e.to_dict() for e in escolas], safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome_oficial = data.get('nome_oficial', '').strip()
            nome_usual = data.get('nome_usual', '').strip()
            if not nome_oficial or not nome_usual:
                return JsonResponse({'erro': 'Nome oficial e nome usual são obrigatórios'}, status=400)

            escola = Escola.objects.create(
                nome_oficial=nome_oficial,
                nome_usual=nome_usual,
                diretor=data.get('diretor', ''),
                mediador=data.get('mediador', ''),
                endereco=data.get('endereco', ''),
                cep=data.get('cep', ''),
                origem='manual',
                bloco_1=bool(data.get('bloco_1', False)),
            )
            return JsonResponse(escola.to_dict(), status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def api_geocodificar_escolas(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        sem_coords = Escola.objects.filter(bloco_1=True, ativo=True).filter(
            latitude__isnull=True
        )
        if not sem_coords.exists():
            return JsonResponse({'mensagem': 'Todas as escolas já possuem coordenadas', 'total': 0})

        sucesso = 0
        falha = 0
        for escola in sem_coords:
            if _obter_coords_escola(escola):
                sucesso += 1
            else:
                falha += 1

        return JsonResponse({
            'mensagem': f'Geocodificação concluída: {sucesso} encontradas, {falha} não encontradas',
            'sucesso': sucesso,
            'falha': falha,
            'total': sucesso + falha,
        })
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@login_required
def api_escola_detail(request, escola_id):
    try:
        escola = Escola.objects.get(pk=escola_id)
    except Escola.DoesNotExist:
        return JsonResponse({'erro': 'Escola não encontrada'}, status=404)

    if request.method == 'GET':
        return JsonResponse(escola.to_dict())

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if data.get('nome_oficial') is not None:
                escola.nome_oficial = data['nome_oficial']
            if data.get('nome_usual') is not None:
                escola.nome_usual = data['nome_usual']
            if data.get('diretor') is not None:
                escola.diretor = data['diretor']
            if data.get('mediador') is not None:
                escola.mediador = data['mediador']
            if data.get('endereco') is not None:
                escola.endereco = data['endereco']
            if data.get('cep') is not None:
                escola.cep = data['cep']
            if data.get('bloco_1') is not None:
                escola.bloco_1 = bool(data['bloco_1'])
            escola.save()
            return JsonResponse(escola.to_dict())
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    elif request.method == 'DELETE':
        if escola.origem != 'manual':
            return JsonResponse({'erro': 'Escola não pode ser removida'}, status=404)
        escola.delete()
        return JsonResponse({'mensagem': 'Escola removida com sucesso'})

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def api_escolas_proximas(request, escola_id):
    try:
        escola_ref = get_object_or_404(Escola, pk=escola_id)
        if escola_ref.latitude is None:
            return JsonResponse({'erro': 'Escola sem coordenadas'}, status=400)

        limite = int(request.GET.get('limite', 5))
        escolas_bloco1 = [e.to_dict() for e in Escola.objects.filter(bloco_1=True, ativo=True)]
        proximas = calculador_distancias.encontrar_escolas_proximas(
            escola_ref.to_dict(), escolas_bloco1, limite
        )
        return JsonResponse(proximas, safe=False)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


# ==================== API - VISITAS ====================

@login_required
def api_visitas(request):
    if request.method == 'GET':
        escola_id = request.GET.get('escola_id')
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        qs = Visita.objects.prefetch_related('turmas', 'anexos').order_by('-data', '-criado_em')
        if escola_id:
            qs = qs.filter(escola_id=escola_id)
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__lte=data_fim)

        return JsonResponse([v.to_dict() for v in qs], safe=False)

    elif request.method == 'POST':
        try:
            escola_id = int(request.POST.get('escola_id'))
            escola = get_object_or_404(Escola, pk=escola_id)

            data_str = request.POST.get('data') or str(datetime.now().date())
            observacoes = request.POST.get('observacoes', '')
            mediador_nome = escola.mediador or ''

            visita = Visita.objects.create(
                escola=escola,
                escola_nome=escola.nome_usual,
                escola_nome_oficial=escola.nome_oficial,
                data=data_str,
                observacoes=observacoes,
                mediador_nome=mediador_nome,
            )

            # Processa anexos
            upload_dir = settings.MEDIA_ROOT
            os.makedirs(upload_dir, exist_ok=True)
            for f in request.FILES.getlist('anexos'):
                if f and _allowed_file(f.name):
                    filename = secure_filename(f.name)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_dir, filename)
                    with open(filepath, 'wb+') as dest:
                        for chunk in f.chunks():
                            dest.write(chunk)
                    ext = filename.rsplit('.', 1)[-1].lower()
                    tipo = 'foto' if ext in ('png', 'jpg', 'jpeg') else ext
                    AnexoVisita.objects.create(
                        visita=visita,
                        arquivo=f'uploads/{filename}',
                        tipo=tipo,
                        nome_original=f.name,
                    )

            return JsonResponse(visita.to_dict(), status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def api_visita_detail(request, visita_id):
    visita = get_object_or_404(Visita.objects.prefetch_related('turmas', 'anexos'), pk=visita_id)
    return JsonResponse(visita.to_dict())


# ==================== API - DISTÂNCIAS ====================

@login_required
def api_calcular_distancia(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        data = json.loads(request.body)
        escola1 = get_object_or_404(Escola, pk=data.get('escola1_id'))
        escola2 = get_object_or_404(Escola, pk=data.get('escola2_id'))

        if escola1.latitude is None or escola2.latitude is None:
            return JsonResponse({'erro': 'Uma ou mais escolas sem coordenadas'}, status=400)

        rota = calculador_distancias.calcular_distancia(
            (escola1.latitude, escola1.longitude),
            (escola2.latitude, escola2.longitude),
        )
        if rota:
            return JsonResponse({
                'escola1': escola1.nome_usual,
                'escola2': escola2.nome_usual,
                'distancia_km': rota['distancia_km'],
                'duracao_minutos': rota['duracao_minutos'],
            })
        return JsonResponse({'erro': 'Erro ao calcular rota'}, status=500)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


# ==================== API - ESTATÍSTICAS ====================

@login_required
def api_estatisticas(request):
    from django.db.models import Count
    total_visitas = Visita.objects.count()
    escolas_visitadas = Visita.objects.values('escola_id').distinct().count()

    escola_mais = (
        Visita.objects.values('escola_nome')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )

    return JsonResponse({
        'total_visitas': total_visitas,
        'total_escolas_visitadas': escolas_visitadas,
        'escola_mais_visitada': escola_mais['escola_nome'] if escola_mais else None,
        'max_visitas_escola': escola_mais['total'] if escola_mais else 0,
    })


# ==================== API - RELATÓRIOS ====================

@login_required
def api_relatorio_consolidado(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        data = json.loads(request.body)
        escola_id = data.get('escola_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        qs = Visita.objects.prefetch_related('turmas', 'anexos')
        if escola_id:
            qs = qs.filter(escola_id=escola_id)
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__lte=data_fim)

        visitas = [v.to_dict() for v in qs]
        if not visitas:
            return JsonResponse({'erro': 'Nenhuma visita encontrada'}, status=404)

        arquivo = gerador_relatorios.gerar_relatorio_consolidado(visitas)
        response = FileResponse(open(arquivo, 'rb'), as_attachment=True,
                                filename=os.path.basename(arquivo))
        return response
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@login_required
def api_folha_oficinas(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        data = json.loads(request.body)
        visita_id = data.get('visita_id')

        if visita_id:
            visita = get_object_or_404(
                Visita.objects.prefetch_related('turmas', 'anexos'), pk=visita_id
            )
            visitas = [visita.to_dict()]
        else:
            qs = Visita.objects.prefetch_related('turmas', 'anexos')
            if data.get('escola_id'):
                qs = qs.filter(escola_id=data['escola_id'])
            if data.get('data_inicio'):
                qs = qs.filter(data__gte=data['data_inicio'])
            if data.get('data_fim'):
                qs = qs.filter(data__lte=data['data_fim'])
            visitas = [v.to_dict() for v in qs]

        if not visitas:
            return JsonResponse({'erro': 'Nenhuma visita encontrada'}, status=404)

        arquivo = gerador_relatorios.gerar_folha_oficinas(visitas)
        return FileResponse(open(arquivo, 'rb'), as_attachment=True,
                            filename=os.path.basename(arquivo))
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


# ==================== API - AGENDA/EVENTOS ====================

def _evento_to_dict_semana(data_str):
    """Retorna lista de eventos de um dia"""
    eventos = Evento.objects.filter(data=data_str).order_by('hora_inicio', 'titulo')
    return [e.to_dict() for e in eventos]


@login_required
def api_agenda_semana(request):
    data_ref = request.GET.get('data')
    if data_ref:
        dt = datetime.strptime(data_ref, '%Y-%m-%d')
    else:
        dt = datetime.now()

    inicio = dt - timedelta(days=dt.weekday())
    fim = inicio + timedelta(days=6)

    eventos_semana = {}
    for i in range(7):
        dia = inicio + timedelta(days=i)
        data_str = dia.strftime('%Y-%m-%d')
        eventos_semana[data_str] = _evento_to_dict_semana(data_str)

    return JsonResponse({
        'semana_inicio': inicio.strftime('%Y-%m-%d'),
        'semana_fim': fim.strftime('%Y-%m-%d'),
        'eventos': eventos_semana,
    })


@login_required
def api_agenda_mes(request):
    try:
        ano = int(request.GET['ano'])
    except (KeyError, ValueError):
        ano = datetime.now().year
    try:
        mes = int(request.GET['mes'])
    except (KeyError, ValueError):
        mes = datetime.now().month

    primeiro_dia = datetime(ano, mes, 1)
    ultimo_dia_num = monthrange(ano, mes)[1]
    ultimo_dia = datetime(ano, mes, ultimo_dia_num)

    eventos_mes = {}
    for dia in range(1, ultimo_dia_num + 1):
        data_str = datetime(ano, mes, dia).strftime('%Y-%m-%d')
        eventos_dia = _evento_to_dict_semana(data_str)
        if eventos_dia:
            eventos_mes[data_str] = eventos_dia

    return JsonResponse({
        'ano': ano,
        'mes': mes,
        'nome_mes': primeiro_dia.strftime('%B'),
        'primeiro_dia': primeiro_dia.strftime('%Y-%m-%d'),
        'ultimo_dia': ultimo_dia.strftime('%Y-%m-%d'),
        'total_dias': ultimo_dia_num,
        'primeiro_dia_semana': primeiro_dia.weekday(),
        'eventos': eventos_mes,
        'total_eventos': sum(len(v) for v in eventos_mes.values()),
    })


@login_required
def api_agenda_mes_stats(request):
    try:
        ano = int(request.GET['ano'])
    except (KeyError, ValueError):
        ano = datetime.now().year
    try:
        mes = int(request.GET['mes'])
    except (KeyError, ValueError):
        mes = datetime.now().month

    qs = Evento.objects.filter(data__year=ano, data__month=mes)
    total = qs.count()
    por_tipo = {}
    por_status = {'planejado': 0, 'executado': 0, 'cancelado': 0}

    for e in qs:
        por_tipo[e.tipo] = por_tipo.get(e.tipo, 0) + 1
        if e.status in por_status:
            por_status[e.status] += 1

    return JsonResponse({'total': total, 'por_tipo': por_tipo, 'por_status': por_status})


@login_required
def api_eventos(request):
    if request.method == 'GET':
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        qs = Evento.objects.order_by('-data')
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__lte=data_fim)
        return JsonResponse([e.to_dict() for e in qs], safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Busca escola
            escola_obj = None
            escola_nome = data.get('escola_nome', '')
            mediador_nome = data.get('mediador_nome', '')
            if data.get('escola_id'):
                try:
                    escola_obj = Escola.objects.get(pk=data['escola_id'])
                    if not escola_nome:
                        escola_nome = escola_obj.nome_usual
                    if not mediador_nome:
                        mediador_nome = escola_obj.mediador or ''
                except Escola.DoesNotExist:
                    pass

            evento = Evento.objects.create(
                tipo=data.get('tipo', 'outro'),
                titulo=data.get('titulo', ''),
                data=date.fromisoformat(data['data']),
                hora_inicio=data.get('hora_inicio') or None,
                hora_fim=data.get('hora_fim') or None,
                turno=data.get('turno', ''),
                dia_inteiro=bool(data.get('dia_inteiro', False)),
                escola=escola_obj,
                escola_nome=escola_nome,
                local=data.get('local', ''),
                descricao=data.get('descricao', ''),
                mediador_nome=mediador_nome,
                status='planejado',
            )
            return JsonResponse(evento.to_dict(), status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def api_evento_detail(request, evento_id):
    try:
        evento = Evento.objects.get(pk=int(evento_id))
    except (Evento.DoesNotExist, ValueError):
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)

    if request.method == 'GET':
        return JsonResponse(evento.to_dict())

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            campos_diretos = ['tipo', 'titulo', 'data', 'hora_inicio', 'hora_fim',
                              'turno', 'dia_inteiro', 'escola_nome', 'local',
                              'descricao', 'mediador_nome', 'status']
            for campo in campos_diretos:
                if campo in data:
                    val = data[campo]
                    if campo in ('hora_inicio', 'hora_fim') and val == '':
                        val = None
                    elif campo == 'data' and isinstance(val, str):
                        val = date.fromisoformat(val)
                    setattr(evento, campo, val)
            if 'escola_id' in data and data['escola_id']:
                try:
                    escola_obj = Escola.objects.get(pk=data['escola_id'])
                    evento.escola = escola_obj
                    if not data.get('escola_nome'):
                        evento.escola_nome = escola_obj.nome_usual
                except Escola.DoesNotExist:
                    pass
            evento.save()
            return JsonResponse(evento.to_dict())
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    elif request.method == 'DELETE':
        evento.delete()
        return JsonResponse({'mensagem': 'Evento removido com sucesso'})

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def api_mover_evento(request, evento_id):
    if request.method != 'PUT':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        evento = Evento.objects.get(pk=int(evento_id))
        data = json.loads(request.body)
        evento.data = date.fromisoformat(data['data'])
        if data.get('hora_inicio'):
            evento.hora_inicio = data['hora_inicio']
        evento.save()
        return JsonResponse({'mensagem': 'Evento movido com sucesso'})
    except Evento.DoesNotExist:
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@login_required
def api_executar_evento(request, evento_id):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        evento = Evento.objects.get(pk=int(evento_id))
        evento.status = 'executado'
        evento.save()
        return JsonResponse({'mensagem': 'Evento marcado como executado'})
    except Evento.DoesNotExist:
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)


@login_required
def api_cancelar_evento(request, evento_id):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        evento = Evento.objects.get(pk=int(evento_id))
        evento.status = 'cancelado'
        evento.save()
        return JsonResponse({'mensagem': 'Evento cancelado'})
    except Evento.DoesNotExist:
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)


@login_required
def api_duplicar_evento(request, evento_id):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        original = Evento.objects.get(pk=int(evento_id))
        data = json.loads(request.body)
        novo = Evento.objects.create(
            tipo=original.tipo,
            titulo=original.titulo,
            data=date.fromisoformat(data['data']),
            hora_inicio=original.hora_inicio,
            hora_fim=original.hora_fim,
            turno=original.turno,
            dia_inteiro=original.dia_inteiro,
            escola=original.escola,
            escola_nome=original.escola_nome,
            local=original.local,
            descricao=original.descricao,
            mediador=original.mediador,
            mediador_nome=original.mediador_nome,
            status='planejado',
        )
        return JsonResponse(novo.to_dict(), status=201)
    except Evento.DoesNotExist:
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@login_required
def api_executar_visita(request):
    """Executa visita a partir da agenda: cria Visita + marca Evento como executado"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    try:
        evento_id = request.POST.get('evento_id')
        observacoes = request.POST.get('observacoes', '')
        contribuicoes = request.POST.get('contribuicoes', '')
        combinados = request.POST.get('combinados', '')
        oficina = request.POST.get('oficina', '')
        turno = request.POST.get('turno', '')

        evento = get_object_or_404(Evento, pk=int(evento_id))

        if evento.tipo != 'visita':
            return JsonResponse({'erro': 'Este evento não é uma visita'}, status=400)

        # Verifica anexo obrigatório
        files = request.FILES.getlist('anexos')
        if not files or not files[0].name:
            return JsonResponse({'erro': 'Anexo é obrigatório'}, status=400)

        # Busca escola
        escola_obj = evento.escola
        mediador_nome = escola_obj.mediador if escola_obj else ''
        gestor_nome = escola_obj.diretor if escola_obj else ''
        escola_nome_oficial = escola_obj.nome_oficial if escola_obj else ''
        articulador_nome = request.user.nome_exibicao if request.user.is_authenticated else ''

        # Processa turmas
        turmas_data = []
        try:
            turmas_data = json.loads(request.POST.get('turmas', '[]'))
        except (json.JSONDecodeError, TypeError):
            turmas_data = []

        # Cria visita
        visita = Visita.objects.create(
            escola=escola_obj,
            escola_nome=evento.escola_nome,
            escola_nome_oficial=escola_nome_oficial,
            data=evento.data,
            turno=turno,
            oficina=oficina,
            observacoes=observacoes or evento.descricao,
            contribuicoes=contribuicoes,
            combinados=combinados,
            mediador_nome=mediador_nome,
            articulador_nome=articulador_nome,
            gestor_nome=gestor_nome,
        )

        # Salva turmas
        for t in turmas_data:
            TurmaVisita.objects.create(
                visita=visita,
                nome_turma=t.get('turma', t.get('nome_turma', '')),
                quantidade=t.get('num_estudantes', t.get('quantidade')),
                nivel=t.get('tema', t.get('nivel', '')),
                avaliacao=t.get('avaliacao', ''),
                faixa_etaria=t.get('faixa_etaria', ''),
            )

        # Salva arquivos
        upload_dir = settings.MEDIA_ROOT
        os.makedirs(upload_dir, exist_ok=True)
        arquivos_salvos = []
        for f in files:
            if f and _allowed_file(f.name):
                filename = secure_filename(f.name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_dir, filename)
                with open(filepath, 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
                ext = filename.rsplit('.', 1)[-1].lower()
                tipo = 'foto' if ext in ('png', 'jpg', 'jpeg') else ext
                AnexoVisita.objects.create(
                    visita=visita,
                    arquivo=f'uploads/{filename}',
                    tipo=tipo,
                    nome_original=f.name,
                )
                arquivos_salvos.append(filename)

        if not arquivos_salvos:
            visita.delete()
            return JsonResponse({'erro': 'Nenhum anexo válido foi enviado'}, status=400)

        # Marca evento como executado
        evento.status = 'executado'
        evento.save()

        return JsonResponse({
            'mensagem': 'Visita executada e registrada com sucesso',
            'visita_id': visita.pk,
            'evento_id': evento.pk,
        })

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


# ==================== MEDIADORES ====================

@login_required
def mediadores_view(request):
    mediadores = Mediador.objects.all().order_by('nome')
    escolas = _bloco1_or_manual_qs().order_by('nome_usual')
    return render(request, 'mediadores.html', {
        'mediadores': mediadores,
        'escolas': escolas,
    })


@login_required
def api_mediadores(request):
    if request.method == 'GET':
        mediadores = Mediador.objects.all().order_by('nome')
        return JsonResponse([{
            'id': m.pk,
            'nome': m.nome,
            'escola_id': m.escola_id,
            'escola_nome': m.escola_nome or '',
            'ativo': m.ativo,
        } for m in mediadores], safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()
            if not nome:
                return JsonResponse({'erro': 'Nome é obrigatório'}, status=400)
            escola_id = data.get('escola_id')
            escola_nome = ''
            if escola_id:
                try:
                    escola = Escola.objects.get(pk=escola_id)
                    escola_nome = escola.nome_usual
                except Escola.DoesNotExist:
                    escola_id = None
            m = Mediador.objects.create(nome=nome, escola_id=escola_id, escola_nome=escola_nome)
            return JsonResponse({'id': m.pk, 'nome': m.nome, 'mensagem': 'Mediador criado'}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def api_mediador_detail(request, mediador_id):
    try:
        m = Mediador.objects.get(pk=mediador_id)
    except Mediador.DoesNotExist:
        return JsonResponse({'erro': 'Mediador não encontrado'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'id': m.pk, 'nome': m.nome, 'escola_id': m.escola_id, 'escola_nome': m.escola_nome, 'ativo': m.ativo})

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'nome' in data:
                m.nome = data['nome'].strip()
            escola_id = data.get('escola_id')
            if escola_id:
                try:
                    escola = Escola.objects.get(pk=escola_id)
                    m.escola_id = escola.pk
                    m.escola_nome = escola.nome_usual
                except Escola.DoesNotExist:
                    m.escola_id = None
                    m.escola_nome = ''
            else:
                m.escola_id = None
                m.escola_nome = ''
            if 'ativo' in data:
                m.ativo = bool(data['ativo'])
            m.save()
            return JsonResponse({'mensagem': 'Mediador atualizado'})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    if request.method == 'DELETE':
        m.delete()
        return JsonResponse({'mensagem': 'Mediador removido'})

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


# ==================== ERROR HANDLERS ====================

def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
