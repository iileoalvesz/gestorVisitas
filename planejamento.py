"""
Modulo para gerenciar agenda/planejamento de eventos
Sistema de agenda para organizar visitas, reunioes, feriados e outros eventos
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from calendar import monthrange


# Tipos de eventos disponiveis
TIPOS_EVENTO = {
    'visita': {'icone': 'bi-building', 'cor': '#f59e0b', 'label': 'Visita'},
    'reuniao': {'icone': 'bi-people', 'cor': '#3b82f6', 'label': 'Reuniao'},
    'feriado': {'icone': 'bi-calendar-x', 'cor': '#ef4444', 'label': 'Feriado'},
    'apresentacao': {'icone': 'bi-easel', 'cor': '#8b5cf6', 'label': 'Apresentacao'},
    'capacitacao': {'icone': 'bi-book', 'cor': '#10b981', 'label': 'Capacitacao'},
    'outro': {'icone': 'bi-calendar-event', 'cor': '#6b7280', 'label': 'Outro'}
}


class GerenciadorAgenda:
    """Gerencia agenda de eventos (visitas, reunioes, feriados, etc)"""

    def __init__(self, arquivo_dados: str = "data/agenda.json"):
        self.arquivo_dados = arquivo_dados
        self.eventos = []
        self._carregar_dados()

    def _carregar_dados(self):
        """Carrega eventos do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    self.eventos = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.eventos = []
        else:
            self.eventos = []
            self._salvar_dados()

    def _salvar_dados(self):
        """Salva eventos no arquivo JSON"""
        os.makedirs(os.path.dirname(self.arquivo_dados), exist_ok=True)
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.eventos, f, ensure_ascii=False, indent=2)

    def _recarregar_do_disco(self):
        """Recarrega eventos do JSON — necessario em ambientes multi-worker (Gunicorn)"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    self.eventos = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

    def _gerar_id(self) -> str:
        """Gera ID unico para evento"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"evt_{timestamp}"

    def adicionar_evento(self, tipo: str, titulo: str, data: str,
                         hora_inicio: str = None, hora_fim: str = None,
                         turno: str = None, escola_id: int = None,
                         escola_nome: str = "", local: str = "",
                         descricao: str = "", mediador_id: int = None,
                         mediador_nome: str = "", dia_inteiro: bool = False) -> Dict:
        """
        Adiciona um novo evento a agenda

        Args:
            tipo: Tipo do evento (visita, reuniao, feriado, apresentacao, capacitacao, outro)
            titulo: Titulo/nome do evento
            data: Data do evento (YYYY-MM-DD)
            hora_inicio: Hora de inicio (HH:MM) - opcional
            hora_fim: Hora de fim (HH:MM) - opcional
            turno: manha, tarde, integral - opcional (alternativa a hora)
            escola_id: ID da escola (para visitas/apresentacoes)
            escola_nome: Nome da escola
            local: Local do evento (para reunioes, etc)
            descricao: Descricao/observacoes
            mediador_id: ID do mediador responsavel
            mediador_nome: Nome do mediador
            dia_inteiro: Se e evento de dia inteiro (feriados)

        Returns:
            Dicionario do evento criado
        """
        dt_data = datetime.strptime(data, "%Y-%m-%d")

        evento = {
            'id': self._gerar_id(),
            'tipo': tipo,
            'titulo': titulo,
            'data': data,
            'dia_semana': dt_data.weekday(),
            'hora_inicio': hora_inicio,
            'hora_fim': hora_fim,
            'turno': turno,
            'dia_inteiro': dia_inteiro,
            'escola_id': escola_id,
            'escola_nome': escola_nome,
            'local': local,
            'descricao': descricao,
            'mediador_id': mediador_id,
            'mediador_nome': mediador_nome,
            'status': 'planejado',
            'criado_em': datetime.now().isoformat(),
            'atualizado_em': datetime.now().isoformat()
        }

        self.eventos.append(evento)
        self._salvar_dados()

        return evento

    def atualizar_evento(self, evento_id: str, **kwargs) -> bool:
        """
        Atualiza um evento existente

        Args:
            evento_id: ID do evento
            **kwargs: Campos a serem atualizados

        Returns:
            True se atualizado com sucesso
        """
        for evento in self.eventos:
            if evento['id'] == evento_id:
                for key, value in kwargs.items():
                    if key in evento:
                        evento[key] = value
                        # Atualiza dia_semana se data mudar
                        if key == 'data' and value:
                            dt = datetime.strptime(value, "%Y-%m-%d")
                            evento['dia_semana'] = dt.weekday()
                evento['atualizado_em'] = datetime.now().isoformat()
                self._salvar_dados()
                return True
        return False

    def remover_evento(self, evento_id: str) -> bool:
        """Remove um evento"""
        tamanho_original = len(self.eventos)
        self.eventos = [e for e in self.eventos if e['id'] != evento_id]
        if len(self.eventos) < tamanho_original:
            self._salvar_dados()
            return True
        return False

    def obter_evento(self, evento_id: str) -> Optional[Dict]:
        """Obtem um evento especifico"""
        for evento in self.eventos:
            if evento['id'] == evento_id:
                return evento
        return None

    def listar_eventos_dia(self, data: str) -> List[Dict]:
        """Lista eventos de um dia especifico"""
        eventos_dia = [e for e in self.eventos if e['data'] == data]
        # Ordena por hora de inicio
        eventos_dia.sort(key=lambda x: (x.get('hora_inicio') or '00:00', x.get('titulo', '')))
        return eventos_dia

    def listar_eventos_semana(self, data_referencia: str = None) -> Dict:
        """
        Lista eventos de uma semana

        Args:
            data_referencia: Qualquer data da semana (YYYY-MM-DD)

        Returns:
            Dicionario com informacoes da semana e eventos por dia
        """
        self._recarregar_do_disco()
        if data_referencia:
            dt = datetime.strptime(data_referencia, "%Y-%m-%d")
        else:
            dt = datetime.now()

        # Calcula segunda-feira da semana
        inicio = dt - timedelta(days=dt.weekday())
        fim = inicio + timedelta(days=6)  # Domingo

        # Coleta eventos da semana
        eventos_semana = {}
        for i in range(7):
            dia = inicio + timedelta(days=i)
            data_str = dia.strftime("%Y-%m-%d")
            eventos_semana[data_str] = self.listar_eventos_dia(data_str)

        return {
            'semana_inicio': inicio.strftime("%Y-%m-%d"),
            'semana_fim': fim.strftime("%Y-%m-%d"),
            'eventos': eventos_semana
        }

    def listar_eventos_mes(self, ano: int = None, mes: int = None) -> Dict:
        """
        Lista eventos de um mes

        Args:
            ano: Ano (default: atual)
            mes: Mes 1-12 (default: atual)

        Returns:
            Dicionario com informacoes do mes e eventos por dia
        """
        self._recarregar_do_disco()
        if ano is None:
            ano = datetime.now().year
        if mes is None:
            mes = datetime.now().month

        # Primeiro e ultimo dia do mes
        primeiro_dia = datetime(ano, mes, 1)
        ultimo_dia_num = monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_num)

        # Coleta eventos do mes
        eventos_mes = {}
        for dia in range(1, ultimo_dia_num + 1):
            data = datetime(ano, mes, dia)
            data_str = data.strftime("%Y-%m-%d")
            eventos_dia = self.listar_eventos_dia(data_str)
            if eventos_dia:  # Apenas dias com eventos
                eventos_mes[data_str] = eventos_dia

        # Calcula primeiro dia da semana do mes (para grid do calendario)
        primeiro_dia_semana = primeiro_dia.weekday()

        return {
            'ano': ano,
            'mes': mes,
            'nome_mes': primeiro_dia.strftime("%B"),
            'primeiro_dia': primeiro_dia.strftime("%Y-%m-%d"),
            'ultimo_dia': ultimo_dia.strftime("%Y-%m-%d"),
            'total_dias': ultimo_dia_num,
            'primeiro_dia_semana': primeiro_dia_semana,
            'eventos': eventos_mes,
            'total_eventos': sum(len(v) for v in eventos_mes.values())
        }

    def mover_evento(self, evento_id: str, nova_data: str,
                     nova_hora_inicio: str = None) -> bool:
        """Move evento para outra data/hora"""
        return self.atualizar_evento(
            evento_id,
            data=nova_data,
            hora_inicio=nova_hora_inicio
        )

    def marcar_executado(self, evento_id: str) -> bool:
        """Marca evento como executado/concluido"""
        return self.atualizar_evento(evento_id, status='executado')

    def cancelar_evento(self, evento_id: str) -> bool:
        """Cancela um evento"""
        return self.atualizar_evento(evento_id, status='cancelado')

    def obter_estatisticas_mes(self, ano: int = None, mes: int = None) -> Dict:
        """Retorna estatisticas do mes"""
        dados_mes = self.listar_eventos_mes(ano, mes)
        todos_eventos = []
        for eventos_dia in dados_mes['eventos'].values():
            todos_eventos.extend(eventos_dia)

        stats = {
            'total': len(todos_eventos),
            'por_tipo': {},
            'por_status': {
                'planejado': 0,
                'executado': 0,
                'cancelado': 0
            }
        }

        for evento in todos_eventos:
            # Por tipo
            tipo = evento.get('tipo', 'outro')
            stats['por_tipo'][tipo] = stats['por_tipo'].get(tipo, 0) + 1

            # Por status
            status = evento.get('status', 'planejado')
            if status in stats['por_status']:
                stats['por_status'][status] += 1

        return stats

    def duplicar_evento(self, evento_id: str, nova_data: str) -> Optional[Dict]:
        """Duplica um evento para outra data"""
        evento_original = self.obter_evento(evento_id)
        if not evento_original:
            return None

        return self.adicionar_evento(
            tipo=evento_original['tipo'],
            titulo=evento_original['titulo'],
            data=nova_data,
            hora_inicio=evento_original.get('hora_inicio'),
            hora_fim=evento_original.get('hora_fim'),
            turno=evento_original.get('turno'),
            escola_id=evento_original.get('escola_id'),
            escola_nome=evento_original.get('escola_nome', ''),
            local=evento_original.get('local', ''),
            descricao=evento_original.get('descricao', ''),
            mediador_id=evento_original.get('mediador_id'),
            mediador_nome=evento_original.get('mediador_nome', ''),
            dia_inteiro=evento_original.get('dia_inteiro', False)
        )


# Manter compatibilidade com codigo antigo
class GerenciadorPlanejamentos(GerenciadorAgenda):
    """Alias para compatibilidade - usar GerenciadorAgenda"""

    def __init__(self, arquivo_dados: str = "data/agenda.json"):
        super().__init__(arquivo_dados)

    def obter_ou_criar_planejamento_semana(self, data: str = None) -> Dict:
        """Compatibilidade: retorna eventos da semana"""
        return self.listar_eventos_semana(data)

    def adicionar_visita_planejada(self, planejamento_id: str = None, escola_id: int = None,
                                    escola_nome: str = "", data: str = None,
                                    turno: str = "manha", ordem: int = None,
                                    observacoes: str = "", mediador_id: int = None,
                                    mediador_nome: str = "") -> Optional[Dict]:
        """Compatibilidade: adiciona visita como evento"""
        return self.adicionar_evento(
            tipo='visita',
            titulo=escola_nome or 'Visita',
            data=data,
            turno=turno,
            escola_id=escola_id,
            escola_nome=escola_nome,
            descricao=observacoes,
            mediador_id=mediador_id,
            mediador_nome=mediador_nome
        )

    def atualizar_visita_planejada(self, planejamento_id: str, visita_id: str,
                                    **kwargs) -> bool:
        """Compatibilidade: atualiza evento"""
        return self.atualizar_evento(visita_id, **kwargs)

    def remover_visita_planejada(self, planejamento_id: str, visita_id: str) -> bool:
        """Compatibilidade: remove evento"""
        return self.remover_evento(visita_id)

    def mover_visita(self, planejamento_id: str, visita_id: str,
                     nova_data: str, nova_ordem: int = None) -> bool:
        """Compatibilidade: move evento"""
        return self.mover_evento(visita_id, nova_data)

    def cancelar_visita(self, planejamento_id: str, visita_id: str) -> bool:
        """Compatibilidade: cancela evento"""
        return self.cancelar_evento(visita_id)

    def obter_planejamento_semana(self, data: str) -> Optional[Dict]:
        """Compatibilidade: retorna eventos da semana"""
        return self.listar_eventos_semana(data)

    def obter_planejamento(self, planejamento_id: str) -> Optional[Dict]:
        """Compatibilidade: retorna eventos da semana atual"""
        return self.listar_eventos_semana()

    def listar_planejamentos(self, data_inicio: str = None,
                             data_fim: str = None) -> List[Dict]:
        """Compatibilidade: lista eventos"""
        self._recarregar_do_disco()
        resultado = self.eventos.copy()
        if data_inicio:
            resultado = [e for e in resultado if e['data'] >= data_inicio]
        if data_fim:
            resultado = [e for e in resultado if e['data'] <= data_fim]
        resultado.sort(key=lambda x: x['data'], reverse=True)
        return resultado

    def obter_estatisticas_semana(self, planejamento_id: str) -> Dict:
        """Compatibilidade: retorna estatisticas"""
        semana = self.listar_eventos_semana()
        todos_eventos = []
        for eventos_dia in semana['eventos'].values():
            todos_eventos.extend(eventos_dia)

        return {
            'total_planejadas': len(todos_eventos),
            'planejadas': len([e for e in todos_eventos if e['status'] == 'planejado']),
            'executadas': len([e for e in todos_eventos if e['status'] == 'executado']),
            'canceladas': len([e for e in todos_eventos if e['status'] == 'cancelado'])
        }
