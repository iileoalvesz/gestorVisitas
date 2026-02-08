"""
Modulo para gerenciar usuarios do sistema
"""
import json
import os
from typing import Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Usuario(UserMixin):
    """Classe de usuario compativel com Flask-Login"""

    def __init__(self, id, username, password_hash, nome_exibicao="", ativo=True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.nome_exibicao = nome_exibicao
        self.ativo = ativo

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.ativo

    def verificar_senha(self, senha):
        return check_password_hash(self.password_hash, senha)

    @staticmethod
    def from_dict(data):
        return Usuario(
            id=data['id'],
            username=data['username'],
            password_hash=data['password_hash'],
            nome_exibicao=data.get('nome_exibicao', ''),
            ativo=data.get('ativo', True)
        )


class GerenciadorUsuarios:
    def __init__(self, arquivo_dados: str = "data/usuarios.json"):
        self.arquivo_dados = arquivo_dados
        self.usuarios = []
        self._carregar_dados()

    def _carregar_dados(self):
        """Carrega usuarios do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                self.usuarios = json.load(f)
        else:
            self.usuarios = []
            self._salvar_dados()

    def _salvar_dados(self):
        """Salva usuarios no arquivo JSON"""
        os.makedirs(os.path.dirname(self.arquivo_dados), exist_ok=True)
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, ensure_ascii=False, indent=2)

    def _gerar_id(self) -> int:
        """Gera proximo ID disponivel"""
        if not self.usuarios:
            return 1
        return max(u['id'] for u in self.usuarios) + 1

    def inicializar_admin(self):
        """Cria usuario admin padrao se nenhum usuario existir"""
        if not self.usuarios:
            self.adicionar_usuario(
                username="mileny_alves",
                senha="M@2026",
                nome_exibicao="Mileny Alves"
            )

    def adicionar_usuario(self, username: str, senha: str,
                          nome_exibicao: str = "") -> Dict:
        """Adiciona novo usuario com senha hasheada"""
        usuario = {
            'id': self._gerar_id(),
            'username': username,
            'password_hash': generate_password_hash(senha),
            'nome_exibicao': nome_exibicao,
            'ativo': True
        }
        self.usuarios.append(usuario)
        self._salvar_dados()
        return usuario

    def obter_por_username(self, username: str) -> Optional[Usuario]:
        """Busca usuario por username e retorna objeto Usuario"""
        for u in self.usuarios:
            if u['username'] == username:
                return Usuario.from_dict(u)
        return None

    def obter_por_id(self, user_id: int) -> Optional[Usuario]:
        """Busca usuario por ID e retorna objeto Usuario"""
        for u in self.usuarios:
            if u['id'] == int(user_id):
                return Usuario.from_dict(u)
        return None
