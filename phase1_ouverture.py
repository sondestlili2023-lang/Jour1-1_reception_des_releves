"""Phase 1 : ouvrir la caisse.

Fait entrer l'integralite de la transmission en memoire, sans en perdre
une ligne en silence. Les lignes qui ne respectent pas le manifeste a
11 champs sont mises de cote, comptees, et sauvegardees a part pour
inspection (data/phase1_ecartes.csv) au lieu d'etre supprimees.
"""
import csv

import pandas as pd

from commun import COLONNES, CSV_BRUT, PHASE1_ECARTES, PHASE1_GARDES, telecharger_si_absent


def charger():
    telecharger_si_absent()

    gardees = []
    ecartees = []
    total = 0
    with open(CSV_BRUT, newline="", encoding="utf-8", errors="replace") as f:
        for ligne in csv.reader(f):
            total += 1
            if len(ligne) == len(COLONNES):
                gardees.append(ligne)
            else:
                ecartees.append(ligne)

    df = pd.DataFrame(gardees, columns=COLONNES)
    df.to_pickle(PHASE1_GARDES)

    with open(PHASE1_ECARTES, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"champ_{i}" for i in range(max(len(r) for r in ecartees))] if ecartees else [])
        w.writerows(ecartees)

    return total, df, ecartees


def load_or_run():
    """Reutilise le cache s'il existe deja, sinon relance la phase 1."""
    if PHASE1_GARDES.exists():
        return pd.read_pickle(PHASE1_GARDES)
    _, df, _ = charger()
    return df


def main():
    total, df, ecartees = charger()

    print("=== Phase 1 : ouvrir la caisse ===")
    print(f"Lignes dans le fichier      : {total}")
    print(f"Lignes chargees (11 champs) : {len(df)}")
    print(f"Lignes mises a part         : {len(ecartees)}")
    assert total == len(df) + len(ecartees), "les trois nombres ne s'additionnent pas"

    print("\nExemple de ligne mise a part :")
    exemple = ecartees[0]
    print(exemple)
    print(f"-> {len(exemple)} champs au lieu de {len(COLONNES)} attendus.")
    print(
        "   La colonne 'city' y est systematiquement vide : un champ "
        "supplementaire (vide) s'est glisse dans la ligne, ce qui decale "
        "tout le reste. Impossible de savoir avec certitude quel champ "
        "a ete duplique, donc on ne devine pas : on met la ligne de cote."
    )


if __name__ == "__main__":
    main()
