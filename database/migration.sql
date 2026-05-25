CREATE TABLE IF NOT EXISTS fluxovia.radar_readings (
    id SERIAL PRIMARY KEY,
    id_aparelho_medidor VARCHAR(100) NOT NULL,
    placa VARCHAR(10) NOT NULL,
    velocidade_registrada DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
