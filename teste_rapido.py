"""
Teste rápido do sistema - verifica se tudo está funcionando
"""
from escolas import GerenciadorEscolas

print("=" * 60)
print(" TESTE RAPIDO DO SISTEMA ".center(60))
print("=" * 60)
print()

# Teste 1: Carregar escolas
print("1. Testando carregamento de escolas...")
try:
    gerenciador = GerenciadorEscolas()
    print(f"   [OK] {len(gerenciador.escolas)} escolas carregadas")
except Exception as e:
    print(f"   [ERRO] {e}")

# Teste 2: Listar Bloco 1
print("\n2. Testando match do Bloco 1...")
try:
    bloco1 = gerenciador.listar_escolas_bloco1()
    print(f"   [OK] {len(bloco1)} escolas no Bloco 1")
except Exception as e:
    print(f"   [ERRO] {e}")

# Teste 3: Buscar escola
print("\n3. Testando busca de escola...")
try:
    escola = gerenciador.buscar_escola("CECAP")
    if escola:
        print(f"   [OK] Encontrada: {escola['nome_oficial']}")
    else:
        print("   [AVISO] Escola nao encontrada")
except Exception as e:
    print(f"   [ERRO] {e}")

# Teste 4: Verificar geocodificação
print("\n4. Verificando geocodificacao...")
try:
    com_coords = sum(1 for e in bloco1 if 'latitude' in e and 'longitude' in e)
    sem_coords = len(bloco1) - com_coords

    print(f"   [OK] Escolas geocodificadas: {com_coords}/{len(bloco1)}")
    if sem_coords > 0:
        print(f"   [AVISO] {sem_coords} escolas ainda sem coordenadas")
        print(f"   Execute: python setup_auto.py")
except Exception as e:
    print(f"   [ERRO] {e}")

print("\n" + "=" * 60)
print(" TESTE CONCLUIDO ".center(60))
print("=" * 60)
print()

if com_coords == len(bloco1):
    print("Sistema pronto para uso!")
    print("Execute: python main.py")
else:
    print("Execute primeiro: python setup_auto.py")
print()
