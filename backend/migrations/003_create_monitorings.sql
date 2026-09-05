CREATE TABLE monitorings (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    monitor_id INTEGER NOT NULL,
    day VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    location VARCHAR(150),
    modality VARCHAR(20) NOT NULL
        CHECK (modality IN ('presencial', 'online')),

    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (monitor_id) REFERENCES users(id)
);