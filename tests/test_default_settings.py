from pathlib import Path
from shutil import rmtree

import pytest
import yaml
from copier.main import copy
from plumbum import local
from plumbum.cmd import diff, git, invoke


def test_default_settings(
    tmp_path: Path, any_odoo_version: float, cloned_template: Path
):
    """Prueba que una plantilla renderizada de cero este OK para cada version.

    No se dan parámetros aparte de odoo_version. Esto prueba que los andamios
    funcionan bien con respuestas predeterminadas.
    """
    dst = tmp_path / f"v{any_odoo_version:.1f}"
    with local.cwd(cloned_template):
        copy(
            ".",
            str(dst),
            vcs_ref="test",
            force=True,
            data={"odoo_version": any_odoo_version},
        )
    with local.cwd(dst):
        # TODO When copier runs pre-commit before extracting diff, make sure
        # here that it works as expected
        Path(dst, "odoo", "auto", "addons").rmdir()
        Path(dst, "odoo", "auto").rmdir()
        git("add", ".")
        git("commit", "-am", "Hello World", retcode=1)  # pre-commit fails
        git("commit", "-am", "Hello World")
    # El resultado coincide con lo que esperamos.
    diff(
        "--context=3",
        "--exclude=.git",
        "--recursive",
        local.cwd / "tests" / "default_settings" / f"v{any_odoo_version:.1f}",
        dst,
    )


def test_pre_commit_autoinstall(tmp_path: Path, supported_odoo_version: float):
    """Testea que pre-commit se (des)instala automaticamente en repos alien.

    Esta prueba es más lenta porque tiene que descargar y construir imágenes
    OCI y descargar código git, por lo que solo se ejecuta en estas versiones
    de Odoo:

    - 10.0 porque es Python 2 y no tiene configuraciones de confirmación previa en OCA.
    - 13.0 porque es Python 3 y tiene configuraciones de confirmación previa en OCA..
    """
    if supported_odoo_version not in {10.0, 13.0}:
        pytest.skip("esta prueba solo se testea con otras versiones de odoo")
    copy(
        ".",
        str(tmp_path),
        vcs_ref="HEAD",
        force=True,
        data={"odoo_version": supported_odoo_version},
    )
    with local.cwd(tmp_path):
        with (tmp_path / "odoo" / "custom" / "src" / "addons.yaml").open("w") as fd:
            yaml.dump({"server-tools": "*"}, fd)
        # El usuario puede descargar el código git desde cualquier carpeta
        with local.cwd(tmp_path / "odoo" / "custom" / "src" / "private"):
            invoke("git-aggregate")
        # Check pre-commit está correctamente (des)instalado
        pre_commit_present = supported_odoo_version >= 13.0
        server_tools_git = (
            tmp_path / "odoo" / "custom" / "src" / "server-tools" / ".git"
        )
        assert server_tools_git.is_dir()
        assert (
            server_tools_git / "hooks" / "pre-commit"
        ).is_file() == pre_commit_present
    # Elimine el código fuente, puede usar mucho espacio en disco
    rmtree(tmp_path)
