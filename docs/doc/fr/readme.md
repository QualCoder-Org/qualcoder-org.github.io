---
path: README
---

# LISEZ-MOI

![](../../logo.png)

# QualCoder
QualCoder est une application d'analyse qualitative de données écrite en Python.

Les fichiers texte peuvent être saisis manuellement ou chargés à partir de fichiers txt, odt, docx, html, htm, md, epub, rtf et  PDF. Les images, les vidéos et les fichiers audio peuvent également être importés pour être codés. Les codes peuvent être attribués à des sélections de texte, d'images et d'audio/vidéo, puis regroupés en catégories de manière hiérarchique. Différents types de rapports peuvent être générés, notamment des graphiques de codage visuel, des comparaisons de codeurs et des fréquences de codage. Des modèles d'IA tels que GPT-4 d'OpenAI peuvent être utilisés pour explorer vos données et analyser les résultats.  

Ce logiciel a été utilisé sur MacOS et diverses distributions Linux.
Les instructions et autres informations sont disponibles ici : https://qualcoder.wordpress.com/ et dans la [documentation](https://qualcoder-org.github.io/doc/fr/).

Il est préférable de télécharger la version actuelle à partir de la page Releases : https://github.com/ccbogel/QualCoder/releases

Si vous aimez QualCoder, offrez-moi un café...

<a href="https://www.buymeacoffee.com/ccbogelB" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## INSTALLATION 

### Pré-requis

Facultatif : VLC pour le codage audio/vidéo.
Facultatif : ffmpeg installé pour l'image de forme d'onde. Pour installer ffmpeg sous Windows, consultez :  https://phoenixnap.com/kb/ffmpeg-windows.

Lors du premier démarrage de QualCoder, vous pouvez [configurer les fonctionnalités améliorées par l'IA](#setup-of-the-ai-features) comme décrit ci-dessous.

### Windows

Vous avez deux options, voir le lien « Releases » (Versions) à droite de cette page :
- Les versions plus récentes contiennent un fichier **exe** créé sous Windows 11. Double-cliquez pour l'exécuter, le démarrage prend 20 secondes.
- Depuis la version 3.6, des **installateurs Windows** sont disponibles sur la page des versions. 

Lors de la première utilisation du fichier exe, Windows peut vous demander d'autoriser l'exécution de QualCoder. Cela est dû au fait qu'il provient d'un éditeur inconnu. L'obtention d'un certificat d'éditeur de confiance coûte très cher, ce qui rend cette option impossible dans un avenir proche. Si ces avertissements vous inquiètent, procédez à l'installation à partir de la source comme indiqué ci-dessous.

**Vous pouvez également procéder à l'installation à partir de la source :**

Utilisez un environnement virtuel (commandes au point 6 ci-dessous). Le fait de ne pas utiliser d'environnement virtuel peut affecter d'autres logiciels Python que vous avez peut-être installés.

1. Téléchargez et installez le langage de programmation Python. Veuillez utiliser Python 3.10, 3.11 ou 3.12 sous Windows, les autres versions pouvant causer des problèmes  [Python3](https://www.python.org/downloads/). Téléchargez le dernier « programme d'installation Windows (64 bits) » (ou celui qui correspond à votre architecture) pour l'une des versions Python mentionnées ci-dessus.

IMPORTANT : dans la première fenêtre de l'installation, cochez l'option « Ajouter Python au PATH ».

2. Téléchargez le logiciel QualCoder à partir du bouton vert « Code » sur la page https://github.com/ccbogel/QualCoder. Il s'agit de la version la plus récente, mais elle n'est pas encore officiellement disponible (des erreurs de codage peuvent parfois s'y glisser).  Cliquez sur le bouton vert « Code », puis sur « Télécharger le fichier ZIP ». **Vous pouvez également** choisir le fichier ZIP de la version la plus récente. Le lien vers les versions est disponible à droite de cette page.

3. Décompressez le dossier à l'emplacement de votre choix (par exemple, dans le dossier « Téléchargements »). (Astuce : supprimez le dossier QualCoder-master\QualCoder-master qui apparaît en double lorsque vous êtes invité à choisir l'emplacement de décompression. Ne conservez que QualCoder-master). 

4. Utilisez l'invite de commande Windows. Tapez « cmd » dans le moteur de recherche Windows Démarrer, puis cliquez sur le logiciel noir « cmd.exe » (la console de commande pour Windows). Dans la console, tapez ou collez, à l'aide du clic droit de la souris (ctrl+v ne fonctionne pas)

5. Dans l'invite de commande, déplacez-vous (à l'aide de la commande « cd ») dans le dossier QualCoder. Vous devriez vous trouver dans le dossier QualCoder-master ou, si vous utilisez une version, dans le dossier Qualcoder-3.6. Par exemple : 

```bash
cd Downloads\QualCoder-master
```

6. Installez l'environnement virtuel et les modules Python requis. 

La commande `py` utilise la dernière version installée de Python. La commande `py` ne fonctionne pas sur tous les systèmes d'exploitation Windows. Vous pouvez remplacer `py` par `python3`. Si plusieurs versions de Python sont installées sur votre système Windows, vous pouvez utiliser une version spécifique, par exemple `py -3.10`. Voir la discussion ici : [Différence entre py et python](https://stackoverflow.com/questions/50896496/what-is-the-difference-between-py-and-python-in-the-terminal)

L'installation peut prendre jusqu'à 10 minutes. Sur certains systèmes d'exploitation Windows, vous devrez peut-être remplacer la commande _py_ par _python3_ ci-dessous : 

```bash
py -m venv env
env\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

7. Exécutez QualCoder à partir de l'invite de commande, versions jusqu'à 3.6

```bash
py -m qualcoder
```

Dernier code, version 3.7 et supérieure, commencez par vous rendre dans le dossier src interne :

```bash
cd src
py -m qualcoder
```

8. Si QualCoder est dans un environnement virtuel, tapez ce qui suit pour quitter l’environnement virtuel :

`deactivate`

La commande devrait enlever le mot *(env)*.

**Relancer QualCoder**

Si vous n’êtes pas dans un environnement virtuel, 
Si vous n'utilisez pas d'environnement virtuel, tant que vous êtes dans la même lettre de lecteur, par exemple C:

`py -m qualcoder`

Si vous utilisez un environnement virtuel :

`cd` to the Qualcoder-master (or Qualcoder release folder) for versions up to 3.6:

```
env\Scripts\activate 
py -m qualcoder
```

`cd` vers Qualcoder-master (ou le dossier QualCoder) pour les versions 3.7 et supérieures : 

```
env\Scripts\activate
cd src
py -m qualcoder
```

## MacOS

Vous trouverez deux options (le « X » représentant la version actuelle) jointes à la version actuelle accessible via le lien situé à droite de cette page :
- **QualCoder_X_arm64.dmg** : ensemble d'applications pour les Mac récents équipés d'Apple Silicon (processeurs M1 ... M4)
- **QualCoder_X_x86_64.dmg** : ensemble d'applications pour les anciens Mac équipés d'un processeur Intel (core i5, i7, etc.).

Les ensembles d'applications sont compilés sur macOS Sequoia. Ils peuvent également fonctionner sur Sonoma et Ventura. Si vous utilisez une version plus ancienne, pensez à mettre à jour votre système d'exploitation ou à installer QualCoder à partir de la source, comme décrit ci-dessous.

Remarque : nous ne sommes actuellement pas en mesure de signer les ensembles d'applications, vous recevrez donc un avertissement indiquant que QualCoder provient d'un développeur non enregistré. Vous devez autoriser manuellement l'exécution de l'application si votre Gatekeeper est actif. Suivez ces étapes :
- Double-cliquez sur le fichier dmg téléchargé.
- Faites glisser QualCoder vers le lien vers vos applications (ignorez le dossier « __main__ » qui se trouve également dans la fenêtre).
- Lancez QualCoder en double-cliquant sur l'application dans votre dossier Applications. Vous recevrez un message d'erreur indiquant que QualCoder provient d'un développeur non enregistré. L'application ne se lancera pas.
- Allez dans Paramètres -> Confidentialité et sécurité -> Faites défiler vers le bas jusqu'à ce que vous voyiez un message indiquant que QualCoder n'a pas pu se lancer. Cliquez sur « Ouvrir quand même ».
- À partir de maintenant, QualCoder devrait démarrer sans problème.

Si ces paquets d'applications ne fonctionnent pas pour vous et que vous souhaitez **exécuter QualCoder à partir de la source**, procédez comme suit : 

**Sinon, installez à partir de la source :**

Utilisez un environnement virtuel (commandes au point 6 ci-dessous)

```bash
cd Downloads/QualCoder-master
```

6. Installer l’environnement virtuel et les paquets Python. 

La commande « python3 » utilise la dernière version installée de Python. Vous pouvez utiliser une version spécifique sur votre macOS si vous avez plusieurs versions de Python installées, par exemple « python3.10 ». Pour vérifier que vous utilisez la bonne version de Python, tapez `which python3`, ce qui devrait afficher : `/Library/Frameworks/Python.framework/Versions/3.<version>/bin/python3`. Si le résultat est `/usr/bin/python3`, ne continuez pas, car il s'agit du Python de votre système et son utilisation est déconseillée.

L'installation peut prendre jusqu'à 10 minutes. 

```bash
python3 -m venv env # this creates the virtual environment with the name "env" in your current directory
source env/bin/activate # this activates the virtual environment "env", (env) should appear in front of your prompt
pip3 install --upgrade pip # optionally; pip and pip3 are equivalent withing a virtual environment
pip3 install -r requirements.txt
```

7. Lancer QualCoder depuis la console

```bash
cd src # only for version 3.7 and newer
python3 -m qualcoder # python and python3 are equivalent withing a virtual environment
```

8. Si QualCoder est lancé dans un environnement virtuel (ce qui est recommandé), pour quitter l’environnement virtuel, tapez :

```bash
deactivate
```

La commande devrait enlever le mot *(env)*.

**Pour relancer QualCoder**

Si vous n’êtes pas dans un environnement virtuel :

```bash
cd Downloads/QualCoder-master
cd src # only for version 3.7 and newer
python3 -m qualcoder
```

Si vous êtes dans un environnement virtuel :

```bash
cd Downloads/QualCoder-master
source env/bin/activate
cd src # only for version 3.7 and newer
python3 -m qualcoder
```

## Linux

### Ubuntu Linux

Il existe un lien vers un fichier exécutable (double-cliquez pour l'exécuter) pour Ubuntu dans la version 3.6. 

Pour installer à partir du code source ci-dessous, dans un environnement virtuel. Si vous utilisez le gestionnaire de bureau alternatif Ubuntu **Xfce**, vous devrez peut-être exécuter cette commande : `sudo apt install libxcb-cursor0`

1. Si vous utilisez l'audio ou la vidéo, installez vlc (téléchargeable sur le site) ou : `sudo apt install vlc`

2. Installez pip et venv

`sudo apt install python3-pip python3.12-venv`

3. Téléchargez et décompressez le dossier Qualcoder. Ensuite, `cd` vers le dossier QualCoder.

4. Configurez l'environnement virtuel et installez les modules python. L'environnement virtuel se trouvera dans son propre dossier appelé env. L'installation des modules requis prend un certain temps.

Par exemple, vous pourriez vous trouver dans ce dossier, où vous avez décompressé Qualcoder : 

votreordinateur:~Téléchargements/QualCoder-3.7

```
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

5. Dernière version du code, version 3.7 et supérieure, commencez par vous rendre dans le dossier src interne :

```
cd src
python3 -m qualcoder
```

6. Après avoir utilisé QualCoder, désactiver l’environnement virtuel :

`deactivate`

**Utilisation à tout moment après l'installation, déplacez-vous vers le dossier QualCoder puis :**

```
source env/bin/activate
cd src
python3 -m qualcoder
```

Pour quitter l’environnement virtuel :

`deactivate`

Vous pouvez également créer un fichier .desktop pour lancer QualCoder :

Créez un fichier .Desktop pour le lancement, entrez cette commande (adaptez-la en fonction de l'emplacement du dossier du code source) :

bash -c 'cd ~/.local/share/qualcoder/src/ && ~/.local/share/qualcoder/env/bin/python3.12 -m qualcoder'

### Fedora 43

These instructions are adapted from the Fedora 42 instructions below, tested with QualCoder 3.7 on Fedora 43 with Python 3.12.12.

1. Install dependencies:

    ```bash
    sudo dnf install python3.12
    ```

2. Set up QualCoder:

    ```bash
    cd ~/qualcoder  # replace with appropriate location on your machine
    python3.12 -m venv env
    source env/bin/activate
    python3.12 -m ensurepip
    python3.12 -m pip install --upgrade pip
    mkdir tmp
    TMPDIR=./tmp python3.12 -m pip install -r requirements.txt
    deactivate
    ```

3. Usage:

    ```bash
    cd ~/qualcoder  # replace with appropriate location on your machine
    source env/bin/activate
    cd src
    python3.12 -m qualcoder
    ```

### Fedora 42

Ces instructions permettent de télécharger le code source actuel directement depuis GitHub. Remarque : Fedora utilise Wayland, qui peut ne pas fonctionner correctement avec l'interface graphique Qt. Il est recommandé d'installer également Xwayland.
Codage audio et vidéo : le logiciel plante et aucune solution n'a été trouvée pour le moment.

`sudo dnf install python3.12`

```
virtualenv env
source env/bin/activate
python3.12 -m ensurepip
python3.12 -m pip install --upgrade pip
git clone https://github.com/ccbogel/QualCoder.git
cd QualCoder
python3.12 -m pip install -r requirements.txt
```
Pour exécuter QualCoder 3.6 :
```
python3.12 -m qualcoder
```

Pour le code le plus récent, version 3.7 et supérieure, commencez par vous rendre dans le dossier src interne :

```
cd src
python3.12 -m qualcoder
```

Pour désactiver l'environnement virtuel :

`deactivate` 

**Utilisation :**

À tout moment, accédez au dossier Qualcoder à l'aide de la commande `cd` (si vous utilisez QualCoder 3.7 ou une version ultérieure, accédez au dossier src interne à l'aide de la commande cd src`) et entrez les commandes suivantes : 

```
cd QualCoder
source env/bin/activate
python3.12 -m qualcoder
```

Une fois terminé, tapez `deactivate` pour quitter l'environnement virtuel.

Remarque concernant Fedora. Il s'agit d'un problème lié au codage audio/vidéo. Le logiciel plante et aucune solution n'a pu être trouvée pour le moment.

 ### Arch/Manjaro Linux

Si vous utilisez des fichiers audio ou vidéo, installez VLC (téléchargeable sur le site) ou : `sudo pacman -S vlc`

Installez pip et venv :

`sudo pacman -S python python-pip python-virtualenv`

Téléchargez et décompressez le dossier Qualcoder. Ensuite, `cd` vers le dossier QualCoder.
Configurez l'environnement virtuel et installez les modules python. L'environnement virtuel se trouvera dans son propre dossier appelé env. L'installation des modules requis prend un certain temps.

```
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Maintenant, la commande pour démarrer QualCoder, pour les versions jusqu'à 3.6 :

`python3 -m qualcoder`

Dernier code, version 3.7 et supérieure, cd vers le dossier src interne d'abord :

```
cd src
python -m qualcoder
```

Après avoir utilisé QualCoder, désactivez l'environnement virtuel.

`deactivate`

Utilisation à tout moment après l'installation, déplacez-vous vers le dossier (puis vers le dossier src interne si vous utilisez la version 3.7 et supérieure), puis :

```
cd QualCoder
source env/bin/activate
python3 -m qualcoder
```

Pour quitter l'environnement :

`deactivate`

## Configuration des fonctionnalités IA
Si vous souhaitez utiliser les fonctionnalités améliorées par l'IA dans QualCoder, une configuration supplémentaire est nécessaire. Lorsque vous lancez l'application pour la première fois, un assistant vous guide tout au long du processus de configuration. Vous pouvez également le lancer ultérieurement via le menu en cliquant sur IA > Assistant de configuration. Voici les principales étapes :
1) Vous devrez activer l'IA et sélectionner le modèle que vous souhaitez utiliser.
   
- Si vous optez pour l'une des variantes de GPT-4 (recommandé), vous aurez besoin d'une clé API d'OpenAI. Rendez-vous sur https://platform.openai.com/ et créez un compte. Rendez-vous ensuite sur votre tableau de bord personnel, cliquez sur « API keys » dans le menu de gauche, créez une clé et entrez-la dans la boîte de dialogue des paramètres de QualCoder. Pour utiliser ces modèles, vous devrez également acheter des « crédits » auprès d'OpenAI. Le montant minimum à payer semble être de 5 dollars, ce qui vous permettra d'aller loin. Le coût d'une seule requête à l'IA est généralement de l'ordre de quelques centimes seulement.
- Vous pouvez également utiliser [« Blablador »](https://helmholtz-blablador.fz-juelich.de), un service gratuit proposé par l'agence allemande de recherche universitaire Helmholtz Society. Ce service utilise des modèles open source (Mixtral 8x7b étant le plus important à l'heure actuelle) et respecte pleinement la vie privée, car il ne stocke aucune donnée. La qualité des résultats est suffisante pour des questions simples, mais n'est pas encore à la hauteur de GPT-4 d'OpenAI. Si vous souhaitez utiliser Blablador, vous aurez besoin d'une clé API de la Helmholtz Society. Vous pouvez vous inscrire avec votre compte universitaire ou Github, Google, ORCID. Suivez les [instructions ici](https://sdlaml.pages.jsc.fz-juelich.de/ai/guides/blablador_api_access/).
- Vous pouvez passer d'un modèle à l'autre à tout moment en utilisant le menu Paramètres (IA > Paramètres).
  
2) Lors du premier démarrage de l'IA, QualCoder téléchargera automatiquement certains composants supplémentaires nécessaires à l'analyse locale de vos documents (ce modèle : https://huggingface.co/intfloat/multilingual-e5-large). Cela prendra un certain temps, veuillez patienter.
- Si vous souhaitez activer/désactiver la fonctionnalité IA ultérieurement ou modifier les paramètres, cliquez sur IA > Paramètres.

## Licence
QualCoder est distribué sous licence LGPLv3.

##  Citation APA style

Curtain, C. Dröge, K. (2025) QualCoder 3.7 [Computer software]. Retrieved from
https://github.com/ccbogel/QualCoder/releases/tag/3.7

## Créateur

**Dr Colin Curtain** BPharm GradDipComp PhD Maître de conférences en pharmacie à l'université de Tasmanie. J'ai obtenu un diplôme d'études supérieures en informatique en 2011. C'est à partir de cette date que j'ai développé mes compétences en programmation Python. Le projet QualCoder est né de mon utilisation de RQDA pendant mon doctorat - *Évaluation de l'aide à la décision clinique fournie par un logiciel d'analyse des médicaments*. Mon logiciel PyQDA original, aujourd'hui complètement obsolète, sur PyPI a été ma première tentative de création d'un logiciel qualitatif. La raison pour laquelle j'ai créé ce logiciel est que, pendant mon doctorat, RQDA ne s'installait pas toujours ou ne fonctionnait pas toujours bien pour moi, mais j'ai réalisé que je pouvais utiliser la même base de données SQLite et y accéder avec Python. La base de données actuelle est différente de l'ancienne version RQDA. Il s'agit d'un projet amateur en cours, peut-être une passion, que j'utilise avec certains étudiants en master et en doctorat que je supervise.

https://www.utas.edu.au/profiles/staff/umore/colin-curtain

https://scholar.google.com/citations?user=KTMRMWoAAAAJ&hl=en

**Fonctionnalités d'intelligence artificielle et plus encore :** 
**Dr. rer. soc. Kai Dröge,** [Université des sciences appliquées](https://www.hslu.ch/de-ch/hochschule-luzern/ueber-uns/personensuche/profile/?pid=823), Lucerne, Suisse et [Institut de recherche sociale](https://www.ifs.uni-frankfurt.de/personendetails/kai-droege.html) Francfort, Allemagne. Kai est un chercheur et enseignant expérimenté dans le domaine des méthodes qualitatives. Ses intérêts de recherche sont très variés et comprennent la sociologie des émotions et des relations intimes, la vie numérique et les nouveaux médias, ainsi que les questions de sociologie économique et du travail. Récemment, il s'est concentré sur les défis et les opportunités méthodologiques liés à l'intégration de l'IA dans la recherche qualitative. Il est également le créateur de [noScribe](https://github.com/kaixxx/noScribe#readme), un outil de transcription open source très populaire destiné spécialement aux entretiens qualitatifs.

## Laissez un avis

Si vous aimez QualCoder et le trouvez utile pour votre travail, merci de laisser un avis sur ces sites :

https://www.saashub.com/qualcoder-alternatives

https://alternativeto.net/software/qualcoder

De plus, si vous appréciez particulièrement Qualcoder et souhaitez promouvoir son utilisation, n'hésitez pas à rédiger un article sur votre expérience avec QualCoder.

## Avertissements concernant d'autres sources d'informations sur QualCoder 

Livre _Qualitative Data Analysis With Chatgpt And Qualcoder_. Nous avons été informés que ce livre pourrait contenir des informations erronées sur QualCoder.

Téléchargements d'exécutables à partir d'autres sites Web. Nous ne recommandons pas le téléchargement d'exécutables à partir d'autres sites que la page des versions QualCoder de GitHub.
