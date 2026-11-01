# Sistema de Monitoria

Sistema web e mobile desenvolvido para auxiliar no gerenciamento de monitorias acadêmicas, permitindo o cadastro de monitorias, agendamento de atendimentos e acompanhamento das atividades realizadas.

O sistema possui três tipos de usuários: aluno, monitor e professor, cada um com diferentes permissões e funcionalidades.

## Funcionalidades

### Usuários

- Cadastro e autenticação de usuários;
- Gerenciamento de perfil;
- Controle de acesso de acordo com o tipo de usuário (aluno, monitor ou professor).

### Monitorias

- Cadastro, edição e exclusão de monitorias pelo professor;
- Associação da monitoria a uma disciplina e a um monitor responsável;
- Definição de dia, horário, local e modalidade (presencial ou online);
- Listagem das monitorias disponíveis;
- Pesquisa e filtragem por disciplina, monitor e dia;
- Visualização dos detalhes da monitoria.

### Agendamentos

- Agendamento de atendimentos pelos alunos;
- Seleção de horários disponíveis;
- Cancelamento de agendamentos;
- Visualização dos agendamentos pelo monitor;
- Histórico de atendimentos;
- Controle do status do agendamento (solicitado, confirmado, concluído ou cancelado).

### Avisos e notificações

- Publicação de avisos relacionados às monitorias;
- Notificações em caso de alteração ou cancelamento de uma monitoria.

### Monitor

- Acesso aos alunos inscritos em suas monitorias;
- Registro das monitorias realizadas;
- Registro das horas de monitoria;
- Visualização de relatórios das atividades realizadas.

### Professor

- Cadastro e gerenciamento das monitorias;
- Atribuição de monitores;
- Visualização das monitorias de suas disciplinas;
- Acompanhamento das atividades dos monitores;
- Visualização de relatórios;
- Gerenciamento dos monitores vinculados às disciplinas.

### Calendário

- Visualização das monitorias programadas em calendário.

## Plataformas

O projeto contará com uma aplicação web e uma aplicação mobile.

## Tecnologias

- **Backend:** Python, FastAPI, psycopg2
- **Banco de dados:** PostgreSQL
- **Documentação da API:** Swagger (gerado automaticamente pelo FastAPI)

## Estrutura do projeto

```
sistema-de-monitoria/
├── backend/
│   ├── migrations/          # scripts SQL (001 a 005) e seed (006)
│   ├── database.py          # conexão com o PostgreSQL
│   ├── main.py              # API
│   ├── requirements.txt
│   └── .env.example         # modelo das variáveis de ambiente
├── UML_Sistema_de_Monitoria.drawio.png
└── README.md
```

## Modelagem

O diagrama UML do sistema está em `UML_Sistema_de_Monitoria.drawio.png`.
O banco possui 5 entidades: `users`, `subjects`, `monitorings`, `appointments` e `study_materials`.

## Como rodar o backend

### Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL instalado e em execução

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd sistema-de-monitoria
git checkout entrega1
```

### 2. Criar o ambiente virtual e instalar as dependências

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Criar o banco de dados e as tabelas

Crie um banco vazio (o nome fica a seu critério):

```bash
createdb -U postgres monitoria
```

Execute os scripts da pasta `backend/migrations/` **em ordem**:

```bash
psql -U postgres -d monitoria -f backend/migrations/001_create_users.sql
psql -U postgres -d monitoria -f backend/migrations/002_create_subjects.sql
psql -U postgres -d monitoria -f backend/migrations/003_create_monitorings.sql
psql -U postgres -d monitoria -f backend/migrations/004_create_appointments.sql
psql -U postgres -d monitoria -f backend/migrations/005_create_study_materials.sql
```

Opcionalmente, carregue os dados de teste:

```bash
psql -U postgres -d monitoria -f backend/migrations/006_seed.sql
```

### 4. Configurar as variáveis de ambiente

```bash
cp backend/.env.example backend/.env
```

Edite o `backend/.env` com os dados do seu banco. Se a senha tiver caracteres especiais (como `#` ou `$`), coloque-a entre aspas simples:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=monitoria
DB_USER=postgres
DB_PASSWORD='sua_senha'
```

O arquivo `.env` não é versionado.

### 5. Iniciar a API

```bash
cd backend
uvicorn main:app --reload
```

A API ficará disponível em `http://localhost:8000`.

### 6. Documentação (Swagger)

Com a API rodando, acesse:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints implementados

| Método | Rota | Descrição |
|---|---|---|
| POST | `/login` | Autenticação de usuário |
| POST | `/users` | Cadastro de usuário |
| GET | `/subjects` | Listagem de disciplinas |
| POST | `/monitorings` | Criar monitoria (apenas professor) |
| GET | `/monitorings` | Listar monitorias (filtros: `subject_id`, `monitor_id`, `day`) |
| GET | `/monitorings/{id}` | Detalhes de uma monitoria |
| PUT | `/monitorings/{id}` | Atualizar monitoria (apenas professor) |
| DELETE | `/monitorings/{id}` | Excluir monitoria (apenas professor) |
| POST | `/appointments` | Agendar atendimento (apenas aluno) |
| GET | `/appointments` | Listar agendamentos (filtros: `student_id`, `monitoring_id`) |
| PUT | `/appointments/{id}/status` | Atualizar status do agendamento |
| POST | `/materials` | Enviar material de estudo (upload de arquivo) |

## Usuários de teste (seed)

| Perfil | Email | Senha |
|---|---|---|
| Aluno | aluno@teste.com | senha_teste |
| Monitor | monitor@teste.com | senha_teste |
| Professor | professor@teste.com | senha_teste |

## Status

Em desenvolvimento.

- **Entrega 1:** modelagem UML, script do banco, login e CRUD de monitorias com documentação.