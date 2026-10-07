#!/usr/bin/env bash
# Source this before running gh:  source .ai/general/skills/github/gh-env.sh
# - Uses an existing gh install + login when present (Claude Code on the PM's machine).
# - Otherwise installs gh into ~/.local/gh (Linux/macOS, amd64/arm64) and loads GH_TOKEN
#   from the Project Brain's gitignored .env (Cowork, cloud sandboxes).
# Never prints the token.

_pb_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"

if ! command -v gh >/dev/null 2>&1; then
  _gh_bin="$(ls -d "$HOME"/.local/gh/gh_*/bin 2>/dev/null | tail -1)"
  if [ -z "$_gh_bin" ]; then
    _os="$(uname -s | tr '[:upper:]' '[:lower:]')"; [ "$_os" = "darwin" ] && _os="macOS"
    case "$(uname -m)" in x86_64|amd64) _arch=amd64 ;; aarch64|arm64) _arch=arm64 ;; *) echo "gh-env: unsupported arch $(uname -m)" >&2; return 1 ;; esac
    _ver="$(curl -fsS --max-time 15 https://api.github.com/repos/cli/cli/releases/latest | sed -n 's/.*"tag_name": *"v\([^"]*\)".*/\1/p')"
    [ -z "$_ver" ] && { echo "gh-env: couldn't look up the latest gh release" >&2; return 1; }
    _ext="tar.gz"; [ "$_os" = "macOS" ] && _ext="zip"
    mkdir -p "$HOME/.local/gh" && cd "$HOME/.local/gh" || return 1
    curl -fsSL --max-time 90 -o "gh.$_ext" "https://github.com/cli/cli/releases/download/v${_ver}/gh_${_ver}_${_os}_${_arch}.${_ext}" || { echo "gh-env: download failed" >&2; cd - >/dev/null; return 1; }
    if [ "$_ext" = "zip" ]; then unzip -q "gh.$_ext"; else tar xzf "gh.$_ext"; fi
    rm -f "gh.$_ext"; cd - >/dev/null
    _gh_bin="$(ls -d "$HOME"/.local/gh/gh_*/bin | tail -1)"
  fi
  export PATH="$_gh_bin:$PATH"
fi

# Load the token only if gh isn't already logged in and none is set.
if [ -z "${GH_TOKEN:-}" ] && ! gh auth status >/dev/null 2>&1; then
  if [ -f "$_pb_root/.env" ]; then
    GH_TOKEN="$(sed -n 's/^GH_TOKEN=//p' "$_pb_root/.env" | tail -1 | tr -d '"'"'"' \r')"
    export GH_TOKEN
  fi
  [ -z "${GH_TOKEN:-}" ] && echo "gh-env: no gh login and no GH_TOKEN in $_pb_root/.env (see .env.example)" >&2
fi
unset _pb_root _gh_bin _os _arch _ver _ext
