#!/usr/bin/env python3
"""
Dry-run tests for install-agents.sh logic.

Mocks: curl (subprocess), git (subprocess), filesystem (os/shutil).
No actual network calls or file writes.
"""

import os
import subprocess
import unittest
from unittest.mock import MagicMock, call, mock_open, patch


CLAUDE_URL = (
    "https://raw.githubusercontent.com/lazyjerry/bu-ketao/"
    "refs/heads/main/rules/CLAUDE.md"
)


# ---------- helpers that mirror the shell script logic ----------

def ensure_tool(tool_name: str) -> bool:
    import shutil
    return shutil.which(tool_name) is not None


def download_sources(tmp_dir: str) -> bool:
    result = subprocess.run(
        ["curl", "-fsSL", CLAUDE_URL, "-o", os.path.join(tmp_dir, "CLAUDE.md")],
        capture_output=True,
    )
    return result.returncode == 0


def detect_project_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return os.getcwd()


def contains_bu_ketao(target_file: str) -> bool:
    if not os.path.isfile(target_file):
        return False
    with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
        return "bu-ketao" in f.read().lower()


def install_into_file(source_file: str, target_file: str) -> str:
    if contains_bu_ketao(target_file):
        return f"略過（已含 bu-ketao）：{target_file}"
    if os.path.isfile(target_file):
        with open(source_file, "rb") as src, open(target_file, "ab") as dst:
            dst.write(src.read())
        return f"已附加內容至：{target_file}"
    with open(source_file, "rb") as src, open(target_file, "wb") as dst:
        dst.write(src.read())
    return f"已建立檔案：{target_file}"


def install_for_global_scope(tmp_dir: str, home: str) -> list[str]:
    results = []
    claude_dir = os.path.join(home, ".claude")
    if os.path.isdir(claude_dir):
        results.append(install_into_file(
            os.path.join(tmp_dir, "CLAUDE.md"),
            os.path.join(claude_dir, "CLAUDE.md"),
        ))
    else:
        results.append(f"沒有 {claude_dir} 資料夾，略過")

    for tool_dir in [".codex", ".copilot", ".cursor", ".kiro"]:
        d = os.path.join(home, tool_dir)
        if os.path.isdir(d):
            results.append(install_into_file(
                os.path.join(tmp_dir, "CLAUDE.md"),
                os.path.join(d, "AGENTS.md"),
            ))
        else:
            results.append(f"沒有 {d} 資料夾，略過")
    return results


def install_for_project_scope(tmp_dir: str, project_root: str) -> list[str]:
    return [
        install_into_file(
            os.path.join(tmp_dir, "CLAUDE.md"),
            os.path.join(project_root, "CLAUDE.md"),
        ),
        install_into_file(
            os.path.join(tmp_dir, "CLAUDE.md"),
            os.path.join(project_root, "AGENTS.md"),
        ),
    ]


# ---------- test cases ----------

class TestEnsureTool(unittest.TestCase):
    @patch("shutil.which", return_value="/usr/bin/curl")
    def test_found(self, _):
        self.assertTrue(ensure_tool("curl"))

    @patch("shutil.which", return_value=None)
    def test_missing(self, _):
        self.assertFalse(ensure_tool("curl"))


class TestDownloadSources(unittest.TestCase):
    @patch("subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(download_sources("/tmp/fake"))
        mock_run.assert_called_once_with(
            ["curl", "-fsSL", CLAUDE_URL, "-o", "/tmp/fake/CLAUDE.md"],
            capture_output=True,
        )

    @patch("subprocess.run")
    def test_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=22)
        self.assertFalse(download_sources("/tmp/fake"))


class TestDetectProjectRoot(unittest.TestCase):
    @patch("subprocess.run")
    def test_git_repo(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="/repo/root\n")
        self.assertEqual(detect_project_root(), "/repo/root")

    @patch("os.getcwd", return_value="/some/dir")
    @patch("subprocess.run")
    def test_not_git_repo(self, mock_run, _):
        mock_run.return_value = MagicMock(returncode=128, stdout="")
        self.assertEqual(detect_project_root(), "/some/dir")


class TestContainsBuKetao(unittest.TestCase):
    @patch("os.path.isfile", return_value=True)
    def test_contains(self, _):
        m = mock_open(read_data="# bu-ketao mode")
        with patch("builtins.open", m):
            self.assertTrue(contains_bu_ketao("/some/CLAUDE.md"))

    @patch("os.path.isfile", return_value=True)
    def test_not_contains(self, _):
        m = mock_open(read_data="# other content")
        with patch("builtins.open", m):
            self.assertFalse(contains_bu_ketao("/some/CLAUDE.md"))

    @patch("os.path.isfile", return_value=False)
    def test_file_missing(self, _):
        self.assertFalse(contains_bu_ketao("/nonexistent/CLAUDE.md"))


class TestInstallIntoFile(unittest.TestCase):
    @patch("builtins.open", mock_open(read_data=b"content"))
    @patch("os.path.isfile", return_value=False)
    def test_creates_new_file(self, _):
        with patch("test_install_agents.contains_bu_ketao", return_value=False):
            result = install_into_file("/tmp/src/CLAUDE.md", "/dst/CLAUDE.md")
        self.assertIn("已建立", result)

    @patch("builtins.open", mock_open(read_data=b"content"))
    @patch("os.path.isfile", return_value=True)
    def test_appends_to_existing(self, _):
        with patch("test_install_agents.contains_bu_ketao", return_value=False):
            result = install_into_file("/tmp/src/CLAUDE.md", "/dst/CLAUDE.md")
        self.assertIn("已附加", result)

    @patch("os.path.isfile", return_value=True)
    def test_skips_if_already_has_bu_ketao(self, _):
        with patch("test_install_agents.contains_bu_ketao", return_value=True):
            result = install_into_file("/tmp/src/CLAUDE.md", "/dst/CLAUDE.md")
        self.assertIn("略過", result)


class TestGlobalScope(unittest.TestCase):
    def _run(self, dirs_exist: dict) -> list[str]:
        with patch("os.path.isdir", side_effect=lambda p: dirs_exist.get(p, False)), \
             patch("test_install_agents.contains_bu_ketao", return_value=False), \
             patch("builtins.open", mock_open(read_data=b"content")), \
             patch("os.path.isfile", return_value=False):
            return install_for_global_scope("/tmp/src", "/home/user")

    def test_all_dirs_exist(self):
        dirs = {
            "/home/user/.claude": True,
            "/home/user/.codex": True,
            "/home/user/.copilot": True,
            "/home/user/.cursor": True,
            "/home/user/.kiro": True,
        }
        results = self._run(dirs)
        self.assertEqual(len(results), 5)
        self.assertTrue(all("略過" not in r for r in results))

    def test_no_dirs_exist(self):
        results = self._run({})
        self.assertEqual(len(results), 5)
        self.assertTrue(all("略過" in r for r in results))

    def test_partial_dirs(self):
        dirs = {
            "/home/user/.claude": True,
            "/home/user/.cursor": True,
        }
        results = self._run(dirs)
        installed = [r for r in results if "略過" not in r]
        skipped = [r for r in results if "略過" in r]
        self.assertEqual(len(installed), 2)
        self.assertEqual(len(skipped), 3)


class TestProjectScope(unittest.TestCase):
    def test_installs_both_files(self):
        with patch("test_install_agents.contains_bu_ketao", return_value=False), \
             patch("builtins.open", mock_open(read_data=b"content")), \
             patch("os.path.isfile", return_value=False):
            results = install_for_project_scope("/tmp/src", "/repo/root")
        self.assertEqual(len(results), 2)
        self.assertTrue(any("CLAUDE.md" in r for r in results))
        self.assertTrue(any("AGENTS.md" in r for r in results))

    def test_skips_when_already_installed(self):
        with patch("test_install_agents.contains_bu_ketao", return_value=True):
            results = install_for_project_scope("/tmp/src", "/repo/root")
        self.assertTrue(all("略過" in r for r in results))


class TestFullFlow(unittest.TestCase):
    """End-to-end dry run for both scopes."""

    def _base_patches(self):
        return [
            patch("shutil.which", return_value="/usr/bin/curl"),
            patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="/repo\n")),
            patch("test_install_agents.contains_bu_ketao", return_value=False),
            patch("builtins.open", mock_open(read_data=b"content")),
            patch("os.path.isfile", return_value=False),
        ]

    def test_global_flow(self):
        dirs = {"/home/u/.claude": True, "/home/u/.cursor": True}
        patches = self._base_patches()
        patches.append(patch("os.path.isdir", side_effect=lambda p: dirs.get(p, False)))
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            self.assertTrue(ensure_tool("curl"))
            self.assertTrue(download_sources("/tmp/src"))
            results = install_for_global_scope("/tmp/src", "/home/u")
        self.assertEqual(len(results), 5)

    def test_project_flow_with_git(self):
        patches = self._base_patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            self.assertTrue(ensure_tool("curl"))
            self.assertTrue(download_sources("/tmp/src"))
            root = detect_project_root()
            results = install_for_project_scope("/tmp/src", root)
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
