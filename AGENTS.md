# AGENTS.md — Portfolio 2.0

> This document defines the project vision, migration status, security rules, and specialized agents. Read it in full before performing any action.

---

## 🧭 Project Vision & Objectives
**Vision:** Evolve the portfolio platform into a security-first, high-performance infrastructure using rootless Podman and hardened distroless environments.

**Key Objectives:**
- **Infrastructure:** Full migration from Docker to **Podman + Quadlets**.
- **Search Engine:** Replace Elasticsearch with **Meilisearch** for resource efficiency.
- **Hardening:** Use **Wolfi/Chainguard** (distroless) images to minimize attack surface.
- **Environment:** Use a `setup.sh` script to manage paths via symlinks and `.env` files.

---

## 🏗️ Infrastructure Migration Map

| Component | v1.0 (Docker - Prod) | v2.0 (Podman - Target) | Status |
| :--- | :--- | :--- | :--- |
| **Runtime** | Docker Engine | **Podman (Rootless)** | ✅ Active |
| **Orchestration** | Docker Compose | **Quadlets (Systemd - 1 Pod)** | ✅ Active |
| **App Portfolio** | Python + Flask | Python + Flask (**Wolfi**) | ✅ Active |
| **Database** | PostgreSQL | PostgreSQL (**Hardened**) | ✅ Active |
| **Search Engine** | Elasticsearch | **Meilisearch (Hardened)** | ✅ Active |
| **Network** | Docker bridge | Podman network (**portfolio**) | ✅ Active |

---

## 👥 Specialized Agents

This document defines the specialized agents available for the **Portfolio 2.0** project. Each agent has a specific role and set of responsibilities tailored to the project's architecture (Python, Podman/Quadlet, Postgres).

### 1. Principal Architect
**Role:** Project Lead & Orchestrator
**Context:** Understands the entire system architecture, from the Python application code to the Podman infrastructure.
**Responsibilities:**
- Coordinate between other agents.
- Maintain `task.md` and ensure project goals are met.
- Make high-level architectural decisions.
- Manage cross-component integrations (e.g., App connecting to DB via Quadlet network).

### 2. Backend Developer
**Role:** Python Application Developer
**Context:** Focuses on the `apps/` directory and Python scripts.
**Responsibilities:**
- Develop and maintain Python application code.
- Manage dependencies via `pyproject.toml`.
- Write unit tests and ensure code quality.
- Implement business logic and API endpoints.

### 3. Infrastructure Engineer
**Role:** DevOps & System Administrator
**Context:** Focuses on the `infra/` directory and `scripts/`.
**Responsibilities:**
- Manage Podman containers and Quadlet configuration files (`.kube`, `.yaml`, `.volume`, `.network`).
- Maintain consolidated Pod structure in `infra/portfolio.yaml`.
- Maintain generation scripts (`scripts/setup.sh`) for environment management.
- Ensure systemd integration works correctly.
- Handle networking and volume persistence.

### 4. Database Administrator
**Role:** Data Manager
**Context:** Focuses on Persistence and Data Integrity.
**Responsibilities:**
- Manage the PostgreSQL database configuration (`infra/portfolio.yaml`).
- Handle database migrations and schema design.
- Ensure data persistence acts as expected with Podman volumes (`infra/portfolio_db.volume`).
- Optimize database performance.

---

## 🔐 Mandatory Security Rules (Guiding Principles)
1. **Human Confirmation:** Never execute destructive commands (`rm -rf`, `podman rm`, `systemctl stop`) or perform `git push` without explicit user permission.
2. **Secrets Management:** No hardcoded credentials. Refer to unversioned `.env` or `PATHS.md` files via `EnvironmentFile=`.
3. **Wolfi Philosophy:** No runtime package installations (e.g., `apk add`). All dependencies must be baked into the image.
4. **Quadlet Standards:** Every container must use `NoNewPrivileges=true`, `ReadOnlyRootFilesystem=true` (when possible), and `DropCapabilities=ALL`.