"""
Management command: init_db
Inicializa o banco de dados com:
  1. Usuário admin padrão
  2. Escolas do Bloco 1 (dados hardcoded de escolas.py)
  3. Importa dados históricos dos JSONs legados (escolas, visitas, agenda)
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

# Importa dados hardcoded do módulo legado
import sys
sys.path.insert(0, str(settings.BASE_DIR))
from escolas import ESCOLAS_TAUBATE, BLOCO_1

from apps.core.models import Usuario, Escola, Mediador, Visita, TurmaVisita, AnexoVisita, Evento


DATA_DIR = settings.BASE_DIR / 'data'


class Command(BaseCommand):
    help = 'Inicializa o banco SQLite com dados padrão e importa histórico dos JSONs legados'

    def handle(self, *args, **options):
        self._criar_admin()
        self._popular_escolas()
        self._importar_escolas_json()
        self._importar_visitas_json()
        self._importar_agenda_json()
        self.stdout.write(self.style.SUCCESS('Banco de dados inicializado com sucesso.'))

    # ------------------------------------------------------------------

    def _criar_admin(self):
        if not Usuario.objects.filter(username='mileny_alves').exists():
            u = Usuario.objects.create_user(
                username='mileny_alves',
                password='M@2026',
                nome_exibicao='Mileny Alves',
                ativo=True,
            )
            u.is_staff = True
            u.save()
            self.stdout.write('  OK Usuário admin criado: mileny_alves')
        else:
            self.stdout.write('  - Usuário admin já existe.')

    # ------------------------------------------------------------------

    def _popular_escolas(self):
        """Cria escolas do Bloco 1 (dados hardcoded) se ainda não existem."""
        criadas = 0
        for dados in ESCOLAS_TAUBATE:
            nome_usual = dados.get('nome_usual', dados['nome_oficial'])
            is_bloco1 = nome_usual in BLOCO_1

            if not is_bloco1:
                continue  # popula apenas Bloco 1 por padrão

            if Escola.objects.filter(nome_oficial=dados['nome_oficial']).exists():
                continue

            Escola.objects.create(
                nome_oficial=dados['nome_oficial'],
                nome_usual=nome_usual,
                latitude=dados.get('latitude'),
                longitude=dados.get('longitude'),
                origem='sistema',
                bloco_1=True,
                ativo=True,
            )
            criadas += 1

        self.stdout.write(f'  OK {criadas} escolas do Bloco 1 criadas (hardcoded).')

    # ------------------------------------------------------------------

    def _importar_escolas_json(self):
        """Importa escolas extras do arquivo data/escolas.json (manuais / bloco_1 customizado)."""
        path = DATA_DIR / 'escolas.json'
        if not path.exists():
            return

        with open(path, 'r', encoding='utf-8') as f:
            try:
                escolas_json = json.load(f)
            except json.JSONDecodeError:
                return

        importadas = 0
        for e in escolas_json:
            nome_oficial = e.get('nome_oficial', '').strip()
            if not nome_oficial:
                continue
            if Escola.objects.filter(nome_oficial=nome_oficial).exists():
                # Atualiza campos extras que podem ter sido editados pelo usuário
                escola_obj = Escola.objects.get(nome_oficial=nome_oficial)
                changed = False
                for campo in ('diretor', 'mediador', 'endereco', 'cep', 'latitude', 'longitude'):
                    val = e.get(campo)
                    if val and not getattr(escola_obj, campo):
                        setattr(escola_obj, campo, val)
                        changed = True
                if e.get('bloco_1') and not escola_obj.bloco_1:
                    escola_obj.bloco_1 = True
                    changed = True
                if changed:
                    escola_obj.save()
                continue

            Escola.objects.create(
                nome_oficial=nome_oficial,
                nome_usual=e.get('nome_usual', nome_oficial),
                diretor=e.get('diretor', ''),
                mediador=e.get('mediador', ''),
                endereco=e.get('endereco', ''),
                cep=e.get('cep', ''),
                latitude=e.get('latitude'),
                longitude=e.get('longitude'),
                origem=e.get('origem', 'manual'),
                bloco_1=bool(e.get('bloco_1', False)),
                ativo=True,
            )
            importadas += 1

        self.stdout.write(f'  OK {importadas} escolas novas importadas de escolas.json.')

    # ------------------------------------------------------------------

    def _importar_visitas_json(self):
        path = DATA_DIR / 'visitas.json'
        if not path.exists():
            return

        with open(path, 'r', encoding='utf-8') as f:
            try:
                visitas_json = json.load(f)
            except json.JSONDecodeError:
                return

        importadas = 0
        for v in visitas_json:
            # Usa escola_nome como chave de dedup (visitas não têm id estável no Django)
            escola_nome = v.get('escola_nome', '')
            data_str = v.get('data', '')
            hora_str = v.get('hora', '')

            if not data_str:
                continue

            # Evita duplicata simples: mesma escola + data + hora
            if Visita.objects.filter(
                escola_nome=escola_nome, data=data_str
            ).exists():
                continue

            # Encontra objeto escola se possível
            escola_obj = None
            if v.get('escola_id'):
                escola_obj = Escola.objects.filter(pk=v['escola_id']).first()
            if not escola_obj and escola_nome:
                escola_obj = (
                    Escola.objects.filter(nome_usual=escola_nome).first() or
                    Escola.objects.filter(nome_oficial__icontains=escola_nome).first()
                )

            hora_time = None
            if hora_str:
                try:
                    hora_time = datetime.strptime(hora_str[:8], '%H:%M:%S').time()
                except ValueError:
                    pass

            visita_obj = Visita.objects.create(
                escola=escola_obj,
                escola_nome=escola_nome,
                escola_nome_oficial=v.get('escola_nome_oficial', ''),
                data=data_str,
                hora=hora_time,
                turno=v.get('turno', ''),
                oficina=v.get('oficina', ''),
                observacoes=v.get('observacoes', ''),
                contribuicoes=v.get('contribuicoes', ''),
                combinados=v.get('combinados', ''),
                mediador_nome=v.get('mediador_nome', ''),
                articulador_nome=v.get('articulador_nome', ''),
                gestor_nome=v.get('gestor_nome', ''),
            )

            for t in v.get('turmas', []):
                TurmaVisita.objects.create(
                    visita=visita_obj,
                    nome_turma=t.get('turma', t.get('nome_turma', '')),
                    quantidade=t.get('num_estudantes', t.get('quantidade')),
                    nivel=t.get('tema', t.get('nivel', '')),
                    avaliacao=t.get('avaliacao', ''),
                    faixa_etaria=t.get('faixa_etaria', ''),
                )

            for a in v.get('anexos', []):
                caminho = a.get('caminho', '')
                nome = a.get('nome_original', os.path.basename(caminho))
                ext = nome.rsplit('.', 1)[-1].lower() if '.' in nome else ''
                tipo = 'foto' if ext in ('png', 'jpg', 'jpeg') else ext
                AnexoVisita.objects.create(
                    visita=visita_obj,
                    arquivo=f'uploads/{os.path.basename(caminho)}' if caminho else '',
                    tipo=tipo,
                    nome_original=nome,
                )

            importadas += 1

        self.stdout.write(f'  OK {importadas} visitas importadas de visitas.json.')

    # ------------------------------------------------------------------

    def _importar_agenda_json(self):
        path = DATA_DIR / 'agenda.json'
        if not path.exists():
            return

        with open(path, 'r', encoding='utf-8') as f:
            try:
                eventos_json = json.load(f)
            except json.JSONDecodeError:
                return

        importados = 0
        for e in eventos_json:
            data_str = e.get('data', '')
            titulo = e.get('titulo', '')
            if not data_str or not titulo:
                continue

            if Evento.objects.filter(titulo=titulo, data=data_str).exists():
                continue

            escola_obj = None
            if e.get('escola_id'):
                escola_obj = Escola.objects.filter(pk=e['escola_id']).first()

            def _parse_time(val):
                if not val:
                    return None
                try:
                    return datetime.strptime(val[:5], '%H:%M').time()
                except ValueError:
                    return None

            Evento.objects.create(
                tipo=e.get('tipo', 'outro'),
                titulo=titulo,
                data=data_str,
                hora_inicio=_parse_time(e.get('hora_inicio')),
                hora_fim=_parse_time(e.get('hora_fim')),
                turno=e.get('turno', ''),
                dia_inteiro=bool(e.get('dia_inteiro', False)),
                escola=escola_obj,
                escola_nome=e.get('escola_nome', ''),
                local=e.get('local', ''),
                descricao=e.get('descricao', ''),
                mediador_nome=e.get('mediador_nome', ''),
                status=e.get('status', 'planejado'),
            )
            importados += 1

        self.stdout.write(f'  OK {importados} eventos importados de agenda.json.')
