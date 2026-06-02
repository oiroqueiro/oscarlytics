---
title: "Portfolio 2.0: Hardened Podman & Quadlet Infrastructure"
language: en
date: 2026-06-02
project_n: 1
keywords: "podman, quadlet, security, postgresql, meilisearch, nginx, ssl, acme, cloud, devops, hardening"
image_title: "project07"
image1: ""
image2: ""
image3: ""
image4: ""
image5: ""
link1: "https://github.com/oiroqueiro/portfolio"
---

## Resume
Evolution and migration of my portfolio infrastructure (Oscarlytics) from a legacy Docker Engine and Elasticsearch environment to a high-security, resource-optimized, and unprivileged (rootless) ecosystem using Podman and systemd-integrated Quadlets, achieving a 90% reduction in memory usage.

## Exposition
After running version 1.0 of Oscarlytics for several years, I decided to pivot it into a personal systems and data lab. However, the original stack presented several challenges:

1. **High resource footprint:** Running Elasticsearch, despite its excellent index search capabilities, required a baseline memory usage of 1.5 GB to 2.5 GB RAM. For a budget VPS, this left virtually no room for other experiments.
2. **Security & Privileges:** The entire Docker Engine daemon ran as `root`, meaning container breakouts could compromise the host operating system.
3. **Configuration overhead:** Using Excel spreadsheets to manage project texts and articles made updates tedious and completely offline.

For this refactoring, I decided to define the architecture and strict standards myself, delegating the heavy lifting to my autonomous coding agent **Gemini (Antigravity)**.

<img src="/static/img/projects/htop_pre_migration.png" class="img-fluid w-100" alt="htop pre"></img>
*Fig 1. Screenshot showing memory and CPU usage (htop) on the previous Docker & Elasticsearch stack.*

<img src="/static/img/projects/docker_stats_pre.png" class="img-fluid w-100" alt="docker stats pre"></img>
*Fig 2. Container stats on the original Docker-based system.*

## Action
To migrate to the 2.0 stack, we implemented the following system engineering changes:

1. **Replaced Elasticsearch with Meilisearch:** Switched the search backend to Meilisearch. Being a lightweight, ultra-fast search engine written in Rust, we preserved rapid project search capabilities while reducing RAM usage to a tiny fraction.
2. **Migrated from Excel to Dynamic Markdown:** Excel files were completely eliminated. Content is now authored in Markdown (`.md`) files with Frontmatter. A startup Python script automatically parses and syncs these posts into the database and Meilisearch index.
3. **User-space Orchestration via Podman Quadlets:** Replaced the legacy `docker-compose` setup with Podman Quadlets, integrated natively as systemd services. The pod runs isolated and without root privileges.
4. **Hardened Container Configuration:** Implemented strict hardening rules on each container:
   - Configured `NoNewPrivileges=true` and `DropCapabilities=ALL` to prevent privilege escalations.
   - Mounted the Nginx and Flask filesystems as read-only (`ReadOnlyRootFilesystem=true`).
   - Sourced clean and secure base images (Chainguard/Wolfi and minimal Alpine).
5. **ACME.sh Sidecar Automation:** Placed ACME.sh in a helper container using the DuckDNS DNS-01 validation challenge, generating SSL certs automatically without needing to bind host ports 80/443.

<img src="/static/img/projects/podman_stats_post.png" class="img-fluid w-100" alt="podman stats post"></img>
*Fig 3. Podman stats on version 2.0, showing a massive memory reduction.*

<img src="/static/img/projects/htop_post_migration.png" class="img-fluid w-100" alt="htop post"></img>
*Fig 4. System load averages on the new Podman stack.*

## Resolution
The migration to Portfolio 2.0 has been a resounding success, delivering the following measurable results:
- **90% RAM reduction:** The entire stack idle usage dropped from ~1.8 GB to **under 190 MB RAM**.
- **Rootless operation:** All containers and host service daemons run in user-space without sudo.
- **Fast Search Indexing:** Meilisearch query times are in single-digit milliseconds, and CPU usage on the VPS host is near 0.1% at idle.

<img src="/static/img/projects/free_h_post.png" class="img-fluid w-100" alt="free -h post"></img>
*Fig 5. Detail of host memory usage on the VPS with the new stack actively running.*

This project showcases how to design self-managed, hardened, and highly efficient stacks. The source code and templates are available at [My Github](https://github.com/oiroqueiro/portfolio).
