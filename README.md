# FluxoVia API 🛣️

> **Repositório principal (Core) do ecossistema FluxoVia — desenvolvido na Oficina de Backend 26/05.**

---

## 📌 Visão Geral do Projeto

O **FluxoVia** é um sistema de processamento de infrações de trânsito construído para simular um ambiente de produção real. Este repositório contém o **núcleo da arquitetura**: a API Python responsável por orquestrar todo o fluxo de dados.

O ciclo de vida de uma infração dentro do sistema funciona assim:

```
Radar na estrada
      │
      ▼
[FluxoVia API - FastAPI]  ◄─── você está aqui
      │  ├─ Valida os dados recebidos
      │  ├─ Aplica as regras de negócio (velocidade > limite?)
      │  ├─ Persiste o registro no PostgreSQL
      │  └─ Publica o evento na fila do RabbitMQ
      │
      ▼
[Worker RabbitMQ Consumer]
      │
      ▼
[FluxoVia SpeedingTicket API - NestJS/AWS]
      │
      └─ Gera o PDF da multa e realiza os disparos
```

**Stack principal:**

| Camada | Tecnologia |
|---|---|
| Framework Web | FastAPI 0.136+ |
| Servidor ASGI | Uvicorn |
| Banco de Dados | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Validação | Pydantic v2 |
| Mensageria | RabbitMQ + Pika |
| Infraestrutura | Docker & Docker Compose |

---

## 🏗️ Estrutura de Arquitetura

A arquitetura segue o padrão de camadas, onde cada diretório tem uma responsabilidade única e bem definida:

```
fluxovia-api/
├── config.py                  # Centralização de todas as variáveis de ambiente
├── compose.yml                # Orquestração dos containers (RabbitMQ, Worker, API)
├── requirements.txt           # Dependências do projeto
│
├── app/
│   ├── models/                # Entidades do banco de dados (SQLAlchemy 2.0)
│   │   └── radar_reading.py   # Mapeamento da tabela de leituras de radar
│   │
│   ├── schemas/               # 📋 DTOs e contratos de entrada/saída (Pydantic)
│   │   └── ...                # Validação automática dos dados recebidos pela API
│   │
│   ├── repositories/          # 🗄️ Padrão Repository — isolamento do acesso ao banco
│   │   └── radar_reading_repository.py
│   │
│   └── services/              # 🧠 Camada de regras de negócio (onde a mágica acontece)
│       └── rabbitmq_publisher.py  # Publicador de eventos na fila
│
├── database/
│   ├── database.py            # Engine, Session e gerenciamento do pool de conexões
│   └── migration.sql          # Script de criação do schema do banco
│
└── worker/
    ├── worker.py              # Consumer RabbitMQ rodando em background
    └── Dockerfile             # Container isolado para o worker
```

> Cada camada conversa **apenas com a camada imediatamente abaixo dela**. A rota não fala com o banco; o repositório não conhece o RabbitMQ. Esse isolamento é o que torna o código testável e manutenível.

---

## 🔗 Integração com o Microserviço de PDFs

O FluxoVia não trabalha sozinho. Após validar e persistir uma infração, o nosso Worker consome a mensagem da fila e a encaminha para uma **API parceira já deployada na AWS**:

**👉 [FluxoVia-SpeedingTicket-API (NestJS)](https://github.com/EderMiqueias/FluxoVia-SpeedingTicket-API)**

**Responsabilidades de cada lado:**

| FluxoVia API (este repo) | SpeedingTicket API (NestJS/AWS) |
|---|---|
| Recebe a leitura do radar | Recebe os dados já validados |
| Aplica as regras de negócio | Gera o PDF da multa |
| Salva no PostgreSQL | Realiza os disparos (e-mail, etc.) |
| Publica na fila RabbitMQ | — |

A comunicação entre o Worker e a API externa é autenticada via **token JWT**, garantindo que apenas o nosso sistema possa acionar a geração de multas.

---

## 🚨 AVISO IMPORTANTE PARA OS PARTICIPANTES DA OFICINA

> [!IMPORTANT]
> ### ⚠️ Leia antes de começar!
>
> Este repositório contém a **fundação arquitetural** do projeto — a estrutura de pastas, as configurações, os modelos de banco de dados, os repositórios e o serviço de mensageria já estão montados e prontos.
>
> **O que ainda NÃO existe (de propósito!):**
> - ❌ Os `schemas` Pydantic de entrada e saída
> - ❌ Os `routers` com os endpoints da API
> - ❌ As regras de negócio na camada de `services`
> - ❌ O `main.py` que inicializa o servidor FastAPI
>
> ### 🎯 Tudo isso será construído **AO VIVO** na nossa aula do dia **26/05**!
>
> Venha com o ambiente configurado e pronto para codar. Vamos sair do zero e chegar em uma API funcional, integrada com banco de dados e mensageria, em uma única sessão. 🚀

---

## ⚙️ Configurando o Ambiente

### Pré-requisitos

- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-started/get-docker/)

### 1️⃣ Clone o repositório e crie o ambiente virtual

```shell
git clone https://github.com/seu-usuario/FluxoVia-API.git
cd FluxoVia-API

# Linux/macOS
python3 -m venv venv && source venv/bin/activate

# Windows
python3 -m venv venv && venv\Scripts\activate
```

### 2️⃣ Instale as dependências Python

```shell
pip install -r requirements.txt
```

### 3️⃣ Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no exemplo abaixo:

```env
# Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fluxovia
DB_USER=postgres
DB_PASSWORD=postgres

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
RABBITMQ_QUEUE=traffic_fines

# API Parceira (SpeedingTicket)
TICKETS_API_BASE_URL=https://...
AUTH_EMAIL=seu@email.com
AUTH_PASSWORD=suasenha
```

### 4️⃣ Suba a infraestrutura com Docker

```shell
docker compose up -d
```

Isso irá inicializar:
- **RabbitMQ** → `localhost:5672` (broker) / `localhost:15672` (painel de gerenciamento)
- **Worker** → consumer rodando em background, aguardando mensagens na fila

> Acesse o painel do RabbitMQ em `http://localhost:15672` com usuário `guest` e senha `guest`.

---

## 🐍 Tecnologias e Versões

```
fastapi==0.136.0
uvicorn==0.45.0
sqlalchemy==2.0.20
pydantic==2.13.3
psycopg2-binary==2.9.12
pika==1.4.1
python-dotenv==1.0.1
```
