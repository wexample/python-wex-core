# Roadmap : transformer les utilitaires Python en services wex

## Contexte

`pdf-generator` et `notification-dispatcher` sont des projets Python indépendants
exposés en HTTP, actuellement consommés par `bdo-letters` via Docker DNS + env vars.

**Objectif final** : les enregistrer comme services wex réutilisables dans
`wex-addon-services-platform` (aux côtés de temporal, n8n, ollama…).
Les repos sources restent indépendants.

---

## Phase 1 — Publication des images Docker en CI/CD

Chaque utilitaire doit produire une image publiée de manière autonome, sans
intervention manuelle.

### pdf-generator

- [ ] Vérifier que `Dockerfile.base` produit une image autonome (sans mount)
- [ ] Ajouter pipeline CI/CD sur le repo `pdf-generator` :
  build + push `syrtis/pdf-generator:<version>` au registry à chaque release
- [ ] Vérifier que la version de l'image suit le semver du `pyproject.toml`

### notification-dispatcher

- [ ] Vérifier que `Dockerfile.base` produit une image autonome
- [ ] Ajouter pipeline CI/CD sur le repo `notification-dispatcher` :
  build + push `syrtis/notification-dispatcher:<version>` à chaque release
- [ ] Vérifier compatibilité version `temporalio` avec le service `temporal`
  déjà défini dans `wex-addon-services-platform`

---

## Phase 2 — Configuration locale (mount + hot-reload)

Définir comment chaque utilitaire tourne en local de façon éditable,
indépendamment de toute intégration wex.

### Pattern commun

- [ ] `Dockerfile.develop` : image avec watchdog + install editable (`pip install -e .`)
- [ ] `docker-compose.dev.yml` : monte le source en volume, utilise Dockerfile.develop
- [ ] Documenter la variable source : `PDF_GENERATOR_SOURCE_PATH` /
  `DISPATCHER_SOURCE_PATH` (ou déduire depuis `PROGRAM_PUBLICATION_SOURCE_LIBRARY_PATH`)
- [ ] Valider hot-reload : modifier un fichier `.py` → redémarrage automatique du serveur

### pdf-generator

- [ ] S'assurer que `docker/docker-compose.dev.yml` est opérationnel en standalone
- [ ] Tester `GET /generate/<job>` après modification à chaud d'un bloc Python

### notification-dispatcher

- [ ] S'assurer que `docker/docker-compose.dev.yml` est opérationnel en standalone
- [ ] Tester le flux workflow Temporal après modification à chaud

---

## Phase 3 — Évaluer et consolider le pattern "apps voisines" (bdo-letters)

Avant de faire des services wex, décider si le pattern actuel (deux projets
distincts que bdo-letters consomme via env var + Docker DNS) est une façon de
travailler reconnue et supportée.

### Analyse

- [ ] Documenter le pattern "app voisine" : chaque utilitaire est lancé
  indépendamment, bdo-letters pointe dessus via `PDF_GENERATOR_URL` /
  `DISPATCHER_URL`
- [ ] Vérifier que ce pattern fonctionne proprement en local :
  - les trois stacks tournent en parallèle sans conflit réseau
  - bdo-letters trouve les services par leur URL configurée
  - modifier pdf-generator à chaud ne nécessite pas de redémarrer bdo-letters
- [ ] Vérifier le comportement en prod : pas de hot-reload, images figées, URLs
  pointant vers des endpoints stables

### Décision

- [ ] Si le pattern "apps voisines" est viable → le documenter comme mode de
  travail officiel et s'assurer qu'il reste supporté après passage en services wex
- [ ] Identifier ce qui manque aujourd'hui pour que ce pattern soit confortable
  (scripts de lancement, commande wex `app::start --with pdf-generator`, etc.)

---

## Phase 4 — Définir les services wex dans wex-addon-services-platform

Une fois les images stables et le pattern local validé, enregistrer chaque
utilitaire comme service wex aux côtés de temporal, n8n, ollama…

```
wex-addon-services-platform/src/.../services/
  pdf-generator/
    service.yml
    docker/
      docker-compose.yml        # image publiée
      docker-compose.dev.yml    # mount source + watchdog
    app_service.py              # contribution workdir : répertoire jobs/
  notification-dispatcher/
    service.yml
    docker/
      docker-compose.yml
      docker-compose.dev.yml
```

### pdf-generator

- [ ] `service.yml` : tags `[utility, pdf]`, vars `PDF_GENERATOR_PORT`,
  `PDF_GENERATOR_JOBS_PATH`, install_config pour `PDF_GENERATOR_URL`
- [ ] `docker/docker-compose.yml` : image publiée, port, volume jobs/
- [ ] `docker/docker-compose.dev.yml` : image develop + volume source
- [ ] `app_service.py` : `get_workdir_contribution` assure que `jobs/` existe

### notification-dispatcher

- [ ] `service.yml` : tags `[utility, notification]`, `dependencies: [temporal]`,
  vars `DISPATCHER_PORT`, install_config pour `DISPATCHER_URL`
- [ ] `docker/docker-compose.yml` : image publiée, port, env `TEMPORAL_HOST`
- [ ] `docker/docker-compose.dev.yml` : image develop + volume source

### Mécanisme d'override dev

- [ ] Définir la convention dans l'env local de l'app :
  ```yaml
  # .wex/env/local/config.yml
  service:
    pdf-generator:
      dev: true
      source_path: /chemin/absolu/pdf-generator
  ```
- [ ] Implémenter la fusion `docker-compose.dev.yml` dans le service resolver
  si le flag `dev: true` est actif
- [ ] Tester hot-reload depuis bdo-letters avec le service wex en mode dev

---

## Phase 5 — Migration bdo-letters vers les services wex

- [ ] Déclarer les services dans `.wex/config.yml` de bdo-letters :
  ```yaml
  service:
    pdf-generator: {}
    notification-dispatcher: {}
  ```
- [ ] Supprimer les références hardcodées aux utilitaires dans le docker-compose
  de bdo-letters (injectés automatiquement par wex)
- [ ] Vérifier que `PDF_GENERATOR_URL` et `DISPATCHER_URL` sont injectés
  dans l'env du container applicatif
- [ ] Tester le flux complet en mode image (prod-like)
- [ ] Tester avec override dev pour pdf-generator (bdo + pdf-generator modifiable)
- [ ] Nettoyer les anciens configs si redondants
