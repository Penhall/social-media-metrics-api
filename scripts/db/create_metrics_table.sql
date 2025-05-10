-- Criação da tabela de métricas
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value NUMERIC(15,2) NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_platform
        FOREIGN KEY(platform_id)
        REFERENCES platforms(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_metric_entry UNIQUE (platform_id, metric_name, collected_at)
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_metrics_platform_id ON metrics(platform_id);
CREATE INDEX IF NOT EXISTS idx_metrics_collected_at ON metrics(collected_at);
CREATE INDEX IF NOT EXISTS idx_metrics_user_id ON metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_metrics_user_collected ON metrics(user_id, collected_at);

-- Comentários sobre a tabela e colunas
COMMENT ON TABLE metrics IS 'Armazena as métricas coletadas das plataformas';
COMMENT ON COLUMN metrics.id IS 'Identificador único da métrica';
COMMENT ON COLUMN metrics.user_id IS 'ID do usuário relacionado';
COMMENT ON COLUMN metrics.platform_id IS 'ID da plataforma relacionada';
COMMENT ON COLUMN metrics.metric_name IS 'Nome da métrica (ex: seguidores, curtidas)';
COMMENT ON COLUMN metrics.value IS 'Valor numérico da métrica';
COMMENT ON COLUMN metrics.collected_at IS 'Data e hora da coleta da métrica';
COMMENT ON COLUMN metrics.created_at IS 'Data de criação do registro';