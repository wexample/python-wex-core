# Roadmap : transformer les utilitaires Python en services wex

## Contexte

`pdf-generator` et `notification-dispatcher` sont des projets Python indépendants
exposés en HTTP, actuellement consommés par `bdo-letters` via Docker DNS + env vars.

**Objectif** : les enregistrer comme services wex réutilisables (pattern identique à
`postgres`, `temporal`, `n8n`…) dans un nouvel addon `wex-addon-services-syrtis`.
Les repos sources restent indépendants ; en local on peut monter le code en volume
pour développer sans rebuild (override manuel dans l'env local de l'app).

---

## Phase 1 — Créer wex-addon-services-syrtis

Nouveau package Python dans `WEXAMPLE/PACKAGES/PYTHON/wex/`.

- [ ] Créer la structure du package :
  ```
  wex-addon-services-syrtis/
    pyproject.toml
    src/wexample_wex_addon_services_syrtis/
      __init__.py
      addon_manager.py          # hérite AbstractAddonManager
      services/                 # services définis ici
  ```
- [ ] `addon_manager.py` : enregistre le package comme addon wex (pattern
  `wex-addon-services-db` / `wex-addon-services-platform`)
- [ ] Enregistrer l'addon dans la chaîne du kernel wex (addons list)
- [ ] Publier le package (tag + PyPI ou registry interne selon la stratégie)

---

## Phase 2 — Service pdf-generator

Source : `SYRTIS/project/utilities/pdf-generator` (reste son propre repo).

### 2a. Image Docker publiée

- [ ] Construire et pousser `syrtis/pdf-generator:<version>` sur le registry
- [ ] Vérifier que `Dockerfile.base` produit une image autonome (sans mount de code)
- [ ] CI : automatiser le build/push à chaque release du repo pdf-generator

### 2b. Définition du service wex

```
services/pdf-generator/
  service.yml
  docker/
    docker-compose.yml          # utilise l'image publiée
    docker-compose.dev.yml      # override : monte le source en volume + watchdog
  app_service.py                # contribution workdir : répertoire jobs/
```

- [ ] `service.yml` :
  - tags : `[utility, pdf]`
  - vars : `PDF_GENERATOR_PORT` (default 8000), `PDF_GENERATOR_JOBS_PATH`
  - install_config : injecter `PDF_GENERATOR_URL` dans l'env de l'app
- [ ] `docker/docker-compose.yml` :
  - image `syrtis/pdf-generator:<version>`
  - port `${PDF_GENERATOR_PORT}:8000`
  - volume `${PDF_GENERATOR_JOBS_PATH}:/app/jobs`
- [ ] `docker/docker-compose.dev.yml` :
  - remplace l'image par `syrtis/pdf-generator:develop` (Dockerfile.develop)
  - ajoute le volume du source : `${PDF_GENERATOR_SOURCE_PATH}:/app/src`
  - watchdog actif
- [ ] `app_service.py` : `get_workdir_contribution` assure que `jobs/` existe sur le host
- [ ] Documenter les vars attendues dans `service.yml`

---

## Phase 3 — Service notification-dispatcher

Source : `SYRTIS/project/utilities/notification-dispatcher` (reste son propre repo).
Dépend du service `temporal` déjà défini dans `wex-addon-services-platform`.

### 3a. Image Docker publiée

- [ ] Construire et pousser `syrtis/notification-dispatcher:<version>`
- [ ] Vérifier que l'image fonctionne sans mount (packages installés, pas editable)
- [ ] CI : automatiser à chaque release

### 3b. Définition du service wex

```
services/notification-dispatcher/
  service.yml
  docker/
    docker-compose.yml
    docker-compose.dev.yml
  app_service.py                # si besoin (répertoires de logs, etc.)
```

- [ ] `service.yml` :
  - tags : `[utility, notification, temporal]`
  - dependencies : `[temporal]`
  - vars : `DISPATCHER_PORT` (default 8000), `TEMPORAL_HOST`
  - install_config : injecter `DISPATCHER_URL` dans l'env de l'app
- [ ] `docker/docker-compose.yml` :
  - image publiée, port, env `TEMPORAL_HOST`
- [ ] `docker/docker-compose.dev.yml` :
  - image develop + volume source
- [ ] Vérifier que la dépendance `temporal` est résolue automatiquement par wex
  (même patron que rocketchat → mongo)

---

## Phase 4 — Mécanisme d'override local-dev

Permet de monter le code source au lieu de l'image, sans toucher la définition
du service ni la config de l'app.

- [ ] Définir la convention de l'override :
  - dans `.wex/env/local/config.yml` de l'app :
    ```yaml
    service:
      pdf-generator:
        dev: true                      # active docker-compose.dev.yml
        source_path: /chemin/absolu    # ou via env var
    ```
  - le `AppAddonManager` (ou le service resolver) fusionne `docker-compose.dev.yml`
    par-dessus `docker-compose.yml` si `dev: true`
- [ ] Implémenter la logique de fusion dans le résolveur de services
  (chercher `docker-compose.dev.yml` si le flag est actif)
- [ ] Documenter la procédure dans le service.yml (section `dev_override`)
- [ ] Tester hot-reload en modifiant un fichier Python du pdf-generator pendant
  que bdo-letters tourne

---

## Phase 5 — Migration bdo-letters

- [ ] Ajouter `wex-addon-services-syrtis` aux addons de l'env bdo-letters
- [ ] Déclarer les services dans `.wex/config.yml` de bdo-letters :
  ```yaml
  service:
    pdf-generator: {}
    notification-dispatcher: {}
  ```
- [ ] Supprimer les références hardcodées dans `.wex/docker/docker-compose.yml`
  de bdo-letters (les services sont maintenant injectés par wex)
- [ ] Vérifier que `PDF_GENERATOR_URL` et `DISPATCHER_URL` sont bien injectés
  dans l'env du container applicatif
- [ ] Tester le flux complet en mode image (prod-like)
- [ ] Tester le flux avec override dev pour pdf-generator
- [ ] Supprimer les anciens docker-compose des projets utilitaires si redondant

---

## Points ouverts

- **Versionnage des images** : décider si la version de l'image suit le semver du
  repo Python ou est découplée
- **Temporal déjà présent** : vérifier que le service `temporal` de
  `wex-addon-services-platform` est compatible avec notification-dispatcher
  (même version du client temporalio)
- **Source path en dev** : `PROGRAM_PUBLICATION_SOURCE_LIBRARY_PATH` peut servir
  de base pour déduire le chemin source automatiquement si la convention est
  respectée (`$BASE/SYRTIS/project/utilities/<name>`)
