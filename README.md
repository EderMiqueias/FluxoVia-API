# FluxoVia API 🛣️

Bem-vindo ao repositório do **ViaFlow API**, o projeto prático da nossa oficina de desenvolvimento de software sustentável. 

Esta API simula um sistema de monitoramento de uma rodovia, construída utilizando **Python**, **FastAPI** e **PostgreSQL**. O objetivo é demonstrar como estruturar código pronto para produção, garantindo manutenibilidade e escalabilidade.
teste
## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.8+
* **Framework Web:** [FastAPI](https://pypi.org/project/fastapi/)
* **Servidor ASGI:** [Uvicorn](https://pypi.org/project/uvicorn/)
* **Banco de Dados:** PostgreSQL
* **Driver do Banco:** [Psycopg2](https://pypi.org/project/psycopg2/)
* **Infraestrutura:** Docker & Docker Compose


## ⚙️ Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
* [Python 3.8+](https://www.python.org/downloads/)
* [Docker](https://docs.docker.com/get-started/get-docker/)

---

## 🚀 Passo a Passo: Configuração do Ambiente Local

### 1️⃣ Criar um ambiente Python virtual

🪟 No Windows:
```shell
python3 -m venv venv
```

🐧 No Linux/macOS:
```shell
python3 -m venv venv
```

### 2️⃣ Ativar o Ambiente Virtual

🪟 No Windows (Prompt de Comando):
```
venv\Scripts\activate.bat
```
Ou
```
venv\Scripts\Activate.ps1
```

🐧 No Linux/macOS:
```shell
source venv/bin/activate
```

### 3️⃣ Instalar as Dependências

🐧🪟 No Linux/macOS/Windows:
```shell
pip install fastapi uvicorn psycopg2-binary
```


### 🏃‍♂️ Rodando a Aplicação

```shell
uvicorn main:app --reload
```