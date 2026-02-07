"""
Script de configuração inicial do sistema
Geocodifica as escolas do Bloco 1 e prepara o ambiente
"""
import os
import sys
from escolas import GerenciadorEscolas
from distancias import CalculadorDistancias


def verificar_diretorios():
    """Cria diretórios necessários se não existirem"""
    print("Verificando estrutura de diretórios...")

    diretorios = ['data', 'anexos', 'relatorios']

    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"  [OK]Criado: {diretorio}/")
        else:
            print(f"  [OK]Existe: {diretorio}/")

    print()


def geocodificar_escolas_bloco1():
    """Geocodifica todas as escolas do Bloco 1"""
    print("=" * 80)
    print("GEOCODIFICAÇÃO DAS ESCOLAS DO BLOCO 1")
    print("=" * 80)
    print()
    print("Esta etapa irá obter as coordenadas geográficas de todas as escolas")
    print("do Bloco 1 usando o serviço Nominatim (OpenStreetMap).")
    print()
    print("[AVISO]IMPORTANTE:")
    print("  - O processo pode demorar alguns minutos (1 requisição/segundo)")
    print("  - Requer conexão com a internet")
    print("  - Algumas escolas podem não ser encontradas automaticamente")
    print()

    confirma = input("Deseja continuar? (s/n): ").strip().lower()

    if confirma != 's':
        print("\nGeocodificação cancelada.")
        return False

    print("\nIniciando geocodificação...\n")
    print("-" * 80)

    gerenciador = GerenciadorEscolas()
    gerenciador.geocodificar_todas_bloco1()

    print("-" * 80)

    # Verifica resultados
    escolas_bloco1 = gerenciador.listar_escolas_bloco1()
    com_coords = sum(1 for e in escolas_bloco1 if 'latitude' in e and 'longitude' in e)
    sem_coords = len(escolas_bloco1) - com_coords

    print(f"\nResultado:")
    print(f"  [OK]Escolas geocodificadas: {com_coords}/{len(escolas_bloco1)}")

    if sem_coords > 0:
        print(f"  [AVISO]Escolas sem coordenadas: {sem_coords}")
        print("\n  Escolas que não foram geocodificadas:")
        for escola in escolas_bloco1:
            if 'latitude' not in escola or 'longitude' not in escola:
                print(f"    - {escola['nome_usual']}")

    print()
    return com_coords > 0


def calcular_matriz_inicial():
    """Calcula matriz de distâncias inicial (opcional)"""
    print("=" * 80)
    print("CÁLCULO DA MATRIZ DE DISTÂNCIAS")
    print("=" * 80)
    print()
    print("Esta etapa é OPCIONAL e irá calcular as distâncias entre todas as")
    print("escolas do Bloco 1 usando rotas reais de carro (OSRM).")
    print()
    print("[AVISO]IMPORTANTE:")
    print("  - Processo pode demorar bastante (20 escolas = 190 cálculos)")
    print("  - Requer conexão com a internet")
    print("  - Pode pular esta etapa e calcular distâncias sob demanda")
    print()

    confirma = input("Deseja calcular a matriz de distâncias agora? (s/n): ").strip().lower()

    if confirma != 's':
        print("\nCálculo de matriz pulado. Você pode fazer isso depois no menu principal.")
        return

    gerenciador = GerenciadorEscolas()
    calculador = CalculadorDistancias()

    escolas_bloco1 = gerenciador.listar_escolas_bloco1()

    # Verifica se todas têm coordenadas
    sem_coords = [e for e in escolas_bloco1 if 'latitude' not in e or 'longitude' not in e]

    if sem_coords:
        print(f"\n[AVISO]{len(sem_coords)} escola(s) ainda sem coordenadas.")
        print("A matriz será calculada apenas para as escolas com coordenadas.\n")

    print("Iniciando cálculo da matriz...\n")
    print("-" * 80)

    matriz = calculador.calcular_matriz_distancias(escolas_bloco1)
    calculador.salvar_matriz(matriz)

    print("-" * 80)
    print("\n[OK]Matriz de distâncias calculada e salva!")
    print()


def exibir_resumo_final():
    """Exibe resumo da configuração"""
    print("=" * 80)
    print("RESUMO DA CONFIGURAÇÃO")
    print("=" * 80)

    gerenciador = GerenciadorEscolas()
    escolas_bloco1 = gerenciador.listar_escolas_bloco1()

    com_coords = sum(1 for e in escolas_bloco1 if 'latitude' in e and 'longitude' in e)

    print(f"\n✓ Escolas no Bloco 1: {len(escolas_bloco1)}")
    print(f"✓ Escolas geocodificadas: {com_coords}")

    # Verifica se matriz existe
    if os.path.exists("data/matriz_distancias.json"):
        print(f"✓ Matriz de distâncias: Calculada")
    else:
        print(f"[ ]Matriz de distâncias: Não calculada (opcional)")

    print("\n" + "=" * 80)
    print()
    print("***CONFIGURAÇÃO INICIAL CONCLUÍDA!")
    print()
    print("Próximos passos:")
    print("  1. Execute 'python main.py' para abrir o sistema")
    print("  2. Registre suas primeiras visitas (Menu: Registrar Visita)")
    print("  3. Gere relatórios (Menu: Gerar Relatórios)")
    print()
    print("Dica: Use 'python exemplo_uso.py' para ver exemplos de uso programático")
    print("=" * 80)
    print()


def main():
    """Executa configuração inicial"""
    print("\n")
    print("=" * 80)
    print(" CONFIGURACAO INICIAL DO SISTEMA ".center(80))
    print(" Gestao de Visitas as Escolas - Taubate/SP ".center(80))
    print("=" * 80)
    print("\n")

    print("Este assistente irá configurar o sistema pela primeira vez.")
    print()

    try:
        # 1. Verifica diretórios
        verificar_diretorios()

        # 2. Geocodifica escolas
        sucesso_geo = geocodificar_escolas_bloco1()

        if not sucesso_geo:
            print("\n[AVISO]Nenhuma escola foi geocodificada.")
            print("Verifique sua conexão com a internet e tente novamente.")
            return

        # 3. Calcula matriz (opcional)
        calcular_matriz_inicial()

        # 4. Resumo final
        exibir_resumo_final()

    except KeyboardInterrupt:
        print("\n\n[AVISO]Configuração interrompida pelo usuário.")
        print("Execute este script novamente para concluir a configuração.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO]Erro durante configuração: {e}")
        print("Por favor, verifique os logs e tente novamente.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
