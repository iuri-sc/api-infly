📊 API Infly – Sistema de Gestão Escolar

API desenvolvida para gerenciar negociações, contas, calendários, leads e matrículas, permitindo análises como taxa de conversão, inadimplência e origem de leads.  
O módulo fornece endpoints de consulta e análise, sendo ideal para integração com dashboards (Power BI) ou frontend web.

---

🚀 Tecnologias Utilizadas

- **Python 3.10+**
- **FastAPI** – Framework backend rápido e moderno
- **Uvicorn** – ASGI server
- **SQLAlchemy** – ORM para acesso ao banco de dados
- **PostgreSQL** – Banco de dados relacional utilizado
- **Pydantic** – Modelos de validação e serialização
- **Argon2** – Hash seguro para senhas
- **PyJWT (jose)** – Autenticação por tokens JWT
- **CORS Middleware** – Acesso seguro a partir de frontends externos

---

📦 Instalação
1️⃣ Clone o repositório

git clone https://github.com/seu-user/api-infly.git
cd api-infly

📜 Instalação das Dependências

2️⃣ Crie e ative um ambiente virtual

🔹 Windows
python -m venv venv
venv\Scripts\activate

🔹 Linux / macOS
python3 -m venv venv
source venv/bin/activate

3️⃣ Instale os pacotes
pip install -r requirements.txt

Como executar o servidor

Depois de estar dentro da pasta api-infly e com o ambiente virtual ativado:

🔹 Windows
cd ..
uvicorn api-infly.main:app --reload

🔹 Linux / macOS
cd ..
uvicorn api-infly.main:app --reload