"""Scripts para migracion de andamios.

Este archivo se ejecuta mediante copier al actualizar proyectos derivados.
"""
import shutil
from pathlib import Path

from invoke import task


@task
def de_scaffolding_a_andamio(c):
    print("Eliminando la basura remanente de scaffolding.")
    shutil.rmtree(Path(".vscode", "doodba"), ignore_errors=True)
    garbage = (
        Path(".travis.yml"),
        Path(".vscode", "doodbasetup.py"),
        Path("odoo", "custom", "src", "private", ".empty"),
    )
    for path in garbage:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    # When using Copier >= 3.0.5, this file didn't get properly migrated
    editorconfig_file = Path(".editorconfig")
    editorconfig_contents = editorconfig_file.read_text()
    editorconfig_contents = editorconfig_contents.replace(
        "[*.yml]", "[*.{code-snippets,code-workspace,json,md,yaml,yml}{,.jinja}]", 1
    )
    editorconfig_file.write_text(editorconfig_contents)


@task
def remove_odoo_auto_folder(c):
    """Esta carpeta no tiene mas sentido para nosotros..

    La tarea `invoke develop` ahora maneja su creación, que se hace con
    el UID y GID del usuario host para evitar problemas.

    Ya no es necesario tenerlo en nuestro árbol de códigos.
    """
    shutil.rmtree(Path("odoo", "auto"), ignore_errors=True)
