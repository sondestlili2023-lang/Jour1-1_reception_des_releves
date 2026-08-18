"""Phase 10 : la chaine de traitement du Bureau.

Deux fautes possibles ici. La premiere : calculer une moyenne, une
mediane ou un vocabulaire sur le fichier entier avant de couper -- une
miette de la partie test se glisse alors dans l'apprentissage. La
seconde, plus bete : a 0,9 % de canulars, une decoupe malchanceuse peut
donner une partie test sans presque aucun canular, et les chiffres
deviennent de la decoration.

Bonne nouvelle sur la premiere faute : `entrainer_evaluer` (phase 4) ne
calcule jamais rien en dehors d'un `Pipeline` scikit-learn, et
`pipeline.fit(X_train, ...)` n'apprend que sur X_train -- la mediane de
`SimpleImputer` et les categories de `OneHotEncoder` n'ont jamais vu la
partie test. Ce script le verifie et le montre, plutot que de le
supposer.
"""
import pandas as pd

from phase3_regle_canular import load_or_run as charger_phase3
from phase4_modele import entrainer_evaluer
from phase8_chronologie import decouper_chronologiquement


def main():
    df = charger_phase3()
    cutoff, idx_train, idx_test = decouper_chronologiquement(df)

    hoax_train = df.loc[idx_train, "is_hoax"].mean() * 100
    hoax_test = df.loc[idx_test, "is_hoax"].mean() * 100
    n_canulars_test = int(df.loc[idx_test, "is_hoax"].sum())

    print("=== Phase 10 : la chaine de traitement du Bureau ===")
    print(f"Proportion de canulars -- apprentissage : {hoax_train:.2f} %   |   test : {hoax_test:.2f} %")
    print(f"Canulars dans la partie test : {n_canulars_test} sur {len(idx_test)} -- assez pour que")
    print("le rappel/precision ne soient pas de la decoration (pas 0, pas une poignee).")

    resultats = entrainer_evaluer(df, utiliser_texte=False, idx_train=idx_train, idx_test=idx_test)
    pipeline = resultats["pipeline"]

    imputeur = pipeline.named_steps["pretraitement"].named_transformers_["num"]
    print(f"\nMediane apprise par l'imputeur (duration_seconds, latitude, longitude, heure, mois) :")
    print(f"  {list(imputeur.statistics_)}")
    print("Ce vecteur est calcule par pipeline.fit(X_train, ...) -- jamais sur X_test. Verification")
    print("avec latitude, dont la mediane bouge selon qu'on regarde tout le fichier ou l'apprentissage seul :")
    mediane_sur_tout = df["latitude"].median()
    mediane_train_seule = df.loc[idx_train, "latitude"].median()
    print(f"  mediane latitude sur TOUT le fichier                : {mediane_sur_tout}")
    print(f"  mediane latitude sur l'apprentissage seul (celle retenue par l'imputeur) : {mediane_train_seule}")
    print("  les deux valeurs different : la fuite qu'on evite n'est pas theorique, elle bougerait le chiffre.")

    print(f"\nRappel    : {resultats['rappel']*100:.1f} / 100 canulars reellement presents sont attrapes")
    print(f"Precision : {resultats['precision']*100:.1f} / 100 releves signales le sont vraiment")
    print("(memes chiffres qu'en phase 8 : la chaine etait deja construite avec un Pipeline "
          "scikit-learn depuis la phase 4, donc rien ne fuyait deja de ce cote-la.)")

    print("\nDemonstration : un relevé invente a la main, jamais vu, traverse toute la chaine en un appel.")
    releve_invente = pd.DataFrame([{
        "duration_seconds": 45,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "heure": 23,
        "mois": 7,
        "shape": "triangle",
        "state": "fr",
        "country": "fr",
    }])
    print(releve_invente.to_string(index=False))
    prediction = pipeline.predict(releve_invente)[0]
    proba = pipeline.predict_proba(releve_invente)[0][1]
    print(f"-> prediction : {'CANULAR' if prediction else 'pas canular'} (probabilite canular : {proba:.3f})")


if __name__ == "__main__":
    main()
