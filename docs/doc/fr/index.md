**ATTENTION : La traduction est en cours, une pré-traduction a été fait avec Deepl. Un travail de relecture est en cours**
Bienvenue sur le wiki de QualCoder !

Ce wiki contient des instructions pour installer et utiliser le logiciel d'analyse de données qualitatives QualCoder. Les informations présentées ici concernent la version la plus récente de QualCoder.

## Qu'est-ce que QualCoder ?
QualCoder est un logiciel gratuit et open source d'analyse de données qualitatives.
Avec QualCoder, vous pouvez coder du texte, des images, de l'audio et de la vidéo, rédiger des notes de journal et des mémos. Vous pouvez organiser les codes dans un schéma hiérarchique en forme d'arbre. Le codage de l'audio et de la vidéo nécessite le lecteur multimédia VLC.
Des rapports de comparaison entre codeurs peuvent être générés pour le codage de texte en utilisant la statistique Kappa de Cohen. Un graphique affichant les codes et les catégories peut être généré pour visualiser la hiérarchie de codage. La plupart des rapports peuvent être exportés au format HTML, en *OpenDocumentText* (ODT) ou en fichiers texte brut.

Depuis la version 3.6, QualCoder inclut un ensemble de fonctionnalités assistées par IA utilisant GPT-4 ou d'autres grands modèles de langage pour explorer, analyser et interagir avec les données de manière innovante. Familiarisez-vous avec de nouvelles données en [explorant des sujets ou concepts larges](https://qualcoder-fr.frama.io/5.1.-AI-chat-based-analysis#topic-analysis-chat) via un chat interactif avec l'IA. Approfondissez des aspects spécifiques grâce au [codage assisté par IA](https://qualcoder-fr.frama.io/4.3.-AI-Assisted-Coding) et à [l'analyse de texte](https://qualcoder-fr.frama.io/5.1.-AI-chat-based-analysis#text-analysis-chat). Et si vous en arrivez au point où vous devez synthétiser et consolider vos résultats, [discutez-en dans un chat de codage](https://qualcoder-fr.frama.io/5.1.-AI-chat-based-analysis#code-analysis-chat) avec l'IA.

QualCoder est conçu pour être utilisé comme un logiciel client, par une seule personne à la fois (un deuxième codeur peut utiliser le même projet sur le même ordinateur, ou le dossier du projet peut être transféré sur l'ordinateur du deuxième codeur). QualCoder n'est pas conçu pour être utilisé simultanément par plusieurs personnes. L'accès au projet dans un espace cloud n'est pas recommandé, car cela peut corrompre la base de données si la connexion est perdue pendant une mise à jour de la base.

## Pourquoi utiliser QualCoder ?

**QualCoder est gratuit.** De nombreux logiciels d'analyse qualitative nécessitent des frais onéreux ou des abonnements mensuels. Tout le monde ne peut pas se permettre ces coûts.

**QualCoder est facile à utiliser.** Il dispose de tout ce dont vous avez besoin pour réaliser une analyse qualitative, sans les interfaces compliquées de certaines alternatives.

**QualCoder fonctionne hors ligne.** Internet n'est pas toujours disponible, et QualCoder n'a pas besoin d'une connexion pour fonctionner.

**QualCoder n'est pas lié à un ordinateur.** Si vous changez de lieu de travail, vous n'avez pas à vous soucier de perdre la licence de votre ancien employeur ou d'en acheter une nouvelle. La licence de QualCoder vous permet d'utiliser le logiciel, peu importe où vous travaillez ou sur quel ordinateur il est installé.

**QualCoder est multiplateforme.** Il fonctionne sous Linux, Windows et Mac, ce qui signifie que vous n'avez pas à vous inquiéter si vous changez de système d'exploitation, et que vous pouvez collaborer avec des collègues utilisant d'autres plateformes.

**QualCoder utilise l'IA de manière transparente.** Contrairement à la plupart des logiciels commerciaux d'analyse qualitative, QualCoder vous permet de voir et même de modifier les commandes sous-jacentes de ses fonctionnalités IA. Vous pouvez également choisir entre différents modèles d'IA ou intégrer le vôtre. Cela redonne le contrôle méthodologique aux chercheurs et fait de QualCoder une plateforme idéale pour expérimenter de nouvelles formes d'analyse qualitative assistée par IA. Et oui, vous pouvez aussi désactiver complètement les fonctionnalités IA si vous choisissez de ne pas les utiliser.

**QualCoder s'appuie sur la communauté.** Si vous trouvez un bug ou avez une demande de fonctionnalité ou un retour, écrivez-le sur la page GitHub de QualCoder : [github.com/ccbogel/QualCoder](https://github.com/ccbogel/QualCoder).

**QualCoder s'améliore constamment.** QualCoder est activement développé, ce qui signifie que des versions améliorées sont régulièrement publiées.

**QualCoder soutient les standards ouverts.** QualCoder vise à supporter le standard REFI-QDA, voir [qdasoftware.org](https://www.qdasoftware.org/). Vous pouvez échanger des livres de codes et des projets avec vos collègues, même s'ils n'utilisent pas QualCoder, tant que leur logiciel supporte le standard REFI-QDA. Cela signifie que vos données ne risquent pas de devenir inaccessibles.

**QualCoder peut être modifié.** Vous pouvez modifier et adapter QualCoder à vos besoins, ou demander à quelqu'un de le faire pour vous, à condition de publier vos modifications pour tous. Cela signifie également que vous pouvez copier le logiciel et le donner gratuitement à vos collègues ou étudiants. Il est publié sous licence LGPL v3 à partir de la version 3.6.

**QualCoder est une option logicielle pour soutenir la science ouverte.** [Recommandations de l'UNESCO sur la science ouverte](https://www.unesco.org/fr/science-ouverte?hub=686)


## Collaboration sur un projet QualCoder

[Page sur le travail en équipe avec QualCoder](https://qualcoder-org.github.io/doc/fr/2.4.-Working-in-a-Team/)

**Si vous utilisez et appréciez QualCoder, soutenez son développement.**

<a href="https://www.buymeacoffee.com/ccbogelB" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
