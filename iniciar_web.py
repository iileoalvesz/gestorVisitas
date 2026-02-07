"""
Script de inicialização do Sistema Web
"""
import os
import sys

def verificar_requisitos():
    """Verifica se todos os requisitos estão instalados"""
    print("Verificando requisitos...")

    requisitos = [
        ('Flask', 'flask'),
        ('Requests', 'requests'),
        ('Geopy', 'geopy'),
        ('Pandas', 'pandas')
    ]

    faltando = []
    for nome, modulo in requisitos:
        try:
            __import__(modulo)
            print(f"  [OK] {nome}")
        except ImportError:
            print(f"  [X] {nome} - NAO INSTALADO")
            faltando.append(nome)

    if faltando:
        print(f"\nFaltam dependencias: {', '.join(faltando)}")
        print("Execute: pip install -r requirements.txt")
        return False

    print("\n[OK] Todos os requisitos estao instalados!")
    return True


def verificar_estrutura():
    """Verifica estrutura de pastas"""
    print("\nVerificando estrutura de pastas...")

    pastas = ['data', 'anexos', 'relatorios', 'templates', 'static', 'static/uploads']

    for pasta in pastas:
        if os.path.exists(pasta):
            print(f"  [OK] {pasta}/")
        else:
            print(f"  [CRIANDO] {pasta}/")
            os.makedirs(pasta, exist_ok=True)

    print("\n[OK] Estrutura de pastas OK!")
    return True


def verificar_dados():
    """Verifica se há dados das escolas"""
    print("\nVerificando dados das escolas...")

    if os.path.exists('data/escolas.json'):
        print("  [OK] Dados das escolas encontrados")
        return True
    else:
        print("  [AVISO] Dados das escolas nao encontrados")
        print("  Execute: python setup_auto.py")
        return False


def iniciar_servidor():
    """Inicia o servidor Flask"""
    print("\n" + "=" * 60)
    print(" INICIANDO SISTEMA WEB ".center(60))
    print("=" * 60)
    print("\nServidor sera iniciado em: http://localhost:5000")
    print("Pressione CTRL+C para encerrar\n")

    # Importa e inicia app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print(" SISTEMA DE GESTAO DE VISITAS - WEB ".center(60))
    print(" Taubate/SP ".center(60))
    print("=" * 60)
    print()

    # Verifica requisitos
    if not verificar_requisitos():
        sys.exit(1)

    # Verifica estrutura
    verificar_estrutura()

    # Verifica dados
    tem_dados = verificar_dados()

    if not tem_dados:
        print("\n[IMPORTANTE] Execute primeiro a configuracao inicial:")
        print("  python setup_auto.py\n")
        resposta = input("Deseja continuar mesmo assim? (s/n): ").strip().lower()
        if resposta != 's':
            print("\nCancelado. Execute setup_auto.py primeiro.")
            sys.exit(0)

    # Inicia servidor
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n\nServidor encerrado pelo usuario.")
        print("Ate logo!\n")
    except Exception as e:
        print(f"\n[ERRO] Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
