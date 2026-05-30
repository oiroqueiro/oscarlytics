# Skills

This document outlines the technical skills and technologies used in the **Portfolio 2.0** project. Agents use these skills to perform their tasks effectively.

## 1. Python Development
**Description:** Proficiency in modern Python development.
**Related Files:** `apps/portfolio/`, `pyproject.toml`
**Capabilities:**
- dependency management (pip/poetry approaches implied by `pyproject.toml`).
- Writing clean, type-hinted Python 3.12+ code.
- Scripting and automation.

## 2. Podman & Quadlet
**Description:** Container orchestration using Podman and Systemd (Quadlet).
**Related Files:** `infra/*.kube`, `infra/*.yaml`, `infra/*.volume`
**Capabilities:**
- Creating and managing Podman containers and Pods.
- Writing Quadlet files for systemd integration.
- Managing container networks and volumes (using `z` for SELinux).
- Implementing UID mapping (`keep-id`) for rootless bind mounts.
- Troubleshooting container startup issues via `journalctl`.

## 3. PostgreSQL Management
**Description:** Database administration for the Postgres backend.
**Related Files:** `infra/portfolio.yaml` (DB container def)
**Capabilities:**
- Configuring PostgreSQL containers.
- SQL query writing and optimization.
- Database backup and recovery strategies.
- Schema management.

## 4. Bash Automation
**Description:** Shell scripting for project setup and maintenance.
**Related Files:** `scripts/setup.sh`
**Capabilities:**
- Writing robust bash scripts.
- Using `envsubst` for template generation.
- Automating setup and teardown workflows.

## 5. Meilisearch & Hardening
**Description:** Building and configuring secure-by-default search services.
**Related Files:** `infra/Containerfile.meilisearch`, `infra/portfolio.yaml`
**Capabilities:**
- Building hardened images via multi-stage builds and Wolfi.
- Managing production security keys (32-character Hex).
- Configuring non-root services in rootless environments.