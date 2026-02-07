"""
Sistema de Gestão de Visitas às Escolas de Taubaté
"""
import os
import sys
from datetime import datetime
from tabulate import tabulate

from escolas import GerenciadorEscolas
from distancias import CalculadorDistancias
from visitas import GerenciadorVisitas
from relatorios import GeradorRelatorios


class SistemaGestaoVisitas:
    def __init__(self):
        self.gerenciador_escolas = GerenciadorEscolas()
        self.calculador_distancias = CalculadorDistancias()
        self.gerenciador_visitas = GerenciadorVisitas()
        self.gerador_relatorios = GeradorRelatorios()

    def limpar_tela(self):
        """Limpa a tela do console"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def pausar(self):
        """Pausa execução aguardando enter"""
        input("\nPressione ENTER para continuar...")

    def menu_principal(self):
        """Exibe menu principal"""
        while True:
            self.limpar_tela()
            print("=" * 80)
            print("SISTEMA DE GESTÃO DE VISITAS ÀS ESCOLAS - TAUBATÉ/SP".center(80))
            print("=" * 80)
            print("\n1. Gerenciar Escolas")
            print("2. Registrar Visita")
            print("3. Visualizar Visitas")
            print("4. Gerar Relatórios")
            print("5. Calcular Distâncias")
            print("0. Sair")
            print("\n" + "-" * 80)

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == '1':
                self.menu_escolas()
            elif opcao == '2':
                self.registrar_visita()
            elif opcao == '3':
                self.menu_visualizar_visitas()
            elif opcao == '4':
                self.menu_relatorios()
            elif opcao == '5':
                self.menu_distancias()
            elif opcao == '0':
                print("\nEncerrando sistema...")
                sys.exit(0)
            else:
                print("\nOpção inválida!")
                self.pausar()

    def menu_escolas(self):
        """Menu de gerenciamento de escolas"""
        while True:
            self.limpar_tela()
            print("=" * 80)
            print("GERENCIAR ESCOLAS".center(80))
            print("=" * 80)
            print("\n1. Listar escolas do Bloco 1")
            print("2. Buscar escola")
            print("3. Geocodificar escolas do Bloco 1")
            print("4. Listar todas as escolas")
            print("0. Voltar")

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == '1':
                self.listar_escolas_bloco1()
            elif opcao == '2':
                self.buscar_escola()
            elif opcao == '3':
                self.geocodificar_escolas()
            elif opcao == '4':
                self.listar_todas_escolas()
            elif opcao == '0':
                break
            else:
                print("\nOpção inválida!")
                self.pausar()

    def listar_escolas_bloco1(self):
        """Lista escolas do Bloco 1"""
        self.limpar_tela()
        print("=" * 80)
        print("ESCOLAS DO BLOCO 1".center(80))
        print("=" * 80)

        escolas = self.gerenciador_escolas.listar_escolas_bloco1()

        dados = []
        for escola in escolas:
            tem_coords = 'latitude' in escola and 'longitude' in escola
            status_coords = "✓" if tem_coords else "✗"

            dados.append([
                escola['id'],
                escola['nome_usual'],
                escola['nome_oficial'][:50] + "..." if len(escola['nome_oficial']) > 50 else escola['nome_oficial'],
                status_coords
            ])

        print(tabulate(dados, headers=['ID', 'Nome Usual', 'Nome Oficial', 'Coords'],
                      tablefmt='grid'))

        print(f"\nTotal: {len(escolas)} escolas")
        self.pausar()

    def buscar_escola(self):
        """Busca uma escola"""
        self.limpar_tela()
        print("=" * 80)
        print("BUSCAR ESCOLA".center(80))
        print("=" * 80)

        termo = input("\nDigite o nome ou ID da escola: ").strip()

        escola = self.gerenciador_escolas.buscar_escola(termo)

        if escola:
            print("\n✓ Escola encontrada:\n")
            print(f"ID: {escola['id']}")
            print(f"Nome Oficial: {escola['nome_oficial']}")
            print(f"Nome Usual: {escola['nome_usual']}")

            if 'latitude' in escola and 'longitude' in escola:
                print(f"Coordenadas: ({escola['latitude']:.6f}, {escola['longitude']:.6f})")
            else:
                print("Coordenadas: Não disponíveis")
        else:
            print("\n✗ Escola não encontrada")

        self.pausar()

    def geocodificar_escolas(self):
        """Geocodifica todas as escolas do Bloco 1"""
        self.limpar_tela()
        print("=" * 80)
        print("GEOCODIFICAR ESCOLAS DO BLOCO 1".center(80))
        print("=" * 80)
        print("\nEsta operação pode demorar alguns minutos...")
        print("As coordenadas serão obtidas do OpenStreetMap.\n")

        confirma = input("Deseja continuar? (s/n): ").strip().lower()

        if confirma == 's':
            print()
            self.gerenciador_escolas.geocodificar_todas_bloco1()
            self.pausar()

    def listar_todas_escolas(self):
        """Lista todas as escolas cadastradas"""
        self.limpar_tela()
        print("=" * 80)
        print("TODAS AS ESCOLAS CADASTRADAS".center(80))
        print("=" * 80)

        dados = []
        for escola in self.gerenciador_escolas.escolas:
            dados.append([
                escola['id'],
                escola['nome_usual'],
                escola['nome_oficial'][:45] + "..." if len(escola['nome_oficial']) > 45 else escola['nome_oficial']
            ])

        print(tabulate(dados, headers=['ID', 'Nome Usual', 'Nome Oficial'],
                      tablefmt='grid'))

        print(f"\nTotal: {len(self.gerenciador_escolas.escolas)} escolas")
        self.pausar()

    def registrar_visita(self):
        """Registra uma nova visita"""
        self.limpar_tela()
        print("=" * 80)
        print("REGISTRAR VISITA".center(80))
        print("=" * 80)

        # Mostra escolas do Bloco 1
        escolas = self.gerenciador_escolas.listar_escolas_bloco1()

        print("\nEscolas disponíveis:")
        for i, escola in enumerate(escolas, 1):
            print(f"{i}. {escola['nome_usual']}")

        print("\n" + "-" * 80)

        # Seleciona escola
        try:
            escolha = int(input("\nNúmero da escola visitada: ").strip())
            if escolha < 1 or escolha > len(escolas):
                print("Opção inválida!")
                self.pausar()
                return

            escola = escolas[escolha - 1]
        except ValueError:
            print("Valor inválido!")
            self.pausar()
            return

        # Data da visita
        data_input = input(f"Data da visita (YYYY-MM-DD) [hoje: {datetime.now().strftime('%Y-%m-%d')}]: ").strip()
        data = data_input if data_input else None

        # Observações
        print("\nObservações sobre a visita:")
        observacoes = input("> ").strip()

        # Anexos
        anexos = []
        print("\nDeseja adicionar anexos/evidências? (s/n): ", end='')
        if input().strip().lower() == 's':
            print("Digite os caminhos dos arquivos (um por linha, linha vazia para finalizar):")
            while True:
                caminho = input("> ").strip()
                if not caminho:
                    break
                if os.path.exists(caminho):
                    anexos.append(caminho)
                    print(f"  ✓ Arquivo adicionado: {os.path.basename(caminho)}")
                else:
                    print(f"  ✗ Arquivo não encontrado: {caminho}")

        # Registra visita
        print("\nRegistrando visita...")
        visita = self.gerenciador_visitas.registrar_visita(
            escola_id=escola['id'],
            escola_nome=escola['nome_usual'],
            data=data,
            observacoes=observacoes,
            anexos=anexos if anexos else None
        )

        print(f"\n✅ Visita registrada com sucesso!")
        print(f"ID da visita: {visita['id']}")
        self.pausar()

    def menu_visualizar_visitas(self):
        """Menu para visualizar visitas"""
        while True:
            self.limpar_tela()
            print("=" * 80)
            print("VISUALIZAR VISITAS".center(80))
            print("=" * 80)
            print("\n1. Listar todas as visitas")
            print("2. Listar visitas por escola")
            print("3. Listar visitas por período")
            print("4. Ver detalhes de uma visita")
            print("0. Voltar")

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == '1':
                self.listar_todas_visitas()
            elif opcao == '2':
                self.listar_visitas_por_escola()
            elif opcao == '3':
                self.listar_visitas_por_periodo()
            elif opcao == '4':
                self.ver_detalhes_visita()
            elif opcao == '0':
                break
            else:
                print("\nOpção inválida!")
                self.pausar()

    def listar_todas_visitas(self):
        """Lista todas as visitas"""
        self.limpar_tela()
        print("=" * 80)
        print("TODAS AS VISITAS".center(80))
        print("=" * 80)

        visitas = self.gerenciador_visitas.listar_visitas()

        if not visitas:
            print("\nNenhuma visita registrada.")
        else:
            dados = []
            for visita in visitas:
                dados.append([
                    visita['id'],
                    visita['escola_nome'],
                    visita['data'],
                    visita['hora'],
                    len(visita.get('anexos', []))
                ])

            print(tabulate(dados, headers=['ID', 'Escola', 'Data', 'Hora', 'Anexos'],
                          tablefmt='grid'))
            print(f"\nTotal: {len(visitas)} visitas")

        self.pausar()

    def listar_visitas_por_escola(self):
        """Lista visitas de uma escola específica"""
        self.limpar_tela()
        print("=" * 80)
        print("VISITAS POR ESCOLA".center(80))
        print("=" * 80)

        termo = input("\nDigite o nome ou ID da escola: ").strip()
        escola = self.gerenciador_escolas.buscar_escola(termo)

        if not escola:
            print("✗ Escola não encontrada")
            self.pausar()
            return

        visitas = self.gerenciador_visitas.listar_visitas(escola_id=escola['id'])

        print(f"\nVisitas à escola: {escola['nome_usual']}")
        print("-" * 80)

        if not visitas:
            print("\nNenhuma visita registrada para esta escola.")
        else:
            dados = []
            for visita in visitas:
                dados.append([
                    visita['data'],
                    visita['hora'],
                    visita.get('observacoes', '')[:50],
                    len(visita.get('anexos', []))
                ])

            print(tabulate(dados, headers=['Data', 'Hora', 'Observações', 'Anexos'],
                          tablefmt='grid'))
            print(f"\nTotal: {len(visitas)} visitas")

        self.pausar()

    def listar_visitas_por_periodo(self):
        """Lista visitas em um período"""
        self.limpar_tela()
        print("=" * 80)
        print("VISITAS POR PERÍODO".center(80))
        print("=" * 80)

        data_inicio = input("\nData inicial (YYYY-MM-DD): ").strip()
        data_fim = input("Data final (YYYY-MM-DD): ").strip()

        visitas = self.gerenciador_visitas.listar_visitas(
            data_inicio=data_inicio if data_inicio else None,
            data_fim=data_fim if data_fim else None
        )

        print(f"\nPeríodo: {data_inicio or 'início'} até {data_fim or 'hoje'}")
        print("-" * 80)

        if not visitas:
            print("\nNenhuma visita encontrada neste período.")
        else:
            dados = []
            for visita in visitas:
                dados.append([
                    visita['escola_nome'],
                    visita['data'],
                    visita['hora'],
                    len(visita.get('anexos', []))
                ])

            print(tabulate(dados, headers=['Escola', 'Data', 'Hora', 'Anexos'],
                          tablefmt='grid'))
            print(f"\nTotal: {len(visitas)} visitas")

        self.pausar()

    def ver_detalhes_visita(self):
        """Mostra detalhes de uma visita"""
        self.limpar_tela()
        print("=" * 80)
        print("DETALHES DA VISITA".center(80))
        print("=" * 80)

        id_visita = input("\nID da visita: ").strip()
        visita = self.gerenciador_visitas.obter_visita(id_visita)

        if not visita:
            print("✗ Visita não encontrada")
        else:
            print(f"\nID: {visita['id']}")
            print(f"Escola: {visita['escola_nome']}")
            print(f"Data: {visita['data']} às {visita['hora']}")
            print(f"\nObservações:\n{visita.get('observacoes', 'Nenhuma')}")

            if visita.get('anexos'):
                print(f"\nAnexos ({len(visita['anexos'])}):")
                for anexo in visita['anexos']:
                    print(f"  - {anexo['nome_original']}")
                    print(f"    Caminho: {anexo['caminho']}")

        self.pausar()

    def menu_relatorios(self):
        """Menu de relatórios"""
        while True:
            self.limpar_tela()
            print("=" * 80)
            print("GERAR RELATÓRIOS".center(80))
            print("=" * 80)
            print("\n1. Relatório completo (texto)")
            print("2. Relatório em Excel")
            print("3. Relatório de estatísticas")
            print("4. Relatório por escola")
            print("5. Listar escolas sem visita")
            print("0. Voltar")

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == '1':
                self.gerar_relatorio_texto()
            elif opcao == '2':
                self.gerar_relatorio_excel()
            elif opcao == '3':
                self.gerar_relatorio_estatisticas()
            elif opcao == '4':
                self.gerar_relatorio_escola()
            elif opcao == '5':
                self.listar_escolas_sem_visita()
            elif opcao == '0':
                break
            else:
                print("\nOpção inválida!")
                self.pausar()

    def gerar_relatorio_texto(self):
        """Gera relatório completo em texto"""
        visitas = self.gerenciador_visitas.listar_visitas()

        relatorio = self.gerador_relatorios.gerar_relatorio_texto(visitas)

        print("\n" + relatorio)

        salvar = input("\nDeseja salvar em arquivo? (s/n): ").strip().lower()
        if salvar == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = self.gerador_relatorios.salvar_relatorio_texto(
                relatorio,
                f"relatorio_completo_{timestamp}.txt"
            )
            print(f"\n✅ Relatório salvo em: {arquivo}")

        self.pausar()

    def gerar_relatorio_excel(self):
        """Gera relatório em Excel"""
        visitas = self.gerenciador_visitas.listar_visitas()

        if not visitas:
            print("\nNenhuma visita para gerar relatório.")
            self.pausar()
            return

        print("\nGerando relatório Excel...")
        arquivo = self.gerador_relatorios.gerar_relatorio_excel(visitas)

        print(f"\n✅ Relatório Excel gerado: {arquivo}")
        self.pausar()

    def gerar_relatorio_estatisticas(self):
        """Gera relatório de estatísticas"""
        visitas = self.gerenciador_visitas.listar_visitas()
        estatisticas = self.gerenciador_visitas.obter_estatisticas()

        relatorio = self.gerador_relatorios.gerar_relatorio_resumo(visitas, estatisticas)

        print("\n" + relatorio)

        salvar = input("\nDeseja salvar em arquivo? (s/n): ").strip().lower()
        if salvar == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = self.gerador_relatorios.salvar_relatorio_texto(
                relatorio,
                f"relatorio_estatisticas_{timestamp}.txt"
            )
            print(f"\n✅ Relatório salvo em: {arquivo}")

        self.pausar()

    def gerar_relatorio_escola(self):
        """Gera relatório de uma escola específica"""
        termo = input("\nDigite o nome ou ID da escola: ").strip()
        escola = self.gerenciador_escolas.buscar_escola(termo)

        if not escola:
            print("✗ Escola não encontrada")
            self.pausar()
            return

        visitas = self.gerenciador_visitas.listar_visitas(escola_id=escola['id'])
        relatorio = self.gerador_relatorios.gerar_relatorio_escola(
            escola['nome_usual'],
            visitas
        )

        print("\n" + relatorio)

        salvar = input("\nDeseja salvar em arquivo? (s/n): ").strip().lower()
        if salvar == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_{escola['nome_usual'].replace(' ', '_')}_{timestamp}.txt"
            arquivo = self.gerador_relatorios.salvar_relatorio_texto(relatorio, nome_arquivo)
            print(f"\n✅ Relatório salvo em: {arquivo}")

        self.pausar()

    def listar_escolas_sem_visita(self):
        """Lista escolas que ainda não foram visitadas"""
        escolas_bloco1 = self.gerenciador_escolas.listar_escolas_bloco1()
        visitas = self.gerenciador_visitas.listar_visitas()

        escolas_sem_visita = self.gerador_relatorios.listar_escolas_sem_visita(
            escolas_bloco1,
            visitas
        )

        print("\n" + "=" * 80)
        print("ESCOLAS SEM VISITA".center(80))
        print("=" * 80)

        if not escolas_sem_visita:
            print("\n✅ Todas as escolas do Bloco 1 já foram visitadas!")
        else:
            print(f"\nTotal: {len(escolas_sem_visita)} escolas\n")
            for i, escola in enumerate(escolas_sem_visita, 1):
                print(f"{i}. {escola}")

        self.pausar()

    def menu_distancias(self):
        """Menu de cálculo de distâncias"""
        while True:
            self.limpar_tela()
            print("=" * 80)
            print("CALCULAR DISTÂNCIAS".center(80))
            print("=" * 80)
            print("\n1. Calcular matriz de distâncias (Bloco 1)")
            print("2. Ver escolas próximas")
            print("3. Calcular distância entre duas escolas")
            print("0. Voltar")

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == '1':
                self.calcular_matriz_distancias()
            elif opcao == '2':
                self.ver_escolas_proximas()
            elif opcao == '3':
                self.calcular_distancia_entre_duas()
            elif opcao == '0':
                break
            else:
                print("\nOpção inválida!")
                self.pausar()

    def calcular_matriz_distancias(self):
        """Calcula matriz de distâncias entre todas as escolas do Bloco 1"""
        self.limpar_tela()
        print("=" * 80)
        print("CALCULAR MATRIZ DE DISTÂNCIAS".center(80))
        print("=" * 80)
        print("\nEsta operação pode demorar vários minutos...")
        print("Serão calculadas as rotas reais de carro usando OSRM.\n")

        confirma = input("Deseja continuar? (s/n): ").strip().lower()

        if confirma != 's':
            return

        escolas = self.gerenciador_escolas.listar_escolas_bloco1()

        # Verifica se todas têm coordenadas
        sem_coords = [e for e in escolas if 'latitude' not in e or 'longitude' not in e]
        if sem_coords:
            print(f"\n⚠️  {len(sem_coords)} escola(s) sem coordenadas.")
            print("Execute a geocodificação primeiro (Menu Escolas > Geocodificar).")
            self.pausar()
            return

        print()
        matriz = self.calculador_distancias.calcular_matriz_distancias(escolas)
        self.calculador_distancias.salvar_matriz(matriz)

        self.pausar()

    def ver_escolas_proximas(self):
        """Mostra escolas próximas a uma escola de referência"""
        self.limpar_tela()
        print("=" * 80)
        print("ESCOLAS PRÓXIMAS".center(80))
        print("=" * 80)

        termo = input("\nDigite o nome ou ID da escola de referência: ").strip()
        escola = self.gerenciador_escolas.buscar_escola(termo)

        if not escola:
            print("✗ Escola não encontrada")
            self.pausar()
            return

        if 'latitude' not in escola or 'longitude' not in escola:
            print("✗ Escola sem coordenadas. Execute a geocodificação primeiro.")
            self.pausar()
            return

        escolas_bloco1 = self.gerenciador_escolas.listar_escolas_bloco1()

        print(f"\nCalculando escolas próximas a: {escola['nome_usual']}")
        print("Aguarde...\n")

        proximas = self.calculador_distancias.encontrar_escolas_proximas(
            escola,
            escolas_bloco1,
            limite=10
        )

        if proximas:
            dados = []
            for item in proximas:
                dados.append([
                    item['escola']['nome_usual'],
                    f"{item['distancia_km']} km",
                    f"{item['duracao_minutos']} min"
                ])

            print(tabulate(dados, headers=['Escola', 'Distância', 'Tempo'],
                          tablefmt='grid'))
        else:
            print("Nenhuma escola próxima encontrada.")

        self.pausar()

    def calcular_distancia_entre_duas(self):
        """Calcula distância entre duas escolas específicas"""
        self.limpar_tela()
        print("=" * 80)
        print("DISTÂNCIA ENTRE DUAS ESCOLAS".center(80))
        print("=" * 80)

        termo1 = input("\nEscola 1 (nome ou ID): ").strip()
        escola1 = self.gerenciador_escolas.buscar_escola(termo1)

        if not escola1:
            print("✗ Escola 1 não encontrada")
            self.pausar()
            return

        termo2 = input("Escola 2 (nome ou ID): ").strip()
        escola2 = self.gerenciador_escolas.buscar_escola(termo2)

        if not escola2:
            print("✗ Escola 2 não encontrada")
            self.pausar()
            return

        if 'latitude' not in escola1 or 'latitude' not in escola2:
            print("✗ Uma ou mais escolas sem coordenadas.")
            self.pausar()
            return

        coords1 = (escola1['latitude'], escola1['longitude'])
        coords2 = (escola2['latitude'], escola2['longitude'])

        print("\nCalculando rota...")
        rota = self.calculador_distancias.calcular_distancia(coords1, coords2)

        if rota:
            print("\n" + "-" * 80)
            print(f"{escola1['nome_usual']} → {escola2['nome_usual']}")
            print("-" * 80)
            print(f"Distância: {rota['distancia_km']} km")
            print(f"Tempo estimado: {rota['duracao_minutos']} minutos")
            print("-" * 80)
        else:
            print("✗ Erro ao calcular rota")

        self.pausar()


def main():
    """Função principal"""
    sistema = SistemaGestaoVisitas()
    sistema.menu_principal()


if __name__ == "__main__":
    main()
