"""
Módulo para gerenciar visitas às escolas
"""
import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class GerenciadorVisitas:
    def __init__(self, arquivo_visitas: str = "data/visitas.json",
                 pasta_anexos: str = "anexos"):
        self.arquivo_visitas = arquivo_visitas
        self.pasta_anexos = pasta_anexos
        self.visitas = []
        self._carregar_visitas()

        # Cria pasta de anexos se não existir
        os.makedirs(pasta_anexos, exist_ok=True)

    def _carregar_visitas(self):
        """Carrega visitas do arquivo JSON"""
        if os.path.exists(self.arquivo_visitas):
            with open(self.arquivo_visitas, 'r', encoding='utf-8') as f:
                self.visitas = json.load(f)
        else:
            self.visitas = []
            self._salvar_visitas()

    def _salvar_visitas(self):
        """Salva visitas no arquivo JSON"""
        os.makedirs(os.path.dirname(self.arquivo_visitas), exist_ok=True)
        with open(self.arquivo_visitas, 'w', encoding='utf-8') as f:
            json.dump(self.visitas, f, ensure_ascii=False, indent=2)

    def _gerar_id_visita(self) -> str:
        """Gera ID único para visita baseado em timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        contador = len([v for v in self.visitas if v['id'].startswith(timestamp)])
        return f"{timestamp}_{contador + 1}"

    def _copiar_anexo(self, caminho_origem: str, id_visita: str) -> Optional[str]:
        """
        Copia arquivo de anexo para pasta do projeto

        Args:
            caminho_origem: Caminho do arquivo original
            id_visita: ID da visita

        Returns:
            Caminho relativo do arquivo copiado ou None em caso de erro
        """
        try:
            if not os.path.exists(caminho_origem):
                print(f"⚠️  Arquivo não encontrado: {caminho_origem}")
                return None

            # Cria subpasta para a visita
            pasta_visita = os.path.join(self.pasta_anexos, id_visita)
            os.makedirs(pasta_visita, exist_ok=True)

            # Copia arquivo mantendo o nome original
            nome_arquivo = os.path.basename(caminho_origem)
            caminho_destino = os.path.join(pasta_visita, nome_arquivo)

            shutil.copy2(caminho_origem, caminho_destino)

            # Retorna caminho relativo
            return os.path.join(id_visita, nome_arquivo)

        except Exception as e:
            print(f"Erro ao copiar anexo: {e}")
            return None

    def registrar_visita(self, escola_id: int, escola_nome: str,
                        data: Optional[str] = None,
                        observacoes: str = "",
                        anexos: Optional[List[str]] = None,
                        mediador_id: Optional[int] = None,
                        mediador_nome: str = "",
                        contribuicoes: str = "",
                        combinados: str = "",
                        oficina: str = "",
                        turno: str = "",
                        articulador_nome: str = "",
                        gestor_nome: str = "",
                        escola_nome_oficial: str = "",
                        turmas: Optional[List[Dict]] = None) -> Dict:
        """
        Registra uma nova visita

        Args:
            escola_id: ID da escola visitada
            escola_nome: Nome usual da escola
            data: Data da visita (formato: YYYY-MM-DD) ou None para hoje
            observacoes: Observações sobre a visita
            anexos: Lista de caminhos de arquivos para anexar
            mediador_id: ID do mediador (opcional, legado)
            mediador_nome: Nome do mediador/profissional
            contribuicoes: Contribuições/sugestões
            combinados: Combinados da visita
            oficina: Nome da oficina
            turno: Turno da visita
            articulador_nome: Nome do articulador (usuario logado)
            gestor_nome: Nome do gestor/diretor da escola
            escola_nome_oficial: Nome oficial da escola
            turmas: Lista de turmas com avaliacao [{turma, num_estudantes, tema, avaliacao}]

        Returns:
            Dicionário com dados da visita criada
        """
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")

        hora = datetime.now().strftime("%H:%M:%S")
        id_visita = self._gerar_id_visita()

        # Processa anexos
        anexos_copiados = []
        if anexos:
            print(f"\nCopiando {len(anexos)} anexo(s)...")
            for caminho in anexos:
                caminho_relativo = self._copiar_anexo(caminho, id_visita)
                if caminho_relativo:
                    anexos_copiados.append({
                        'caminho': caminho_relativo,
                        'nome_original': os.path.basename(caminho),
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"  ✓ {os.path.basename(caminho)}")

        visita = {
            'id': id_visita,
            'escola_id': escola_id,
            'escola_nome': escola_nome,
            'escola_nome_oficial': escola_nome_oficial,
            'data': data,
            'hora': hora,
            'turno': turno,
            'oficina': oficina,
            'observacoes': observacoes,
            'contribuicoes': contribuicoes,
            'combinados': combinados,
            'mediador_id': mediador_id,
            'mediador_nome': mediador_nome,
            'articulador_nome': articulador_nome,
            'gestor_nome': gestor_nome,
            'turmas': turmas or [],
            'anexos': anexos_copiados,
            'criado_em': datetime.now().isoformat()
        }

        self.visitas.append(visita)
        self._salvar_visitas()

        return visita

    def listar_visitas(self, escola_id: Optional[int] = None,
                      data_inicio: Optional[str] = None,
                      data_fim: Optional[str] = None) -> List[Dict]:
        """
        Lista visitas com filtros opcionais

        Args:
            escola_id: Filtrar por ID da escola
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)

        Returns:
            Lista de visitas filtradas
        """
        visitas_filtradas = self.visitas.copy()

        if escola_id is not None:
            visitas_filtradas = [v for v in visitas_filtradas if v['escola_id'] == escola_id]

        if data_inicio:
            visitas_filtradas = [v for v in visitas_filtradas if v['data'] >= data_inicio]

        if data_fim:
            visitas_filtradas = [v for v in visitas_filtradas if v['data'] <= data_fim]

        # Ordena por data e hora (mais recentes primeiro)
        visitas_filtradas.sort(key=lambda x: (x['data'], x['hora']), reverse=True)

        return visitas_filtradas

    def obter_visita(self, id_visita: str) -> Optional[Dict]:
        """Obtém uma visita específica pelo ID"""
        for visita in self.visitas:
            if visita['id'] == id_visita:
                return visita
        return None

    def adicionar_anexo_visita(self, id_visita: str, caminho_anexo: str) -> bool:
        """
        Adiciona anexo a uma visita existente

        Args:
            id_visita: ID da visita
            caminho_anexo: Caminho do arquivo a anexar

        Returns:
            True se sucesso, False caso contrário
        """
        visita = self.obter_visita(id_visita)

        if not visita:
            print(f"⚠️  Visita {id_visita} não encontrada")
            return False

        caminho_relativo = self._copiar_anexo(caminho_anexo, id_visita)

        if caminho_relativo:
            visita['anexos'].append({
                'caminho': caminho_relativo,
                'nome_original': os.path.basename(caminho_anexo),
                'timestamp': datetime.now().isoformat()
            })
            self._salvar_visitas()
            print(f"✓ Anexo adicionado: {os.path.basename(caminho_anexo)}")
            return True

        return False

    def atualizar_observacoes(self, id_visita: str, novas_observacoes: str) -> bool:
        """
        Atualiza observações de uma visita

        Args:
            id_visita: ID da visita
            novas_observacoes: Novas observações

        Returns:
            True se sucesso, False caso contrário
        """
        visita = self.obter_visita(id_visita)

        if visita:
            visita['observacoes'] = novas_observacoes
            visita['atualizado_em'] = datetime.now().isoformat()
            self._salvar_visitas()
            return True

        return False

    def excluir_visita(self, id_visita: str) -> bool:
        """
        Exclui uma visita e seus anexos

        Args:
            id_visita: ID da visita

        Returns:
            True se sucesso, False caso contrário
        """
        visita = self.obter_visita(id_visita)

        if not visita:
            return False

        # Remove pasta de anexos
        pasta_anexos_visita = os.path.join(self.pasta_anexos, id_visita)
        if os.path.exists(pasta_anexos_visita):
            shutil.rmtree(pasta_anexos_visita)

        # Remove visita da lista
        self.visitas = [v for v in self.visitas if v['id'] != id_visita]
        self._salvar_visitas()

        return True

    def obter_estatisticas(self) -> Dict:
        """
        Obtém estatísticas das visitas

        Returns:
            Dicionário com estatísticas
        """
        total_visitas = len(self.visitas)

        # Conta visitas por escola
        visitas_por_escola = {}
        for visita in self.visitas:
            escola_nome = visita['escola_nome']
            if escola_nome not in visitas_por_escola:
                visitas_por_escola[escola_nome] = 0
            visitas_por_escola[escola_nome] += 1

        # Escola mais visitada
        escola_mais_visitada = None
        max_visitas = 0
        for escola, count in visitas_por_escola.items():
            if count > max_visitas:
                max_visitas = count
                escola_mais_visitada = escola

        # Visitas por mês
        visitas_por_mes = {}
        for visita in self.visitas:
            mes = visita['data'][:7]  # YYYY-MM
            if mes not in visitas_por_mes:
                visitas_por_mes[mes] = 0
            visitas_por_mes[mes] += 1

        return {
            'total_visitas': total_visitas,
            'total_escolas_visitadas': len(visitas_por_escola),
            'escola_mais_visitada': escola_mais_visitada,
            'max_visitas_escola': max_visitas,
            'visitas_por_escola': visitas_por_escola,
            'visitas_por_mes': visitas_por_mes
        }
