from pathlib import Path
from yarl import URL

ROOT = list(Path(__file__).parents)[1]

FOLDER_DATA = ROOT / "data"
FOLDER_RAW = FOLDER_DATA / "raw"

# Censos 
CENSO_DATA = FOLDER_DATA / "Censos"
censo_url = URL("https://ine.mx/wp-content/uploads/")

# Elecciones
ELECCIONES_DATA = FOLDER_DATA / "Elecciones"
elecciones_url = URL("https://ieesonora.org.mx/resultados/computo/diputaciones")