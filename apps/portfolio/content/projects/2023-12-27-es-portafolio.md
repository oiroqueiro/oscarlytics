---
title: "Portafolio"
language: es
date: 2023-12-27
project_n: 1
keywords: "python, flask, hugo, base de datos, sqlite, postgresql, elasticsearch, contenedor, docker, multi-idioma, portafolio, nginx, https"
image_title: "project0401"
image1: "project0402"
image2: "project0403"
image3: "project0404"
link1: ""
link2: ""
link3: ""
link4: ""
link5: ""
---

## Resumen
Portafolio creado desde cero, desde la planificación de la página web sin saber desarrollo web hasta la implementación con Docker sin tener idea de contenedores.

## Exposición
Tenía varios proyectos que quería mostrar pero no me gustaba la idea de usar una página web existente porque todas las alternativas que había probado no tenían todas las caracterías que pensaba eran necesarias en mi portafolio o no eran flexibles para personalizarlas o no eran suficientemene bonitas (o lo que yo considero bonito para un portafolio).  
Usar una de esas plataformas sería la mejor opción ya que tengo un trabajo a jornada completa y dos pequeñas nacidas durante los años de la pandemia, pero decidí tomar el camino más complicado (a veces infernal) y <u>crear mi portafolio desde cero</u>.  
Sé que un portafolio no es un gran ejemplo como proyecto de análisis de datos, realmente no está relacionado con el análisis de datos, pero sí que es una gran oportunidad para mostrar mi <u>determinación</u>, <u>resolución creativa de problemas</u>, <u>adaptabilidad</u> y aprender un montón durante todo el tiempo que le he dedicado a este proyecto.  
Las características que me gustaría que tuviera mi portafolio incluyen:  
1. Multi-idioma  
2. Página web adaptable (responsive)  
3. Modo claro/oscuro  
4. Personalizable  
5. Uso de contenedores  
6. Búsqueda por índices  
Las primeras 4 eran obligatorias, las otras dos me gustaría aprenderlas y practicar con ellas.  


## Acción
Así que paso a explicar el camino desde el principio.   

<img>image1</img>

#### **El camino**  
Puesto que yo no soy un diseañador o desarrollador web, y mi conocimiento de HTML, CSS, y JavaScript era limitado, el reto empezó siendo super complicado para mi..   
##### **Multi-idioma**  
Una cosa de la que yo estaba seguro que no iba a pasar era el uso de una librería para realizar la traducción de todos los textos automáticamente. Sé que hay fantásticas opciones por ahí que podrían hacer mi portafolio accesible a casi todo el mundo, pero creo que una característica como esta iría contra lo que es la naturaleza de un portafolio.  
Un portafolio debería de ser una carta de presentación del trabajo de alguien para mostrar las habilidades del propietario, el uso de una herramienta automatizada, la cual es bastante sencilla de implementar (sé de lo que hablo porque la usé en 2 de mis anteriores proyectos y por supuesto, no estoy en contra de su uso), no es lo que yo quería, así que la opción que escogí para implementar el multi-idioma fue traducir por mí mismo los textos y guardarlos en la base de datos haciendo sencillo para los usuarios su uso y el cambio entre los idiomas que el dueño conoce (o decide mostrar).  
##### **La página web**  
Cuando empecé a investigar mis opciones de crear una página web, el inicio fue descorazonador. Solamente cuando descubrí [**Hugo**](https://gohugo.io/) empecé a ver la luz al final del túnel. Hugo es una plataforma para construir sitios web con muchas plantillas bonitas y una gran comunidad. Así que estuve investigando Hugo y sus plantillas bastante tiempo hasta que encontŕé algunas que podrían cumplir con mis requerimientos. El problema era que Hugo es fantástico para crear páginas web estáticas lo que es contrario a mi idea de un portafolio.  
De manera que al final cuando escogí la plantilla de [**iWriter**](https://github.com/statichunt/iwriter-hugo) llegó el momento de adaptarla a un sitio web dinámico.  
##### **Flask**  
Una tecnología que quería explorar y en la que quería mejorar mis habilidades era [**Python**](https://www.python.org/) porque tiene cientos de librerías, frameworks, y con una impresionante comunidad detrás. Así, cuando pensé en sitios web dinámicos, [**Flask**](https://flask.palletsprojects.com/en/3.0.x/) vino rápidamente a mi mente. Desde que había trabajado con él en mi proyecto [*Lyrics*](https://oscarlytics.com/es/project/2022-12-17/1/lyrics/), conocía sus capacidades pero la parte dura del trabajo no solamente acababa de empezar.  
Tuve que adaptar la plantilla iWriter para ser una plantilla dinámica con [Jinja](https://jinja.palletsprojects.com/en/3.1.x/templates/) sin perder ninguna funcionalidad que me gustaba de esta plantilla.  
Después de invertir muchas, muchas, muchas horas entendiendo el HTML, CSS, JavaScript, y Bootstrap (y otras tecnología) que mi plantilla estaba usando para tener tales funcionalidades y más horas limpiando el código y adaptándolo, conseguí tener algunas plantillas bastante limpias y listas para usar con la lógica de mi página web.  
En este punto quería compartir con todos vosotros [**este fantástico tutorial de Flask**](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world), de *Miguel Grinberg*. También usé este otro, en Español, de [**j2logo**](https://j2logo.com/tutorial-flask-espanol/) por *Juan José Lozano Gómez*. Aprendí un montón con ellos y con todas las funcionalidades que tuve que encarar.  

<img>image2</img>
##### **Personalizable**  
Quería una página web personalizable así que después de evaluar diferentes opciones, decidí usar un fichero Excel para almacenar los textos de mi sitio web junto con el contenido de mi portafolio. Los textos de los menús, botones, imagenes, ... pueden ser adaptadas facilmente.  
Al principio pensé en gestionar la creación del contenido desde el propio sitio web, pero pronto me di cuenta de que no tenía tiempo si quería terminar el proyecto este año. Sin embargo, investigué y al final,  pude crear una parte de la que me siento un poco orgulloso, esto es que pude hacer las URLs para las páginas de inicio de sesión y fin de sesión de mi sitio web personalizadas via variables de entorno. La opción de editar el contenido sería una funcionalidad para el futuro.  
Y cómo podría hacer el contenido de mi portafolio personalizable? Primero pensé en el uso de HTML, después en el uso de [**Markdown**](https://www.markdownguide.org/), y al final, pensé, ¿qué es mejor que permitir el uso de ambos? Así, podemos escribir nuestro contenido usando etiquetas Markdown y HTML al mismo tiempo.  
##### **BBDD**  
He trabajado con Microsoft SQL Server durante más de 15 años y últimamente, he estado trabajando con MySQL, al principio de mi carrera estuve usando Oracle durante años. Así que para este proyecto, decidí intentar una nueva base de dtaos y la opción escogida para desarrollo era [**SQLite**](https://www.sqlite.org/index.html) pero para el uso en producción una vez implementara el proyecto sería [**PostgreSQL**](https://www.postgresql.org/). La mejor parte es que mi portafolio funciona perfectamente con  ambas así que solamente hay que cambiar las variables de entorno para usar SQLite, PostgreSQL, u otra base de datos distinta.  
##### **La búsqueda**  
Al principio, mi portafolio tendría pocos proyectos, así que una funcionalidad de búsqueda no sería demasiado importante pero quería crear un proyecto vivo durante bastante tiempo y facilmente mantenible así que al final implementé una función sencilla de búsqueda usando las consultas de la extensión [**FlaskSQLAlchemy**](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/) la cual era la librería que estaba usando para trabajar con las bases de datos. Pero los últimos meses he estado leyendo bastante a menudo sobre bases de datos NoSQL, y las capacidades de [**Elasticsearch**](https://www.elastic.co/) para la búsqueda, así que decidí empezar a trabajar con este tipo de bases de datos usando Elasticsearch en mi proyecto.  
Finalmente, la opción de búsqueda en mi portafolio está facilitada por Elasticsearch y, en caso de que esta herramienta no está presente en nuestro entorno, será gestionada por FlaskSQLAlchemy.  
También tengo una búsqueda de palabras clave, esta es mucho más simple y encontrará solamente la palabra clave que estemos buscando pero con la característica de traer también las palabras claves que comparten los proyectos donde nuestra palabra clave de búsqueda esté presente.  
##### **Contenedores**  
Y, si no fuera suficiente con todas las tecnologías que tuve que explorar, aprender, e implementar para mi proyecto, decidí que debería usar contenedores en mi aplicación. Así que empecé a aprender [**Docker**](https://www.docker.com/) ya que es una de las plataformas más populares. Durante mi aprendizaje, fuí capaz de crear un contenedor de docker para mi aplicación Flask, así que tenía un contenedor docker con mi portafolio funcionando pero quería crear todo mi proyecto con contenedores. Al final, terminé con una red de docker con <del>3 contenedores</del> 4 contenedores:  
- El primero, y más importante porque tiene todo los datos, un docker con PostgreSQL  
- El segundo, si está presente, es el docker de Elasticsearch para la funcionalidad de búsquedas  
- El tercero es mi aplicación Flask la cual tiene incluso el servidor HTTP WSGI  gestionado con [**Gunicorn**](https://gunicorn.org/)  
- El cuarto es el auténtico Servidor Web y Proxy Reverso, el docker con [**Nginx**](https://www.nginx.com/)
##### **Implementación**  
Como último paso de mi proyecto, necesito implementarlo. Durante toda esta ruta, estuve trabajando siempre con opensource u opciones gratuitas (excepto el nombre de dominio que he tenido que pagar) y la opción que he encontrado y que podría funcionar para mi era el uso de [**OCI**](https://www.oracle.com/es/cloud/), la **Infraestructura de la nube de Oracle** (Oracle Cloud Infrastructure) que tenía una opción gratuita (Always Free Services) la cual podría usar para la implementación.  
Los problemas surgieron cuando no pude ejecutar todos los contenedores, pude descargar incluso mi contenedor Flask desde el docker hub, pero cuando lo intenté levantar me encontré con un montón de problemas con la arquitectura del hardware. Después de muchas pruebas y modificaciones de mi contenedor (incluso intenté recompilar todo para la nueva plataforma), me rendí y decidí intentar otro proveedor de servidores VPS.  
Esta vez decidí probar con un proveedor de pago con una plataforma que yo pudiese manejar sin muchos problemas, el resultado fue que después de configurar un nuevo servidor Ubuntu en [**Ginernet**](https://ginernet.com/es/vps/), un proveedor español (ya que yo estoy viviendo en España) con precios razonables, pude desplegar mi página web sin problemas.  
Los nuevos problemas arribaron cuando intenté acceder a mi página web desde mi móvil Android.    
El navegador cambia siempre el protocolo *HTTP* a *HTTPS* el cual no había implementado en mi aplicación Flask app, así que necesitaba cambiar mi fichero de docker-compose y añadir el cuarto contenedor (Nginx). Entonces fue el turno de la implementación del protocolo ***HTTPS*** ,que requiere certificados ***SSL*** pero no uno cualquiera firmado por mi servidor porque a los navegadores web solamente les gustan los certificados firmados por autoridades certificadoras reconocidas (si nuestro certificado no es así, el navegador web mostrará una página bastante fea antes de nuestra bonita página web), así que con la ayuda de [**Let's Encrypt**](https://letsencrypt.org/) y unas pocas pruebas (como crear un nuevo contededor que tuve que eliminar al final) pude darle a mi sitio un suficiente bueno y gratis certificado *SSL*.   
Ahora mismo, la calidad del certificado __SSL__ de mi servidor es grado **A** en [**Qualys. SSL Labs**](https://www.ssllabs.com/), pero seguiré intentando obtener pronto el grado **A+**.    
Además de todo esto, creé una cuenta en [**Google Analytics**](https://analytics.google.com/) para seguir y analizar mi página web, la cual está funcionando bien.    

<img>image3</img>  

Y esto es todo mi recorrido, amigos. Espero que todo esto sea de ayuda para alguien.   


## Resolución
Resumendo, los enlaces de mi proyecto son:  
-Todo el código fuente (incluyendo los ficheros docker y docker compose): [**Mi Github**](https://github.com/oiroqueiro/portfolio)  
-Demo real: [**mi página web Portfolio**](https://oscarlytics.com/es/index/)  

