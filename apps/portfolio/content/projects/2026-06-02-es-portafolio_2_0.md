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
link1: "https://github.com/oiroqueiro/oscarlytics"
link2: "/es/project/2023-12-27/1/portafolio/"
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

1. **Migración de Elasticsearch a Meilisearch:** Reemplazamos el motor de búsqueda por Meilisearch. Al ser un motor ultraligero y de alto rendimiento escrito en Rust, logramos mantener una búsqueda rápida de proyectos pero con una fraction diminuta del consumo de memoria.
2. **Migración de Excel a Markdown dinámico:** Eliminamos por completo el uso de Excel. El contenido del portafolio se gestiona ahora a través de ficheros Markdown (`.md`) con metadatos Frontmatter. Un script en Python analiza y sincroniza automáticamente las publicaciones en la base de datos y Meilisearch al iniciar la aplicación.
3. **Ecosistema Rootless con Podman y Quadlets:** Sustituimos el clásico `docker-compose` por Podman Quadlets, integrados nativamente con el gestor de servicios `systemd` de Linux. La aplicación se ejecuta de forma aislada, sin privilegios root y como un demonio del sistema operativo.
4. **Contenedores Endurecidos (Hardening):** Aplicamos estrictas políticas de seguridad en cada contenedor:
   - Configuración de `NoNewPrivileges=true` y `DropCapabilities=ALL` para mitigar escapes de contenedor.
   - Sistemas de archivos de solo lectura (`ReadOnlyRootFilesystem=true`) en los contenedores Nginx y la Aplicación Flask.
   - Uso de imágenes base limpias y seguras (Chainguard/Wolfi y Alpine minimalistas).
5. **Automatización de Despliegue y SSL:** ACME.sh se ejecuta como un contenedor sidecar realizando la validación DNS-01 (DuckDNS) para asegurar certificados SSL automáticos sin interrumpir el puerto 80/443 de Nginx.
6. **Observabilidad y Monitorización Distribuida:** Implementamos una infraestructura de observabilidad distribuida. En el servidor `vps-prod` desplegamos un sensor de sistema operativo (Node Exporter), un sensor de métricas de Podman (Podman Exporter) y un recolector de logs endurecido y rootless (Promtail) agrupados dentro de un mismo Pod de monitorización. Estos servicios envían de forma segura la telemetría a través de una red VPN overlay privada (NetBird) hacia un nodo central de observabilidad en Oracle Cloud Infrastructure (OCI). En OCI se centraliza el almacenamiento con Prometheus y Loki, y se aprovisiona mediante API un cuadro de mando maestro en Grafana que unifica logs, uso de recursos por contenedor, I/O de disco/red y analíticas web en tiempo real.

<img src="/static/img/projects/podman_stats_post.png" class="img-fluid w-100" alt="podman stats post"></img>
*Fig 3. Estadísticas de contenedores de la versión 2.0 (Podman stats) que muestran el drástico descenso de RAM.*

<img src="/static/img/projects/htop_post_migration.png" class="img-fluid w-100" alt="htop post"></img>
*Fig 4. Carga del sistema con el nuevo stack de Podman en producción.*

<img src="/static/img/projects/free_h_post.png" class="img-fluid w-100" alt="free -h post"></img>
*Fig 5. Detalle final del uso de memoria en caliente del servidor VPS con el nuevo stack activo.*

Adicionalmente, realizamos pruebas de estrés HTTP (HTTP Benchmarking) simulando carga concurrente para evaluar la latencia y la capacidad de respuesta global del servidor. Los resultados post-migración demuestran una mejora sustancial en el rendimiento de la web, entregando tiempos de respuesta mucho más estables, menor latencia y cero pérdida de paquetes debido a la ligereza del ecosistema y a la correcta optimización de Nginx.

<img src="/static/img/projects/http_benchmarking_pre.png" class="img-fluid w-100" alt="http benchmarking pre"></img>
*Fig 6. Pruebas de rendimiento HTTP en la infraestructura anterior.*

<img src="/static/img/projects/http_benchmarking_post.png" class="img-fluid w-100" alt="http benchmarking post"></img>
*Fig 7. Pruebas de rendimiento HTTP tras la migración y optimización.*

<img src="/static/img/projects/grafana_vps_prod.png" class="img-fluid w-100" alt="grafana vps prod"></img>
*Fig 8. Cuadro de mando maestro consolidado de observabilidad en Grafana mostrando métricas de rendimiento y logs en tiempo real.*

## Resolución
La migración a Portafolio 2.0 ha sido un éxito rotundo, logrando los siguientes resultados medibles:
- **Reducción del 90% en el consumo de RAM:** El stack completo en reposo pasó de requerir casi 1.8 GB a consumir **menos de 190 MB de RAM**.
- **Cero privilegios de superusuario (root):** Todos los contenedores y el pod se ejecutan en espacio de usuario.
- **Rendimiento e indexación instantáneos:** La búsqueda de Meilisearch responde en pocos milisegundos y la carga del procesador en el VPS host se mantiene cercana al 0.1% en reposo.

Este proyecto demuestra que es posible diseñar infraestructuras autogestionadas extremadamente seguras y de alto rendimiento sin sobrecargar los recursos del servidor.

El código fuente y las plantillas de esta nueva versión están disponibles en [Mi GitHub](https://github.com/oiroqueiro/oscarlytics). Si quieres conocer más detalles sobre el diseño original de la versión 1.0 (basada en Docker y Elasticsearch), puedes visitar el artículo correspondiente de [Portafolio 1.0](/es/project/2023-12-27/1/portafolio/).
