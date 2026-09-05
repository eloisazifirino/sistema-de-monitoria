# Atividade 1 

## 1. Quais tabelas você definiu inicialmente?

Inicialmente foram definidas quatro tabelas principais:

- `users`: armazena os usuários do sistema, como alunos, monitores e professores.
- `subjects`: armazena as disciplinas que possuem monitoria.
- `monitorings`: armazena as monitorias, incluindo informações como disciplina, monitor responsável, horário, local e modalidade.
- `appointments`: armazena os agendamentos feitos pelos alunos para uma monitoria.

Essas tabelas representam as entidades principais necessárias para iniciar o funcionamento do sistema.

## 2. Você utilizou migrations? Se sim, quantas migrations? Descreva em uma frase o que cada uma faz.

Sim, inicialmente serão utilizadas quatro migrations:

1. `001_create_users.sql` — cria a tabela de usuários.
2. `002_create_subjects.sql` — cria a tabela de disciplinas.
3. `003_create_monitorings.sql` — cria a tabela de monitorias e seus relacionamentos com usuários e disciplinas.
4. `004_create_appointments.sql` — cria a tabela de agendamentos e seus relacionamentos com usuários e monitorias.

As migrations serão armazenadas no diretório `backend/migrations/`.

## 3. Qual o caminho do arquivo que gera a seed do seu banco?

O arquivo utilizado para popular o banco com dados iniciais será:

`backend/seed.sql`

Esse arquivo terá dados de teste como usuários, disciplinas e monitorias pq facilita o desenvolvimento e os testes da aplicação.

## 4. Quais os endpoints que você irá implementar inicialmente?

Inicialmente pretendo implementar os seguintes endpoints:

- `GET /api/monitorings` — listar as monitorias disponíveis.
- `GET /api/monitorings/:id` — buscar os detalhes de uma monitoria específica.
- `POST /api/monitorings` — cadastrar uma nova monitoria.
- `PUT /api/monitorings/:id` — atualizar os dados de uma monitoria.
- `DELETE /api/monitorings/:id` — excluir uma monitoria.

- `POST /api/appointments` — realizar um agendamento.
- `GET /api/appointments` — listar os agendamentos.
- `DELETE /api/appointments/:id` — cancelar um agendamento.

Pretendo começar pelos endpoints de consulta de monitorias, porque eles permitem validar primeiro a integração entre o banco de dados e a API. Depois disso serão implementadas as operações de criação, alteração e exclusão das monitorias e em seguida os agendamentos que vão depender da existência das monitorias e dos usuários.

## 5. Você está usando algum framework para escrever os endpoints da sua API? Se sim, qual?

Sim, vou utilizar o Express com Node.js e TypeScript para implementar os endpoints da API.