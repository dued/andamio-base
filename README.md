# Andamio Base

![Andamio deployment](https://img.shields.io/badge/deployment-andamio-base)
![Andamio-base template](https://img.shields.io/badge/template%20engine-andamio.base-informational)
[![Boost Software License 1.0](https://img.shields.io/badge/license-bsl--1.0-important)](COPYING)
![latest version](https://img.shields.io/github/v/release/dued/andamio-base?sort=semver)
![test](https://github.com/dued/andamio-base/workflows/test/badge.svg)
![lint](https://github.com/dued/andamio-base/workflows/lint/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->

## ¿Que hace andamio-base?

Es básicamente una plantilla base para mantener e integrar proyectos Dued que se pueden
orquestar en cubos [maxive]() tanto en la nube o si lo prefieres sobre metal desnudo.
Incluye; desarrollo, test y producción basado en su imagen imperativa
[andamio](https://github.com/dued/andamio-base) .

## ¿Por que?

Se necesita un enfoque de infraestructuras no dependientes para desarrollar y orquestar
una nueva generación de aplicaciones basadas en el enfoque DUED.

## ¿Como lo hace?

Sobre una imagen en el registry definimos un andamiaje-base que luego sera un proyecto
independiente una estructura definitiva que se configura de forma dinámica tal que Dued
pueda administrar con eficiencia todo el ciclo del proyecto.

> Nota el proyecto está en una etapa final de su etapa beta y la versión candidata sigue
> en un nivel que requiere todavia de mayores pruebas, por lo que sugerimos tener
> cuidado.

### Créditos

Este proyecto está mantenido por

[![dued](https://raw.githubusercontent.com/dued/co-data/master/static/igob_logo_smll.png)](https://igob.pe/dued/)

Además, ¡gracias totales! a
[Nuestros queridos contribuyentes de la comunidad](https://github.com/dued/andamio-base/graphs/contributors).
