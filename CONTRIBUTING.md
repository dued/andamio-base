# Cómo contribuir

<details>
<!-- prettier-ignore-start -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
<summary>Table of contents</summary>

- [Discusión general](#discusi%C3%B3n-general)
- [Issues](#issues)
- [Proponer cambios](#proponer-cambios)
  - [Establecer un entorno de desarrollo](#establecer-un-entorno-de-desarrollo)
    - [Conozca nuestro kit de herramientas de desarrollo](#conozca-nuestro-kit-de-herramientas-de-desarrollo)
  - [Open a Pull Request - Abrir una solicitud de extracción](#open-a-pull-request---abrir-una-solicitud-de-extracci%C3%B3n)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<!-- prettier-ignore-end -->
</details>

Debe saber cómo usar Github para contribuir a este proyecto. Para aprender, siga estos
tutoriales:

- [Introduciión a GitHub](https://lab.github.com/githubtraining/introduction-to-github)

Ahora que sabe cómo usar Github, simplemente seguimos el proceso estándar como todos los
demás aquí: problemas y solicitudes de extracción.

## Discusión general

Siga las mismas instrucciones que para [issues](#issues).

## Issues

En primer lugar, asegúrese de que su problema o sugerencia esté relacionado con
andamio-base.

Si ese es el caso, abra un problema en nuestro proyecto Github.
[Lee las instrucciones](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue)
para saber cómo hacerlo

## Proponer cambios

### Establecer un entorno de desarrollo

Para hackear este proyecto, debe configurar un entorno de desarrollo. Para hacer eso,
primero asegúrese de haber instalado las dependencias esenciales:

- [git](https://git-scm.com/)
- [invoke](https://www.pyinvoke.org/)
- [poetry](https://python-poetry.org/)
- [python](https://www.python.org/) 3.6+

Luego, ejecute:

```bash
git clone https://github.com/andamio/andamio-base.git
cd andamio-base
invoke develop
```

🎉 ¡Su entorno de desarrollo está listo!.

#### Conozca nuestro kit de herramientas de desarrollo

Una vez que haya realizado los pasos anteriores, será bueno que sepa que nuestros
componentes básicos aquí son:

- [copier](https://github.com/pykong/copier)
- [poetry](https://python-poetry.org/)
- [pre-commit](https://pre-commit.com/)
- [pytest](https://docs.pytest.org/)

### Open a Pull Request - Abrir una solicitud de extracción

Siga
[instrucciones Github para abrir una solicitud de extracción](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

Después de que hayas hecho eso:

1. Lo revisaremos lo antes posible.
1. "ASAP" podría ser mucho tiempo; recuerda que no nos pagas 😉
1. Si se ajusta al proyecto, posiblemente le pediremos que cambie algunas cosas.
1. Si no se ajusta al proyecto, podríamos rechazarlo. No lo tomes mal, pero mantener las
   cosas a largo plazo lleva tiempo ... ¡Siempre puedes usar tu propio fork!
