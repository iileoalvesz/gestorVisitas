"""
Aplicação Web Flask - Sistema de Gestão de Visitas às Escolas
"""
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

from escolas import GerenciadorEscolas
from visitas import GerenciadorVisitas
from distancias import CalculadorDistancias
from relatorios import GeradorRelatorios
from mediadores import GerenciadorMediadores
from planejamento import GerenciadorPlanejamentos
from usuarios import GerenciadorUsuarios

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
CORS(app)

# Configuracao de autenticacao
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faca login para acessar esta pagina.'
login_manager.login_message_category = 'warning'

# Inicializa gerenciadores
gerenciador_escolas = GerenciadorEscolas()
gerenciador_visitas = GerenciadorVisitas()
gerenciador_mediadores = GerenciadorMediadores()
gerenciador_planejamentos = GerenciadorPlanejamentos()
calculador_distancias = CalculadorDistancias()
gerador_relatorios = GeradorRelatorios()
gerenciador_usuarios = GerenciadorUsuarios()
gerenciador_usuarios.inicializar_admin()

# Configurações
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}


def allowed_file(filename):
    """Verifica se arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== AUTENTICACAO ====================

@login_manager.user_loader
def load_user(user_id):
    return gerenciador_usuarios.obter_por_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """Retorna 401 para APIs, redireciona para login para paginas"""
    if request.path.startswith('/api/'):
        return jsonify({'erro': 'Autenticacao necessaria'}), 401
    return redirect(url_for('login', next=request.url))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina de login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('password', '')
        lembrar = request.form.get('lembrar') == 'on'

        usuario = gerenciador_usuarios.obter_por_username(username)

        if usuario and usuario.verificar_senha(senha):
            login_user(usuario, remember=lembrar)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario ou senha invalidos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout do usuario"""
    logout_user()
    flash('Voce saiu do sistema com sucesso.', 'success')
    return redirect(url_for('login'))


@app.route('/health')
def health():
    """Healthcheck endpoint (publico, sem autenticacao)"""
    return jsonify({'status': 'ok'}), 200


# ==================== ROTAS DE PÁGINAS ====================

@app.route('/')
@login_required
def index():
    """Página inicial / Dashboard"""
    stats = gerenciador_visitas.obter_estatisticas()
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()

    # Escolas sem visita
    visitas = gerenciador_visitas.listar_visitas()
    escolas_sem_visita = gerador_relatorios.listar_escolas_sem_visita(escolas_bloco1, visitas)

    return render_template('index.html',
                         stats=stats,
                         total_escolas=len(escolas_bloco1),
                         escolas_sem_visita=len(escolas_sem_visita))


@app.route('/escolas')
@login_required
def escolas():
    """Página de listagem de escolas"""
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    return render_template('escolas.html', escolas=escolas_bloco1)


@app.route('/visitas')
@login_required
def visitas():
    """Página de listagem de visitas"""
    todas_visitas = gerenciador_visitas.listar_visitas()
    return render_template('visitas.html', visitas=todas_visitas)


@app.route('/visitas/nova')
@login_required
def nova_visita():
    """Página para registrar nova visita"""
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    mediadores_ativos = gerenciador_mediadores.listar_mediadores(apenas_ativos=True)
    return render_template('nova_visita.html', escolas=escolas_bloco1, mediadores=mediadores_ativos)


@app.route('/visitas/<visita_id>')
@login_required
def detalhes_visita(visita_id):
    """Página de detalhes de uma visita"""
    visita = gerenciador_visitas.obter_visita(visita_id)
    if not visita:
        return "Visita não encontrada", 404
    return render_template('detalhes_visita.html', visita=visita)


@app.route('/distancias')
@login_required
def distancias():
    """Página de cálculo de distâncias"""
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    return render_template('distancias.html', escolas=escolas_bloco1)


@app.route('/relatorios')
@login_required
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html')


@app.route('/mapa')
@login_required
def mapa():
    """Página com mapa das escolas"""
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    # Filtra escolas com coordenadas
    escolas_com_coords = [e for e in escolas_bloco1 if 'latitude' in e and 'longitude' in e]
    return render_template('mapa.html', escolas=escolas_com_coords)


@app.route('/mediadores')
@login_required
def mediadores():
    """Página de gerenciamento de mediadores"""
    todos_mediadores = gerenciador_mediadores.listar_mediadores(apenas_ativos=False)
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    return render_template('mediadores.html', mediadores=todos_mediadores, escolas=escolas_bloco1)


@app.route('/agenda')
@app.route('/agenda/<data>')
@login_required
def agenda(data=None):
    """Pagina de agenda semanal para planejamento de visitas"""
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    mediadores_ativos = gerenciador_mediadores.listar_mediadores(apenas_ativos=True)
    return render_template('agenda.html', escolas=escolas_bloco1, mediadores=mediadores_ativos)


# ==================== API ENDPOINTS ====================

@app.route('/api/escolas')
@login_required
def api_escolas():
    """API: Lista escolas do Bloco 1"""
    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    return jsonify(escolas_bloco1)


@app.route('/api/escolas/<int:escola_id>')
@login_required
def api_escola_detalhes(escola_id):
    """API: Detalhes de uma escola"""
    for escola in gerenciador_escolas.escolas:
        if escola['id'] == escola_id:
            return jsonify(escola)
    return jsonify({'erro': 'Escola não encontrada'}), 404


@app.route('/api/escolas/<int:escola_id>', methods=['PUT'])
@login_required
def api_atualizar_escola(escola_id):
    """API: Atualiza dados de uma escola"""
    try:
        data = request.get_json()
        sucesso = gerenciador_escolas.atualizar_escola(
            escola_id,
            nome_oficial=data.get('nome_oficial'),
            nome_usual=data.get('nome_usual'),
            diretor=data.get('diretor')
        )
        if sucesso:
            escola = gerenciador_escolas.obter_escola(escola_id)
            return jsonify(escola)
        return jsonify({'erro': 'Escola não encontrada'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/escolas/geocodificar', methods=['POST'])
@login_required
def api_geocodificar_escolas():
    """API: Geocodifica escolas sem coordenadas"""
    try:
        escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
        sem_coords = [e for e in escolas_bloco1 if 'latitude' not in e or 'longitude' not in e]

        if not sem_coords:
            return jsonify({'mensagem': 'Todas as escolas ja possuem coordenadas', 'total': 0})

        sucesso = 0
        falha = 0
        for escola in sem_coords:
            coords = gerenciador_escolas.obter_coordenadas(escola)
            if coords:
                sucesso += 1
            else:
                falha += 1

        return jsonify({
            'mensagem': f'Geocodificacao concluida: {sucesso} encontradas, {falha} nao encontradas',
            'sucesso': sucesso,
            'falha': falha,
            'total': sucesso + falha
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/escolas', methods=['POST'])
@login_required
def api_criar_escola():
    """API: Cria nova escola"""
    try:
        data = request.get_json()
        nome_oficial = data.get('nome_oficial')
        nome_usual = data.get('nome_usual')
        diretor = data.get('diretor', '')

        if not nome_oficial or not nome_usual:
            return jsonify({'erro': 'Nome oficial e nome usual são obrigatórios'}), 400

        escola = gerenciador_escolas.adicionar_escola(nome_oficial, nome_usual, diretor)
        return jsonify(escola), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/visitas', methods=['GET'])
@login_required
def api_visitas():
    """API: Lista visitas com filtros opcionais"""
    escola_id = request.args.get('escola_id', type=int)
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    visitas = gerenciador_visitas.listar_visitas(escola_id, data_inicio, data_fim)
    return jsonify(visitas)


@app.route('/api/visitas', methods=['POST'])
@login_required
def api_criar_visita():
    """API: Cria nova visita"""
    try:
        data = request.form
        escola_id = int(data.get('escola_id'))

        # Busca escola
        escola = None
        for e in gerenciador_escolas.escolas:
            if e['id'] == escola_id:
                escola = e
                break

        if not escola:
            return jsonify({'erro': 'Escola não encontrada'}), 404

        # Busca mediador se fornecido
        mediador_id = None
        mediador_nome = ""
        if data.get('mediador_id'):
            mediador_id = int(data.get('mediador_id'))
            mediador = gerenciador_mediadores.obter_mediador(mediador_id)
            if mediador:
                mediador_nome = mediador['nome']

        # Processa anexos
        anexos_paths = []
        if 'anexos' in request.files:
            files = request.files.getlist('anexos')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(filepath)
                    anexos_paths.append(filepath)

        # Registra visita
        visita = gerenciador_visitas.registrar_visita(
            escola_id=escola_id,
            escola_nome=escola['nome_usual'],
            data=data.get('data') if data.get('data') else None,
            observacoes=data.get('observacoes', ''),
            anexos=anexos_paths if anexos_paths else None,
            mediador_id=mediador_id,
            mediador_nome=mediador_nome
        )

        return jsonify(visita), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/visitas/<visita_id>')
@login_required
def api_visita_detalhes(visita_id):
    """API: Detalhes de uma visita"""
    visita = gerenciador_visitas.obter_visita(visita_id)
    if visita:
        return jsonify(visita)
    return jsonify({'erro': 'Visita não encontrada'}), 404


@app.route('/api/distancia', methods=['POST'])
@login_required
def api_calcular_distancia():
    """API: Calcula distância entre duas escolas"""
    try:
        data = request.get_json()
        escola1_id = data.get('escola1_id')
        escola2_id = data.get('escola2_id')

        # Busca escolas
        escola1 = None
        escola2 = None
        for e in gerenciador_escolas.escolas:
            if e['id'] == escola1_id:
                escola1 = e
            if e['id'] == escola2_id:
                escola2 = e

        if not escola1 or not escola2:
            return jsonify({'erro': 'Uma ou mais escolas não encontradas'}), 404

        if 'latitude' not in escola1 or 'latitude' not in escola2:
            return jsonify({'erro': 'Uma ou mais escolas sem coordenadas'}), 400

        coords1 = (escola1['latitude'], escola1['longitude'])
        coords2 = (escola2['latitude'], escola2['longitude'])

        rota = calculador_distancias.calcular_distancia(coords1, coords2)

        if rota:
            return jsonify({
                'escola1': escola1['nome_usual'],
                'escola2': escola2['nome_usual'],
                'distancia_km': rota['distancia_km'],
                'duracao_minutos': rota['duracao_minutos']
            })
        else:
            return jsonify({'erro': 'Erro ao calcular rota'}), 500

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/escolas/<int:escola_id>/proximas')
@login_required
def api_escolas_proximas(escola_id):
    """API: Escolas próximas a uma escola"""
    try:
        # Busca escola de referência
        escola_ref = None
        for e in gerenciador_escolas.escolas:
            if e['id'] == escola_id:
                escola_ref = e
                break

        if not escola_ref:
            return jsonify({'erro': 'Escola não encontrada'}), 404

        if 'latitude' not in escola_ref:
            return jsonify({'erro': 'Escola sem coordenadas'}), 400

        escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
        limite = request.args.get('limite', default=5, type=int)

        proximas = calculador_distancias.encontrar_escolas_proximas(
            escola_ref, escolas_bloco1, limite
        )

        return jsonify(proximas)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/estatisticas')
@login_required
def api_estatisticas():
    """API: Estatísticas gerais"""
    stats = gerenciador_visitas.obter_estatisticas()
    return jsonify(stats)


@app.route('/api/mediadores', methods=['GET'])
@login_required
def api_mediadores():
    """API: Lista mediadores"""
    apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
    mediadores = gerenciador_mediadores.listar_mediadores(apenas_ativos)
    return jsonify(mediadores)


@app.route('/api/mediadores', methods=['POST'])
@login_required
def api_criar_mediador():
    """API: Cria novo mediador"""
    try:
        data = request.get_json()
        nome = data.get('nome')

        if not nome:
            return jsonify({'erro': 'Nome é obrigatório'}), 400

        # Busca escola se fornecida
        escola_id = data.get('escola_id')
        escola_nome = ""
        if escola_id:
            for e in gerenciador_escolas.escolas:
                if e['id'] == escola_id:
                    escola_nome = e['nome_usual']
                    break

        mediador = gerenciador_mediadores.adicionar_mediador(
            nome=nome,
            cargo=data.get('cargo', ''),
            telefone=data.get('telefone', ''),
            email=data.get('email', ''),
            escola_id=escola_id,
            escola_nome=escola_nome
        )

        return jsonify(mediador), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/mediadores/<int:mediador_id>', methods=['PUT'])
@login_required
def api_atualizar_mediador(mediador_id):
    """API: Atualiza mediador"""
    try:
        data = request.get_json()

        # Busca escola se fornecida
        escola_id = data.get('escola_id')
        escola_nome = ""
        if escola_id:
            for e in gerenciador_escolas.escolas:
                if e['id'] == escola_id:
                    escola_nome = e['nome_usual']
                    break

        sucesso = gerenciador_mediadores.atualizar_mediador(
            mediador_id=mediador_id,
            nome=data.get('nome'),
            cargo=data.get('cargo'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            escola_id=escola_id,
            escola_nome=escola_nome if escola_id else None
        )

        if sucesso:
            mediador = gerenciador_mediadores.obter_mediador(mediador_id)
            return jsonify(mediador)
        else:
            return jsonify({'erro': 'Mediador não encontrado'}), 404

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/relatorios/excel', methods=['POST'])
@login_required
def api_gerar_relatorio_excel():
    """API: Gera relatório Excel"""
    try:
        data = request.get_json()
        escola_id = data.get('escola_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        visitas = gerenciador_visitas.listar_visitas(escola_id, data_inicio, data_fim)

        if not visitas:
            return jsonify({'erro': 'Nenhuma visita encontrada'}), 404

        arquivo = gerador_relatorios.gerar_relatorio_excel(visitas)

        return send_file(arquivo, as_attachment=True,
                        download_name=os.path.basename(arquivo))

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/relatorios/texto', methods=['POST'])
@login_required
def api_gerar_relatorio_texto():
    """API: Gera relatório em texto"""
    try:
        data = request.get_json()
        escola_id = data.get('escola_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        visitas = gerenciador_visitas.listar_visitas(escola_id, data_inicio, data_fim)

        if not visitas:
            return jsonify({'erro': 'Nenhuma visita encontrada'}), 404

        relatorio = gerador_relatorios.gerar_relatorio_texto(visitas)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = gerador_relatorios.salvar_relatorio_texto(
            relatorio, f"relatorio_{timestamp}.txt"
        )

        return send_file(arquivo, as_attachment=True,
                        download_name=os.path.basename(arquivo))

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/relatorios/word', methods=['POST'])
@login_required
def api_gerar_relatorio_word():
    """API: Gera relatório em Word"""
    try:
        data = request.get_json()
        escola_id = data.get('escola_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        visitas = gerenciador_visitas.listar_visitas(escola_id, data_inicio, data_fim)

        if not visitas:
            return jsonify({'erro': 'Nenhuma visita encontrada'}), 404

        arquivo = gerador_relatorios.gerar_relatorio_word(visitas)

        return send_file(arquivo, as_attachment=True,
                        download_name=os.path.basename(arquivo))

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/relatorios/consolidado', methods=['POST'])
@login_required
def api_gerar_relatorio_consolidado():
    """API: Gera relatório consolidado com fotos"""
    try:
        data = request.get_json()
        escola_id = data.get('escola_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        visitas = gerenciador_visitas.listar_visitas(escola_id, data_inicio, data_fim)

        if not visitas:
            return jsonify({'erro': 'Nenhuma visita encontrada'}), 404

        # Verifica se há template personalizado
        template_path = os.path.join('Downloads', 'RelatorioConsolidado.docx')
        if not os.path.exists(template_path):
            template_path = None

        arquivo = gerador_relatorios.gerar_relatorio_consolidado(
            visitas,
            arquivo_template=template_path
        )

        return send_file(arquivo, as_attachment=True,
                        download_name=os.path.basename(arquivo))

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/relatorios/folha-oficinas', methods=['POST'])
@login_required
def api_gerar_folha_oficinas():
    """API: Gera Folha de Acompanhamento de Oficinas"""
    try:
        data = request.get_json()
        escola_id = data.get('escola_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        visitas = gerenciador_visitas.listar_visitas(escola_id, data_inicio, data_fim)

        if not visitas:
            return jsonify({'erro': 'Nenhuma visita encontrada'}), 404

        arquivo = gerador_relatorios.gerar_folha_oficinas(visitas)

        return send_file(arquivo, as_attachment=True,
                        download_name=os.path.basename(arquivo))

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ==================== API - AGENDA/EVENTOS ====================

@app.route('/api/agenda/eventos', methods=['GET'])
@login_required
def api_listar_eventos():
    """API: Lista todos os eventos com filtros"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    eventos = gerenciador_planejamentos.listar_planejamentos(data_inicio, data_fim)
    return jsonify(eventos)


@app.route('/api/agenda/eventos', methods=['POST'])
@login_required
def api_criar_evento():
    """API: Cria novo evento"""
    try:
        data = request.get_json()

        # Busca nome da escola se for visita/apresentacao
        escola_nome = data.get('escola_nome', '')
        if not escola_nome and data.get('escola_id'):
            for e in gerenciador_escolas.escolas:
                if e['id'] == data['escola_id']:
                    escola_nome = e['nome_usual']
                    break

        # Busca nome do mediador se fornecido
        mediador_nome = data.get('mediador_nome', '')
        if not mediador_nome and data.get('mediador_id'):
            mediador = gerenciador_mediadores.obter_mediador(data['mediador_id'])
            if mediador:
                mediador_nome = mediador['nome']

        evento = gerenciador_planejamentos.adicionar_evento(
            tipo=data.get('tipo', 'outro'),
            titulo=data.get('titulo', ''),
            data=data['data'],
            hora_inicio=data.get('hora_inicio'),
            hora_fim=data.get('hora_fim'),
            turno=data.get('turno'),
            escola_id=data.get('escola_id'),
            escola_nome=escola_nome,
            local=data.get('local', ''),
            descricao=data.get('descricao', ''),
            mediador_id=data.get('mediador_id'),
            mediador_nome=mediador_nome,
            dia_inteiro=data.get('dia_inteiro', False)
        )

        return jsonify(evento), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/agenda/eventos/<evento_id>', methods=['GET'])
@login_required
def api_obter_evento(evento_id):
    """API: Obtem detalhes de um evento"""
    evento = gerenciador_planejamentos.obter_evento(evento_id)
    if evento:
        return jsonify(evento)
    return jsonify({'erro': 'Evento nao encontrado'}), 404


@app.route('/api/agenda/eventos/<evento_id>', methods=['PUT'])
@login_required
def api_atualizar_evento(evento_id):
    """API: Atualiza evento"""
    try:
        data = request.get_json()

        # Busca nome da escola se alterou
        if data.get('escola_id') and not data.get('escola_nome'):
            for e in gerenciador_escolas.escolas:
                if e['id'] == data['escola_id']:
                    data['escola_nome'] = e['nome_usual']
                    break

        sucesso = gerenciador_planejamentos.atualizar_evento(evento_id, **data)

        if sucesso:
            evento = gerenciador_planejamentos.obter_evento(evento_id)
            return jsonify(evento)
        return jsonify({'erro': 'Evento nao encontrado'}), 404

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/agenda/eventos/<evento_id>', methods=['DELETE'])
@login_required
def api_remover_evento(evento_id):
    """API: Remove evento"""
    sucesso = gerenciador_planejamentos.remover_evento(evento_id)
    if sucesso:
        return jsonify({'mensagem': 'Evento removido com sucesso'})
    return jsonify({'erro': 'Evento nao encontrado'}), 404


@app.route('/api/agenda/eventos/<evento_id>/mover', methods=['PUT'])
@login_required
def api_mover_evento(evento_id):
    """API: Move evento para outra data"""
    try:
        data = request.get_json()
        sucesso = gerenciador_planejamentos.mover_evento(
            evento_id,
            nova_data=data['data'],
            nova_hora_inicio=data.get('hora_inicio')
        )

        if sucesso:
            return jsonify({'mensagem': 'Evento movido com sucesso'})
        return jsonify({'erro': 'Evento nao encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/agenda/eventos/<evento_id>/executar', methods=['POST'])
@login_required
def api_executar_evento(evento_id):
    """API: Marca evento como executado"""
    sucesso = gerenciador_planejamentos.marcar_executado(evento_id)
    if sucesso:
        return jsonify({'mensagem': 'Evento marcado como executado'})
    return jsonify({'erro': 'Evento nao encontrado'}), 404


@app.route('/api/agenda/eventos/executar-visita', methods=['POST'])
@login_required
def api_executar_visita():
    """API: Executa visita com anexo obrigatorio e registra na tabela de visitas"""
    try:
        evento_id = request.form.get('evento_id')
        observacoes = request.form.get('observacoes', '')

        # Busca o evento
        evento = gerenciador_planejamentos.obter_evento(evento_id)
        if not evento:
            return jsonify({'erro': 'Evento nao encontrado'}), 404

        if evento.get('tipo') != 'visita':
            return jsonify({'erro': 'Este evento nao e uma visita'}), 400

        # Verifica anexo obrigatorio
        if 'anexos' not in request.files:
            return jsonify({'erro': 'Anexo e obrigatorio'}), 400

        files = request.files.getlist('anexos')
        if not files or not files[0].filename:
            return jsonify({'erro': 'Anexo e obrigatorio'}), 400

        # Processa anexos
        anexos_paths = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                anexos_paths.append(filepath)

        if not anexos_paths:
            return jsonify({'erro': 'Nenhum anexo valido foi enviado'}), 400

        # Registra visita na tabela de visitas
        visita = gerenciador_visitas.registrar_visita(
            escola_id=evento.get('escola_id'),
            escola_nome=evento.get('escola_nome', ''),
            data=evento.get('data'),
            observacoes=observacoes if observacoes else evento.get('descricao', ''),
            anexos=anexos_paths,
            mediador_id=evento.get('mediador_id'),
            mediador_nome=evento.get('mediador_nome', '')
        )

        # Marca evento como executado
        gerenciador_planejamentos.marcar_executado(evento_id)

        return jsonify({
            'mensagem': 'Visita executada e registrada com sucesso',
            'visita_id': visita.get('id'),
            'evento_id': evento_id
        })

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/agenda/eventos/<evento_id>/cancelar', methods=['POST'])
@login_required
def api_cancelar_evento(evento_id):
    """API: Cancela evento"""
    sucesso = gerenciador_planejamentos.cancelar_evento(evento_id)
    if sucesso:
        return jsonify({'mensagem': 'Evento cancelado'})
    return jsonify({'erro': 'Evento nao encontrado'}), 404


@app.route('/api/agenda/eventos/<evento_id>/duplicar', methods=['POST'])
@login_required
def api_duplicar_evento(evento_id):
    """API: Duplica evento para outra data"""
    try:
        data = request.get_json()
        evento = gerenciador_planejamentos.duplicar_evento(evento_id, data['data'])
        if evento:
            return jsonify(evento), 201
        return jsonify({'erro': 'Evento nao encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/agenda/semana', methods=['GET'])
@login_required
def api_agenda_semana():
    """API: Obtem eventos da semana"""
    data = request.args.get('data')
    semana = gerenciador_planejamentos.listar_eventos_semana(data)
    return jsonify(semana)


@app.route('/api/agenda/mes', methods=['GET'])
@login_required
def api_agenda_mes():
    """API: Obtem eventos do mes"""
    ano = request.args.get('ano', type=int)
    mes = request.args.get('mes', type=int)
    dados_mes = gerenciador_planejamentos.listar_eventos_mes(ano, mes)
    return jsonify(dados_mes)


@app.route('/api/agenda/mes/estatisticas', methods=['GET'])
@login_required
def api_estatisticas_mes():
    """API: Estatisticas do mes"""
    ano = request.args.get('ano', type=int)
    mes = request.args.get('mes', type=int)
    stats = gerenciador_planejamentos.obter_estatisticas_mes(ano, mes)
    return jsonify(stats)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    """Página 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Página 500"""
    return render_template('500.html'), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    # Cria pastas necessárias
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('anexos', exist_ok=True)
    os.makedirs('relatorios', exist_ok=True)

    # Inicia servidor
    print("\n" + "=" * 60)
    print(" SISTEMA DE GESTAO DE VISITAS AS ESCOLAS ".center(60))
    print(" Aplicacao Web - Flask ".center(60))
    print("=" * 60)
    print("\nServidor iniciado!")
    print("Acesse: http://localhost:5000")
    print("\nPressione CTRL+C para encerrar\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
