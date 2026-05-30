---
title: "Gestión contenido vía web"
language: es
date: 2026-03-01
project_n: 1
keywords: "python, flask, base de datos, postgresql, multi-idioma, markdown"
image_title: "project0501"
image1: "project0502"
image2: "project0503"
image3: "project0504"
image4: "project0505"
image5: "project0506"
link1: ""
link2: ""
link3: ""
link4: ""
link5: ""
---

## Resumen
Creación de un sistema de gestión de contenido (textos de la web y proyectos) como una sección nueva del menú principal.

## Exposición
Cuando creé el proyecto de [**Portfolio**](/es/project/2023-12-27/1/portfolio/), me quedó una idea inicial que tenía en el tintero por falta de tiempo:

>Al principio pensé en gestionar la creación del contenido desde el propio sitio web, pero pronto me di cuenta de que no tenía tiempo si quería terminar el proyecto este año. Sin embargo, investigué y al final,  pude crear una parte de la que me siento un poco orgulloso, esto es que pude hacer las URLs para las páginas de inicio de sesión y fin de sesión de mi sitio web personalizadas via variables de entorno. La opción de editar el contenido sería una funcionalidad para el futuro.

Y el futuro llegó.

## Acción
En este proyecto me propuse probar las capacidades de los agentes IA de programación, así que ¿por qué no darle esta tarea a Gemini?. 

Recientemente Google publicó un IDE, al estilo Visual Studio Code que era el que estaba usando -y sigo usando para otros temas-, [**Antigravity**](https://antigravity.google/) que a diferencia de Visual Studio Code está enfocado en el uso de agentes. Así que aprovechando que tengo una cuenta de Google con las cuotas de consumo de tokens un poco más elevadas me propuse realizar algún proyecto con su ayuda, siendo este el primero.

<div class="notices info">
<p>
<b>Reflexión:</b> He de decir que, quien se dedica a la programación si no usa asiduamente la IA o no ha llegado a probar los agentes de programación, está perdiendo un tiempo muy valioso, ya no debido a la evolución tan rápida de estos sistemas si no porque se está perdiendo una mejora de productividad brutal. Y ya no digo a quien pretende entrar en este mundo, los programadores juniors, el uso de la IA es obligatorio hoy en día, y hay que aprender a diferenciarse para no quedarse en la búsqueda de un primer empleo que al ritmo que lleva el crecimiento de la IA podría convertirse en una búsqueda permanente..
</p>
</div>

En este proyecto, en mis tareas de planificador, control y pruebas (y cero programación), empecé pidiendo un menú en el que se pudiera subir un fichero markdown con la información del proyecto (este proyecto forma parte de otros proyectos mucho más grandes entre ellos eliminar el uso de una hoja excel para la carga de los datos, y en ellos explicaré con más detalle estos cambios), Además añadimos también la carga de los textos de la web vía archivo también.

<img>image1</img>

Pero cuando lo probamos y estaba funcionando, qué mejor manera que de probar también el agente pidiendo un CRUD de proyectos.

<img>image2</img>

En este CRUD (que va por idioma como toda la web), se puede ver, editar el contenido o eliminar un proyecto. Este borrado (que pide confirmación) del proyecto únicamente lo elimina de la base de datos para que no aparezca, no elimina el fichero markdown con lo que se podría volver a subir en caso de error. Si queremos que sea definitivo, tendríamos que eliminar el fichero markdown.

<img>image3</img>

Además en la edición también se pueden indentificar las imagenes que se quieren mostrar.

<img>image4</img>

Todo esto funciona dentro de la sección que habia planteado en el proyecto de [**Portfolio**](/es/project/2023-12-27/1/portfolio/) en el que vía variables de entorno, se define el endpoint de login y logout, así como el usuario y la contraseña.

>PORTFOLIO_LOGIN_URL=manage

<img>image5</img>

>PORTFOLIO_LOGOUT_URL=theend

>ADMIN_USER=

>ADMIN_PASSWORD=


## Resolución
<div class="notices info">
<p>
Resumiendo, este proyecto no lo he programado yo, pero sí que lo he ideado, gestionado y testeado, tener agentes de programación a mi disposición es como un tener un ejército de programadores, con un conocimiento inmenso, aunque visto en un nivel profesional en algunas situaciones son completamente juniors. Trabajar con agentes IA (y con la IA a nivel programación, en general) requiere tener conocimiento de lo que se quiere, se pide y lo que se espera, si no podríamos encontrarnos con un programa funcional, sí, pero que quizás a la mínima de cambio falla o es imposible de mantener.
</p>
</div>