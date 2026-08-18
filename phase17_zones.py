"""Phase 17 : l'angle mort du Bureau.

Quatre relevés sur cinq viennent des Etats-Unis : tout ce que le systeme
a appris vient essentiellement d'un seul pays. La moyenne globale est
ecrasee par la zone la plus lourde -- il faut regarder zone par zone
pour voir si le systeme marche vraiment partout, ou seulement chez lui.
"""
import numpy as np
from sklearn.metrics import precision_score, recall_score

import modele_final as mf
from phase13_facture import chercher_seuil_optimal

ZONES = ["us", "ca", "gb", "autre"]
SEUIL_DEFAUT = 0.5


def assigner_zone(pays):
    return pays.where(pays.isin(["us", "ca", "gb"]), "autre")


def resultats_par_zone(y, pred, zone):
    lignes = []
    for z in ZONES:
        masque = (zone == z).values
        lignes.append({
            "zone": z,
            "n": int(masque.sum()),
            "canulars": int(y[masque].sum()),
            "% canulars": round(y[masque].mean() * 100, 2),
            "rappel %": round(recall_score(y[masque], pred[masque], zero_division=0) * 100, 1),
            "precision %": round(precision_score(y[masque], pred[masque], zero_division=0) * 100, 2),
        })
    return lignes


def main():
    m = mf.charger()
    y, proba = m.y_test.values, m.proba_test
    zone = assigner_zone(m.df.loc[m.idx_test, "country"])

    print("=== Phase 17 : l'angle mort du Bureau ===")
    print(f"Repartition du test : us={int((zone=='us').sum())}, ca={int((zone=='ca').sum())}, "
          f"gb={int((zone=='gb').sum())}, autre={int((zone=='autre').sum())} "
          f"(sur {len(zone)} relevés)\n")

    pred = (proba >= SEUIL_DEFAUT).astype(int)
    lignes = resultats_par_zone(y, pred, zone)
    print(f"A la frontiere par defaut (0.5) :")
    print(f"{'zone':<8}{'n':>8}{'canulars':>10}{'% canulars':>12}{'rappel %':>10}{'precision %':>13}")
    for l in lignes:
        print(f"{l['zone']:<8}{l['n']:>8}{l['canulars']:>10}{l['% canulars']:>12}{l['rappel %']:>10}{l['precision %']:>13}")
    r_g = recall_score(y, pred, zero_division=0) * 100
    p_g = precision_score(y, pred, zero_division=0) * 100
    print(f"{'global':<8}{len(y):>8}{int(y.sum()):>10}{y.mean()*100:>12.2f}{r_g:>10.1f}{p_g:>13.2f}")

    print(
        "\nLe rappel n'est pas le meme partout : 47,7 % aux Etats-Unis (la zone qui pese le plus, "
        "donc proche du chiffre global), seulement 14,3 % au Canada, et jusqu'a 80 % au "
        "Royaume-Uni. La moyenne globale (50,7 %) ne raconte que l'histoire americaine."
    )
    print(
        "\nMais attention (phase 15) : le Canada ne compte que 7 canulars dans le test, le "
        "Royaume-Uni seulement 5. Un rappel de '14,3 %' ou de '80 %' sur un si petit effectif "
        "bouge de dizaines de points si on deplace un seul relevé -- ce ne sont pas des mesures "
        "fiables, ce sont des indications."
    )

    seuil_opt, _ = chercher_seuil_optimal(y, proba)
    pred_opt = (proba >= seuil_opt).astype(int)
    lignes_opt = resultats_par_zone(y, pred_opt, zone)
    print(f"\nA titre d'illustration, a la frontiere retenue en phase 13 ({seuil_opt:.3f}, tres "
          "conservatrice pour limiter les fausses alertes) :")
    for l in lignes_opt:
        print(f"  {l['zone']}: rappel {l['rappel %']}%, precision {l['precision %']}%")
    print(
        "Le seul canular attrape par tout le systeme a cette frontiere tombe dans 'autre' : les "
        "Etats-Unis, le Canada et le Royaume-Uni n'en attrapent aucun. Une frontiere unique et "
        "tres haute peut donc, en pratique, ne plus rien detecter du tout dans la zone qui pese "
        "le plus lourd -- exactement le trou que la moyenne globale ne montre pas."
    )

    print(
        "\nDecision : une seule frontiere pour toutes les zones, pas une par zone. Le Canada et "
        "le Royaume-Uni n'ont pas assez de canulars de test pour calibrer quoi que ce soit de "
        "fiable a leur echelle (phase 15) ; fragmenter la frontiere reviendrait a l'ajuster sur "
        "du bruit. On garde une frontiere globale, mais les zones hors Etats-Unis sont a "
        "surveiller qualitativement, pas a re-calibrer statistiquement pour l'instant."
    )


if __name__ == "__main__":
    main()
