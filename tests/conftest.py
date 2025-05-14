import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

# Configurações padrão para pytest
pytest_plugins = [
    "pytest_mock",
]