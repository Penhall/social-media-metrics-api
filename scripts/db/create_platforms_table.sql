-- Criação da tabela de plataformas de redes sociais
CREATE TABLE IF NOT EXISTS platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_platform_name UNIQUE (name)
);

-- Comentários sobre a tabela e colunas
COMMENT ON TABLE platforms IS 'Armazena as plataformas de redes sociais monitoradas';
COMMENT ON COLUMN platforms.id IS 'Identificador único da plataforma';
COMMENT ON COLUMN platforms.name IS 'Nome da plataforma (ex: Twitter, Instagram)';
COMMENT ON COLUMN platforms.url IS 'URL base da plataforma';
COMMENT ON COLUMN platforms.created_at IS 'Data de criação do registro';