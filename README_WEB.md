# Sistema Web de Gestão de Visitas às Escolas - Taubaté/SP

## Sistema Completamente Web com Interface Moderna

### Visão Geral

Sistema web completo para gerenciar visitas às escolas de Taubaté/SP com interface moderna e intuitiva.

**Tecnologias:**
- Backend: Flask (Python)
- Frontend: Bootstrap 5 + JavaScript
- Mapas: Leaflet.js + OpenStreetMap
- Rotas: OSRM (Open Source Routing Machine)

### Como Iniciar

#### 1. Instalação (Apenas na Primeira Vez)

```bash
cd gestor_visitas_escolas

# Instalar dependências
pip install -r requirements.txt

# Configurar dados iniciais (geocodificar escolas)
python setup_auto.py
```

#### 2. Iniciar o Sistema Web

```bash
# Opção 1: Script de inicialização (recomendado)
python iniciar_web.py

# Opção 2: Diretamente
python app.py
```

#### 3. Acessar o Sistema

Abra seu navegador e acesse: **http://localhost:5000**

### Funcionalidades do Sistema Web

#### Dashboard (Página Inicial)
- Estatísticas em tempo real
- Total de visitas realizadas
- Escolas visitadas vs pendentes
- Escola mais visitada
- Visitas por mês
- Ações rápidas para principais tarefas

#### Gerenciamento de Escolas
- **URL:** `/escolas`
- Lista completa das 20 escolas do Bloco 1
- Visualização de coordenadas GPS
- Botão direto para registrar visita
- Link para visualizar no mapa
- Filtros e busca

#### Registro de Visitas
- **URL:** `/visitas/nova`
- Formulário intuitivo
- Seleção de escola
- Data da visita (padrão: hoje)
- Campo de observações
- Upload de múltiplos anexos (fotos, PDFs, documentos)
- Formatos permitidos: JPG, PNG, PDF, DOC, DOCX
- Tamanho máximo: 16MB por arquivo

#### Visualização de Visitas
- **URL:** `/visitas`
- Lista de todas as visitas
- Filtros por:
  - Escola
  - Período (data início/fim)
- Visualização de anexos
- Detalhes completos de cada visita
- Contadores em tempo real

#### Mapa Interativo
- **URL:** `/mapa`
- Visualização de todas as escolas no mapa
- Marcadores clicáveis com informações
- Popup com nome da escola
- Botão para registrar visita direto do mapa
- Zoom e navegação
- Centralização automática em escola específica

#### Cálculo de Distâncias
- **URL:** `/distancias`
- **Calcula distância real de carro** (não em linha reta)
- Duas funcionalidades:
  1. **Distância entre duas escolas:**
     - Selecione origem e destino
     - Veja distância em km e tempo em minutos
  2. **Escolas próximas:**
     - Selecione uma escola de referência
     - Veja as 3, 5 ou 10 escolas mais próximas
     - Ordenadas por distância
- Usa OSRM para rotas reais

#### Relatórios
- **URL:** `/relatorios`
- **Relatório Excel:**
  - Múltiplas abas
  - Todas as visitas
  - Resumo por escola
  - Resumo por data
  - Download direto
- **Relatório Texto:**
  - Formato TXT
  - Visitas agrupadas por escola
  - Detalhes completos
  - Lista de anexos
- **Filtros:**
  - Por período (data início/fim)
  - Deixe em branco para todas as visitas

### APIs REST Disponíveis

#### Escolas

```http
GET /api/escolas
GET /api/escolas/<id>
```

#### Visitas

```http
GET  /api/visitas?escola_id=1&data_inicio=2025-01-01&data_fim=2025-01-31
POST /api/visitas
GET  /api/visitas/<id>
```

Exemplo POST:
```javascript
fetch('/api/visitas', {
  method: 'POST',
  body: formData  // FormData com escola_id, data, observacoes, anexos
})
```

#### Distâncias

```http
POST /api/distancia
GET  /api/escolas/<id>/proximas?limite=5
```

Exemplo POST:
```javascript
fetch('/api/distancia', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    escola1_id: 1,
    escola2_id: 2
  })
})
```

#### Estatísticas

```http
GET /api/estatisticas
```

#### Relatórios

```http
POST /api/relatorios/excel
POST /api/relatorios/texto
```

### Estrutura do Projeto

```
gestor_visitas_escolas/
├── app.py                  # Aplicação Flask (servidor web)
├── iniciar_web.py          # Script de inicialização
├── escolas.py              # Lógica de gerenciamento de escolas
├── visitas.py              # Lógica de registro de visitas
├── distancias.py           # Cálculo de distâncias (OSRM)
├── relatorios.py           # Geração de relatórios
├── setup_auto.py           # Configuração inicial (geocoding)
│
├── templates/              # Templates HTML
│   ├── base.html          # Layout base (navbar, footer)
│   ├── index.html         # Dashboard
│   ├── escolas.html       # Lista de escolas
│   ├── nova_visita.html   # Formulário de visita
│   ├── visitas.html       # Lista de visitas
│   ├── detalhes_visita.html  # Detalhes da visita
│   ├── mapa.html          # Mapa interativo
│   ├── distancias.html    # Cálculo de distâncias
│   ├── relatorios.html    # Geração de relatórios
│   ├── 404.html           # Página não encontrada
│   └── 500.html           # Erro do servidor
│
├── static/                 # Arquivos estáticos
│   ├── css/               # CSS customizado (futuro)
│   ├── js/                # JavaScript customizado (futuro)
│   └── uploads/           # Uploads de anexos
│
├── data/                   # Dados JSON
│   ├── escolas.json       # Escolas com coordenadas
│   ├── visitas.json       # Visitas registradas
│   └── matriz_distancias.json  # Cache de distâncias
│
├── anexos/                 # Evidências das visitas (backup)
├── relatorios/             # Relatórios gerados
│
└── requirements.txt        # Dependências Python
```

### Dados Já Configurados

**20 Escolas do Bloco 1 Geocodificadas:**
1. Bela Vista
2. CECAP
3. Chácaras Reunidas
4. Continental
5. Coronel
6. Ezequiel
7. FONTE II
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

Todas com coordenadas GPS precisas!

### Fluxo de Uso Típico

1. **Acessar Dashboard** → Ver estatísticas gerais
2. **Planejar Visitas** → Ver escolas no mapa e calcular distâncias
3. **Durante a Visita** → Registrar observações e tirar fotos
4. **Após a Visita** → Fazer upload das evidências
5. **Gerar Relatórios** → Mensais, por escola ou período

### Configurações Avançadas

#### Alterar Porta do Servidor

Edite `app.py` na última linha:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Mude 5000 para 5001
```

#### Modo Produção

Para usar em produção com Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Acesso Remoto

O servidor está configurado para aceitar conexões de qualquer IP (`0.0.0.0`).

Para acessar de outro computador na mesma rede:
```
http://<IP_DO_COMPUTADOR>:5000
```

Exemplo: `http://192.168.1.100:5000`

### Solução de Problemas

#### Porta 5000 já em uso
- Altere a porta em `app.py`
- Ou finalize o processo que está usando a porta 5000

#### Erro ao fazer upload de arquivos
- Verifique se a pasta `static/uploads` existe
- Verifique permissões de escrita
- Tamanho máximo: 16MB

#### Mapas não aparecem
- Verifique conexão com internet
- OpenStreetMap requer conexão ativa

#### Distâncias não calculam
- Verifique se as escolas têm coordenadas
- Execute `python setup_auto.py` se necessário
- Verifique conexão com internet (OSRM online)

### Vantagens do Sistema Web

✅ **Acesso de qualquer lugar** - Não precisa instalar nada
✅ **Interface moderna** - Bootstrap 5 responsivo
✅ **Mapas interativos** - Visualização geográfica
✅ **Upload de arquivos** - Evidências organizadas
✅ **Relatórios automáticos** - Excel e TXT
✅ **APIs REST** - Fácil integração
✅ **Responsivo** - Funciona em celular e tablet

### Próximos Passos

1. Inicie o sistema: `python iniciar_web.py`
2. Acesse: http://localhost:5000
3. Explore o dashboard
4. Registre sua primeira visita
5. Gere relatórios

---

**Sistema pronto para uso!** 🚀

Para dúvidas, consulte:
- [INICIAR_WEB.md](INICIAR_WEB.md) - Guia de inicialização
- [README.md](README.md) - Documentação completa
