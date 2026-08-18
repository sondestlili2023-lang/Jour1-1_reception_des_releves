"""Phase 15 : deux analystes, deux chiffres.

Le rappel et la precision se calculent sur une poignee de canulars du
test (140 sur 18269). Deplacer trois d'entre eux d'un cote a l'autre de
la decoupe suffirait a bouger le chiffre de plusieurs points, sans que
le modele ait change. On mesure cette incertitude par bootstrap : on
retire le test avec remise plusieurs centaines de fois, en gardant le
modele fixe, et on regarde de combien le chiffre bouge.
"""
import numpy as np
from sklearn.metrics import precision_score, recall_score

import modele_final as mf

SEUIL = 0.5
N_DECOUPES = 1000
GRAINE = 42


def bootstrap(y, proba, seuil=SEUIL, n_decoupes=N_DECOUPES, graine=GRAINE):
    rng = np.random.default_rng(graine)
    n = len(y)
    rappels, precisions = [], []
    for _ in range(n_decoupes):
        idx = rng.integers(0, n, n)
        yb = y[idx]
        predb = (proba[idx] >= seuil).astype(int)
        if yb.sum() == 0 or predb.sum() == 0:
            continue
        rappels.append(recall_score(yb, predb, zero_division=0))
        precisions.append(precision_score(yb, predb, zero_division=0))
    return np.array(rappels), np.array(precisions)


def main():
    m = mf.charger()
    y, proba = m.y_test.values, m.proba_test
    n_canulars = int(y.sum())

    rappels, precisions = bootstrap(y, proba)

    ic_rappel = np.percentile(rappels, [2.5, 97.5])
    ic_precision = np.percentile(precisions, [2.5, 97.5])

    print("=== Phase 15 : deux analystes, deux chiffres ===")
    print(f"Taille de la partie test : {len(y)}")
    print(f"Canulars reellement presents dedans : {n_canulars}")
    print(f"Decoupes utilisees pour la fourchette (rechantillonnage du test, modele fixe) : {N_DECOUPES}")

    print(f"\nRappel    : {np.median(rappels)*100:.1f} % -- intervalle 95% : "
          f"[{ic_rappel[0]*100:.1f} % ; {ic_rappel[1]*100:.1f} %]")
    print(f"Precision : {np.median(precisions)*100:.2f} % -- intervalle 95% : "
          f"[{ic_precision[0]*100:.2f} % ; {ic_precision[1]*100:.2f} %]")

    print(
        f"\nReponse au Conseil sur les deux analystes (0,31 et 0,34) : la question est mal posee. "
        f"Avec seulement {n_canulars} canulars dans notre propre test, notre intervalle de precision "
        f"a lui seul fait {(ic_precision[1]-ic_precision[0])*100:.2f} points de large -- un ecart de "
        "0,03 entre deux systemes ne se distingue pas du bruit d'echantillonnage. Il faudrait soit "
        "plus de canulars de test, soit un test statistique explicite (pas juste comparer deux "
        "decimales), pour dire que l'un des deux systemes est vraiment meilleur."
    )


if __name__ == "__main__":
    main()
