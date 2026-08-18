"""Phase 5 : le Conseil ne vous croit pas.

Un signalement qui arrive a l'instant n'a pas encore ete relu par le
Bureau. Toute colonne dont la valeur depend d'une relecture posterieure
(faite en connaissant deja le statut canular) n'a pas le droit de nourrir
un modele cense repondre "maintenant". On construit le tableau colonne
par colonne, on retire celles qui trichent, et on recompare les chiffres
de la phase 4 avant/apres.
"""
from phase3_regle_canular import load_or_run as charger_phase3
from phase4_modele import COLONNES_CATEGORIELLES, COLONNES_NUMERIQUES, entrainer_evaluer

# Qui ecrit chaque colonne utilisee par le modele, a quel moment, et est-ce
# que cette personne connaissait deja le statut canular en l'ecrivant.
# (jugement d'analyste : ce n'est pas quelque chose que les donnees disent
# elles-memes, personne au Bureau n'a code cette information.)
TABLEAU_FUITE = [
    ("datetime (-> heure, mois)", "temoin", "le soir de l'observation", "non"),
    ("shape", "temoin", "le soir de l'observation", "non"),
    ("duration_seconds", "temoin", "le soir de l'observation", "non"),
    ("state / country", "sonde (geocodage automatique)", "a la reception du signalement", "non"),
    ("latitude / longitude", "sonde (geocodage automatique)", "a la reception du signalement", "non"),
    ("comments", "temoin PUIS employe du Bureau (meme champ)", "le soir meme, ET des semaines plus tard a la relecture", "OUI -- l'employe y ecrit litteralement le mot qui sert a fabriquer l'etiquette"),
]


def afficher_tableau():
    print("Colonne                     | Qui ecrit                              | Quand                         | Connait deja le canular ?")
    print("-" * 130)
    for col, qui, quand, sait in TABLEAU_FUITE:
        print(f"{col:<28} | {qui:<38} | {quand:<29} | {sait}")


def main():
    df = charger_phase3()

    print("=== Phase 5 : le Conseil ne vous croit pas ===\n")
    afficher_tableau()

    avant = entrainer_evaluer(df, utiliser_texte=True)
    apres = entrainer_evaluer(
        df,
        colonnes_numeriques=COLONNES_NUMERIQUES,
        colonnes_categorielles=COLONNES_CATEGORIELLES,
        utiliser_texte=False,
    )

    print("\n                 avant (avec comments)   apres (sans comments)")
    print(f"Rappel           {avant['rappel']*100:>18.1f}   {apres['rappel']*100:>19.1f}")
    print(f"Precision        {avant['precision']*100:>18.1f}   {apres['precision']*100:>19.1f}")

    print(
        "\nL'ecart ne vient pas d'un modele qui 'devient moins bon' : la colonne "
        "comments contient, ecrit noir sur blanc par le Bureau, le mot qui a servi "
        "a fabriquer l'etiquette is_hoax en phase 3. Le modele 'avant' ne predit "
        "rien, il relit une reponse deja ecrite dans sa propre entree. Une fois "
        "comments retire, il ne reste que des champs connus au moment du "
        "signalement, et le modele doit deviner un canular pour de vrai -- ce que "
        "les champs structurels (forme, duree, position) permettent tres mal."
    )


if __name__ == "__main__":
    main()
