---
title: "QualCoder : une mise à jour majeure pour l'analyse qualitative"
date: 2026-08-XX
---

Nous sommes ravis de vous présenter la dernière version de QualCoder, une mise à jour riche en fonctionnalités qui révolutionne votre façon de travailler avec les données qualitatives. Que vous soyez chercheur, analyste ou professionnel des données, cette version apporte des améliorations significatives en matière de hiérarchie des codes, d’intégration de l’IA, de gestion des fichiers et de visualisation.

Cette version marque également une évolution importante dans la structure et l’analyse des données. Vous trouverez ci-dessous un aperçu détaillé des principales nouvelles fonctionnalités.


## Prise en charge linguistique améliorée

Afin de garantir une expérience utilisateur de la plus haute qualité, QualCoder se concentre désormais sur quatre langues principales : l’anglais, l’allemand, le français et l’espagnol. Ces langues bénéficient de révisions humaines régulières et de mises à jour fréquentes afin d’assurer des traductions précises et naturelles.

D’autres langues restent disponibles dans le dossier « Autres langues », mais elles peuvent ne pas être aussi à jour ou ne pas avoir fait l’objet d’une révision humaine. Vous pouvez contribuer à améliorer les traductions en espéranto, basque, farsi, créole haïtien, italien, japonais, portugais, roumain, suédois et mandarin, ou suggérer votre propre langue. Si vous souhaitez contribuer à la traduction de votre langue, veuillez nous contacter.


## Changements structurels : des codes mieux organisés

### Hiérarchie des codes améliorée

L’une des principales nouveautés de cette version est la possibilité de créer des sous-codes. Auparavant, QualCoder vous permettait uniquement de structurer vos données en catégories. Désormais, vous pouvez également créer des hiérarchies de codes, ce qui offre une granularité bien plus fine pour organiser vos analyses.


## Sauvegardes : plus simples et plus accessibles

Les sauvegardes de projet sont désormais stockées dans le même dossier que le projet lui-même. Tout est regroupé au même endroit, ce qui simplifie la gestion et la restauration de votre travail.


## Améliorations de l’IA

L’intégration de l’intelligence artificielle dans QualCoder a été entièrement repensée. Le chat IA n’est plus seulement un assistant conversationnel ; il est devenu un collaborateur actif capable d’interagir avec vos données. Veuillez noter que l’IA est facultative dans QualCoder.

Nous avons mis en place trois niveaux d’accès afin de protéger les données contre toute modification accidentelle et d’offrir une flexibilité adaptée à vos besoins et à votre niveau de confiance :

| Niveau d’accès | Autorisations | Cas d’utilisation |
|--------------|-------------|----------|
| Lecture seule | Accès complet à l’arborescence des codes, aux mémos, aux codages et aux données empiriques via divers outils de recherche (texte uniquement). | Analyse et exploration des données sans risque de modification. |
| Mode bac à sable | Accès en lecture + écriture limitée : possibilité de créer de nouveaux codes et codages, mais impossibilité de modifier ou de supprimer ceux qui existent déjà. | Tests et expérimentations en toute sécurité. |
| Accès complet | Toutes les autorisations, y compris la modification des codes, codages, attributs et cas existants. Les opérations destructives nécessitent une confirmation explicite de l’utilisateur. | Travail avancé avec validation humaine pour les actions critiques. |


## Menus et onglets : une interface remaniée

L’interface de QualCoder a été restructurée afin d’améliorer l’ergonomie et la lisibilité.

Un nouvel onglet « Analyse » a été ajouté, centralisant toutes les fonctionnalités d’analyse des données. Les éléments de menu ont été répartis entre les onglets « Analyse » et « Rapports » pour une meilleure organisation logique. Les onglets « Gestion », « Codage » et « Rapports » comprennent désormais des explications détaillées sur leurs rôles respectifs, accessibles via des infobulles ou des descriptions intégrées.


## Journaux : exportation et fonctionnalités étendues

Les journaux (journaux de bord, notes, etc.) bénéficient de plusieurs améliorations :

- Exportation au format ODT : vos journaux peuvent désormais être exportés au format OpenDocument Text, un format universel et modifiable, ouvrable avec LibreOffice Writer, Microsoft Word ou tout autre logiciel similaire.
- Conversion en fichier de codage : cliquez avec le bouton droit sur un journal pour le convertir en fichier codable au sein de votre projet QualCoder.
- Ouverture directe d’une URL : si votre journal contient des liens (commençant par http, https ou www), cliquez avec le bouton droit sur l’URL pour l’ouvrir directement dans votre navigateur.


## Gestion des fichiers : import et manipulation avancés

Un menu contextuel propose les options « Supprimer » et « Exporter » accessibles par un clic droit. Dans la colonne « Nom du fichier », appuyer sur la touche Suppr supprime les fichiers sélectionnés.

### Import d’enquêtes

Un bouton « Importer une enquête » permet désormais d’importer des données à partir de fichiers Excel (XLSX) ou CSV. La sélection de plusieurs lignes vous permet de choisir plusieurs lignes à la fois pour les importer en tant qu’attributs ou pour un traitement qualitatif.

### Import de PDF avec surlignages et soulignements

Vous pouvez désormais importer des PDF annotés et coder automatiquement les segments annotés. Deux types d’annotations sont détectés : les surlignages et les soulignements. QualCoder vous demande si vous souhaitez les coder, puis crée une catégorie « Surlignages PDF », une catégorie « Soulignements PDF », ou les deux, en fonction du contenu des fichiers. Un code est créé par couleur et par type de surlignage (par exemple « Surlignage jaune » ou « Soulignement bleu »), les couleurs des annotations étant adaptées pour correspondre au mieux à la palette de QualCoder. Les commentaires écrits sur un surlignage ou un soulignement deviennent la note du segment codé résultant, tandis que les autres annotations contenant du texte (notes autocollantes et similaires) sont regroupées dans la note du fichier, avec leur numéro de page.

### Import LaTeX

Les fichiers LaTeX peuvent désormais être importés et convertis en texte brut lisible. Notez que les présentations complexes ou les fichiers utilisant des commandes telles que |input| ou |include| peuvent ne pas s’importer parfaitement.


## Gestion des références : pièces jointes et Zotero

La gestion des références a été étendue avec deux voies d’import. Les fichiers RIS peuvent désormais être importés avec leurs documents joints : lorsque l’entrée pointe vers un PDF ou un EPUB, le fichier est importé dans le projet et lié à sa référence, de sorte que le document et sa notice bibliographique vont de pair.

Les références peuvent également être importées directement depuis une installation locale de Zotero (version 7 ou plus récente) via son API locale, avec leurs pièces jointes au format PDF, sans aucun compte ni clé. Ces deux méthodes partagent la même boîte de dialogue de prévisualisation, qui répertorie les références trouvées, signale celles déjà présentes dans le projet ainsi que leurs pièces jointes en double, et vous permet de choisir ce que vous souhaitez importer et si vous souhaitez inclure les pièces jointes.


## Arbre de codes : plus intuitif et plus puissant

L’arbre de codes, présent dans tous les écrans de codage, a été considérablement amélioré :

- Des sous-menus ont été ajoutés pour les options Modifier (codes ou catégories sélectionnés), Filtrer et Trier.
- Un indicateur visuel de filtrage (icône de filtre) apparaît lorsque l’arbre est filtré (par exemple, via « Afficher les codes similaires » ou « Afficher les codes par couleur »).
- Un filtre textuel par nom de code a été ajouté sous l’arborescence.
- Une option « Déplacer la catégorie » vous permet de réorganiser votre arborescence.
- La fonctionnalité glisser-déposer a été améliorée : vous pouvez désormais déplacer un élément vers le haut ou vers le bas de l’arborescence visible, et celle-ci défilera automatiquement.
- Un menu dans l’en-tête de l’arborescence permet de choisir entre un redimensionnement automatique ou manuel des colonnes.


## Codage de texte : personnalisation avancée et exportation

Le codage de texte a été enrichi de nombreuses fonctionnalités pour une expérience plus fluide et plus flexible :

- Personnalisez la police et la taille du texte de votre document.
- Redimensionnez les étiquettes de code à l’aide des poignées de redimensionnement.
- Basculez entre différents styles de mise en évidence : surlignage, soulignement ou rayures verticales aux marges pour les codes.
- Exportez les documents codés au format ODF (OpenDocument Format), avec des surlignages par code couleur, les commentaires associés, ou sous forme de rapport analytique.

Des raccourcis clavier ont été ajoutés : par exemple, la touche C pour ajouter une nouvelle catégorie. Le mode d’édition de texte comprend désormais une barre de recherche pour faciliter la navigation.

!!! info
    Documents complets au lieu de segments

Les documents texte se chargent désormais toujours dans leur intégralité. Le paramètre « Taille des segments de texte codé » (50 000 ou 30 000 caractères) et la navigation « caractères suivants / précédents » ont été supprimés. Le chargement par blocs permettait d’économiser de la mémoire sur les fichiers très volumineux, mais il présentait des risques pour les données : la modification d’un fichier alors qu’un bloc partiel était chargé pouvait n’enregistrer que la partie visible et écraser le reste du document ; la navigation entre les blocs après une modification pouvait provoquer un plantage ; et le retour au premier bloc pouvait masquer le début du texte. Avec le chargement intégral, les positions des caractères et les encodages restent toujours cohérents.


## Codage des PDF : une expérience révolutionnaire

Le codage des PDF a été considérablement amélioré. La présentation et la manipulation des PDF offrent désormais une interface plus fluide et plus intuitive. Vous pouvez coder directement sur la page PDF, qu’il s’agisse de zones de texte ou d’images. L’analyse de texte assistée par IA peut être appliquée directement depuis la fenêtre de codage des PDF.

Une méthode de refactorisation a été ajoutée pour les projets QualCoder existants : le texte est réextrait et les codages existants sont remappés selon la nouvelle méthode d’extraction. Les codages qui ne peuvent pas être remappés sont consignés dans les journaux en tant que « codes perdus » pour que vous puissiez les examiner.

L’exportation des surlignages PDF génère une copie du PDF d’origine avec les codages intégrés sous forme d’annotations natives : le texte codé apparaît en surlignage et les zones codées sous forme de rectangles, chacun dans la couleur du code et comportant le nom du code, sa note et le nom du codeur. Cela permet d’ouvrir et de consulter le document codé dans n’importe quel lecteur PDF standard. Une fonctionnalité de rapport ODT permet également d’exporter un rapport de codage au format OpenDocument Text (ODT), répertoriant les segments codés avec leurs codes (texte et images).


## Codage d’images : redimensionnement facile

Les zones codées sur les images peuvent désormais être redimensionnées via un menu contextuel accessible par un clic droit ou à l’aide de poignées de redimensionnement.


## Codage audio/vidéo : amélioration des signets et de la navigation

La fonctionnalité de signets vous permet de revenir à la position dans le média et le texte dans les fenêtres « Code A/V » et « Affichage A/V » (accessibles depuis « Gérer les fichiers ») après avoir défini un signet. Des raccourcis clavier sont disponibles : B pour créer un signet, et Maj + B pour accéder à un signet.


## Rapport de cooccurrence : visualisation et exportation

Les graphiques de proximité vous permettent de visualiser les relations entre les codes. Deux graphiques peuvent être exportés sous forme d’images haute résolution : le graphique de cooccurrence, où l’épaisseur de chaque ligne indique la fréquence à laquelle deux codes ont été codés ensemble, et le graphique des grappes de communautés, qui regroupe les codes en grappes colorées en fonction de leurs liens les plus forts. Un clic droit sur chaque bouton permet de définir la taille de la police et de choisir si la couleur s’applique aux nœuds ou aux étiquettes. La matrice elle-même peut être exportée vers Excel, et le réseau peut être exporté au format GraphML, compatible avec Gephi, un puissant outil d’analyse de réseaux.

!!! Remarque
    Note technique : comment sont calculés les graphiques de cooccurrence
    La cooccurrence est comptabilisée fichier par fichier, entre des segments correspondant à deux codes différents. Dans le texte, deux codages cooccur lorsqu’ils couvrent exactement le même passage, lorsque l’un     contient l’autre, ou lorsqu’ils se chevauchent partiellement. Dans les images et les zones PDF, ces trois     mêmes cas sont déterminés à partir des rectangles, au sein d’un même fichier et, pour les PDF, d’une même     page. La valeur de chaque paire correspond à la somme des deux directions de la matrice.

    Les graphes sont construits avec networkx et tracés avec matplotlib. Les nœuds correspondent aux codes visibles, les arêtes aux paires dont le nombre de cooccurrences est supérieur à zéro, et le poids de chaque arête correspond à ce nombre, l’épaisseur de la ligne étant proportionnelle à la valeur la plus élevée. Le graphe de cooccurrence positionne les nœuds selon une disposition de type « spring » (Fruchterman-Reingold). Le graphe de clusters détecte d’abord les communautés à l’aide de la méthode de Louvain (avec la modularité gloutonne comme solution de repli), appliquée au sous-réseau des arêtes dont le poids est égal ou supérieur à la moyenne, de sorte que seules les relations les plus fortes définissent les groupes ; les nœuds sont ensuite positionnés selon la méthode de Kamada-Kawai en utilisant l’inverse du nombre d’occurrences comme distance, en recourant à une disposition « spring » lorsque le réseau n’est pas connecté. Les exportations vers Gephi et GraphML contiennent ces mêmes nœuds et poids.


## Graphe : plus de flexibilité et de contrôle

Graphe offre davantage de flexibilité et de contrôle :

- La manipulation des objets a été améliorée, ce qui vous permet de déplacer, redimensionner et organiser les nœuds plus facilement.
- Exportez des cartes mentales dans un format compatible avec draw.io pour les intégrer à d’autres outils de visualisation.
- Développez ou réduisez des parties du graphe (catégories) pour une vue plus claire.
- Une nouvelle boîte de dialogue permet d’ajouter des segments codés à votre graphe.
- Plusieurs options d’organisation du graphe sont disponibles, avec différents choix de mise en page : radiale, verticale ou horizontale.
- La personnalisation des polices et des couleurs offre davantage d’options pour adapter l’apparence de votre graphe.
- Une mini-carte défilable vous aide à naviguer plus facilement dans les grands graphes.
- Choisissez parmi différents styles de nœuds (rectangle, ovale, etc.).
- Utilisez la sélection multiple pour manipuler plusieurs éléments à la fois.

### Modèles de graphiques automatisés

Six modèles de graphiques peuvent être générés automatiquement au lieu de construire le graphique à la main : hiérarchie des catégories, hiérarchie des fichiers, comparaison de fichiers (deux fichiers), hiérarchie des cas, comparaison de cas (deux cas) et réseau de cooccurrence. Dans les modèles comparatifs, les lignes de connexion indiquent également la fréquence de chaque code ou catégorie dans ce cas ou ce fichier.


### Lignes de relation

Les lignes reliant les nœuds peuvent désormais comporter une relation nommée, choisie parmi un ensemble de cadres théoriques : la théorie ancrée (Strauss et Corbin), l’analyse qualitative de contenu (Mayring), la phénoménologie (Moustakas et van Manen), l’analyse thématique (Braun et Clarke), l’analyse du discours, ainsi qu’un cadre utilisateur permettant de définir vos propres relations. Chaque relation est accompagnée d’une brève définition, et la direction de la flèche ainsi que le style de la ligne peuvent être définis individuellement pour chaque ligne. Les libellés sont enregistrés en anglais et affichés dans la langue de l’interface ; ainsi, un graphe enregistré dans une langue s’affiche correctement dans une autre.


## Requêtes SQL : exécution simplifiée

Les requêtes SQL peuvent désormais être exécutées plus simplement :

- Utilisez le raccourci Ctrl + Entrée pour exécuter votre requête.
- Si vous avez sélectionné une partie de votre requête, seule cette partie sera exécutée.
- Une option de menu vous permet de commenter ou de décommenter le texte sélectionné.


## Nuages de mots et filtres

Vous pouvez désormais choisir des listes de mots vides dans plusieurs langues pour affiner vos résultats. Des filtres de texte ont été ajoutés aux listes déroulantes pour les fichiers, les dossiers et les catégories. Un clic droit ouvre un menu proposant des options supplémentaires.


## Rapports de codage : plus d’options et de flexibilité

### Résumé du codage

Un menu contextuel vous permet d’afficher les fichiers codés associés à un code.

### Fréquence du codage

Un menu contextuel vous permet également d’afficher les fichiers codés associés à un code. Vous pouvez activer ou désactiver le redimensionnement automatique de la largeur des colonnes. Les noms complets des codes (y compris leur hiérarchie) peuvent également être affichés.


## Corrections de bogues

Cette version inclut de nombreuses corrections de bogues visant à améliorer la stabilité et la fiabilité de QualCoder :

- Recherche A/V par cas : correction d’un problème où le filtre « important » et la clause ORDER BY étaient appliqués à la mauvaise requête SQL, ce qui entraînait des résultats de filtrage erronés pour les médias audio/vidéo.
- Exportation vers Excel (XLSX) : suppression d’une colonne en double qui décalait de manière incorrecte la valeur « a/v » dans les rapports de cas.
- Filtre « Only memos » : les chaînes « Only memos » et « Only coded memos » n’étaient pas marquées pour la traduction, ce qui empêchait le filtre de fonctionner correctement dans la version espagnole. Ce problème est désormais résolu pour toutes les langues.
- En-têtes de la matrice : correction de quatre problèmes qui empêchaient l’affichage correct des codes, des fichiers et des mémos de cas dans la vue matricielle (notamment une faute de frappe « alll », une comparaison superflue avec « Case: », une validation incorrecte des tuples et un littéral « All memo » mal placé).
- Option « Also all memos » : affiche désormais correctement le mémo du segment codé, un comportement qui faisait défaut auparavant malgré ce que suggérait le libellé.
- Fusion de projets : correction d’une erreur qui survenait parfois lors de la fusion de projets contenant des fichiers audio, vidéo ou image.

## Nouvelles fonctionnalités

### Hiérarchie des catégories dans les en-têtes

Le chemin hiérarchique complet s’affiche désormais avant le nom du code (par exemple : Catégorie racine > Sous-catégorie > … > Code), ce qui facilite la lecture contextuelle de chaque segment.

### Codes cooccurrents

Sous chaque note de segment codé, l’ensemble des codes qui se recoupent au sein d’un même fichier est désormais répertorié entre parenthèses, ce qui permet d’identifier rapidement les recoupements de codage. Cette fonctionnalité s'applique aux données textuelles, audio/vidéo et aux images. Vous pouvez consulter et exporter les codes qui se chevauchent.

### Nouvelle option de tri par catégorie

Une nouvelle option de tri a été ajoutée au menu de tri : « Catégorie A-Z » et « Catégorie Z-A », qui organise les résultats par ordre alphabétique selon la hiérarchie des catégories (le nom du code servant de critère secondaire).


## En résumé

Cette mise à jour de QualCoder représente une avancée majeure pour l’analyse qualitative. Elle offre une meilleure organisation grâce à des hiérarchies de codes, une intégration intelligente de l’IA avec des niveaux d’autorisation sécurisés, ainsi que des outils de gestion de fichiers plus puissants (PDF, LaTeX, questionnaires). L’interface a été améliorée pour une meilleure ergonomie, avec des visualisations avancées (graphiques de cooccurrence, cartes mentales) et des exportations flexibles (ODT, PDF annotés, Gephi, draw.io). De nombreuses corrections de bogues ont également été mises en œuvre pour une expérience plus stable.


## Prochaines étapes

Nous travaillons déjà sur les prochaines améliorations de QualCoder. Vos retours sont essentiels pour nous aider à hiérarchiser les fonctionnalités futures. N’hésitez pas à nous faire part de vos suggestions, rapports de bogues ou idées via [notre canal d’assistance](https://github.com/ccbogel/QualCoder/issues).
