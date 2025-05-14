import os
from pathlib import Path
# Remover import load_dotenv
# Remover load_dotenv()

# Determinar o diretório raiz do projeto (assumindo que tests/e2e/conftest.py está dois níveis abaixo da raiz)
# CWD é d:/PYTHON/social-media-metrics-api
# __file__ será d:/PYTHON/social-media-metrics-api/tests/e2e/conftest.py
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / ".env"

# print(f"DEBUG: Tentando carregar .env de: {dotenv_path}") # Para depuração, se necessário
# Remover a lógica de carregamento explícito do .env aqui


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Reverter importações de app.main e app.db.database para o topo
from app.main import app
from app.db.database import Base, get_db

# Definir SQLALCHEMY_DATABASE_URL aqui, pois é usado para criar a engine de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # Usado para o banco de dados de teste

# Criar a engine de teste AQUI, pois não depende das configurações da aplicação
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Remover fixtures set_test_environment, session_monkeypatch e mock_settings_and_app

# A fixture db_setup precisa de Base.
# Remover dependência de mock_settings_and_app
@pytest.fixture(scope="session")
def db_setup():
    # Importar Base AQUI, após o ambiente estar configurado e settings mockado
    # A importação de app.db.database ainda pode ocorrer cedo, mas o mock de settings
    # deve estar ativo no momento da instanciação de Settings.
    # Base já está importada no topo agora
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# A fixture db precisa de TestingSessionLocal, que já está definida globalmente.
# Ela também precisa de db_setup.
# Remover dependência de mock_settings_and_app
@pytest.fixture
def db(db_setup): # Depende de db_setup
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# A fixture client precisa de app e get_db.
# Remover dependência de mock_settings_and_app
@pytest.fixture
def client(db): # Depende de db
    # Importar a aplicação e get_db AQUI, APÓS as variáveis de ambiente serem definidas e settings mockado
    # app e get_db já estão importados no topo agora
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    # Limpar as dependências sobrescritas após o teste
    app.dependency_overrides = {}
