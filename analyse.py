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


def main():
    for phase in (
        phase1_ouverture,
        phase2_types,
        phase3_regle_canular,
        phase4_modele,
        phase5_fuite,
        phase6_stagiaire,
    ):
        phase.main()
        print()


if __name__ == "__main__":
    main()
