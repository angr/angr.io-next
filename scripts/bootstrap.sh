#!/usr/bin/env bash
#
# Bootstrap a local dev environment for angr.io.
#
# This environment has no system Node and a ~/.local install that doesn't always
# survive reboots, so this script (re)installs everything the site needs:
#
#   - Node (to ~/.local, only if `node` is missing)
#   - npm dependencies (npm ci)
#   - the Playwright Chromium used by the screenshot feedback loop
#
# It's idempotent — safe to re-run any time `node` or the browser goes missing.
#
#   ./scripts/bootstrap.sh            # full setup
#   ./scripts/bootstrap.sh --no-browser   # skip the Playwright download
#
set -euo pipefail

NODE_VERSION="${NODE_VERSION:-v22.16.0}"
PREFIX="${PREFIX:-$HOME/.local}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export PATH="$PREFIX/bin:$PATH"

install_node() {
  if command -v node >/dev/null 2>&1; then
    echo "✓ node $(node --version) already present"
    return
  fi
  local arch tarball url tmp
  case "$(uname -m)" in
    x86_64) arch="x64" ;;
    aarch64 | arm64) arch="arm64" ;;
    *) echo "✗ unsupported arch $(uname -m)" >&2; exit 1 ;;
  esac
  tarball="node-${NODE_VERSION}-linux-${arch}.tar.xz"
  url="https://nodejs.org/dist/${NODE_VERSION}/${tarball}"
  tmp="$(mktemp -d)"
  echo "→ installing node ${NODE_VERSION} (${arch}) to ${PREFIX}"
  curl -fsSL -o "${tmp}/node.tar.xz" "$url"
  mkdir -p "$PREFIX"
  tar -xf "${tmp}/node.tar.xz" -C "$tmp"
  cp -r "${tmp}/node-${NODE_VERSION}-linux-${arch}/." "$PREFIX/"
  rm -rf "$tmp"
  echo "✓ node $(node --version) installed"
}

install_deps() {
  echo "→ installing npm dependencies (npm ci)"
  ( cd "$REPO_DIR" && npm ci )
  echo "✓ dependencies installed"
}

install_browser() {
  echo "→ installing Playwright Chromium"
  ( cd "$REPO_DIR" && npx playwright install chromium )
  echo "✓ browser installed"
}

main() {
  install_node
  install_deps
  if [[ "${1:-}" != "--no-browser" ]]; then
    install_browser
  fi
  echo
  echo "Done. Add this to your shell for the current session:"
  echo "    export PATH=\"$PREFIX/bin:\$PATH\""
  echo "Then: npm run dev"
}

main "$@"
