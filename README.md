# Tutor Platform

Plataforma backend para tutores inteligentes com FastAPI, SQLAlchemy, PostgreSQL, LangChain, LangSmith e integração com Tavily para extração de conteúdo web.

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1E6E8C?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge)](https://python.langchain.com/)
[![LangSmith](https://img.shields.io/badge/LangSmith-0B0F19?style=for-the-badge)](https://docs.smith.langchain.com/)
[![Alembic](https://img.shields.io/badge/Alembic-1F2937?style=for-the-badge)](https://alembic.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![Ruff](https://img.shields.io/badge/Ruff-2C2F33?style=for-the-badge)](https://docs.astral.sh/ruff/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-2C2F33?style=for-the-badge)](https://www.uvicorn.org/)

## Sumário
- [1. Título do projeto](#1-título-do-projeto)
- [2. Demonstração](#2-demonstração)
- [3. Objetivo do projeto](#3-objetivo-do-projeto)
- [4. Arquitetura](#4-arquitetura)
- [5. Tecnologias utilizadas](#5-tecnologias-utilizadas)
- [6. Estrutura do projeto](#6-estrutura-do-projeto)
- [7. Fluxo de funcionamento](#7-fluxo-de-funcionamento)
- [8. Knowledge Providers](#8-knowledge-providers)
- [9. Persistência](#9-persistência)
- [10. Observabilidade](#10-observabilidade)
- [11. Segurança](#11-segurança)
- [12. Instalação](#12-instalação)
- [13. Variáveis de ambiente](#13-variáveis-de-ambiente)
- [14. Executando os testes](#14-executando-os-testes)
- [15. Ruff e qualidade de código](#15-ruff-e-qualidade-de-código)
- [16. Endpoints](#16-endpoints)
- [17. Integração com o Frontend](#17-integração-com-o-frontend)
- [18. Decisões arquiteturais](#18-decisões-arquiteturais)
- [19. Melhorias futuras](#19-melhorias-futuras)
- [20. Autor e créditos](#20-autor-e-créditos)

---

## 1. Título do projeto

**Tutor Platform** é o backend de uma plataforma de tutores inteligentes. O projeto expõe uma API para cadastro e gestão de tutores, registro de fontes de conhecimento, atendimento via chat e configuração para embed.

---

## 2. Demonstração

- URL da API em produção: https://tutor-plataform.onrender.com
- URL da documentação Swagger: `http://127.0.0.1:8000/docs` em ambiente local; em produção, a rota padrão permanece a mesma
- URL do OpenAPI: `http://127.0.0.1:8000/openapi.json` em ambiente local; em produção, a rota padrão permanece a mesma
- Frontend publicado: não há frontend publicado referenciado neste repositório

> Observação: o repositório atual não contém Dockerfile nem docker-compose. A execução local é feita diretamente com UV.

---

## 3. Objetivo do projeto

O desafio proposto é construir a base backend de uma plataforma de tutores inteligentes, com separação clara entre domínio, persistência, orquestração de conhecimento, geração de respostas e camada HTTP.

Na prática, a plataforma resolve o problema de criar tutores que respondem com base em conteúdo cadastrado e em fontes externas validadas, mantendo o histórico de conversas e uma arquitetura preparada para evoluções futuras.

A plataforma de Tutores Inteligentes representa um backend capaz de:

- cadastrar tutores com prompt sistêmico próprio;
- associar múltiplas fontes de conhecimento a cada tutor;
- validar essas fontes antes da persistência;
- responder perguntas via LLM com contexto recuperado;
- persistir conversas e mensagens;
- expor endpoints para administração, chat e embed.

---

## 4. Arquitetura

A aplicação foi organizada em camadas, com responsabilidade bem delimitada entre HTTP, serviços, persistência, providers e geração de respostas.

```mermaid
flowchart TD
    U[Usuário] --> API[FastAPI]
    API --> CS[ChatService]
    CS --> TA[TutorAgent]
    TA --> KT[KnowledgeTool]
    KT --> KF[KnowledgeProviderFactory]
    KF --> P[Providers]
    TA --> PB[Prompt Builder]
    PB --> LLM[LLMClient / ChatOpenAI]
    P --> KR[KnowledgeResult]
    LLM --> R[Resposta]
    CS --> DB[(PostgreSQL)]
    KT --> DB
```

### Papel de cada camada

- **Services**: coordenam casos de uso e transações. `TutorService`, `KnowledgeService` e `ChatService` centralizam as regras de negócio e o uso do Unit of Work.
- **Repositories**: encapsulam as consultas e mutações SQLAlchemy para `Tutor`, `KnowledgeSource`, `Conversation` e `Message`.
- **Providers**: executam a recuperação/validação do conteúdo de cada fonte. Cada provider conhece a própria forma de validar e extrair dados.
- **Agent**: o `TutorAgent` orquestra recuperação de contexto, construção de prompt e chamada do LLM.
- **Prompt Builder**: monta o prompt final com SYSTEM, HISTORY, CONTEXT e USER.
- **Banco de dados**: persiste tutores, fontes de conhecimento, conversas e mensagens usando PostgreSQL e SQLAlchemy Async.

---

## 5. Tecnologias utilizadas

| Tecnologia | Uso no projeto | Estado atual |
|---|---|---|
| Python 3.12 | Linguagem principal | Utilizada |
| FastAPI | API HTTP | Utilizada |
| SQLAlchemy 2.0 | ORM assíncrono e consultas | Utilizada |
| PostgreSQL | Banco relacional | Utilizada |
| Alembic | Migrations e evolução de schema | Utilizada |
| LangChain | Cliente do LLM e integração do Tavily | Utilizada |
| LangSmith | Tracing da execução do chat flow | Utilizada |
| Tavily | Extração de conteúdo web | Utilizada via langchain-tavily |
| Pydantic | Schemas e Settings | Utilizada |
| UV | Gestão de ambiente e execução | Utilizada |
| Pytest | Testes automatizados | Utilizada |
| Docker | Containerização | Não presente no repositório atual |

---

## 6. Estrutura do projeto

A estrutura real do repositório é a seguinte:

```text
app/
  api/
    dependencies.py
    errors.py
    schemas.py
    v1/
  agents/
  core/
  db/
  knowledge/
  llm/
  models/
  prompts/
  repositories/
  services/
  tools/
alembic/
docs/
tests/
```

### Diretórios principais

- **app/api**: camada HTTP. Contém dependências, handlers globais de erro, schemas Pydantic e os routers versionados em `v1`.
- **app/agents**: orquestração do tutor inteligente. Hoje contém o `TutorAgent`.
- **app/core**: configurações e exceções de aplicação.
- **app/db**: base declarativa, sessão assíncrona e Unit of Work.
- **app/knowledge**: abstração de providers, modelos de resultado, factory e exceptions da camada de conhecimento.
- **app/llm**: cliente fino em cima de `ChatOpenAI`.
- **app/models**: modelos ORM e enums do domínio.
- **app/prompts**: construção do prompt final enviado ao LLM.
- **app/repositories**: acesso ao banco com SQLAlchemy.
- **app/services**: camada de casos de uso e coordenação.
- **app/tools**: ferramentas de orquestração, como o `KnowledgeTool`.
- **alembic**: env, script template e revisões de migration.
- **docs**: documentação técnica complementar e decisões arquiteturais.
- **tests**: testes automatizados da API e da camada de knowledge.

> Observação: não existe uma pasta separada `schemas/` no estado atual. Os schemas HTTP ficam em `app/api/schemas.py`.

---

## 7. Fluxo de funcionamento

Quando um usuário envia uma pergunta para o chat, o fluxo acontece assim:

```mermaid
flowchart TD
  SP[SYSTEM PROMPT do tutor] --> PB[Prompt Builder]
  H[HISTORY da conversa] --> PB
  C[CONTEXT recuperado pelo KnowledgeTool] --> PB
  U[USER QUESTION] --> PB
  PB --> L[LLMClient / ChatOpenAI]
  L --> A[ANSWER]
```

O `SYSTEM PROMPT` vem de `tutor.system_prompt` por meio de `tutor.instructions`. O `HISTORY` é composto pelas mensagens já persistidas na conversa. O `CONTEXT` reúne os resultados retornados pelos providers de conhecimento. A `USER QUESTION` é a pergunta atual enviada pelo cliente. O `LLMClient` recebe o prompt final e retorna a `ANSWER`, que depois é persistida como mensagem do assistente.

1. O cliente chama `POST /api/v1/chat` ou `POST /api/v1/embed/chat`.
2. A rota injeta `ChatService` e `TutorAgent` via dependências FastAPI.
3. `ChatService` carrega o tutor e cria ou reutiliza a `Conversation` com base em `conversation_id`.
4. O histórico da conversa é carregado antes de persistir a nova pergunta.
5. A mensagem do usuário é salva como `Message` com role `USER`.
6. O `TutorAgent` recebe o tutor, a pergunta e o histórico.
7. O `KnowledgeTool` percorre as `knowledge_sources` do tutor.
8. A `KnowledgeProviderFactory` seleciona o provider correto para cada fonte.
9. O provider valida e extrai o conteúdo da fonte.
10. O `Prompt Builder` monta o prompt final com SYSTEM, HISTORY, CONTEXT e USER.
11. O `LLMClient` envia o prompt ao `ChatOpenAI`.
12. A resposta do assistente é persistida como `Message` com role `ASSISTANT`.
13. A API retorna `conversation_id`, `answer` e `sources`.

---

## 8. Knowledge Providers

A camada de conhecimento é resolvida por factory e providers especializados.

```mermaid
flowchart TD
  KS[Knowledge Source] --> KF[KnowledgeProviderFactory]
  KF --> P[Provider concreto]
  P --> KR[KnowledgeResult]
  KR --> PB[Prompt Builder]
  PB --> LLM[LLM]
```

Essa arquitetura isola a lógica de validação e extração em implementações específicas. Para adicionar um novo provider, basta implementar o contrato da camada de conhecimento e registrá-lo na factory, sem alterar o restante do fluxo de chat.

### HttpProvider

Usado para fontes públicas em HTML/texto. Ele faz uma requisição HTTP com `httpx`, respeita timeout configurável e normaliza a resposta como texto.

### JsonProvider

Usado para URLs que retornam JSON. Ele baixa o conteúdo, valida se a resposta é JSON válido e serializa o payload para texto normalizado.

### TavilyProvider

Usado para extração de conteúdo de páginas web via Tavily. Esta implementação usa a integração oficial do ecossistema LangChain com `langchain-tavily` e `TavilyExtract`.

O provider:

- valida a URL antes da persistência;
- usa `TAVILY_API_KEY`;
- aceita `TAVILY_API_BASE_URL` como override opcional;
- respeita timeout em nível de aplicação;
- converte o retorno em `KnowledgeResult`;
- registra erros via logging.

### Factory

A `KnowledgeProviderFactory` seleciona automaticamente o provider correto com base no enum `ProviderType`:

- `HTTP_TEXT` -> `HttpProvider`
- `JSON` -> `JsonProvider`
- `TAVILY_EXTRACT` -> `TavilyProvider`

---

## 9. Persistência

### Tutor

Entidade principal do domínio. Contém:

- `id`
- `name`
- `description`
- `system_prompt`
- `status`
- `created_at`
- `updated_at`

### KnowledgeSource

Representa cada fonte conectada a um tutor. Contém:

- `tutor_id`
- `provider_type`
- `source_name`
- `source_url`
- `configuration` em JSONB
- `enabled`
- timestamps

### Conversation

Guarda a sessão de chat associada ao tutor. O par `tutor_id + session_id` é único, permitindo reutilização da conversa correta.

### Message

Armazena as mensagens da conversa com `role`, `content` e timestamp. As mensagens são recuperadas em ordem cronológica para construção do histórico.

### Histórico

O histórico é armazenado no banco e carregado pelo `ChatService` antes da geração da resposta. Isso permite que o prompt tenha contexto da conversa anterior sem depender de memória externa.

---

## 10. Observabilidade

A observabilidade existente hoje é composta por tracing do LangSmith e logs da própria aplicação.

- O fluxo de chat está instrumentado com `@traceable(name="chat_flow")` em `app/api/v1/chat.py`, o que permite acompanhar a execução do caso de uso no LangSmith quando `LANGSMITH_TRACING` está habilitado.
- O tracing cobre o fluxo de chat; a instrumentação não está espalhada para todos os providers ou services de forma separada.
- A aplicação registra erros com `logging.exception` em pontos críticos como `TutorAgent`, `KnowledgeTool` e `TavilyProvider`.
- `DB_ECHO` permite expor SQL emitido pelo SQLAlchemy quando a investigação local exigir esse nível de detalhe.
- Não há configuração de logs estruturados, métricas ou dashboards no repositório atual.

---

## 11. Segurança

As proteções implementadas hoje são simples, explícitas e concentradas na camada HTTP e na validação de fontes.

- `ADMIN_API_KEY` é a chave configurada no ambiente para autorizar operações administrativas de escrita.
- O header esperado é `X-ADMIN-KEY`, validado por `app.core.security.require_admin_api_key`.
- Os endpoints administrativos de criação, atualização e exclusão usam um router protegido por dependência FastAPI, então qualquer requisição sem chave válida recebe `401 Unauthorized`.
- Os endpoints públicos de listagem, chat e embed não exigem `X-ADMIN-KEY`.
- O campo `embed_token` é gerado automaticamente na criação do tutor como um UUID hexadecimal de 32 caracteres, possui índice e unicidade, e não é aceito em requests de escrita.
- O `embed_token` serve como identificador público para o fluxo embarcado em `/api/v1/embed/chat`, evitando expor `tutor_id` no frontend.
- As `Knowledge Sources` são validadas antes da persistência: na criação e na atualização, o provider correspondente tenta processar a URL e rejeita entradas inválidas antes do commit.

---

## 12. Instalação

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd tutor-platform
```

### 2. Criar o ambiente e instalar dependências

O projeto usa UV.

```bash
uv sync
```

### 3. Configurar o ambiente

Copie o arquivo `.env.example` para `.env` e ajuste os valores conforme sua máquina.

```bash
cp .env.example .env
```

### 4. Executar migrations

```bash
uv run alembic upgrade head
```

### 5. Subir a aplicação

```bash
uv run uvicorn app.main:app --reload
```

A aplicação fica disponível em `http://127.0.0.1:8000`.

A documentação Swagger fica em `http://127.0.0.1:8000/docs`.

O OpenAPI fica em `http://127.0.0.1:8000/openapi.json`.

---

## 13. Variáveis de ambiente

| Variável | Finalidade | Exemplo |
|---|---|---|
| `DATABASE_URL` | String de conexão PostgreSQL assíncrona usada pelo SQLAlchemy e Alembic | `postgresql+asyncpg://user:password@host:5432/dbname` |
| `DB_ECHO` | Habilita logs SQL do SQLAlchemy | `false` |
| `DB_POOL_SIZE` | Tamanho base do pool de conexões | `5` |
| `DB_MAX_OVERFLOW` | Número máximo de conexões extras no pool | `10` |
| `ADMIN_API_KEY` | Chave usada para autenticar os endpoints administrativos de escrita | `admin-...` |
| `OPENAI_API_KEY` | Chave da OpenAI usada pelo `ChatOpenAI` | `sk-...` |
| `LLM_MODEL` | Nome do modelo padrão | `gpt-5.4-mini` |
| `LLM_TEMPERATURE` | Temperatura padrão do LLM | `0` |
| `TAVILY_API_KEY` | Chave obrigatória para o `TavilyProvider` | `tvly-...` |
| `TAVILY_API_BASE_URL` | Override opcional do endpoint Tavily | `https://api.tavily.com` |
| `TAVILY_TIMEOUT_SECONDS` | Timeout aplicado às operações Tavily | `30` |
| `LANGSMITH_TRACING` | Ativa tracing do fluxo de chat no LangSmith | `true` |
| `LANGSMITH_ENDPOINT` | Endpoint do LangSmith | `https://api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | Chave do LangSmith | `lsv2_...` |
| `LANGSMITH_PROJECT` | Nome do projeto no LangSmith | `Project` |

### Observações

- O arquivo `.env` é carregado na inicialização.
- `ADMIN_API_KEY` é obrigatória para os endpoints administrativos de escrita e deve ser enviada no header `X-ADMIN-KEY`.
- `TAVILY_API_KEY` é necessário para criação/uso de fontes do tipo `TAVILY_EXTRACT`.
- `OPENAI_API_KEY` é necessário para geração real de respostas pelo LLM.

---

## 14. Executando os testes

### Suíte completa

```bash
uv run pytest
```

### Testes de API e integração

```bash
uv run pytest tests/test_admin_api.py tests/test_chat_api.py tests/test_knowledge_validation.py
```

### Cobertura

Não há configuração de cobertura dedicada no repositório atual.

---

## 15. Ruff e qualidade de código

O projeto usa Ruff para lint e formatação. A configuração fica em [pyproject.toml](pyproject.toml) e já cobre os diretórios `app`, `alembic` e `tests`.

### Como usar

Após rodar `uv sync`, o Ruff já fica disponível no ambiente do projeto. Os comandos principais são:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ruff format .
uv run ruff check . --fix
```

### Onde ele se encaixa no fluxo

- `uv run ruff check .` valida imports, regras de estilo e problemas estáticos antes do envio de mudanças.
- `uv run ruff format --check .` confirma que a base está formatada de forma consistente.
- `uv run ruff format .` aplica a formatação automaticamente quando necessário.
- `uv run ruff check . --fix` corrige automaticamente parte dos problemas simples de lint.

Na prática, o Ruff deve ser executado antes dos testes e antes de abrir PRs, para manter o backend consistente e pronto para revisão.

---

## 16. Endpoints

### Tutor

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v1/tutors` | Cria um tutor. Requer `X-ADMIN-KEY`. |
| `GET` | `/api/v1/tutors` | Lista tutores |
| `GET` | `/api/v1/tutors/{tutor_id}` | Busca um tutor por ID |
| `PATCH` | `/api/v1/tutors/{tutor_id}` | Atualiza um tutor. Requer `X-ADMIN-KEY`. |
| `DELETE` | `/api/v1/tutors/{tutor_id}` | Inativa um tutor. Requer `X-ADMIN-KEY`. |

### Knowledge Source

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v1/tutors/{tutor_id}/knowledge-sources` | Cria uma fonte de conhecimento para um tutor. Requer `X-ADMIN-KEY`. |
| `GET` | `/api/v1/tutors/{tutor_id}/knowledge-sources` | Lista as fontes de um tutor |
| `PATCH` | `/api/v1/knowledge-sources/{knowledge_source_id}` | Atualiza uma fonte de conhecimento. Requer `X-ADMIN-KEY`. |
| `DELETE` | `/api/v1/knowledge-sources/{knowledge_source_id}` | Remove uma fonte de conhecimento. Requer `X-ADMIN-KEY`. |

### Chat

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v1/chat` | Executa o fluxo de chat com persistência de conversa |

### Embed

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v1/embed/{tutor_id}/config` | Retorna a configuração pública do tutor para embed |
| `POST` | `/api/v1/embed/chat` | Executa o mesmo fluxo do chat para embed usando `embed_token` |

### Tutor público

O tutor expõe `embed_token` como identificador público da integração embarcada. Esse campo é gerado automaticamente na criação do tutor, não é aceito em requests de escrita e pode ser usado pelo frontend para chamar `/api/v1/embed/chat` sem expor `tutor_id`.

---

## 17. Integração com o Frontend

A integração com o frontend é feita via HTTP em uma arquitetura REST simples, sem acoplamento direto à implementação da interface.

- O frontend consome os endpoints da API através de requisições HTTP padrão.
- A documentação OpenAPI em `/openapi.json` funciona como contrato de referência para desenvolvimento e integração.
- A interface Swagger em `/docs` facilita a validação manual dos contratos e dos payloads.
- O fluxo embarcado usa `embed_token` para consumir a API sem expor `tutor_id` ao cliente.
- Não há frontend publicado documentado neste repositório; se existir uma implantação externa, ela deve apontar para esta API usando os mesmos contratos descritos pela OpenAPI.

---

## 18. Decisões arquiteturais

### Repository Pattern

O acesso ao banco foi isolado em repositórios específicos por agregado. Isso mantém as queries fora das services e facilita testes e manutenção.

### Service Layer

As regras de negócio e a coordenação transacional ficam nas services. Isso evita que a camada HTTP fale diretamente com o ORM.

### Provider Pattern

Cada tipo de fonte de conhecimento possui sua própria implementação de provider. Isso mantém validação e extração encapsuladas no lugar certo.

### Factory Pattern

A factory seleciona o provider com base no enum `ProviderType`, sem reflexão ou imports dinâmicos.

### Separation of Concerns

- HTTP só lida com request/response.
- Services orquestram casos de uso.
- Repositories acessam dados.
- Providers resolvem conteúdo externo.
- Agent monta prompt e gera resposta.

### Por que não foi utilizado banco vetorial

O estado atual do projeto está focado em fontes diretas e extração via providers. Ainda não há embeddings, chunking para busca semântica ou necessidade de indexação vetorial no escopo implementado.

### Como o Tavily foi utilizado

O Tavily foi integrado como provider de extração web via `langchain-tavily`, com validação de URL e timeout em nível de aplicação.

### Evolução para RAG mais avançado

A arquitetura atual já deixa o caminho aberto para introduzir:

- chunking;
- embeddings;
- vetor de busca;
- recuperação híbrida;
- roteamento de fontes por tipo.

Sem quebrar a abstração atual de providers.

---

## 19. Melhorias futuras

Algumas evoluções naturais para próximas sprints:

- Streaming de respostas
- Memória de longo prazo
- LangGraph para orquestração mais rica
- MCP para integração com ferramentas externas
- Dashboard administrativo
- Banco vetorial para RAG semântico
- Observabilidade avançada com métricas e tracing ampliado

Essas funcionalidades não estão implementadas no estado atual do projeto.

---

## 20. Autor e créditos

O projeto foi desenvolvido por Ronald Damasio como solução para um desafio técnico de Engenheiro de Soluções de IA.

Os créditos de implementação e manutenção pertencem ao autor do repositório.
