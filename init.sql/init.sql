-- Criar tabela de features
CREATE TABLE IF NOT EXISTS features (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de valores de features
CREATE TABLE IF NOT EXISTS feature_values (
    id SERIAL PRIMARY KEY,
    feature_id VARCHAR(255) REFERENCES features(id),
    entity_id VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(feature_id, entity_id)
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_feature_values_feature_id ON feature_values(feature_id);
CREATE INDEX IF NOT EXISTS idx_feature_values_entity_id ON feature_values(entity_id);
CREATE INDEX IF NOT EXISTS idx_feature_values_timestamp ON feature_values(timestamp);

-- Criar view para últimos valores de features
CREATE OR REPLACE VIEW latest_feature_values AS
SELECT DISTINCT ON (feature_id, entity_id)
    id,
    feature_id,
    entity_id,
    value,
    timestamp
FROM feature_values
ORDER BY feature_id, entity_id, timestamp DESC;
