from pathlib import Path

import pytest

from mdalign.checks import wide_chars
from mdalign.cli import run_checks, run_fixes

FIXTURES = Path(__file__).parent / "fixtures"
CHECK_ONLY_MODULES = {"wide-chars": wide_chars}


def collect_fixtures():
    for d in sorted(FIXTURES.rglob("input.md")):
        yield pytest.param(d.parent, id=d.parent.relative_to(FIXTURES).as_posix())


def _is_check_only(fixture_dir):
    rel = fixture_dir.relative_to(FIXTURES).as_posix()
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "checks":
        return parts[1] in CHECK_ONLY_MODULES
    return False


@pytest.mark.parametrize("fixture_dir", collect_fixtures())
def test_check_detects_issues(fixture_dir):
    input_md = (fixture_dir / "input.md").read_text()
    expected_md = (fixture_dir / "expected.md").read_text()
    errors = run_checks(input_md.splitlines(keepends=True))
    if input_md == expected_md:
        if not _is_check_only(fixture_dir):
            assert errors == []
    else:
        assert len(errors) > 0


@pytest.mark.parametrize("fixture_dir", collect_fixtures())
def test_fix_produces_expected(fixture_dir):
    input_md = (fixture_dir / "input.md").read_text()
    expected_md = (fixture_dir / "expected.md").read_text()
    if _is_check_only(fixture_dir) and input_md != expected_md:
        pytest.skip("check-only module, fix is no-op")
    fixed = run_fixes(input_md.splitlines(keepends=True))
    assert "".join(fixed) == expected_md


@pytest.mark.parametrize("fixture_dir", collect_fixtures())
def test_fix_is_idempotent(fixture_dir):
    expected_md = (fixture_dir / "expected.md").read_text()
    lines = expected_md.splitlines(keepends=True)
    fixed = run_fixes(lines)
    assert "".join(fixed) == expected_md
