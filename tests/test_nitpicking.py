"""Nitpicking small tests ahead."""
import json
from pathlib import Path
from textwrap import dedent

import pytest
import yaml
from copier.main import copy
from plumbum import local
from plumbum.cmd import diff, git, invoke, pre_commit

WHITESPACE_PREFIXED_LICENSES = (
    "AGPL-3.0-or-later",
    "Apache-2.0",
    "LGPL-3.0-or-later",
)


@pytest.mark.parametrize("project_license", WHITESPACE_PREFIXED_LICENSES)
def test_license_whitespace_prefix(
    tmp_path: Path, cloned_template: Path, project_license
):
    dst = tmp_path / "dst"
    copy(
        str(cloned_template),
        str(dst),
        vcs_ref="test",
        force=True,
        data={"project_license": project_license},
    )
    assert (dst / "LICENSE").read_text().startswith("   ")


def test_no_vscode_in_private(tmp_path: Path):
    """Asegurese que las carpetas .vscode se git-ignoren en la carpeta privada.
    """
    copy(".", str(tmp_path), vcs_ref="HEAD", force=True)
    with local.cwd(tmp_path):
        git("add", ".")
        git("commit", "--no-verify", "-am", "hello world")
        vscode = tmp_path / "odoo" / "custom" / "src" / "private" / ".vscode"
        vscode.mkdir()
        (vscode / "something").touch()
        assert not git("status", "--porcelain")


def test_mqt_configs_synced():
    """Asegurese de que las configuraciones de MQT esten sincronizadas."""
    template = Path("tests", "default_settings", "v13.0")
    mqt = Path("vendor", "maintainer-quality-tools", "sample_files", "pre-commit-13.0")
    good_diffs = Path("tests", "samples", "mqt-diffs")
    for conf in (".pylintrc", ".pylintrc-mandatory"):
        good = (good_diffs / f"{conf}.diff").read_text()
        tested = diff(template / conf, mqt / conf, retcode=1)
        assert good == tested


def test_gitlab_badges(tmp_path: Path):
    """Las insignias de Gitlab estan formateadas correctamente en README."""
    copy(
        ".",
        str(tmp_path),
        vcs_ref="HEAD",
        force=True,
        data={"gitlab_url": "https://gitlab.ejemplo.com/dued/mi-badged-odoo"},
    )
    expected_badges = dedent(
        """
        [![pipeline status](https://gitlab.ejemplo.com/dued/mi-badged-odoo/badges/13.0/pipeline.svg)](https://gitlab.ejemplo.com/dued/mi-badged-odoo/commits/13.0)
        [![coverage report](https://gitlab.ejemplo.com/dued/mi-badged-odoo/badges/13.0/coverage.svg)](https://gitlab.ejemplo.com/dued/mi-badged-odoo/commits/13.0)
        """
    )
    assert expected_badges.strip() in (tmp_path / "README.md").read_text()


def test_alt_domains_rules(tmp_path: Path, cloned_template: Path):
    """Asegurese de que las redirecciones de dominios alternativos sean buenas para Traefik."""
    copy(
        str(cloned_template),
        str(tmp_path),
        vcs_ref="HEAD",
        force=True,
        data={
            "domain_prod": "www.ejemplo.com",
            "domain_prod_alternatives": [
                "old.ejemplo.com",
                "ejemplo.com",
                "ejemplo.org",
                "www.ejemplo.org",
            ],
        },
    )
    with local.cwd(tmp_path):
        git("add", "prod.yaml")
        pre_commit("run", "-a", retcode=1)
    expected = Path("tests", "samples", "alt-domains", "prod.yaml").read_text()
    generated = (tmp_path / "prod.yaml").read_text()
    generated_scalar = yaml.load(generated)
    # Cualquiera de estos caracteres en una etiqueta traefik es un error casi seguro
    error_chars = ("\n", "'", '"')
    for service in generated_scalar["services"].values():
        for key, value in service.get("labels", {}).items():
            if not key.startswith("traefik."):
                continue
            for char in error_chars:
                assert char not in key
                assert char not in str(value)
    assert generated == expected


def test_cidr_whitelist_rules(tmp_path: Path, cloned_template: Path):
    """Asegurese de que las redirecciones de la lista blanca CIDR sean buenas para Traefik."""
    copy(
        str(cloned_template),
        str(tmp_path),
        vcs_ref="HEAD",
        force=True,
        data={"cidr_whitelist": ["123.123.123.123/24", "456.456.456.456"]},
    )
    with local.cwd(tmp_path):
        git("add", "prod.yaml", "test.yaml")
        pre_commit("run", "-a", retcode=1)
    expected = Path("tests", "samples", "cidr-whitelist")
    assert (tmp_path / "prod.yaml").read_text() == (expected / "prod.yaml").read_text()
    assert (tmp_path / "test.yaml").read_text() == (expected / "test.yaml").read_text()


def test_code_workspace_file(tmp_path: Path, cloned_template: Path):
    """El archivo se genera como se esperaba."""
    copy(
        str(cloned_template), str(tmp_path), vcs_ref="HEAD", force=True,
    )
    assert (tmp_path / f"andamio.{tmp_path.name}.code-workspace").is_file()
    (tmp_path / f"andamio.{tmp_path.name}.code-workspace").rename(
        tmp_path / "andamio.other1.code-workspace"
    )
    with local.cwd(tmp_path):
        invoke("write-code-workspace-file")
        assert (tmp_path / "andamio.other1.code-workspace").is_file()
        assert not (tmp_path / f"andamio.{tmp_path.name}.code-workspace").is_file()
        # Do a stupid and dirty git clone to check it's sorted fine
        git("clone", cloned_template, Path("odoo", "custom", "src", "zzz"))
        invoke("write-code-workspace-file", "-c", "andamio.other2.code-workspace")
        assert not (tmp_path / f"andamio.{tmp_path.name}.code-workspace").is_file()
        assert (tmp_path / "andamio.other1.code-workspace").is_file()
        assert (tmp_path / "andamio.other2.code-workspace").is_file()
        with (tmp_path / "andamio.other2.code-workspace").open() as fp:
            workspace_definition = json.load(fp)
        assert workspace_definition == {
            "folders": [
                {"path": "odoo/custom/src/zzz"},
                {"path": "odoo/custom/src/private"},
                {"path": "."},
            ]
        }


def test_dotdocker_ignore_content(tmp_path: Path, cloned_template: Path):
    """Todo lo que hay dentro de .docker debe ser ignorado."""
    copy(
        str(cloned_template), str(tmp_path), vcs_ref="HEAD", force=True,
    )
    with local.cwd(tmp_path):
        git("add", ".")
        git("commit", "-am", "hello", retcode=1)
        git("commit", "-am", "hello")
        (tmp_path / ".docker" / "some-file").touch()
        assert not git("status", "--porcelain")


def test_template_update_badge(tmp_path: Path, cloned_template: Path):
    """Pruebe que la insignia de actualizacion de plantilla este formateada correctamente."""
    tag = "v99999.0.0-99999-bye-bye"
    with local.cwd(cloned_template):
        git("tag", "--delete", "test")
        git("tag", "--force", tag)
    copy(str(cloned_template), str(tmp_path), vcs_ref=tag, force=True)
    expected = "[![ultimo andamio actualizado](https://img.shields.io/badge/ultimo%20andamio%20actualizado-v99999.0.0--99999--bye--bye-informational)](https://github.com/dued/andamio-base/tree/v99999.0.0-99999-bye-bye)"
    assert expected in (tmp_path / "README.md").read_text()


def test_pre_commit_config(
    tmp_path: Path, cloned_template: Path, supported_odoo_version: float
):
    """Prueba que .pre-commit-config.yaml tiene configuraciones específicas OK."""
    copy(
        str(cloned_template),
        str(tmp_path),
        vcs_ref="HEAD",
        force=True,
        data={"odoo_version": supported_odoo_version},
    )
    pre_commit_config = yaml.load((tmp_path / ".pre-commit-config.yaml").read_text())
    is_py3 = supported_odoo_version >= 11
    found = 0
    should_find = 1
    for repo in pre_commit_config["repos"]:
        if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks":
            found += 1
            if is_py3:
                assert {"id": "debug-statements"} in repo["hooks"]
                assert {"id": "fix-encoding-pragma", "args": ["--remove"]} in repo[
                    "hooks"
                ]
            else:
                assert {"id": "debug-statements"} not in repo["hooks"]
                assert {"id": "fix-encoding-pragma", "args": ["--remove"]} not in repo[
                    "hooks"
                ]
                assert {"id": "fix-encoding-pragma"} in repo["hooks"]
    assert found == should_find
