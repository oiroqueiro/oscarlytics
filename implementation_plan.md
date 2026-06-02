# Plan de Implementación: Migración y Despliegue de Oscarlytics (Portfolio 2.0)

Este documento presenta el plan de migración paso a paso para desplegar **Oscarlytics (Personal Data Lab)** en tu VPS de producción, garantizando la seguridad, la persistencia de datos (cero pérdida de datos), un rendimiento sobresaliente y la integración del stack de monitorización local.

---

## 🧭 Resumen del Objetivo
Evolucionar la plataforma actual hacia **Oscarlytics (Personal Data Lab)**, migrando desde la versión 1.0 (Docker Compose, base de datos Postgres clásica, motor de búsqueda pesado Elasticsearch, configuración manual) hacia la versión 2.0 (Podman rootless con Quadlets, imágenes minimalistas endurecidas de Wolfi, Meilisearch y automatización de certificados SSL/TLS vía acme.sh). El directorio final en el servidor de producción será `~/oscarlytics`.

---

## 📑 Índice de Fases del Plan

1. [Fase 1: Copia de Seguridad de Portfolio 1.0 (VPS Producción)](#fase-1-copia-de-seguridad-de-portfolio-10-vps-producción)
2. [Fase 2: Benchmark de Rendimiento de la Versión 1.0](#fase-2-benchmark-de-rendimiento-de-la-versión-10)
3. [Fase 3: Análisis de Eliminación y Sustitución de Componentes](#fase-3-análisis-de-eliminación-y-sustitución-de-componentes)
4. [Fase 4: Compilación y Subida de Imágenes Endurecidas a GHCR](#fase-4-compilación-y-subida-de-imágenes-endurecidas-a-ghcr)
5. [Fase 5: Auditoría de Seguridad y Preparación de Repositorio para GitHub](#fase-5-auditoría-de-seguridad-y-preparación-de-repositorio-para-github)
6. [Fase 6: Guía Paso a Paso de Transferencia y Migración de Datos](#fase-6-guía-paso-a-paso-de-transferencia-y-migración-de-datos)
7. [Fase 7: Guía de Despliegue de Oscarlytics (VPS)](#fase-7-guía-de-despliegue-de-oscarlytics-vps)
8. [Fase 8: Benchmark de Rendimiento de Oscarlytics](#fase-8-benchmark-de-rendimiento-de-oscarlytics)
9. [Fase 9: Puesta en Marcha del Stack de Control y Monitorización](#fase-9-puesta-en-marcha-del-stack-de-control-y-monitorización)
10. [Fase 10: Sugerencias Cruciales para Prevenir Fallos](#fase-10-sugerencias-cruciales-para-prevenir-fallos)

---

## Fase 1: Copia de Seguridad de Portfolio 1.0 (VPS Producción)

Para garantizar la seguridad total de la información actual y poder restaurar todo si ocurriese cualquier imprevisto, realizaremos un backup exhaustivo de la versión 1.0.

### 1. Copia de Seguridad de la Base de Datos (PostgreSQL)
Ejecuta el siguiente comando en tu VPS para volcar la base de datos de producción a un archivo SQL legible:
```bash
# Entrar al contenedor de Postgres actual y volcar la BD
docker exec -t <nombre_contenedor_postgres_old> pg_dump -U <usuario_db_old> -d <nombre_db_old> > ~/portfolio1.0_backup_db.sql
```
*Si no recuerdas el nombre del contenedor o las credenciales, puedes buscarlos ejecutando `docker ps` y visualizando tu archivo `docker-compose.yml` actual.*

### 2. Copia de Seguridad de las Imágenes y Archivos Multimedia
Es fundamental copiar las imágenes del portfolio que subiste en producción (como imágenes de proyectos, logos, etc.):
```bash
# Empaquetar la carpeta de almacenamiento de medios de Portfolio 1.0
tar -czvf ~/portfolio1.0_backup_media.tar.gz -C /ruta/a/tus/imagenes/en/vps .
```

### 3. Copia de Seguridad de la Configuración y Certificados
```bash
# Guardar el docker-compose.yml y el archivo .env actual
mkdir -p ~/portfolio1.0_config_backup
cp /ruta/a/portfolio1.0/docker-compose.yml ~/portfolio1.0_config_backup/
cp /ruta/a/portfolio1.0/.env ~/portfolio1.0_config_backup/

# Opcional: Hacer backup de los certificados de Let's Encrypt antiguos
tar -czvf ~/portfolio1.0_backup_certs.tar.gz -C /etc/letsencrypt .
```

### 4. Descargar los Backups al Equipo Local
Desde tu terminal local, descarga de forma segura todos los archivos generados:
```bash
# Ejecutar localmente para descargar los archivos mediante rsync o scp
mkdir -p ~/backups_portfolio_prod
rsync -avz -e "ssh" usuario@tu_vps:~/portfolio1.0_backup_* ~/backups_portfolio_prod/
```
> [!IMPORTANT]
> **Regla de oro de backups:** No detengas el servicio de Portfolio 1.0 hasta haber verificado visualmente que el archivo `portfolio1.0_backup_db.sql` tiene contenido y que el tar.gz de imágenes se abre correctamente en tu equipo local.

---

## Fase 2: Benchmark de Rendimiento de la Versión 1.0

Antes de migrar, analizaremos el rendimiento de la VPS ejecutando la v1.0 para tener un punto de partida numérico claro de latencias y consumo de recursos.

### 1. Métricas de Consumo del Servidor (Durante carga pasiva y activa)
Ejecuta en tu VPS durante el benchmark:
```bash
# Consumo de CPU/Memoria global del servidor
htop
# Consumo por contenedor Docker
docker stats --no-stream
```
*Toma nota de la memoria RAM consumida por Elasticsearch (suele rondar de 1GB a 2.5GB de RAM) y el contenedor de Flask.*

### 2. Prueba de Carga Externa (HTTP Benchmarking)
Utilizaremos `wrk` (o en su defecto `k6` / `ab`) desde tu ordenador local (o una máquina con buena conexión externa) apuntando a tu dominio de producción actual:
```bash
# Instalar wrk localmente si no lo tienes (Ubuntu/Debian: sudo apt install wrk)
# Ejecutar test de 30 segundos, con 12 hilos de ejecución y 400 conexiones concurrentes
wrk -t12 -c400 -d30s https://tudominio.com/
```
**Métricas críticas a registrar:**
- **Requests/sec (RPS):** Número de peticiones procesadas por segundo.
- **Latency (Avg/Max/Stdev):** Latencia de respuesta media.
- **P95 / P99 Latency:** El percentil 95 y 99 de respuestas (indica la experiencia del peor caso de usuario).
- **Socket errors:** Cantidad de peticiones fallidas por timeout o sobrecarga.

---

## Fase 3: Análisis de Eliminación y Sustitución de Componentes

La evolución a Oscarlytics limpia dependencias pesadas y las reemplaza por tecnologías punteras y optimizadas para rendimiento y seguridad:

| Elemento a Eliminar (v1.0) | Componente Sustituto (v2.0) | Beneficio y Funcionalidad Aprovechada |
| :--- | :--- | :--- |
| **Hojas de cálculo Excel** | **Archivos Markdown (.md) + Frontmatter YAML** | Se elimina la dependencia de librerías de lectura complejas de Excel. Los archivos `.md` facilitan el formateo enriquecido directamente, admiten bloques de código con sintaxis resaltada e inserción nativa de HTML e imágenes. Se indexan directamente en la base de datos al arrancar mediante `sync_projects.py` y se pueden gestionar visualmente en el Admin Dashboard. |
| **Docker Engine & Daemon de root** | **Podman Rootless + Quadlets** | El stack corre enteramente en espacio de usuario sin privilegios de `sudo`. El demonio de Docker (vector de ataque clásico) se sustituye por unidades nativas de **Systemd**. Se aprovecha el control de ciclo de vida nativo de Linux (`systemctl --user start/stop`). |
| **Elasticsearch** | **Meilisearch (Endurecido)** | Reducción de consumo de RAM abismal (de ~1.5GB a ~60MB). Respuestas ultra rápidas con tolerancia a erratas de escritura (Typo-Tolerance), ordenamiento personalizado y filtros nativos. |
| **Imágenes Debian/Alpine clásicas** | **Wolfi/Chainguard Distroless** | Reducción de vulnerabilidades de seguridad a 0. No hay intérpretes de shell (`sh`, `bash`), ni gestores de paquetes (`apk`, `apt`), ni utilidades de red innecesarias en ejecución. Si un atacante entrase al contenedor, no puede ejecutar comandos ni descargar exploits. |
| **Certbot en host** | **Contenedor Sidecar `acme-sh` + DuckDNS** | Los certificados se generan automáticamente mediante la validación DNS-01 (DuckDNS), lo que evita abrir puertos extras en la VPS para la validación HTTP de Let's Encrypt y elimina micro-cortes durante la renovación. |

---

## Fase 4: Compilación y Subida de Imágenes Endurecidas a GHCR

El despliegue de Oscarlytics utiliza el GitHub Container Registry (GHCR) para alojar tus versiones endurecidas.

### 1. Iniciar Sesión en GHCR desde tu Equipo Local
Necesitas un **Personal Access Token (PAT)** de GitHub con alcance `write:packages` y `read:packages`.
```bash
# Loguearse en el registro de paquetes de GitHub
podman login ghcr.io -u TU_USUARIO_GITHUB
# (Introduce tu Token de Acceso Personal cuando solicite el Password)
```

### 2. Configurar y Personalizar el Script de Compilación
En tu entorno de desarrollo, edita el archivo `infra/.env` y asegúrate de establecer el registro a tu cuenta:
```ini
GHCR_REGISTRY=ghcr.io/tu-usuario-github
```

### 3. Compilar y Subir las Imágenes
El script `scripts/build_and_push.sh` automatiza la compilación usando las Containerfiles personalizadas y realiza el push:
```bash
# Asegurar permisos y ejecutar
chmod +x scripts/build_and_push.sh
./scripts/build_and_push.sh
```
El script generará y subirá cuatro imágenes endurecidas:
- `ghcr.io/tu-usuario-github/portfolio-meilisearch:latest`
- `ghcr.io/tu-usuario-github/portfolio-app:latest`
- `ghcr.io/tu-usuario-github/portfolio-nginx:latest`
- `ghcr.io/tu-usuario-github/portfolio-acmesh:latest`

---

## Fase 5: Auditoría de Seguridad y Preparación de Repositorio para GitHub

Analizamos el estado actual del repositorio Git para asegurar una subida limpia, privada en datos sensibles y pública en código base.

### 1. Estado de la Auditoría del Repositorio
- **`.gitignore` (Correcto):** Excluye correctamente la carpeta `data/` (base de datos local, índices de Meilisearch, logs), el archivo `.env` con contraseñas, los archivos de Systemd generados dinámicamente (`infra/*.generated.*`), los entornos virtuales `.venv/` y tus proyectos reales en Markdown e imágenes en local (`apps/portfolio/content/projects/*.md`, etc.).
- **Limpieza de secretos:** El archivo `infra/env.example` está perfectamente configurado con valores de ejemplo y libre de claves reales.

### 2. Preparación para subir a GitHub
Actualmente, el repositorio local está inicializado pero no tiene ningún commit (visto en `git status`). Sigue estos pasos para subir tu primer commit de forma limpia:

```bash
# 1. Copiar los proyectos de ejemplo de la carpeta examples a la estructura del app
# Esto asegura que el repositorio clonado en cualquier máquina funcione al instante con datos dummy
cp examples/projects/*.md apps/portfolio/content/projects/
cp examples/img/example_project.png apps/portfolio/portfolio/static/img/projects/

# 2. Agregar los archivos rastreados al índice de Git
git add .

# 3. Comprobar que NO se añade ningún archivo privado (.env, datos reales)
git status

# 4. Crear el commit inicial
git commit -m "🚀 Initial Commit: Oscarlytics Personal Data Lab Quadlet Infrastructure"

# 5. Crear el repositorio en tu cuenta de GitHub (Público o Privado) y enlazarlo
git remote add origin https://github.com/tu-usuario-github/oscarlytics.git
git branch -M main
git push -u origin main
```

---

## Fase 6: Guía Paso a Paso de Transferencia y Migración de Datos

Esta sección describe cómo migrar tus datos actuales (imágenes, logos y posts históricos) al esquema de Oscarlytics en producción sin perder nada.

### 1. Migración de Proyectos en Markdown
*Dado que ahora usarás tus propios datos reales de Oscarlytics en producción, debes transferirlos directamente desde tu ordenador.*

1. **Ubicación en Producción:**
   En Oscarlytics, los archivos de producción se leen de forma externa al contenedor para no requerir compilar la imagen de nuevo al subir contenido.
   La ruta destino en tu VPS es:
   `~/oscarlytics/data/portfolio_storage/projects/`
2. **Transferencia de archivos:**
   Sube todos tus archivos de proyectos actuales `.md` que creaste en tu PC a la carpeta anterior mediante SFTP o usando rsync:
   ```bash
   # Ejecutar en tu máquina local
   rsync -avz -e "ssh" ~/03.\ Projects/06.portfolio_2.0/apps/portfolio/content/projects/ usuario@tu_vps:~/oscarlytics/data/portfolio_storage/projects/
   ```

### 2. Migración de Imágenes, Logos y Recursos Estáticos
1. **Ubicación en Producción:**
   Las imágenes finales en producción deben residir en la carpeta externa:
   `~/oscarlytics/data/portfolio_img/projects/`
2. **Transferencia de imágenes:**
   Sube tus imágenes personalizadas de proyectos y logos mediante rsync:
   ```bash
   # Ejecutar en tu máquina local
   rsync -avz -e "ssh" ~/03.\ Projects/06.portfolio_2.0/apps/portfolio/portfolio/static/img/projects/ usuario@tu_vps:~/oscarlytics/data/portfolio_img/projects/
   ```

### 3. Migración de Datos de la Base de Datos (Postgres)
No queremos perder configuraciones de administración ni contactos del formulario. Restauraremos la base de datos en el nuevo PostgreSQL endurecido (Chainguard).

> [!CAUTION]
> Asegúrate de que las credenciales de base de datos (`DB_NAME`, `DB_USER`, `DB_PASSWORD`) especificadas en tu archivo `infra/.env` de producción sean iguales o las registres correctamente para realizar la restauración.

Una vez que el nuevo stack de Podman esté en funcionamiento (Fase 7), importaremos los datos usando el backup que creamos en la **Fase 1**:
```bash
# 1. Copiar el backup SQL al servidor de producción en la carpeta temporal si no está ya
# 2. Ejecutar la restauración directamente inyectando el SQL en el contenedor Postgres rootless de Podman:
podman exec -i portfolio-db psql -U <tu_usuario_db_env> -d <nombre_db_env> < ~/portfolio1.0_backup_db.sql
```

---

## Fase 7: Guía de Despliegue de Oscarlytics (VPS)

Guía completa para implantar el nuevo stack e integrarlo con Systemd de forma limpia en tu VPS de producción bajo el directorio `~/oscarlytics`.

### 1. Preparar el Servidor VPS (Prerrequisitos)
Asegúrate de tener instalado Podman y las herramientas de plantillas:
```bash
# En Ubuntu/Debian:
sudo apt update && sudo apt install -y podman envsubst rsync
```

### 2. Configurar Permisos para Puertos Privilegiados (80 / 443)
Por defecto, las aplicaciones Rootless de Podman no pueden escuchar en puertos por debajo del 1024. Para permitir que nuestro Nginx escuche en el puerto 80 y 443 sin ejecutar privilegios de root, ejecuta en la terminal de la VPS:
```bash
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
# Para hacerlo persistente en reinicios del sistema:
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
```

### 3. Permitir que el stack se ejecute en segundo plano (Linger)
Por defecto, Systemd detiene todos los procesos del usuario rootless cuando este cierra la sesión SSH. Para evitar esto y que Oscarlytics corra de por vida en producción:
```bash
# Habilitar persistencia de Systemd User Manager para tu usuario
loginctl enable-linger $USER
```

### 4. Estructura de Directorios en Producción (VPS)
Recomendamos clonar o crear solo la carpeta `infra` y `scripts` en el directorio de producción `~/oscarlytics`.
```bash
# Crear la estructura básica en la VPS
mkdir -p ~/oscarlytics/infra
mkdir -p ~/oscarlytics/scripts
```
Transfiere estos archivos desde tu máquina de desarrollo local:
```bash
# Desde tu equipo local:
rsync -avz -e "ssh" infra/ usuario@tu_vps:~/oscarlytics/infra/
rsync -avz -e "ssh" scripts/ usuario@tu_vps:~/oscarlytics/scripts/
```

### 5. Crear el Archivo de Configuración Real (`infra/.env`)
Crea y edita el archivo `~/oscarlytics/infra/.env` en tu VPS:
```bash
nano ~/oscarlytics/infra/.env
```
Asegúrate de rellenar los datos con tus claves reales:
```ini
DOMAIN=oscarlytics.com                # Tu dominio real
DB_NAME=portfolio
DB_USER=pod_user
DB_PASSWORD=una_contrasena_muy_segura
SECRET_KEY=clave_secreta_flask_aleatoria
MEILI_MASTER_KEY=clave_maestra_meilisearch_larga
GHCR_REGISTRY=ghcr.io/tu-usuario-github
ADMIN_USER=tu_usuario_admin
ADMIN_PASSWORD=tu_contrasena_admin_segura
DuckDNS_Token=tu_token_duckdns        # Necesario para la validación de certificados SSL acme.sh
```

### 6. Ejecutar el Despliegue Automatizado
Ejecuta el script de despliegue que generará los Quadlets en Systemd:
```bash
cd ~/oscarlytics
chmod +x scripts/deploy_prod.sh
./scripts/deploy_prod.sh
```
El script realizará las siguientes acciones automáticamente:
1. Creará los directorios de persistencia necesarios en `~/oscarlytics/data/` (`portfolio_db/`, `meilisearch_data/`, `portfolio_storage/`).
2. Asignará los permisos de escritura necesarios para los UID de contenedores no raíz (`chmod 777` en almacenamiento e índices).
3. Utilizará `envsubst` para inyectar las variables del `.env` en las plantillas y creará los archivos `.generated` que aíslan contraseñas.
4. Generará enlaces simbólicos en `~/.config/containers/systemd/` para que Systemd entienda la configuración de Quadlet.
5. Recargará Systemd en espacio de usuario (`systemctl --user daemon-reload`).
6. Detendrá la versión anterior (si existiese) e iniciará el servicio Systemd `portfolio.service`.

### 7. Comprobación de Arranque y Logs
```bash
# Estado del servicio
systemctl --user status portfolio.service

# Ver logs en tiempo real para verificar que descarga las imágenes y corre el servidor Flask/Nginx/Postgres/Meilisearch
journalctl --user -u portfolio.service -f
```

---

## Fase 8: Benchmark de Rendimiento de Oscarlytics

Una vez que el nuevo stack endurecido esté arriba, realizaremos el mismo benchmark ejecutado en la **Fase 2** para analizar las diferencias cualitativas y cuantitativas.

### 1. Comprobación del Uso de Recursos
En tu VPS ejecuta:
```bash
# Ver el consumo de CPU y RAM del nuevo Pod rootless
podman stats --no-stream
```
*Observarás que Meilisearch consume una fracción minúscula de RAM en comparación con Elasticsearch v1.0, y que los contenedores Wolfi no consumen recursos en procesos secundarios ocultos.*

### 2. Prueba de Carga Comparativa (HTTP Benchmarking)
Ejecuta el mismo comando de la Fase 2 desde la misma máquina cliente local:
```bash
wrk -t12 -c400 -d30s https://tudominio.com/
```
Compare los resultados y documente la mejora en:
- Latencia en el P95 y P99 (gracias a Nginx endurecido y Flask corriendo sobre imágenes minimalistas distroless).
- El rendimiento del buscador Meilisearch (puedes probar la latencia al realizar búsquedas en `/search?q=algo`).
- Estabilidad de las peticiones sin timeouts ni errores de socket.

---

## Fase 9: Puesta en Marcha del Stack de Control y Monitorización

Pondremos en marcha el stack de monitorización basado en Prometheus y exportadores de sistema endurecidos (`07.pod-monitor`), el cual correrá localmente en tu ordenador local y monitorizará los recursos de la máquina de manera segura.

### 1. Iniciar el Socket de Podman (Prerrequisito)
Para que el exportador de Podman (`sensor-podman`) pueda leer el socket y recopilar métricas de tus contenedores rootless, es indispensable habilitar el servicio de socket de Podman en Systemd:
```bash
# Arrancar y habilitar de forma permanente el socket de Podman para tu usuario rootless
systemctl --user enable --now podman.socket

# Verificar que el socket existe y tiene los permisos adecuados
ls -la /run/user/1000/podman/podman.sock
```

### 2. Compilar las Imágenes del Stack de Control
Ve al directorio de tu stack de monitorización en tu ordenador local:
```bash
cd "/home/roque/03. Projects/07.pod-monitor"
```
Asegúrate de compilar las imágenes endurecidas locales para el exportador de sistema, de podman y el servidor Prometheus:
```bash
chmod +x scripts/build_images.sh
./scripts/build_images.sh
```

### 3. Configurar el Entorno del Monitor Stack
Verifica el archivo de configuración `env/local.env` y confirma que las rutas y puertos sean los esperados:
- `PODMAN_SOCK=/run/user/1000/podman/podman.sock` (La ubicación por defecto del socket rootless de tu usuario 1000).
- `PORT_NODE_EXPORTER=9100`
- `PORT_PODMAN_EXPORTER=9882`
- `PORT_PROMETHEUS=9090`

### 4. Desplegar e Integrar con Systemd
Ejecuta el script de despliegue local:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```
El script creará la red personalizada de monitorización en Podman (`monitor-network`), preparará los directorios persistentes en `data/prometheus`, inyectará las variables de entorno mediante `envsubst` y vinculará las unidades Quadlet en tu Systemd (`~/.config/containers/systemd/monitor.kube`, etc.).

### 5. Arrancar y Visualizar el Panel de Monitorización
```bash
# Arrancar el servicio de monitorización
systemctl --user start monitor.service

# Comprobar estado del servicio
systemctl --user status monitor.service

# Visualizar logs para asegurar que Prometheus lee las métricas sin problemas
journalctl --user -u monitor.service -f
```
Ahora podrás entrar en tu navegador local a `http://localhost:9090` para abrir la consola web de Prometheus y consultar todas las métricas del sistema local e incluso tus contenedores Podman en tiempo real.

---

## Fase 10: Sugerencias Cruciales para Prevenir Fallos

Para que la migración y producción sean 100% robustas y exitosas, te sugerimos seguir estas buenas prácticas fundamentales:

1. **Prueba de Certificados (Dry Run) de `acme.sh`:**
   Dado que `acme.sh` utilizará la API de DuckDNS, asegúrate de que el token de DuckDNS sea el correcto. La primera vez puede tardar unos minutos en propagar los registros TXT DNS. Puedes ver los logs usando `podman logs -f portfolio-acme-sh`.
2. **Estrategia Zero-Downtime:**
   No elimines de golpe Portfolio 1.0 (Docker Compose) antes de verificar que Oscarlytics (Podman) descarga las imágenes y compila correctamente.
   - Detén el portfolio viejo: `docker-compose down`.
   - Lanza el portfolio nuevo: `systemctl --user start portfolio`.
   - Si Nginx da algún error de configuración o el SSL tarda, puedes volver a levantar la versión anterior de forma inmediata ejecutando `docker-compose up -d` en segundos, garantizando un impacto nulo.
3. **Caché y Cookies del Navegador:**
   Nginx de la versión 2.0 tiene cabeceras de seguridad endurecidas más estrictas (como HSTS, Content Security Policy). Si pruebas en tu navegador habitual, es posible que experimentes redirecciones o advertencias temporales si tienes sesiones anteriores activas. Prueba siempre los cambios de despliegue usando una pestaña de **Incógnito** o limpiando la caché DNS/Cookies.
4. **Permisos SELinux (si aplica):**
   Si tu VPS corre una distro de la familia RedHat (CentOS, Rocky Linux, Fedora), SELinux podría restringir el acceso de los contenedores a las carpetas montadas. Si es el caso, añade `:z` o `:Z` a los mounts o ejecuta `chcon -Rt svirt_sandbox_file_t ~/oscarlytics/data/`. En distros basadas en Debian/Ubuntu no es necesario.
5. **Comprobación de logs de importación:**
   Al arrancar Oscarlytics por primera vez con los datos transferidos, comprueba que el indexador procesa y carga los markdown en base de datos. Lo puedes hacer inspeccionando el log del contenedor app: `podman logs portfolio-app`.
