# Bureau d'Analyse Terrestre -- releves Klaxo-3

Analyse des 88 875 signalements OVNI transmis par la sonde Klaxo-3.

## Utilisation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pandas numpy scikit-learn
python3 analyse.py
```

`analyse.py` telecharge la transmission, refait tout le travail et
affiche les chiffres de chaque phase, d'une traite, sur une machine
neuve (~3 minutes). Chaque phase vit aussi dans son propre fichier
(`phase1_ouverture.py` a `phase18_archive.py`) et peut etre relancee
seule. A partir de la phase 13, elles s'appuient toutes sur
`modele_final.py`, qui assemble le modele construit dans les phases 7
a 12.

Les chiffres et decisions sont detailles dans [RAPPORT.md](RAPPORT.md).
Le fichier de donnees n'est pas versionne (il se telecharge, voir
`commun.py`) : tout ce qui est genere atterrit dans `data/`.
