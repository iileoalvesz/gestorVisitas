# Guia de Inicialização - Sistema Web

## Instalação das Dependências

```bash
cd gestor_visitas_escolas
pip install -r requirements.txt
```

## Executar o Sistema Web

```bash
python app.py
```

O sistema estará disponível em: **http://localhost:5000**

## Acesso Rápido

Após iniciar o servidor, abra seu navegador e acesse:

- **Dashboard**: http://localhost:5000
- **Escolas**: http://localhost:5000/escolas
- **Visitas**: http://localhost:5000/visitas
- **Mapa Interativo**: http://localhost:5000/mapa
- **Distâncias**: http://localhost:5000/distancias
- **Relatórios**: http://localhost:5000/relatorios

## Funcionalidades Disponíveis

### 1. Dashboard (Página Inicial)
- Estatísticas gerais de visitas
- Escolas mais visitadas
- Ações rápidas
- Visão geral do sistema

### 2. Gerenciamento de Escolas
- Lista de todas as 20 escolas do Bloco 1
- Visualização de coordenadas
- Link direto para registrar visita
- Integração com mapa

### 3. Registro de Visitas
- Formulário intuitivo para registrar visitas
- Upload de anexos/evidências (fotos, PDFs)
- Seleção de data
- Campo de observações

### 4. Visualização de Visitas
- Lista completa de visitas registradas
- Filtros por escola e período
- Visualização de anexos
- Detalhes completos de cada visita

### 5. Mapa Interativo
- Visualização de todas as escolas no mapa
- Marcadores clicáveis com informações
- Cálculo de rotas entre escolas
- Zoom e navegação

### 6. Cálculo de Distâncias
- Calcular distância real de carro entre duas escolas
- Tempo estimado de viagem
- Escolas próximas a uma referência
- Usa OSRM para rotas reais

### 7. Relatórios
- Gerar relatórios em Excel
- Gerar relatórios em texto
- Filtros por escola e período
- Download direto dos arquivos

## APIs Disponíveis

### Escolas
- `GET /api/escolas` - Lista todas as escolas
- `GET /api/escolas/<id>` - Detalhes de uma escola

### Visitas
- `GET /api/visitas` - Lista visitas (com filtros opcionais)
- `POST /api/visitas` - Cria nova visita
- `GET /api/visitas/<id>` - Detalhes de uma visita

### Distâncias
- `POST /api/distancia` - Calcula distância entre duas escolas
  ```json
  {
    "escola1_id": 1,
    "escola2_id": 2
  }
  ```
- `GET /api/escolas/<id>/proximas?limite=5` - Escolas próximas

### Estatísticas
- `GET /api/estatisticas` - Estatísticas gerais

### Relatórios
- `POST /api/relatorios/excel` - Gera relatório Excel
- `POST /api/relatorios/texto` - Gera relatório TXT

## Estrutura do Projeto Web

```
gestor_visitas_escolas/
├── app.py                 # Aplicação Flask principal
├── escolas.py             # Backend - Gerenciamento de escolas
├── visitas.py             # Backend - Registro de visitas
├── distancias.py          # Backend - Cálculo de distâncias
├── relatorios.py          # Backend - Geração de relatórios
├── templates/             # Templates HTML
│   ├── base.html          # Layout base
│   ├── index.html         # Dashboard
│   ├── escolas.html       # Lista de escolas
│   ├── nova_visita.html   # Formulário de visita
│   ├── visitas.html       # Lista de visitas
│   ├── mapa.html          # Mapa interativo
│   ├── distancias.html    # Cálculo de distâncias
│   └── relatorios.html    # Geração de relatórios
├── static/                # Arquivos estáticos
│   ├── css/              # CSS customizado
│   ├── js/               # JavaScript
│   └── uploads/          # Uploads de anexos
├── data/                  # Dados JSON
└── anexos/                # Evidências das visitas
```

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5
- **Mapas**: Leaflet.js + OpenStreetMap
- **Ícones**: Bootstrap Icons
- **Rotas**: OSRM (Open Source Routing Machine)
- **Geocoding**: Nominatim (OpenStreetMap)

## Dicas de Uso

1. **Primeira Vez**: Os dados das 20 escolas do Bloco 1 já estão geocodificados e prontos para uso

2. **Registrar Visita**:
   - Acesse "Visitas" > Botão "Nova Visita"
   - Ou clique em "+" ao lado de uma escola na lista

3. **Ver Mapa**:
   - Clique em "Mapa" no menu
   - Clique nos marcadores para ver informações
   - Use o zoom para navegar

4. **Calcular Distâncias**:
   - Acesse "Distâncias"
   - Selecione duas escolas
   - Veja a distância real de carro e tempo estimado

5. **Gerar Relatórios**:
   - Acesse "Relatórios"
   - Escolha o formato (Excel ou Texto)
   - Aplique filtros se necessário
   - Clique em "Gerar" para download

## Solução de Problemas

### Porta 5000 já em uso
Se a porta 5000 estiver ocupada, edite `app.py` e altere:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use outra porta
```

### Erro ao fazer upload de arquivos
Verifique se a pasta `static/uploads` existe:
```bash
mkdir -p static/uploads
```

### Mapas não carregam
- Verifique sua conexão com a internet
- Os mapas usam OpenStreetMap (online)

## Modo de Produção

Para usar em produção, use um servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Ou use o arquivo `run_production.py` (a ser criado).

## Suporte

Para dúvidas ou problemas:
1. Verifique este guia
2. Consulte o README.md principal
3. Execute `python teste_rapido.py` para verificar o sistema

---

**Sistema pronto para uso!** Inicie com `python app.py` e acesse http://localhost:5000
