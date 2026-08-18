# Rapport -- Bureau d'Analyse Terrestre

Transmission Klaxo-3 : `ufo-complete-geocoded-time-standardized.csv` (le fichier "complet",
88 875 lignes, 15 Mo -- pas le fichier "scrubbed" qui est deja nettoye).

## Phase 1 -- ouvrir la caisse

Le fichier n'a pas d'en-tete, on l'a chargee via le manifeste a 11 champs.

- Lignes dans le fichier : **88 875**
- Lignes chargees (11 champs, conformes au manifeste) : **88 679**
- Lignes mises a part : **196**

88 679 + 196 = 88 875, ca colle.

Les 196 lignes mises a part ont toutes 12 champs au lieu de 11, et dans les
196 cas la colonne `city` est vide. Exemple :

```
['10/1/2006 12:00', '', '', '', '', '0', '', '', '((EDITORIAL COMMENT ABOUT THE UFO PHENOMEN))  ufo+alien+reptiles', '10/30/2006', '0', '0']
```

Un champ vide en trop s'est glisse quelque part entre `datetime` et
`comments`. Vu que plusieurs des champs autour (city, state, country, shape,
duration_hours_min) sont vides eux aussi sur ces lignes, on ne peut pas
deviner sans ambiguite lequel des 12 champs est le "faux" -- donc au lieu
d'inventer une hypothese de decalage qui pourrait etre fausse, on les met de
cote plutot que de les forcer dans le mauvais champ.

## Phase 2 -- rien n'est du bon type

Conversion des 5 champs numeriques/dates, sur les 88 679 lignes chargees en
phase 1. Aucune ligne supprimee. Anomalies rencontrees :

| Champ | Valeurs resistantes | Origine | Explication |
|---|---|---|---|
| `datetime` | 1 220 | temoin | le temoin ecrit parfois "24:00" pour minuit, une heure qui n'existe pas formellement |
| `duration_seconds` | 5 | temoin + transmission | 2 vides (temoin n'a rien mis), 3 avec un caractere `` ` `` en trop (ex `2\`` ) -- artefact d'encodage cote transmission |
| `date_posted` | 0 | -- | champ propre |
| `latitude` | 1 | capteur (geocodage) | `33q.200088`, une lettre parasite au milieu du nombre |
| `longitude` | 0 | -- | champ propre |
| `country` | 12 365 | transmission (geocodage incomplet) | dont 7 704 lignes ont pourtant un `state` rempli -- le geocodage n'en a pas deduit le pays |

Le point signale dans l'enonce ("une colonne entiere peut etre inutilisable a
cause d'une seule valeur") est exactement le cas de `latitude` : une seule
valeur corrompue sur 88 679 (`33q.200088`) suffit a empecher `pd.to_numeric`
de reconnaitre toute la colonne si on ne convertit pas valeur par valeur avec
`errors='coerce'`.

## Phase 3 -- trier les canulars

Il n'existe pas de champ "canular" dans la transmission. En lisant les
commentaires on voit que le Bureau (NUFORC) glisse ses propres annotations
dans le meme champ `comments` que le temoignage, entre doubles parentheses :
`((HOAX))`, `((HOAX??))`, `((NUFORC Note: ... Possible hoax?? PD))`.

**Regle** : un releve est marque canular si le mot "hoax" apparait dans son
champ `comments`.

- Releves marques canulars : **802 sur 88 679 (0,90 %)**

Limites connues de la regle :
- **9 faux positifs** : des temoins ecrivent eux-memes "not a hoax" / "no
  hoax" dans leur recit pour se defendre -- la regle les marque canular
  alors que c'est l'inverse (ex : *"Hudson Valley-New Jersey-Large
  Sighting, No Hoax"*).
- **622 des 802 cas** viennent d'un simple `"hoax??"` du Bureau -- une
  suspicion, pas une confirmation -- que la regle traite pourtant comme un
  canular certain. La regle sur-classe.

## Phase 4 -- le premier verdict

Modele : regression logistique sur un melange de champs numeriques
(duree, latitude/longitude, heure, mois), categoriels (forme, etat, pays)
et texte (`comments` en TF-IDF). Separation 80/20 stratifiee, graine fixe
(42), evalue sur les 17 736 releves du test jamais vus a l'entrainement
(160 canulars dedans).

- Rappel : **99,4 / 100** canulars reellement presents sont attrapes
- Precision : **99,4 / 100** releves signales le sont vraiment

(spoiler : ces chiffres sont beaucoup trop beaux, voir phase 5)

## Phase 5 -- le Conseil ne vous croit pas

Tableau colonne par colonne, pour les colonnes utilisees par le modele de
phase 4 :

| Colonne | Qui l'ecrit | A quel moment | Connait deja le canular ? |
|---|---|---|---|
| `datetime` (heure, mois) | temoin | le soir de l'observation | non |
| `shape` | temoin | le soir de l'observation | non |
| `duration_seconds` | temoin | le soir de l'observation | non |
| `state` / `country` | sonde (geocodage automatique) | a la reception du signalement | non |
| `latitude` / `longitude` | sonde (geocodage automatique) | a la reception du signalement | non |
| `comments` | temoin **puis** employe du Bureau, dans le meme champ | le soir meme, **et** des semaines plus tard a la relecture | **oui** -- l'employe y ecrit litteralement le mot qui sert a fabriquer l'etiquette |

Seule `comments` repond "oui" a la quatrieme case. On la retire et on
reentraine avec les memes reglages (meme graine, meme test) :

| | avant (avec `comments`) | apres (sans `comments`) |
|---|---|---|
| Rappel | 99,4 | 56,2 |
| Precision | 99,4 | 1,3 |

L'ecart ne vient pas d'un modele "devenu moins bon". La colonne `comments`
contient, ecrit noir sur blanc par le Bureau des semaines apres les faits, le
mot "hoax" qui a lui-meme servi a fabriquer l'etiquette en phase 3 : le
modele "avant" ne devine rien, il relit une reponse deja presente dans son
entree. Une fois `comments` retire, il ne reste que des champs connus au
moment du signalement, et devant la vraie question ("ce releve est-il un
canular ?") ils ne suffisent presque pas -- ce qui est la reponse honnete a
la question du Conseil.

## Phase 6 -- le modele le plus bete du Bureau

Systeme du stagiaire : repondre "pas un canular", toujours.

- Exactitude du stagiaire : **99,1 %**
- Exactitude du vrai modele (phase 5, sans fuite) : **61,0 %**
- Rappel / precision du vrai modele : **56,2 % / 1,3 %**

Le stagiaire bat le vrai modele sur l'exactitude, et ce n'est pas une
erreur de calcul : les canulars ne pesent que 0,9 % des releves, donc
repondre "non" tout le temps est deja juste plus de 99 fois sur 100 sans
avoir rien appris sur rien. C'est une mesure qui ne recompense jamais la
detection de la classe rare -- exactement celle qui interesse le Bureau.

**Mesure defendue devant le Conseil : le rappel et la precision sur la
classe "canular"**, pas l'exactitude. Ce sont les seules qui disent si le
systeme repere vraiment des canulars, chose que le stagiaire, par
construction, ne fait jamais -- meme s'il "a raison" plus souvent que nous.

## Note pour la suite

`analyse.py` enchaine les 6 phases (`phase1_ouverture.py` a
`phase6_stagiaire.py`) d'une traite, du telechargement de la transmission au
dernier chiffre, verifie sur un dossier vide. La sonde continue d'emettre :
les scripts re-telechargent la transmission si `data/` est absent, donc une
nouvelle transmission remplacera automatiquement l'ancienne au prochain
`rm -rf data && python3 analyse.py`.
