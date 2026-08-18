"""Phase 6 : le modele le plus bete du Bureau.

Le stagiaire propose de toujours repondre "ce n'est pas un canular".
On code ce systeme, on mesure son taux de bonnes reponses (exactitude),
et on le met a cote de celui du vrai modele (la version honnete de la
phase 5, sans la colonne qui trichait) pour trancher ce qui prouve
vraiment quelque chose au Conseil.
"""
from phase3_regle_canular import load_or_run as charger_phase3
from phase4_modele import COLONNES_CATEGORIELLES, COLONNES_NUMERIQUES, entrainer_evaluer


def main():
    df = charger_phase3()

    modele_honnete = entrainer_evaluer(
        df,
        colonnes_numeriques=COLONNES_NUMERIQUES,
        colonnes_categorielles=COLONNES_CATEGORIELLES,
        utiliser_texte=False,
    )

    # Le stagiaire ne s'entraine sur rien : il repond toujours "pas un canular".
    # Son exactitude sur le meme test se calcule directement : c'est la part
    # de releves du test qui ne sont effectivement pas des canulars.
    exactitude_stagiaire = (modele_honnete["n_test"] - modele_honnete["n_canulars_test"]) / modele_honnete["n_test"]

    print("=== Phase 6 : le modele le plus bete du Bureau ===")
    print(f"Exactitude du stagiaire ('jamais canular')      : {exactitude_stagiaire*100:.1f} %")
    print(f"Exactitude du vrai modele (phase 5, sans fuite) : {modele_honnete['exactitude']*100:.1f} %")
    print(f"Rappel du vrai modele                           : {modele_honnete['rappel']*100:.1f} %")
    print(f"Precision du vrai modele                        : {modele_honnete['precision']*100:.1f} %")

    print(
        "\nL'exactitude ne prouve rien ici : les canulars ne pesent que 0,9 % des "
        "releves, donc repondre toujours 'non' suffit deja a avoir raison plus de "
        "99 fois sur 100 sans avoir rien appris. La mesure qu'on defend devant le "
        "Conseil est le rappel et la precision sur la seule classe qui nous "
        "interesse (les canulars) : ce sont elles qui disent si le systeme repere "
        "vraiment quelque chose que le stagiaire, par construction, ne repere "
        "jamais."
    )


if __name__ == "__main__":
    main()
