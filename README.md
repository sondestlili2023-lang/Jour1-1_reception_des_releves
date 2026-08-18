# Bureau d'Analyse Terrestre -- releves Klaxo-3

Analyse des 88 875 signalements OVNI transmis par la sonde Klaxo-3.

## Utilisation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 analyse.py
```

`analyse.py` telecharge la transmission, refait tout le travail et
affiche les chiffres de chaque phase, d'une traite, sur une machine
neuve. Chaque phase vit aussi dans son propre fichier (`phase1_ouverture.py`
a `phase12_ville_heure.py`) et peut etre relancee seule.

Les chiffres et decisions sont detailles dans [RAPPORT.md](RAPPORT.md).
Le fichier de donnees n'est pas versionne (il se telecharge, voir
`commun.py`) : tout ce qui est genere atterrit dans `data/`, ignore par git.
