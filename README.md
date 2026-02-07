# Sistema de Gestão de Visitas às Escolas - Taubaté/SP

Sistema completo para gerenciar visitas às escolas de Taubaté, com matching de dados, geocodificação, cálculo de distâncias reais por carro e geração de relatórios.

## Funcionalidades

### 1. Gerenciamento de Escolas
- Matching automático entre nome oficial e nome usual das escolas
- Geocodificação automática usando OpenStreetMap (Nominatim)
- Lista de 52 escolas de Taubaté com foco no Bloco 1 (20 escolas)
- Busca por nome ou ID

### 2. Cálculo de Distâncias
- Usa OSRM (Open Source Routing Machine) para calcular rotas reais de carro
- Não usa linha direta - calcula rotas reais pelas ruas
- Matriz de distâncias entre todas as escolas do Bloco 1
- Busca de escolas próximas a uma referência
- Cálculo de distância entre duas escolas específicas

### 3. Registro de Visitas
- Registro de visitas com data, hora e observações
- Suporte para anexos/evidências (fotos, documentos, etc.)
- Armazenamento automático de anexos com organização por visita
- Busca de visitas por escola, período ou ID
- Estatísticas de visitas

### 4. Relatórios
- Relatório completo em texto
- Relatório em Excel com múltiplas abas
- Relatório de estatísticas (visitas por escola, por mês, etc.)
- Relatório por escola específica
- Lista de escolas sem visita

## Instalação

### Requisitos
- Python 3.8 ou superior

### Passo 1: Instalar dependências

```bash
cd gestor_visitas_escolas
pip install -r requirements.txt
```

### Passo 2: Executar o sistema

```bash
python main.py
```

## Uso

### Interface Interativa (Menu)

Execute `python main.py` para acessar o menu interativo com todas as funcionalidades.

#### Primeiro Uso - Configuração Inicial

1. **Geocodificar as Escolas do Bloco 1**
   - Menu: `1. Gerenciar Escolas` → `3. Geocodificar escolas do Bloco 1`
   - Aguarde alguns minutos (1 requisição por segundo para respeitar limites do serviço)
   - As coordenadas são salvas em `data/escolas.json`

2. **Calcular Matriz de Distâncias (Opcional)**
   - Menu: `5. Calcular Distâncias` → `1. Calcular matriz de distâncias`
   - Útil se você for consultar distâncias frequentemente
   - Salvo em `data/matriz_distancias.json`

#### Registrando Visitas

1. Menu: `2. Registrar Visita`
2. Selecione a escola visitada
3. Informe a data (ou deixe em branco para hoje)
4. Adicione observações
5. Anexe evidências (fotos, PDFs, etc.) se desejar

#### Gerando Relatórios

1. Menu: `4. Gerar Relatórios`
2. Escolha o tipo de relatório:
   - Completo em texto
   - Excel (múltiplas abas com análises)
   - Estatísticas
   - Por escola específica
3. Relatórios são salvos na pasta `relatorios/`

### Uso Programático

Você também pode usar os módulos diretamente em seus scripts:

```python
from escolas import GerenciadorEscolas
from visitas import GerenciadorVisitas
from distancias import CalculadorDistancias
from relatorios import GeradorRelatorios

# Inicializar gerenciadores
escolas = GerenciadorEscolas()
visitas = GerenciadorVisitas()
distancias = CalculadorDistancias()
relatorios = GeradorRelatorios()

# Listar escolas do Bloco 1
bloco1 = escolas.listar_escolas_bloco1()
print(f"Escolas do Bloco 1: {len(bloco1)}")

# Registrar uma visita
escola = escolas.buscar_escola("CECAP")
visita = visitas.registrar_visita(
    escola_id=escola['id'],
    escola_nome=escola['nome_usual'],
    observacoes="Reunião com coordenação pedagógica",
    anexos=["foto1.jpg", "ata_reuniao.pdf"]
)

# Calcular distância entre duas escolas
escola1 = escolas.buscar_escola("CECAP")
escola2 = escolas.buscar_escola("Continental")

coords1 = (escola1['latitude'], escola1['longitude'])
coords2 = (escola2['latitude'], escola2['longitude'])

rota = distancias.calcular_distancia(coords1, coords2)
print(f"Distância: {rota['distancia_km']} km")
print(f"Tempo: {rota['duracao_minutos']} minutos")

# Gerar relatório Excel
todas_visitas = visitas.listar_visitas()
arquivo_excel = relatorios.gerar_relatorio_excel(todas_visitas)
print(f"Relatório gerado: {arquivo_excel}")
```

Veja `exemplo_uso.py` para mais exemplos.

## Estrutura de Dados

### Escolas do Bloco 1

Com base nos anexos fornecidos, as seguintes escolas foram identificadas para o Bloco 1:

1. Bela Vista
2. CECAP
3. Chácaras Reunidas
4. Continental
5. Coronel
6. Ezequiel
7. Fonte II
8. Itaim
9. Jaboticabeiras
10. Juvenal
11. Marlene Miranda
12. Monte Belo
13. Novo Horizonte
14. Ramon
15. Santa Luzia
16. Santa Luzia Rural
17. Santa Tereza
18. São Gonçalo
19. Vila Velha
20. Vila Caetano

## Estrutura de Pastas

```
gestor_visitas_escolas/
├── main.py                 # Interface principal do sistema
├── escolas.py             # Gerenciamento de escolas
├── visitas.py             # Gerenciamento de visitas
├── distancias.py          # Cálculo de distâncias com OSRM
├── relatorios.py          # Geração de relatórios
├── requirements.txt       # Dependências do projeto
├── README.md             # Este arquivo
├── exemplo_uso.py        # Exemplos de uso programático
├── data/                 # Dados do sistema
│   ├── escolas.json      # Escolas com coordenadas
│   ├── visitas.json      # Registro de visitas
│   └── matriz_distancias.json  # Matriz pré-calculada (opcional)
├── anexos/               # Evidências das visitas
│   └── [ID_VISITA]/      # Uma pasta por visita
└── relatorios/           # Relatórios gerados
```

## Serviços Utilizados

### Geocodificação
- **Nominatim (OpenStreetMap)**: Geocodificação gratuita
- Limite: 1 requisição por segundo
- Não requer API key

### Cálculo de Rotas
- **OSRM (Open Source Routing Machine)**: Servidor público gratuito
- Calcula rotas reais de carro (não linha direta)
- URL padrão: `http://router.project-osrm.org`
- Alternativa: `https://routing.openstreetmap.de/routed-car`

## Limitações e Considerações

1. **Geocodificação**:
   - Pode não encontrar algumas escolas com precisão exata
   - Resultados baseados em dados do OpenStreetMap
   - Recomenda-se verificar coordenadas críticas manualmente

2. **Cálculo de Distâncias**:
   - Usa servidor público do OSRM (pode ter indisponibilidade ocasional)
   - Para uso intensivo, considere hospedar seu próprio servidor OSRM
   - Distâncias são estimativas baseadas em rotas

3. **Armazenamento**:
   - Dados salvos em arquivos JSON localmente
   - Anexos copiados para pasta do projeto
   - Sem banco de dados (adequado para uso individual/pequena equipe)

## Troubleshooting

### Erro ao geocodificar
- Verifique conexão com internet
- Aguarde 1 segundo entre requisições
- Algumas escolas podem não ser encontradas automaticamente

### Erro ao calcular distâncias
- Verifique se as escolas têm coordenadas (execute geocodificação primeiro)
- Teste conectividade com: `http://router.project-osrm.org`
- Considere usar servidor alternativo em `distancias.py`

### Anexos não encontrados
- Use caminhos absolutos ao adicionar anexos
- Verifique permissões de leitura dos arquivos

## Melhorias Futuras

- [ ] Interface web com Flask/Django
- [ ] Banco de dados (SQLite/PostgreSQL)
- [ ] Exportação para PDF
- [ ] Mapas interativos com visualização de rotas
- [ ] Sincronização em nuvem
- [ ] App mobile
- [ ] Notificações de escolas não visitadas

## Licença

Este projeto foi desenvolvido para uso interno de supervisão de escolas de Taubaté/SP.

## Suporte

Para dúvidas ou problemas, consulte a documentação dos módulos individuais ou entre em contato com o desenvolvedor.
