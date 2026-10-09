# Team

Hello, I am Dr. Colin Curtain and I am a lecturer from Australia at the [University of Tasmania](https://discover.utas.edu.au/colin.curtain). I have many interests including clinical pharmacy, computer programming, research, statistics and clinical decision support. I completed a PhD evaluating computerised clinical decision support in 2014. When doing my PhD I used R as the statistics program of choice. This is where my interest in qualitative data analysis and the use of RQDA came from, which ultimately led to this project. I am currently teaching in post-graduate clinical pharmacy and supervising Masters and PhD research.
[Google Scholar Publications](https://scholar.google.com/citations?user=BjiFQb0AAAAJ&hl=en)

Originally when doing my PhD I analysed qualitative survey data via thematic analysis using RQDA. After some installation difficulties with RQDA, I thought this could be reproduced in Python. I thought I would share QualCoder in the hope that it may help others. I generally work with Linux Ubuntu, and Windows. I work on the programming for this in my spare time, as a hobby.

If you use QualCoder and publish your results, I would really appreciate it if you can let me know.

========

Dr. Kai Dröge has been heavily involved with QualCoder development, particularly with artificial intelligence features and more.

**Dr. rer. soc. Kai Dröge,** [University for Applied Science](https://www.hslu.ch/de-ch/hochschule-luzern/ueber-uns/personensuche/profile/?pid=823), Lucerne, Switzerland and [Institute for Social Research](https://www.ifs.uni-frankfurt.de/personendetails/kai-droege.html) Frankfurt, Germany. Kai is an experienced researcher and teacher of qualitative methods. His research interests are wide-ranging and include the sociology of emotions and intimate relationships, digital life and new media, and questions of economic and labor sociology. Recently, he has focused on the methodological challenges and opportunities of integrating AI into qualitative research. He is also the creator of [noScribe](https://github.com/kaixxx/noScribe#readme), a popular open-source transcription tool aimed especially at qualitative interviews.

========

**Dr. Justin Missaghieh--Poncet** [Université de Pau et des Pays de l'Adour](https://www.univ-pau.fr/fr/index.html)
Testing, translation into French, software development. Other organisational developments, such as this website.

========

**Psic. Lorenzo Salomón Cárdenas** [Universidad Autónoma de Sinaloa](https://www.uas.edu.mx/)
Testing, software development enthusiast, translations into Spanish. Freelance Researcher and Human Rights Activist.

========

There are also many other contributors who have added code or suggestions for improvements over the years since QualCoder was first released in 2019.

========

## Governance

This document describes how the QualCoder project is run, who makes decisions and how people can take on responsibility. It is deliberately short. QualCoder is a volunteer project and the aim is to write down what already happens, not to add bureaucracy. Full details are here [GOVERNANCE.md](https://github.com/ccbogel/QualCoder/blob/master/docs/GOVERNANCE.md).

## Roles

### Project lead

Colin Curtain created QualCoder in 2019 and leads the project. The project lead:

- Reviews contributions, and merges them into the main repository.
- Publishes releases (or delegates this to another maintainer).
- Administers the GitHub repository (and the Codeberg mirror).

### Maintainers

Maintainers have write access to the repository. They review and merge pull requests, triage issues, answer questions in Discussions and take part in decisions about the roadmap.

Current maintainers:

| Name | Main areas
|------|------------|
| Colin Curtain | Project lead, core application, Windows builds |
| Kai Dröge | AI features, MCP integration, macOS builds, German translation.|
| Justin Missaghieh-Poncet | Website (qualcoder.org), Linux builds, French translation |
| Lorenzo Salomón | Testing, interface and module development, Spanish translation |

### Contributors

Anyone who submits code, documentation, translations, bug reports, tests or support to other users. Contributors do not need write access. Contributions are made under the project licence (LGPL v3), as described in [CONTRIBUTING.md](https://github.com/ccbogel/QualCoder/blob/master/docs/CONTRIBUTING.md).

### Translators

Translations are maintained through the `.po`/`.ts` files in `other_languages` and the `rebuild_lang.py` script. Translators are credited in the release notes.

| Translation coordinator  | Language |
|--------------------------|----------|
| Kai Dröge                | German   |
| Justin Missaghieh-Poncet | French   |
| Lorenzo Salomón          | Spanish  |
|                          |          |

## How decisions are made

- Day-to-day decisions (bug fixes, small improvements, documentation) are made by whichever maintainer handles the issue or pull request.
- Larger changes (new modules, changes to the database structure, changes to the project file format, new dependencies, licence changes) are discussed publicly in a GitHub issue or Discussion before work starts. Maintainers aim for consensus; if there is no consensus, the project lead decides.
- The roadmap is kept in `ROADMAP.md`, with each item linked to an issue where the discussion can be read.
- Decisions that affect users (removed features, changed behaviour, new minimum versions) are recorded in the release notes.

## Becoming a maintainer

A contributor may be invited to become a maintainer when they have:

- Contributed regularly over several months (code, translations, documentation or testing).
- Shown they can review other people's work constructively.
- Followed the Code of Conduct.

Any maintainer can propose a new maintainer. The proposal is discussed among the maintainers and accepted if no maintainer objects. The new maintainer is added to the table above and given repository access.

## Continuity

The repository lives under the project lead's GitHub account. To reduce the risk of the project depending on a single person:

- All maintainers have write access to the repository and to the Codeberg mirror.
- At least two maintainers hold the credentials for the project website and the CI secrets. [TO CONFIRM]
- If the project lead takes an extended break, the other maintainers can keep handling issues, reviewing contributions and publishing releases in the meantime.


## Code of Conduct

All participation in the project is subject to the Code of Conduct in [CONDUCT.md](https://github.com/ccbogel/QualCoder/blob/master/docs/CONDUCT.md).. Reports are handled by the maintainers.