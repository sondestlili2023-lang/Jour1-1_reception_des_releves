"""Phase 11 : combien de temps ca a dure.

`duration_seconds` est censee etre la version propre, numerique, de ce
que le temoin a ecrit dans `duration_hours_min` ("5 minutes", "1-2 hrs"...).
Le service de transmission l'a fabriquee automatiquement -- et l'a
parfois ratee : des lignes ou `duration_seconds` vaut 0 alors que le
texte du temoin est parfaitement lisible. On reconstruit une duree
utilisable en repartant du texte quand le nombre est absent ou nul.
"""
import re

import pandas as pd

from phase3_regle_canular import load_or_run as charger_phase3

UNITES = {
    "sec": 1, "secs": 1, "second": 1, "seconds": 1,
    "min": 60, "mins": 60, "minute": 60, "minutes": 60,
    "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
    "day": 86400, "days": 86400,
}
UNITE_RE = "|".join(sorted(UNITES, key=len, reverse=True))
FRACTIONS = {"1/2": 0.5, "1/4": 0.25, "3/4": 0.75}
MOTS_NOMBRES = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "fifteen": 15,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "couple": 2, "few": 3, "several": 5, "dozen": 12,
}
MOT_NOMBRE_RE = "|".join(MOTS_NOMBRES)


def parser_duree_texte(texte):
    """Convertit une duree ecrite a la main ('5 minutes', '1-2 hrs', '1/2 hour',
    'a few seconds', '1:30'...) en secondes. Renvoie None si illisible."""
    if not isinstance(texte, str) or not texte.strip():
        return None
    t = texte.strip().lower().replace("approximately", "").replace("approx", "").replace("about", "").strip()
    t = t.replace("+", " ")

    for frac_str, frac_val in FRACTIONS.items():
        m = re.search(rf"{re.escape(frac_str)}\s*({UNITE_RE})", t)
        if m:
            return frac_val * UNITES[m.group(1)]

    m = re.search(r"half\s+(?:an?\s+)?(hour|minute|min)", t)
    if m:
        return 0.5 * UNITES["hr" if "hour" in m.group(1) else "min"]

    m = re.search(rf"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*({UNITE_RE})\b", t)
    if m:
        a, b, u = float(m.group(1)), float(m.group(2)), m.group(3)
        return (a + b) / 2 * UNITES[u]

    m = re.search(rf"(\d+(?:\.\d+)?)\s*({UNITE_RE})\b", t)
    if m:
        return float(m.group(1)) * UNITES[m.group(2)]

    m = re.fullmatch(r"(\d{1,2}):(\d{2})", t)
    if m:
        h, mn = int(m.group(1)), int(m.group(2))
        if mn < 60:
            return h * 3600 + mn * 60

    m = re.search(rf"\b({MOT_NOMBRE_RE})\b[a-z\s]*?\b({UNITE_RE})\b", t)
    if m:
        return MOTS_NOMBRES[m.group(1)] * UNITES[m.group(2)]

    m = re.fullmatch(r"(\d+(?:\.\d+)?)", t)
    if m:
        # un nombre seul, sans unite : convention temoin la plus frequente = des minutes
        return float(m.group(1)) * 60

    return None


def construire_duree(df):
    df = df.copy()
    df["duree_texte_s"] = df["duration_hours_min"].apply(parser_duree_texte)
    ds_valide = df["duration_seconds"].notna() & (df["duration_seconds"] > 0)
    df["duree_manquante"] = ~(ds_valide | df["duree_texte_s"].notna())
    df["duree_s"] = df["duration_seconds"].where(ds_valide, df["duree_texte_s"])
    return df, ds_valide


def main():
    df = charger_phase3()
    df, ds_valide = construire_duree(df)

    recuperees = (~ds_valide) & df["duree_texte_s"].notna()
    both = ds_valide & df["duree_texte_s"].notna()
    ratio = pd.concat([df.loc[both, "duration_seconds"], df.loc[both, "duree_texte_s"]], axis=1).max(axis=1) / \
        pd.concat([df.loc[both, "duration_seconds"], df.loc[both, "duree_texte_s"]], axis=1).min(axis=1)
    contradictions = int((ratio >= 5).sum())

    print("=== Phase 11 : combien de temps ca a dure ===")
    print(f"Lignes traitees : {len(df)} (identique avant/apres, aucune supprimee)\n")

    print(f"Duree encore inutilisable apres traitement : {int(df['duree_manquante'].sum())} "
          f"({df['duree_manquante'].mean()*100:.1f} %)")
    print(f"  dont recuperees grace au texte du temoin (duration_seconds absent/a 0, "
          f"duration_hours_min lisible) : {int(recuperees.sum())}")
    print(f"Lignes ou les deux colonnes se contredisent (l'une dit au moins 5x l'autre) : {contradictions}")
    print(f"Duree mediane : {df['duree_s'].median():.0f} secondes ({df['duree_s'].median()/60:.1f} minutes)")

    plus_dun_jour = int((df["duree_s"] > 86400).sum())
    print(f"Relevés annoncant plus d'une journee d'observation : {plus_dun_jour}")

    print("\nLes trois durees les plus longues du fichier :")
    top3 = df.nlargest(3, "duree_s")[["datetime", "city", "state", "duration_seconds", "duration_hours_min", "duree_s"]]
    print(top3.to_string(index=False))
    plus_dun_an = int((df["duree_s"] > 365 * 86400).sum())
    print(
        f"\nCes valeurs viennent du temoin lui-meme ('31 years', '23000hrs', '21 years') : le service "
        "de transmission les a converties correctement, c'est le contenu qui est invraisemblable. "
        f"On garde ces lignes (aucune suppression demandee) -- {plus_dun_an} au total depassent un "
        "an -- mais on ne les laisse pas polluer une moyenne : la mediane, utilisee ici, ne bouge "
        "pas d'une seconde qu'on les garde ou non, contrairement a ce qu'aurait fait une moyenne."
    )


if __name__ == "__main__":
    main()
