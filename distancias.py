"""
Módulo para calcular distâncias entre escolas usando OSRM
"""
import requests
from typing import List, Dict, Optional, Tuple
import json


class CalculadorDistancias:
    def __init__(self, servidor_osrm: str = "http://router.project-osrm.org"):
        """
        Inicializa o calculador de distâncias

        Args:
            servidor_osrm: URL do servidor OSRM (padrão: servidor público)
                          Pode usar também: "https://routing.openstreetmap.de/routed-car"
        """
        self.servidor_osrm = servidor_osrm

    def calcular_distancia(self, origem: Tuple[float, float], destino: Tuple[float, float]) -> Optional[Dict]:
        """
        Calcula distância e tempo de viagem entre dois pontos

        Args:
            origem: Tupla (latitude, longitude) do ponto de origem
            destino: Tupla (latitude, longitude) do ponto de destino

        Returns:
            Dicionário com informações da rota ou None se houver erro
        """
        try:
            # OSRM usa formato: longitude,latitude (inverso!)
            url = f"{self.servidor_osrm}/route/v1/driving/{origem[1]},{origem[0]};{destino[1]},{destino[0]}"

            params = {
                'overview': 'false',  # Não precisa da geometria completa
                'steps': 'false'       # Não precisa das instruções passo a passo
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('code') == 'Ok' and 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]

                return {
                    'distancia_metros': route['distance'],
                    'distancia_km': round(route['distance'] / 1000, 2),
                    'duracao_segundos': route['duration'],
                    'duracao_minutos': round(route['duration'] / 60, 1)
                }
            else:
                print(f"Erro na resposta OSRM: {data.get('code', 'desconhecido')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Erro ao calcular rota: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return None

    def calcular_matriz_distancias(self, escolas: List[Dict]) -> Dict:
        """
        Calcula matriz de distâncias entre todas as escolas

        Args:
            escolas: Lista de escolas com coordenadas

        Returns:
            Dicionário com matriz de distâncias
        """
        matriz = {}
        total_calculos = len(escolas) * (len(escolas) - 1) // 2
        calculos_feitos = 0

        print(f"Calculando matriz de distâncias para {len(escolas)} escolas...")
        print(f"Total de cálculos necessários: {total_calculos}\n")

        for i, escola_origem in enumerate(escolas):
            if 'latitude' not in escola_origem or 'longitude' not in escola_origem:
                print(f"⚠️  Escola {escola_origem['nome_usual']} sem coordenadas, pulando...")
                continue

            origem_key = escola_origem['nome_usual']
            if origem_key not in matriz:
                matriz[origem_key] = {}

            for j, escola_destino in enumerate(escolas):
                if i >= j:  # Evita calcular duplicados e distância para si mesmo
                    continue

                if 'latitude' not in escola_destino or 'longitude' not in escola_destino:
                    continue

                destino_key = escola_destino['nome_usual']

                origem_coords = (escola_origem['latitude'], escola_origem['longitude'])
                destino_coords = (escola_destino['latitude'], escola_destino['longitude'])

                rota = self.calcular_distancia(origem_coords, destino_coords)

                if rota:
                    # Adiciona nas duas direções (assumindo que a distância é a mesma)
                    matriz[origem_key][destino_key] = rota

                    if destino_key not in matriz:
                        matriz[destino_key] = {}
                    matriz[destino_key][origem_key] = rota

                    calculos_feitos += 1
                    print(f"[{calculos_feitos}/{total_calculos}] {origem_key} → {destino_key}: "
                          f"{rota['distancia_km']} km, {rota['duracao_minutos']} min")
                else:
                    print(f"✗ Erro: {origem_key} → {destino_key}")

        return matriz

    def encontrar_escolas_proximas(self, escola_ref: Dict, outras_escolas: List[Dict],
                                   limite: int = 5) -> List[Dict]:
        """
        Encontra as escolas mais próximas de uma escola de referência

        Args:
            escola_ref: Escola de referência
            outras_escolas: Lista de outras escolas
            limite: Número máximo de escolas a retornar

        Returns:
            Lista de escolas mais próximas com suas distâncias
        """
        if 'latitude' not in escola_ref or 'longitude' not in escola_ref:
            print(f"⚠️  Escola {escola_ref['nome_usual']} sem coordenadas")
            return []

        ref_coords = (escola_ref['latitude'], escola_ref['longitude'])
        distancias = []

        for escola in outras_escolas:
            if escola['id'] == escola_ref['id']:
                continue

            if 'latitude' not in escola or 'longitude' not in escola:
                continue

            escola_coords = (escola['latitude'], escola['longitude'])
            rota = self.calcular_distancia(ref_coords, escola_coords)

            if rota:
                distancias.append({
                    'escola': escola,
                    'distancia_km': rota['distancia_km'],
                    'duracao_minutos': rota['duracao_minutos']
                })

        # Ordena por distância
        distancias.sort(key=lambda x: x['distancia_km'])

        return distancias[:limite]

    def salvar_matriz(self, matriz: Dict, arquivo: str = "data/matriz_distancias.json"):
        """Salva matriz de distâncias em arquivo JSON"""
        import os
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)

        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(matriz, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Matriz salva em: {arquivo}")

    def carregar_matriz(self, arquivo: str = "data/matriz_distancias.json") -> Optional[Dict]:
        """Carrega matriz de distâncias de arquivo JSON"""
        import os

        if not os.path.exists(arquivo):
            return None

        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    def obter_distancia_entre(self, escola1: str, escola2: str,
                              matriz: Dict) -> Optional[Dict]:
        """
        Obtém distância entre duas escolas da matriz pré-calculada

        Args:
            escola1: Nome usual da primeira escola
            escola2: Nome usual da segunda escola
            matriz: Matriz de distâncias pré-calculada

        Returns:
            Dicionário com informações de distância ou None
        """
        if escola1 in matriz and escola2 in matriz[escola1]:
            return matriz[escola1][escola2]
        elif escola2 in matriz and escola1 in matriz[escola2]:
            return matriz[escola2][escola1]
        else:
            return None
