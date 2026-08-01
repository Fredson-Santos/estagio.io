import sys
from pathlib import Path

# Adiciona o diretório /app/scraper ao sys.path para resolução do pacote 'src'
scraper_dir = Path(__file__).parent.parent
if str(scraper_dir) not in sys.path:
    sys.path.insert(0, str(scraper_dir))
