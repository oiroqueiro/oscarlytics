# 🚀 Portfolio 2.0: The Hardened Stack

## 🤖 Reflexiones sobre IA y el Desarrollo
> *[Tu perspectiva personal aquí: Puedes usar este espacio para contar cómo ha sido tu experiencia construyendo y refactorizando esta aplicación desde cero en colaboración con un Agente de IA (Antigravity). ¡El escenario es tuyo!]*

A state-of-the-art, high-performance, and **secure-by-design** portfolio infrastructure. This version represents a complete evolution from legacy Docker/Elasticsearch setups to a modern, rootless **Podman** architecture managed via **Quadlets**.

## 📖 History & Background (The Path from Zero to 2.0)

This project began as a journey from zero knowledge of web development to a fully containerized professional deployment. It stands as a testament to **determination, creative problem solving, and adaptability**. I am not originally a UX/Designer or a Web Developer, but I wanted a portfolio that had specific features: Multi-language, Responsive, Light/Dark mode, Customizable, Containerized, and with an Index Search. 

### Portfolio 1.0 (The Foundation)
I started by adapting a static Hugo template into a dynamic website using **Python and Flask**. 
To make it customizable, I initially used an Excel file to store all the texts and content. For the database, I started with SQLite and evolved to **PostgreSQL**. To power the search functionality, after experimenting with basic SQL queries, I implemented **Elasticsearch**.
Finally, I containerized the whole application with **Docker**, configuring 4 containers (Postgres, Elastic, App, Nginx) and deploying them to a VPS using **Let's Encrypt** for an A-grade SSL certificate.

### Portfolio 2.0 (The Hardened Evolution)
Portfolio 2.0 takes all the lessons learned and upgrades the entire ecosystem to modern, secure, and highly efficient standards:
- **Migration of Data**: Excel was completely removed. Content is now managed entirely through dynamic **Markdown (.md)** files with Frontmatter, loaded on startup and allowing rich media embedding.
- **Search Engine Upgrade**: Elasticsearch was replaced by **Meilisearch**, which is drastically lighter, faster, and more resource-efficient for this scale.
- **Maximum Security (Hardened Images)**: The containers are now built using **Wolfi/Chainguard** distroless images, meaning they contain zero unnecessary binaries (not even a shell), reducing the attack surface to a minimum.
- **Rootless Podman & Quadlets**: The entire stack dropped `docker-compose` in favor of **Podman Quadlets**. It runs entirely in user-space (rootless) and integrates natively with Linux `systemd`. No orchestrator needed; the pods run like any other OS daemon.
- **High Performance Nginx & SSL**: Nginx is hardened, and SSL is automatically handled via a sidecar `acme.sh` container using the DuckDNS DNS-01 challenge, ensuring a Grade-A certificate without downtime.

---

## 🛡️ Key Security Pillars

### 1. Minimalist Wolfi Images
Zero unnecessary binaries, reduced attack surface. No `apk`, no shell access in production.

### 2. Rootless Operation
The entire stack runs in user-space without `sudo` requirements.

### 3. Secret Management
Zero-leak policy. Sensitive data is injected via `.env` and templated in manifests `${VAR}` using `envsubst`. Generated quadlets are ignored by `.gitignore`.

### 4. Network Isolation
Dedicated pod network namespace, isolated from the host and other pods. All containers inside the pod communicate via localhost.

---

## 📁 Project Structure & Data Paths (Where to put your files)

To make updating your portfolio as easy as possible, it is essential to understand where files live, both while developing locally and once deployed in production.

```text
├── apps/portfolio/       # 🐍 Flask Application Logic & Source Code
│   ├── content/          
│   │   ├── content.yaml  # 📝 Static texts (menus, about me, translations)
│   │   └── projects/     # 📄 LOCAL Markdown files (.md)
│   ├── portfolio/
│   │   └── static/
│   │       └── img/      # 🖼️ LOCAL Images
│   └── sync_projects.py  # 🔄 The magic script that reads the .md files
│
├── infra/                # 🏗️ Infrastructure-as-code
│   ├── .env              # 🔐 Secrets (Passwords, DuckDNS, Database URLs)
│   ├── portfolio.yaml    # 📦 Kubernetes-style Podman manifest
│   └── Containerfiles    # 🐳 Dockerfiles for hardened Wolfi images
│
├── scripts/              # 🤖 Automation & Setup utilities
│   ├── build_and_push.sh # Compiles images and pushes them to GitHub
│   ├── deploy_prod.sh    # Deploys the infrastructure on your VPS
│   └── setup.sh          # Builds and runs everything locally for testing
│
└── data/                 # 🗄️ Persistent volumes (Created automatically, ignored by Git)
    ├── portfolio_img/    # 🖼️ PRODUCTION Images (SFTP here)
    ├── portfolio_storage/# 📄 PRODUCTION Markdown files (SFTP inside /projects)
    ├── portfolio_db/     # PostgreSQL database binary data
    └── meilisearch_data/ # Meilisearch search indexes
```

### 💻 Local Testing vs 🌍 Production
There is a big difference between testing on your computer and deploying on your VPS:

**1. Testing Locally (Your Computer):**
- **Markdown (.md)**: Place your projects inside `apps/portfolio/content/projects/`.
- **Images**: Place your images inside `apps/portfolio/portfolio/static/img/projects/`.
- **Why?**: When you run `./scripts/setup.sh`, the system will compile the application and the `sync_projects.py` script will automatically read from these folders and populate your local database. *Note: Git is configured to ignore your personal files so they won't accidentally be pushed to GitHub.*

**2. Production (Your VPS):**
- **Markdown (.md)**: Upload your files via SFTP to `~/portfolio_2.0/data/portfolio_storage/projects/`.
- **Images**: Upload your images via SFTP to `~/portfolio_2.0/data/portfolio_img/projects/`.
- **Why?**: In production, the source code (`apps/`) doesn't exist on the server. The containers pull the application image from GitHub and mount the `data/` folder as persistent volumes. When the container restarts, it reads the `.md` files directly from the `data/` folder!

---

## 🛠️ Deployment Workflows

This architecture separates the building process from the production deployment using a Container Registry (e.g., GitHub Container Registry).

### 1. Local Development (All-in-one)
If you just cloned the repository to test it locally:
```bash
cp infra/env.example infra/.env
# Edit infra/.env with your dev tokens
chmod +x scripts/setup.sh
./scripts/setup.sh
```
*Your local `.md` files in `apps/portfolio/content/projects/` will be automatically synced to the database on startup!*

### 1.1 Local Iteration (Fast Rebuild)
If you are developing locally and want to test changes made to application files (like `HTML` templates, `CSS`, or the `content.yaml` file), you can quickly rebuild the app image and restart the pod without tearing down the entire environment:
```bash
chmod +x scripts/rebuild_app.sh
./scripts/rebuild_app.sh
```
*Note: This is only needed for files baked into the image (source code). Markdown files and images in `data/` update instantly.*

### 2. Build & Push to Registry
When you have a new version ready to release, build it and push it to GHCR:
```bash
# Ensure GHCR_REGISTRY in your infra/.env points to: ghcr.io/your-username
chmod +x scripts/build_and_push.sh
./scripts/build_and_push.sh
```

### 3. Pure Production Deployment (No Source Code)
On the production server, you don't need to clone the full repository. You only need the `infra/` folder, the `.env` file, and the deployment script:
```bash
chmod +x scripts/deploy_prod.sh
./scripts/deploy_prod.sh
```
*Podman will automatically download the hardened images from your registry and set up the systemd services.*

### 4. Upload Content (Production)
Log into the application as an admin using the credentials you defined in `.env`.
Go to the **Admin Dashboard** and use the **Upload Markdown Project** feature to easily upload your `.md` projects. Alternatively, upload them via SFTP to the `data/portfolio_storage/projects/` folder and they will be indexed automatically on startup.

## ✍️ Writing Content (The Markdown Manual)

Portfolio 2.0 uses Markdown for project content, completely replacing the old Excel-based approach. The system automatically reads, parses, and loads `.md` files on startup.

### 1. Naming Convention
Files must follow this exact format:
`YYYY-MM-DD-lang-projectname.md`
- **YYYY-MM-DD**: Release date (e.g., `2024-01-01`).
- **lang**: Two-letter language code (`es` or `en`).
- **projectname**: Any descriptive slug (e.g., `my-cool-project`).

*Example:* `2024-02-23-es-portfolio_2.0.md`

### 2. Frontmatter (Metadata)
Every `.md` file MUST start with a YAML block (Frontmatter) enclosed in `---`. This replaces the columns of the old Excel file.
```yaml
---
title: "Módulo de Gestión de Contenido en MarkDown"
language: es
date: 2024-02-23
project_n: 1
keywords: python, flask, markdown, seo
image_title: portfolio_admin
image1: mockup_admin_panel.png
link1: https://github.com/roque/nuevo_portfolio
---
```
- **project_n**: Number of the project if multiple released on the same date.
- **image1, image2, image3**: Names of the images stored in `apps/portfolio/portfolio/static/img/projects/` (or `data/portfolio_img/projects/` in production). Don't include the full path, just the filename (e.g., `my_image.webp`).

### 3. Writing the Content (Body)
Below the second `---`, you write your project description using standard Markdown and/or HTML.

**Formatting Text:**
Use standard Markdown for `**bold**`, `*italics*`, `[links](http...)`, and `## headings`. The system automatically renders this beautifully while maintaining SEO hierarchy.

**Embedding Images:**
Because we allow raw HTML mixed with Markdown, you can embed your project images dynamically within the text! Use the `<img>` tag and point to the static folder:
```html
<img src="/static/img/projects/mockup_admin_panel.png" alt="Admin Panel"></img>
*Fig 1. Captura del nuevo panel*.
```

**Embedding Videos:**
You can directly paste YouTube/Vimeo iframes:
```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/XXXXXX" frameborder="0" allowfullscreen></iframe>
```

---

## 📊 Management Commands

| Action | Command |
| :--- | :--- |
| **Status** | `systemctl --user status portfolio` |
| **Logs** | `podman logs -f portfolio-app` |
| **Restart App** | `systemctl --user restart portfolio` |

---
*Developed by Gemini Pro Agents. Managed by Oscar Iglesias Roqueiro*
