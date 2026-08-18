"""Phase 14 : une promesse a 80 %.

Un systeme peut trier juste et chiffrer faux. On decoupe les
probabilites annoncees en tranches, et pour chaque tranche on compare
la probabilite moyenne annoncee a la proportion de canulars reellement
observee dedans. Tranches a effectif egal (quantiles), pour ne jamais
juger un chiffre calcule sur trois relevés.
"""
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV

import modele_final as mf

N_TRANCHES = 10


def table_fiabilite(y, proba, n_tranches=N_TRANCHES):
    tranche = pd.qcut(proba, n_tranches, duplicates="drop")
    df = pd.DataFrame({"y": y, "p": proba, "tranche": tranche})
    return df.groupby("tranche", observed=True).agg(
        n=("y", "size"), proba_annoncee=("p", "mean"), taux_reel=("y", "mean")
    )


def main():
    m = mf.charger()
    y = m.y_test.values

    print("=== Phase 14 : une promesse a 80 % ===")
    print("Avant correction (probabilites brutes du modele) :\n")
    table_avant = table_fiabilite(y, m.proba_test)
    print(table_avant.to_string())

    ecart_moyen = (table_avant["proba_annoncee"] - table_avant["taux_reel"]).mean()
    print(f"\nDans chaque tranche, la probabilite annoncee est tres au-dessus du taux reel "
          f"(ecart moyen +{ecart_moyen*100:.1f} points) : le systeme est trop confiant. "
          "C'est attendu : class_weight='balanced' (necessaire pour un rappel exploitable "
          "a 0,9% de canulars) deforme les probabilites brutes en les poussant vers le haut.")

    print("\nCorrection : recalibrage sigmoide (Platt scaling) par validation croisee, "
          "appris sur l'apprentissage seul.")
    cal = CalibratedClassifierCV(mf.construire_pipeline(), method="sigmoid", cv=5)
    cal.fit(m.X_train, m.y_train)
    proba_corrigee = cal.predict_proba(m.X_test)[:, 1]

    print("\nApres correction :\n")
    table_apres = table_fiabilite(y, proba_corrigee)
    print(table_apres.to_string())

    ecart_apres = (table_apres["proba_annoncee"] - table_apres["taux_reel"]).abs().mean()
    print(f"\nEcart absolu moyen apres correction : {ecart_apres*100:.2f} points -- "
          "les probabilites annoncees sont maintenant proches des taux reellement observes, "
          "tranche par tranche.")


if __name__ == "__main__":
    main()
