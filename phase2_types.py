"""Phase 2 : rien n'est du bon type.

Convertit chaque champ vers son vrai type (dates, nombres) sans
supprimer une seule ligne. Les valeurs qui resistent a la conversion
deviennent des valeurs manquantes (NaN / NaT), et sont comptees et
montrees plutot que silencieusement ignorees.
"""
import numpy as np
import pandas as pd

from commun import PHASE2_TYPES
from phase1_ouverture import load_or_run as charger_phase1


def convertir(df):
    df = df.copy()

    anomalies = {}

    # --- datetime : date + heure de l'observation, ecrite par le temoin ---
    dt = pd.to_datetime(df["datetime"], format="%m/%d/%Y %H:%M", errors="coerce")
    anomalies["datetime"] = {
        "n": int(dt.isna().sum()),
        "exemples": df.loc[dt.isna(), "datetime"].head(3).tolist(),
        "origine": "temoin",
        "explication": (
            "le temoin note parfois minuit '24:00', une heure qui n'existe pas "
            "au sens strict (23:59 ou 00:00 le lendemain seraient valides)."
        ),
    }
    df["datetime"] = dt

    # --- date_posted : date de publication, ajoutee par le Bureau ---
    dp = pd.to_datetime(df["date_posted"], format="%m/%d/%Y", errors="coerce")
    anomalies["date_posted"] = {
        "n": int(dp.isna().sum()),
        "exemples": df.loc[dp.isna(), "date_posted"].head(3).tolist(),
        "origine": "service de transmission",
        "explication": "champ propre : aucune valeur ne resiste a la conversion.",
    }
    df["date_posted"] = dp

    # --- duration_seconds : nombre ---
    dur = pd.to_numeric(df["duration_seconds"], errors="coerce")
    mauvaises_dur = df.loc[dur.isna(), "duration_seconds"]
    anomalies["duration_seconds"] = {
        "n": int(dur.isna().sum()),
        "exemples": mauvaises_dur.head(5).tolist(),
        "origine": "melange temoin/transmission",
        "explication": (
            "2 valeurs vides (le temoin n'a pas rempli le champ) et 3 valeurs "
            "portant un caractere ` en trop (ex: '2`'), un artefact d'encodage "
            "introduit par le service de transmission."
        ),
    }
    df["duration_seconds"] = dur

    # --- latitude / longitude : nombres, ajoutes par le geocodage de la sonde ---
    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    anomalies["latitude"] = {
        "n": int(lat.isna().sum()),
        "exemples": df.loc[lat.isna(), "latitude"].head(5).tolist(),
        "origine": "capteur (geocodage de la sonde)",
        "explication": (
            "une seule valeur sur 88 679, '33q.200088', contient une lettre "
            "parasite au milieu du nombre. Sans conversion valeur-par-valeur "
            "(errors='coerce'), cette unique ligne suffit a empecher toute la "
            "colonne latitude d'etre reconnue comme numerique."
        ),
    }
    df["latitude"] = lat
    anomalies["longitude"] = {
        "n": int(lon.isna().sum()),
        "exemples": [],
        "origine": "capteur (geocodage de la sonde)",
        "explication": "champ propre : aucune valeur ne resiste a la conversion.",
    }
    df["longitude"] = lon

    # --- categorielles vides : remplacees par NaN pour etre explicites ---
    for col in ["city", "state", "country", "shape", "duration_hours_min", "comments"]:
        vide = df[col] == ""
        if col == "country":
            anomalies["country"] = {
                "n": int(vide.sum()),
                "exemples": [],
                "origine": "service de transmission (geocodage incomplet)",
                "explication": (
                    "12 365 lignes n'ont pas de pays alors que 7 704 d'entre elles "
                    "ont pourtant un etat/province renseigne (ex: 'ca', 'tx', 'on') : "
                    "le service de transmission n'a pas su en deduire le pays."
                ),
            }
        df[col] = df[col].replace("", np.nan)

    df.to_pickle(PHASE2_TYPES)
    return df, anomalies


def load_or_run():
    if PHASE2_TYPES.exists():
        return pd.read_pickle(PHASE2_TYPES)
    df, _ = convertir(charger_phase1())
    return df


def main():
    df1 = charger_phase1()
    df2, anomalies = convertir(df1)

    print("=== Phase 2 : rien n'est du bon type ===")
    print(f"Lignes traitees : {len(df2)} (aucune supprimee)\n")

    for champ in ["datetime", "duration_seconds", "date_posted", "latitude", "longitude", "country"]:
        a = anomalies[champ]
        print(f"- {champ} : {a['n']} valeur(s) resistantes -- origine : {a['origine']}")
        if a["exemples"]:
            print(f"    exemples : {a['exemples']}")
        print(f"    {a['explication']}")


if __name__ == "__main__":
    main()
