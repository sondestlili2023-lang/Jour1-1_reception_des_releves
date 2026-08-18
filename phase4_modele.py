"""Phase 4 : le premier verdict.

Entraine un modele qui, devant un releve, dit s'il s'agit d'un canular
(etiquette fabriquee en phase 3). Le Conseil ne veut pas d'un pourcentage
vague mais deux nombres mesures sur des releves jamais vus a l'entrainement :
- rappel   : sur 100 canulars reellement presents, combien le systeme attrape.
- precision: sur 100 releves signales, combien le sont vraiment.

Ce script sert aussi de brique reutilisee par la phase 5 : la fonction
entrainer_evaluer() prend en parametre l'ensemble de colonnes a utiliser,
ce qui permet de comparer "avec" et "sans" une colonne suspecte.
"""
import warnings

from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from phase3_regle_canular import load_or_run as charger_phase3

# Avec un signal aussi net que le mot "hoax" dans le texte, la separation est
# quasi parfaite : la regression logistique ne "converge" jamais au sens
# strict mais ses predictions sont deja stables. On n'a pas besoin de plus.
warnings.filterwarnings("ignore", category=ConvergenceWarning)

GRAINE = 42

COLONNES_NUMERIQUES = ["duration_seconds", "latitude", "longitude", "heure", "mois"]
COLONNES_CATEGORIELLES = ["shape", "state", "country"]
COLONNE_TEXTE = "comments"


def preparer_features(df):
    df = df.copy()
    df["heure"] = df["datetime"].dt.hour
    df["mois"] = df["datetime"].dt.month
    for c in COLONNES_CATEGORIELLES:
        df[c] = df[c].fillna("manquant")
    df[COLONNE_TEXTE] = df[COLONNE_TEXTE].fillna("")
    return df


def construire_pipeline(colonnes_numeriques, colonnes_categorielles, utiliser_texte):
    transformateurs = [
        ("num", SimpleImputer(strategy="median"), colonnes_numeriques),
        ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles),
    ]
    if utiliser_texte:
        transformateurs.append(
            ("texte", TfidfVectorizer(max_features=3000, min_df=2), COLONNE_TEXTE)
        )
    pretraitement = ColumnTransformer(transformateurs)
    return Pipeline([
        ("pretraitement", pretraitement),
        ("modele", LogisticRegression(max_iter=3000, class_weight="balanced")),
    ])


def entrainer_evaluer(df, colonnes_numeriques=None, colonnes_categorielles=None, utiliser_texte=True,
                       graine=GRAINE, idx_train=None, idx_test=None, pipeline=None):
    """Entraine et evalue. Par defaut, decoupe aleatoire stratifiee (phases 4/5/6).

    A partir de la phase 7, idx_train/idx_test permettent d'imposer une
    decoupe deja calculee ailleurs (par evenement, chronologique...) sans
    dupliquer la logique d'entrainement/evaluation.
    """
    colonnes_numeriques = colonnes_numeriques or COLONNES_NUMERIQUES
    colonnes_categorielles = colonnes_categorielles or COLONNES_CATEGORIELLES

    df = preparer_features(df)
    colonnes_X = colonnes_numeriques + colonnes_categorielles + ([COLONNE_TEXTE] if utiliser_texte else [])
    X = df[colonnes_X]
    y = df["is_hoax"].astype(int)

    if idx_train is None or idx_test is None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=graine
        )
    else:
        X_train, X_test = X.loc[idx_train], X.loc[idx_test]
        y_train, y_test = y.loc[idx_train], y.loc[idx_test]

    if pipeline is None:
        pipeline = construire_pipeline(colonnes_numeriques, colonnes_categorielles, utiliser_texte)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    return {
        "rappel": recall_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "exactitude": accuracy_score(y_test, y_pred),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_canulars_test": int(y_test.sum()),
        "pipeline": pipeline,
    }


def main():
    df = charger_phase3()
    resultats = entrainer_evaluer(df, utiliser_texte=True)

    print("=== Phase 4 : le premier verdict ===")
    print(f"Entrainement sur {resultats['n_train']} releves, test sur {resultats['n_test']} "
          f"jamais vus a l'entrainement ({resultats['n_canulars_test']} canulars dans ce test).")
    print(f"Rappel    : {resultats['rappel']*100:.1f} / 100 canulars reellement presents sont attrapes")
    print(f"Precision : {resultats['precision']*100:.1f} / 100 releves signales le sont vraiment")


if __name__ == "__main__":
    main()
