import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tests.test_config import TestSettings, get_test_settings

# Mock das configurações antes de qualquer importação
sys.modules['app.core.config'] = type(sys)('app.core.config')
sys.modules['app.core.config'].Settings = TestSettings
sys.modules['app.core.config'].get_settings = get_test_settings

# Agora importamos a app com as configurações mockadas
from app.db.database import Base
from app.main import app

# Configuração do banco de dados em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_setup():
    """Cria todas as tabelas no banco de teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(db_setup):
    """Fornece uma sessão do banco de dados para cada teste"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    """Fornece um cliente de teste FastAPI com banco de dados mockado"""
    from app.db.database import get_db
    
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    # Sobrescreve a dependência do banco de dados
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Limpa as dependências sobrescritas após o teste
    app.dependency_overrides.clear()
