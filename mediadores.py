"""
Módulo para gerenciar mediadores
"""
import json
import os
from typing import List, Dict, Optional


class GerenciadorMediadores:
    def __init__(self, arquivo_dados: str = "data/mediadores.json"):
        self.arquivo_dados = arquivo_dados
        self.mediadores = []
        self._carregar_dados()

    def _carregar_dados(self):
        """Carrega mediadores do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                self.mediadores = json.load(f)
        else:
            self.mediadores = []
            self._salvar_dados()

    def _salvar_dados(self):
        """Salva mediadores no arquivo JSON"""
        os.makedirs(os.path.dirname(self.arquivo_dados), exist_ok=True)
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.mediadores, f, ensure_ascii=False, indent=2)

    def _gerar_id(self) -> int:
        """Gera próximo ID disponível"""
        if not self.mediadores:
            return 1
        return max(m['id'] for m in self.mediadores) + 1

    def adicionar_mediador(self, nome: str, escola_id: int = None, escola_nome: str = "") -> Dict:
        """Adiciona novo mediador"""
        mediador = {
            'id': self._gerar_id(),
            'nome': nome,
            'escola_id': escola_id,
            'escola_nome': escola_nome,
            'ativo': True
        }

        self.mediadores.append(mediador)
        self._salvar_dados()
        return mediador

    def listar_mediadores(self, apenas_ativos: bool = True) -> List[Dict]:
        """Lista mediadores"""
        if apenas_ativos:
            return [m for m in self.mediadores if m.get('ativo', True)]
        return self.mediadores.copy()

    def obter_mediador(self, mediador_id: int) -> Optional[Dict]:
        """Obtém mediador por ID"""
        for mediador in self.mediadores:
            if mediador['id'] == mediador_id:
                return mediador
        return None

    def atualizar_mediador(self, mediador_id: int, nome: str = None,
                          escola_id: int = None, escola_nome: str = None) -> bool:
        """Atualiza dados de um mediador"""
        mediador = self.obter_mediador(mediador_id)
        if not mediador:
            return False

        if nome is not None:
            mediador['nome'] = nome
        if escola_id is not None:
            mediador['escola_id'] = escola_id
        if escola_nome is not None:
            mediador['escola_nome'] = escola_nome

        self._salvar_dados()
        return True

    def desativar_mediador(self, mediador_id: int) -> bool:
        """Desativa um mediador"""
        mediador = self.obter_mediador(mediador_id)
        if mediador:
            mediador['ativo'] = False
            self._salvar_dados()
            return True
        return False

    def reativar_mediador(self, mediador_id: int) -> bool:
        """Reativa um mediador"""
        mediador = self.obter_mediador(mediador_id)
        if mediador:
            mediador['ativo'] = True
            self._salvar_dados()
            return True
        return False

    def buscar_mediador(self, termo: str) -> List[Dict]:
        """Busca mediadores por nome"""
        termo_lower = termo.lower()
        resultados = []

        for mediador in self.mediadores:
            if termo_lower in mediador['nome'].lower():
                resultados.append(mediador)

        return resultados
