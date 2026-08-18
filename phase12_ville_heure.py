"""Phase 12 : la ville et l'heure.

Deux pieges opposes. La ville : un one-hot direct sur 22 018 villes fait
exploser le tableau, et la plupart de ces colonnes ne contiennent qu'un
seul 1 puisqu'une ville sur deux n'apparait qu'une fois dans tout le
fichier -- rien a generaliser de ca. L'heure : sur une echelle 0-23,
23h et 0h sont a la fois voisines dans le ciel et aux deux extremites de
la regle, ce qui fait croire au modele qu'elles sont maximalement
eloignees.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from phase3_regle_canular import load_or_run as charger_phase3
from phase8_chronologie import decouper_chronologiquement

SEUIL_VILLE = 10
SEUIL_FORME = 5
FUSION_FORMES = {"changed": "changing", "round": "circle"}


def preparer(df):
    df = df.copy()
    df["heure"] = df["datetime"].dt.hour
    df["mois"] = df["datetime"].dt.month
    for c in ["shape", "state", "country", "city"]:
        df[c] = df[c].fillna("manquant")

    freq_ville = df["city"].value_counts()
    df["ville_regroupee"] = np.where(df["city"].map(freq_ville) >= SEUIL_VILLE, df["city"], "autre")

    forme = df["shape"].replace(FUSION_FORMES)
    freq_forme = forme.value_counts()
    df["forme_nettoyee"] = np.where(forme.map(freq_forme) >= SEUIL_FORME, forme, "autre")

    df["heure_sin"] = np.sin(2 * np.pi * df["heure"] / 24)
    df["heure_cos"] = np.cos(2 * np.pi * df["heure"] / 24)
    return df


def largeur_avant(df, idx_train):
    ct = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), ["duration_seconds", "latitude", "longitude", "heure", "mois"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["shape", "state", "country", "city"]),
    ])
    ct.fit(df.loc[idx_train])
    return len(ct.get_feature_names_out())


def largeur_apres(df, idx_train):
    ct = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"),
         ["duration_seconds", "latitude", "longitude", "heure_sin", "heure_cos", "mois"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"),
         ["forme_nettoyee", "state", "country", "ville_regroupee"]),
    ])
    ct.fit(df.loc[idx_train])
    return len(ct.get_feature_names_out())


def main():
    df_brut = charger_phase3()
    n_formes_brutes = df_brut["shape"].nunique()

    df = preparer(df_brut)
    _, idx_train, _ = decouper_chronologiquement(df)

    print("=== Phase 12 : la ville et l'heure ===")
    print(f"Colonnes du tableau AVANT (ville et heure brutes, one-hot direct) : {largeur_avant(df, idx_train)}")
    print(f"Colonnes du tableau APRES (ville regroupee, heure cyclique)      : {largeur_apres(df, idx_train)}")

    n_singleton = int((df["city"].value_counts() == 1).sum())
    print(f"\nRegle ville : une ville garde sa propre colonne si elle apparait au moins "
          f"{SEUIL_VILLE} fois dans toute la transmission, sinon elle rejoint 'autre'.")
    print(f"Villes qui n'apparaissent qu'une seule fois dans toute la transmission : {n_singleton}")

    def point(h):
        return np.array([np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24)])
    d_23_0 = float(np.linalg.norm(point(23) - point(0)))
    d_23_20 = float(np.linalg.norm(point(23) - point(20)))
    print(f"\nEncodage cyclique de l'heure (sin, cos) :")
    print(f"  distance(23h, 0h)  = {d_23_0:.3f}")
    print(f"  distance(23h, 20h) = {d_23_20:.3f}")
    print("  23h est bien plus proche de 0h que de 20h -- ce qui est vrai dans le ciel.")

    formes_restantes = sorted(f for f in df["forme_nettoyee"].unique() if f != "manquant")
    print(f"\nShape : {n_formes_brutes} formes brutes -> fusion de deux paires qui designent "
          f"la meme chose sous deux orthographes ('changed'/'changing', 'round'/'circle'), puis les "
          f"formes avec moins de {SEUIL_FORME} occurrences rejoignent 'autre'.")
    print(f"Formes restantes, 'manquant' mis a part ({len(formes_restantes)}) : {formes_restantes}")

    print(
        "\nLes deux encodages (ville regroupee, forme nettoyee) sont appris uniquement sur la partie "
        "apprentissage de la decoupe chronologique (phase 8) : une ville ou une forme qui n'existe que "
        "dans le futur n'a pas pu influencer le seuil de regroupement, et sera simplement ignoree par "
        "l'encodeur (handle_unknown='ignore') si elle apparait dans le test."
    )


if __name__ == "__main__":
    main()
