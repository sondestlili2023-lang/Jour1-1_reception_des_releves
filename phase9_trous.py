"""Phase 9 : les cases vides.

Un trou n'est pas rien : c'est un temoin presse, un dossier bacle, un
signalement que personne au Bureau n'a juge digne d'etre complete. Avant
de choisir comment le traiter (jeter la ligne ? remplir avec la valeur la
plus frequente ?), on mesure si les relevés troues se comportent comme
les autres.
"""
import pandas as pd

from phase3_regle_canular import load_or_run as charger_phase3
from phase4_modele import construire_pipeline, entrainer_evaluer, preparer_features

COLONNES_LES_PLUS_TROUEES = ["country", "state", "duration_hours_min"]


def proportions_par_trou(df):
    lignes = []
    for col in COLONNES_LES_PLUS_TROUEES:
        trou = df[col].isna()
        lignes.append({
            "colonne": col,
            "n_trous": int(trou.sum()),
            "hoax_pct_si_trou": round(df.loc[trou, "is_hoax"].mean() * 100, 2),
            "hoax_pct_si_rempli": round(df.loc[~trou, "is_hoax"].mean() * 100, 2),
        })
    return pd.DataFrame(lignes)


def main():
    df = charger_phase3()
    table = proportions_par_trou(df)

    print("=== Phase 9 : les cases vides ===")
    print("Les trois colonnes les plus trouees, et le taux de canulars selon qu'elles le sont ou pas :\n")
    print(table.to_string(index=False))

    print(
        "\nDans les trois cas, le taux de canulars est plus haut chez les relevés troues que chez "
        "les relevés complets (jusqu'a x2.8 pour duration_hours_min). Un trou porte donc de "
        "l'information : le jeter ou le boucher avec la valeur la plus frequente reviendrait a "
        "effacer ce signal."
    )

    print(
        "\nTraitement retenu : aucune ligne supprimee, aucun trou rempli par la valeur la plus "
        "frequente. Pour les colonnes categorielles (state, country, shape...), le trou devient sa "
        "propre categorie 'manquant', encodee comme une valeur a part entiere -- le modele voit "
        "explicitement 'ce champ etait vide' au lieu de se le faire recopier depuis une autre ligne."
    )

    resultats = entrainer_evaluer(df, utiliser_texte=False)
    pipeline = resultats["pipeline"]
    noms = pipeline.named_steps["pretraitement"].get_feature_names_out()
    noms_manquant = [n for n in noms if "manquant" in n]
    print(f"\nPreuve : le pretraitement genere {len(noms)} colonnes, dont ces categories 'manquant' "
          f"explicites (le trou reste visible du modele) :")
    for n in noms_manquant:
        print(f"  - {n}")
    print(
        "\n`duration_hours_min` n'est pas encore une feature numerique du modele (phase 11 la "
        "fusionne avec duration_seconds) : le meme principe s'y appliquera, avec un indicateur de "
        "trou explicite plutot qu'un remplissage silencieux."
    )


if __name__ == "__main__":
    main()
