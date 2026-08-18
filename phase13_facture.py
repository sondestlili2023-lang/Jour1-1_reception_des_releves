"""Phase 13 : la facture du Bureau.

Un score n'est pas une decision : il faut une frontiere. La bibliotheque
en pose une par defaut a 0.5, sans savoir qu'un canular rate coute au
Bureau 15 fois plus cher qu'une fausse alerte. On cherche la frontiere
qui coute le moins cher, sur la partie test, avec cette grille.

Note sur la grille : le tableau de couts vote par le Conseil ne nous est
pas parvenu (perdu dans la transmission de l'enonce) -- le seul chiffre
donne explicitement est le ratio 15/1 entre un canular rate (faux negatif)
et une fausse alerte (faux positif). On construit la grille la plus
simple qui respecte ce ratio : 15 credits par canular rate, 1 credit par
fausse alerte, 0 pour une reponse correcte.
"""
import numpy as np

import modele_final as mf

COUT_FAUX_NEGATIF = 15
COUT_FAUSSE_ALERTE = 1


def facture(y, proba, seuil):
    pred = (proba >= seuil).astype(int)
    fn = int(((pred == 0) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    return COUT_FAUX_NEGATIF * fn + COUT_FAUSSE_ALERTE * fp, fn, fp


def chercher_seuil_optimal(y, proba):
    candidats = np.unique(np.concatenate([[0.0, 1.0], proba]))
    couts = [facture(y, proba, s)[0] for s in candidats]
    i = int(np.argmin(couts))
    return candidats[i], couts[i]


def main():
    m = mf.charger()
    y, proba = m.y_test.values, m.proba_test

    print("=== Phase 13 : la facture du Bureau ===")
    print(f"Grille retenue : {COUT_FAUX_NEGATIF} credits par canular rate, "
          f"{COUT_FAUSSE_ALERTE} credit par fausse alerte.\n")

    print("Facture selon la frontiere (echantillon) :")
    print(f"{'seuil':>6} {'facture':>8} {'faux negatifs':>14} {'fausses alertes':>16}")
    for s in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        cout, fn, fp = facture(y, proba, s)
        print(f"{s:>6.1f} {cout:>8} {fn:>14} {fp:>16}")

    seuil_opt, cout_opt = chercher_seuil_optimal(y, proba)
    cout_05, fn_05, fp_05 = facture(y, proba, 0.5)
    cout_1, fn_1, fp_1 = facture(y, proba, 1.0)

    print(f"\nFrontiere retenue (cout minimal) : {seuil_opt:.3f}")
    print(f"Facture a 0.5 (defaut de la bibliotheque) : {cout_05} credits "
          f"({fn_05} canulars rates, {fp_05} fausses alertes)")
    print(f"Facture avec la frontiere retenue          : {cout_opt} credits")
    print(f"Ecart : {cout_05 - cout_opt} credits economises en changeant la frontiere.")

    print(f"\nA titre de reference, ne jamais rien signaler (seuil=1.0) coute "
          f"{cout_1} credits ({fn_1} canulars rates, 0 fausse alerte).")
    print(f"La frontiere optimale ne fait mieux que 'ne rien signaler' que de "
          f"{cout_1 - cout_opt} credits : avec ce ratio de couts et ce modele, "
          f"la marge de manoeuvre reelle est etroite.")


if __name__ == "__main__":
    main()
