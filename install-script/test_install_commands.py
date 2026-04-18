#!/usr/bin/env python3
"""
Dry-run tests for install-commadns.sh logic.

Mocks: curl (subprocess), filesystem (os/shutil), mktemp.
No actual network calls or file writes.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call


COMMAND_FILENAME = "bu-ketao.md"
COMMAND_URL = (
    "https://raw.githubusercontent.com/lazyjerry/bu-ketao/"
    "refs/heads/main/commands/bu-ketao.md"
)


# ---------- helpers that mirror the shell script logic ----------

def ensure_tool(tool_name: str) -> bool:
    result = shutil.which(tool_name)
    return result is not None


def download_source(url: str, tmp_path: str) -> bool:
    result = subprocess.run(
        ["curl", "-fsSL", url, "-o", tmp_path],
        capture_output=True,
    )
    return result.returncode == 0


def install_command(commands_dir: str, tmp_file: str, filename: str) -> str:
    target = os.path.join(commands_dir, filename)
    if not os.path.isdir(commands_dir):
        return f"略過（目錄不存在）：{commands_dir}"
    existed = os.path.isfile(target)
    shutil.copy2(tmp_file, target)
    return "已覆蓋" if existed else "已安裝"


# ---------- test cases ----------

class TestEnsureTool(unittest.TestCase):
    @patch("shutil.which", return_value="/usr/bin/curl")
    def test_tool_found(self, _):
        self.assertTrue(ensure_tool("curl"))

    @patch("shutil.which", return_value=None)
    def test_tool_missing(self, _):
        self.assertFalse(ensure_tool("curl"))


class TestDownloadSource(unittest.TestCase):
    @patch("subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        ok = download_source(COMMAND_URL, "/tmp/fake_tmp")
        self.assertTrue(ok)
        mock_run.assert_called_once_with(
            ["curl", "-fsSL", COMMAND_URL, "-o", "/tmp/fake_tmp"],
            capture_output=True,
        )

    @patch("subprocess.run")
    def test_curl_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=22)
        ok = download_source(COMMAND_URL, "/tmp/fake_tmp")
        self.assertFalse(ok)


class TestInstallCommand(unittest.TestCase):
    @patch("shutil.copy2")
    @patch("os.path.isfile", return_value=False)
    @patch("os.path.isdir", return_value=True)
    def test_fresh_install(self, _isdir, _isfile, mock_copy):
        result = install_command("/home/user/.claude/commands", "/tmp/src", COMMAND_FILENAME)
        self.assertEqual(result, "已安裝")
        mock_copy.assert_called_once_with(
            "/tmp/src",
            f"/home/user/.claude/commands/{COMMAND_FILENAME}",
        )

    @patch("shutil.copy2")
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_overwrite(self, _isdir, _isfile, mock_copy):
        result = install_command("/home/user/.claude/commands", "/tmp/src", COMMAND_FILENAME)
        self.assertEqual(result, "已覆蓋")
        mock_copy.assert_called_once()

    @patch("shutil.copy2")
    @patch("os.path.isdir", return_value=False)
    def test_dir_missing(self, _isdir, mock_copy):
        result = install_command("/nonexistent/commands", "/tmp/src", COMMAND_FILENAME)
        self.assertIn("略過", result)
        mock_copy.assert_not_called()


class TestFullFlow(unittest.TestCase):
    """End-to-end dry run: no real curl, no real disk writes."""

    @patch("shutil.copy2")
    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/curl")
    @patch("tempfile.mkstemp", return_value=(3, "/tmp/mock_tmp"))
    @patch("os.path.isfile", return_value=False)
    @patch("os.path.isdir")
    def test_full_flow_some_dirs_exist(
        self, mock_isdir, _isfile, _mkstemp, _which, mock_run, mock_copy
    ):
        dirs_exist = {
            os.path.expanduser("~/.claude/commands"): True,
            os.path.expanduser("~/.codex/commands"): False,
            os.path.expanduser("~/.cursor/commands"): True,
            os.path.expanduser("~/.kiro/prompts"): False,
            os.path.expanduser("~/.copilot/commands"): False,
        }
        mock_isdir.side_effect = lambda p: dirs_exist.get(p, False)
        mock_run.return_value = MagicMock(returncode=0)

        # simulate main()
        self.assertTrue(ensure_tool("curl"))
        ok = download_source(COMMAND_URL, "/tmp/mock_tmp")
        self.assertTrue(ok)

        results = []
        for d in dirs_exist:
            results.append(install_command(d, "/tmp/mock_tmp", COMMAND_FILENAME))

        installed = [r for r in results if r in ("已安裝", "已覆蓋")]
        skipped = [r for r in results if "略過" in r]

        self.assertEqual(len(installed), 2)   # claude + cursor
        self.assertEqual(len(skipped), 3)
        self.assertEqual(mock_copy.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
