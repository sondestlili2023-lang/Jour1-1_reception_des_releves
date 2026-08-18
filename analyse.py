"""Point d'entree unique : relance tout le travail, du telechargement
au dernier chiffre, sur une machine neuve, sans intervention.

Chaque phase vit dans son propre fichier phaseN_*.py (executable seul
aussi). Ce script se contente de les enchainer dans l'ordre.
"""
import phase1_ouverture
import phase2_types
import phase3_regle_canular
import phase4_modele
import phase5_fuite
import phase6_stagiaire
import phase7_evenements
import phase8_chronologie
import phase9_trous
import phase10_pipeline
import phase11_duree
import phase12_ville_heure


def main():
    for phase in (
        phase1_ouverture,
        phase2_types,
        phase3_regle_canular,
        phase4_modele,
        phase5_fuite,
        phase6_stagiaire,
        phase7_evenements,
        phase8_chronologie,
        phase9_trous,
        phase10_pipeline,
        phase11_duree,
        phase12_ville_heure,
    ):
        phase.main()
        print()


if __name__ == "__main__":
    main()
