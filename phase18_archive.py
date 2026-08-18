"""Phase 18 : la transmission d'archive.

L'etiquette canular n'est pas une mesure, c'est une annotation ecrite a
la main par le Bureau, un jour donne, avec les habitudes de ce jour-la.
Si ces habitudes ont change au fil des decennies couvertes par la
transmission, le systeme a appris une definition moyenne qui ne
correspond a aucune epoque en particulier. Deux mesures, puis un plan de
surveillance qui ne demande jamais de connaitre la reponse -- parce qu'en
production, on ne la connait jamais tout de suite.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score

import modele_final as mf
from phase13_facture import chercher_seuil_optimal


def main():
    m = mf.charger()
    df = m.df

    print("=== Phase 18 : la transmission d'archive ===")
    print("Proportion de canulars par annee de publication (date_posted), toute la periode :\n")
    par_annee = df.assign(annee=df["date_posted"].dt.year).groupby("annee")["is_hoax"].mean() * 100
    print(par_annee.round(2).to_string())
    print(
        "\nLa courbe n'est pas plate : quasi nulle de 1998 a 2004, elle grimpe a partir de 2005, "
        "pic en 2008 (2,76 %), puis redescend et refluctue -- confirme des la phase 8. Le systeme "
        "a bien appris une definition moyenne d'une regle qui a change au moins trois fois."
    )

    print("\n--- L'epreuve : apprentissage sur le plus ancien, test sur le plus recent ---")
    cutoff50 = df["date_posted"].quantile(0.5)
    idx_train = df.index[df["date_posted"] < cutoff50]
    idx_test = df.index[df["date_posted"] >= cutoff50]
    X_train, y_train = df.loc[idx_train, m.colonnes_X], df.loc[idx_train, "is_hoax"].astype(int)
    X_test, y_test = df.loc[idx_test, m.colonnes_X], df.loc[idx_test, "is_hoax"].astype(int)

    pipeline = mf.construire_pipeline()
    pipeline.fit(X_train, y_train)
    proba = pipeline.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    rappel = recall_score(y_test, pred) * 100
    precision = precision_score(y_test, pred) * 100

    print(f"Coupure a la mediane ({cutoff50.date()}) : {len(idx_train)} apprentissage "
          f"(avant) / {len(idx_test)} test (apres), {int(y_test.sum())} canulars dans le test.")
    print(f"Rappel : {rappel:.1f} %   Precision : {precision:.2f} %")
    print(f"A comparer a la phase 8 (decoupe 80/20, ecart de temps plus court) : rappel 53,6 %, precision 1,2 %.")
    print(
        f"Le rappel chute de 53,6 % a {rappel:.1f} % quand on force le modele a apprendre sur une "
        "epoque plus ancienne et a juger une epoque plus lointaine : plus l'ecart temporel entre "
        "apprentissage et deploiement grandit, moins la definition apprise colle a la realite "
        "qu'on lui demande de juger."
    )

    print("\n--- Ce qu'on surveille, sans jamais connaitre la reponse ---")
    seuil, _ = chercher_seuil_optimal(m.y_test.values, m.proba_test)
    proba_train_ref = m.pipeline.predict_proba(m.X_train)[:, 1]
    mois_ref = m.df.loc[m.idx_train, "date_posted"].dt.to_period("M")

    proba_mensuelle = pd.Series(proba_train_ref, index=m.idx_train).groupby(mois_ref).mean()
    base_proba, ecart_proba = proba_mensuelle.mean(), proba_mensuelle.std()

    manquant_country = (m.df.loc[m.idx_train, "country"] == "manquant").groupby(mois_ref).mean() * 100
    base_mc, ecart_mc = manquant_country.mean(), manquant_country.std()

    manquant_duree = m.df.loc[m.idx_train, "duree_manquante"].groupby(mois_ref).mean() * 100
    base_md, ecart_md = manquant_duree.mean(), manquant_duree.std()

    print("1. Probabilite moyenne predite par mois (aucune etiquette necessaire : on n'a besoin "
          "que des relevés et du modele).")
    print(f"   Reference (apprentissage) : {base_proba:.3f} +/- {ecart_proba:.3f}")
    print(f"   Alerte si la moyenne du mois sort de [{base_proba-2*ecart_proba:.3f} ; "
          f"{base_proba+2*ecart_proba:.3f}] (2 ecarts-types).")

    print("\n2. Taux de valeurs manquantes dans les champs cles (country, duree) par mois "
          "(mesurable des la reception, avant tout traitement du dossier par un analyste).")
    print(f"   country manquant -- reference : {base_mc:.1f} % +/- {ecart_mc:.1f} % "
          f"-- alerte hors [{base_mc-2*ecart_mc:.1f} % ; {base_mc+2*ecart_mc:.1f} %]")
    print(f"   duree manquante  -- reference : {base_md:.1f} % +/- {ecart_md:.1f} % "
          f"-- alerte hors [{base_md-2*ecart_md:.1f} % ; {base_md+2*ecart_md:.1f} %]")
    print(
        "   Ces deux indicateurs sont lies : duree_manquante est la colonne la plus importante du "
        "modele (phase 16). Si son taux de trous derive, c'est le signal le plus important qui "
        "change de nature sous les pieds du modele."
    )

    print("\nFrequence de lecture : mensuelle -- assez de volume par mois (quelques milliers de "
          "relevés historiquement) pour que les moyennes ne soient pas juste du bruit d'un jour.")
    print("Seuil de rappel des analystes : un des deux indicateurs sort de sa bande a 2 "
          "ecarts-types deux mois de suite (un seul mois hors bande arrive par hasard environ "
          "1 fois sur 20 meme si rien n'a change ; deux mois consecutifs, beaucoup plus rarement).")


if __name__ == "__main__":
    main()
