CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    monitoring_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('solicitado', 'confirmado', 'concluido', 'cancelado')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (monitoring_id) REFERENCES monitorings(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);