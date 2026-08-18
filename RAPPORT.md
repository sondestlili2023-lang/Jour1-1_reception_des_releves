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

## Le Conseil renvoie le rapport

Six annotations dans la marge, chacune sur la methode, pas sur les
resultats. Comme prevenu : les deux chiffres de la phase 4 vont surtout
baisser dans cette partie. Un chiffre honnete qui descend n'est pas un
recul, c'est le prix de la premiere version qui trichait sans qu'on le sache.

## Phase 7 -- plusieurs temoins, un seul evenement

**Un evenement = meme ville, meme etat, meme nuit** (colonne `datetime`,
au jour pres). Les 1 220 lignes sans datetime valide (phase 2) ne peuvent
partager de nuit avec personne : chacune forme son propre evenement a elle
seule plutot que d'etre regroupee au hasard.

- Evenements signales par plus d'un temoin : **2 383**
- Temoins pour le plus gros d'entre eux : **56** (Tinley Park, Illinois,
  la nuit du 31 octobre 2004 -- un survol reellement documente, pas un
  artefact du fichier)
- Avec la decoupe aleatoire des phases 4/5/6, **813 evenements** (soit
  **2 035 relevés**) se retrouvaient coupes en deux entre apprentissage
  et test -- le systeme "reconnaissait" une soiree qu'il avait deja lue,
  au lieu de la detecter.

Nouvelle decoupe : un `GroupShuffleSplit` sur la colonne evenement, qui
garantit qu'un evenement entier part du meme cote (verifie : 0 evenement
commun entre apprentissage et test apres la coupe). Les 56 temoins de
Tinley Park sont bien tous ensemble, cote test.

| | avant (decoupe aleatoire) | apres (decoupe par evenement) |
|---|---|---|
| Rappel | 56,2 | 52,8 |
| Precision | 1,3 | 1,3 |

Le rappel baisse : une partie de ce que le modele "attrapait" venait de
la ressemblance entre temoins d'un meme survol, pas d'une vraie
detection.

**Cas plus grossier** : 612 relevés partagent un commentaire identique,
mot pour mot, avec au moins un autre relevé. Ce ne sont pas des copies
d'un meme temoignage sur un meme evenement -- les dates et les villes
different a chaque fois (ex : "Fireball" apparait seul, tel quel, sur
12 relevés de villes et d'annees sans rapport). Ce sont des phrases
courtes et generiques ecrites independamment par des temoins sans lien
entre eux. On ne les fusionne pas et on ne les supprime pas : ce sont des
relevés distincts et legitimes. Le seul risque serait de les reutiliser
comme feature texte, ce qu'on ne fait plus depuis la phase 5.

## Phase 8 -- l'ordre des choses

Deux dates existent : `datetime` (quand le temoin a leve les yeux) et
`date_posted` (quand le Bureau a recu/publie le dossier). On coupe sur
**`date_posted`** : un temoignage de 1950 publie en 2004 arrive au Bureau
en 2004, pas en 1950 -- c'est l'ordre de `date_posted` qui correspond a
l'ordre reel dans lequel les dossiers atterrissent sur le bureau de
l'analyste.

- Date de coupure (80e percentile de `date_posted`) : **13 mai 2012**
- Apprentissage : **70 410 relevés** (avant la coupure)
- Test : **18 269 relevés** (a partir de la coupure)
- Proportion de canulars -- apprentissage : **0,94 %** / test : **0,77 %**

Les deux proportions ne sont **pas egales**, et ce n'est pas du bruit :
decoupees par annee de publication, elles racontent une histoire claire.

| Annee | 1998 | 1999-2004 | 2005 | 2006 | 2007 | 2008 | 2009-2011 | 2012-2014 |
|---|---|---|---|---|---|---|---|---|
| % canulars | 0,00 | 0,02-0,06 | 0,45 | 1,21 | 1,95 | 2,76 | 1,58-1,84 | 0,51-1,69 |

Avant 2005, le Bureau n'annotait quasiment jamais un dossier comme
canular. La pratique commence vers 2005 et devient ensuite irreguliere
d'une annee sur l'autre. Notre etiquette ne mesure donc pas seulement
"ceci est un canular" : elle mesure aussi "le Bureau a eu le temps et
l'habitude de le noter" -- une habitude qui a change avec le temps,
independamment des relevés eux-memes.

Rappel/precision, decoupe chronologique : **53,6 % / 1,2 %**.

## Phase 9 -- les cases vides

Les trois colonnes les plus trouees, et le taux de canulars selon
qu'elles le sont ou pas :

| Colonne | Trous | % canulars si trou | % canulars si rempli |
|---|---|---|---|
| `country` | 12 365 | 1,16 | 0,86 |
| `state` | 7 409 | 1,30 | 0,87 |
| `duration_hours_min` | 3 017 | 2,35 | 0,85 |

Dans les trois cas le taux de canulars est plus haut chez les relevés
troues (jusqu'a x2,8 pour `duration_hours_min`) : un trou porte de
l'information, ce n'est pas du bruit a boucher.

**Traitement retenu** : aucune ligne supprimee, aucun trou rempli par la
valeur la plus frequente. Pour les colonnes categorielles, le trou
devient sa propre categorie `manquant`, encodee comme une valeur a part
entiere (`cat__state_manquant`, `cat__country_manquant`,
`cat__shape_manquant` existent bien dans les 110 colonnes produites par
le pretraitement) : le modele voit explicitement "ce champ etait vide"
au lieu de se le faire recopier depuis une autre ligne. `duration_hours_min`
n'est pas encore une feature numerique (elle le devient en phase 11) ;
le meme principe -- indicateur de trou explicite plutot que remplissage
silencieux -- s'y appliquera.

## Phase 10 -- la chaine de traitement du Bureau

Bonne nouvelle : `entrainer_evaluer` (phase 4) n'a jamais calcule quoi
que ce soit en dehors d'un `Pipeline` scikit-learn, et
`pipeline.fit(X_train, ...)` n'apprend que sur `X_train`. Verification
avec la mediane de `latitude`, qui bouge selon qu'on la calcule sur tout
le fichier ou sur l'apprentissage seul :

- Mediane sur tout le fichier : **39,2333**
- Mediane sur l'apprentissage seul (celle retenue par l'imputeur) :
  **39,1611**

Les deux valeurs different : la fuite qu'on evite n'est pas theorique,
elle bougerait vraiment le chiffre si on la laissait faire.

Deuxieme point : la partie test de la decoupe chronologique contient
**140 canulars sur 18 269** relevés -- assez pour que rappel et precision
ne soient pas de la decoration.

- Proportion de canulars -- apprentissage : 0,94 % / test : 0,77 %
- Rappel / precision (chaine correcte) : **53,6 % / 1,2 %** -- identiques
  a la phase 8, puisque la chaine etait deja construite avec un `Pipeline`
  scikit-learn depuis la phase 4.

**Demonstration** : un relevé invente a la main (Paris, forme triangle,
45 secondes, 23h en juillet) traverse toute la chaine en un seul appel
`pipeline.predict(...)` et ressort avec une prediction (`CANULAR`,
probabilite 0,572) sans qu'aucune etape ne soit retapee a la main.

## Phase 11 -- combien de temps ca a dure

`duration_seconds` est la version que le service de transmission a
fabriquee a partir de `duration_hours_min` (ce que le temoin a ecrit a la
main) -- et il l'a parfois ratee. On reconstruit une duree utilisable en
repartant du texte quand le nombre est absent ou nul (parseur regex :
"5 minutes", "1-2 hrs", "1/2 hour", "a few seconds", "1:30"...).

- Lignes traitees : **88 679**, identique avant/apres, aucune supprimee
- Duree encore inutilisable apres traitement : **6 304 (7,1 %)**, dont
  **728** recuperees grace au texte du temoin la ou `duration_seconds`
  etait absent ou a 0
- Lignes ou les deux colonnes se contredisent (l'une dit au moins 5 fois
  l'autre) : **1 757**
- Duree mediane : **180 secondes (3 minutes)**
- Relevés annoncant plus d'une journee d'observation : **218**

Les trois durees les plus longues du fichier viennent du temoin
lui-meme : *"31 years"*, *"23000hrs"*, *"21 years"* -- le service de
transmission les a converties correctement, c'est le contenu qui est
invraisemblable (6 relevés au total depassent un an). On garde ces
lignes (aucune suppression demandee), mais on ne les laisse pas polluer
une moyenne : la mediane, utilisee ici, ne bouge pas d'une seconde qu'on
les garde ou non.

## Phase 12 -- la ville et l'heure

**Largeur du tableau** :
- Avant (ville et heure brutes, one-hot direct) : **19 692 colonnes**
- Apres (ville regroupee, heure cyclique) : **1 835 colonnes**

**Regle ville** : une ville garde sa propre colonne si elle apparait au
moins 10 fois dans toute la transmission (1 731 villes concernees),
sinon elle rejoint `autre`. **14 177 villes** (sur 22 018) n'apparaissent
qu'une seule fois dans toute la transmission -- rien a generaliser de ca.

**Heure cyclique** (`sin`, `cos` de l'heure sur 24h) :
- distance(23h, 0h) = **0,261**
- distance(23h, 20h) = **0,765**

23h ressort bien plus proche de 0h que de 20h, ce qui est vrai dans le
ciel et faux sur une echelle 0-23 brute.

**Shape** : 29 formes brutes. Fusion de deux paires qui designent
visiblement la meme chose sous deux orthographes (`changed`/`changing`,
`round`/`circle`), puis les formes avec moins de 5 occurrences rejoignent
`autre`. Il reste **23 formes** (`manquant` mis a part).

Les deux encodages (ville regroupee, forme nettoyee) sont appris
uniquement sur la partie apprentissage de la decoupe chronologique
(phase 8) : une ville ou une forme qui n'existe que dans le futur n'a pas
pu influencer le seuil de regroupement, et sera simplement ignoree par
l'encodeur (`handle_unknown='ignore'`) si elle apparait dans le test.

## Ce qui a bouge, phase par phase

| Phase | Chiffre | Avant | Apres |
|---|---|---|---|
| 7 -- evenements | Rappel / Precision | 56,2 % / 1,3 % | 52,8 % / 1,3 % |
| 8 -- chronologie | Rappel / Precision | 56,2 % / 1,3 % (decoupe par evenement) | 53,6 % / 1,2 % (decoupe chronologique) |
| 9 -- trous | Rien ne bouge dans le modele | categories `manquant` deja presentes dans le pretraitement | prouve : 3 colonnes `..._manquant` retrouvees dans les 110 colonnes generees |
| 10 -- pipeline | Rappel / Precision | 53,6 % / 1,2 % (deja correct depuis la phase 4) | 53,6 % / 1,2 % (verifie) |
| 11 -- duree | Relevés a duree utilisable | 81 647 (`duration_seconds` seul, valide et > 0) | 82 375 (+728 recuperes via le texte du temoin) |
| 12 -- ville/heure | Colonnes du tableau | 19 692 (ville brute) | 1 835 (ville regroupee + heure cyclique) |

Le rappel est passe de 99,4 % (phase 4, avec fuite) a 53,6 % (phase 10,
sans aucune triche methodologique) et la precision de 99,4 % a 1,2 %.
C'est le chiffre que le Bureau peut deposer devant le Conseil : plus bas,
mais gagne honnetement, sur des relevés que le systeme n'a ni memorises,
ni lus a l'avance.

## Note pour la suite

`analyse.py` enchaine les 12 phases (`phase1_ouverture.py` a
`phase12_ville_heure.py`) d'une traite, du telechargement de la
transmission au dernier chiffre, verifie sur un dossier vide. La sonde
continue d'emettre : les scripts re-telechargent la transmission si
`data/` est absent, donc une nouvelle transmission remplacera
automatiquement l'ancienne au prochain `rm -rf data && python3 analyse.py`.
