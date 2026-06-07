"""Domain tags exposed by this addon — one entry per `domain:*` value its commands use."""

from __future__ import annotations


class DomainTag:
    """Functional domain this addon's commands touch."""

    CODE_GEN = "domain:code-gen"
    CORE = "domain:core"
    DEMO = "domain:demo"
    ENV = "domain:env"
    GIT = "domain:git"
    HTTP = "domain:http"
    INTROSPECTION = "domain:introspection"
    PACKAGE = "domain:package"
    REGISTRY = "domain:registry"
    RELEASE = "domain:release"
    WEBHOOK = "domain:webhook"
