"""
Exemplos de uso programático do Sistema de Gestão de Visitas
"""
from escolas import GerenciadorEscolas
from visitas import GerenciadorVisitas
from distancias import CalculadorDistancias
from relatorios import GeradorRelatorios
from datetime import datetime, timedelta


def exemplo_1_listar_escolas():
    """Exemplo 1: Listar e fazer match das escolas do Bloco 1"""
    print("=" * 80)
    print("EXEMPLO 1: Listando escolas do Bloco 1")
    print("=" * 80)

    gerenciador = GerenciadorEscolas()

    # Lista escolas do Bloco 1
    escolas_bloco1 = gerenciador.listar_escolas_bloco1()

    print(f"\nTotal de escolas no Bloco 1: {len(escolas_bloco1)}\n")

    for i, escola in enumerate(escolas_bloco1, 1):
        tem_coords = 'latitude' in escola and 'longitude' in escola
        status = "[OK]" if tem_coords else "[X]"

        print(f"{i}. {escola['nome_usual']:25} | {escola['nome_oficial'][:45]:45} | {status}")

    print("\n" + "=" * 80 + "\n")


def exemplo_2_geocodificar_escola():
    """Exemplo 2: Geocodificar uma escola específica"""
    print("=" * 80)
    print("EXEMPLO 2: Geocodificando uma escola")
    print("=" * 80)

    gerenciador = GerenciadorEscolas()

    # Busca escola
    escola = gerenciador.buscar_escola("CECAP")

    if escola:
        print(f"\nEscola encontrada: {escola['nome_oficial']}")
        print(f"Nome usual: {escola['nome_usual']}")

        # Obtém coordenadas
        coords = gerenciador.obter_coordenadas(escola)

        if coords:
            print(f"Coordenadas: ({coords[0]:.6f}, {coords[1]:.6f})")
        else:
            print("Não foi possível obter coordenadas")

    print("\n" + "=" * 80 + "\n")


def exemplo_3_calcular_distancia():
    """Exemplo 3: Calcular distância entre duas escolas"""
    print("=" * 80)
    print("EXEMPLO 3: Calculando distância entre escolas")
    print("=" * 80)

    gerenciador_escolas = GerenciadorEscolas()
    calculador = CalculadorDistancias()

    # Busca duas escolas
    escola1 = gerenciador_escolas.buscar_escola("CECAP")
    escola2 = gerenciador_escolas.buscar_escola("Continental")

    if escola1 and escola2:
        print(f"\nOrigem: {escola1['nome_usual']}")
        print(f"Destino: {escola2['nome_usual']}")

        # Verifica se têm coordenadas
        if 'latitude' in escola1 and 'latitude' in escola2:
            coords1 = (escola1['latitude'], escola1['longitude'])
            coords2 = (escola2['latitude'], escola2['longitude'])

            print("\nCalculando rota...")
            rota = calculador.calcular_distancia(coords1, coords2)

            if rota:
                print(f"\n[OK] Distância: {rota['distancia_km']} km")
                print(f"[OK] Tempo estimado: {rota['duracao_minutos']} minutos")
                print(f"[OK] Tempo em horas: {rota['duracao_minutos']/60:.1f}h")
            else:
                print("\n[X] Erro ao calcular rota")
        else:
            print("\n[AVISO]Uma ou mais escolas sem coordenadas")
            print("Execute a geocodificação primeiro")

    print("\n" + "=" * 80 + "\n")


def exemplo_4_escolas_proximas():
    """Exemplo 4: Encontrar escolas próximas"""
    print("=" * 80)
    print("EXEMPLO 4: Encontrando escolas próximas")
    print("=" * 80)

    gerenciador_escolas = GerenciadorEscolas()
    calculador = CalculadorDistancias()

    # Escola de referência
    escola_ref = gerenciador_escolas.buscar_escola("CECAP")

    if escola_ref and 'latitude' in escola_ref:
        print(f"\nEscola de referência: {escola_ref['nome_usual']}")
        print("\nBuscando escolas próximas...\n")

        # Lista todas as escolas do Bloco 1
        todas_escolas = gerenciador_escolas.listar_escolas_bloco1()

        # Encontra as 5 mais próximas
        proximas = calculador.encontrar_escolas_proximas(
            escola_ref,
            todas_escolas,
            limite=5
        )

        if proximas:
            print("Top 5 escolas mais próximas:\n")
            for i, item in enumerate(proximas, 1):
                print(f"{i}. {item['escola']['nome_usual']:25} - "
                      f"{item['distancia_km']:6.2f} km - "
                      f"{item['duracao_minutos']:5.1f} min")
        else:
            print("Nenhuma escola próxima encontrada")

    print("\n" + "=" * 80 + "\n")


def exemplo_5_registrar_visita():
    """Exemplo 5: Registrar uma visita"""
    print("=" * 80)
    print("EXEMPLO 5: Registrando uma visita")
    print("=" * 80)

    gerenciador_escolas = GerenciadorEscolas()
    gerenciador_visitas = GerenciadorVisitas()

    # Busca escola
    escola = gerenciador_escolas.buscar_escola("CECAP")

    if escola:
        print(f"\nRegistrando visita à escola: {escola['nome_usual']}")

        # Registra visita sem anexos
        visita = gerenciador_visitas.registrar_visita(
            escola_id=escola['id'],
            escola_nome=escola['nome_usual'],
            data=datetime.now().strftime("%Y-%m-%d"),
            observacoes="Reunião com equipe gestora sobre planejamento pedagógico. "
                       "Discutidos objetivos do semestre e necessidades de capacitação."
        )

        print(f"\n[OK] Visita registrada com sucesso!")
        print(f"  ID: {visita['id']}")
        print(f"  Data: {visita['data']} às {visita['hora']}")

    print("\n" + "=" * 80 + "\n")


def exemplo_6_listar_visitas():
    """Exemplo 6: Listar visitas com filtros"""
    print("=" * 80)
    print("EXEMPLO 6: Listando visitas")
    print("=" * 80)

    gerenciador_visitas = GerenciadorVisitas()

    # Listar todas as visitas
    todas_visitas = gerenciador_visitas.listar_visitas()
    print(f"\nTotal de visitas: {len(todas_visitas)}")

    if todas_visitas:
        print("\nÚltimas 5 visitas:\n")
        for visita in todas_visitas[:5]:
            print(f"- {visita['escola_nome']:25} | {visita['data']} | "
                  f"{len(visita.get('anexos', []))} anexo(s)")

    # Visitas dos últimos 30 dias
    data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    visitas_recentes = gerenciador_visitas.listar_visitas(data_inicio=data_inicio)

    print(f"\nVisitas nos últimos 30 dias: {len(visitas_recentes)}")

    print("\n" + "=" * 80 + "\n")


def exemplo_7_estatisticas():
    """Exemplo 7: Obter estatísticas"""
    print("=" * 80)
    print("EXEMPLO 7: Estatísticas de visitas")
    print("=" * 80)

    gerenciador_visitas = GerenciadorVisitas()

    stats = gerenciador_visitas.obter_estatisticas()

    print(f"\nTotal de visitas: {stats['total_visitas']}")
    print(f"Escolas visitadas: {stats['total_escolas_visitadas']}")

    if stats['escola_mais_visitada']:
        print(f"Escola mais visitada: {stats['escola_mais_visitada']} "
              f"({stats['max_visitas_escola']} visitas)")

    print("\nVisitas por escola:")
    for escola, count in sorted(stats['visitas_por_escola'].items(),
                                key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {escola:25}: {count} visitas")

    print("\n" + "=" * 80 + "\n")


def exemplo_8_gerar_relatorio():
    """Exemplo 8: Gerar relatório"""
    print("=" * 80)
    print("EXEMPLO 8: Gerando relatórios")
    print("=" * 80)

    gerenciador_visitas = GerenciadorVisitas()
    gerador_relatorios = GeradorRelatorios()

    visitas = gerenciador_visitas.listar_visitas()

    if visitas:
        # Relatório em texto
        print("\nGerando relatório em texto...")
        relatorio_texto = gerador_relatorios.gerar_relatorio_texto(visitas)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_txt = gerador_relatorios.salvar_relatorio_texto(
            relatorio_texto,
            f"relatorio_exemplo_{timestamp}.txt"
        )
        print(f"[OK] Relatório texto salvo: {arquivo_txt}")

        # Relatório Excel
        print("\nGerando relatório Excel...")
        arquivo_excel = gerador_relatorios.gerar_relatorio_excel(visitas)
        print(f"[OK] Relatório Excel salvo: {arquivo_excel}")

        # Estatísticas
        print("\nGerando relatório de estatísticas...")
        stats = gerenciador_visitas.obter_estatisticas()
        relatorio_stats = gerador_relatorios.gerar_relatorio_resumo(visitas, stats)

        arquivo_stats = gerador_relatorios.salvar_relatorio_texto(
            relatorio_stats,
            f"relatorio_estatisticas_{timestamp}.txt"
        )
        print(f"[OK] Relatório estatísticas salvo: {arquivo_stats}")
    else:
        print("\nNenhuma visita registrada para gerar relatórios")

    print("\n" + "=" * 80 + "\n")


def exemplo_9_escolas_sem_visita():
    """Exemplo 9: Listar escolas sem visita"""
    print("=" * 80)
    print("EXEMPLO 9: Escolas sem visita")
    print("=" * 80)

    gerenciador_escolas = GerenciadorEscolas()
    gerenciador_visitas = GerenciadorVisitas()
    gerador_relatorios = GeradorRelatorios()

    escolas_bloco1 = gerenciador_escolas.listar_escolas_bloco1()
    visitas = gerenciador_visitas.listar_visitas()

    escolas_sem_visita = gerador_relatorios.listar_escolas_sem_visita(
        escolas_bloco1,
        visitas
    )

    print(f"\nEscolas do Bloco 1: {len(escolas_bloco1)}")
    print(f"Escolas sem visita: {len(escolas_sem_visita)}")

    if escolas_sem_visita:
        print("\nLista de escolas que ainda precisam ser visitadas:\n")
        for i, escola in enumerate(escolas_sem_visita, 1):
            print(f"{i}. {escola}")
    else:
        print("\n✅ Todas as escolas do Bloco 1 já foram visitadas!")

    print("\n" + "=" * 80 + "\n")


def exemplo_10_workflow_completo():
    """Exemplo 10: Workflow completo de um dia de visitas"""
    print("=" * 80)
    print("EXEMPLO 10: Workflow completo - Simulando um dia de visitas")
    print("=" * 80)

    gerenciador_escolas = GerenciadorEscolas()
    gerenciador_visitas = GerenciadorVisitas()
    calculador = CalculadorDistancias()

    # 1. Planejar rota do dia
    print("\n1. PLANEJAMENTO DA ROTA DO DIA")
    print("-" * 80)

    escolas_visitar = ["CECAP", "Continental", "Chácaras Reunidas"]
    print(f"Escolas planejadas para hoje: {', '.join(escolas_visitar)}\n")

    escolas_objetos = []
    for nome in escolas_visitar:
        escola = gerenciador_escolas.buscar_escola(nome)
        if escola:
            escolas_objetos.append(escola)
            print(f"[OK] {escola['nome_usual']} ({escola['nome_oficial']})")

    # 2. Calcular distâncias entre as escolas
    print("\n2. CALCULANDO DISTÂNCIAS")
    print("-" * 80)

    for i in range(len(escolas_objetos) - 1):
        origem = escolas_objetos[i]
        destino = escolas_objetos[i + 1]

        if 'latitude' in origem and 'latitude' in destino:
            coords_origem = (origem['latitude'], origem['longitude'])
            coords_destino = (destino['latitude'], destino['longitude'])

            rota = calculador.calcular_distancia(coords_origem, coords_destino)

            if rota:
                print(f"{origem['nome_usual']} → {destino['nome_usual']}: "
                      f"{rota['distancia_km']} km, {rota['duracao_minutos']} min")

    # 3. Registrar visitas do dia
    print("\n3. REGISTRANDO VISITAS")
    print("-" * 80)

    observacoes_padrao = [
        "Acompanhamento de aulas. Observada boa participação dos alunos.",
        "Reunião com coordenação. Alinhadas estratégias pedagógicas.",
        "Verificação de infraestrutura. Solicitada manutenção preventiva."
    ]

    for i, escola in enumerate(escolas_objetos):
        visita = gerenciador_visitas.registrar_visita(
            escola_id=escola['id'],
            escola_nome=escola['nome_usual'],
            observacoes=observacoes_padrao[i % len(observacoes_padrao)]
        )
        print(f"[OK] Visita registrada: {escola['nome_usual']} (ID: {visita['id']})")

    # 4. Gerar relatório do dia
    print("\n4. GERANDO RELATÓRIO DO DIA")
    print("-" * 80)

    hoje = datetime.now().strftime("%Y-%m-%d")
    visitas_hoje = gerenciador_visitas.listar_visitas(
        data_inicio=hoje,
        data_fim=hoje
    )

    print(f"Total de visitas realizadas hoje: {len(visitas_hoje)}")
    print("\nResumo:")
    for visita in visitas_hoje:
        print(f"  - {visita['escola_nome']} às {visita['hora']}")

    print("\n" + "=" * 80 + "\n")


def main():
    """Executa todos os exemplos"""
    print("\n")
    print("=" * 80)
    print(" EXEMPLOS DE USO - SISTEMA DE GESTAO DE VISITAS ".center(80))
    print("=" * 80)
    print("\n")

    exemplos = [
        ("Listar escolas do Bloco 1", exemplo_1_listar_escolas),
        ("Geocodificar escola", exemplo_2_geocodificar_escola),
        ("Calcular distância entre escolas", exemplo_3_calcular_distancia),
        ("Encontrar escolas próximas", exemplo_4_escolas_proximas),
        ("Registrar visita", exemplo_5_registrar_visita),
        ("Listar visitas", exemplo_6_listar_visitas),
        ("Estatísticas", exemplo_7_estatisticas),
        ("Gerar relatórios", exemplo_8_gerar_relatorio),
        ("Escolas sem visita", exemplo_9_escolas_sem_visita),
        ("Workflow completo", exemplo_10_workflow_completo),
    ]

    print("Escolha um exemplo para executar:\n")
    for i, (nome, _) in enumerate(exemplos, 1):
        print(f"{i}. {nome}")
    print("0. Executar todos os exemplos")
    print()

    try:
        escolha = int(input("Digite o número do exemplo: ").strip())

        if escolha == 0:
            print("\nExecutando todos os exemplos...\n")
            for nome, funcao in exemplos:
                funcao()
        elif 1 <= escolha <= len(exemplos):
            print()
            exemplos[escolha - 1][1]()
        else:
            print("Opção inválida!")

    except ValueError:
        print("Valor inválido!")
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")


if __name__ == "__main__":
    main()
