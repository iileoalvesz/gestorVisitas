"""
Script de configuração automática do sistema (sem interação)
Geocodifica as escolas do Bloco 1 e prepara o ambiente
"""
import os
import sys
from escolas import GerenciadorEscolas


def main():
    """Executa configuração inicial automaticamente"""
    print("\n")
    print("=" * 80)
    print(" CONFIGURACAO AUTOMATICA DO SISTEMA ".center(80))
    print(" Gestao de Visitas as Escolas - Taubate/SP ".center(80))
    print("=" * 80)
    print("\n")

    # 1. Verifica diretórios
    print("Verificando estrutura de diretorios...")
    diretorios = ['data', 'anexos', 'relatorios']

    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"  [OK] Criado: {diretorio}/")
        else:
            print(f"  [OK] Existe: {diretorio}/")

    print()

    # 2. Geocodifica escolas
    print("=" * 80)
    print("GEOCODIFICACAO DAS ESCOLAS DO BLOCO 1")
    print("=" * 80)
    print()
    print("Iniciando geocodificacao automatica...")
    print("Isso pode demorar alguns minutos (1 requisicao/segundo)")
    print()
    print("-" * 80)

    gerenciador = GerenciadorEscolas()
    gerenciador.geocodificar_todas_bloco1()

    print("-" * 80)

    # Verifica resultados
    escolas_bloco1 = gerenciador.listar_escolas_bloco1()
    com_coords = sum(1 for e in escolas_bloco1 if 'latitude' in e and 'longitude' in e)
    sem_coords = len(escolas_bloco1) - com_coords

    print(f"\nResultado:")
    print(f"  [OK] Escolas geocodificadas: {com_coords}/{len(escolas_bloco1)}")

    if sem_coords > 0:
        print(f"  [AVISO] Escolas sem coordenadas: {sem_coords}")
        print("\n  Escolas que nao foram geocodificadas:")
        for escola in escolas_bloco1:
            if 'latitude' not in escola or 'longitude' not in escola:
                print(f"    - {escola['nome_usual']}")

    print()

    # 3. Resumo final
    print("=" * 80)
    print("RESUMO DA CONFIGURACAO")
    print("=" * 80)

    print(f"\n[OK] Escolas no Bloco 1: {len(escolas_bloco1)}")
    print(f"[OK] Escolas geocodificadas: {com_coords}")

    print("\n" + "=" * 80)
    print()
    print("*** CONFIGURACAO INICIAL CONCLUIDA!")
    print()
    print("Proximos passos:")
    print("  1. Execute 'python main.py' para abrir o sistema")
    print("  2. Registre suas primeiras visitas (Menu: Registrar Visita)")
    print("  3. Gere relatorios (Menu: Gerar Relatorios)")
    print()
    print("Dica: Use 'python exemplo_uso.py' para ver exemplos de uso programatico")
    print("=" * 80)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[AVISO] Configuracao interrompida pelo usuario.")
        print("Execute este script novamente para concluir a configuracao.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro durante configuracao: {e}")
        import traceback
        traceback.print_exc()
        print("\nPor favor, verifique os logs e tente novamente.\n")
        sys.exit(1)
