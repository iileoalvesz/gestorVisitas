"""
Módulo para gerar relatórios das visitas
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from tabulate import tabulate
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


class GeradorRelatorios:
    def __init__(self, pasta_relatorios: str = "relatorios"):
        self.pasta_relatorios = pasta_relatorios
        os.makedirs(pasta_relatorios, exist_ok=True)

    def _formatar_data(self, data_str: str) -> str:
        """Formata data de YYYY-MM-DD para DD/MM/YYYY"""
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d")
            return data.strftime("%d/%m/%Y")
        except:
            return data_str

    def gerar_relatorio_texto(self, visitas: List[Dict],
                             escolas: Optional[List[Dict]] = None,
                             titulo: str = "Relatório de Visitas") -> str:
        """
        Gera relatório em formato texto

        Args:
            visitas: Lista de visitas
            escolas: Lista de escolas (opcional, para informações adicionais)
            titulo: Título do relatório

        Returns:
            String com relatório formatado
        """
        linhas = []
        linhas.append("=" * 80)
        linhas.append(titulo.center(80))
        linhas.append("=" * 80)
        linhas.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        linhas.append(f"Total de visitas: {len(visitas)}")
        linhas.append("=" * 80)
        linhas.append("")

        if not visitas:
            linhas.append("Nenhuma visita registrada.")
            return "\n".join(linhas)

        # Agrupa visitas por escola
        visitas_por_escola = {}
        for visita in visitas:
            escola_nome = visita['escola_nome']
            if escola_nome not in visitas_por_escola:
                visitas_por_escola[escola_nome] = []
            visitas_por_escola[escola_nome].append(visita)

        # Gera seção para cada escola
        for escola_nome in sorted(visitas_por_escola.keys()):
            visitas_escola = visitas_por_escola[escola_nome]

            linhas.append(f"\n📍 {escola_nome}")
            linhas.append("-" * 80)
            linhas.append(f"Total de visitas: {len(visitas_escola)}\n")

            for i, visita in enumerate(visitas_escola, 1):
                linhas.append(f"  Visita #{i}")
                linhas.append(f"  Data: {self._formatar_data(visita['data'])} às {visita['hora']}")

                if visita.get('observacoes'):
                    linhas.append(f"  Observações: {visita['observacoes']}")

                if visita.get('anexos'):
                    linhas.append(f"  Anexos: {len(visita['anexos'])} arquivo(s)")
                    for anexo in visita['anexos']:
                        linhas.append(f"    - {anexo['nome_original']}")

                linhas.append("")

        return "\n".join(linhas)

    def gerar_relatorio_excel(self, visitas: List[Dict],
                             arquivo: Optional[str] = None) -> str:
        """
        Gera relatório em formato Excel

        Args:
            visitas: Lista de visitas
            arquivo: Nome do arquivo (opcional)

        Returns:
            Caminho do arquivo gerado
        """
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"relatorio_visitas_{timestamp}.xlsx"

        caminho_completo = os.path.join(self.pasta_relatorios, arquivo)

        # Prepara dados para DataFrame
        dados = []
        for visita in visitas:
            dados.append({
                'ID': visita['id'],
                'Escola': visita['escola_nome'],
                'Data': self._formatar_data(visita['data']),
                'Hora': visita['hora'],
                'Observações': visita.get('observacoes', ''),
                'Nº Anexos': len(visita.get('anexos', []))
            })

        df = pd.DataFrame(dados)

        # Cria Excel writer
        with pd.ExcelWriter(caminho_completo, engine='openpyxl') as writer:
            # Aba principal com todas as visitas
            df.to_excel(writer, sheet_name='Todas as Visitas', index=False)

            # Aba com resumo por escola
            resumo_por_escola = df.groupby('Escola').agg({
                'ID': 'count',
                'Nº Anexos': 'sum'
            }).rename(columns={'ID': 'Total de Visitas', 'Nº Anexos': 'Total de Anexos'})

            resumo_por_escola.to_excel(writer, sheet_name='Resumo por Escola')

            # Aba com resumo por data
            resumo_por_data = df.groupby('Data').agg({
                'ID': 'count',
                'Escola': lambda x: ', '.join(sorted(set(x)))
            }).rename(columns={'ID': 'Nº Visitas', 'Escola': 'Escolas Visitadas'})

            resumo_por_data.to_excel(writer, sheet_name='Resumo por Data')

        return caminho_completo

    def gerar_relatorio_resumo(self, visitas: List[Dict],
                              estatisticas: Dict) -> str:
        """
        Gera relatório resumido com estatísticas

        Args:
            visitas: Lista de visitas
            estatisticas: Dicionário com estatísticas

        Returns:
            String com relatório formatado
        """
        linhas = []
        linhas.append("=" * 80)
        linhas.append("RELATÓRIO RESUMIDO - ESTATÍSTICAS".center(80))
        linhas.append("=" * 80)
        linhas.append("")

        linhas.append(f"📊 Total de visitas realizadas: {estatisticas['total_visitas']}")
        linhas.append(f"🏫 Total de escolas visitadas: {estatisticas['total_escolas_visitadas']}")

        if estatisticas['escola_mais_visitada']:
            linhas.append(f"⭐ Escola mais visitada: {estatisticas['escola_mais_visitada']} "
                         f"({estatisticas['max_visitas_escola']} visitas)")

        linhas.append("\n" + "-" * 80)
        linhas.append("VISITAS POR ESCOLA")
        linhas.append("-" * 80)

        # Tabela de visitas por escola
        dados_escola = []
        for escola, count in sorted(estatisticas['visitas_por_escola'].items(),
                                   key=lambda x: x[1], reverse=True):
            dados_escola.append([escola, count])

        tabela = tabulate(dados_escola, headers=['Escola', 'Nº Visitas'],
                         tablefmt='grid')
        linhas.append(tabela)

        if estatisticas['visitas_por_mes']:
            linhas.append("\n" + "-" * 80)
            linhas.append("VISITAS POR MÊS")
            linhas.append("-" * 80)

            dados_mes = []
            for mes, count in sorted(estatisticas['visitas_por_mes'].items()):
                try:
                    data = datetime.strptime(mes, "%Y-%m")
                    mes_formatado = data.strftime("%B/%Y")
                except:
                    mes_formatado = mes
                dados_mes.append([mes_formatado, count])

            tabela = tabulate(dados_mes, headers=['Mês', 'Nº Visitas'],
                             tablefmt='grid')
            linhas.append(tabela)

        return "\n".join(linhas)

    def gerar_relatorio_escola(self, escola_nome: str, visitas: List[Dict]) -> str:
        """
        Gera relatório específico para uma escola

        Args:
            escola_nome: Nome da escola
            visitas: Lista de visitas da escola

        Returns:
            String com relatório formatado
        """
        linhas = []
        linhas.append("=" * 80)
        linhas.append(f"RELATÓRIO DE VISITAS - {escola_nome}".center(80))
        linhas.append("=" * 80)
        linhas.append(f"Total de visitas: {len(visitas)}")
        linhas.append("=" * 80)
        linhas.append("")

        if not visitas:
            linhas.append("Nenhuma visita registrada para esta escola.")
            return "\n".join(linhas)

        # Ordena visitas por data
        visitas_ordenadas = sorted(visitas, key=lambda x: (x['data'], x['hora']))

        for i, visita in enumerate(visitas_ordenadas, 1):
            linhas.append(f"VISITA #{i}")
            linhas.append("-" * 80)
            linhas.append(f"ID: {visita['id']}")
            linhas.append(f"Data: {self._formatar_data(visita['data'])} às {visita['hora']}")

            if visita.get('observacoes'):
                linhas.append(f"\nObservações:")
                linhas.append(visita['observacoes'])

            if visita.get('anexos'):
                linhas.append(f"\nAnexos ({len(visita['anexos'])} arquivo(s)):")
                for anexo in visita['anexos']:
                    linhas.append(f"  - {anexo['nome_original']}")
                    linhas.append(f"    Localização: {anexo['caminho']}")

            linhas.append("=" * 80)
            linhas.append("")

        return "\n".join(linhas)

    def salvar_relatorio_texto(self, conteudo: str, nome_arquivo: str) -> str:
        """
        Salva relatório em arquivo de texto

        Args:
            conteudo: Conteúdo do relatório
            nome_arquivo: Nome do arquivo

        Returns:
            Caminho do arquivo gerado
        """
        if not nome_arquivo.endswith('.txt'):
            nome_arquivo += '.txt'

        caminho_completo = os.path.join(self.pasta_relatorios, nome_arquivo)

        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(conteudo)

        return caminho_completo

    def listar_escolas_sem_visita(self, todas_escolas: List[Dict],
                                  visitas: List[Dict]) -> List[str]:
        """
        Lista escolas que ainda não foram visitadas

        Args:
            todas_escolas: Lista de todas as escolas
            visitas: Lista de visitas realizadas

        Returns:
            Lista de nomes de escolas sem visita
        """
        escolas_visitadas = set(v['escola_nome'] for v in visitas)
        escolas_sem_visita = []

        for escola in todas_escolas:
            if escola['nome_usual'] not in escolas_visitadas:
                escolas_sem_visita.append(escola['nome_usual'])

        return sorted(escolas_sem_visita)

    def gerar_relatorio_word(self, visitas: List[Dict],
                            arquivo: Optional[str] = None) -> str:
        """
        Gera relatório em formato Word (.docx)

        Args:
            visitas: Lista de visitas
            arquivo: Nome do arquivo (opcional)

        Returns:
            Caminho do arquivo gerado
        """
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"relatorio_visitas_{timestamp}.docx"

        caminho_completo = os.path.join(self.pasta_relatorios, arquivo)

        # Cria documento
        doc = Document()

        # Adiciona título
        titulo = doc.add_heading('Relatório de Visitas às Escolas', 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Adiciona subtítulo com data e informações
        subtitulo = doc.add_paragraph()
        subtitulo.add_run(f'Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}\n').bold = True
        subtitulo.add_run(f'Total de visitas: {len(visitas)}').bold = True
        subtitulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()  # Espaço

        if not visitas:
            doc.add_paragraph('Nenhuma visita registrada.')
            doc.save(caminho_completo)
            return caminho_completo

        # Agrupa visitas por escola
        visitas_por_escola = {}
        for visita in visitas:
            escola_nome = visita['escola_nome']
            if escola_nome not in visitas_por_escola:
                visitas_por_escola[escola_nome] = []
            visitas_por_escola[escola_nome].append(visita)

        # Gera seção para cada escola
        for escola_nome in sorted(visitas_por_escola.keys()):
            visitas_escola = visitas_por_escola[escola_nome]

            # Título da escola
            heading_escola = doc.add_heading(f'📍 {escola_nome}', level=1)

            # Info da escola
            info = doc.add_paragraph()
            info.add_run(f'Total de visitas: {len(visitas_escola)}').italic = True

            # Lista cada visita
            for i, visita in enumerate(visitas_escola, 1):
                # Subtítulo da visita
                doc.add_heading(f'Visita #{i}', level=2)

                # Detalhes
                p_data = doc.add_paragraph()
                p_data.add_run('Data: ').bold = True
                p_data.add_run(f"{self._formatar_data(visita['data'])} às {visita['hora']}")

                # Mediador
                if visita.get('mediador_nome'):
                    p_mediador = doc.add_paragraph()
                    p_mediador.add_run('Mediador: ').bold = True
                    p_mediador.add_run(visita['mediador_nome'])

                # Observações
                if visita.get('observacoes'):
                    p_obs = doc.add_paragraph()
                    p_obs.add_run('Observações: ').bold = True
                    doc.add_paragraph(visita['observacoes'], style='Quote')

                # Anexos
                if visita.get('anexos'):
                    p_anexos = doc.add_paragraph()
                    p_anexos.add_run(f'Anexos ({len(visita["anexos"])} arquivo(s)): ').bold = True

                    for anexo in visita['anexos']:
                        doc.add_paragraph(
                            f"• {anexo['nome_original']}",
                            style='List Bullet'
                        )

                doc.add_paragraph()  # Espaço entre visitas

            # Quebra de página entre escolas
            doc.add_page_break()

        # Remove última quebra de página
        if len(doc.element.body) > 0:
            last_element = doc.element.body[-1]
            if last_element.tag.endswith('sectPr'):
                doc.element.body.remove(last_element)

        # Salva documento
        doc.save(caminho_completo)

        return caminho_completo

    def gerar_relatorio_consolidado(self, visitas: List[Dict],
                                    arquivo_template: str = None,
                                    arquivo: Optional[str] = None) -> str:
        """
        Gera relatório consolidado articulado com fotos usando template

        Args:
            visitas: Lista de visitas
            arquivo_template: Caminho do template Word (opcional)
            arquivo: Nome do arquivo de saída (opcional)

        Returns:
            Caminho do arquivo gerado
        """
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"relatorio_consolidado_{timestamp}.docx"

        caminho_completo = os.path.join(self.pasta_relatorios, arquivo)

        # Se houver template, usa ele; senão cria novo documento
        if arquivo_template and os.path.exists(arquivo_template):
            doc = Document(arquivo_template)
        else:
            doc = Document()

            # Se não há template, cria cabeçalho básico
            titulo = doc.add_heading('RELATÓRIO ARTICULADO PEDAGÓGICO DE ÁREA', 0)
            titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

            subtitulo = doc.add_paragraph()
            subtitulo.add_run('Convênio 24.480/2025').bold = True
            subtitulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Adiciona data de geração
        info = doc.add_paragraph()
        info.add_run(f'Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}\n').bold = True
        info.add_run(f'Total de visitas: {len(visitas)}').bold = True

        doc.add_paragraph()  # Espaço

        if not visitas:
            doc.add_paragraph('Nenhuma visita registrada.')
            doc.save(caminho_completo)
            return caminho_completo

        # Seção 1: Identificação
        doc.add_heading('1- IDENTIFICAÇÃO', level=1)

        # Tabela de articuladores (simplificada)
        mediadores_unicos = {}
        for visita in visitas:
            if visita.get('mediador_nome'):
                med_nome = visita['mediador_nome']
                escola = visita['escola_nome']
                if med_nome not in mediadores_unicos:
                    mediadores_unicos[med_nome] = escola

        if mediadores_unicos:
            doc.add_paragraph('Articuladores Pedagógicos de Área:')
            for i, (nome, escola) in enumerate(mediadores_unicos.items(), 1):
                doc.add_paragraph(f'{i}. {nome} - {escola}', style='List Bullet')

        doc.add_paragraph()

        # Seção 2: Descritivo de oficinas
        doc.add_heading('2- DESCRITIVO DE OFICINAS E ACOMPANHAMENTOS', level=1)

        # Agrupa visitas por escola
        visitas_por_escola = {}
        for visita in visitas:
            escola_nome = visita['escola_nome']
            if escola_nome not in visitas_por_escola:
                visitas_por_escola[escola_nome] = []
            visitas_por_escola[escola_nome].append(visita)

        for escola_nome in sorted(visitas_por_escola.keys()):
            visitas_escola = visitas_por_escola[escola_nome]

            doc.add_heading(f'Unidade Escolar: {escola_nome}', level=2)

            for i, visita in enumerate(visitas_escola, 1):
                p = doc.add_paragraph()
                p.add_run(f'Visita #{i} - ').bold = True
                p.add_run(f"{self._formatar_data(visita['data'])} às {visita['hora']}")

                if visita.get('mediador_nome'):
                    p_med = doc.add_paragraph()
                    p_med.add_run('Mediador: ').bold = True
                    p_med.add_run(visita['mediador_nome'])

                if visita.get('observacoes'):
                    doc.add_paragraph(visita['observacoes'])

                doc.add_paragraph()  # Espaço

        # Seção 3: Registro fotográfico
        doc.add_heading('3- REGISTRO FOTOGRÁFICO DAS ATIVIDADES DESENVOLVIDAS NAS OFICINAS', level=1)

        # Processa fotos das visitas
        for visita in visitas:
            if visita.get('anexos'):
                escola = visita['escola_nome']

                doc.add_paragraph()
                p_escola = doc.add_paragraph()
                p_escola.add_run(f'Unidade Escolar: {escola}').bold = True

                # Filtra apenas imagens
                imagens = [a for a in visita['anexos']
                          if a['nome_original'].lower().endswith(('.jpg', '.jpeg', '.png'))]

                if imagens:
                    # Adiciona até 4 imagens por página (2x2)
                    for idx, anexo in enumerate(imagens[:4]):
                        try:
                            # Monta caminho completo do anexo
                            caminho_anexo = os.path.join('static/uploads',
                                                        os.path.basename(anexo.get('caminho', '')))

                            if os.path.exists(caminho_anexo):
                                # Adiciona imagem com largura de 7cm (aproximadamente)
                                doc.add_picture(caminho_anexo, width=Inches(2.8))

                                # Adiciona legenda
                                p_legenda = doc.add_paragraph(anexo['nome_original'])
                                p_legenda.alignment = WD_ALIGN_PARAGRAPH.CENTER

                                # Quebra de linha a cada 2 imagens
                                if (idx + 1) % 2 == 0:
                                    doc.add_paragraph()
                        except Exception as e:
                            # Se não conseguir adicionar a imagem, continua
                            print(f"Erro ao adicionar imagem: {e}")
                            pass

                doc.add_paragraph()  # Espaço entre escolas

        # Salva documento
        doc.save(caminho_completo)

        return caminho_completo
