#!/usr/bin/env bash

set -euo pipefail

CLAUDE_URL="https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/rules/CLAUDE.md"

tmp_dir=""

cleanup() {
	if [[ -n "$tmp_dir" && -d "$tmp_dir" ]]; then
		rm -rf "$tmp_dir"
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

prompt_install_scope() {
	local answer=""

	echo "請選擇安裝位置："
	echo "1) 專案目錄（目前資料夾所屬專案根目錄）"
	echo "2) 全域位置（預設）"
	read -r -p "請輸入 1 或 2（預設 2）：" answer

	case "${answer:-2}" in
		1) echo "project" ;;
		2) echo "global" ;;
		*)
			echo "輸入無效，將使用預設值：全域位置"
			echo "global"
			;;
	esac
}

download_sources() {
	tmp_dir="$(mktemp -d)"

	curl -fsSL "$CLAUDE_URL" -o "$tmp_dir/CLAUDE.md"
}

detect_project_root() {
	if command -v git >/dev/null 2>&1 && git rev-parse --show-toplevel >/dev/null 2>&1; then
		git rev-parse --show-toplevel
	else
		pwd
	fi
}

contains_bu_ketao() {
	local target_file="$1"

	if [[ -f "$target_file" ]] && grep -qi "bu-ketao" "$target_file"; then
		return 0
	fi

	return 1
}

install_into_file() {
	local source_file="$1"
	local target_file="$2"

	if contains_bu_ketao "$target_file"; then
		echo "目前偵測到『bu-ketao』字樣，請確認是否已經安裝？"
		echo "已略過：$target_file"
		return
	fi

	if [[ -f "$target_file" ]]; then
		cat "$source_file" >> "$target_file"
		echo "已附加內容至：$target_file"
	else
		cat "$source_file" > "$target_file"
		echo "已建立檔案：$target_file"
	fi
}

install_for_project_scope() {
	local project_root=""

	project_root="$(detect_project_root)"
	echo "偵測到專案根目錄：$project_root"

	install_into_file "$tmp_dir/CLAUDE.md" "$project_root/CLAUDE.md"
	install_into_file "$tmp_dir/CLAUDE.md" "$project_root/AGENTS.md"
}

install_for_global_scope() {
	local directory=""
	local target=""

	directory="$HOME/.claude"
	target="$directory/CLAUDE.md"

	if [[ -d "$directory" ]]; then
		install_into_file "$tmp_dir/CLAUDE.md" "$target"
	else
		echo "沒有 $directory 資料夾，略過 $target"
	fi

	for directory in \
		"$HOME/.codex" \
		"$HOME/.copilot" \
		"$HOME/.cursor" \
		"$HOME/.kiro"; do
		target="$directory/AGENTS.md"

		if [[ -d "$directory" ]]; then
			install_into_file "$tmp_dir/CLAUDE.md" "$target"
		else
			echo "沒有 $directory 資料夾，略過 $target"
		fi
	done
}

main() {
	local scope=""

	ensure_tool "curl"

	scope="$(prompt_install_scope)"

	download_sources

	if [[ "$scope" == "project" ]]; then
		install_for_project_scope
	else
		install_for_global_scope
	fi

	echo "安裝流程完成。"
}

main
