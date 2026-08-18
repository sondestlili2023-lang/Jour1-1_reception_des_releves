"""Constantes et utilitaires partages entre les scripts phaseN.py.

Ce fichier n'est pas une "phase" en soi : il evite juste de recopier
l'URL, la liste des colonnes et les chemins de fichiers dans chaque script.
"""
from pathlib import Path
import urllib.request

RACINE = Path(__file__).resolve().parent
DATA_DIR = RACINE / "data"
DATA_DIR.mkdir(exist_ok=True)

URL_TRANSMISSION = (
    "https://raw.githubusercontent.com/planetsig/ufo-reports/master/"
    "csv-data/ufo-complete-geocoded-time-standardized.csv"
)
CSV_BRUT = DATA_DIR / "releves_klaxo3.csv"

# Le manifeste retrouve a part (l'ordre des 11 champs, sans en-tete dans le fichier)
COLONNES = [
    "datetime",
    "city",
    "state",
    "country",
    "shape",
    "duration_seconds",
    "duration_hours_min",
    "comments",
    "date_posted",
    "latitude",
    "longitude",
]

# Fichiers intermediaires produits par chaque phase (caches locaux, non versionnes)
PHASE1_GARDES = DATA_DIR / "phase1_gardes.pkl"
PHASE1_ECARTES = DATA_DIR / "phase1_ecartes.csv"
PHASE2_TYPES = DATA_DIR / "phase2_types.pkl"
PHASE3_ETIQUETE = DATA_DIR / "phase3_etiquete.pkl"


def telecharger_si_absent():
    """Recupere la transmission si elle n'est pas deja sur le disque."""
    if CSV_BRUT.exists():
        return CSV_BRUT
    print(f"Telechargement de la transmission depuis {URL_TRANSMISSION} ...")
    urllib.request.urlretrieve(URL_TRANSMISSION, CSV_BRUT)
    print(f"Transmission enregistree dans {CSV_BRUT}")
    return CSV_BRUT
