"""Phase 8 : l'ordre des choses.

Le systeme jugera des relevés qui n'existent pas encore. La decoupe des
phases precedentes melangeait des observations de 1998 et de 2013 dans
la meme partie test : au moment de juger un relevé de 1998, le systeme
avait deja lu quinze ans de la suite de l'histoire. On decoupe dans
l'ordre du temps a la place.

Deux dates existent dans la transmission : `datetime` (quand le temoin a
regarde le ciel) et `date_posted` (quand le Bureau a recu/publie le
dossier). C'est la deuxieme qui compte ici : un relevé de 1950 publie en
2004 arrive au Bureau en 2004, pas en 1950. `date_posted` est l'ordre
dans lequel les dossiers arrivent vraiment sur le bureau de l'analyste ;
c'est elle qu'on ne doit pas laisser deborder dans le futur.
"""
import pandas as pd

from phase3_regle_canular import load_or_run as charger_phase3
from phase4_modele import entrainer_evaluer


def decouper_chronologiquement(df, proportion_test=0.2):
    cutoff = pd.Timestamp(df["date_posted"].quantile(1 - proportion_test).date())
    idx_train = df.index[df["date_posted"] < cutoff]
    idx_test = df.index[df["date_posted"] >= cutoff]
    return cutoff, idx_train, idx_test


def main():
    df = charger_phase3()
    cutoff, idx_train, idx_test = decouper_chronologiquement(df)

    hoax_train = df.loc[idx_train, "is_hoax"].mean() * 100
    hoax_test = df.loc[idx_test, "is_hoax"].mean() * 100

    print("=== Phase 8 : l'ordre des choses ===")
    print("Decoupe sur date_posted (date de reception/publication par le Bureau), pas sur")
    print("datetime : un temoignage de 1950 publie en 2004 arrive au Bureau en 2004, pas en 1950.")
    print(f"\nDate de coupure   : {cutoff.date()}")
    print(f"Apprentissage     : {len(idx_train)} releves (avant la coupure)")
    print(f"Test              : {len(idx_test)} releves (a partir de la coupure)")
    print(f"Proportion canulars -- apprentissage : {hoax_train:.2f} %   |   test : {hoax_test:.2f} %")

    print("\nProportion de canulars par annee de publication (date_posted) :")
    par_annee = df.assign(annee=df["date_posted"].dt.year).groupby("annee")["is_hoax"].mean() * 100
    print(par_annee.round(2).to_string())

    resultats = entrainer_evaluer(df, utiliser_texte=False, idx_train=idx_train, idx_test=idx_test)
    print(f"\nRappel    : {resultats['rappel']*100:.1f} / 100 canulars reellement presents sont attrapes")
    print(f"Precision : {resultats['precision']*100:.1f} / 100 releves signales le sont vraiment")

    print(
        f"\nLes deux proportions ne sont pas egales ({hoax_train:.2f} % contre {hoax_test:.2f} %) : "
        "avant 2005, le Bureau n'annotait quasiment jamais un dossier comme canular (0,00 % a 0,06 % "
        "de 1998 a 2004) ; la pratique commence vers 2005 et devient ensuite irreguliere d'une annee "
        "sur l'autre. Notre etiquette ne mesure donc pas seulement 'ceci est un canular', elle mesure "
        "aussi 'le Bureau a eu le temps et l'habitude de le noter' -- une habitude qui a change avec le "
        "temps, independamment des relevés eux-memes."
    )


if __name__ == "__main__":
    main()
