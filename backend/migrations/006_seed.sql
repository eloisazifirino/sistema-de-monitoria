-- usuarios
INSERT INTO users (name, email, password, role)
VALUES
    ('Aluno Teste', 'aluno@teste.com', 'senha_teste', 'aluno'),
    ('Monitor Teste', 'monitor@teste.com', 'senha_teste', 'monitor'),
    ('Professor Teste', 'professor@teste.com', 'senha_teste', 'professor');

-- disciplinas
INSERT INTO subjects (name, code)
VALUES
    ('Programação B', 'PROGB'),
    ('Cálculo II', 'CALC2');

-- monitorias
INSERT INTO monitorings (
    subject_id,
    monitor_id,
    day,
    start_time,
    location,
    modality
)
VALUES (
    1,
    2,
    'segunda-feira',
    '14:00',
    'Sala 01',
    'presencial'
);

-- agendamentos
INSERT INTO appointments (
    monitoring_id,
    student_id,
    status
)
VALUES (
    1,
    1,
    'solicitado'
);

-- materiais de estudo
INSERT INTO study_materials (
    monitoring_id,
    title,
    description,
    file_type,
    file_attachment
)
VALUES (
    1,
    'Resumo de Laços de Repetição',
    'Arquivo em PDF com exemplos práticos de for e while.',
    'application/pdf',
    'arquivo_mock_dados'::bytea
);