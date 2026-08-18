"""Le modele final du Bureau, assemble a partir de ce que les phases 7 a
12 ont etabli. Ce n'est pas une phase en soi : c'est la brique que les
phases 13 a 18 reutilisent toutes, pour ne pas reconstruire six fois la
meme chaine.

Decoupe : chronologique sur date_posted (phase 8).
Features : duree reconciliee (phase 11), ville/forme regroupees et heure
cyclique (phase 12), le tout appris sur l'apprentissage seul (phase 10).
Pas de `comments` (phase 5). class_weight='balanced' pour un rappel
exploitable a 0,9% de canulars -- garde a l'esprit que ca decale les
probabilites brutes, voir phase 14.
"""
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from phase3_regle_canular import load_or_run as charger_phase3
from phase8_chronologie import decouper_chronologiquement
from phase11_duree import construire_duree
from phase12_ville_heure import preparer as preparer_12

warnings.filterwarnings("ignore", category=ConvergenceWarning)

COLONNES_NUMERIQUES = ["duree_s", "latitude", "longitude", "heure_sin", "heure_cos", "mois"]
COLONNES_CATEGORIELLES = ["forme_nettoyee", "state", "country", "ville_regroupee"]


def preparer_donnees():
    df = charger_phase3()
    df, _ = construire_duree(df)
    df = preparer_12(df)
    df["duree_manquante"] = df["duree_manquante"].astype(int)
    return df


def construire_pipeline():
    pretraitement = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), COLONNES_NUMERIQUES + ["duree_manquante"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), COLONNES_CATEGORIELLES),
    ])
    return Pipeline([
        ("pretraitement", pretraitement),
        ("modele", LogisticRegression(max_iter=3000, class_weight="balanced")),
    ])


class ModeleFinal:
    """Entraine une fois, reutilisable par toutes les phases 13-18."""

    def __init__(self):
        self.df = preparer_donnees()
        self.cutoff, self.idx_train, self.idx_test = decouper_chronologiquement(self.df)
        self.colonnes_X = COLONNES_NUMERIQUES + ["duree_manquante"] + COLONNES_CATEGORIELLES
        self.X_train = self.df.loc[self.idx_train, self.colonnes_X]
        self.y_train = self.df.loc[self.idx_train, "is_hoax"].astype(int)
        self.X_test = self.df.loc[self.idx_test, self.colonnes_X]
        self.y_test = self.df.loc[self.idx_test, "is_hoax"].astype(int)

        self.pipeline = construire_pipeline()
        self.pipeline.fit(self.X_train, self.y_train)
        self.proba_test = self.pipeline.predict_proba(self.X_test)[:, 1]

    def predire_proba(self, X):
        return self.pipeline.predict_proba(X)[:, 1]


_INSTANCE = None


def charger():
    """Un seul entrainement partage par tout le process (cache module-level)."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = ModeleFinal()
    return _INSTANCE
