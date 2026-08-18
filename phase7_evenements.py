"""Phase 7 : plusieurs temoins, un seul evenement.

Un meme survol produit plusieurs releves : un par temoin, la meme nuit,
dans la meme ville. La decoupe aleatoire de la phase 4 melange ces
temoins entre apprentissage et test, si bien qu'a l'examen le systeme
"reconnait" une soiree qu'il a deja lue vingt-quatre fois plutot que de
detecter quoi que ce soit. On regroupe les releves par evenement et on
force chaque evenement entier du meme cote.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from phase3_regle_canular import load_or_run as charger_phase3
from phase4_modele import entrainer_evaluer

GRAINE = 42


def ajouter_evenement(df):
    """Un evenement = memes ville+etat, meme nuit (le champ datetime).

    Les 1220 lignes sans datetime valide (phase 2) ne peuvent partager de
    nuit avec personne : on leur donne un identifiant a elles seules plutot
    que de les regrouper arbitrairement.
    """
    df = df.copy()
    df["evenement"] = [
        f"SANS_DATE_{i}" if pd.isna(dt) else f"{ville}|{etat}|{dt.date()}"
        for i, (dt, ville, etat) in enumerate(zip(df["datetime"], df["city"], df["state"]))
    ]
    return df


def decoupe_ancienne_a_cheval(df):
    """Combien de lignes appartenaient a un evenement coupe en deux par la
    decoupe aleatoire de la phase 4/5 (meme graine, meme test_size)."""
    idx_train, idx_test = train_test_split(
        df.index, test_size=0.2, stratify=df["is_hoax"].astype(int), random_state=GRAINE
    )
    evt_train = set(df.loc[idx_train, "evenement"])
    evt_test = set(df.loc[idx_test, "evenement"])
    evenements_a_cheval = evt_train & evt_test
    lignes_a_cheval = df["evenement"].isin(evenements_a_cheval).sum()
    return len(evenements_a_cheval), int(lignes_a_cheval)


def decoupe_par_evenement(df, graine=GRAINE):
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=graine)
    idx_train, idx_test = next(gss.split(df, groups=df["evenement"]))
    return df.index[idx_train], df.index[idx_test]


def main():
    df = ajouter_evenement(charger_phase3())

    tailles = df.groupby("evenement").size()
    multi = tailles[tailles > 1]
    plus_gros = tailles.idxmax()

    print("=== Phase 7 : plusieurs temoins, un seul evenement ===")
    print("Un evenement = meme ville, meme etat, meme nuit (colonne datetime).\n")
    print(f"Evenements signales par plus d'un temoin : {len(multi)}")
    print(f"Temoins pour le plus gros evenement       : {tailles.max()} ({plus_gros})")

    n_evt_cheval, n_lignes_cheval = decoupe_ancienne_a_cheval(df)
    print(f"\nAvec la decoupe aleatoire des phases 4/5/6 :")
    print(f"  evenements coupes en deux entre apprentissage et test : {n_evt_cheval}")
    print(f"  releves concernes par cette coupe                     : {n_lignes_cheval}")

    print(f"\nExemple -- le plus gros evenement, tous ses temoins :")
    exemple = df[df["evenement"] == plus_gros][["datetime", "city", "state", "shape", "is_hoax"]]
    print(exemple.to_string())

    idx_train, idx_test = decoupe_par_evenement(df)
    evt_train = set(df.loc[idx_train, "evenement"])
    evt_test = set(df.loc[idx_test, "evenement"])
    assert not (evt_train & evt_test), "un evenement est encore a cheval !"
    print(f"\nNouvelle decoupe par evenement : {len(idx_train)} apprentissage / {len(idx_test)} test,")
    print(f"aucun evenement a cheval (verifie : {len(evt_train & evt_test)} evenement(s) commun(s)).")
    print(f"Tous les {tailles.max()} temoins du plus gros evenement sont du meme cote : "
          f"{'test' if df.loc[df['evenement'] == plus_gros].index[0] in idx_test else 'apprentissage'}.")

    avant = entrainer_evaluer(df, utiliser_texte=False)
    apres = entrainer_evaluer(df, utiliser_texte=False, idx_train=idx_train, idx_test=idx_test)
    print(f"\n                 avant (decoupe aleatoire)   apres (decoupe par evenement)")
    print(f"Rappel           {avant['rappel']*100:>21.1f}   {apres['rappel']*100:>27.1f}")
    print(f"Precision        {avant['precision']*100:>21.1f}   {apres['precision']*100:>27.1f}")

    texte = df["comments"].fillna("")
    non_vide = texte != ""
    dup = texte[non_vide].duplicated(keep=False)
    n_dup = int(dup.sum())
    print(f"\nTemoignages identiques mot pour mot sur plusieurs lignes : {n_dup}")
    exemple_dup = texte[non_vide][dup].value_counts().index[0]
    lignes_exemple = df[texte == exemple_dup][["datetime", "city", "state"]]
    print(f"Exemple -- '{exemple_dup}' apparait {len(lignes_exemple)} fois, sur des villes et dates differentes :")
    print(lignes_exemple.head(5).to_string())
    print(
        "Ce ne sont pas des copies d'un meme temoignage sur un meme evenement (villes et dates "
        "differentes a chaque fois) : ce sont des phrases courtes et generiques ('Fireball', "
        "'Lights in the sky'...) ecrites independamment par des temoins sans lien entre eux. On "
        "ne les fusionne donc pas comme un evenement et on ne les supprime pas : ce sont des "
        "releves distincts et legitimes. Le seul risque serait de les reutiliser comme feature "
        "texte, ce qu'on ne fait plus depuis la phase 5."
    )


if __name__ == "__main__":
    main()
