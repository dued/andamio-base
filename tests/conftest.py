import os
from pathlib import Path

import pytest
import yaml
from plumbum import local
from plumbum.cmd import git

with open("copier.yml") as copier_fd:
    COPIER_SETTINGS = yaml.safe_load(copier_fd)

# Diferentes tests diferentes versiones de odoo
OLDEST_SUPPORTED_ODOO_VERSION = 8.0
ALL_ODOO_VERSIONS = tuple(COPIER_SETTINGS["odoo_version"]["choices"])
SUPPORTED_ODOO_VERSIONS = tuple(
    v for v in ALL_ODOO_VERSIONS if v >= OLDEST_SUPPORTED_ODOO_VERSION
)
LAST_ODOO_VERSION = max(SUPPORTED_ODOO_VERSIONS)
SELECTED_ODOO_VERSIONS = (
    frozenset(map(float, os.environ.get("SELECTED_ODOO_VERSIONS", "").split()))
    or ALL_ODOO_VERSIONS
)


@pytest.fixture(params=ALL_ODOO_VERSIONS)
def any_odoo_version(request) -> float:
    """Devuelve cualquier version odoo utilizable."""
    if request.param not in SELECTED_ODOO_VERSIONS:
        pytest.skip("La version odoo no esta en el rango seleccionado")
    return request.param


@pytest.fixture(params=SUPPORTED_ODOO_VERSIONS)
def supported_odoo_version(request) -> float:
    """Devuelve cualquier version odoo soportada."""
    if request.param not in SELECTED_ODOO_VERSIONS:
        pytest.skip("La version de Odoo Soportada no esta en el rango seleccionado")
    return request.param


@pytest.fixture()
def cloned_template(tmp_path_factory):
    """Este repositorio clonado a un destino temporal.

    El clon incluirá cambios sucios y tendrá una etiqueta de 'prueba' en su HEAD.

    Devuelve el `Path` local al clon.
    """
    patches = [git("diff", "--cached"), git("diff")]
    with tmp_path_factory.mktemp("cloned_template_") as dirty_template_clone:
        git("clone", ".", dirty_template_clone)
        with local.cwd(dirty_template_clone):
            for patch in patches:
                if patch:
                    (git["apply", "--reject"] << patch)()
                    git("add", ".")
                    git(
                        "commit",
                        "--author=Test<test@test>",
                        "--message=dirty changes",
                        "--no-verify",
                    )
            git("tag", "--force", "test")
        yield dirty_template_clone


@pytest.fixture()
def versionless_odoo_autoskip(request):
    """Accesorio para omitir automaticamente las pruebas en versiones anteriores de odoo."""
    is_version_specific_test = (
        "any_odoo_version" in request.fixturenames
        or "supported_odoo_version" in request.fixturenames
    )
    if LAST_ODOO_VERSION not in SELECTED_ODOO_VERSIONS and not is_version_specific_test:
        pytest.skip(
            "test version-independent en la sesión de prueba de odoo versionada antigua"
        )


def teardown_function(function):
    pre_commit_log = (
        Path("~") / ".cache" / "pre-commit" / "pre-commit.log"
    ).expanduser()
    if pre_commit_log.is_file():
        print(pre_commit_log.read_text())
        pre_commit_log.unlink()
