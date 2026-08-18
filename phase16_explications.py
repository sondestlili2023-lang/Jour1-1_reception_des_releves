"""Phase 16 : trois dossiers sur le bureau.

Deux niveaux d'explication qui ne se remplacent pas. Le dossier :
pourquoi CE relevé a bascule dans un sens ou l'autre -- on decompose la
prediction en contribution par feature (coefficient x valeur, le modele
est une regression logistique, la decomposition est exacte). L'ensemble :
sur quoi le systeme s'appuie en general -- on abime une colonne a la
fois (permutation) et on regarde de combien l'average precision chute.
"""
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

import modele_final as mf
from phase13_facture import chercher_seuil_optimal


def expliquer_dossier(m, idx_ligne, top=6):
    pretraitement = m.pipeline.named_steps["pretraitement"]
    modele = m.pipeline.named_steps["modele"]
    noms = pretraitement.get_feature_names_out()
    coefs = modele.coef_[0]

    ligne = m.df.loc[[idx_ligne], m.colonnes_X]
    x = pretraitement.transform(ligne)
    if hasattr(x, "toarray"):
        x = x.toarray()
    contributions = x[0] * coefs
    ordre = np.argsort(-np.abs(contributions))[:top]
    return pd.DataFrame({
        "feature": noms[ordre],
        "valeur": x[0][ordre],
        "contribution": contributions[ordre],
    })


def main():
    m = mf.charger()
    y, proba = m.y_test.values, m.proba_test
    seuil, _ = chercher_seuil_optimal(y, proba)

    idx_test = m.idx_test
    i_confiant = idx_test[np.argmax(proba)]
    au_dessus = np.where(proba >= seuil)[0]
    i_borderline = idx_test[au_dessus[np.argmin(proba[au_dessus])]]
    rates = np.where((y == 1) & (proba < seuil))[0]
    i_rate = idx_test[rates[np.argmax(proba[rates])]]

    print("=== Phase 16 : trois dossiers sur le bureau ===")
    print(f"Frontiere de reference (phase 13) : {seuil:.3f}\n")

    dossiers = [
        ("Forte confiance", i_confiant, "marque canular avec une tres forte confiance"),
        ("Juste au-dessus de la frontiere", i_borderline, "marque canular, mais de justesse"),
        ("Canular laisse passer", i_rate, "vrai canular, non signale"),
    ]

    for titre, idx, description in dossiers:
        ligne = m.df.loc[idx]
        print(f"--- {titre} (relevé {idx}) ---")
        print(f"{ligne['datetime']} -- {ligne['city']}, {ligne['state']}, {ligne['country']} -- "
              f"forme {ligne['shape']} -- is_hoax reel : {ligne['is_hoax']}")
        i_pos = np.where(idx_test == idx)[0][0]
        print(f"Probabilite annoncee : {proba[i_pos]:.3f} ({description})")
        print(expliquer_dossier(m, idx).to_string(index=False))
        print()

    print(
        "Dossier 'forte confiance' : c'est le relevé de la phase 11 avec une duree de "
        "'31 years' -- duree_s (97 836 000 secondes) pese a lui seul plus que toutes les "
        "autres colonnes reunies. Et ce relevé n'est PAS marque canular par le Bureau "
        "(is_hoax=False) : c'est une fausse alerte a tres forte confiance, causee par une "
        "seule valeur extreme.\n"
        "Dossier 'juste au-dessus' : c'est l'indicateur duree_manquante qui fait basculer, "
        "pas une valeur de duree en particulier.\n"
        "Dossier 'laisse passer' : les signaux positifs existent (duree manquante, forme "
        "'egg') mais restent trop faibles face a un profil par ailleurs tres ordinaire "
        "(Etats-Unis, mois de janvier) pour franchir une frontiere volontairement haute."
    )

    print("\n--- Explication d'ensemble (permutation importance, average precision) ---")
    r = permutation_importance(m.pipeline, m.X_test, m.y_test, scoring="average_precision",
                                n_repeats=10, random_state=42, n_jobs=-1)
    ordre = np.argsort(-r.importances_mean)
    classement = pd.DataFrame({
        "colonne": [m.colonnes_X[i] for i in ordre],
        "chute_moyenne": [round(r.importances_mean[i], 4) for i in ordre],
        "ecart_type": [round(r.importances_std[i], 4) for i in ordre],
    })
    print(classement.to_string(index=False))

    print(
        "\nSurprise : duree_s (la valeur numerique de la duree) est presque au dernier rang "
        "du classement global (0.0005), alors qu'elle est la variable qui domine, et de loin, "
        "l'explication du dossier 'forte confiance' ci-dessus. En moyenne sur tout le test, la "
        "duree brute n'aide presque jamais -- mais sur UN relevé precis avec une valeur extreme, "
        "elle peut a elle seule faire basculer la decision. Le classement global et l'explication "
        "d'un dossier ne repondent donc pas a la meme question, exactement comme annonce."
    )


if __name__ == "__main__":
    main()
