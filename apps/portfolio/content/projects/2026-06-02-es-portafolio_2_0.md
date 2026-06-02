---
title: "Portafolio 2.0: Infraestructura Endurecida con Podman y Quadlets"
language: es
date: 2026-06-02
project_n: 1
keywords: "podman, quadlet, seguridad, postgresql, meilisearch, nginx, ssl, acme, cloud, devops, hardening"
image_title: "project07"
image1: ""
image2: ""
image3: ""
image4: ""
image5: ""
link1: "https://github.com/oiroqueiro/portfolio"
---

## Resumen
Evolución y migración de la infraestructura de mi portafolio (Oscarlytics) desde un entorno tradicional con Docker Engine y Elasticsearch hacia un ecosistema de alta seguridad, rendimiento optimizado y ejecución sin privilegios (rootless) mediante Podman y Quadlets integrados en Systemd, reduciendo el consumo de memoria en un 90%.

## Exposición
Tras unos años en funcionamiento con la versión 1.0 de Oscarlytics, sentí la necesidad de evolucionarlo hacia un verdadero laboratorio de datos y sistemas personales. Sin embargo, el stack original presentaba algunos desafíos importantes:

1. **Consumo de recursos excesivo:** La presencia de Elasticsearch, a pesar de sus increíbles capacidades de búsqueda, requería un consumo base de memoria de entre 1.5 GB y 2.5 GB de RAM. Para un servidor VPS de recursos limitados, esto dejaba muy poco margen para otros experimentos.
2. **Seguridad y privilegios:** Todo el stack dependía del demonio central de Docker corriendo como `root`. Cualquier vulnerabilidad en los contenedores podría comprometer potencialmente el sistema host.
3. **Mantenimiento y configuración:** El uso de hojas Excel para alimentar el contenido de los proyectos hacía que las actualizaciones fueran manuales y poco dinámicas.

Para este refactor, decidí plantear la estrategia y la arquitectura yo mismo (estableciendo estándares de endurecimiento y optimización estrictos), delegando la ejecución en mi agente autónomo **Gemini (Antigravity)**.

<img src="/static/img/projects/htop_pre_migration.png" class="img-fluid w-100" alt="htop pre"></img>
*Fig 1. Captura del consumo y carga del sistema (htop) en la infraestructura anterior con Docker y Elasticsearch.*

<img src="/static/img/projects/docker_stats_pre.png" class="img-fluid w-100" alt="docker stats pre"></img>
*Fig 2. Estadísticas de uso de contenedores en la versión original.*

## Acción
Para llevar a cabo la migración al stack 2.0, se implementaron las siguientes acciones de ingeniería:

1. **Migración de Elasticsearch a Meilisearch:** Reemplazamos el motor de búsqueda por Meilisearch. Al ser un motor ultraligero y de alto rendimiento escrito en Rust, logramos mantener una búsqueda rápida de proyectos pero con una fracción diminuta del consumo de memoria.
2. **Migración de Excel a Markdown dinámico:** Eliminamos por completo el uso de Excel. El contenido del portafolio se gestiona ahora a través de ficheros Markdown (`.md`) con metadatos Frontmatter. Un script en Python analiza y sincroniza automáticamente las publicaciones en la base de datos y Meilisearch al iniciar la aplicación.
3. **Ecosistema Rootless con Podman y Quadlets:** Sustituimos el clásico `docker-compose` por Podman Quadlets, integrados nativamente con el gestor de servicios `systemd` de Linux. La aplicación se ejecuta de forma aislada, sin privilegios root y como un demonio del sistema operativo.
4. **Contenedores Endurecidos (Hardening):** Aplicamos estrictas políticas de seguridad en cada contenedor:
   - Configuración de `NoNewPrivileges=true` y `DropCapabilities=ALL` para mitigar escapes de contenedor.
   - Sistemas de archivos de solo lectura (`ReadOnlyRootFilesystem=true`) en los contenedores Nginx y la Aplicación Flask.
   - Uso de imágenes base limpias y seguras (Chainguard/Wolfi y Alpine minimalistas).
5. **Automatización de Despliegue y SSL:** ACME.sh se ejecuta como un contenedor sidecar realizando la validación DNS-01 (DuckDNS) para asegurar certificados SSL automáticos sin interrumpir el puerto 80/443 de Nginx.

<img src="/static/img/projects/podman_stats_post.png" class="img-fluid w-100" alt="podman stats post"></img>
*Fig 3. Estadísticas de contenedores de la versión 2.0 (Podman stats) que muestran el drástico descenso de RAM.*

<img src="/static/img/projects/htop_post_migration.png" class="img-fluid w-100" alt="htop post"></img>
*Fig 4. Carga del sistema con el nuevo stack de Podman en producción.*

## Resolución
La migración a Portafolio 2.0 ha sido un éxito rotundo, logrando los siguientes resultados medibles:
- **Reducción del 90% en el consumo de RAM:** El stack completo en reposo pasó de requerir casi 1.8 GB a consumir **menos de 190 MB de RAM**.
- **Cero privilegios de superusuario (root):** Todos los contenedores y el pod se ejecutan en espacio de usuario.
- **Rendimiento e indexación instantáneos:** La búsqueda de Meilisearch responde en pocos milisegundos y la carga del procesador en el VPS host se mantiene cercana al 0.1% en reposo.

<img src="/static/img/projects/free_h_post.png" class="img-fluid w-100" alt="free -h post"></img>
*Fig 5. Detalle final del uso de memoria en caliente del servidor VPS con el nuevo stack activo.*

Este proyecto demuestra que es posible diseñar infraestructuras autogestionadas extremadamente seguras y de alto rendimiento sin sobrecargar los recursos del servidor. El código fuente y las plantillas están disponibles en [Mi Github](https://github.com/oiroqueiro/portfolio).
