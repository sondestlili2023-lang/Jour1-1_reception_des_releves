"""Phase 3 : le Conseil veut trier les canulars.

Aucun champ ne dit si un releve est un canular : on en fabrique un a
partir de ce que le fichier contient deja. Le champ 'comments' melange
en realite deux auteurs : le temoignage brut, et des annotations que le
Bureau (NUFORC) glisse dans le meme champ entre doubles parentheses,
du type ((HOAX)) ou ((NUFORC Note: Possible hoax?? PD)).
"""
import pandas as pd

from commun import PHASE3_ETIQUETE
from phase2_types import load_or_run as charger_phase2

MOTIF_CANULAR = r"hoax"


def etiqueter(df):
    df = df.copy()
    texte = df["comments"].fillna("")
    df["is_hoax"] = texte.str.contains(MOTIF_CANULAR, case=False, regex=True)
    df.to_pickle(PHASE3_ETIQUETE)
    return df


def load_or_run():
    if PHASE3_ETIQUETE.exists():
        return pd.read_pickle(PHASE3_ETIQUETE)
    return etiqueter(charger_phase2())


def main():
    df = etiqueter(charger_phase2())
    texte = df["comments"].fillna("")

    n = int(df["is_hoax"].sum())
    proportion = n / len(df) * 100

    print("=== Phase 3 : le Conseil veut trier les canulars ===")
    print("Regle : un releve est marque canular si le mot 'hoax' apparait dans")
    print("son champ comments (annotations du Bureau du type ((HOAX)) ou ((NUFORC Note: ... hoax ...)).")
    print(f"\nReleves marques canulars : {n} sur {len(df)} ({proportion:.2f} %)")

    faux_positifs = texte[texte.str.contains(r"not a hoax|no hoax|isn.t a hoax|not hoax", case=False, regex=True)]
    incertains = texte[texte.str.contains(r"hoax\?\?", case=False, regex=True)]
    print(f"\nLimite 1 (faux positifs) : {len(faux_positifs)} temoins ecrivent eux-memes")
    print("'not a hoax' / 'no hoax' dans leur recit -- la regle les marque canular a tort.")
    print(f"   exemple : {faux_positifs.iloc[0][:120]!r}")

    print(f"\nLimite 2 (sur-classement) : {len(incertains)} des {n} cas viennent d'un simple")
    print("'hoax??' du Bureau -- une suspicion, pas une certitude -- que la regle traite")
    print("pourtant comme un canular confirme.")


if __name__ == "__main__":
    main()
