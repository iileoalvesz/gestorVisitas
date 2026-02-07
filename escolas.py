"""
Módulo para gerenciar dados das escolas de Taubaté
"""
import json
import os
from typing import List, Dict, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Dados das escolas baseados nos anexos fornecidos
ESCOLAS_TAUBATE = [
    {"id": 1, "nome_oficial": "EMIEF Profa. Anita Ribas de Andrade", "nome_usual": "Anita Ribas"},
    {"id": 2, "nome_oficial": "EMIEF Padre Silvino Vicente Kunz", "nome_usual": "Areião"},
    {"id": 3, "nome_oficial": "EMIEF Dr. Avedis Victor Nahas", "nome_usual": "Avedis"},
    {"id": 4, "nome_oficial": "EMIEF Dom Pereira de Barros", "nome_usual": "Bela Vista"},
    {"id": 5, "nome_oficial": "EMIEF Prof. Emílio Simonetti", "nome_usual": "Bosque"},
    {"id": 6, "nome_oficial": "EMEIEF Mário Lemos de Oliveira", "nome_usual": "Caieiras"},
    {"id": 7, "nome_oficial": "EMEF Prefeito Guido José Gomes Miné", "nome_usual": "CECAP"},
    {"id": 8, "nome_oficial": "EMEF Prof. José Sant'Anna de Souza", "nome_usual": "Chácara Flórida"},
    {"id": 9, "nome_oficial": "EMEIEF Prof. Ciniro Mathias Bueno", "nome_usual": "Chácara Ingrid"},
    {"id": 10, "nome_oficial": "EMEF Profa. Marisa Lapido Barbosa", "nome_usual": "Chácaras Reunidas"},
    {"id": 11, "nome_oficial": "EMEF Cônego José Luiz Pereira Ribeiro", "nome_usual": "Cônego"},
    {"id": 12, "nome_oficial": "EMEIEF Profa. Ana Silvia Paolichi Ferro", "nome_usual": "Continental"},
    {"id": 13, "nome_oficial": "EMEF Coronel José Benedito Marcondes de Mattos", "nome_usual": "Coronel"},
    {"id": 14, "nome_oficial": "EMEF Dr. Quirino", "nome_usual": "Dr. Quirino"},
    {"id": 15, "nome_oficial": "EMEF Prof. Ernani Giannico", "nome_usual": "Ernani-Giannico"},
    {"id": 16, "nome_oficial": "EMIEF Prof. Ernesto de Oliveira Filho", "nome_usual": "Ernesto"},
    {"id": 17, "nome_oficial": "EMEFM Vereador Joaquim França", "nome_usual": "Esplanada I"},
    {"id": 18, "nome_oficial": "EMIEF Prof. Dr. João Baptista Ortiz Monteiro", "nome_usual": "Esplanada II"},
    {"id": 19, "nome_oficial": "EMEF Monsenhor Evaristo Campista César", "nome_usual": "Evaristo"},
    {"id": 20, "nome_oficial": "EMEFM Prof. José Ezequiel de Souza", "nome_usual": "Ezequiel"},
    {"id": 21, "nome_oficial": "EMEF Prof. Antônio Carlos Ribas Branco", "nome_usual": "Fonte I"},
    {"id": 22, "nome_oficial": "EMIEF Vereador Mário Monteiro dos Santos", "nome_usual": "Gurilândia"},
    {"id": 23, "nome_oficial": "EMEF Hildebrando Rocha", "nome_usual": "Hildebrando"},
    {"id": 24, "nome_oficial": "EMEIEF Cônego Benedito Augusto Corrêa", "nome_usual": "Itaim"},
    {"id": 25, "nome_oficial": "EMEIEF Profa. Simone dos Santos", "nome_usual": "Jaboticabeiras"},
    {"id": 26, "nome_oficial": "EMEF Aldeeira Sophia de Faria Martins Ferreira", "nome_usual": "Jardim dos Estados"},
    {"id": 27, "nome_oficial": "EMEF Profa. Judith Campista César", "nome_usual": "Judith"},
    {"id": 28, "nome_oficial": "EMEF Prof. Juvenal da Costa de Silva", "nome_usual": "Juvenal"},
    {"id": 29, "nome_oficial": "EMEF Prof. Luiz Augusto da Silva", "nome_usual": "Luiz Augusto"},
    {"id": 30, "nome_oficial": "EMEEEIF Madre Cecília", "nome_usual": "Madre Cecília"},
    {"id": 31, "nome_oficial": "EMEIEFM Emílio Amadei Beringhs", "nome_usual": "Marlene Miranda"},
    {"id": 32, "nome_oficial": "EMEIEFM Prof. José Marcondes de Moura", "nome_usual": "Monjolinho"},
    {"id": 33, "nome_oficial": "EMEF Prof. Luiz Ribeiro Muniz", "nome_usual": "Monte Belo"},
    {"id": 34, "nome_oficial": "EMEF Prof. Claudio Cesar Guilherme de Toledo", "nome_usual": "Mourisco"},
    {"id": 35, "nome_oficial": "EMIEF Marta Miranda Del Rei", "nome_usual": "Novo Horizonte"},
    {"id": 36, "nome_oficial": "EMEF Pe. Prof. Dr. Ramon de Oliveira Ortiz", "nome_usual": "Ramon"},
    {"id": 37, "nome_oficial": "EMEIEF Antônio de Angelis", "nome_usual": "Registro"},
    {"id": 38, "nome_oficial": "EMEF Diácono José Ângelo Victal", "nome_usual": "Santa Luzia"},
    {"id": 39, "nome_oficial": "EMEIEF Braz Silvério Lemes", "nome_usual": "Santa Luzia Rural"},
    {"id": 40, "nome_oficial": "EMEIEF Profa. Docelina Silva de Campos Coelho", "nome_usual": "Santa Tereza"},
    {"id": 41, "nome_oficial": "EMEF Prof. Lafayette Rodrigues Pereira", "nome_usual": "São Gonçalo"},
    {"id": 42, "nome_oficial": "EMEFM Anna dos Reis Signorini", "nome_usual": "SEDES"},
    {"id": 43, "nome_oficial": "EMEIEF Sargento Everton Vendramel de Castro Chagas", "nome_usual": "Sítio II"},
    {"id": 44, "nome_oficial": "EMEF Prof. Walther de Oliveira", "nome_usual": "Santa Maria"},
    {"id": 45, "nome_oficial": "UEI Profa. Lúcia Helena Moraes dos Santos", "nome_usual": "UEI CETI"},
    {"id": 47, "nome_oficial": "EMEF Vereador Pedro Grandchain", "nome_usual": "FONTE II"},
    {"id": 46, "nome_oficial": "UEI Prof. Laércio Antônio Soares dos Santos", "nome_usual": "UEI Planalto"},
    {"id": 48, "nome_oficial": "UEI Profa. Thereza Villarta Gonçalves", "nome_usual": "UEI Três Marias"},
    {"id": 49, "nome_oficial": "EMEIEF Vereadora Judith Mazella Moura", "nome_usual": "Vila Caetano"},
    {"id": 50, "nome_oficial": "EMEF Dom José Antônio do Couto", "nome_usual": "Vila J'min"},
    {"id": 51, "nome_oficial": "EMEIEF Tomé Portes Del Rei", "nome_usual": "Vila Velha"},
    {"id": 52, "nome_oficial": "EMEF Walter Thaumaturgo", "nome_usual": "Walter"},
]

# Escolas do Bloco 1 (do anexo 2)
BLOCO_1 = [
    "Bela Vista", "CECAP", "Chácaras Reunidas", "Continental", "Coronel",
    "Ezequiel", "Fonte II", "Itaim", "Jaboticabeiras", "Juvenal",
    "Marlene Miranda", "Monte Belo", "Novo Horizonte", "Ramon", "Santa Luzia",
    "Santa Luzia Rural", "Santa Tereza", "São Gonçalo", "Vila Velha", "Vila Caetano"
]


class GerenciadorEscolas:
    def __init__(self, arquivo_dados: str = "data/escolas.json"):
        self.arquivo_dados = arquivo_dados
        self.escolas = []
        self.geolocator = Nominatim(user_agent="gestor_visitas_escolas_taubate")
        self._carregar_dados()

    def _carregar_dados(self):
        """Carrega dados das escolas do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                self.escolas = json.load(f)
        else:
            self.escolas = ESCOLAS_TAUBATE.copy()
            self._salvar_dados()

    def _salvar_dados(self):
        """Salva dados das escolas no arquivo JSON"""
        os.makedirs(os.path.dirname(self.arquivo_dados), exist_ok=True)
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.escolas, f, ensure_ascii=False, indent=2)

    def fazer_match_bloco1(self) -> List[Dict]:
        """Faz o match entre as escolas do Bloco 1 e a lista completa"""
        escolas_bloco1 = []

        for nome_bloco in BLOCO_1:
            escola_encontrada = None
            nome_bloco_lower = nome_bloco.lower().strip()

            # Procura match exato
            for escola in self.escolas:
                nome_usual_lower = escola['nome_usual'].lower().strip()
                if nome_usual_lower == nome_bloco_lower:
                    escola_encontrada = escola.copy()
                    break

            # Se não encontrou match exato, procura parcial
            if not escola_encontrada:
                for escola in self.escolas:
                    nome_usual_lower = escola['nome_usual'].lower().strip()
                    if nome_bloco_lower in nome_usual_lower or nome_usual_lower in nome_bloco_lower:
                        escola_encontrada = escola.copy()
                        break

            if escola_encontrada:
                escolas_bloco1.append(escola_encontrada)
            else:
                print(f"[AVISO]Escola não encontrada no match: {nome_bloco}")

        return escolas_bloco1

    def _geocode_com_retry(self, query: str, max_tentativas: int = 3) -> Optional[tuple]:
        """Tenta geocodificar com retry em caso de timeout"""
        for tentativa in range(max_tentativas):
            try:
                location = self.geolocator.geocode(query, timeout=10)
                if location:
                    return (location.latitude, location.longitude)
                return None
            except GeocoderTimedOut:
                if tentativa < max_tentativas - 1:
                    time.sleep(1)
                    continue
                return None
            except Exception as e:
                print(f"Erro ao geocodificar {query}: {e}")
                return None
        return None

    def obter_coordenadas(self, escola: Dict) -> Optional[tuple]:
        """Obtém coordenadas geográficas de uma escola"""
        # Se já tem coordenadas salvas, retorna
        if 'latitude' in escola and 'longitude' in escola:
            return (escola['latitude'], escola['longitude'])

        # Tenta geocodificar com o nome oficial
        query = f"{escola['nome_oficial']}, Taubaté, SP, Brasil"
        coords = self._geocode_com_retry(query)

        # Se não encontrou, tenta com nome usual
        if not coords:
            query = f"Escola {escola['nome_usual']}, Taubaté, SP, Brasil"
            coords = self._geocode_com_retry(query)

        # Se não encontrou, tenta apenas com bairro/região
        if not coords:
            query = f"{escola['nome_usual']}, Taubaté, SP, Brasil"
            coords = self._geocode_com_retry(query)

        if coords:
            # Atualiza escola com coordenadas
            for esc in self.escolas:
                if esc['id'] == escola['id']:
                    esc['latitude'] = coords[0]
                    esc['longitude'] = coords[1]
                    break
            self._salvar_dados()

        # Aguarda para não sobrecarregar o serviço
        time.sleep(1)

        return coords

    def geocodificar_todas_bloco1(self):
        """Geocodifica todas as escolas do Bloco 1"""
        escolas_bloco1 = self.fazer_match_bloco1()

        print(f"Geocodificando {len(escolas_bloco1)} escolas do Bloco 1...\n")

        for i, escola in enumerate(escolas_bloco1, 1):
            print(f"[{i}/{len(escolas_bloco1)}] {escola['nome_usual']}... ", end='')

            coords = self.obter_coordenadas(escola)

            if coords:
                print(f"[OK] ({coords[0]:.6f}, {coords[1]:.6f})")
            else:
                print("[X] Não encontrado")

        print("\n[OK] Geocodificacao concluida!")

    def listar_escolas_bloco1(self) -> List[Dict]:
        """Lista todas as escolas do Bloco 1 com suas informações"""
        return self.fazer_match_bloco1()

    def buscar_escola(self, termo: str) -> Optional[Dict]:
        """Busca uma escola por nome usual ou ID"""
        termo_lower = termo.lower().strip()

        # Tenta buscar por ID
        try:
            escola_id = int(termo)
            for escola in self.escolas:
                if escola['id'] == escola_id:
                    return escola
        except ValueError:
            pass

        # Busca por nome usual
        for escola in self.escolas:
            if termo_lower in escola['nome_usual'].lower():
                return escola

        return None

    def atualizar_diretor(self, escola_id: int, nome_diretor: str) -> bool:
        """Atualiza o diretor de uma escola"""
        for escola in self.escolas:
            if escola['id'] == escola_id:
                escola['diretor'] = nome_diretor
                self._salvar_dados()
                return True
        return False

    def obter_diretor(self, escola_id: int) -> Optional[str]:
        """Obtém o nome do diretor de uma escola"""
        for escola in self.escolas:
            if escola['id'] == escola_id:
                return escola.get('diretor', '')
        return None

    def atualizar_escola(self, escola_id: int, nome_oficial: str = None,
                        nome_usual: str = None, diretor: str = None) -> bool:
        """Atualiza dados de uma escola"""
        for escola in self.escolas:
            if escola['id'] == escola_id:
                if nome_oficial is not None:
                    escola['nome_oficial'] = nome_oficial
                if nome_usual is not None:
                    escola['nome_usual'] = nome_usual
                if diretor is not None:
                    escola['diretor'] = diretor
                self._salvar_dados()
                return True
        return False

    def adicionar_escola(self, nome_oficial: str, nome_usual: str, diretor: str = "") -> Dict:
        """Adiciona uma nova escola"""
        novo_id = max(e['id'] for e in self.escolas) + 1 if self.escolas else 1
        nova_escola = {
            'id': novo_id,
            'nome_oficial': nome_oficial,
            'nome_usual': nome_usual,
            'diretor': diretor
        }
        self.escolas.append(nova_escola)
        self._salvar_dados()
        return nova_escola

    def obter_escola(self, escola_id: int) -> Optional[Dict]:
        """Obtém uma escola por ID"""
        for escola in self.escolas:
            if escola['id'] == escola_id:
                return escola
        return None
