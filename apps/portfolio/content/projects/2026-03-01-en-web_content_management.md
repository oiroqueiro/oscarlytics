---
title: "Content Management via Web"
language: en
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

## Resume
Building a content management system (web texts and proyects) as a new section of the main menu.

## Exposition
When I built the [**Portfolio**](/en/project/2023-12-27/1/portfolio/) project, I had an initial idea that I had put aside due to lack of time:

>At the beginning I thought to manage the creation of the content within the website, but soon I realized that I didn't have time if I wanted to finish the project this year. Nevertheless, I did investigate and in the end, I could create one part that makes me feel a little proud of, it is that I could make the URLs to the login and logout pages of my website customizable via environment variables. The option of editing the content would be a future feature.

And the future arrived.

## Action
In this project, the goal was to test the capabilities of AI coding agents, so why not give this task to Gemini?.

Google recently released an IDE, similar to Visual Studio Code -which was and still used for other things-, called [**Antigravity**](https://antigravity.google/) that, unlike Visual Studio Code, focuses on the use of agents. So, taking advantage of having a Google account with slightly higher token consumption quotas, it was decided to carry ou a project with its help, this being the first one.

</div>
<div class="notices info">
<p>
<b>Reflection:</b> Anyone dedicated to programming who dows not regularly use AI or has not tried programming agents is losing valuable time. This is not due to the rapid evolution of these systems, but also because they are missing out on a significant productivity imprvement. This applies not just to those trying to enter this world, for junior programmers, the use of AI is mandatory today. Programmers must learn how to differentiate themselves so as not tho get stuck in the search for a first job, At the rate AI is growing, that search could become permanent.
</p>
</div>

In this project, in the roles of planner, controller and tester (with zero programming), the process began by requesting a menu where a markdown file with the project information could be uploaded (this project is part of other much larger projects, including eliminating the use of an Excel sheet for data loading, and these changes will be explained in more detail). Additionally, the loading of web texts via a file was also added.

<img>image1</img>

But once it was tested and working, what better way to test the agent than by requesting a project CRUD?.

<img>image2</img>

In this CRUD (which works by language like the rest of the web), it's possible to view, edit the content, or delete a project. This deletion (which asks for confirmation) only removes the project from the database so that it dows not appear, it does not delete the markdown file so it could be re-uploaded in case of error. If a permanent deletion is desired, the markdown file would need to be deleted.

<img>image3</img>

Furthermore, in the edition, the images that you want to show can also be indentified.

<img>image4</img>

All of this works within the section planned in the [**Portfolio**](/en/project/2023-12-27/1/portfolio/) planned, where, via environment variables, the login and logout endpoints are defined, as well as the username and password.

>PORTFOLIO_LOGIN_URL=manage

<img>image5</img>

>PORTFOLIO_LOGOUT_URL=theend

>ADMIN_USER=

>ADMIN_PASSWORD=


## Resolution
<div class="notices info">
<p>
In summary, this project was not programmed directly, but it was devised, managed, and tested. Having programming agents available is like having an army of programmers with immense knowledge, although at a professional level, in some situations, they are completely juniors. Working with AI agents (and with AI at a programming level, in general) requires knowledge of what is wanted, what is asked for, and what is expected; otherwise, a functional program could result, but one that might fail at the slightest change or be impossible to maintain.
</p>
</div>