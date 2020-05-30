# -*- coding: utf-8 -*-
"""Andamio tareas del proyecto hijo.

Este archivo se ejecutará con https://www.pyinvoke.org/ en Python 3.6+.

Contiene ayudantes comunes para desarrollar usando este proyecto hijo.
"""
import json
import os
from glob import glob, iglob
from pathlib import Path

from invoke import task

PROJECT_ROOT = Path(__file__).parent.absolute()
SRC_PATH = PROJECT_ROOT / "odoo" / "custom" / "src"
DEVELOP_DEPENDENCIES = (
    "copier",
    "docker-compose",
    "pre-commit",
)
UID_ENV = {"GID": str(os.getgid()), "UID": str(os.getuid()), "UMASK": "27"}


@task
def write_code_workspace_file(c, cw_path=None):
    """Genera el archivo de definicion del espacio de trabajo de código.

    Algunas otras tareas llamarán a esta cuando sea necesario, y dado que no puede
    especificar el nombre del archivo allí, si desea una específica, debe llamar a
    esta tarea antes.

    La mayoría de las veces puede olvidarse de esta tarea y dejar que se ejecute
    automáticamente cuando sea necesario.

    Si no define un nombre de workspace, esta tarea reutilizará el primer archivo
    `andamio.*.code-workspace` que se encuentra dentro del directorio actual.

    Si no se encuentra ninguno, el valor predeterminado será
    `andamio.$(basename $PWD).code-workspace`

    Si lo define manualmente, recuerde usar el mismo prefijo y sufijo
    si desea que git-ignored por defecto.

    Ejemplo: `--cw-path andamio.mi-propio-nombre.code-workspace`
    """
    if not cw_path:
        try:
            cw_path = next(iglob(str(PROJECT_ROOT / "andamio.*.code-workspace")))
        except StopIteration:
            cw_path = f"andamio.{PROJECT_ROOT.name}.code-workspace"
    if not Path(cw_path).is_absolute():
        cw_path = PROJECT_ROOT / cw_path
    cw_config = {}
    try:
        with open(cw_path) as cw_fd:
            cw_config = json.load(cw_fd)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass  # Nevermind, we start with a new config
    cw_config["folders"] = []
    addon_repos = glob(str(SRC_PATH / "*" / ".git" / ".."))
    for subrepo in sorted(addon_repos):
        subrepo = Path(subrepo).resolve()
        cw_config["folders"].append({"path": str(subrepo.relative_to(PROJECT_ROOT))})
    # HACK https://github.com/microsoft/vscode/issues/95963 put private second to last
    private = SRC_PATH / "private"
    if private.is_dir():
        cw_config["folders"].append({"path": str(private.relative_to(PROJECT_ROOT))})
    # HACK https://github.com/microsoft/vscode/issues/37947 put top folder last
    cw_config["folders"].append({"path": "."})
    with open(cw_path, "w") as cw_fd:
        json.dump(cw_config, cw_fd, indent=2)
        cw_fd.write("\n")


@task
def develop(c):
    """Establecer un entorno de desarrollo basico."""
    # Install basic dependencies
    for dep in DEVELOP_DEPENDENCIES:
        try:
            c.run(f"{dep} --version", hide=True)
        except Exception:
            try:
                c.run("pipx --version")
            except Exception:
                c.run("python3 -m pip install --user pipx")
            c.run(f"pipx install {dep}")
    # Prepar el entorno
    Path(PROJECT_ROOT, "odoo", "auto", "addons").mkdir(parents=True, exist_ok=True)
    with c.cd(str(PROJECT_ROOT)):
        c.run("git init")
        c.run("ln -sf devel.yaml docker-compose.yml")
        write_code_workspace_file(c)
        c.run("pre-commit install")


@task(develop)
def git_aggregate(c):
    """Descargar el codigo git de odoo & addons.

    Ejecuta git-agregador desde dentro del contenedor Andamio.
    """
    with c.cd(str(PROJECT_ROOT)):
        c.run(
            "docker-compose --file setup-devel.yaml run --rm odoo", env=UID_ENV,
        )
    write_code_workspace_file(c)
    for git_folder in iglob(str(SRC_PATH / "*" / ".git" / "..")):
        action = (
            "install"
            if Path(git_folder, ".pre-commit-config.yaml").is_file()
            else "uninstall"
        )
        with c.cd(git_folder):
            c.run(f"pre-commit {action}")


@task(develop)
def img_build(c, pull=True):
    """Construye imagenes de docker."""
    cmd = "docker-compose build"
    if pull:
        cmd += " --pull"
    with c.cd(str(PROJECT_ROOT)):
        c.run(cmd, env=UID_ENV)


@task(develop)
def img_pull(c):
    """Tira las imagenes docker-compose pull."""
    with c.cd(str(PROJECT_ROOT)):
        c.run("docker-compose pull")


@task(develop)
def lint(c, verbose=False):
    """Lint-ea & formatea el codigo de origen."""
    cmd = "pre-commit run --show-diff-on-failure --all-files --color=always"
    if verbose:
        cmd += " --verbose"
    with c.cd(str(PROJECT_ROOT)):
        c.run(cmd)


@task(develop)
def start(c, detach=True, ptvsd=False):
    """Inicia el entorno."""
    cmd = "docker-compose up"
    if detach:
        cmd += " --detach"
    with c.cd(str(PROJECT_ROOT)):
        c.run(cmd, env={"ANDAMIO_PTVSD_ENABLE": str(int(ptvsd))})


@task(
    develop,
    help={
        "purge": "Eliminar todo contenedor relacionado, imágenes de redes y volumenes."
    },
)
def stop(c, purge=False):
    """Para y (Opcionalmente) purga el entorno."""
    cmd = "docker-compose"
    if purge:
        cmd += " down --remove-orphans --rmi local --volumes"
    else:
        cmd += " stop"
    with c.cd(str(PROJECT_ROOT)):
        c.run(cmd)


@task(develop)
def restart(c, quick=True):
    """Reinicia contenedor(es) Dued."""
    cmd = "docker-compose restart"
    if quick:
        cmd = f"{cmd} -t0"
    cmd = f"{cmd} odoo odoo_proxy"
    with c.cd(str(PROJECT_ROOT)):
        c.run(cmd)


@task(develop)
def logs(c, tail=10):
    """Obtiene los ultimos logs del entorno actual."""
    cmd = "docker-compose logs -f"
    if tail:
        cmd += f" --tail {tail}"
    with c.cd(str(PROJECT_ROOT)):
        c.run(cmd)
