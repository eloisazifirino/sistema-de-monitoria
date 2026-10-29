CREATE TABLE study_materials (
    id SERIAL PRIMARY KEY,
    monitoring_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    file_type VARCHAR(50) NOT NULL,
    file_attachment BYTEA, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (monitoring_id) REFERENCES monitorings(id)
);