#!/usr/bin/env bash

set -euo pipefail

COMMAND_URL="https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/commands/bu-ketao.md"
COMMAND_FILENAME="bu-ketao.md"

tmp_file=""

cleanup() {
	if [[ -n "$tmp_file" && -f "$tmp_file" ]]; then
		rm -f "$tmp_file"
	fi
}

trap cleanup EXIT

ensure_tool() {
	local tool_name="$1"

	if ! command -v "$tool_name" >/dev/null 2>&1; then
		echo "找不到必要工具：$tool_name"
		exit 1
	fi
}

download_source() {
	tmp_file="$(mktemp)"
	curl -fsSL "$COMMAND_URL" -o "$tmp_file"
}

install_command() {
	local commands_dir="$1"
	local target="$commands_dir/$COMMAND_FILENAME"

	if [[ ! -d "$commands_dir" ]]; then
		echo "略過（目錄不存在）：$commands_dir"
		return
	fi

	if [[ -f "$target" ]]; then
		cp "$tmp_file" "$target"
		echo "已覆蓋：$target"
	else
		cp "$tmp_file" "$target"
		echo "已安裝：$target"
	fi
}

main() {
	ensure_tool "curl"

	echo "下載 $COMMAND_FILENAME ..."
	download_source
	echo ""

	echo "=== 安裝結果 ==="

	# Claude Code
	install_command "$HOME/.claude/commands"

	# Codex
	install_command "$HOME/.codex/commands"

	# Cursor
	install_command "$HOME/.cursor/commands"

	# Kiro
	install_command "$HOME/.kiro/prompts"

	# Copilot
	install_command "$HOME/.copilot/commands"

	echo ""
	echo "安裝流程完成。"
}

main
