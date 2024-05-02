# Erste Schritte und Work-Around für Git

- [Erste Schritte](#erste-schritte)
  - [Voreinstellungen](#voreinstellungen)
    - [Python installieren](#python-installieren)
    - [Git installieren](#git-installieren)
  - [Repository lokal einrichten](#repository-lokal-einrichten)
    - [Existierendes Repo downloaden](#existierendes-repo-downloaden)
    - [VM einrichten & Pakete installieren](#virtuelle-umgebung-einrichten--pakete-installieren)
    - [Branch wechseln](#branch-wechseln)
  - [Export von requirements.txt](#export-von-requirementstxt)
- [Git-Handbuch mit Erklärungen](#git-handbuch-mit-erklärungen)
  - [Git Installieren](#git-installieren)
  - [Repository Aufsetzen](#repository-aufsetzen)
  - [Änderungen Speichern und Uploaden](#änderungen-speichern-und-uploaden)
  - [Branches & Merges](#branches-und-merges)
    - [Branches](#branches)
    - [Merges](#merges)
    - [Pull Request](#pull--merge-request)
  - [Updates aus globalem Repo downloaden](#updates-aus-globalem-repo-downloaden)
  - [Zusatz](#zusatz)
    - [Rebase](#rebase)
    - [Zusammenfassen von Commits](#zusammenfassen-von-commits)
- [Nützliches](#nützliches--links)

# Erste Schritte

> Die Schritte sind alle für den Umgang mit der **Kommando-Zeile** erklärt. Das lässt sich aber auch auf **Visual Studio** übertragen. In VS gibt es auch das Icon für „Source Control“ mit dem Repos hinzugefügt und virtuelle Maschinen erstellt werden können.

## Voreinstellungen

### Python installieren

Check aktuelle Version:

    python3 --version

Besser >= `Python 3.9` einrichten. Auf Windows direkt über Microsoft Store installieren. Für Mac und manuelle Installation über [Python.org](https://www.python.org/downloads/).

### Git installieren

Um zu schauen, ob Git bereits installiert ist, gib im **Terminal / CMD** folgenden Befehl ein:

    git --version

Ist noch kein Git installiert, gibt es hier die entsprechenden [Download-Files](https://git-scm.com/downloads). Nach der Installation wieder mit `git --version` überprüfen.

Beim ersten Verbinden eines lokalen Repo's mit einem remote Repo kann es sein, dass noch der Uername und die E-Mail hinterlegt werden müssen.

    git --global user.name "John Smith"
    git config --global user.email "your_email@example.com"

## Repository lokal einrichten

### Existierendes Repo downloaden

In gewünschtes Arbeitsverzeichnis wechseln:

    cd <dir>

Oder (_einfacher_) über Dateien / Finder in das Verzeichnis wechseln und:

- für Windows: `cmd` in die Suchleiste schreiben

- für Mac: `Rechtsklick` auf aktuelles Verzeichnis -> `In Terminal öffnen`

Anschließend dann das remote Repo clonen:

    git clone https://gitlab.hrz.tu-chemnitz.de/tud-fgdh/software-development/software-development-ws-23/swdev-23-ws-g2.git

Danach sollte Ordner mit dem Namen _SWDEV-23-WS-G2_ erstellt worden sein.

> In manchen Fällen wird anstelle eines Passwortes ein eigener **_„Personal Access Token“_** gefordert, um Zugriff auf das Repo zu bekommen. Den kann man sich einfach im Gitlab unter seinem Account -> „Preferences“ -> „Access Tokens“ erstellen, kopieren und dann als Passwort verwenden.

<u>Zum überprüfen der Verbindung:</u>

    git remote -v

Nun sind jeweils das globale und lokale Repo aufgesetzt und über `git remote -v` miteinander verbunden.

### Virtuelle Umgebung einrichten & Pakete installieren

> Benötigt Python3.x Installation! Check mit `python3 --version`. Besser >= `Python 3.9` einrichten.

#

In virtuellen Umgebungen können alle benötigten Pakete wie Pandas, Numpy, etc. eingerichtet und nach dem Projekt einfach wieder gelöscht werden. Bekannt ist sicherlich Anaconda, womit automatisch viele Pakete für Data Science Projekte installiert werden. Außerdem kann man mit Anaconda auch verschiedene Python-Versionen für verschiedene Umgebungen nutzen und beim installieren von zusätzlichen Paketen werden abhängigkeiten sehr genau geprüft (_conda_ als Paketverwaltung). Nachteil allerdings: kostet Geld sobald man mal Kommerziell arbeitet, deshalb hier noch mal ein Intro, um direkt mit dem zuvor installierten Python eine virtuelle Umgebung zu erstellen:

Dafür zwei Möglichkeiten:

#### 1. Automatisch via makefile

Benötigt `make`-Befehl. Mit `make --version` testen.

Im Terminal von _Visual Studio_:

    make run

Damit ist sowohl die virtuelle Umgebung aktiviert als auch alle Pakete aus `requirements.txt` installiert.

#### 2. Manuell

In Arbeitsumgebung wechseln:

    cd SWDEV-23-WS-G2

Virtuelle Umgebung erstellen:

    python3 -m venv .venv

Virtuelle Umgebung aktivieren:

- auf Mac / Linux:

        source .venv/bin/activate

- auf Windows:

        .venv\Scripts\activate

Sobald Umgebung aktiviert ist, erscheint der Name der Umgebung in Klammern vor dem Arbeitsverzeichnis `(.venv)`.

Virtuelle Umgebung deaktivieren mit:

    deactivate

#

> Aktuell ist die virtuelle Umgebung noch "_plain_", sprich es sind keine individuellen Pakete installiert!

Wer bisher immer mit Anaconda gearbeitet hat, kennt bereits `conda install ...` als Paketverwaltung. Die von Python selber bereitgestellte Paketverwaltung heißt `pip` und damit können genauso alle möglichen Pakete installiert werden: `pip install <paket>==<Version>`. (Über)

Installierte Pakete sehen:

    pip list

Pip updaten:

    pip install --upgrade pip

##### Pakete installieren

In einer `requirements.txt` werden alle für das Projekt benötigten Pakete gespeichert, um das Einrichten für alle Entwickler zu erleichtern. Zur Installation einfach mit aktivierter virtueller Umgebung den Befehl ausführen:

    pip install -r requirements.txt

#

### Branch wechseln

Für eine genauere Erklärung was Branches eigentlich sind, gibt es unten noch den [Git-Workshop mit Erklärungen](#git-workshop-mit-erklärungen) mit dem Unterkapitel [Branches](#branches). Damit es zu keinen Konflikten beim Upload kommt und jeder direkt starten kann, sei dem aber vorweggegriffen und hier eine kurze Erklärung zu Branches gegebenen:

![](img/git-branches.svg)
[Quelle: Bitbucket - Using Branches](https://www.atlassian.com/git/tutorials/using-branches)

Mit einem Branch (==Zweig), kann ausgehend von einem bestimmten Arbeitsstand, eine Kopie erzeugt und der Code darauf aufbauend weiter entwicklt werden. Um die Neuerungen aus dem Branch wieder mit dem „Hauptzweig“ zusammenzuführen, gibt es entweder den [Merge](#merges)-Befehl (**_lokal_**) oder den „[Pull / Merge Request](#pull--merge-request)“ (**_global_**).

Eine übersicht aller Branches erhalten:

    git branch -r
    git branch -a

Einen neuen Branch erstellen:

    git branch -b <new-branch> <Referenz Branch>

oder:

    git checkout -b <Branch Name> <Referenz Branch>

Schauen in welchem Branch man sich befindet:

    git status

Den Branch wechseln:

    git checkout <new-branch>

Neuen Branch uploaden:

    git push -u origin HEAD:<branch-name>

„-u“ fügt den online-Branch als Tracking-Branch hinzu, wodurch zukünftig nur noch `git push` nötig ist. „origin“ ist der „Upstream“, also die URL des gesamten Repositories. „HEAD“ referenziert auf den aktuellen Stand des Branches in dem man sich befindet. Durch `:<branch-name>` wird dann der Stand von HEAD in den Branch geschoben und falls nötig, noch erstellt.

## Export von requirements.txt

Arbeitet man an eigenen Features kommen sicher auch neue Pakete hinzu, die dann jeder andere auch bei sich installieren muss, sobald er den Code lokal ausführen möchte. Dafür gibt es auch ein Paket, was die Verwaltung und Erstellung der `requirements.txt` vereinfacht.

    pip install pipreqs

    pipreqs ./src --ignore .venv (--force)

Option `--force`, falls existierende `requirements.txt` überschrieben werden soll.

# Git-Handbuch mit Erklärungen

- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/setting-up-a-repository): Komplettes Git-Tutorial

## Git installieren

Um zu schauen, ob Git bereits installiert ist, gib im **Terminal / CMD** folgenden Befehl ein:

    git --version

Ist noch kein Git installiert, gibt es hier die entsprechenden [Download-Files](https://git-scm.com/downloads).

## Repository aufsetzen

[Atlassian Tutorial - Setting Up A Repo](https://www.atlassian.com/git/tutorials/setting-up-a-repository)

Git erleichert das gemeinsame Bearbeiten und Entwicklen von Code. Dafür wird ein zentrales (globales) Repository (Repo) bei einem Git-Anbieter wie _Bitbucket_, _GitHub_ oder **_GitLab_** erzeugt, auf dem dann alle Teilnehmer Zugriff haben. Neben dem **globalen Repo** ist ein **lokales Repo** nötig, um lokal am Code mit Hilfe seiner IDE VisualStudio, IntelliJ, etc. zu arbeiten.

Beim ersten Verbinden eines lokalen Repo's mit einem gloabeln Repo kann es sein, dass noch der Uername und die E-Mail hinterlegt werden müssen.

    git --global user.name "John Smith"
    git config --global user.email "your_email@example.com"

#

Prinzipiell gibt es **zwei Möglichkeiten** um mit einem Git-Projekt zu starten:

#### 1. Erzeuge lokales Repo und globales Repo separat und verbinde via URL

    git init <project-name>
    cd <project-name>
    git remote add origin https://gitlab.com/<username>/<global-repo-name>.git

Beim erstellen eines globalen Repo's wird automatisch ein _„Branch“_ mit dem Namen **„Main“** _oder_ **„Master“** erstellt. Dieser existiert lokal noch nicht und muss dementsprechend vom globale Repo heruntergeladen werden.

<u>Zum überprüfen:</u>

    git branch -r

oder

    git branch -a

`-r` / `-a` steht jeweils für `remote` / `all`.

<u>Zum herunterladen:</u>

    git pull origin main

#

#### 2. Erstelle globales Repo und clone auf lokalen Rechner

    git clone https://gitlab.com/<username>/<global-repo-name>.git

<u>Zum überprüfen der Verbindung:</u>

    git remote -v

Nun sind jeweils das globale und lokale Repo aufgesetzt und über `git remote -v` miteinander verbunden.

## Änderungen speichern und uploaden

[Atlassian Tutorial - Saving Changes](https://www.atlassian.com/git/tutorials/saving-changes)

Alle bereits getätigten Änderungen können mit `git status` oder im Git-Plugin bei **Visual Studio** unter „Changes“ überprüft werden. Bei `git status` gibt es entweder _„changes“_ oder _„(un-)tracked files“_, also Änderungen in bereits exisitierenden Files oder neu erstellte Files.

Untracked files (und directories) können mit `git clean -d -f` entfernt werden (KANN NICHT MEHR RÜCKGÄNGIG GEMACHT WERDEN!). `-f` steht für `force` und `-d` für `directory`. Mit der flag `-n` kann man sich auch erstmal **_nur_** anzeigen lassen, welche Files gelöscht werden.

    git clean -n (zeigt nur zu löschende files)
    git clean -dn (zeigt zu löschende files & dirs)

    git clean -f (löscht nur files)
    git clean -df (löscht files & dirs)

Mit `-i` lässt sich auch ein `interactive` Modus starten bei dem man da für jedes File separat entscheiden kann, was damit passieren soll.

Änderungen in der `.gitignore` können mit dem Befehl `git rm -rf --cached .` berücksichtigt werden (insbesondere das nachträgliche Löschen von Files).

<u>Git arbeitet mit den „three trees“:</u>

1. _Working Directory_
2. _Staging Area_
3. _Commit History_

#

Nach den Änderungen an einem File befinden sich die Änderungen lediglich im **Working Directory**. Das wird dadurch gekennzeichnet, dass bei `git status` steht _„Changes not staged [...]“_ oder _„Untracked files:“_. Möchte man die Änderungen in die **Staging Area** überführen und damit bereitmachen, um in die **Commit History** zu gehen, führt man

    git add <file-name> (einzelne Datei)
    git add .   (alle Änderungen im Repo)

Bei `git status` oder Visual Studio sind alle Änderungen jetzt als _„Changes to be committed:“_ oder _„Staged Changes“_ aufgeführt. Möchte man einzelne oder alle Dateien wieder zurück in das **Working Directory** bringen, um noch Änderungen daran zu machen:

    git reset <file>
    git reset

Sind alle Ändernungen gemacht und sollen in die „**Commit History**“ gebracht werden, geht das mit

    git commit -m "Kommentar was gemacht wurde etc.."

`git status` ist wieder leer und ein neuer _„Commit“_ wurde erzeugt. Die gesamte Commit History kann via `git log` oder (schöner)

    git log --graph --oneline --decorate

angeschaut werden. Mit `git commit -a -m "Message"` kann `git add .` und kann `git commit` zusammengefasst werden.

#

Wurde ausversehen eine Änderung commited, die wieder rückgängig gemacht werden soll oder möchte generell an einen früheren Punkt des Projektes springen, geht das mit:

    git rebase <commit-id>

sowie

    git reset <commit-id>

`git rebase <commit-id>` ist eine schwächere Version des Reset und versetzt den **HEAD** lediglich an die Stelle der commit-ID. Dort kann dann der Stand zu dem Zeitpunkt angeschaut werden. Änderungen allerdings immer in einem neuen Branch!

![](img/git-reset.svg)

Mit `git reset <commit-id>` (implizit `--mixed`) bleiben alle Änderungen im Working Directory erhalten, lediglich die Commits & Stages werden zum Zeitpunkt der commit-ID zurückgesetzt. Das heißt es befinden sich Dateien im Working Directory, die noch nicht gestaged sind (`git status`).

Mit git `git reset <commit-id> --hard` werden auch alle Änderungen im Working Directory überschrieben. Also Änderungen rückgängig gemacht und `git status` ist up-to-date mit dem Stand des commit-id.

`git reset <commit-id> --soft` liegt genau dazwischen und setzt ledglich die Commit-Historie zurück und lässt alle Änderungen in der Staging Area.

#

Für Änderungen im Kommentar des letzten commits:

    git commit --amend -m "an updated commit message"

Für Änderungen im Code, die nachträglich zum letzten commit hinzugefügt werden sollen:

    git add .
    git commit --amend --no-edit

Möchten wir die Arbeit der letzten lokalen commits zusammenfassen geht das mit

    git rebase -i HEAD:~x

wobei x die Anzahl der letzten commits beschreibt die zusammengefasst werden sollen. Anstelle von HEAD:~x geht auch die commit-ID (`git log`).

Ist nun alles bereit zum Upload, kann mit dem nachfolgenden Befehl alles in den master-Branch geschoben werden.

    git push origin HEAD:master

## Branches und Merges

### Branches

Um die Arbeit mit Git noch besser zu verstehen, noch ein kurzes Intro zu „Branches“ (Zweige).

![](img/git-branches.svg)
[Quelle: Bitbucket - Using Branches](https://www.atlassian.com/git/tutorials/using-branches)

Bisher haben wir nur vom „Main“- oder „Master“-Branch geredet, der am Ende auch den finalen lauffähigen Code beinhaltet. Bei mehrere Developern kann es allerdings hinderlich sein, wenn jeder seine individuellen Änderungen in den Main-Branch pusht und damit dann Konflikte bei anderen auftreten („Centralized WorkFlow“, [hier mehr](https://www.atlassian.com/git/tutorials/comparing-workflows)). Besser ist der „[Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)“, bei dem jedes zu entwickelnde Feature einen eigenen Branch enthält und dann zum Schluss komplett in den Main-Branch überführt wird.

Eine übersicht aller Branches erhalten:

    git branch -r
    git branch -a

#

Einen neuen Branch erstellen:

    git branch -b <new-branch> <Referenz Branch>

oder:

    git checkout -b <Branch Name> <Referenz Branch>

#

Branch Löschen

    git branch -d <branch>
    git branch -D <branch>

#

Schauen in welchem Branch man sich befindet:

    git status

#

In einen neuen Branch wechseln:

    git checkout <new-branch>

#

Den aktuellen Branch umbennenen:

    git branch -m <new-branch-name>

#

Neuen Branch uploaden:

    git push -u origin HEAD:<branch-name>

„-u“ fügt den online-Branch als Tracking-Branch hinzu, wodurch zukünftig nur noch `git push` nötig ist. „origin“ ist der „Upstream“, also die URL des gesamten Repositories. „HEAD“ referenziert auf den aktuellen Stand des Branches in dem man sich befindet. Durch `:<branch-name>` wird dann der Stand von HEAD in den Branch geschoben und falls nötig, noch erstellt.

### Merges

#

Fast-Forward-Merge vs. 3-Way-Merge

Angenommen man hat an einem Feature gearbeitet, während sich der Stand vom Main nicht, oder nur in andere Files geändert hat. Dann gibt es den Fast-Forward-Merge, der das aktuelle Feature an die Spitze vom Main setzt und dann den Main mit dem Feature vereint, sodass Main und der neue Branch auf dem selben Stand sind.

![](img/git-ffw-merge.svg)
[Quelle: Bitbucket - Merge](https://www.atlassian.com/git/tutorials/using-branches/git-merge)

    git checkout main
    git merge --no-ff <feature-branch>
    git branche -d <feature-branch> (löscht Branch)

Die Flag „-no-ff“ fügt für den Merge einen neuen commit hinzu, alo einen Eintrag, dass ein Merge stattgefunden hat. Das würde normalerweise durch die Fast-Forward-Struktur verloren gehen. Die Funktion `git merge` führt dann automatisch einen `git rebase` durch, der auch zum zusammenfassen von Commits genutzt wird. Weitere Infos dazu unten in [Rebase](#rebase).

![](img/git-3w-merge.svg)
[Quelle: Bitbucket - Using Branches](https://www.atlassian.com/git/tutorials/using-branches/git-merge)

Jetzt zum 3-Way-Merge. Dabei ändert sich auch der Inhalt im Main-Branch und bildet quasi den normalen Workflow ab.

    git checkout main
    git merge <feature-branch>
    git branche -d <feature-branch> (löscht Branch)

Im Laufe der Entwicklung eines Feature kommen einige Commits zusammen (`git log --graph --oneline --decorate `). Falls man da etwas aufräumen möchte, schaut weiter bei [Zusammenfassen von Commits](#zusammenfassen-von-commits) nach.

### Pull / Merge Request

Mit dem Pull / Merge Request, können Änderungen aus einem Branch in einen anderen Branch integriert werden. Für gewöhnlich macht man das für die Entwicklung neuer Features im Main-Branch. Ist man mit der Entwicklung eines Features in einem separaten Branch fertig, pusht man seinen Code in den zugehörigen remote Branch und erstellt über die Benutzeroberfläche von GitLab einen „Merge Request“.

Dabei wird festgelegt welcher „Source Branch“ in welchen „Target Branch“ gemergt werden soll und wer als „Approver“ noch mal über den Code schauen soll, um die Änderungen quasi „abszusegnen“.

Hier sei einfach noch mal auf die Doku von GitLab verwiesen: [Merge Request](https://docs.gitlab.com/ee/user/project/merge_requests/)

## Updates aus globalem Repo downloaden

Falls andere Developer Änderungen an ihrem Code in das Repo gepusht haben, gibt es zwei Varianten, diese in den lokalen Code zu integrieren:

Git Fetch:

    git fetch --dry-run
    git fetch origin
    git checkout <branch>
    git log --oneline <fetched_remote_branch>
    git merge <fetched_remote_branch>

Git Pull:

    git pull

Git pull führt die oben genannten Befehle automatisch aus.

## Zusatz

### Files löschen

Sollen Files aus dem Repo entfernt werden, kommt es häufig vor, dass die Änderung nicht registriert wird (insbesondere, wenn das `.gitignore`-File angepasst wird).

Dafür werden mit `git rm -r --cached .` erst alle bisher getrackten Files entfernt und mit der Flag `--cached` bleiben diese allerdings im Working Directory enrhalten. Anschließend erstellt man dafür einen neuen Commit und die gelöschten Files werden nicht mehr hinzugefügt.

    git rm -r --cached .
    git add .
    git commit -m ".gitignore is now working"

### Rebase

OPTIONAL: Um sein aktuelles Feature an die Spitze von Main zu bringen gibt es die Funktion `git rebase`. Diese ordnet dem aktuellen Branch eine neue „Base“ zu -> „RE-base“. Die Base wird dann entsprechend bei `git log --graph --oneline --decorate ` angezeigt.

![](img/git-rebase.svg)
[Quelle: Bitbucket - Rebase](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase)

Dafür:

    git checkout <feature-branch>
    git rebase main

### Zusammenfassen von Commits

Im Laufe der Entwicklung eines Feature kommen einige Commits zusammen (`git log --graph --oneline --decorate `). Falls man da etwas aufräumen möchte, kann man das mit dem Befehl machen:

    git rebase -i HEAD~3

Danach öffnet sich ein Text-Editor mit einigen Optionen:

    pick ba80f58 new update on README
    pick 3ddb80f Update README.md
    pick 607343a Update README.md

    Rebase b900b43..607343a onto b900b43 (3 commands)

    Commands:
    p, pick = use commit
    r, reword = use commit, but edit the commit message
    e, edit = use commit, but stop for amending
    s, squash = use commit, but meld into previous commit
    f, fixup = like "squash", but discard this commit's log message
    x, exec = run command (the rest of the line) using shell
    d, drop = remove commit

    These lines can be re-ordered; they are executed from top to bottom.

    If you remove a line here THAT COMMIT WILL BE LOST.

    However, if you remove everything, the rebase will be aborted.

    Note that empty commits are commented out

Um commits zusammenzuführen wählt man „squash“ wie folgt aus (Shift + I zum bearbeiten):

    pick ba80f58 new update on README
    squash 3ddb80f Update README.md
    squash 607343a Update README.md

Mit „Esc“ + „:wq!“ verlässt man den Editor und speichert. Der Commit erhält den Kommentar des oberen Commits „new update on README“. Falls man den anpassen möchte:

    reword ba80f58 new update on README
    squash 3ddb80f Update README.md
    squash 607343a Update README.md

Es öffnet sich ein neues Fenster mit:

    This is a combination of 3 commits.
    This is the 1st commit message:

    New Squash on Commit
    With new line

    This is the commit message #2:

    adjustments on app.py

    This is the commit message #3:

    Merged Commits

    Update README.md

Message anpassen und wieder mit „:wq!“ schließen.

Anstelle von

    git rebase -i HEAD~3

Kann auch die entsprechende Commit-ID benutzt werden. Diese steht bei `git log` neben den entsprechenden Commits

    git rebase -i a6f040abf48df4f00185f097cb17a62aded27b4b

Der Rest verhält sich analog.

# Nützliches & Links

- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/setting-up-a-repository): Komplettes Git-Tutorial
- [draw.io](https://app.diagrams.net/): Umgebung um Skizzen anzufertigen. Bspw. Darstellen von Architekturen oder Funktionen einzelner Features
- [Markdown-Syntax](https://www.markdownguide.org/basic-syntax/): Erklärung zur Markdown-Syntax
- [PEP 8 Style Guide für Python Code](https://peps.python.org/pep-0008/#code-lay-out)
- `src`:

  - `git-cheat-sheet.pdf`: Alle wichtigen Git-Kommandos auf einen Blick
